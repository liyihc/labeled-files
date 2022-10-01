from ..handler import VscodePath


def test_local():
    target_path = VscodePath(
        typ="file",
        protocol="local",
        host="",
        path="/home/ubuntu"
    )
    target_str = target_path.to_str()
    path = VscodePath.from_str(target_str)
    assert path == target_path


def test_ssh():
    target_path = VscodePath(
        typ="folder",
        protocol="ssh",
        host="1.2.3.4",
        path="/home"
    )
    target_str = target_path.to_str()
    path = VscodePath.from_str(target_str)
    assert path == target_path
