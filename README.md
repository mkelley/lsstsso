# LSST SSO

Get and plot light curves of solar system objects observed by LSST.

The data interface is designed in an attempt to be simple and useful in interactive sessions.  If you need something efficient or suitable for large scales, maybe try something else.

Features:
* Query caching.
* Convenience functions for common queries.
* Result objects designed for column-based and row-based inspection.
* Powered by [astropy](https://astropy.org/)!

The API is not currently stable.

The convenience queries are currently hard-coded for DP2.

You'll want to have the [RSP DP2 schemas](https://sdm-schemas.lsst.io/dp2.html) on hand for reference.

## Set up

1. Install as per usual, e.g., `pip install "git+https://github.com/mkelley/lsstsso.git#egg=lsstsso"`.

2. Get an API key for the Rubin Science Platform.  The key only needs read:tap permissions.

3. Save this key to an environment variable: LSST_SSO_RSP_TOKEN.

## Usage

### Convenience functions

Query the Rubin Science Platform for a list of all Solar System objects with cometary designations and observations in DP2:

```python
>>> import lsstsso
>>> rsp = lsstsso.RSP()
>>> comets = lsstsso.get.comets(rsp)
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
>>> lc = lsstsso.get.lightcurve(rsp, 5785498485624156464)
>>> lc
<Table length=11>
     SSObjectId       midpointMjdTai   helioRange topoRange phaseAngle ...
                                           AU         AU       deg     ...
       int64               Time         float32    float32   float32   ...
------------------- ------------------ ---------- --------- ---------- ...
5785498485624156464 60847.158599118426   4.736578  3.751748  3.4085186 ...
...
```

Query the SSObject table.  This function takes a string of constraints (i.e., ADQL "WHERE" clauses):

```python
>>> sso = lsstsso.get.ssobject(rsp, "ssObjectId = 5785498485624156464")
>>> sso
<Table length=1>
     ssObjectId     designation  nObs   arc   firstObservationMjdTai tisserand_J permid
                                         d                                             
       int64            str9    int32 float32          Time            float32    str4 
------------------- ----------- ----- ------- ---------------------- ----------- ------
5785498485624156464   P/1988 D1    11 22.9181     60847.158599118426     2.98857   110P
```

Get an object's orbit.
```python
>>> orbit = lsstsso.get.orbit(rsp, "P/1988 D1")
>>> orbit
<Table length=1>
designation epoch_mjd    a           q                 e         ...
                         AU          AU                          ...
   str16       Time   float64     float64           float64      ...
----------- --------- ------- ---------------- ----------------- ...
  P/1988 D1   61000.0     nan 2.45298759313139 0.319253973199543 ...
```

If you needed other columns on these queries, use the `columns=` keyword argument, e.g.,:

```python
>>> columns = ["designation", "u_nObs", "g_nObs", "r_nObs", "i_nObs", "z_nObs", "y_nObs"]
>>> n_obs = lsstsso.get.ssobject(rsp, "designation LIKE 'P/%'", columns=columns)
>>> orbit = lsstsso.get.orbit(rsp, "P/1988 D1", columns=["*"])  # get all columns
```

Make your own query with the `RSP` object:

```python
>>> result = rsp.query_tap("SELECT whatever FROM dp2.table WHERE constraints")
```

Avoid returning column names that conflict with `Result` methods (e.g., "columns", "sort", "as_table").


### Result: columns

Get a list of columns in the `Result` object:

```python
>>> lc.columns()
('SSObjectId', 'midpointMjdTai', 'helioRange', 'topoRange', 'phaseAngle', 'elongation', 'ephRate', 'ephOffset', 'band', 'apFlux', 'apFluxErr', 'centroid_flag', 'pixelFlags')
```

Result columns are accessed by class attributes or by indexing with a string:

```python
>>> lc = lsstsso.get.lightcurve(rsp, 5785498485624156464)
>>> lc.SSObjectId
array([5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464])
>>> lc["SSObjectId"]
array([5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464, 5785498485624156464,
       5785498485624156464, 5785498485624156464])
```

Time columns are astropy ``Time`` objects:

```python
>>> lc.midpointMjdTai
<Time object: scale='tai' format='mjd' value=[60847.15859912 60859.10020628 60859.13561585 60861.05626209
 60861.07909194 60861.09632008 60863.16210835 60863.20864203
 60863.2195257  60869.07914862 60870.07673914]>
```

Columns named "band" use the internal `Band` object:

```python
>>> lc.band
array([<Band: i, 755.9 nm>, <Band: i, 755.9 nm>, <Band: z, 868.0 nm>,
       <Band: y, 975.3 nm>, <Band: y, 975.3 nm>, <Band: y, 975.3 nm>,
       <Band: r, 622.1 nm>, <Band: i, 755.9 nm>, <Band: z, 868.0 nm>,
       <Band: z, 868.0 nm>, <Band: r, 622.1 nm>], dtype=object)
>>> lc.band[0]
<Band: i, 755.9 nm>
>>> lc.band[0].name
'i'
>>> lc.band[0].wave
<Quantity 755.9 nm>
```

### Result: rows

A single row is obtained by indexing with an integer:

```python
>>> lc[0]
>>> ResultRow(SSObjectId=np.int64(5785498485624156464), midpointMjdTai=<Time object: scale='tai' format='mjd' value=60847.158599118426>, helioRange=<Quantity 4.736578 AU>, topoRange=...
```

A subset of rows may be retrieved using slices or arrays, as usual with numpy objects:
```python
>>> lc[lc.midpointMjdTai < Time("2025-09-01")]
<Table length=1>
     SSObjectId       midpointMjdTai   helioRange topoRange phaseAngle ...
                                           AU         AU       deg     ...
       int64               Time         float32    float32   float32   ...
------------------- ------------------ ---------- --------- ---------- ...
5785498485624156464 60847.158599118426   4.736578  3.751748  3.4085186 ...
```

The `Result` object may be iterated over, row-by-row, using the `rows()` method:

```python
>>> for row in lc.rows():
...     do_something(row)
```

### Result: sorting

Use the sort method to sort the data:

```python
>>> lc.sort("helioRange")
>>> lc
<Table length=11>
     SSObjectId       midpointMjdTai   helioRange topoRange phaseAngle ...
                                           AU         AU       deg     ...
       int64               Time         float32    float32   float32   ...
------------------- ------------------ ---------- --------- ---------- ...
5785498485624156464 60870.076739144635   4.726744 3.7212656  2.0368574 ...
...
```

The band object naturally sorts by wavelength:

```python
>>> lc.sort("band")
>>> lc.band
array([<Band: r, 622.1 nm>, <Band: r, 622.1 nm>, <Band: i, 755.9 nm>,
       <Band: i, 755.9 nm>, <Band: i, 755.9 nm>, <Band: z, 868.0 nm>,
       <Band: z, 868.0 nm>, <Band: z, 868.0 nm>, <Band: y, 975.3 nm>,
       <Band: y, 975.3 nm>, <Band: y, 975.3 nm>], dtype=object)
```

### Result: convert to table

The `Result` object can be converted into an astropy `Table`:

```python
>>> tab = lc.as_table()
>>> type(tab)
astropy.table.table.Table
```