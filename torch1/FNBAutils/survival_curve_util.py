import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from lifelines import KaplanMeierFitter


def plot_survival_curve(duration_months, event_observed, label="All loans", save_path=None, ax=None):
    """Fit and plot a Kaplan-Meier survival curve.

    Parameters
    ----------
    duration_months : pd.Series: total observed months per loan
    event_observed  : pd.Series: 1 if the loan prepaid, 0 if right-censored
    label           : legend label for the KM line
    save_path       : if given, save the figure to this path
    ax              : existing Axes to draw on; if None a new figure is created

    Returns
    -------
    (fig, ax, kmf)
    """
    kmf = KaplanMeierFitter()
    kmf.fit(durations=duration_months, event_observed=event_observed, label=label)

    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.get_figure()

    kmf.plot_survival_function(ax=ax, ci_show=True, color="steelblue", linewidth=2)

    median_t = kmf.median_survival_time_
    ax.axvline(median_t, color="steelblue", linestyle=":", linewidth=1, alpha=0.6)
    ax.text(median_t + 1, 0.52, f"Median: {median_t:.0f} mo", color="steelblue", fontsize=9)

    ax.set_xlabel("Loan age (months)", fontsize=12)
    ax.set_ylabel("S(t)  -  P(no prepayment by month t)", fontsize=12)
    ax.set_title("Kaplan-Meier survival curve", fontsize=13, fontweight="normal")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10)

    if standalone:
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches="tight", dpi=130)
        plt.show()

    return fig, ax, kmf


def summary(duration_months, event_observed, label="All loans"):
    """Return a summary dictionary of KM statistics.

    Parameters
    ----------
    duration_months : pd.Series - total observed months per loan
    event_observed  : pd.Series - 1 if the loan prepaid, 0 if right-censored
    label           : legend label passed to the internal KM fit

    Returns
    -------
    dict with keys: total_loans, events, event_rate, censored, censored_rate,
                    median_survival_months, s_at_12mo, s_at_60mo, s_at_120mo
    """
    kmf = KaplanMeierFitter()
    kmf.fit(durations=duration_months, event_observed=event_observed, label=label)

    return {
        "total_loans":              len(duration_months),
        "events":                   int(event_observed.sum()),
        "event_rate":               float(event_observed.mean()),
        "censored":                 int((event_observed == 0).sum()),
        "censored_rate":            float((event_observed == 0).mean()),
        "median_survival_months":   float(kmf.median_survival_time_),
        "s_at_12mo":                float(kmf.survival_function_at_times(12).values[0]),
        "s_at_60mo":                float(kmf.survival_function_at_times(60).values[0]),
        "s_at_120mo":               float(kmf.survival_function_at_times(120).values[0]),
    }
