"""Provenza AI - Conflict Review Page

Visual Diff Cards, deterministic trust comparison, and interactive Human-in-the-Loop review buttons.
"""

import re
import streamlit as st
from app.models.reconciliation import ConflictDetail
from app.storage.store import store


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_conflicts(demo_mode: bool):
    """Render the conflict review page."""

    if demo_mode:
        st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## ⚠️ Multi-Source Conflict Review")
    st.caption("Inspect cross-source data discrepancies with line-by-line evidence & deterministic recommendations.")

    results = st.session_state.get("demo_results")

    if not results:
        st.info("No analysis results available. Run an analysis from the **Product Analysis** page first.")
        return

    recon = results["reconciliation"]
    conflicts = recon.conflicts

    if not conflicts:
        st.success("✅ No conflicts detected! All product attributes match across sources.")
        return

    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)

    # Summary Alert Banner
    render_html_clean(f"""
<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
<div style="display: flex; align-items: center; gap: 12px;">
<span style="font-size: 1.5rem;">⚠️</span>
<div>
<div style="font-weight: 800; color: #fbbf24; font-size: 1.05rem;">{len(conflicts)} Discrepanc{'ies' if len(conflicts) > 1 else 'y'} Requiring Attention</div>
<div style="font-size: 0.82rem; color: #94a3b8;">Provenza AI flagged differing attributes across sources. Review evidence below to validate.</div>
</div>
</div>
<span class="status-badge status-badge-conflict">REQUIRES REVIEW</span>
</div>
""")

    # ── Render each conflict card ────────────────────
    for i, conflict in enumerate(conflicts):
        _render_conflict_card(conflict, i, results)


