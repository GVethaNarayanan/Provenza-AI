"""Provenza AI - Modern Executive Overview Dashboard

Modern glassmorphism, interactive Plotly visualizations, hero insight banners,
and clear metric cards without text truncation.
"""

import re
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.storage.store import store


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_overview(demo_mode: bool):
    """Render the executive overview dashboard page."""

    # ── Executive Hero Insight Banner ───────────────────
    render_html_clean("""
<div class="hero-banner">
<div style="display: flex; justify-content: space-between; align-items: flex-start; wrap: flex-wrap; gap: 16px;">
<div>
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
<span style="background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.4); padding: 3px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">
⚡ AI EXECUTIVE INSIGHT
</span>
<span style="color: #94a3b8; font-size: 0.8rem;">Multi-Source Reconciliation Active</span>
</div>
<div style="font-size: 1.5rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 6px;">
Product Data Auditor Dashboard
</div>
<div style="color: #94a3b8; font-size: 0.88rem; max-width: 750px; line-height: 1.5;">
Provenza AI continuously ingests, normalizes, and reconciles fragmented technical specifications across legacy catalogs and modern spec sheets. 
</div>
</div>
<div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 12px 18px; text-align: right;">
<div style="font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Overall Catalog Health</div>
<div style="font-size: 1.8rem; font-weight: 800; color: #34d399; font-family: 'JetBrains Mono', monospace;">91.4%</div>
<div style="font-size: 0.72rem; color: #60a5fa;">Trust-Weighted Verified</div>
</div>
</div>
</div>
""")

    # Get stats
    stats = store.get_stats()
    results = st.session_state.get("demo_results")

    if results:
        recon = results["reconciliation"]
        stats["attributes_extracted"] = recon.total_attributes
        stats["conflicts_detected"] = recon.conflict_count
        matched = recon.matched_count + recon.enriched_count
        stats["attributes_validated"] = matched
        stats["fields_requiring_review"] = recon.conflict_count

    # ── Metric Cards Row (No Truncation) ────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        render_html_clean(f"""
<div class="modern-card" style="padding:16px 18px;">
<div style="font-size:0.72rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
📦 PRODUCTS ANALYZED
</div>
<div style="font-size:2rem; font-weight:800; color:#fff; font-family:'JetBrains Mono';">
{stats.get("products_analyzed", 1)}
</div>
<div style="font-size:0.72rem; color:#34d399; margin-top:4px;">● Active Catalog</div>
</div>
""")

    with col2:
        render_html_clean(f"""
<div class="modern-card" style="padding:16px 18px;">
<div style="font-size:0.72rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
⚡ ATTRIBUTES EXTRACTED
</div>
<div style="font-size:2rem; font-weight:800; color:#60a5fa; font-family:'JetBrains Mono';">
{stats.get("attributes_extracted", 13)}
</div>
<div style="font-size:0.72rem; color:#94a3b8; margin-top:4px;">Across Multi-Sources</div>
</div>
""")

    with col3:
        render_html_clean(f"""
<div class="modern-card" style="padding:16px 18px; border-color: rgba(245, 158, 11, 0.3);">
<div style="font-size:0.72rem; font-weight:700; color:#fbbf24; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
⚠ CONFLICTS DETECTED
</div>
<div style="font-size:2rem; font-weight:800; color:#fbbf24; font-family:'JetBrains Mono';">
{stats.get("conflicts_detected", 2)}
</div>
<div style="font-size:0.72rem; color:#fbbf24; margin-top:4px;">150 vs 200 PSI Hero Discrepancy</div>
</div>
""")

    with col4:
        render_html_clean(f"""
<div class="modern-card" style="padding:16px 18px;">
<div style="font-size:0.72rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
✅ ATTRIBUTES VALIDATED
</div>
<div style="font-size:2rem; font-weight:800; color:#34d399; font-family:'JetBrains Mono';">
{stats.get("attributes_validated", 11)}
</div>
<div style="font-size:0.72rem; color:#34d399; margin-top:4px;">Matched + Enriched</div>
</div>
""")

    with col5:
        render_html_clean(f"""
<div class="modern-card" style="padding:16px 18px;">
<div style="font-size:0.72rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
🛡️ REVIEW REQUIRED
</div>
<div style="font-size:2rem; font-weight:800; color:#a78bfa; font-family:'JetBrains Mono';">
{stats.get("fields_requiring_review", 2)}
</div>
<div style="font-size:0.72rem; color:#a78bfa; margin-top:4px;">Human Review Ready</div>
</div>
""")

    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)

    # ── Processing Pipeline Node Flow ──────────────────
    st.markdown("### 🔄 Multi-Source Processing Pipeline")

    steps = [
        ("1. Ingestion", "PyMuPDF + pdfplumber", "✓"),
        ("2. AI Extraction", "Gemini 2.0 Flash JSON", "✓"),
        ("3. Normalization", "Unit & Term Normalizer", "✓"),
        ("4. Product Match", "Embeddings + SKU Match", "✓"),
        ("5. Reconciliation", "Deterministic Comparison", "✓"),
        ("6. Trust Scoring", "Deterministic Trust Scoring", "✓"),
    ]

    pipeline_cols = st.columns(6)
    for (step_name, desc, check), col in zip(steps, pipeline_cols):
        with col:
            render_html_clean(f"""
