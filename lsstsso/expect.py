import warnings


def expect(condition: bool, exception: Exception, warn: bool = False) -> None:
    """If condition is false, raise an exception or warning.


    Parameters
    ----------

    condition : bool
        The condition to test.

    execption : Exception
        The exception to raise or warn.

    warn : bool, optional
        Warn the user, otherwise raise the exception.

    """

    if condition:
        return

    if warn:
        warnings.warn(exception)

    raise exception
