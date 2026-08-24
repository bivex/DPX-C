"""C Intrusive Data Structure (container_of) Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class IntrusiveListTreeRule(BasePatternRule):
    """Detects Linux-kernel style intrusive linked lists (list_head, container_of, offsetof)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.INTRUSIVE_LIST_TREE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            src = f.raw_source
            has_list_head = "struct list_head" in src or "struct list_node" in src or "struct slist_node" in src
            has_container_of = "container_of(" in src or "offsetof(" in src or "list_entry(" in src or "list_for_each(" in src

            if has_list_head or has_container_of:
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Intrusive Data Structure pattern (zero-allocation intrusive nodes resolved via `container_of` / `offsetof`)",
                        weight=0.85,
                        rule_code="INTRUSIVE_LIST_CONTAINER_OF",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="intrusive_structure_file",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
