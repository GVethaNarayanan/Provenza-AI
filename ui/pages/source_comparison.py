"""Provenza AI - Modern Source Comparison Page

Side-by-side attribute comparison table with status badges & match confidence.
"""

import re
import streamlit as st
import pandas as pd
from app.models.reconciliation import AttributeStatus


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


STATUS_BADGES = {
    AttributeStatus.MATCH: ('✓ MATCH', 'status-badge status-badge-match'),
    AttributeStatus.ENRICHED: ('+ ENRICHED', 'status-badge status-badge-enriched'),
    AttributeStatus.CONFLICT: ('⚠ CONFLICT', 'status-badge status-badge-conflict'),
    AttributeStatus.MISSING: ('— MISSING', 'status-badge'),
    AttributeStatus.UNCERTAIN: ('? UNCERTAIN', 'status-badge'),
}


def render_source_comparison(demo_mode: bool):
    """Render the source comparison page."""

    if demo_mode:
        st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## 📋 Multi-Source Attribute Comparison")
    st.caption("Granular side-by-side reconciliation matrix across ingested product documents.")

    results = st.session_state.get("demo_results")

    if not results:
        st.info("No analysis results available. Run an analysis from the **Product Analysis** page first.")
        return

    recon = results["reconciliation"]
    source_a = results["source_a"]
    source_b = results["source_b"]

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Product Match Confidence ────────────────────
    match_result = results.get("match_result", {})
    match_conf = match_result.get("overall_confidence", 0)
    match_quality = match_result.get("match_quality", "High")

    render_html_clean(f"""
<div class="modern-card" style="border-color: rgba(59, 130, 246, 0.4);">
<div style="font-size:0.78rem; font-weight:800; color:#60a5fa; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;">
🔗 MULTI-SOURCE PRODUCT MATCH CONFIDENCE
</div>
<div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
<div style="font-size:2.4rem; font-weight:800; color:{'#34d399' if match_conf >= 0.9 else '#fbbf24'}; font-family:'JetBrains Mono';">
{match_conf*100:.0f}%
</div>
<div style="flex:1; min-width:250px;">
<div style="background:rgba(255,255,255,0.08); border-radius:10px; height:10px; overflow:hidden;">
<div style="background:linear-gradient(90deg, #10b981, #60a5fa); height:100%; width:{match_conf*100:.0f}%;"></div>
</div>
<div style="color:var(--text-secondary); font-size:0.8rem; margin-top:6px;">
Match Rating: <strong style="color:#fff;">{match_quality} Match</strong> &nbsp;|&nbsp;
SKU: <strong>{match_result.get('sku_score', 0)*100:.0f}%</strong> &nbsp;|&nbsp;
Fuzzy Name: <strong>{match_result.get('fuzzy_name_score', 0)*100:.0f}%</strong> &nbsp;|&nbsp;
Semantic Embeddings: <strong>{match_result.get('semantic_score', 0)*100:.0f}%</strong>
</div>
</div>
</div>
</div>
""")

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Summary Badges Row (No truncation) ────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_html_clean(f"""
<div class="modern-card" style="padding:14px 18px; text-align:center;">
<div style="font-size:0.72rem; color:#34d399; font-weight:700;">✓ MATCHED ATTRIBUTES</div>
<div style="font-size:1.8rem; font-weight:800; color:#34d399; font-family:'JetBrains Mono';">{recon.matched_count}</div>
</div>
""")

    with col2:
        render_html_clean(f"""
<div class="modern-card" style="padding:14px 18px; text-align:center;">
<div style="font-size:0.72rem; color:#60a5fa; font-weight:700;">+ ENRICHED ATTRIBUTES</div>
<div style="font-size:1.8rem; font-weight:800; color:#60a5fa; font-family:'JetBrains Mono';">{recon.enriched_count}</div>
</div>
""")

    with col3:
        render_html_clean(f"""
<div class="modern-card" style="padding:14px 18px; text-align:center; border-color: rgba(245, 158, 11, 0.3);">
<div style="font-size:0.72rem; color:#fbbf24; font-weight:700;">⚠ DISCREPANCIES DETECTED</div>
<div style="font-size:1.8rem; font-weight:800; color:#fbbf24; font-family:'JetBrains Mono';">{recon.conflict_count}</div>
</div>
""")

    with col4:
        render_html_clean(f"""
<div class="modern-card" style="padding:14px 18px; text-align:center;">
<div style="font-size:0.72rem; color:#94a3b8; font-weight:700;">TOTAL RECONCILED</div>
<div style="font-size:1.8rem; font-weight:800; color:#fff; font-family:'JetBrains Mono';">{recon.total_attributes}</div>
</div>
""")

    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)

    # ── Comparison Table ────────────────────────────
    st.markdown("### Attribute Comparison Matrix")
    st.caption(f"Comparing Source A ({source_a.source_name}) vs Source B ({source_b.source_name})")

    # Build HTML table for rich formatting
    table_rows = []
    for entry in recon.entries:
        label, css_class = STATUS_BADGES.get(entry.status, ('?', 'status-badge'))

        # Format values
        val_a = entry.source_a_value or "—"
        if entry.source_a_unit:
            val_a = f"{val_a} {entry.source_a_unit}"

        val_b = entry.source_b_value or "—"
        if entry.source_b_unit:
            val_b = f"{val_b} {entry.source_b_unit}"

        # Highlight conflicts
        row_bg = "background: rgba(15, 23, 42, 0.6);"
        if entry.status == AttributeStatus.CONFLICT:
            row_bg = "background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b;"

        table_rows.append(f"""
<tr style="{row_bg}; border-bottom: 1px solid rgba(255,255,255,0.05);">
<td style="padding:14px 16px; font-weight:700; color:#f8fafc; font-size:0.9rem;">{entry.display_name}</td>
<td style="padding:14px 16px; color:#cbd5e1; font-family:'JetBrains Mono'; font-size:0.88rem;">{val_a}</td>
<td style="padding:14px 16px; color:#cbd5e1; font-family:'JetBrains Mono'; font-size:0.88rem;">{val_b}</td>
<td style="padding:14px 16px;"><span class="{css_class}">{label}</span></td>
<td style="padding:14px 16px; color:#94a3b8; font-weight:700; font-family:'JetBrains Mono'; font-size:0.88rem;">{entry.confidence*100:.0f}%</td>
</tr>
""")

    html_table = f"""
<div style="overflow-x:auto; border-radius:14px; border:1px solid rgba(255,255,255,0.08); box-shadow:0 8px 32px rgba(0,0,0,0.3);">
<table style="width:100%; border-collapse:collapse;">
<thead>
<tr style="background: rgba(30, 41, 59, 0.8); border-bottom:1px solid rgba(255,255,255,0.1);">
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Attribute Name</th>
<th style="padding:14px 16px; text-align:left; color:#fbbf24; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Source A ({source_a.source_name})</th>
<th style="padding:14px 16px; text-align:left; color:#34d399; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Source B ({source_b.source_name})</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Reconciliation Status</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Confidence</th>
</tr>
</thead>
<tbody>
{''.join(table_rows)}
</tbody>
</table>
</div>
"""

    render_html_clean(html_table)