def _render_conflict_card(conflict: ConflictDetail, index: int, results: dict):
    """Render a single conflict detail card with review actions."""

    is_resolved = conflict.reviewer_decision is not None
    status_text = conflict.reviewer_decision or conflict.review_status

    render_html_clean(f"""
<div class="conflict-diff-container">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
<div>
<span style="font-size:1.25rem; font-weight:800; color:#fbbf24; letter-spacing: -0.01em;">
⚠ {conflict.display_name.upper()} DISCREPANCY
</span>
<span style="margin-left:10px; font-size:0.75rem; color:#94a3b8; font-family:'JetBrains Mono';">{conflict.conflict_id}</span>
</div>
<div>
<span class="{'status-badge status-badge-match' if is_resolved else 'status-badge status-badge-conflict'}">
{'✓ RESOLVED' if is_resolved else '● ACTION REQUIRED'}
</span>
</div>
</div>
""")

    # ── Source values side by side Split-View ───────
    col_a, col_vs, col_b = st.columns([5, 1, 5])

    with col_a:
        render_html_clean(f"""
<div class="diff-box-a">
<div style="color:#fbbf24; font-size:0.72rem; text-transform:uppercase; font-weight:800; letter-spacing:0.08em; margin-bottom:6px;">
SOURCE A (LEGACY)
</div>
<div style="font-weight:700; color:#f8fafc; font-size:0.95rem; margin-bottom:4px;">{conflict.source_a_name}</div>
<div style="font-size:1.8rem; font-weight:800; color:#fbbf24; font-family:'JetBrains Mono';">{conflict.source_a_display}</div>
<div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
<span style="color:#94a3b8; font-size:0.78rem;">Authority Rating:</span>
<span style="color:#fbbf24; font-weight:700; font-size:0.85rem; font-family:'JetBrains Mono';">
{conflict.source_a_reliability} ({conflict.source_a_reliability_score*100:.0f}%)
</span>
</div>
<div class="evidence-panel" style="margin-top:12px; background: rgba(0,0,0,0.3); border-color: rgba(245, 158, 11, 0.3);">
<strong>Source Evidence:</strong> "{conflict.source_a_evidence}"
</div>
</div>
""")

    with col_vs:
        render_html_clean("""
<div style="display:flex; align-items:center; justify-content:center; height:100%; min-height:160px;">
<div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #94a3b8; font-size: 0.9rem;">
VS
</div>
</div>
""")

    with col_b:
        render_html_clean(f"""
<div class="diff-box-b">
<div style="color:#34d399; font-size:0.72rem; text-transform:uppercase; font-weight:800; letter-spacing:0.08em; margin-bottom:6px;">
SOURCE B (CURRENT SPEC)
</div>
<div style="font-weight:700; color:#f8fafc; font-size:0.95rem; margin-bottom:4px;">{conflict.source_b_name}</div>
<div style="font-size:1.8rem; font-weight:800; color:#34d399; font-family:'JetBrains Mono';">{conflict.source_b_display}</div>
<div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
<span style="color:#94a3b8; font-size:0.78rem;">Authority Rating:</span>
<span style="color:#34d399; font-weight:700; font-size:0.85rem; font-family:'JetBrains Mono';">
{conflict.source_b_reliability} ({conflict.source_b_reliability_score*100:.0f}%)
</span>
</div>
<div class="evidence-panel" style="margin-top:12px; background: rgba(0,0,0,0.3); border-color: rgba(16, 185, 129, 0.3);">
<strong>Source Evidence:</strong> "{conflict.source_b_evidence}"
</div>
</div>
""")

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── AI Recommendation Box ───────────────────────
    render_html_clean(f"""
<div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 14px; padding: 20px; box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
<div style="color:#60a5fa; font-size:0.78rem; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; display:flex; align-items:center; gap:6px;">
<span>🤖 AI RECONCILIATION RECOMMENDATION</span>
</div>
<span class="status-badge status-badge-match">CONFIDENCE: {conflict.confidence*100:.0f}%</span>
</div>
<div style="display:flex; align-items:baseline; gap:14px; margin-bottom:8px;">
<span style="font-size:1.8rem; font-weight:800; color:#ffffff; font-family:'JetBrains Mono';">{conflict.display_recommendation}</span>
<span style="color:#94a3b8; font-size:0.85rem;">Recommended Source: <strong style="color:#60a5fa;">{conflict.recommendation_source}</strong></span>
</div>
<div style="color:#cbd5e1; font-size:0.88rem; line-height:1.6; background: rgba(0,0,0,0.2); padding: 12px 14px; border-radius: 8px;">
<strong>Explainable Rationale:</strong> {conflict.reasoning}
</div>
</div>
""")

    # ── Interactive Human-in-the-loop Toolbar ─────────
    if not is_resolved:
        st.markdown("#### 👤 Human-in-the-Loop Decision")

        btn_cols = st.columns([2, 2, 2, 3])

        with btn_cols[0]:
            if st.button(
                f"✅ Approve {conflict.display_recommendation}",
                key=f"approve_{index}",
                use_container_width=True,
            ):
                _resolve_conflict(conflict, "approved", conflict.recommendation, results)

        with btn_cols[1]:
            alt_val = conflict.source_a_display if conflict.recommendation == conflict.source_b_value else conflict.source_b_display
            if st.button(
                f"↩ Use {alt_val}",
                key=f"use_other_{index}",
                use_container_width=True,
            ):
                alt_raw = conflict.source_a_value if conflict.recommendation == conflict.source_b_value else conflict.source_b_value
                _resolve_conflict(conflict, "use_other", alt_raw, results)

        with btn_cols[2]:
            if st.button(
                "❌ Reject Both",
                key=f"reject_{index}",
                use_container_width=True,
            ):
                _resolve_conflict(conflict, "rejected", None, results)

        with btn_cols[3]:
            custom_val = st.text_input(
                "Custom Value Override",
                key=f"custom_val_{index}",
                placeholder="Enter custom value...",
                label_visibility="collapsed",
            )
            if custom_val and st.button("✏️ Override with Custom Value", key=f"edit_{index}", use_container_width=True):
                _resolve_conflict(conflict, "edited", custom_val, results)
    else:
        render_html_clean(f"""
<div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; justify-content: space-between;">
<div style="color: #c084fc; font-weight: 700; font-size: 0.9rem;">
✅ Reviewer Decision Recorded: {conflict.reviewer_decision.replace('_', ' ').title()} {f'({conflict.reviewer_value})' if conflict.reviewer_value else ''}
</div>
<span class="status-badge status-badge-enriched">LOGGED TO AUDIT TRAIL</span>
</div>
""")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 28px 0;'>", unsafe_allow_html=True)


def _resolve_conflict(conflict: ConflictDetail, decision: str, value, results: dict):
    """Apply human review decision to a conflict."""
    conflict.reviewer_decision = decision
    conflict.reviewer_value = str(value) if value else None
    conflict.review_status = decision

    # Update audit trail
    audit_trail = results.get("audit_trail")
    if audit_trail:
        audit_trail.add_entry(
            attribute=conflict.attribute,
            display_name=conflict.display_name,
            previous_value=f"{conflict.source_a_value} vs {conflict.source_b_value}",
            new_value=str(value) if value else "rejected",
            source="Human Reviewer",
            confidence=conflict.confidence,
            action=f"conflict_{decision}",
            decision=f"human_{decision}",
            reviewer="user",
            product_name=results.get("product_record", {}).product_name if hasattr(results.get("product_record"), "product_name") else "",
        )

    # Update product record
    product = results.get("product_record")
    if product and conflict.attribute in product.attributes:
        attr = product.attributes[conflict.attribute]
        attr.reviewer_decision = decision
        attr.review_required = False
        attr.status = "reviewed"
        if value:
            attr.value = str(value)

    st.success(f"Decision recorded: **{decision.replace('_', ' ').title()}**")
    st.rerun()
