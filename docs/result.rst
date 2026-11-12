.. _lsstsso_result:

**************************************
Inspecting results (`lsstsso.results`)
**************************************

Introduction
============

Results from the RSP TAP queries are formatted into `~lsstsso.result.Result` objects.  These objects encapsulate tabular data into a slightly more convenient (to me) format by allowing columns to be accessed by member attributes.

For example, get a list of Solar System objects in DP2 with cometary designations:

.. doctest-remote-data::
.. code-block:: python

    >>> from lsstsso import get
    >>>
    >>> comets = get.comets()
    Querying SSObject LEFT JOIN numbered_identifications
    
    SELECT  s.ssObjectId,s.designation,s.nObs,s.arc,s.firstObservationMjdTai,s.tisserand_J, ...
    LEFT JOIN dp2.numbered_identifications AS n
    ON n.unpacked_primary_provisional_designation = s.designation
    WHERE s.designation LIKE 'C/%' OR s.designation LIKE 'P/%' OR s.designation LIKE 'A/%'
    
    Query not cached ...
    OK in 8.18 s
    Caching result to ...
    >>> comets
    <Result: ssObjectId,designation,nObs,arc,firstObservationMjdTai,tisserand_J,permid>

Each column in the result table is available as an attribute.  For example, print out the SSObject IDs:

.. doctest-remote-data::
.. code-block:: python

    >>> print(comets.ssObjectId)
    [5785498485624156464 5785499551010926896 5785499555373003312
     5785492992629420110 5785209301197926704 5785771130468382804
     5785498476983890224 5785499585387442480 5785489672703586864
     5785771143150449200 5785771134796642136 5785771151790715696
     5785772246839603760 5785209314384818480 5785771160449726026
     5785771143217558320 5785772247091262512 5785491880266445104
     5785772259674174000 5785772229677101145 5785772255630864944
     5785772229659734320 5785771164776281136 5785772234239914288
     4849024628320907568 5785771151958815809 5785491893050683952
     5785772259959386416 5785772229962315080 5785772247028020556
     5785494087795749168 5785772264153691440 5785772246990599239
     5785771143251245400 5785772229944946992 5785496291130749232
     5785497352105111856 5785497373361844528 5785497364889350448
     5785498451599962416 5785498468461064496 5785497381884670512
     4849024619630309680 4849024623958831920 4849024628287353136
     4849024628287353392 5785772255630865712]


Show all columns
================

Show all columns in the result:

.. doctest-remote-data::
.. code-block:: python

    >>> comets.columns
    ['ssObjectId',
     'designation',
     'nObs',
     'arc',
     'firstObservationMjdTai',
     'tisserand_J',
     'permid']


Sorting
=======

Sort the result by a column:

    >>> comets.sort("nObs")


Format as a table
=================

Printing the result object will display a table:

.. doctest-remote-data::
.. code-block:: python

    >>> print(comets)
         ssObjectId     designation  nObs     arc     firstObservationMjdTai tisserand_J permid
                                               d                d                              
    ------------------- ------------ ---- ----------- ---------------------- ----------- ------
    5785771130468382804 P/2000 WT168   57     56.8895     60823.328466791805     2.71072   150P
    ...


Or, use :func:`~lsstsso.result.Result.as_table` to get the data as an astropy `~astropy.table.Table` object:

.. doctest-remote-data::
.. code-block:: python

    >>> tab = comets.as_table()
    >>> tab
    <Table length=47>
         ssObjectId     designation   nObs    arc     firstObservationMjdTai tisserand_J ...
                                               d                d                        ...           int64           str16     int32  float32          float64           float32   str16 
    ------------------- ------------ ----- ---------- ---------------------- ----------- ...
    5785498485624156464    P/1988 D1    11    22.9181     60847.158599118426     2.98857 ...
    ...


Reference/API
=============

.. automodapi:: lsstsso.result
