"""C Command Dispatch Table Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class CommandDispatchTableRule(BasePatternRule):
    """Detects static command dispatch tables mapping opcode/string commands to function pointers."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.COMMAND_DISPATCH_TABLE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            src = f.raw_source
            # Match static arrays of command structs: static const struct cmd_entry cmds[] = { ... }
            matches = re.finditer(r"\bstatic\s+(?:const\s+)?(?:struct\s+[a-zA-Z0-9_]+|[a-zA-Z0-9_]+_t)\s+([a-zA-Z0-9_]*(?:dispatch|commands|cmds|handlers|table|routes)[a-zA-Z0-9_]*)\s*\[\s*\]\s*=", src)
            for m in matches:
                table_name = m.group(1)
                line_no = src[:m.start()].count("\n") + 1
                loc = f.location
                evidences = [
                    Evidence(
                        description=f"Array '{table_name}' implements Command Dispatch Table mapping identifiers to function pointer handlers",
                        weight=0.85,
                        rule_code="COMMAND_DISPATCH_TABLE_ARRAY",
                        location=loc,
                    )
                ]
                det = self._create_detection(
                    target_name=f"{f.file_path}:{table_name}",
                    target_kind="command_dispatch_table",
                    evidences=evidences,
                    location=loc,
                )
                detections.append(det)

        return detections
