"""Provenza AI - Modern Enterprise Application

Entry point for Provenza AI dashboard with glassmorphism UI & interactive visualizations.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from ui.styles import get_custom_css


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Provenza AI — AI Product Data Auditor",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def render_sidebar():
    """Render the ultra-modern navigation sidebar."""
    with st.sidebar:
        st.markdown("""
            <div style="padding: 10px 0 16px 0;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 8px 12px; border-radius: 12px; font-weight: 900; color: white; font-size: 1.2rem; box-shadow: 0 0 15px rgba(59,130,246,0.5);">P</div>
                    <div>
                        <div style="font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em;">PROVENZA AI</div>
                        <div style="font-size: 0.68rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;">Product Intelligence Platform</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 14px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 5px 12px; border-radius: 20px; width: fit-content;">
                    <span class="live-dot"></span>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #34d399; letter-spacing: 0.04em;">ENGINE ONLINE</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        # Navigation Options with glowing circles
        pages = [
            "●  📊 Overview",
            "●  🔬 Product Analysis",
            "●  📋 Source Comparison",
            "●  ⚠️ Conflicts",
            "●  ✅ Validation",
            "●  📦 Product Record",
            "●  📝 Audit Trail",
        ]

        page_selection = st.radio(
            "NAVIGATION",
            pages,
            label_visibility="visible",
        )

        # Strip circle indicator for internal routing
        page_clean = page_selection.replace("●  ", "")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)

        # Demo mode toggle
        demo_mode = st.toggle("Demo Mode (SS-304-V2)", value=True, key="demo_mode_toggle")
        if demo_mode:
            st.markdown('<span class="status-badge status-badge-enriched">⚡ HERO DEMO LOADED</span>', unsafe_allow_html=True)
            st.caption("Pre-loaded valve comparison dataset")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem; color:#64748b; text-align:center; font-style:italic;">'
            '"We don\'t just extract product data — we make it trustworthy."'
            '</div>',
            unsafe_allow_html=True,
        )

        return page_clean, demo_mode


def main():
    setup_page()
    page, demo_mode = render_sidebar()

    # Initialize session state
    if "demo_loaded" not in st.session_state:
        st.session_state.demo_loaded = False
    if "demo_results" not in st.session_state:
        st.session_state.demo_results = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False

    # Load demo data if demo mode is on
    if demo_mode and not st.session_state.demo_loaded:
        from app.demo.demo_data import run_demo_pipeline
        st.session_state.demo_results = run_demo_pipeline()
        st.session_state.demo_loaded = True
        st.session_state.analysis_complete = True

    # Reset if demo mode is turned off
    if not demo_mode and st.session_state.demo_loaded:
        st.session_state.demo_loaded = False
        st.session_state.demo_results = None
        st.session_state.analysis_complete = False

    # Route to page
    if page == "📊 Overview":
        from ui.pages.overview import render_overview
        render_overview(demo_mode)
    elif page == "🔬 Product Analysis":
        from ui.pages.product_analysis import render_product_analysis
        render_product_analysis(demo_mode)
    elif page == "📋 Source Comparison":
        from ui.pages.source_comparison import render_source_comparison
        render_source_comparison(demo_mode)
    elif page == "⚠️ Conflicts":
        from ui.pages.conflicts import render_conflicts
        render_conflicts(demo_mode)
    elif page == "✅ Validation":
        from ui.pages.validation import render_validation
        render_validation(demo_mode)
    elif page == "📦 Product Record":
        from ui.pages.product_record import render_product_record
        render_product_record(demo_mode)
    elif page == "📝 Audit Trail":
        from ui.pages.audit_trail import render_audit_trail
        render_audit_trail(demo_mode)


if __name__ == "__main__":
    main()
