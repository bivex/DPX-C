"""C VTable Interface / Function Pointer Polymorphism Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class VTableInterfaceRule(BasePatternRule):
    """Detects VTable function pointer method tables (struct ops / struct vtable)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.VTABLE_INTERFACE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for s_name, st in f.structs.items():
                func_ptrs = st.function_pointer_members
                if len(func_ptrs) >= 2 or (func_ptrs and ("ops" in s_name or "vtable" in s_name or "interface" in s_name or "driver" in s_name)):
                    evidences = [
                        Evidence(
                            description=f"Struct '{s_name}' defines polymorphic VTable Interface containing {len(func_ptrs)} function pointer method(s) ({', '.join(m.name for m in func_ptrs[:3])})",
                            weight=0.85,
                            rule_code="VTABLE_FUNCTION_POINTER_INTERFACE",
                            location=st.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=s_name,
                        target_kind="vtable_struct",
                        evidences=evidences,
                        location=st.location or f.location,
                    )
                    detections.append(det)

        return detections
