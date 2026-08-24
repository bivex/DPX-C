"""Tests for Scanning and Detection Services in DPX-C."""

from __future__ import annotations

from pattern_detector.bootstrap.container import create_container


def test_scanning_service_memory():
    sources = {
        "src/buffer.c": """
        typedef struct buffer_s buffer_t;

        buffer_t* buffer_create(size_t cap) {
            buffer_t* b = (buffer_t*)malloc(sizeof(buffer_t));
            if (!b) return NULL;
            return b;
        }

        void buffer_destroy(buffer_t* b) {
            if (b) free(b);
        }
        """
    }
    container = create_container()
    scanner = container.get_scanner()
    report = scanner.scan_sources(sources)

    assert report.scanned_files_count == 1
    assert report.total_detections_count >= 1
    assert any(d.pattern_type.value == "opaque_pointer_adt" for d in report.detections)
