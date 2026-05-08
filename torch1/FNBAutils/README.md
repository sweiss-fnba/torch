# This file is documentation for the FNBAutils library

**Purpose: The FNBAutils library was designed to automate and standardize certain tasks which are common in the workflow of the FNBA AI/ML team. They are useful for saving development time and keeping us all "speaking the same language" as the project grows.**

# Table of Contents:
- §0 Template Specifications
- §0.1 Template 1: Loan-Grain Specification
- §0.2 Template 2: Month-Grain Specification
- §1 Transformation Utilities
- §1.1 FMAC_data_transformation
- §1.2 FNBA_data_transformation
- §1.3 bit_tape_transformation
- §2 Visualization Utilities
- §2.1 survival_curve_util
- §2.2 hazard_util
- §3 Testing Utilities

# §0 Template Specifications
- All utilities in this library will ONLY work on data which is in a compatible form with the given utility. 
- To ensure no issues before using a function from this library, make sure your data matches the appropriate template:

## §0.1 Template 1: Loan-Grain Specification
- Data saved in this form follows the file name convention: *_loan_grain.ext
- The first column is "duration_months": the total number of months the loan was observed, either until the prepayment event or until censoring (e.g. maturity, payoff, end of study)
- The second column is "event_observed": binary flag == 1 if the loan prepaid (event occurred), == 0 if right-censored
- The data must be "loan grain", meaning that each row contains a unique loan.

## §0.2 Template 2: Month-Grain Specification
- Data saved in this form follows the file name convention: *_month_grain.ext
- The first column is "duration_months": the total number of months the loan was observed, either until the prepayment event or until censoring (e.g. maturity, payoff, end of study)
- The second column is "event_observed": binary flag == 1 if the loan prepaid (event occurred), == 0 if right-censored
- The third column is "t": the 1-based month index within this loan's panel history, running from 1 to duration_months
- The fourth column is "event_this_month": binary flag - 1 if the prepayment event occurred in this specific month t, 0 otherwise; exactly one row per loan will have a 1 (the terminal row, only if event_observed == 1)
- The data must be "month grain", meaning that each row contains a unique month of each loans life.

# §1 Transformation Utilities
These utilities are used for transforming data of a given source into the form that matches one of our pre-specified templates:

## §1.1 FMAC_data_transformation
### §1.1.1 Spec


## §1.2 FNBA_data_transformation
### §1.2.1 Spec
TODO not implemented, no code (yet)

## §1.3 bit_tape_transformation
### §1.3.1 Spec
TODO not implemented, no code (yet)

# §2 Visualization Utilities
These utilities are used for visualizing and retrieving summary statistics for mathematical equations which are common to our problem

## §2.1 survival_curve_util
### §2.1.1 Spec
This util expects loan grain conforming data (see §0.1 Template 1)

### §2.1.2 Recap on survival functions and what this program is visualizing:
Per Wikipedia, the definition of the survival function is: 

"Let the lifetime $T$ be a continuous random variable describing the time to failure. If $T$ has 
**cumulative distribution function** $F(t)$ and **probability density function** $f(t)$ on the 
interval $[0, \infty)$, then the *survival function* or *reliability function* is:

$$S(t) = \int_t^{\infty} f(u)\, du = \Pr(T > t) = 1 - F(t) = 1 - \int_0^t f(u)\, du$$
"

You can read more here "https://en.wikipedia.org/wiki/Survival_function"

### §2.1.3 Uses
This util fits compatible data to a KaplanMeierFitter(). It can then be used to plot survival curves and display them dynamically (or save them to a .png). It can also return summary information about the fitted kmf.

## §2.2 hazard_util
### §2.2.1 Spec
This util expects month grain conforming data (see §0.2 Template 2)

### §2.2.2 Recap 
read §2.1.2 before you read this section

- The survival function can be related to the probability density function $f(t)$ and the hazard function $\lambda(t)$
  - $f(t) = -S'(t)$
  - $\lambda(t) = -\dfrac{d}{dt} \log S(t)$

So that $S(t) = \exp\left[-\int_0^t \lambda(t')\, dt'\right]$

- The expected survival time $\mathbb{E}(T) = \int_0^{\infty} S(t)\, dt$

You can read more here "https://en.wikipedia.org/wiki/Survival_function"

### §2.2.3 Uses
This util fits compatible data to a NelsonAalenFitter(). It can then be used to plot hazard curves and display them dynamically (or save them to a .png). These plots can either be created to visualize the empirical (or instant) hazard rate over t or the cumulative hazard curve over t. It can also return summary information about the fitted naf.

# §3 Testing Utilities
