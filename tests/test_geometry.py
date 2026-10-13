"""
Tests for geometry.py — compute_midpoint

Run with:
    uv run pytest tests/ -v
"""
from __future__ import annotations

import math
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "weld-geometry"))

from geometry import compute_midpoint, compute_scale


# ── Happy-path tests ──────────────────────────────────────────────────────────

class TestComputeMidpointHappyPath:

    def test_symmetric_horizontal(self):
        """Midpoint of two points on the same horizontal line."""
        mx, my = compute_midpoint((0.0, 0.0), (4.0, 0.0))
        assert mx == pytest.approx(2.0)
        assert my == pytest.approx(0.0)

    def test_symmetric_vertical(self):
        """Midpoint of two points on the same vertical line."""
        mx, my = compute_midpoint((0.0, 0.0), (0.0, 10.0))
        assert mx == pytest.approx(0.0)
        assert my == pytest.approx(5.0)

    def test_general_case(self):
        """Midpoint in the general case."""
        mx, my = compute_midpoint((100.0, 200.0), (300.0, 400.0))
        assert mx == pytest.approx(200.0)
        assert my == pytest.approx(300.0)

    def test_integer_inputs_return_floats(self):
        """Integer inputs must still return float results."""
        mx, my = compute_midpoint((0, 0), (4, 0))
        assert isinstance(mx, float)
        assert isinstance(my, float)

    def test_same_point_returns_same_point(self):
        """Midpoint of a point with itself is the point itself."""
        mx, my = compute_midpoint((123.5, 456.7), (123.5, 456.7))
        assert mx == pytest.approx(123.5)
        assert my == pytest.approx(456.7)

    def test_real_world_base_values(self):
        """Values taken from an actual annotated corte in cortes.csv."""
        # Corte 1: BL=(306, 222), BR=(541, 221)
        mx, my = compute_midpoint((306.0, 222.0), (541.0, 221.0))
        assert mx == pytest.approx(423.5)
        assert my == pytest.approx(221.5)

    def test_non_integer_pixel_coords(self):
        """Pixel coords can be fractional after zoom-rescaling."""
        mx, my = compute_midpoint((10.3, 20.7), (30.1, 40.5))
        assert mx == pytest.approx((10.3 + 30.1) / 2)
        assert my == pytest.approx((20.7 + 40.5) / 2)

    def test_result_is_tuple_of_two(self):
        """Return type must be a 2-element tuple."""
        result = compute_midpoint((0.0, 0.0), (1.0, 1.0))
        assert isinstance(result, tuple)
        assert len(result) == 2


# ── Validation / error path tests ────────────────────────────────────────────

class TestComputeMidpointValidation:

    def test_raises_on_nan_left_x(self):
        with pytest.raises(ValueError, match="NaN"):
            compute_midpoint((float("nan"), 0.0), (1.0, 0.0))

    def test_raises_on_nan_right_y(self):
        with pytest.raises(ValueError, match="NaN"):
            compute_midpoint((0.0, 0.0), (1.0, float("nan")))

    def test_raises_on_string_coordinate(self):
        with pytest.raises(TypeError, match="numeric"):
            compute_midpoint(("not a number", 0.0), (1.0, 0.0))

    def test_raises_on_single_value_instead_of_tuple(self):
        with pytest.raises(ValueError, match="2-element"):
            compute_midpoint(5.0, (1.0, 0.0))  # type: ignore[arg-type]

    def test_raises_on_3_element_tuple(self):
        with pytest.raises(ValueError, match="2-element"):
            compute_midpoint((0.0, 0.0, 0.0), (1.0, 0.0))  # type: ignore[arg-type]

    def test_raises_on_none(self):
        with pytest.raises((ValueError, TypeError)):
            compute_midpoint(None, (1.0, 0.0))  # type: ignore[arg-type]


# ── Scale computation tests ──────────────────────────────────────────────────

class TestComputeScaleHappyPath:

    def test_horizontal_scale_bar(self):
        """Scale factor with a horizontal 100 px bar and 3.0 mm."""
        scale = compute_scale((0.0, 0.0), (100.0, 0.0), 3.0)
        assert scale == pytest.approx(0.03)

    def test_vertical_scale_bar(self):
        """Scale factor with a vertical 50 px bar and 1.0 mm."""
        scale = compute_scale((0.0, 0.0), (0.0, 50.0), 1.0)
        assert scale == pytest.approx(0.02)

    def test_diagonal_scale_bar(self):
        """3-4-5 right triangle length: 30 and 40 -> hypotenuse 50 px."""
        scale = compute_scale((0.0, 0.0), (30.0, 40.0), 5.0)
        assert scale == pytest.approx(0.1)

    def test_real_world_scale_values(self):
        """Values from typical 3mm scale bar annotation (122 px)."""
        scale = compute_scale((686.0, 52.0), (808.0, 52.0), 3.0)
        # 3.0 / 122.0 ≈ 0.024590
        assert scale == pytest.approx(3.0 / 122.0, rel=1e-5)

    def test_integer_inputs_accepted(self):
        scale = compute_scale((10, 20), (110, 20), 3)
        assert isinstance(scale, float)
        assert scale == pytest.approx(0.03)


class TestComputeScaleValidation:

    def test_raises_on_identical_points(self):
        with pytest.raises(ValueError, match="idénticos"):
            compute_scale((50.0, 50.0), (50.0, 50.0), 3.0)

    def test_raises_on_zero_length_reference(self):
        with pytest.raises(ValueError, match="positivo"):
            compute_scale((0.0, 0.0), (100.0, 0.0), 0.0)

    def test_raises_on_negative_length_reference(self):
        with pytest.raises(ValueError, match="positivo"):
            compute_scale((0.0, 0.0), (100.0, 0.0), -3.0)

    def test_raises_on_nan_in_points(self):
        with pytest.raises(ValueError, match="NaN"):
            compute_scale((float("nan"), 0.0), (100.0, 0.0), 3.0)

    def test_raises_on_non_numeric_reference(self):
        with pytest.raises(ValueError, match="positivo"):
            compute_scale((0.0, 0.0), (100.0, 0.0), "3.0")  # type: ignore[arg-type]

