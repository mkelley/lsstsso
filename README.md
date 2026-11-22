# LSST SSO

Get and plot light curves of solar system objects observed by LSST with Python.

The data interface is designed in an attempt to be simple and useful in interactive sessions.  If you need something efficient or suitable for large scales, maybe try something else.

Features:
* Query caching.
* Convenience functions for common queries.
* Result objects designed for column-based and row-based inspection.
* Calculate colors with correlated uncertainties.
* Powered by [astropy](https://astropy.org/) and [sbpy](https://sbpy.org/)!

The API is advanced but not currently stable.

The convenience queries are currently hard-coded for DP2.

[![codecov](https://codecov.io/gh/mkelley/lsstsso/graph/badge.svg?token=43YF0G7O3K)](https://codecov.io/gh/mkelley/lsstsso) [![documentation](https://lsstsso.readthedocs.io/en/latest/)](https://app.readthedocs.org/projects/lsstsso/badge/?version=latest&style=flat)

## Installation and setup

1. Install as per usual, e.g., `pip install "git+https://github.com/mkelley/lsstsso.git#egg=lsstsso"`.

2. Get an API key for the Rubin Science Platform.  The key only needs read:tap permissions.

3. Save this key to an environment variable: LSST_SSO_RSP_TOKEN.

## Documentation

Full documentation is in ``docs/`` and the code doc-strings.  Compiled documentation is hosted at [lsstsso.readthedocs.io](https://lsstsso.readthedocs.io/).

## Brief demo

Get a list of comets in DP2:

```python
>>> import lsstsso
>>> comets = lsstsso.get.comets()
>>> comets
<Table length=47>
     ssObjectId     designation   nObs     arc     firstObservationMjdTai tisserand_J permid
                                            d
       int64           str12     int32   float32            Time            float32    str4
------------------- ------------ ----- ----------- ---------------------- ----------- ------
5785498485624156464    P/1988 D1    11     22.9181     60847.158599118426     2.98857   110P
...
```

Get the lightcurve of an object.  The result is based on a join with the DiaSource table:

```python
>>> lc = lsstsso.get.lightcurve(5785498485624156464)
>>> lc
<Table length=11>
     SSObjectId       midpointMjdTai   helioRange topoRange phaseAngle ...
                                           AU         AU       deg     ...
       int64               Time         float32    float32   float32   ...
------------------- ------------------ ---------- --------- ---------- ...
5785498485624156464 60847.158599118426   4.736578  3.751748  3.4085186 ...
...
```

Calculate *g*–*r* color from *u*–*g*, *u*–*i*, and *r*–*i* measurements:

```python
>>> from lsstsso.color import Color, ColorMatrix, solve
>>>
>>> cm = ColorMatrix.from_colors([
...     Color("u", "g", 1.3, 0.01),
...     Color("u", "i", 1.8, 0.01),
...     Color("r", "i", 0.2, 0.01),
... ])
>>> result = solve(cm)
>>> result["g", "r"]
g-r = 0.300 ± 0.017 mag
```
