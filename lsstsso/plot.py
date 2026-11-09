import astropy.units as u
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time

from .band import Band
from .color.color import Color
from .color.color_matrix import ColorMatrix
from .color.transform import transform

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


def colors_to_labels(
    anchor: Band, cm: ColorMatrix | None, default_cm: ColorMatrix | None
):
    labels = {}

    for band in Band:
        if (cm is None and default_cm is None) or band == anchor:
            color = None
        else:
            color = None
            try:
                # first use default color matrix
                color, _ = transform(0 * u.mag, 0 * u.mag, band, anchor, default_cm)
                color = color.value

                if cm is not None:
                    # now try provided color matrix
                    color, _ = transform(0 * u.mag, 0 * u.mag, band, anchor, cm)
                    color = color.value
            except ValueError:
                # at least one transformation failed, but this is OK, either
                # color will be `None` or the default color matrix was used
                pass

        if color is None or band == anchor:
            label = f"${band}$"
        else:
            label = f"${band}{color:+.2f}$"

        labels[band] = {"label": label}

    return labels


def lightcurve(
    t: Time | u.Quantity,
    m: u.Quantity,
    unc: u.Quantity,
    bands: np.ndarray[Band],
    anchor: Band | str = Band.r,
    cm: ColorMatrix | None = None,
    use_default_cm: bool = True,
    ax: mpl.axes.Axes = None,
    labels: dict[Band, str] | None = None,
    **kwargs,
):
    """Plot a lightcurve in magnitudes."""

    if ax is None:
        ax = plt.gca()

    if use_default_cm:
        default_cm = ColorMatrix(
            [
                Color("u", "g", 1.83 * u.mag, 0.05 * u.mag),
                Color("g", "r", 0.59 * u.mag, 0.01 * u.mag),
                Color("r", "i", 0.21 * u.mag, 0.01 * u.mag),
                Color("i", "z", 0.05 * u.mag, 0.01 * u.mag),
                Color("z", "y", 0.03 * u.mag, 0.01 * u.mag),
            ]
        )
    else:
        default_cm = None

    labels = colors_to_labels(Band(anchor), cm, default_cm)

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

        if cm is None or band == anchor:
            ax.errorbar(t[i], m[i], unc[i], **opts)
        else:
            try:
                a, aunc = transform(m[i], unc[i], band, anchor, cm)
            except ValueError:
                if default_cm:
                    a, aunc = transform(m[i], unc[i], band, anchor, default_cm)
                else:
                    a = m[i]
                    aunc = unc[i]
            ax.errorbar(t[i], a, aunc, **opts)
