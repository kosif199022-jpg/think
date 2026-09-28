"""
Generative Canvas & Interactive HTML5 UI Engine for KOSIF Think.
Synthesizes self-contained interactive web widgets, data visualizations, and dashboards.
"""

from typing import Dict, Any, List

class GenerativeCanvas:
    """Builds interactive HTML5 Canvas visualizers and reactive UI widgets."""

    def build_dashboard_widget(self, title: str, metrics: List[Dict[str, Any]], chart_points: List[float]) -> str:
        """Generates self-contained interactive HTML widget with dark mode styling."""
        metric_cards = []
        for m in metrics:
            color = m.get("color", "#38bdf8")
            metric_cards.append(f"""
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; flex: 1; min-width: 160px;">
                <div style="font-size: 13px; color: #94a3b8; margin-bottom: 4px;">{m.get('label')}</div>
                <div style="font-size: 26px; font-weight: 700; color: {color};">{m.get('value')}</div>
                <div style="font-size: 12px; color: #10b981; margin-top: 4px;">{m.get('sub', '')}</div>
            </div>
            """)

        pts_json = str(chart_points)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 24px; font-family: system-ui, -apple-system, sans-serif; background: #0b0f19; color: #f8fafc; }}
  .container {{ max-width: 800px; margin: 0 auto; background: #131c2e; border: 1px solid #1e293b; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
  .title {{ font-size: 20px; font-weight: 700; color: #f1f5f9; }}
  .metrics-grid {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  canvas {{ width: 100%; height: 240px; background: #0f172a; border-radius: 12px; border: 1px solid #1e293b; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="title">⚡ {title}</div>
    <span style="font-size: 12px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; padding: 4px 10px; border-radius: 20px; font-weight: 600;">LIVE METRICS</span>
  </div>
  <div class="metrics-grid">
    {''.join(metric_cards)}
  </div>
  <canvas id="chartCanvas"></canvas>
</div>
<script>
  const canvas = document.getElementById('chartCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth - 48;
  canvas.height = 240;
  
  const data = {pts_json};
  const padding = 30;
  const w = canvas.width - padding * 2;
  const h = canvas.height - padding * 2;
  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const range = (maxVal - minVal) || 1;

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 3;
  ctx.lineJoin = 'round';
  ctx.beginPath();

  data.forEach((val, i) => {{
    const x = padding + (i / (data.length - 1)) * w;
    const y = canvas.height - padding - ((val - minVal) / range) * h;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }});
  ctx.stroke();

  // Gradient fill under curve
  ctx.lineTo(padding + w, canvas.height - padding);
  ctx.lineTo(padding, canvas.height - padding);
  ctx.closePath();
  const grad = ctx.createLinearGradient(0, padding, 0, canvas.height - padding);
  grad.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
  grad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
  ctx.fillStyle = grad;
  ctx.fill();
</script>
</body>
</html>"""
        return html
