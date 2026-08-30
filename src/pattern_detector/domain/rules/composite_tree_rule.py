"""C Composite Tree Node (AST / DOM) Rule."""

from __future__ import annotations

import re
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
        seen_locations: set[tuple[str, int]] = set()

        linear_names = {
            "prev", "next", "head", "tail", "first", "last", "forward", "backward",
            "hh_prev", "hh_next", "pel_prev", "pel_next", "first_block", "last_block"
        }
        tree_keywords = ("child", "children", "left", "right", "parent", "subnode", "sibling", "branch", "root", "leaf")

        for f in model.all_files():
            for s_name, st in f.structs.items():
                loc_key = (f.file_path, st.location.line if st.location else 0)
                if loc_key in seen_locations:
                    continue

                # Check for recursive self-pointers using exact word boundary matching on type string
                type_pattern = re.compile(r"\b(?:" + re.escape(s_name) + (r"|" + re.escape(st.name) if st.name else "") + r")\b")
                child_ptrs = [
                    m for m in st.members
                    if type_pattern.search(m.type_str) and m.is_pointer and not m.is_function_pointer
                ]
                if not child_ptrs:
                    continue

                ptr_names = {m.name.lower() for m in child_ptrs}
                is_pure_linear_list = len(ptr_names) > 0 and all(
                    any(p.startswith(prefix) for prefix in ("prev", "next", "head", "tail", "first", "last", "forward", "backward", "hh_", "pel_"))
                    for p in ptr_names
                )
                has_tree_child_names = any(
                    any(t in m.name.lower() for t in tree_keywords)
                    for m in child_ptrs
                )

                if has_tree_child_names or (len(child_ptrs) >= 2 and not is_pure_linear_list):
                    seen_locations.add(loc_key)
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
