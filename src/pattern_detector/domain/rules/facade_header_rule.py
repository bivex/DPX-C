"""C Facade Header Subsystem Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class FacadeHeaderRule(BasePatternRule):
    """Detects Facade headers aggregating multiple internal subsystem headers."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FACADE_HEADER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        std_headers = {
            "stdio.h", "stdlib.h", "string.h", "stdint.h", "stdbool.h", "stddef.h",
            "stdarg.h", "limits.h", "errno.h", "fcntl.h", "unistd.h", "time.h",
            "math.h", "assert.h", "signal.h", "ctype.h", "setjmp.h", "float.h",
            "locale.h", "inttypes.h", "pthread.h", "windows.h", "winsock2.h",
            "ws2tcpip.h", "process.h", "io.h", "direct.h", "malloc.h", "memory.h",
        }

        for f in model.all_files():
            if not f.is_header:
                continue

            internal_includes = [
                inc for inc in f.includes
                if inc not in std_headers
                and not inc.startswith("sys/")
                and not inc.startswith("mach/")
                and not inc.startswith("arpa/")
                and not inc.startswith("netinet/")
            ]

            if len(internal_includes) >= 4 and len(f.functions) == 0:
                evidences = [
                    Evidence(
                        description=f"Header '{f.file_path}' serves as a Subsystem Facade aggregating {len(internal_includes)} internal module headers ({', '.join(internal_includes[:3])}) into a single public interface",
                        weight=0.75,
                        rule_code="FACADE_HEADER_AGGREGATOR",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="facade_header",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
