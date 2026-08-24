"""C Reactor I/O Event Demultiplexer Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ReactorEventLoopRule(BasePatternRule):
    """Detects Reactor event loops (epoll_wait, kqueue, poll, select)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.REACTOR_EVENT_LOOP

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                if "epoll_wait(" in body or "kevent(" in body or "poll(" in body or "select(" in body:
                    evidences = [
                        Evidence(
                            description=f"Function '{fn.id_str}' implements Reactor I/O Demultiplexer Event Loop dispatching non-blocking system events",
                            weight=0.85,
                            rule_code="REACTOR_EVENT_LOOP_DISPATCHER",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="reactor_event_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
