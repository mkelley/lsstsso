from itertools import combinations

import astropy.units as u

from ..band import Band


def test_init():
    band = Band("u")
    assert band == Band.u

    band = Band("g")
    assert band == Band.g

    band = Band("r")
    assert band == Band.r

    band = Band("i")
    assert band == Band.i

    band = Band("z")
    assert band == Band.z

    band = Band("y")
    assert band == Band.y


def test_repr():
    assert repr(Band.g) == "<Band: g, 480.7 nm>"


def test_str():
    for band, b in zip(Band, "ugrizy"):
        assert str(band) == b


def test_comparisons():
    for blue, red in combinations(Band, 2):
        assert blue < red
        assert blue <= red
        assert not (blue > red)
        assert not (blue >= red)

        assert red > blue
        assert red >= blue
        assert not (red < blue)
        assert not (red <= blue)

    for band in Band:
        assert band == Band(str(band))


def test_wave():
    for band, wave in zip(Band, [372.4, 480.7, 622.1, 755.9, 868.0, 975.3] * u.nm):
        assert u.isclose(band.wave, wave)
