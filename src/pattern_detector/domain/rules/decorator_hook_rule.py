"""C Decorator / Execution Hook Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class DecoratorHookRule(BasePatternRule):
    """Detects function pointer interceptors and hook decorators in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DECORATOR_HOOK

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            hook_fns = [fn for fn in f.functions.values() if "hook" in fn.name or "filter" in fn.name or "interceptor" in fn.name]
            if hook_fns:
                for fn in hook_fns:
                    if any(p.is_function_pointer for p in fn.params):
                        evidences = [
                            Evidence(
                                description=f"Function '{fn.id_str}' decorates/intercepts execution flow via function pointer hooks",
                                weight=0.80,
                                rule_code="DECORATOR_HOOK_FUNCTION",
                                location=fn.location or f.location,
                            )
                        ]
                        det = self._create_detection(
                            target_name=f"{f.file_path}:{fn.name}",
                            target_kind="decorator_hook",
                            evidences=evidences,
                            location=fn.location or f.location,
                        )
                        detections.append(det)

        return detections
