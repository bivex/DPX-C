"""C Potential Memory Leak Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class MemoryLeakMissingFreeRule(BasePatternRule):
    """Detects functions that allocate memory without corresponding free on error paths."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.MEMORY_LEAK_MISSING_FREE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        dealloc_indicators = (
            "free(", "fclose(", "zfree(", "uv__free(", "uv_free(", "cJSON_free(",
            "luaM_free(", "sdsfree(", "je_free(", "free_", "_free(", "_destroy(",
            "_release(", "_close(", "_deinit(", "_cleanup(", "cleanup:"
        )

        container_save_keywords = (
            "_add(", "_insert(", "_push(", "_set(", "_register(", "_append(", "_put("
        )

        for f in model.all_files():
            for fn in f.functions.values():
                if fn.name == "main":
                    continue

                body = fn.body
                has_alloc = "malloc(" in body or "calloc(" in body or "fopen(" in body
                if not has_alloc:
                    continue

                has_dealloc = any(d in body for d in dealloc_indicators)
                returns_ptr = "*" in fn.return_type or "struct " in fn.return_type
                has_out_param = any(p.type_str.count("*") >= 2 or "*" in p.name for p in fn.params)
                stores_to_struct = "->" in body or any(k in body for k in container_save_keywords)

                if not (has_dealloc or returns_ptr or has_out_param or stores_to_struct):
                    evidences = [
                        Evidence(
                            description=f"Memory Safety Risk (Potential Leak): Function '{fn.id_str}' in '{f.file_path}' allocates local resources without deallocating them or returning them to caller",
                            weight=0.75,
                            rule_code="LOCAL_ALLOCATION_WITHOUT_FREE",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="potential_leak_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
