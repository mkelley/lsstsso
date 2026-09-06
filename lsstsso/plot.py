import astropy.units as u
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from astropy.time import Time

from .band import Band

markers = {
    Band.u: {
        "color": "tab:blue",
        "marker": "v",
    },
    Band.g: {
        "color": "tab:green",
        "marker": "o",
    },
    Band.r: {
        "color": "tab:orange",
        "marker": "s",
    },
    Band.i: {
        "color": "tab:red",
        "marker": "^",
    },
    Band.z: {
        "color": "tab:pink",
        "marker": "<",
    },
    Band.y: {
        "color": "tab:purple",
        "marker": ">",
    },
}


def color_to_labels(anchor: Band, color: dict[Band, float]):
    labels = {}

    for band in Band:
        if band < anchor:
            label = f"${band}{color[band]:+.2f}$"
        elif band == anchor:
            label = "${band}$"
        else:
            label = f"${band}{color[band]:+.2f}$"

        labels[band] = label

    return labels


def lightcurve(
    t: Time | u.Quantity,
    m: u.Quantity,
    unc: u.Quantity,
    bands: np.ndarray[Band],
    ax: mpl.axes.Axes = None,
    labels: dict[Band, str] = None,
    **kwargs,
):
    """Plot a lightcurve in magnitudes."""

    if ax is None:
        ax = plt.gca()

    labels = {
        Band.u: {"label": "$u$"},
        Band.g: {"label": "$g$"},
        Band.r: {"label": "$r$"},
        Band.i: {"label": "$i$"},
        Band.z: {"label": "$z$"},
        Band.y: {"label": "$y$"},
    }

    default_opts = {
        "markersize": 7,
        "linestyle": "none",
        "alpha": 0.66,
    }

    for band in Band:
        i = (bands == band) * np.isfinite(m)
        if not any(i):
            continue

        opts = default_opts | markers[band] | labels[band] | kwargs

        ax.errorbar(t[i], m[i], unc[i], **opts)
