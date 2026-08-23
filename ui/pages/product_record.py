"""Provenza AI - Modern Product Record Page

Commerce-ready product record with instant JSON/CSV export & traceability.
"""

import re
import streamlit as st
from app.export.exporter import export_to_json, export_to_csv


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_product_record(demo_mode: bool):
    """Render the final product record page."""

    if demo_mode:
        st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## 📦 Verified Product Record")
    st.caption("Commerce-ready structured product record with end-to-end evidence lineage.")

    results = st.session_state.get("demo_results")

    if not results:
        st.info("No analysis results available. Run an analysis from the **Product Analysis** page first.")
        return

    product = results["product_record"]

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Product Header ──────────────────────────────
    render_html_clean(f"""
<div class="modern-card" style="border-color: rgba(16, 185, 129, 0.4);">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
<div>
<div style="font-size:1.4rem; font-weight:800; color:#ffffff;">{product.product_name}</div>
<div style="color:var(--text-secondary); font-size:0.88rem; margin-top:6px;">
<strong>Product ID:</strong> <span style="font-family:'JetBrains Mono'; color:#60a5fa;">{product.product_id}</span> &nbsp;|&nbsp;
<strong>Model:</strong> <span style="font-family:'JetBrains Mono'; color:#f8fafc;">{product.model_number}</span> &nbsp;|&nbsp;
<strong>Brand:</strong> {product.brand} &nbsp;|&nbsp;
<strong>Category:</strong> {product.category}
</div>
</div>
<div style="text-align:right;">
<div style="font-size:2.2rem; font-weight:800; color:{'#34d399' if product.overall_confidence >= 0.9 else '#fbbf24'}; font-family:'JetBrains Mono';">
{product.overall_confidence*100:.0f}%
</div>
<div style="color:var(--text-muted); font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;">
Overall Reconciled Trust
</div>
</div>
</div>
</div>
""")

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Attributes Table ────────────────────────────
    st.markdown("### Reconciled Attributes Matrix")

    table_rows = []
    for attr_name, attr in product.attributes.items():
        conf = attr.confidence
        conf_color = "#34d399" if conf >= 0.9 else "#fbbf24" if conf >= 0.7 else "#f87171"

        status_map = {
            "validated": ("status-badge status-badge-match", "Validated"),
            "provisionally_validated": ("status-badge status-badge-match", "Prov. Validated"),
            "enriched": ("status-badge status-badge-enriched", "Enriched"),
            "reviewed": ("status-badge status-badge-match", "Human Reviewed"),
            "requires_review": ("status-badge status-badge-conflict", "Review Required"),
            "conflict": ("status-badge status-badge-conflict", "Conflict"),
        }

        css_class, status_label = status_map.get(attr.status, ("status-badge", attr.status.title()))

        table_rows.append(f"""
<tr style="background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid rgba(255,255,255,0.05);">
<td style="padding:12px 16px; font-weight:700; color:#f8fafc; font-size:0.88rem;">{attr.display_name or attr.attribute}</td>
<td style="padding:12px 16px; color:#ffffff; font-weight:700; font-family:'JetBrains Mono'; font-size:0.9rem;">{attr.display_value}</td>
<td style="padding:12px 16px;"><span class="status-badge" style="background:rgba(255,255,255,0.08); color:#cbd5e1;">{attr.source}</span></td>
<td style="padding:12px 16px; color:{conf_color}; font-weight:800; font-family:'JetBrains Mono'; font-size:0.88rem;">{conf*100:.0f}%</td>
<td style="padding:12px 16px;"><span class="{css_class}">{status_label}</span></td>
</tr>
""")

    html_table = f"""
<div style="overflow-x:auto; border-radius:14px; border:1px solid rgba(255,255,255,0.08); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
<table style="width:100%; border-collapse:collapse;">
<thead>
<tr style="background: rgba(30, 41, 59, 0.8); border-bottom:1px solid rgba(255,255,255,0.1);">
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Attribute</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Reconciled Value</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Selected Source</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Trust Score</th>
<th style="padding:14px 16px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.06em;">Audit Status</th>
</tr>
</thead>
<tbody>
{''.join(table_rows)}
</tbody>
</table>
</div>
"""

    render_html_clean(html_table)

    st.markdown("<div style='margin: 18px 0;'></div>", unsafe_allow_html=True)

    # ── Export Buttons ──────────────────────────────
    st.markdown("### 📤 Export Commerce Record")

    export_col1, export_col2, _ = st.columns([1, 1, 3])

    json_str = export_to_json(product)
    csv_str = export_to_csv(product)

    with export_col1:
        st.download_button(
            label="📥 Export JSON Record",
            data=json_str,
            file_name=f"{product.product_id}_record.json",
            mime="application/json",
            use_container_width=True,
        )

    with export_col2:
        st.download_button(
            label="📥 Export CSV Matrix",
            data=csv_str,
            file_name=f"{product.product_id}_record.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── JSON Preview ────────────────────────────────
    with st.expander("🔍 View Raw Commerce-Ready JSON Schema"):
        st.code(json_str, language="json")
