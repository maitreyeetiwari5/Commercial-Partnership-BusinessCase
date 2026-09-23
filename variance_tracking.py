"""
Post-signing performance tracking: business case (plan) vs. actuals.

Reuses the approach from my Finance Forecast & Variance Automation project:
  * self-calibrating, per-KPI variance thresholds (median + scaled MAD, leave-one-out)
  * commentary gated on a documented driver in an analyst-maintained event log;
    unexplained variances are routed for review rather than given an invented cause.

Actuals are SIMULATED (seeded, reproducible) because the deal is hypothetical.
Usage: python variance_tracking.py
"""
import csv
import random
import statistics as st
from pathlib import Path

from deal_model import XLSX, load_inputs

ROOT = Path(__file__).resolve().parent
DATA, OUT = ROOT, ROOT
QUARTERS = [f"Y{y}Q{q}" for y in (1, 2) for q in (1, 2, 3, 4)]
KPIS = ["subscribers_mm", "viewing_hours_mm", "cpm_usd", "incremental_revenue_mm"]
MAD_K = 3.0          # sensitivity of the threshold
FLOOR = 0.05         # never flag variances under 5%
SEED = 7


def plan_kpis(g, d):
    """Quarterly plan for Years 1-2 of the Base case (flows split evenly across quarters)."""
    plan = []
    for yr in (1, 2):
        grow = (1 + d["growth"]) ** (yr - 1)
        subs, hours = d["subs"] * grow, d["hours"] * grow
        ad = hours * g["admin"] * g["spots"] * d["cpm"] / 1000 * g["fill"]
        incr = subs * g["price"] * (1 - g["fee"]) + ad * (1 - d["cannib"])
        for _ in range(4):
            plan.append({"subscribers_mm": subs, "viewing_hours_mm": hours / 4,
                         "cpm_usd": d["cpm"], "incremental_revenue_mm": incr / 4})
    return plan


def simulate_actuals(plan, g, d):
    """Driver KPIs = plan x small random noise, plus three injected shocks to test the flagging logic.
    Incremental revenue is then rebuilt from the simulated drivers, so driver shocks flow through to revenue."""
    rng = random.Random(SEED)
    shocks = {("Y1Q3", "subscribers_mm"): -0.15,     # documented in event log
              ("Y2Q1", "cpm_usd"): -0.18,            # NOT documented -> must route to review
              ("Y2Q3", "viewing_hours_mm"): 0.20}    # documented in event log
    actuals = []
    for q, p in zip(QUARTERS, plan):
        row = {k: p[k] * (1 + rng.gauss(0, 0.02) + shocks.get((q, k), 0.0)) for k in KPIS[:3]}
        ad = row["viewing_hours_mm"] * g["admin"] * g["spots"] * row["cpm_usd"] / 1000 * g["fill"]
        row["incremental_revenue_mm"] = row["subscribers_mm"] * g["price"] * (1 - g["fee"]) / 4 + ad * (1 - d["cannib"])
        actuals.append(row)
    return actuals


def load_event_log():
    with open(DATA / "event_log.csv", newline="") as f:
        return {(r["quarter"], r["kpi"]): r["driver"] for r in csv.DictReader(f)}


def mad_threshold(values):
    med = st.median(values)
    mad = st.median([abs(v - med) for v in values])
    return max(FLOOR, med + MAD_K * 1.4826 * mad)


def analyze(plan, actuals, events):
    rows = []
    for k in KPIS:
        pct = [(a[k] - p[k]) / p[k] for p, a in zip(plan, actuals)]
        for i, q in enumerate(QUARTERS):
            others = [abs(v) for j, v in enumerate(pct) if j != i]   # leave-one-out
            thr = mad_threshold(others)
            flag = abs(pct[i]) > thr
            upstream = [f"{kk}: {events[(q, kk)]}" for kk in KPIS[:3] if (q, kk) in events]
            if not flag:
                status, comment = "On track", ""
            elif (q, k) in events:
                status, comment = "Explained", events[(q, k)]
            elif k == "incremental_revenue_mm" and upstream and not any(
                    r["quarter"] == q and r["status"] == "Route to analyst review" for r in rows):
                status, comment = "Explained", "Flows from documented driver - " + "; ".join(upstream)
            else:
                status, comment = "Route to analyst review", "No documented driver - cause not assumed"
            rows.append({"quarter": q, "kpi": k, "plan": round(plan[i][k], 3), "actual": round(actuals[i][k], 3),
                         "variance_pct": round(pct[i], 4), "threshold_pct": round(thr, 4),
                         "flag": "FLAG" if flag else "OK", "status": status, "commentary": comment})
    return rows


def chart(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    for ax, k in zip(axes.flat, KPIS):
        r = [x for x in rows if x["kpi"] == k]
        colors = ["#4f81bd" if x["flag"] == "OK" else ("#9bbb59" if x["status"] == "Explained" else "#c0504d") for x in r]
        ax.bar(QUARTERS, [x["variance_pct"] * 100 for x in r], color=colors)
        ax.plot(QUARTERS, [x["threshold_pct"] * 100 for x in r], "k--", lw=0.8)
        ax.plot(QUARTERS, [-x["threshold_pct"] * 100 for x in r], "k--", lw=0.8)
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(k.replace("_", " "))
        ax.set_ylabel("Variance vs plan (%)")
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle("Actual vs. business case: blue = on track, green = flagged & explained, red = routed to review")
    fig.tight_layout(); fig.savefig(OUT / "variance_tracking.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    g, scen = load_inputs(XLSX)
    plan = plan_kpis(g, scen["Base"])
    actuals = simulate_actuals(plan, g, scen["Base"])
    with open(DATA / "quarterly_actuals_simulated.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter"] + KPIS)
        for q, a in zip(QUARTERS, actuals):
            w.writerow([q] + [round(a[k], 3) for k in KPIS])
    rows = analyze(plan, actuals, load_event_log())
    with open(OUT / "variance_report.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    chart(rows)
    flagged = [r for r in rows if r["flag"] == "FLAG"]
    print(f"{len(rows)} KPI-quarters checked, {len(flagged)} flagged "
          f"({sum(r['status'] == 'Explained' for r in flagged)} explained, "
          f"{sum(r['status'] != 'Explained' for r in flagged)} routed to review):")
    for r in flagged:
        print(f"  {r['quarter']} {r['kpi']:<24} {r['variance_pct']:+.1%} (threshold {r['threshold_pct']:.1%}) "
              f"-> {r['status']}: {r['commentary']}")
