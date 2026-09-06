"""
Interact with RSP via API.
"""

import os
import hashlib
import subprocess
import time
from contextlib import contextmanager
from glob import glob
from logging import getLogger

import pyvo as vo
from astropy.table import Table
from pyvo.auth import AuthSession

from .result import make_result


class RSP:
    """Rubin Science Platform API interface."""

    def __init__(self) -> None:
        token = os.environ["LSST_SSO_RSP_TOKEN"]
        self.session = AuthSession()
        self.session.credentials.set_password("x-oauth-basic", token)

        self.tap_service = vo.dal.TAPService(
            "https://data.lsst.cloud/api/tap", session=self.session
        )

    def query_tap(
        self, query: str, units: dict[str, str] = {}, cache: bool = True, **kwargs
    ):
        """Query the RSP TAP endpoint.


        Parameters
        ----------
        query : string
            The ADQL query to send.

        units : dict, optional
            Column-unit pairs: assign these units to each respective column.

        cache : bool, optional
            ``True`` to use result cache.

        **kwargs
            Additional keyword arguments to pass to `TAPService.submit_job`.


        Returns
        -------
        result : Result

        """

        logger = getLogger("lsstsso")

        table = self._cached_result(query, cache, **kwargs)
        if table is not None:
            return make_result(table)

        start = time.monotonic()
        job = self.tap_service.submit_job(query, **kwargs)
        job.run()
        job.wait(phases=["COMPLETED", "ERROR"])
        job.raise_if_error()

        try:
            tap_result = job.fetch_result()
            end = time.monotonic()
        finally:
            logger.info("%s in %.2f s", tap_result.status[0], end - start)
            job.delete()

        table = tap_result.to_table()
        table.meta = tap_result.infos

        if cache:
            self._cache_query(query, table, **kwargs)

        return make_result(table)

    @staticmethod
    def clean_cache(max_age: float = 0):
        """Remove cache files older than max age days."""
        files = glob(os.environ["HOME"] + "/.cache/lsst-sso/*ecsv")
        count = len(files)
        removed = 0
        for fn in files:
            if os.stat(fn).st_mtime > max_age * 86400:
                os.unlink(fn)
                removed += 1

        print(f"{removed}/{count} cache files removed.")

    @staticmethod
    def cache_file_name(query: str, **kwargs) -> str:
        hash = hashlib.md5(query.encode() + str(kwargs).encode())
        return os.environ["HOME"] + "/.cache/lsst-sso/" + hash.hexdigest() + ".ecsv"

    @staticmethod
    def _cached_result(query: str, cache: bool, **kwargs):
        logger = getLogger("lsstsso")

        # are we using the caching system?
        if not cache:
            return None

        # get the file name
        fn = RSP.cache_file_name(query, **kwargs)

        # if the file exists, return the table
        if os.path.exists(fn):
            logger.info(f"Returning cached result from {fn}")
            return Table.read(fn)

        logger.info(f"Query not cached ({fn})")

        return None

    def _cache_query(self, query: str, table: Table, **kwargs):
        logger = getLogger("lsstsso")

        # get the file name
        fn = self.cache_file_name(query, **kwargs)

        # make directories as needed
        dirname = os.path.dirname(fn)
        if not os.path.exists(dirname):
            subprocess.check_call(["mkdir", "-p", dirname])

        # write the file
        logger.info(f"Caching result to {fn}")
        table.write(fn, format="ascii.ecsv", overwrite=True)


rsp = RSP()


@contextmanager
def provider(refresh=False):
    """Context manager for the RSP client.


    Parameters
    ----------
    refresh : bool
        Set to true to force a refresh on the RSP client, e.g., if the token
        changed and/or the environment was reloaded (via os.reload_environ()).

    """

    global rsp

    if refresh:
        rsp = RSP()

    yield rsp
