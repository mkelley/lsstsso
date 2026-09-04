"""
Interact with RSP via API.
"""

import os
import hashlib
import subprocess
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

    def query_tap(self, query: str, cached: bool = True):
        """Query the RSP TAP endpoint.


        Parameters
        ----------
        query : string
            The ADQL query to send.

        cache : bool, optional
            ``True`` to use result cache.

        Returns
        -------
        result : Result

        """

        logger = getLogger()

        table = self._cached_result(query, cached)
        if table is not None:
            return make_result(table)

        job = self.tap_service.submit_job(query)
        job.run()
        job.wait(phases=["COMPLETED", "ERROR"])
        job.raise_if_error()

        tap_result = job.fetch_result()
        logger.info(tap_result.status[0])

        job.delete()

        table = tap_result.to_table()
        table.meta = tap_result.infos

        if cached:
            self._cache_query(query, table)

        return make_result(table)

    @staticmethod
    def clean_cache(max_age: float = 0):
        """Remove cache files older than max age days."""
        files = glob("~/.cache/lsst-sso/*ecsv")
        count = len(files)
        removed = 0
        for fn in files:
            if os.stat(fn).st_mtime > max_age * 86400:
                os.unlink(fn)
                removed += 1

        print(f"{removed}/{count} cache files removed.")

    @staticmethod
    def cache_file_name(query: str) -> str:
        hash = hashlib.md5(query.encode())
        return os.environ["HOME"] + "/.cache/lsst-sso/" + hash.hexdigest() + ".ecsv"

    @staticmethod
    def _cached_result(query: str, cached: bool):
        if not cached:
            return None

        fn = RSP.cache_file_name(query)

        logger = getLogger()
        logger.info(f"Returning cached result from {fn}")

        if os.path.exists(fn):
            return Table.read(fn)

        return None

    def _cache_query(self, query: str, table: Table):
        fn = self.cache_file_name(query)

        dirname = os.path.dirname(fn)
        if not os.path.exists(dirname):
            subprocess.check_call(["mkdir", "-p", dirname])

        table.write(fn, format="ascii.ecsv", overwrite=True)
