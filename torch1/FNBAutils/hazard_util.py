import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from lifelines import NelsonAalenFitter


def _make_loan_idx(t):
    """Derive 0-based loan index from t, treating t==1 as the start of each new loan."""
    return (t == 1).cumsum() - 1


def _build_at_risk_table(t, event_this_month, loan_idx, horizon):
    df = pd.DataFrame({"t": t, "event_this_month": event_this_month, "loan_idx": loan_idx})
    at_risk = (
        df[df["t"] <= horizon]
        .groupby("t")
        .agg(
            n_at_risk=("loan_idx", "nunique"),
            n_events=("event_this_month", "sum"),
        )
        .reset_index()
    )
    at_risk["hazard_raw"] = at_risk["n_events"] / at_risk["n_at_risk"]
    at_risk["hazard_smoothed"] = (
        at_risk["hazard_raw"]
        .rolling(window=6, center=True, min_periods=1)
        .mean()
    )
    return at_risk


def _fit_nelson_aalen(duration_months, event_observed):
    naf = NelsonAalenFitter()
    naf.fit(durations=duration_months, event_observed=event_observed)
    return naf


def plot_hazard(t, event_this_month, duration_months, event_observed, mode, loan_idx=None, horizon=None, save_path=None):
    """Plot either the empirical h(t) or the Nelson-Aalen cumulative H(t).

    Parameters
    ----------
    t                : pd.Series - 1-based month index within each loan's history
    event_this_month : pd.Series - 1 if the prepayment event occurred this month, else 0
    duration_months  : pd.Series - loan-level total observed months (one value per loan)
    event_observed   : pd.Series - loan-level flag; 1 if the loan prepaid, 0 if right-censored
    mode             : 'empirical'  - plot monthly h(t) bar chart with smoothed overlay
                       'cumulative' - plot Nelson-Aalen cumulative H(t)
    loan_idx         : pd.Series - integer loan identifier; derived from t if None
    horizon          : cap the x-axis at this many months; defaults to max(duration_months)
    save_path        : if given, save the figure to this path

    Returns
    -------
    (fig, ax, at_risk) for mode='empirical'
    (fig, ax, naf)     for mode='cumulative'
    """
    if loan_idx is None:
        loan_idx = _make_loan_idx(t)

    if horizon is None:
        horizon = int(max(duration_months))

    fig, ax = plt.subplots(figsize=(10, 5))

    match mode:
        case "empirical":
            at_risk = _build_at_risk_table(t, event_this_month, loan_idx, horizon)

            ax.bar(
                at_risk["t"], at_risk["hazard_raw"] * 100,
                color="#7F77DD", alpha=0.35, width=1.0, label="Monthly h(t)",
            )
            ax.plot(
                at_risk["t"], at_risk["hazard_smoothed"] * 100,
                color="tomato", linewidth=2, label="Smoothed (6-mo window)",
            )

            peak_idx = at_risk["hazard_smoothed"].idxmax()
            peak_t = at_risk.loc[peak_idx, "t"]
            peak_h = at_risk.loc[peak_idx, "hazard_smoothed"] * 100
            ax.annotate(
                f"Peak: month {peak_t:.0f}\n({peak_h:.2f}%/mo)",
                xy=(peak_t, peak_h),
                xytext=(peak_t + 15, peak_h * 1.3),
                fontsize=9, color="tomato",
                arrowprops=dict(arrowstyle="->", color="tomato", lw=1.2),
            )

            ax.set_ylabel("h(t)  —  monthly hazard rate (%)", fontsize=11)
            ax.set_title(f"Empirical hazard rate h(t) (capped at {horizon} months)", fontsize=12, fontweight="normal")
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f%%"))
            ax.set_xlim(0, horizon)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=10)

            plt.tight_layout()
            if save_path:
                plt.savefig(save_path, bbox_inches="tight", dpi=130)
            plt.show()

            return fig, ax, at_risk

        case "cumulative":
            naf = _fit_nelson_aalen(duration_months, event_observed)
            naf_trimmed = naf.cumulative_hazard_[naf.cumulative_hazard_.index <= horizon]

            ax.plot(
                naf_trimmed.index, naf_trimmed.values,
                color="steelblue", linewidth=2, label="Cumulative H(t)",
            )
            ax.fill_between(naf_trimmed.index, naf_trimmed.values.flatten(), alpha=0.1, color="steelblue")

            ax.set_ylabel("H(t)  —  cumulative hazard", fontsize=11)
            ax.set_xlabel("Loan age (months)", fontsize=12)
            ax.set_title("Nelson-Aalen cumulative hazard H(t)", fontsize=12, fontweight="normal")
            ax.set_xlim(0, horizon)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=10)

            plt.tight_layout()
            if save_path:
                plt.savefig(save_path, bbox_inches="tight", dpi=130)
            plt.show()

            return fig, ax, naf

        case _:
            raise ValueError(f"mode must be 'empirical' or 'cumulative', got {mode!r}")


def summary(duration_months, event_observed, t, event_this_month, loan_idx=None, horizon=180):
    """Return a summary dictionary of hazard statistics.

    Parameters
    ----------
    duration_months  : pd.Series - loan-level total observed months (one value per loan)
    event_observed   : pd.Series - loan-level flag; 1 if the loan prepaid, 0 if right-censored
    t                : pd.Series - 1-based month index within each loan's history
    event_this_month : pd.Series - 1 if the prepayment event occurred this month, else 0
    loan_idx         : pd.Series - integer loan identifier; derived from t if None
    horizon          : months cap used when computing the at-risk table

    Returns
    -------
    dict with keys: loans_in_sample, loan_months_in_panel, peak_hazard_month,
                    peak_hazard_rate, h_at_60mo, h_at_120mo
    """
    if loan_idx is None:
        loan_idx = _make_loan_idx(t)

    at_risk = _build_at_risk_table(t, event_this_month, loan_idx, horizon)
    naf = _fit_nelson_aalen(duration_months, event_observed)

    peak_idx = at_risk["hazard_smoothed"].idxmax()

    return {
        "loans_in_sample":      int(loan_idx.nunique()),
        "loan_months_in_panel": int(len(t)),
        "peak_hazard_month":    int(at_risk.loc[peak_idx, "t"]),
        "peak_hazard_rate":     float(at_risk.loc[peak_idx, "hazard_smoothed"] * 100),
        "h_at_60mo":            float(naf.cumulative_hazard_at_times([60]).values[0]),
        "h_at_120mo":           float(naf.cumulative_hazard_at_times([120]).values[0]),
    }
