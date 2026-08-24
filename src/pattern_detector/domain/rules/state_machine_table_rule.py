"""C Finite State Machine (FSM) Transition Table Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class StateMachineTableRule(BasePatternRule):
    """Detects Finite State Machine (FSM) 2D transition tables in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.STATE_MACHINE_TABLE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            src = f.raw_source
            # 2D array matching: static const state_t transition_table[STATE_MAX][EVENT_MAX]
            m = re.search(r"\b(?:static\s+)?(?:const\s+)?[a-zA-Z0-9_]+\s+([a-zA-Z0-9_]*(?:state|transition|fsm)[a-zA-Z0-9_]*)\s*\[[^\]]+\]\s*\[[^\]]+\]", src)
            if m:
                table_name = m.group(1)
                evidences = [
                    Evidence(
                        description=f"2D Array '{table_name}' implements Finite State Machine (FSM) state transition matrix",
                        weight=0.85,
                        rule_code="STATE_MACHINE_2D_MATRIX",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f"{f.file_path}:{table_name}",
                    target_kind="state_machine_table",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
