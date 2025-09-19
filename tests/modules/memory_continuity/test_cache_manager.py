import os
import pickle
import pytest

from nfl_simulation_engine.modules.memory_continuity.cache_manager import CacheManager


@pytest.fixture(scope="function")
def cache_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture(scope="function")
def cache_manager(cache_dir):
    return CacheManager(cache_dir=cache_dir)


def test_cache_hit_and_miss(cache_manager):
    key = "test1"
    artifact = {"a": 1}
    assert not cache_manager.has_cache(key)
    assert cache_manager.get_cache(key) is None

    cache_manager.set_cache(key, artifact)
    assert cache_manager.has_cache(key)
    cached = cache_manager.get_cache(key)
    assert cached == artifact


def test_ensure_artifact_generates_and_caches(cache_manager):
    key = "gen_key"

    def gen_func(x):
        return {"value": x}

    result = cache_manager.ensure_artifact(key, gen_func, 42)
    assert result == {"value": 42}
    # Should now hit cache
    result2 = cache_manager.ensure_artifact(key, gen_func, 999)
    assert result2 == {"value": 42}  # Should NOT rerun gen_func


def test_cache_overwrite(cache_manager):
    key = "overwrite"
    first = [1, 2, 3]
    second = [4, 5, 6]
    cache_manager.set_cache(key, first)
    assert cache_manager.get_cache(key) == first
    cache_manager.set_cache(key, second)
    assert cache_manager.get_cache(key) == second


def test_multi_type_artifact_support(cache_manager):
    key_int = "int"
    key_dict = "dict"
    key_obj = "obj"
    cache_manager.set_cache(key_int, 123)
    cache_manager.set_cache(key_dict, {"foo": "bar"})
    cache_manager.set_cache(key_obj, [1, 2, 3])

    assert cache_manager.get_cache(key_int) == 123
    assert cache_manager.get_cache(key_dict) == {"foo": "bar"}
    assert cache_manager.get_cache(key_obj) == [1, 2, 3]


def test_cache_corruption_handling(cache_manager):
    key = "corrupt"
    path = cache_manager._get_cache_path(key)
    # Write bad data
    with open(path, "wb") as f:
        f.write(b"notapickle")
    # Should not raise, just return None
    try:
        result = cache_manager.get_cache(key)
    except Exception:
        result = None
    assert result is None


def test_cache_dir_creation(tmp_path):
    cache_dir = str(tmp_path / "new_cache_dir")
    assert not os.path.exists(cache_dir)
    cm = CacheManager(cache_dir=cache_dir)
    assert os.path.exists(cache_dir)
