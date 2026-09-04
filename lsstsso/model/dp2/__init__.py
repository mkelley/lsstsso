"""DP2 data models.

Convered from schemas at sdm-schemas.lsst.io/dp2.html

* Download CSV and load into astropy table:

    for row in tab:
        print(row["Column Name"], ": ",
              (row["Data Type"] if row["Unit"] is np.ma.masked else "u.Quantity[u." + row["Unit"] + "]"),
              " = field(doc=\"", row["Description"], '")', sep="")

* Then edit as needed.

"""

from .diasource import DiaSource
from .ssobject import SSObject
from .sssource import SSSource
