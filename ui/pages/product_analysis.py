"""Provenza AI - Product Analysis Page

Product input, source upload, and analysis execution.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path


def render_product_analysis(demo_mode: bool):
    """Render the product analysis page."""

    if demo_mode:
        st.markdown('<span class="demo-badge">DEMO DATA</span>', unsafe_allow_html=True)

    st.markdown("## 🔬 Product Analysis")
    st.caption("Upload product sources and analyze for multi-source reconciliation")

    st.markdown("---")

    # ── Product Input ───────────────────────────────
    st.markdown("### Product Information")

    results = st.session_state.get("demo_results")

    if demo_mode and results:
        pi = results["product_input"]
        col1, col2 = st.columns(2)
        with col1:
            product_id = st.text_input("Product ID / SKU", value=pi.sku, key="prod_id")
            brand = st.text_input("Brand", value=pi.brand, key="prod_brand")
        with col2:
            product_name = st.text_input("Product Name", value=pi.product_name, key="prod_name")
            description = st.text_input("Short Description", value=pi.short_description, key="prod_desc")
    else:
        col1, col2 = st.columns(2)
        with col1:
            product_id = st.text_input("Product ID / SKU", placeholder="e.g., SS-304-V2", key="prod_id")
            brand = st.text_input("Brand", placeholder="e.g., ValveTech Industries", key="prod_brand")
        with col2:
            product_name = st.text_input("Product Name", placeholder="e.g., Stainless Steel Ball Valve", key="prod_name")
            description = st.text_input("Short Description", placeholder="Brief product description", key="prod_desc")

    st.markdown("---")

    # ── Source Upload ───────────────────────────────
    st.markdown("### 📄 Data Sources")

    src_col1, src_col2 = st.columns(2)

    with src_col1:
        st.markdown("#### Source A")
        if demo_mode:
            st.markdown(f"""
            <div class="card">
                <div style="color:var(--text-primary); font-weight:500;">📄 Old Product Catalog</div>
                <div style="color:var(--text-muted); font-size:0.8rem; margin-top:4px;">
                    PDF • Authority: Medium • March 2023
                </div>
            </div>
            """, unsafe_allow_html=True)
            source_a_authority = st.selectbox(
                "Source A Authority",
                ["Older Catalog", "Authorized Catalog", "Manufacturer Website",
                 "Current Manufacturer Technical Specification", "Unverified Third-Party Source"],
                index=0,
                key="src_a_auth",
            )
        else:
            file_a = st.file_uploader(
                "Upload Source A",
                type=["pdf", "txt", "csv", "xlsx"],
                key="file_a",
            )
            source_a_authority = st.selectbox(
                "Source A Authority",
                ["Older Catalog", "Authorized Catalog", "Manufacturer Website",
                 "Current Manufacturer Technical Specification", "Unverified Third-Party Source"],
                key="src_a_auth",
            )

    with src_col2:
        st.markdown("#### Source B")
        if demo_mode:
            st.markdown(f"""
            <div class="card">
                <div style="color:var(--text-primary); font-weight:500;">📄 New Technical Specification</div>
                <div style="color:var(--text-muted); font-size:0.8rem; margin-top:4px;">
                    PDF • Authority: Very High • June 2026
                </div>
            </div>
            """, unsafe_allow_html=True)
            source_b_authority = st.selectbox(
                "Source B Authority",
                ["Current Manufacturer Technical Specification", "Manufacturer Website",
                 "Authorized Catalog", "Older Catalog", "Unverified Third-Party Source"],
                index=0,
                key="src_b_auth",
            )
        else:
            file_b = st.file_uploader(
                "Upload Source B",
                type=["pdf", "txt", "csv", "xlsx"],
                key="file_b",
            )
            source_b_authority = st.selectbox(
                "Source B Authority",
                ["Current Manufacturer Technical Specification", "Manufacturer Website",
                 "Authorized Catalog", "Older Catalog", "Unverified Third-Party Source"],
                key="src_b_auth",
            )

    st.markdown("---")

    # ── Analysis Button ─────────────────────────────
    if demo_mode:
        if st.button("🔬 Analyze Product", use_container_width=True, type="primary"):
            _run_demo_analysis()
    else:
        if st.button("🔬 Analyze Product", use_container_width=True, type="primary"):
            if not (product_name or product_id):
                st.error("Please enter a product name or ID.")
            elif 'file_a' not in st.session_state or st.session_state.file_a is None:
                st.error("Please upload at least Source A.")
            else:
                _run_live_analysis(
                    product_id, product_name, brand, description,
                    source_a_authority, source_b_authority,
                )

    # ── Pipeline Status ─────────────────────────────
    if st.session_state.get("analysis_complete"):
        st.markdown("---")
        st.markdown("### ✅ Analysis Complete")

        steps = ["Ingested", "Extracted", "Normalized", "Matched", "Reconciled", "Validated"]
        pipeline_html = " → ".join(
            f'<span class="pipeline-step pipeline-done">✓ {s}</span>'
            for s in steps
        )
        st.markdown(pipeline_html, unsafe_allow_html=True)

        if results:
            recon = results["reconciliation"]
            st.markdown("")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attributes", recon.total_attributes)
            with col2:
                st.metric("Matched", recon.matched_count)
            with col3:
                st.metric("Enriched", recon.enriched_count)
            with col4:
                st.metric("Conflicts", recon.conflict_count)

            st.success("Navigate to **Source Comparison** to see detailed results, or **Conflicts** to review detected conflicts.")


def _run_demo_analysis():
    """Run demo analysis pipeline."""
    with st.spinner("Running AI analysis pipeline..."):
        import time

        progress = st.progress(0, text="Ingesting documents...")
        time.sleep(0.4)
        progress.progress(15, text="Extracting product attributes...")
        time.sleep(0.4)
        progress.progress(35, text="Normalizing values and units...")
        time.sleep(0.3)
        progress.progress(55, text="Matching products across sources...")
        time.sleep(0.3)
        progress.progress(70, text="Reconciling multi-source data...")
        time.sleep(0.4)
        progress.progress(85, text="Running trust-weighted validation...")
        time.sleep(0.3)
        progress.progress(100, text="Analysis complete!")
        time.sleep(0.2)

    from app.demo.demo_data import run_demo_pipeline
    st.session_state.demo_results = run_demo_pipeline()
    st.session_state.demo_loaded = True
    st.session_state.analysis_complete = True
    st.rerun()


def _run_live_analysis(product_id, product_name, brand, description,
                       source_a_authority, source_b_authority):
    """Run live analysis with uploaded files."""
    from datetime import datetime
    from app.models.source import SourceMetadata, SourceType, SourceAuthority
    from app.ingestion.pdf_parser import PDFParser
    from app.ingestion.text_parser import TextParser
    from app.ingestion.csv_parser import CSVParser
    from app.extraction.llm_extractor import LLMExtractor
    from app.reconciliation.engine import ReconciliationEngine
    from app.matching.product_matcher import calculate_match_confidence
    from app.storage.store import store
    from app.config import UPLOADS_DIR

    AUTHORITY_MAP = {
        "Current Manufacturer Technical Specification": SourceAuthority.VERY_HIGH,
        "Manufacturer Website": SourceAuthority.HIGH,
        "Authorized Catalog": SourceAuthority.MEDIUM_HIGH,
        "Older Catalog": SourceAuthority.MEDIUM,
        "Unverified Third-Party Source": SourceAuthority.LOW,
    }

    progress = st.progress(0, text="Starting analysis...")

    try:
        # Save uploaded files
        file_a = st.session_state.file_a
        file_b = st.session_state.get("file_b")

        path_a = str(UPLOADS_DIR / file_a.name)
        with open(path_a, "wb") as f:
            f.write(file_a.getbuffer())

        path_b = None
        if file_b:
            path_b = str(UPLOADS_DIR / file_b.name)
            with open(path_b, "wb") as f:
                f.write(file_b.getbuffer())

        # Setup sources
        source_a = SourceMetadata(
            source_name=file_a.name,
            source_type=SourceType(Path(file_a.name).suffix.lower().lstrip('.')),
            authority=AUTHORITY_MAP.get(source_a_authority, SourceAuthority.MEDIUM),
            recency_date=datetime.now(),
        )

        source_b = None
        if path_b and file_b:
            source_b = SourceMetadata(
                source_name=file_b.name,
                source_type=SourceType(Path(file_b.name).suffix.lower().lstrip('.')),
                authority=AUTHORITY_MAP.get(source_b_authority, SourceAuthority.MEDIUM),
                recency_date=datetime.now(),
            )

        # Parse documents
        progress.progress(15, text="Ingesting documents...")
        parsers = [PDFParser(), TextParser(), CSVParser()]

        parsed_a = None
        for parser in parsers:
            if parser.can_parse(path_a):
                parsed_a = parser.parse(path_a, source_a.source_id, source_a.source_name)
                break

        if not parsed_a or not parsed_a.parse_success:
            st.error(f"Failed to parse Source A: {parsed_a.error_message if parsed_a else 'Unknown format'}")
            return

        parsed_b = None
        if path_b and source_b:
            for parser in parsers:
                if parser.can_parse(path_b):
                    parsed_b = parser.parse(path_b, source_b.source_id, source_b.source_name)
                    break

        # Extract attributes
        progress.progress(35, text="Extracting product attributes with AI...")
        extractor = LLMExtractor()
        attrs_a = extractor.extract(parsed_a)

        if not attrs_a:
            st.error("Failed to extract attributes from Source A. Please check your API key.")
            return

        attrs_b = []
        if parsed_b:
            attrs_b = extractor.extract(parsed_b)

        progress.progress(55, text="Normalizing and matching...")

        # Match products
        match_result = {"overall_confidence": 0.0, "is_match": False}
        if attrs_b:
            match_result = calculate_match_confidence(attrs_a, attrs_b, use_embeddings=False)

        progress.progress(70, text="Reconciling multi-source data...")

        # Reconcile
        engine = ReconciliationEngine()
        if attrs_b and source_b:
            reconciliation = engine.reconcile(
                attrs_a, attrs_b, source_a, source_b,
                product_id=product_id or "PRD-LIVE",
            )
        else:
            # Single source — no reconciliation needed
            reconciliation = engine.reconcile(
                attrs_a, [], source_a,
                SourceMetadata(source_name="(No second source)", source_type=SourceType.MANUAL),
                product_id=product_id or "PRD-LIVE",
            )

        progress.progress(85, text="Building product record...")

        # Build product record
        audit_trail = store.get_or_create_audit_trail(product_id or "PRD-LIVE")
        product_record = engine.build_product_record(
            reconciliation=reconciliation,
            product_input={
                "product_id": product_id or "PRD-LIVE",
                "product_name": product_name,
                "brand": brand,
                "category": "",
                "model_number": product_id,
            },
            source_a=source_a,
            source_b=source_b or SourceMetadata(source_name="(No second source)", source_type=SourceType.MANUAL),
            audit_trail=audit_trail,
        )

        store.save_product(product_record)
        store.save_reconciliation(reconciliation)

        progress.progress(100, text="Analysis complete!")

        # Store results
        st.session_state.demo_results = {
            "product_input": type('PI', (), {
                "product_id": product_id, "sku": product_id, "brand": brand,
                "product_name": product_name, "short_description": description, "category": ""
            })(),
            "source_a": source_a,
            "source_b": source_b or SourceMetadata(source_name="(No second source)", source_type=SourceType.MANUAL),
            "attrs_a": attrs_a,
            "attrs_b": attrs_b,
            "match_result": match_result,
            "reconciliation": reconciliation,
            "product_record": product_record,
            "audit_trail": audit_trail,
        }
        st.session_state.analysis_complete = True
        st.rerun()

    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
