from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
OUT = ROOT / "outputs" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

country = pd.read_csv(P / "tb_country_year.csv")
agg = pd.read_csv(P / "tb_aggregates_year.csv")
age = pd.read_csv(P / "tb_age_sex_2024.csv")

global_df = agg[(agg.geo_level == "Global") & (agg.geography == "Global")].sort_values("year")

NAVY = "#0B1F33"
TEAL = "#0E7490"
MINT = "#14B8A6"
CORAL = "#E76F51"
GOLD = "#F4A261"
SLATE = "#64748B"
PALE = "#EEF6F8"
GRID = "#DCE7EC"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 19,
    "axes.titleweight": "bold",
    "axes.labelcolor": NAVY,
    "axes.edgecolor": GRID,
    "xtick.color": SLATE,
    "ytick.color": SLATE,
    "text.color": NAVY,
    "axes.facecolor": "white",
    "figure.facecolor": "white",
})


def finish(fig, name: str, tight=True):
    if tight:
        fig.tight_layout()
    fig.savefig(OUT / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# 1. Global burden and notifications
fig, ax = plt.subplots(figsize=(12.5, 6.8))
x = global_df.year
inc = global_df.e_inc_num / 1e6
notif = global_df.c_newinc / 1e6
ax.fill_between(x, notif, inc, color=CORAL, alpha=.14, label="Estimated notification difference")
ax.plot(x, inc, color=CORAL, linewidth=3, marker="o", markersize=3.5, label="Estimated incident TB")
ax.plot(x, notif, color=TEAL, linewidth=3, marker="o", markersize=3.5, label="Notified new and relapse")
ax.axvline(2020, color=SLATE, linewidth=1.2, linestyle="--")
ax.text(2020.2, 4.0, "2020 service disruption", color=SLATE, fontsize=10, rotation=90, va="bottom")
ax.scatter([2024], [inc.iloc[-1]], s=70, color=CORAL, zorder=5)
ax.scatter([2024], [notif.iloc[-1]], s=70, color=TEAL, zorder=5)
ax.annotate(f"{inc.iloc[-1]:.2f}M estimated", (2024, inc.iloc[-1]), xytext=(-112, 16), textcoords="offset points", color=CORAL, fontweight="bold")
ax.annotate(f"{notif.iloc[-1]:.2f}M notified", (2024, notif.iloc[-1]), xytext=(-105, -26), textcoords="offset points", color=TEAL, fontweight="bold")
ax.set_title("Global TB burden and notified cases, 2000–2024", loc="left", pad=18)
ax.text(0, 1.015, "The gap narrowed substantially, but an estimated 2.22 million-case difference remained in the reproducible 2024 snapshot.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_ylabel("People (millions)")
ax.set_xlabel("")
ax.set_ylim(0, max(inc) * 1.12)
ax.grid(axis="y", color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.10))
finish(fig, "global_burden_notifications.png")

# 2. Global rates
fig, ax = plt.subplots(figsize=(12.5, 6.8))
ax.plot(x, global_df.e_inc_100k, color=NAVY, linewidth=3, marker="o", markersize=3.5, label="Incidence rate")
ax.plot(x, global_df.e_mort_100k, color=GOLD, linewidth=3, marker="o", markersize=3.5, label="Mortality rate")
ax.axvspan(2020, 2021, color=PALE, alpha=.9)
ax.text(2020.5, 179, "COVID-19\nperiod", ha="center", color=SLATE, fontsize=10)
ax.annotate(f"{global_df.e_inc_100k.iloc[-1]:.1f}", (2024, global_df.e_inc_100k.iloc[-1]), xytext=(-38, 12), textcoords="offset points", color=NAVY, fontweight="bold")
ax.annotate(f"{global_df.e_mort_100k.iloc[-1]:.1f}", (2024, global_df.e_mort_100k.iloc[-1]), xytext=(-34, -22), textcoords="offset points", color=GOLD, fontweight="bold")
ax.set_title("Global TB incidence and mortality rates declined, but progress remains insufficient", loc="left", pad=18)
ax.text(0, 1.015, "From 2015 to 2024, the project snapshot shows a 12.3% decline in incidence rate and a 36.7% decline in mortality rate.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_ylabel("Rate per 100,000 population")
ax.set_ylim(0, 210)
ax.grid(axis="y", color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
finish(fig, "global_rates.png")

# 3. Top notification differences
snap = country[country.year == 2024].dropna(subset=["notification_gap_num_nonnegative"]).nlargest(10, "notification_gap_num_nonnegative").sort_values("notification_gap_num_nonnegative")
fig, ax = plt.subplots(figsize=(12.5, 7.2))
vals = snap.notification_gap_num_nonnegative / 1000
bars = ax.barh(snap.country, vals, color=TEAL, alpha=.92)
for bar, (_, r) in zip(bars, snap.iterrows()):
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.0f}K  |  {r.c_cdr:.0f}% coverage", va="center", fontsize=10, color=NAVY)
ax.set_title("Largest estimated notification differences, 2024", loc="left", pad=18)
ax.text(0, 1.015, "Difference = estimated incident cases minus notified new and relapse cases; it is not proof that every person was untreated.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_xlabel("Estimated difference (thousands of people)")
ax.set_ylabel("")
ax.set_xlim(0, vals.max() * 1.38)
ax.grid(axis="x", color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
finish(fig, "country_notification_gaps_2024.png")

# 4. Region profile bubble chart
reg = agg[(agg.geo_level == "WHO region") & (agg.year == 2024)].copy()
fig, ax = plt.subplots(figsize=(12.5, 7.2))
region_colors = [TEAL, MINT, CORAL, GOLD, NAVY, "#7C3AED"]
for (_, r), c in zip(reg.sort_values("e_inc_num", ascending=False).iterrows(), region_colors):
    size = 220 + 1200 * r.e_inc_num / reg.e_inc_num.max()
    ax.scatter(r.e_inc_100k, r.c_cdr, s=size, color=c, alpha=.78, edgecolor="white", linewidth=1.5)
    ax.annotate(r.geography, (r.e_inc_100k, r.c_cdr), xytext=(5, 7), textcoords="offset points", fontsize=10, fontweight="bold")
ax.axhline(80, color=SLATE, linestyle="--", linewidth=1)
ax.text(28, 80.8, "80% coverage reference", color=SLATE, fontsize=9)
ax.set_title("WHO regions combine very different burden and coverage profiles", loc="left", pad=18)
ax.text(0, 1.015, "Bubble size represents estimated incident cases. Africa had the highest incidence rate; South-East Asia had the highest calculated coverage.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_xlabel("TB incidence per 100,000")
ax.set_ylabel("Calculated diagnosis and treatment coverage (%)")
ax.set_xlim(0, 230)
ax.set_ylim(68, 92)
ax.grid(color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
finish(fig, "who_region_profile_2024.png")

# 5. Age-sex pyramid
non = ["0_4", "5_9", "10_14", "15_19", "20_24", "25_34", "35_44", "45_54", "55_64", "65plus"]
order = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-34", "35-44", "45-54", "55-64", "65+"]
a = age[(age.age_group.isin(non)) & (age.sex.isin(["m", "f"]))]
piv = a.groupby(["age_group_label", "sex_label"]).e_inc_num.sum().unstack().reindex(order)
fig, ax = plt.subplots(figsize=(12.5, 7.2))
y = np.arange(len(order))
ax.barh(y, -piv["Female"] / 1000, color=CORAL, label="Female")
ax.barh(y, piv["Male"] / 1000, color=TEAL, label="Male")
ax.set_yticks(y, order)
ax.axvline(0, color=NAVY, linewidth=1)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{abs(v):.0f}K"))
ax.set_title("Estimated TB incidence by age and sex, 2024", loc="left", pad=18)
ax.text(0, 1.015, "The male burden exceeds the female burden in most adult age groups; total male-to-female ratio in this snapshot is about 1.50.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_xlabel("Estimated incident cases")
ax.grid(axis="x", color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
finish(fig, "age_sex_pyramid_2024.png")

# 6. TB-HIV and RR/MDR paired ranking
snap = country[country.year == 2024]
top_hiv = snap.dropna(subset=["e_inc_tbhiv_num"]).nlargest(8, "e_inc_tbhiv_num").sort_values("e_inc_tbhiv_num")
top_rr = snap.dropna(subset=["e_inc_rr_num"]).nlargest(8, "e_inc_rr_num").sort_values("e_inc_rr_num")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.4))
ax1.barh(top_hiv.country, top_hiv.e_inc_tbhiv_num / 1000, color="#7C3AED", alpha=.88)
ax1.set_title("HIV-associated TB", loc="left", fontsize=16)
ax1.set_xlabel("Estimated cases (thousands)")
ax1.grid(axis="x", color=GRID, linewidth=.8)
ax2.barh(top_rr.country, top_rr.e_inc_rr_num / 1000, color=CORAL, alpha=.9)
ax2.set_title("RR/MDR-TB", loc="left", fontsize=16)
ax2.set_xlabel("Estimated cases (thousands)")
ax2.grid(axis="x", color=GRID, linewidth=.8)
for ax in (ax1, ax2):
    ax.spines[["top", "right", "left"]].set_visible(False)
fig.suptitle("Two different high-risk dimensions require targeted responses", x=.06, ha="left", fontsize=19, fontweight="bold", color=NAVY)
fig.text(.06, .93, "HIV weakens immunity and increases progression to active TB; RR/MDR-TB reflects resistance to key medicines.", color=SLATE, fontsize=11)
fig.subplots_adjust(top=.84, wspace=.42, left=.13, right=.98, bottom=.10)
finish(fig, "hiv_rr_burden_2024.png", tight=False)

# 7. Lebanon exploratory forecast
name = "Lebanon"
fc = country[(country.country == name) & country.e_inc_100k.notna()].sort_values("year")[["year", "e_inc_100k"]].tail(12)
xv = fc.year.to_numpy(float)
yv = fc.e_inc_100k.to_numpy(float)
slope, intercept = np.polyfit(xv, yv, 1)
future = np.arange(int(fc.year.max()) + 1, int(fc.year.max()) + 4)
pred = np.maximum(slope * future + intercept, 0)
resid = yv - (slope * xv + intercept)
sd = np.std(resid, ddof=2)
fig, ax = plt.subplots(figsize=(12.5, 6.8))
ax.plot(xv, yv, color=TEAL, linewidth=3, marker="o", label="Observed")
ax.plot(future, pred, color=CORAL, linewidth=3, linestyle="--", marker="o", label="Exploratory linear projection")
ax.fill_between(future, np.maximum(pred - 1.96*sd, 0), pred + 1.96*sd, color=CORAL, alpha=.15, label="Approximate residual band")
ax.set_title("Illustrative three-year TB incidence-rate projection for Lebanon", loc="left", pad=18)
ax.text(0, 1.015, "This extrapolation is a dashboard bonus feature, not a causal or clinical forecast.", transform=ax.transAxes, color=SLATE, fontsize=11)
ax.set_ylabel("Cases per 100,000")
ax.set_xlabel("Year")
ax.grid(axis="y", color=GRID, linewidth=.8)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(.5, -.11))
finish(fig, "lebanon_exploratory_forecast.png")

print(f"Created {len(list(OUT.glob('*.png')))} charts in {OUT}")
