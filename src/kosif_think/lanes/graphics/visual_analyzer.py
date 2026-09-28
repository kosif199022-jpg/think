"""
Visual Layout & Bounding Box Analyzer for KOSIF Think.
Calculates visual element layout geometries, overlap detection, and visual hierarchy.
"""

from typing import Dict, Any, List

class VisualLayoutAnalyzer:
    """Analyzes geometric bounds of UI elements and computes visual hierarchy."""

    def analyze_layout(self, elements: List[Dict[str, Any]], viewport_w: int = 1920, viewport_h: int = 1080) -> Dict[str, Any]:
        """Calculates visual balance, overlapping bounding boxes, and viewport coverage."""
        total_area = viewport_w * viewport_h
        covered_area = 0
        overlaps = 0

        rects = [e.get("rect") for e in elements if e.get("rect")]

        for i, r1 in enumerate(rects):
            w1 = r1.get("w", 0)
            h1 = r1.get("h", 0)
            covered_area += (w1 * h1)

            for j, r2 in enumerate(rects[i+1:], i+1):
                # Check overlap
                x1, y1 = r1.get("x", 0), r1.get("y", 0)
                x2, y2 = r2.get("x", 0), r2.get("y", 0)
                w2, h2 = r2.get("w", 0), r2.get("h", 0)

                if not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1):
                    overlaps += 1

        coverage_pct = round(min(100.0, (covered_area / max(1, total_area)) * 100), 2)

        return {
            "total_elements": len(elements),
            "elements_with_bounds": len(rects),
            "viewport": {"w": viewport_w, "h": viewport_h},
            "density_coverage_pct": coverage_pct,
            "detected_overlaps": overlaps,
            "is_clean_layout": overlaps == 0
        }
