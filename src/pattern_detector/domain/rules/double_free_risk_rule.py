"""C Double Free / Dangling Pointer Risk Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class DoubleFreeRiskRule(BasePatternRule):
    """Detects multiple free calls on the same pointer variable or free in loops without NULL assignment."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DOUBLE_FREE_RISK

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                vulnerable_var = self._find_double_free_var(body)
                if vulnerable_var:
                    evidences = [
                        Evidence(
                            description=f"Memory Safety Hazard (Double Free Risk): Function '{fn.id_str}' in '{f.file_path}' calls free() multiple times on '{vulnerable_var}' on sequential execution path without reallocation or NULL check",
                            weight=0.85,
                            rule_code="DOUBLE_FREE_DUPLICATE_CALL",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="double_free_risk_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections

    def _find_double_free_var(self, body: str) -> str | None:
        matches = list(re.finditer(r"\b(?:free|zfree|cJSON_free|uv__free)\s*\(\s*([a-zA-Z0-9_]+)\s*\)", body))
        if len(matches) < 2:
            return None

        var_positions: dict[str, list[int]] = {}
        for m in matches:
            var_positions.setdefault(m.group(1), []).append(m.start())

        for var, positions in var_positions.items():
            if len(positions) < 2:
                continue

            for i in range(len(positions) - 1):
                pos1 = positions[i]
                pos2 = positions[i + 1]
                segment = body[pos1:pos2]

                has_exit_or_branch = (
                    "return " in segment
                    or "return;" in segment
                    or "goto " in segment
                    or "else " in segment
                    or "else{" in segment
                    or "break;" in segment
                    or "exit(" in segment
                    or "abort(" in segment
                    or re.search(r"\b" + re.escape(var) + r"\s*=", segment) is not None
                )

                if not has_exit_or_branch:
                    return var

        return None
