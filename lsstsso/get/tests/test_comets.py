import pytest

from ... import get


@pytest.mark.remote_data
def test_comets():
    comets = get.comets()
    assert len(comets) == 47
    assert "P/1988 D1" in comets.designation
