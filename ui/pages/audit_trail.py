"""Provenza AI - Modern Audit Trail Page

Chronological history of all extraction, normalization, conflict resolution & reviewer decisions.
"""

import re
import streamlit as st
from app.storage.store import store


def render_html_clean(html_str: str):
    """Render HTML safely without markdown code-block conversion."""
    cleaned = re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def render_audit_trail(demo_mode: bool):
    """Render the audit trail page."""

    if demo_mode:
        st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## 📝 Compliance Audit Trail")
    st.caption("Immutable chronological lineage log for complete enterprise catalog auditability.")

    results = st.session_state.get("demo_results")

    if not results:
        st.info("No audit entries available. Run an analysis from the **Product Analysis** page first.")
        return

    audit_trail = results.get("audit_trail")
    if not audit_trail or not audit_trail.entries:
        st.info("No audit entries recorded yet.")
        return

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    entries = sorted(audit_trail.entries, key=lambda e: e.timestamp, reverse=True)

    # ── Action filter ───────────────────────────────
    actions = sorted(set(e.action for e in entries))
    selected_actions = st.multiselect(
        "Filter Audit Events",
        options=actions,
        default=actions,
        key="audit_filter",
    )

    filtered = [e for e in entries if e.action in selected_actions]

    st.markdown("<div style='margin: 14px 0;'></div>", unsafe_allow_html=True)

    # ── Build table ─────────────────────────────────
    table_rows = []
    for entry in filtered:
        action_colors = {
            "match": "#34d399",
            "enriched": "#60a5fa",
            "conflict": "#fbbf24",
            "conflict_approved": "#c084fc",
            "conflict_edited": "#c084fc",
            "conflict_rejected": "#f87171",
            "conflict_use_other": "#c084fc",
        }
        action_color = action_colors.get(entry.action, "#9ca3af")

        decision_badge = ""
        if "human" in entry.decision:
            decision_badge = f'<span class="status-badge status-badge-enriched" style="font-size:0.7rem;">👤 {entry.decision.replace("_", " ").title()}</span>'
        elif entry.decision:
            decision_badge = f'<span class="status-badge" style="font-size:0.7rem; background:rgba(255,255,255,0.08); color:#cbd5e1;">{entry.decision.replace("_", " ").title()}</span>'

        conf_display = f"{entry.confidence*100:.0f}%" if entry.confidence > 0 else "—"

        table_rows.append(f"""
<tr style="background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid rgba(255,255,255,0.05);">
<td style="padding:10px 14px; color:#94a3b8; font-size:0.78rem; font-family:'JetBrains Mono'; white-space:nowrap;">{entry.timestamp}</td>
<td style="padding:10px 14px; font-weight:700; color:#f8fafc; font-size:0.88rem;">{entry.display_name or entry.attribute}</td>
<td style="padding:10px 14px; color:#cbd5e1; font-size:0.85rem; font-family:'JetBrains Mono';">{entry.previous_value or "—"}</td>
<td style="padding:10px 14px; color:#ffffff; font-weight:700; font-size:0.88rem; font-family:'JetBrains Mono';">{entry.new_value or "—"}</td>
<td style="padding:10px 14px;"><span style="color:{action_color}; font-weight:800; font-size:0.82rem;">{entry.action.replace('_', ' ').title()}</span></td>
<td style="padding:10px 14px;"><span class="status-badge" style="background:rgba(255,255,255,0.08); color:#cbd5e1;">{entry.source}</span></td>
<td style="padding:10px 14px; color:#94a3b8; font-family:'JetBrains Mono'; font-weight:700; font-size:0.85rem;">{conf_display}</td>
<td style="padding:10px 14px;">{decision_badge}</td>
</tr>
""")

    html_table = f"""
<div style="overflow-x:auto; border-radius:14px; border:1px solid rgba(255,255,255,0.08); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
<table style="width:100%; border-collapse:collapse;">
<thead>
<tr style="background: rgba(30, 41, 59, 0.8); border-bottom:1px solid rgba(255,255,255,0.1);">
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Timestamp</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Attribute</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Previous Value</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">New Reconciled Value</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Action Event</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Source</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Trust Score</th>
<th style="padding:12px 14px; text-align:left; color:#94a3b8; font-weight:700; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em;">Decision Type</th>
</tr>
</thead>
<tbody>
{''.join(table_rows)}
</tbody>
</table>
</div>
"""

    render_html_clean(html_table)
