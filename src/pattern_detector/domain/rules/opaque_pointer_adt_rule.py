"""C Opaque Pointer / Abstract Data Type (ADT) Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class OpaquePointerAdtRule(BasePatternRule):
    """Detects Opaque Pointer / ADT information hiding idiom in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.OPAQUE_POINTER_ADT

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            # Check for typedef struct foo foo_t; or struct foo_s* foo_create(...)
            for td_name, td in f.typedefs.items():
                if "struct" in td.target_type:
                    stem = td_name.rstrip("_t").rstrip("_s")
                    create_fn = f.find_function(f"{stem}_create") or f.find_function(f"{stem}_new") or f.find_function(f"{stem}_init")
                    destroy_fn = f.find_function(f"{stem}_destroy") or f.find_function(f"{stem}_free") or f.find_function(f"{stem}_deinit")

                    evidences = []
                    if create_fn:
                        evidences.append(
                            Evidence(
                                description=f"Provides constructor factory function '{create_fn.name}()'",
                                weight=0.60,
                                rule_code="OPAQUE_FACTORY_CONSTRUCTOR",
                                location=create_fn.location or td.location,
                            )
                        )
                    if destroy_fn:
                        evidences.append(
                            Evidence(
                                description=f"Provides destructor release function '{destroy_fn.name}()'",
                                weight=0.60,
                                rule_code="OPAQUE_FACTORY_DESTRUCTOR",
                                location=destroy_fn.location or td.location,
                            )
                        )

                    if evidences:
                        evidences.insert(
                            0,
                            Evidence(
                                description=f"Encapsulates Abstract Data Type via Opaque Pointer '{td_name}'",
                                weight=0.75,
                                rule_code="OPAQUE_POINTER_TYPEDEF",
                                location=td.location,
                            ),
                        )
                        det = self._create_detection(
                            target_name=td_name,
                            target_kind="opaque_adt_struct",
                            evidences=evidences,
                            location=td.location,
                        )
                        if det.confidence.score >= 0.70:
                            detections.append(det)

        return detections
