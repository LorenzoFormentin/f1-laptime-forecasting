from f1laptime.data.fastf1_cache import enable_fastf1_cache
from f1laptime.settings import FASTF1_CACHE_DIR


def test_enable_cache_creates_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("FASTF1_CACHE_DIR", str(tmp_path / "fastf1_cache"))
    cache_dir = enable_fastf1_cache()
    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_default_cache_dir_is_inside_data():
    # This checks our project convention, not FastF1 behavior.
    assert "data" in str(FASTF1_CACHE_DIR)
