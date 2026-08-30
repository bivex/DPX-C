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
            # Exclude scripting language runtime standard libraries (e.g. Lua loslib.c)
            if "loslib" in f.file_path or "lua" in f.file_path and "oslib" in f.file_path:
                continue

            adapter_fns = [
                fn for fn in f.functions.values()
                if fn.name.startswith(("pal_", "hal_", "plat_"))
                or (fn.name.startswith("os_") and any(w in f.file_path.lower() for w in ("pal", "hal", "plat", "adapter", "port", "compat", "platform", "win", "unix", "posix", "os_wrap", "pages")))
            ]

            is_adapter_path = any(w in f.file_path.lower() for w in ("/pal/", "/hal/", "/platform/", "/adapter/", "/compat/"))
            has_platform_guards = "#ifdef _WIN32" in f.raw_source or "#if defined(_WIN32)" in f.raw_source or "#ifdef __linux__" in f.raw_source

            if len(adapter_fns) >= 3 or (is_adapter_path and has_platform_guards and len(f.functions) >= 2):
                count = len(adapter_fns) if adapter_fns else len(f.functions)
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Adapter / Hardware Abstraction Layer (HAL) defining {count} uniform platform wrapper(s)",
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
