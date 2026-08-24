"""Tests for C Domain Models and Value Objects."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel, FileModel, FunctionModel
from pattern_detector.domain.value_objects import (
    Confidence,
    ConfidenceLevel,
    Evidence,
    SourceLocation,
)


def test_confidence_calculation():
    evidences = [
        Evidence(description="Found VTable function pointers", weight=0.8, rule_code="VTABLE_STRUCT"),
        Evidence(description="Found ops naming convention", weight=0.5, rule_code="OPS_NAME"),
    ]
    conf = Confidence.from_evidences(evidences)
    # Expected: 1.0 - (1 - 0.8) * (1 - 0.5) = 1.0 - (0.2 * 0.5) = 0.90
    assert abs(conf.score - 0.90) < 1e-4
    assert conf.level == ConfidenceLevel.VERY_HIGH
    assert conf.percentage_str == "90%"


def test_source_location_str():
    loc = SourceLocation(file_path="src/network/socket.c", line=42, column=5)
    assert str(loc) == "src/network/socket.c:42:5"


def test_circular_include_detection():
    model = CodeModel()

    file_a = FileModel(file_path="include/a.h", is_header=True, includes=["b.h"])
    file_b = FileModel(file_path="include/b.h", is_header=True, includes=["a.h"])

    model.files["include/a.h"] = file_a
    model.files["include/b.h"] = file_b

    cycles = model.find_circular_includes()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a.h", "b.h"}
