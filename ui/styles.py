"""Provenza AI - Modern Enterprise CSS Engine

Glassmorphism, dark mode neon accents, futuristic navigation, and custom layout styling.
"""


def get_custom_css() -> str:
    return """
<style>
    /* ── Import Google Fonts ──────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Root Design System Tokens ────────────────────── */
    :root {
        --bg-main: #060911;
        --bg-sidebar: #0b0f19;
        --bg-glass: rgba(15, 23, 42, 0.75);
        --bg-glass-hover: rgba(30, 41, 59, 0.85);
        --bg-card: #0f172a;
        --bg-input: #1e293b;
        
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glow-blue: rgba(59, 130, 246, 0.4);
        --border-glow-amber: rgba(245, 158, 11, 0.4);
        --border-glow-emerald: rgba(16, 185, 129, 0.4);

        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;

        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --accent-purple: #a855f7;

        --gradient-blue: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        --gradient-emerald: linear-gradient(135deg, #10b981 0%, #047857 100%);
        --gradient-amber: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
        --gradient-purple: linear-gradient(135deg, #a855f7 0%, #6b21a8 100%);
        --gradient-glass: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        
        --radius-sm: 8px;
        --radius-md: 14px;
        --radius-lg: 20px;

        --shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.2);
        --shadow-glow-amber: 0 0 20px rgba(245, 158, 11, 0.2);
    }

    /* ── Global Page Overrides ────────────────────────── */
    .stApp {
        background-color: var(--bg-main) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* Hide default header */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* ── Sidebar Custom Styling ───────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-glass) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.5) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }

    /* Modern Radio Navigation Styling */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        gap: 8px !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 14px !important;
        margin: 2px 0 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
        transform: translateX(3px) !important;
    }

    /* Radio Indicator Circle Custom Styling */
    section[data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
        letter-spacing: -0.01em !important;
    }

    /* Highlight Active Radio Option */
    section[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.5) !important;
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.25) !important;
    }

    section[data-testid="stSidebar"] .stRadio label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* ── Executive Metric Cards (No Truncation) ───────── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        padding: 18px 22px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: visible !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-glow-blue) !important;
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-glow-blue) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        white-space: normal !important; /* Fix truncation! */
        word-wrap: break-word !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.03em !important;
    }

    /* Custom Hero Executive Card */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: var(--radius-lg);
        padding: 24px 28px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, rgba(0,0,0,0) 70%);
        pointer-events: none;
    }

    /* ── Modern Glass Card ───────────────────────────── */
    .modern-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-md);
        padding: 22px 26px;
        backdrop-filter: blur(16px);
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .modern-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* ── Status Pills & Badges ────────────────────────── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .status-badge-match {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.15);
    }

    .status-badge-enriched {
        background: rgba(59, 130, 246, 0.12);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.15);
    }

    .status-badge-conflict {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 16px rgba(245, 158, 11, 0.2);
        animation: pulse-amber 2s infinite;
    }

    @keyframes pulse-amber {
        0% { box-shadow: 0 0 8px rgba(245, 158, 11, 0.2); }
        50% { box-shadow: 0 0 20px rgba(245, 158, 11, 0.4); }
        100% { box-shadow: 0 0 8px rgba(245, 158, 11, 0.2); }
    }

    /* ── Split Conflict Visual Diff Card ─────────────── */
    .conflict-diff-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid var(--border-glow-amber);
        border-radius: var(--radius-lg);
        padding: 26px;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(245, 158, 11, 0.12);
    }

    .diff-box-a {
        background: rgba(245, 158, 11, 0.05);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: var(--radius-md);
        padding: 18px;
    }

    .diff-box-b {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: var(--radius-md);
        padding: 18px;
    }

    /* ── Modern Button Customization ──────────────────── */
    .stButton > button {
        background: var(--gradient-blue) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 10px 24px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.5) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background: var(--gradient-emerald) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
    }

    /* ── Tab Bar Styling ─────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        padding: 6px !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--gradient-blue) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    /* Live Badge */
    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #10b981;
    }
</style>
"""
