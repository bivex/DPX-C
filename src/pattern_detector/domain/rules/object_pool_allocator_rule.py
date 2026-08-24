"""C Object Pool / Slab Allocator Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ObjectPoolAllocatorRule(BasePatternRule):
    """Detects Object Pool and Slab memory allocators in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.OBJECT_POOL_ALLOCATOR

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for s_name, st in f.structs.items():
                member_names = [m.name for m in st.members]
                if ("free_list" in member_names or "freelist" in member_names or "chunks" in member_names or "slots" in member_names) and ("capacity" in member_names or "block_size" in member_names or "count" in member_names):
                    evidences = [
                        Evidence(
                            description=f"Struct '{s_name}' implements Object Pool / Slab memory allocator managing recycled chunk slots",
                            weight=0.85,
                            rule_code="OBJECT_POOL_SLAB_STRUCT",
                            location=st.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=s_name,
                        target_kind="object_pool_struct",
                        evidences=evidences,
                        location=st.location or f.location,
                    )
                    detections.append(det)

        return detections
