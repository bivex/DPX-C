"""C Composite Tree Node (AST / DOM) Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class CompositeTreeRule(BasePatternRule):
    """Detects Composite Tree node structs (ASTs, DOM trees, expression hierarchies)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.COMPOSITE_TREE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for s_name, st in f.structs.items():
                # Check for recursive self-pointers: struct node* left, *right or struct node** children
                child_ptrs = [m for m in st.members if s_name in m.type_str and m.is_pointer]
                if len(child_ptrs) >= 2 or any(m.name in ("children", "child", "first_child") for m in child_ptrs):
                    evidences = [
                        Evidence(
                            description=f"Struct '{s_name}' implements Composite Tree Pattern containing recursive child node links ({', '.join(m.name for m in child_ptrs)})",
                            weight=0.85,
                            rule_code="COMPOSITE_RECURSIVE_TREE_STRUCT",
                            location=st.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=s_name,
                        target_kind="composite_tree_struct",
                        evidences=evidences,
                        location=st.location or f.location,
                    )
                    detections.append(det)

        return detections
