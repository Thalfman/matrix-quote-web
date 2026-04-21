"""Unit tests for Q-7: _load_bundle LRU cache keyed on (path, mtime_ns).

Guarantees:
1. Two calls with the same mtime_ns return the identical Python object (cached).
2. A bumped mtime_ns causes a fresh load (new object from joblib.load).
"""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tiny_models"


@pytest.fixture(autouse=True)
def _fixture_data_dir(monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(FIXTURE_DIR))
    yield


def _any_bundle_path() -> Path:
    """Return the path to one real joblib bundle from the fixture tree."""
    models = FIXTURE_DIR / "models"
    bundles = sorted(models.glob("*_v1.joblib"))
    assert bundles, "No joblib fixtures found — rebuild with scripts/build_test_fixtures.py"
    return bundles[0]


def test_same_mtime_returns_cached_object():
    """_load_bundle must return the identical bundle dict for the same path+mtime."""
    from backend.app.explain import _load_bundle, _load_bundle_cached

    # Clear the cache to avoid cross-test contamination.
    _load_bundle_cached.cache_clear()

    path = _any_bundle_path()
    bundle1 = _load_bundle(path)
    bundle2 = _load_bundle(path)

    assert bundle1 is bundle2, (
        "_load_bundle must return the same object on repeated calls with unchanged mtime"
    )
    info = _load_bundle_cached.cache_info()
    assert info.hits >= 1, "Expected at least one cache hit"


def test_bumped_mtime_triggers_fresh_load():
    """After the mtime changes, _load_bundle_cached must load a fresh bundle.

    _load_bundle is a thin wrapper that passes (path, mtime_ns) to the cached
    function. We call _load_bundle_cached directly with two different mtime_ns
    values to confirm the cache key differs and joblib.load runs twice,
    returning non-identical objects.
    """
    from backend.app.explain import _load_bundle_cached

    _load_bundle_cached.cache_clear()

    path = _any_bundle_path()
    real_mtime = path.stat().st_mtime_ns

    bundle1 = _load_bundle_cached(path, real_mtime)
    # Same mtime → same cached object.
    bundle1_again = _load_bundle_cached(path, real_mtime)
    assert bundle1 is bundle1_again, "Same mtime must return cached object"

    # Bumped mtime → different cache entry → fresh load.
    bundle2 = _load_bundle_cached(path, real_mtime + 1)
    assert bundle1 is not bundle2, (
        "_load_bundle_cached must produce a fresh bundle when mtime_ns changes"
    )
