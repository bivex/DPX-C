"""C Singleton Module Pattern Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class SingletonModuleRule(BasePatternRule):
    """Detects C Singleton modules managing private static state."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.SINGLETON_MODULE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            if f.is_header:
                continue
            src = f.raw_source
            has_static_state = bool(re.search(r"\bstatic\s+(?:struct\s+[a-zA-Z0-9_]+|[a-zA-Z0-9_]+_t)\s+g_[a-zA-Z0-9_]+", src)) or bool(re.search(r"\bstatic\s+bool\s+[a-zA-Z0-9_]*init", src))
            has_get_instance = bool(re.search(r"\b[a-zA-Z0-9_]+_(?:get_instance|instance|get_default|get_global)\s*\(", src)) or "pthread_once(" in src

            if has_static_state and has_get_instance:
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Singleton pattern encapsulating synchronized module-wide private static state",
                        weight=0.85,
                        rule_code="SINGLETON_STATIC_MODULE",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="singleton_module",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
