"""C Builder Config Struct Idiom Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class BuilderConfigStructRule(BasePatternRule):
    """Detects Builder Config Struct idiom (`*_config_t` / `*_options_t`)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.BUILDER_CONFIG_STRUCT

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for s_name, st in f.structs.items():
                if (s_name.endswith("_config") or s_name.endswith("_config_s") or s_name.endswith("_options") or s_name.endswith("_opts")) and len(st.members) >= 3:
                    evidences = [
                        Evidence(
                            description=f"Struct '{s_name}' implements Builder Configuration Idiom encapsulating {len(st.members)} designated parameter fields",
                            weight=0.80,
                            rule_code="BUILDER_CONFIG_STRUCT_IDIOM",
                            location=st.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=s_name,
                        target_kind="config_builder_struct",
                        evidences=evidences,
                        location=st.location or f.location,
                    )
                    detections.append(det)

        return detections
