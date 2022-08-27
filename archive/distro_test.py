import numpy as np
import matplotlib.pyplot as plt
import time
import math

from scipy import stats

from scipy.stats import (
    norm, beta, expon, gamma, genextreme, logistic, lognorm, triang, uniform, fatiguelife,
    gengamma, gennorm, dweibull, dgamma, gumbel_r, powernorm, rayleigh, weibull_max, weibull_min,
    laplace, alpha, genexpon, bradford, betaprime, burr, fisk, genpareto, hypsecant,
    halfnorm, halflogistic, invgauss, invgamma, levy, loglaplace, loggamma, maxwell,
    mielke, ncx2, ncf, nct, nakagami, pareto, lomax, powerlognorm, powerlaw,
    semicircular, trapezoid, rice, invweibull, foldnorm, foldcauchy, cosine, exponpow,
    exponweib, wald, wrapcauchy, truncexpon, truncnorm, t, rdist
    )

distributions = np.array([
    norm, beta, expon, gamma, genextreme, logistic, lognorm, triang, uniform, fatiguelife,
    gengamma, gennorm, dweibull, dgamma, gumbel_r, powernorm, rayleigh, weibull_max, weibull_min,
    laplace, alpha, genexpon, bradford, betaprime, burr, fisk, genpareto, hypsecant,
    halfnorm, halflogistic, invgauss, invgamma, levy, loglaplace, loggamma, maxwell,
    mielke, ncx2, ncf, nct, nakagami, pareto, lomax, powerlognorm, powerlaw,
    semicircular, trapezoid, rice, invweibull, foldnorm, foldcauchy, cosine, exponpow,
    exponweib, wald, wrapcauchy, truncexpon, truncnorm, t, rdist
])

ksN = 100           # Kolmogorov-Smirnov KS test for goodness of fit: samples
ALPHA = 0.05        # significance level for hypothesis test

# setup distro
distro_type = np.random.choice(distributions)
# distro = distro_type(1, 1)
# distro = gamma(1, 1)
# distro = norm(0, 2)
distro = beta(2, 6, loc=100, scale=220)

x = distro.rvs(size=1000)

# noinspection SpellCheckingInspection
moments_values = [v.item() for v in distro.stats(moments="mvsk")]
moments_values.append(distro.std())
moments_keys = ["mean", "var", "skew", "kurt", "std"]
moments = dict(zip(moments_keys, moments_values))

_ = [print(k, ":", f"{v:.3f}") for k, v in moments.items()]
print(f"sqrt_var = {math.sqrt(moments['var']):.3f}")

fig, ax = plt.subplots(1, 2)
fig.suptitle(f"{distro.dist.name}, mean: {moments['mean']}, variance: {moments['var']}")

ax[0].hist(x, density=True, histtype="stepfilled", alpha=0.2)
ax[0].set_title("Histogram")

# construct and draw pdf
lin_space_low = distro.ppf(0.01)
lin_space_high = distro.ppf(0.99)

x_values = np.linspace(lin_space_low, lin_space_high)
ax[1].plot(x_values, distro.pdf(x_values), "r")
ax[1].set_title("Probability density function")

# setup plot params
fig.subplots_adjust(wspace=1)
fig.tight_layout()
fig.canvas.manager.set_window_title('Histogram and probability density function')

# plot cdf and ppf
fig2, ax2 = plt.subplots(1, 2)
fig2.suptitle("Cumulative density function and percent point function")

ax2[0].plot(x_values, distro.cdf(x_values), "orange")
ax2[0].set_title("Cumulative density function")

q = np.linspace(0.0, 1.0, 100)
ax2[1].plot(q*100, distro.ppf(q), "b")
ax2[1].set_title("Percentage point function")

fig2.canvas.manager.set_window_title('CDF and PPF')

print(f"Support: {distro.support()}")

## distribution fitter
# set up parameters - shape, location, scale
shp, loc, scl = 1.5, 0.0, 50000.0

# create new distro
distro = weibull_min(c=shp, loc=loc, scale=scl)

# simulate data following weibull distro
data = distro.rvs(1000)

# display simulated data on histogram
fig, ax3 = plt.subplots(1, 1)
ax3.hist(data, density=True, histtype="stepfilled", alpha=0.2, label="distribution of sim. data")

# fit distribution
fit_distro_params = weibull_min.fit(data, floc=0)
param_names = ["shape", "loc", "scale"]
print("\nFitted distribution:")
_ = {print(f"{k} : {v:.3f}") for k, v in zip(param_names, fit_distro_params)}

fit_distro = weibull_min(c=fit_distro_params[0],
                         loc=fit_distro_params[1],
                         scale=fit_distro_params[2],
                         )

# show the pdfs for the original and the fitted distribution
x = np.linspace(distro.ppf(0.01),
                distro.ppf(0.99),
                100,
                )
fit_x = np.linspace(fit_distro.ppf(0.01),
                    fit_distro.ppf(0.99),
                    100,
                    )
ax3.plot(x, distro.pdf(x), "r-", label="pdf_original")
ax3.plot(fit_x, fit_distro.pdf(fit_x), "gx", label="pdf_fitted", alpha=0.5)
ax3.legend(loc="best")

plt.show()

# calculate goodness of fit
ks = stats.kstest(data,
                  weibull_min.name,
                  [shp, loc, scl],
                  ksN,
                  )

ks_p = ks[1]

ks_fit = stats.kstest(data,
                      weibull_min.name,
                      fit_distro_params,
                      ksN,
                      )

ks_fit_p = ks_fit[1]
print(f"\nOriginal distribution goodness of fit: {ks_p:.3f}\nFitted distribution goodness of fit: {ks_fit_p:.3f}")