<div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
<div style="font-size: 0.72rem; color: #34d399; font-weight: 800;">{check} COMPLETE</div>
<div style="font-size: 0.82rem; font-weight: 700; color: #f8fafc; margin: 4px 0;">{step_name}</div>
<div style="font-size: 0.68rem; color: #94a3b8;">{desc}</div>
</div>
""")

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # ── Visual Analytics Section (Interactive Plotly Charts) ──
    col_chart_l, col_chart_r = st.columns([1, 1])

    with col_chart_l:
        st.markdown("### 📊 Attribute Reconciliation Status")

        if results:
            recon = results["reconciliation"]
            labels = ["Matched Attributes", "Enriched Attributes", "Conflict Fields"]
            values = [recon.matched_count, recon.enriched_count, recon.conflict_count]
            colors = ["#10b981", "#3b82f6", "#f59e0b"]

            fig_donut = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.6,
                marker_colors=colors,
                textinfo='label+percent',
                insidetextorientation='radial',
                hoverinfo='label+value+percent'
            )])

            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=20, b=40, l=20, r=20),
                height=280
            )

            st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart_r:
        st.markdown("### 🎯 Trust Confidence Breakdown")

        if results:
            product = results["product_record"]
            high = sum(1 for a in product.attributes.values() if a.confidence >= 0.90)
            medium = sum(1 for a in product.attributes.values() if 0.70 <= a.confidence < 0.90)
            low = sum(1 for a in product.attributes.values() if a.confidence < 0.70)

            categories = ['High Trust (≥90%)', 'Medium Trust (70-89%)', 'Low Trust (<70%)']
            counts = [high, medium, low]
            bar_colors = ['#10b981', '#f59e0b', '#ef4444']

            fig_bar = go.Figure(data=[go.Bar(
                x=counts,
                y=categories,
                orientation='h',
                marker=dict(color=bar_colors, cornerradius=8),
                text=counts,
                textposition='auto',
            )])

            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
                xaxis=dict(showgrid=False, title="Number of Attributes"),
                yaxis=dict(showgrid=False),
                margin=dict(t=20, b=40, l=20, r=20),
                height=280
            )

            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)

    # ── Active Product & Data Sources ─────────────────
    if results:
        st.markdown("### 📌 Active Hero Product & Source Reliability")

        prod_col1, prod_col2 = st.columns([1, 1])

        with prod_col1:
            product = results["product_record"]
            recon = results["reconciliation"]

            render_html_clean(f"""
<div class="modern-card">
<div style="font-size:1.1rem; font-weight:800; color:#fff; margin-bottom:8px;">
{product.product_name}
</div>
<div style="color:var(--text-secondary); font-size:0.85rem; line-height:1.6;">
<strong>SKU / Model:</strong> <span style="font-family:'JetBrains Mono'; color:#60a5fa;">{product.model_number}</span><br>
<strong>Brand:</strong> {product.brand}<br>
<strong>Category:</strong> {product.category}
</div>
<div style="margin-top:14px; display:flex; gap:8px;">
<span class="status-badge status-badge-match">✓ {recon.matched_count} Matched</span>
<span class="status-badge status-badge-enriched">+ {recon.enriched_count} Enriched</span>
<span class="status-badge status-badge-conflict">⚠ {recon.conflict_count} Conflicts</span>
</div>
</div>
""")

        with prod_col2:
            sa = results["source_a"]
            sb = results["source_b"]

            render_html_clean(f"""
<div class="modern-card">
<div style="font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:10px;">
📄 Source Authority Matrix
</div>
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.08);">
<div>
<div style="font-weight:600; font-size:0.85rem; color:#f8fafc;">Source A: {sa.source_name}</div>
<div style="font-size:0.75rem; color:#fbbf24;">{sa.authority_label}</div>
</div>
<div style="font-weight:800; font-family:'JetBrains Mono'; color:#fbbf24; font-size:1.1rem;">60% Trust</div>
</div>
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<div style="font-weight:600; font-size:0.85rem; color:#f8fafc;">Source B: {sb.source_name}</div>
<div style="font-size:0.75rem; color:#34d399;">{sb.authority_label}</div>
</div>
<div style="font-weight:800; font-family:'JetBrains Mono'; color:#34d399; font-size:1.1rem;">95% Trust</div>
</div>
</div>
""")

    # ── Value Proposition Footer ───────────────────────
    render_html_clean("""
<div class="modern-card" style="text-align:center; padding:28px;">
<div style="font-size:1.05rem; font-weight:700; color:var(--text-primary); margin-bottom:10px;">
Why Provenza AI Multi-Source Reconciliation?
</div>
<div style="color:var(--text-secondary); font-size:0.88rem; max-width:750px; margin:0 auto; line-height:1.7;">
Standard AI systems say: <em>"Here is the extracted product data."</em><br>
<strong>Provenza AI</strong> says: <em>"Here is the reconciled product record, exactly where every attribute originated, the line-by-line evidence, our trust confidence score, detected conflicts, and why this specific value was chosen."</em>
</div>
</div>
""")
