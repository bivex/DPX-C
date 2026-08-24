"""C Observer / Callback Registry Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ObserverCallbackRegistryRule(BasePatternRule):
    """Detects Observer / Callback registration mechanisms in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.OBSERVER_CALLBACK_REGISTRY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                is_sub = any(fn.name.startswith(p) for p in ("register_", "add_listener", "subscribe_", "on_", "set_callback"))
                has_fp = any(p.is_function_pointer for p in fn.params)
                has_userdata = any("user_data" in p.name or "userdata" in p.name or "ctx" in p.name or "arg" in p.name for p in fn.params)

                if is_sub and (has_fp or has_userdata):
                    evidences = [
                        Evidence(
                            description=f"Function '{fn.id_str}' implements Observer Callback Registration allowing event listeners to attach opaque callbacks with context pointers",
                            weight=0.85,
                            rule_code="OBSERVER_CALLBACK_REGISTRATION",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="observer_registry_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
