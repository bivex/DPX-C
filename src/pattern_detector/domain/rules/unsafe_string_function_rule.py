"""C Unsafe String Function Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class UnsafeStringFunctionRule(BasePatternRule):
    """Detects dangerous legacy string functions prone to buffer overflow (strcpy, strcat, sprintf, gets)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.UNSAFE_STRING_FUNCTION

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                unsafe_found = []
                for bad_fn in ("strcpy(", "strcat(", "sprintf(", "gets("):
                    if bad_fn in body:
                        unsafe_found.append(bad_fn.rstrip("("))

                if unsafe_found:
                    evidences = [
                        Evidence(
                            description=f"Security / Buffer Overflow Vulnerability: Function '{fn.id_str}' in '{f.file_path}' calls bounds-unsafe string API ({', '.join(unsafe_found)}); replace with snprintf/strncpy/strlcpy",
                            weight=0.85,
                            rule_code="UNSAFE_STRING_BUFFER_OVERFLOW",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="vulnerable_string_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
