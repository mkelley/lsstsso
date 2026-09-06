import argparse

import astropy.constants as const
import astropy.units as u
import lsstsso
import matplotlib.pyplot as plt
import numpy as np
from lsstsso import Band, scale
from numpy import pi

parser = argparse.ArgumentParser()
parser.add_argument("ssobjectid")
args = parser.parse_args()

rsp = lsstsso.RSP()

sso = lsstsso.get.ssobject(rsp, f"ssObjectId = {args.ssobjectid}")[0]
source = lsstsso.get.lightcurve(rsp, args.ssobjectid)
orbit = lsstsso.get.orbit(rsp, sso.designation)[0]

bands = source.band
m = source.apFlux.to_value(u.ABmag)
m_unc = 1.0857 * (source.apFluxErr / source.apFlux)

# My favorite aliases
rh = source.helioRange
delta = source.topoRange
phase = source.phaseAngle

tmtp = (source.midpointMjdTai - orbit.peri_time).jd

if orbit.e < 0.95:
    a = orbit.q / (1 - orbit.e)
    P = (2 * pi * np.sqrt(a**3 / const.GM_sun)).to("day")

Hy = m + scale.geometry(rh, delta, phase) + scale.activity(rh, delta, -2, -1)
color, color_unc = scale.color(Hy, m_unc, bands)
C = np.array([color[band] for band in bands])

fig, axes = plt.subplots(3, 1, num=1, figsize=(7, 10), clear=True)

for band in Band:
    i = (source["band"] == band) * np.isfinite(m)
    if not any(i):
        continue

    opts = dict(
        markersize=7,
        linestyle="none",
        alpha=0.66,
        **lsstsso.plot.markers[band],
    )

    axes[0].errorbar(tmtp[i], m[i], m_unc[i], label=f"${band}$", **opts)

    if band < Band.r:
        label = f"${band}{color[band]:+.2f}$"
    elif band == Band.r:
        label = "$r$"
    else:
        label = f"${band}{color[band]:+.2f}$"

    axes[1].errorbar(tmtp[i], m[i] + C[i], m_unc[i], label=label, **opts)

    axes[2].errorbar(tmtp[i], Hy[i] + C[i], m_unc[i], label=label, **opts)


axes[0].set(ylabel="m (mag)")
axes[1].set(ylabel="r (mag)")
axes[2].set(ylabel="Hy (mag)")
axes[2].set(xlabel=f"T-Tp (days, Tp={orbit.peri_time.utc.mjd:.2f} UTC)")

for ax in axes:
    ax.legend()
    ax.invert_yaxis()
    ax.minorticks_on()

plt.tight_layout()
