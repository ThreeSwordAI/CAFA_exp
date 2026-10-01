import numpy as np
import pytest

from cafa.external_orders import load_orders, save_orders, validate_orders


def test_roundtrip_and_validation(tmp_path):
    rng = np.random.default_rng(0)
    orders = np.stack([rng.permutation(12) for _ in range(30)])
    path = tmp_path / "o.npz"
    save_orders(path, orders, policy="afabench_gdfs", dataset="csv:physionet", heldout_digest="abc", meta={"k": 1})
    d = load_orders(path, n_expected=30, T_expected=12, heldout_digest="abc")
    assert np.array_equal(d["orders"], orders) and d["policy"] == "afabench_gdfs" and d["meta"] == {"k": 1}
    with pytest.raises(ValueError):
        load_orders(path, heldout_digest="other")
    with pytest.raises(ValueError):
        load_orders(path, n_expected=31)
    bad = orders.copy()
    bad[3, 0] = bad[3, 1]
    with pytest.raises(ValueError):
        validate_orders(bad)
