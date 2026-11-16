import pytest

from ... import get


@pytest.mark.remote_data
def test_ssobject():
    result = get.ssobject("ssObjectId = 5785498485624156464")
    assert len(result) == 1
    assert result.ssObjectId[0] == 5785498485624156464

    result = get.ssobject("s.tisserand_J < 2.9", top=10)
    assert len(result) == 10
