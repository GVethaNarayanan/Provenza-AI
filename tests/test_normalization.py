"""Provenza AI - Normalization Tests"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.normalization.unit_normalizer import (
    normalize_unit, normalize_value_with_unit, normalize_size, extract_numeric
)
from app.normalization.attribute_normalizer import (
    normalize_attribute_name, get_display_name
)
from app.normalization.material_normalizer import (
    normalize_material, normalize_connection, normalize_category,
    normalize_value_by_attribute
)


class TestUnitNormalization:
    """Tests for unit normalization."""

    def test_psi_normalization(self):
        assert normalize_unit("psi") == "PSI"
        assert normalize_unit("PSI") == "PSI"

    def test_inch_normalization(self):
        assert normalize_unit("in") == "inch"
        assert normalize_unit("in.") == "inch"
        assert normalize_unit('"') == "inch"
        assert normalize_unit("inches") == "inch"

    def test_temperature_normalization(self):
        assert normalize_unit("°F") == "°F"
        assert normalize_unit("fahrenheit") == "°F"
        assert normalize_unit("°C") == "°C"
        assert normalize_unit("celsius") == "°C"

    def test_weight_normalization(self):
        assert normalize_unit("lbs") == "lb"
        assert normalize_unit("kg") == "kg"

    def test_value_with_unit_split(self):
        val, unit = normalize_value_with_unit("200 PSI")
        assert val == "200"
        assert unit == "PSI"

    def test_value_with_unit_separate(self):
        val, unit = normalize_value_with_unit("200", "psi")
        assert val == "200"
        assert unit == "PSI"

    def test_extract_numeric(self):
        assert extract_numeric("200") == 200.0
        assert extract_numeric("150 PSI") == 150.0
        assert extract_numeric("2.5") == 2.5
        assert extract_numeric("no number") is None

    def test_normalize_size(self):
        val, unit = normalize_size('2"')
        assert val == "2"
        assert unit == "inch"

    def test_null_unit(self):
        assert normalize_unit(None) is None
        assert normalize_unit("") is None


class TestAttributeNormalization:
    """Tests for attribute name normalization."""

    def test_pressure_variations(self):
        assert normalize_attribute_name("pressure") == "pressure_rating"
        assert normalize_attribute_name("Pressure Rating") == "pressure_rating"
        assert normalize_attribute_name("max pressure") == "pressure_rating"

    def test_material_variations(self):
        assert normalize_attribute_name("material") == "material"
        assert normalize_attribute_name("materials") == "material"

    def test_connection_variations(self):
        assert normalize_attribute_name("connection") == "connection_type"
        assert normalize_attribute_name("Connection Type") == "connection_type"
        assert normalize_attribute_name("end connection") == "connection_type"

    def test_display_names(self):
        assert get_display_name("pressure_rating") == "Pressure Rating"
        assert get_display_name("material") == "Material"
        assert get_display_name("connection_type") == "Connection Type"

    def test_unknown_attribute(self):
        result = normalize_attribute_name("some_custom_attr")
        assert result == "some_custom_attr"


class TestMaterialNormalization:
    """Tests for material and terminology normalization."""

    def test_stainless_steel_304_variations(self):
        assert normalize_material("SS304") == "304 Stainless Steel"
        assert normalize_material("304 SS") == "304 Stainless Steel"
        assert normalize_material("Stainless Steel 304") == "304 Stainless Steel"
        assert normalize_material("ss-304") == "304 Stainless Steel"
        assert normalize_material("304 Stainless Steel") == "304 Stainless Steel"

    def test_general_stainless(self):
        assert normalize_material("Stainless Steel") == "Stainless Steel"
        assert normalize_material("stainless") == "Stainless Steel"

    def test_connection_normalization(self):
        assert normalize_connection("threaded") == "Threaded"
        assert normalize_connection("npt") == "NPT Threaded"
        assert normalize_connection("flanged") == "Flanged"

    def test_category_normalization(self):
        assert normalize_category("ball valve") == "Ball Valve"
        assert normalize_category("gate valve") == "Gate Valve"

    def test_value_by_attribute(self):
        assert normalize_value_by_attribute("material", "SS304") == "304 Stainless Steel"
        assert normalize_value_by_attribute("connection_type", "threaded") == "Threaded"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
