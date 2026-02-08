import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("results.csv")


def plot_true_vs_est(mode, B_list, title):
    plt.figure(figsize=(10, 5))

    base = df[(df["mode"] == mode) & (df["B"] == B_list[0])]
    true_line = base.groupby("t")["F0_true"].mean()
    plt.plot(
        true_line.index,
        true_line.values,
        label="F0 true",
        linewidth=3,
        color="black"
    )

    for B in B_list:
        sub = df[(df["mode"] == mode) & (df["B"] == B)]
        est = sub.groupby("t")["F0_est"].mean()
        plt.plot(est.index, est.values, label=f"estimate (B={B})")

    plt.xlabel("Processed elements")
    plt.ylabel("Unique count")
    plt.title(title)
    plt.grid(True)
    plt.legend(ncol=2, fontsize=9)
    plt.show()


plot_true_vs_est(
    mode="slow",
    B_list=[4, 6, 8, 10, 12],
    title="True vs HyperLogLog estimate (SLOW, different B)"
)

plot_true_vs_est(
    mode="fast",
    B_list=[4, 6, 8, 10, 12, 14, 16],
    title="True vs HyperLogLog estimate (FAST, different B)"
)



plt.figure(figsize=(11, 6))

for mode in ["slow", "fast"]:
    for B in sorted(df[df["mode"] == mode]["B"].unique()):
        sub = df[(df["mode"] == mode) & (df["B"] == B)].copy()

        sub["rel_err"] = (sub["F0_est"] - sub["F0_true"]) / sub["F0_true"]

        grouped = sub.groupby("t")["rel_err"]
        mean = grouped.mean()
        std = grouped.std()

        linestyle = "-" if mode == "slow" else "--"

        plt.plot(
            mean.index,
            mean.values,
            linestyle=linestyle,
            label=f"{mode} B={B}"
        )

        plt.fill_between(
            mean.index,
            mean - std,
            mean + std,
            alpha=0.12
        )

plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Processed elements")
plt.ylabel("Relative error")
plt.title("Mean relative error (slow vs fast, all B)")
plt.grid(True)
plt.legend(ncol=2, fontsize=8)
plt.show()


B0 = 10

slow10 = df[(df["mode"] == "slow") & (df["B"] == B0)].copy()
fast10 = df[(df["mode"] == "fast") & (df["B"] == B0)].copy()

m_slow10 = slow10.groupby("t")[["F0_true", "F0_est"]].mean()
m_fast10 = fast10.groupby("t")[["F0_true", "F0_est"]].mean()

plt.figure(figsize=(10, 5))

true_line = m_slow10["F0_true"]
plt.plot(true_line.index, true_line.values, label="F0 true", linewidth=3, color="black")

plt.plot(m_slow10.index, m_slow10["F0_est"], label="estimate slow (B=10)")
plt.plot(m_fast10.index, m_fast10["F0_est"], linestyle="--", label="estimate fast (B=10)")

y_min = min(true_line.min(), m_slow10["F0_est"].min(), m_fast10["F0_est"].min())
y_max = max(true_line.max(), m_slow10["F0_est"].max(), m_fast10["F0_est"].max())
pad = 0.03 * (y_max - y_min + 1e-9)
plt.ylim(y_min - pad, y_max + pad)

plt.xlabel("Processed elements")
plt.ylabel("Unique count")
plt.title("ZOOM: True vs HLL estimate (B=10)")
plt.grid(True)
plt.legend()
plt.show()


slow10["rel_err"] = (slow10["F0_est"] - slow10["F0_true"]) / slow10["F0_true"]
fast10["rel_err"] = (fast10["F0_est"] - fast10["F0_true"]) / fast10["F0_true"]

stats_slow = slow10.groupby("t")["rel_err"]
stats_fast = fast10.groupby("t")["rel_err"]

mean_slow = stats_slow.mean()
std_slow = stats_slow.std()

mean_fast = stats_fast.mean()
std_fast = stats_fast.std()

plt.figure(figsize=(10, 5))

plt.plot(mean_slow.index, mean_slow.values, label="slow mean error (B=10)")
plt.fill_between(mean_slow.index, mean_slow - std_slow, mean_slow + std_slow, alpha=0.2)

plt.plot(mean_fast.index, mean_fast.values, linestyle="--", label="fast mean error (B=10)")
plt.fill_between(mean_fast.index, mean_fast - std_fast, mean_fast + std_fast, alpha=0.2)

all_min = min((mean_slow - std_slow).min(), (mean_fast - std_fast).min())
all_max = max((mean_slow + std_slow).max(), (mean_fast + std_fast).max())
pad = 0.2 * (all_max - all_min + 1e-9)
plt.ylim(all_min - pad, all_max + pad)

plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Processed elements")
plt.ylabel("Relative error")
plt.title("ZOOM: Relative error (B=10)")
plt.grid(True)
plt.legend()
plt.show()

