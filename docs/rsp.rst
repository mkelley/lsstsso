.. _lsstsso_rsp:

********************************
Fetching data with `lsstsso.rsp`
********************************

`lsstsso.rsp` fetches data from the Rubin Science Platform (RSP) Table Access Protocol (TAP) services.  This is a lower level interface than `lsstsso.get` that can send any ADQL commands to the RSP and format the result as tabular data.  It can also cache queries locally to avoid repeated interaction with the RSP.


