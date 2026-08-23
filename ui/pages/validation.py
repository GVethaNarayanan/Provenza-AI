"""Provenza AI - Modern Validation Status Page

Deterministic trust-weighted validation matrix with transparent scoring breakdowns.
"""

import re
import streamlit as st
from app.reconciliation.trust_scorer import TrustScorer
from app.config import TRUST_WEIGHTS


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_validation(demo_mode: bool):
    """Render the validation status page."""

    if demo_mode:
        st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## ✅ Trust-Weighted Validation Engine")
    st.caption("Transparent deterministic scoring architecture without LLM black-box decision making.")

    results = st.session_state.get("demo_results")

    if not results:
        st.info("No analysis results available. Run an analysis from the **Product Analysis** page first.")
        return

    product = results["product_record"]

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Trust Scoring Configuration Header ─────────────────
    st.markdown("### ⚙️ Deterministic Trust Model Weights")

    weight_cols = st.columns(5)
    labels = {
        "source_authority": "Source Authority",
        "recency": "Recency Date",
        "evidence_quality": "Evidence Quality",
        "extraction_confidence": "LLM Confidence",
        "cross_source_agreement": "Cross Agreement",
    }

    for (key, label), col in zip(labels.items(), weight_cols):
        w = TRUST_WEIGHTS[key]
        with col:
            render_html_clean(f"""
<div class="modern-card" style="text-align:center; padding:14px;">
<div style="color:var(--text-muted); font-size:0.72rem; text-transform:uppercase; font-weight:700; margin-bottom:4px;">
{label}
</div>
<div style="font-size:1.5rem; font-weight:800; color:#60a5fa; font-family:'JetBrains Mono';">
{w*100:.0f}%
</div>
</div>
""")

    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)

    # ── Field Validation Table ──────────────────────
    st.markdown("### 📋 Field-Level Trust Matrix")

    for attr_name, attr in product.attributes.items():
        _render_validation_row(attr)

    # ── Overall Confidence ──────────────────────────
    st.markdown("<div style='margin: 18px 0;'></div>", unsafe_allow_html=True)
    overall = product.overall_confidence

    render_html_clean(f"""
<div class="modern-card" style="text-align:center; padding:26px; border-color: rgba(59, 130, 246, 0.4);">
<div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; font-weight:800; letter-spacing:0.08em; margin-bottom:8px;">
Overall Verified Catalog Confidence
</div>
<div style="font-size:2.8rem; font-weight:800; color:{'#34d399' if overall >= 0.9 else '#fbbf24' if overall >= 0.7 else '#f87171'}; font-family:'JetBrains Mono';">
{overall*100:.0f}%
</div>
<div style="background:rgba(255,255,255,0.08); border-radius:10px; height:10px; max-width:400px; margin:14px auto 0; overflow:hidden;">
<div style="background:linear-gradient(90deg, #10b981, #60a5fa); height:100%; width:{overall*100:.0f}%;"></div>
</div>
<div style="color:var(--text-secondary); font-size:0.88rem; margin-top:10px;">
Catalog Governance Status: <strong style="color:#fff;">{product.review_status.replace('_', ' ').title()}</strong>
</div>
</div>
""")


def _render_validation_row(attr):
    """Render a single attribute validation row."""

    conf = attr.confidence
    conf_color = "#34d399" if conf >= 0.9 else "#fbbf24" if conf >= 0.7 else "#f87171"

    status_map = {
        "validated": ("status-badge status-badge-match", "Validated"),
        "provisionally_validated": ("status-badge status-badge-match", "Prov. Validated"),
        "enriched": ("status-badge status-badge-enriched", "Enriched"),
        "reviewed": ("status-badge status-badge-match", "Reviewed"),
        "requires_review": ("status-badge status-badge-conflict", "Review Required"),
        "conflict": ("status-badge status-badge-conflict", "Conflict"),
        "pending": ("status-badge", "Pending"),
    }

    css_class, status_label = status_map.get(attr.status, ("status-badge", attr.status))

    review_badge = ""
    if attr.reviewer_decision:
        review_badge = f'<span class="status-badge status-badge-enriched" style="margin-left:8px;">👤 {attr.reviewer_decision.replace("_", " ").title()}</span>'

    render_html_clean(f"""
<div class="modern-card" style="padding:16px 20px;">
<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
<div style="flex:1;">
<div style="display:flex; align-items:center; gap:10px;">
<span style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{attr.display_name or attr.attribute}</span>
<span class="{css_class}">{status_label}</span>
{review_badge}
</div>
<div style="color:#cbd5e1; font-size:0.88rem; margin-top:4px; font-family:'JetBrains Mono';">
{attr.display_value} &nbsp;·&nbsp; Source: <span style="color:#60a5fa;">{attr.source}</span>
</div>
{'<div class="evidence-panel" style="margin-top:8px; font-size:0.82rem;">"' + attr.evidence + '"</div>' if attr.evidence else ''}
{'<div style="color:#94a3b8; font-size:0.8rem; margin-top:4px;"><em>Rationale: ' + attr.reasoning + '</em></div>' if attr.reasoning else ''}
</div>
<div style="text-align:right; min-width:90px;">
<div style="font-size:1.4rem; font-weight:800; color:{conf_color}; font-family:'JetBrains Mono';">{conf*100:.0f}%</div>
<div style="background:rgba(255,255,255,0.08); border-radius:6px; height:6px; width:70px; margin-top:4px; overflow:hidden;">
<div style="background:{conf_color}; height:100%; width:{conf*100:.0f}%;"></div>
</div>
</div>
</div>
</div>
""")
