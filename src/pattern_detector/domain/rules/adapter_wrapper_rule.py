"""C Adapter / HAL Platform Wrapper Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class AdapterWrapperRule(BasePatternRule):
    """Detects Platform Abstraction Layer (PAL/HAL) and driver adapters."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ADAPTER_WRAPPER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            adapter_fns = [fn for fn in f.functions.values() if fn.name.startswith("pal_") or fn.name.startswith("hal_") or fn.name.startswith("os_") or fn.name.startswith("plat_")]
            if len(adapter_fns) >= 3:
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Adapter / Hardware Abstraction Layer (HAL) defining {len(adapter_fns)} uniform platform wrapper(s)",
                        weight=0.80,
                        rule_code="HAL_PLATFORM_ADAPTER",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="adapter_layer_file",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
