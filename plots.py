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


B0 = 14

fastB = df[(df["mode"] == "fast") & (df["B"] == B0)].copy()

m_fast = fastB.groupby("t")[["F0_true", "F0_est"]].mean()

plt.figure(figsize=(10, 5))

true_line = m_fast["F0_true"]
plt.plot(
    true_line.index,
    true_line.values,
    label="F0 true",
    linewidth=3,
    color="black"
)

plt.plot(
    m_fast.index,
    m_fast["F0_est"],
    linestyle="--",
    label=f"estimate fast (B={B0})"
)

y_min = min(true_line.min(), m_fast["F0_est"].min())
y_max = max(true_line.max(), m_fast["F0_est"].max())
pad = 0.03 * (y_max - y_min + 1e-9)
plt.ylim(y_min - pad, y_max + pad)

plt.xlabel("Processed elements")
plt.ylabel("Unique count")
plt.title(f"ZOOM: True vs HLL estimate (FAST, B={B0})")
plt.grid(True)
plt.legend()
plt.show()


fastB["rel_err"] = (fastB["F0_est"] - fastB["F0_true"]) / fastB["F0_true"]

stats_fast = fastB.groupby("t")["rel_err"]

mean_fast = stats_fast.mean()
std_fast = stats_fast.std()

plt.figure(figsize=(10, 5))

plt.plot(
    mean_fast.index,
    mean_fast.values,
    linestyle="--",
    label=f"fast mean error (B={B0})"
)

plt.fill_between(
    mean_fast.index,
    mean_fast - std_fast,
    mean_fast + std_fast,
    alpha=0.2
)

all_min = (mean_fast - std_fast).min()
all_max = (mean_fast + std_fast).max()
pad = 0.2 * (all_max - all_min + 1e-9)
plt.ylim(all_min - pad, all_max + pad)

plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Processed elements")
plt.ylabel("Relative error")
plt.title(f"ZOOM: Relative error (FAST, B={B0})")
plt.grid(True)
plt.legend()
plt.show()


plt.axhline(0, color="black", linestyle="--")
plt.xlabel("Processed elements")
plt.ylabel("Relative error")
plt.title("ZOOM: Relative error (B=10)")
plt.grid(True)
plt.legend()
plt.show()

