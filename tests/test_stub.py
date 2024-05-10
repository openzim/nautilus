from nautiluszim.__about__ import __version__


def test_version():
    assert __version__[0].isdigit()
