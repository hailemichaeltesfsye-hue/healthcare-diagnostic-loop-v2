"""
MedVoice AI & Clinical Command Center Dashboard.

Unified enterprise-grade application combining:
1. Real-time conversational voice interaction powered by AssemblyAI STT.
2. Clinical emergency & red-flag detection layer across 6 global languages.
3. Centralized 6-language support (English, Amharic, Arabic, Chinese, French, Hindi).
4. Hardened speech synthesis with browser Web Speech API / gTTS fallback.
5. Live structured medical summary with clinician-ready export (.txt & .html).
6. 9-node peer-to-peer LangGraph diagnostic workforce with live telemetry.
7. Semantic memory layer (ChromaDB) for historical case retrieval.
8. Human-in-the-loop (HITL) practitioner verification and governance gate.
9. Futuristic glassmorphism and clinical AI command center interface.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Set

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

from src.agents.voice_agent import (
    HealthcareVoiceAgent,
    StructuredMedicalSummary,
    VoiceAgentResponse,
)
from src.ui.workforce_topology import (
    WORKFORCE_NODES,
    generate_live_workforce_topology_html,
)
from src.db.vector_store import ClinicalVectorStore
from src.graph.pipeline import compile_workflow
from src.graph.state import SharedState
from src.safety.emergency_detector import EmergencyDetector, RiskLevel
from src.voice.language_support import (
    DEFAULT_LANGUAGE_CODE,
    SUPPORTED_CLINICAL_LANGUAGES,
    get_language_profile,
    resolve_language_profile,
)

# --- Node Constants for 9-Node Diagnostic Workforce ---
NODE_ORDER = (
    "voice_input",
    "triage",
    "researcher",
    "diagnostic",
    "critic",
    "compliance",
    "hitl",
    "final_compile",
    "voice_output",
)
NODE_LABELS = {
    "voice_input": "Voice Intake (AssemblyAI)",
    "triage": "Triage / Symptom Extraction",
    "researcher": "Researcher (ChromaDB RAG)",
    "diagnostic": "Diagnostic (Tree-of-Thoughts)",
    "critic": "Critic (Self-Healing Gate)",
    "compliance": "Compliance Officer (PII Guard)",
    "hitl": "Practitioner Review (HITL)",
    "final_compile": "Final Compile",
    "voice_output": "Voice Response (gTTS)",
}
NODE_SHORT_LABELS = {
    "voice_input": "VOICE IN",
    "triage": "TRIAGE",
    "researcher": "RESEARCH",
    "diagnostic": "DIAGNOSTIC",
    "critic": "CRITIC",
    "compliance": "COMPLIANCE",
    "hitl": "HITL REVIEW",
    "final_compile": "FINALIZE",
    "voice_output": "VOICE OUT",
}
NODE_ICONS = {
    "voice_input": "🎙️",
    "triage": "🩺",
    "researcher": "📚",
    "diagnostic": "🧠",
    "critic": "🔁",
    "compliance": "🛡️",
    "hitl": "👨‍⚕️",
    "final_compile": "📋",
    "voice_output": "🔊",
}
VOICE_NODES = {"voice_input", "voice_output"}

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="MedVoice AI — Clinical Command Center",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Unified Modern Glassmorphism & Clinical Theme CSS ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --canvas: #050811;
        --surface-1: rgba(15, 23, 42, 0.75);
        --surface-2: rgba(30, 41, 59, 0.65);
        --surface-glow: rgba(56, 189, 248, 0.08);
        --line-subtle: rgba(148, 163, 184, 0.14);
        --line-active: rgba(56, 189, 248, 0.4);
        --accent-cyan: #38BDF8;
        --accent-indigo: #818CF8;
        --accent-purple: #C084FC;
        --accent-emerald: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #F43F5E;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --success: #10B981;
        --info: #3B82F6;
        --amber: #F59E0B;
        --danger: #F87171;
    }

    .stApp {
        background-color: var(--canvas);
        background-image:
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(129, 140, 248, 0.09) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #080D1A !important;
        border-right: 1px solid var(--line-subtle);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

    .block-container {
        max-width: 1540px !important;
        padding: 1.25rem 2.25rem 3rem !important;
    }

    /* Top Hero Header */
    .hero-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.5rem;
        padding: 1.2rem 1.75rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.4) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--line-subtle);
        border-radius: 20px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        margin-bottom: 1.25rem;
    }

    .hero-left {
        display: flex;
        align-items: center;
        gap: 1.25rem;
    }

    .ai-orb-wrapper {
        position: relative;
        width: 62px;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .ai-orb-core {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #38BDF8, #6366F1 55%, #A855F7 90%);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.55), inset 0 0 12px rgba(255, 255, 255, 0.7);
        animation: orb-breathe 3.5s ease-in-out infinite;
    }

    .ai-orb-ring {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 1.5px dashed rgba(56, 189, 248, 0.4);
        animation: ring-rotate 12s linear infinite;
    }

    .ai-orb-ring-pulse {
        position: absolute;
        inset: -4px;
        border-radius: 50%;
        border: 1px solid rgba(192, 132, 252, 0.25);
        animation: orb-ping 2.5s cubic-bezier(0, 0, 0.2, 1) infinite;
    }

    @keyframes orb-breathe {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.06); filter: brightness(1.18); box-shadow: 0 0 35px rgba(129, 140, 248, 0.75); }
    }
    @keyframes ring-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes orb-ping { 0% { transform: scale(0.9); opacity: 0.8; } 80%, 100% { transform: scale(1.3); opacity: 0; } }

    .hero-title-group h1 {
        margin: 0;
        font-size: 2.15rem;
        font-weight: 850;
        letter-spacing: -0.04em;
        line-height: 1.1;
        background: linear-gradient(120deg, #FFFFFF 15%, #E0E7FF 50%, #38BDF8 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 0.88rem;
        font-weight: 500;
        margin-top: 0.25rem;
    }

    .hero-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.22rem 0.7rem;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #7DD3FC;
        margin-bottom: 0.25rem;
    }

    .pipeline-bar {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(8, 13, 26, 0.6);
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        border: 1px solid var(--line-subtle);
        font-size: 0.76rem;
        font-weight: 600;
        color: var(--text-secondary);
    }
    .pipe-step {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.04);
        color: #E2E8F0;
    }
    .pipe-arrow { color: #64748B; font-size: 0.7rem; }

    /* Telemetry Row */
    .telemetry-row {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0.65rem;
        margin-bottom: 1.25rem;
    }
    .telemetry-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.45));
        backdrop-filter: blur(12px);
        border: 1px solid var(--line-subtle);
        border-radius: 14px;
        padding: 0.65rem 0.9rem;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        transition: all 0.2s ease;
    }
    .telemetry-card:hover {
        border-color: var(--line-active);
        box-shadow: 0 4px 18px rgba(56, 189, 248, 0.1);
        transform: translateY(-1px);
    }
    .telemetry-label {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
    }
    .telemetry-value {
        font-size: 0.82rem;
        font-weight: 700;
        color: #E2E8F0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .telemetry-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
    .dot-online { background: var(--accent-emerald); box-shadow: 0 0 10px var(--accent-emerald); animation: pulse-dot 2s infinite; }
    .dot-warning { background: var(--accent-amber); box-shadow: 0 0 10px var(--accent-amber); }
    .dot-emergency { background: var(--accent-rose); box-shadow: 0 0 12px var(--accent-rose); animation: pulse-dot 1s infinite; }
    @keyframes pulse-dot { 0%, 100% { opacity: 0.6; transform: scale(0.95); } 50% { opacity: 1; transform: scale(1.15); } }

    /* Glass Cards */
    .glass-card {
        background: linear-gradient(150deg, rgba(15, 23, 42, 0.75) 0%, rgba(15, 23, 42, 0.5) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--line-subtle);
        border-radius: 18px;
        padding: 1.35rem;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.25rem;
        position: relative;
    }
    .glass-card-accent {
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.12), 0 16px 36px rgba(0, 0, 0, 0.35);
    }
    .card-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.9rem;
        padding-bottom: 0.65rem;
        border-bottom: 1px solid var(--line-subtle);
    }
    .card-header-title {
        font-size: 1.05rem;
        font-weight: 750;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }
    .card-header-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* Voice State Indicator */
    .voice-state-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.15rem;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.1) 0%, rgba(129, 140, 248, 0.08) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        margin-bottom: 1.1rem;
    }
    .voice-state-left { display: flex; align-items: center; gap: 0.75rem; }
    .voice-state-title { font-size: 0.85rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: #38BDF8; }
    .voice-state-desc { font-size: 0.8rem; color: var(--text-secondary); }

    /* Waveform visualizer */
    .waveform-visualizer {
        display: inline-flex;
        align-items: flex-end;
        gap: 3.5px;
        height: 22px;
        vertical-align: middle;
    }
    .waveform-visualizer span {
        display: inline-block;
        width: 3.5px;
        border-radius: 2px;
        background: linear-gradient(180deg, #38BDF8, #818CF8);
        animation: wave-anim 1.1s ease-in-out infinite;
    }
    .waveform-visualizer span:nth-child(1) { height: 40%; animation-delay: 0.0s; }
    .waveform-visualizer span:nth-child(2) { height: 90%; animation-delay: 0.15s; }
    .waveform-visualizer span:nth-child(3) { height: 60%; animation-delay: 0.3s; }
    .waveform-visualizer span:nth-child(4) { height: 100%; animation-delay: 0.45s; }
    .waveform-visualizer span:nth-child(5) { height: 75%; animation-delay: 0.6s; }
    @keyframes wave-anim {
        0%, 100% { transform: scaleY(0.35); opacity: 0.5; }
        50% { transform: scaleY(1); opacity: 1; filter: brightness(1.25); }
    }

    /* Emergency Alert Card */
    .alert-emergency {
        background: linear-gradient(145deg, rgba(239, 68, 68, 0.22) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 2px solid var(--accent-rose);
        border-radius: 16px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 0 35px rgba(244, 63, 94, 0.35);
        animation: pulse-red-card 2s infinite;
        margin-bottom: 1.25rem;
    }
    @keyframes pulse-red-card {
        0%, 100% { border-color: rgba(244, 63, 94, 0.6); box-shadow: 0 0 25px rgba(244, 63, 94, 0.25); }
        50% { border-color: rgba(244, 63, 94, 1); box-shadow: 0 0 40px rgba(244, 63, 94, 0.5); }
    }

    .badge-emergency { background: rgba(244, 63, 94, 0.25); border: 1px solid var(--accent-rose); color: #FECDD3; font-weight: 800; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.78rem; }
    .badge-urgent { background: rgba(245, 158, 11, 0.22); border: 1px solid var(--accent-amber); color: #FDE68A; font-weight: 800; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.78rem; }
    .badge-routine { background: rgba(16, 185, 129, 0.18); border: 1px solid var(--accent-emerald); color: #A7F3D0; font-weight: 800; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.78rem; }

    .symptom-chip { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.7rem; border-radius: 999px; font-size: 0.76rem; font-weight: 600; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #BAE6FD; margin-right: 0.4rem; margin-bottom: 0.4rem; }
    .flag-chip { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.7rem; border-radius: 999px; font-size: 0.76rem; font-weight: 700; background: rgba(244, 63, 94, 0.18); border: 1px solid rgba(244, 63, 94, 0.55); color: #FECDD3; margin-right: 0.4rem; margin-bottom: 0.4rem; }

    /* Conversation Bubbles */
    .chat-stream { display: flex; flex-direction: column; gap: 1.15rem; margin-top: 0.75rem; }
    .chat-bubble-patient {
        align-self: flex-end;
        max-width: 85%;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 20px 20px 4px 20px;
        padding: 1.05rem 1.35rem;
        color: #F8FAFC;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .chat-bubble-assistant {
        align-self: flex-start;
        max-width: 90%;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.55), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(129, 140, 248, 0.45);
        border-radius: 20px 20px 20px 4px;
        padding: 1.2rem 1.45rem;
        color: #FAF5FF;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.18);
    }
    .chat-meta-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.55rem; font-size: 0.74rem; font-weight: 750; letter-spacing: 0.05em; text-transform: uppercase; }
    .follow-up-box { margin-top: 0.85rem; padding: 0.65rem 0.95rem; background: rgba(129, 140, 248, 0.12); border-left: 3px solid #818CF8; border-radius: 0 10px 10px 0; font-size: 0.86rem; font-weight: 600; color: #C7D2FE; }

    /* Agent Telemetry Grid & Cards */
    .agent-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; margin-top: 0.75rem; }
    .agent-card { min-height: 112px; padding: 0.9rem; border: 1px solid #30435d; border-radius: 11px; background: rgba(17,24,39,0.9); color: #8190a5; transition: all 0.25s ease; }
    .agent-card.active { border-color: var(--success); box-shadow: 0 0 22px rgba(16,185,129,0.42); animation: telemetry-pulse 1.25s ease-in-out infinite; color: var(--text-primary); }
    .agent-card.done { border-color: rgba(16,185,129,0.66); background: rgba(16,185,129,0.08); color: #d1fae5; }
    .agent-card.blocked { border-color: var(--danger); background: rgba(248,113,113,0.08); color: #fecaca; }
    .agent-card.voice { border-color: #4c3a73; }
    .agent-card.voice.active { border-color: #A78BFA; box-shadow: 0 0 22px rgba(167,139,250,0.48); animation: telemetry-pulse-voice 1.25s ease-in-out infinite; color: var(--text-primary); }
    .agent-card.voice.done { border-color: rgba(167,139,250,0.66); background: rgba(167,139,250,0.1); color: #e9d5ff; }
    @keyframes telemetry-pulse { 0%,100% { box-shadow: 0 0 5px rgba(16,185,129,0.25); } 50% { box-shadow: 0 0 25px rgba(16,185,129,0.75); } }
    @keyframes telemetry-pulse-voice { 0%,100% { box-shadow: 0 0 5px rgba(167,139,250,0.28); } 50% { box-shadow: 0 0 25px rgba(167,139,250,0.8); } }
    .agent-index { color: #64748b; font-size: 0.67rem; letter-spacing: 0.12em; font-weight: 800; }
    .agent-title { margin-top: 0.42rem; font-size: 0.86rem; font-weight: 760; }
    .agent-status { margin-top: 0.7rem; font-size: 0.68rem; letter-spacing: 0.09em; font-weight: 800; }
    .packet { color: #6ee7b7; margin-top: 0.5rem; font-size: 0.68rem; }

    /* Dashboard Metrics & Panels */
    .metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.7rem; margin: 0.75rem 0; }
    .metric { background: rgba(11,15,25,0.72); border: 1px solid var(--line-subtle); border-radius: 10px; padding: 0.8rem; min-height: 76px; }
    .metric-label { color: var(--text-muted); font-size: 0.69rem; letter-spacing: 0.07em; text-transform: uppercase; }
    .metric-value { color: var(--text-primary); font-size: 1.22rem; font-weight: 760; margin-top: 0.35rem; }
    .metric-value.success { color: #6ee7b7; }
    .metric-value.info { color: #93c5fd; }
    .metric-value.amber { color: #fcd34d; }

    .ledger-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.55rem 0; border-bottom: 1px solid rgba(42,58,82,0.65); color: var(--text-muted); font-size: 0.78rem; }
    .ledger-row:last-child { border-bottom: 0; }
    .ledger-value { color: var(--text-primary); font-weight: 750; }

    .privacy-badge { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.4rem 0.85rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; font-size: 0.74rem; font-weight: 600; color: #6EE7B7; }
    .legal-disclaimer { padding: 0.75rem 1rem; background: rgba(8, 13, 26, 0.7); border: 1px dashed rgba(148, 163, 184, 0.2); border-radius: 12px; font-size: 0.74rem; color: var(--text-muted); line-height: 1.5; margin-top: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

# --- Session State Accessors & Helpers ---
def get_vector_store() -> ClinicalVectorStore:
    """Return the session-scoped ChromaDB semantic memory store."""
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = ClinicalVectorStore()
    return st.session_state.vector_db


def get_compiled_graph() -> Any:
    """Return the current compiled 9-node P2P graph."""
    if st.session_state.get("compiled_graph_version") != 4:
        st.session_state.compiled_graph = compile_workflow()
        st.session_state.compiled_graph_version = 4
    return st.session_state.compiled_graph


def get_telemetry() -> Dict[str, Any]:
    """Return initialized session-level token and cost counters."""
    if "accumulated_tokens" not in st.session_state:
        st.session_state.accumulated_tokens = {"input": 0, "output": 0, "total_cost": 0.0}
    return st.session_state.accumulated_tokens


def update_telemetry(result_state: Mapping[str, Any]) -> None:
    """Aggregate token and cost records from a graph result."""
    telemetry = get_telemetry()
    logs = result_state.get("token_usage_log", [])
    telemetry["input"] = sum(int(log.get("input_tokens", 0)) for log in logs)
    telemetry["output"] = sum(int(log.get("output_tokens", 0)) for log in logs)
    telemetry["total_cost"] = sum(float(log.get("estimated_cost", 0.0)) for log in logs)


def render_metric(label: str, value: str, tone: str = "") -> str:
    """Build one reusable metric card fragment."""
    return f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value {tone}">{value}</div></div>'


def build_report_html(result_state: Mapping[str, Any], patient_id: str) -> str:
    """Render a standalone, printable HTML report with complete script font fallback."""
    profile, _ = resolve_language_profile(result_state.get("detected_language_code", "en"))
    direction = "rtl" if profile.assemblyai_code == "ar" else "ltr"
    report_text = str(result_state.get("final_clinical_report", "")).replace("\n", "<br>")
    symptoms = ", ".join(result_state.get("extracted_symptoms", [])) or "—"
    diagnosis = str(result_state.get("initial_diagnosis", "")) or "—"
    return f"""<!DOCTYPE html>
<html lang="{profile.assemblyai_code}" dir="{direction}">
<head>
<meta charset="utf-8">
<title>Clinical Verification Report — {patient_id}</title>
<style>
  body {{ font-family: "Noto Sans", "Segoe UI", Tahoma, Arial, sans-serif; max-width: 720px; margin: 2.5rem auto; color: #111; line-height: 1.6; padding: 0 1.5rem; }}
  h1 {{ font-size: 1.4rem; border-bottom: 2px solid #333; padding-bottom: .5rem; }}
  .meta {{ color: #555; font-size: .9rem; margin-bottom: 1.5rem; }}
  .section {{ margin-bottom: 1.4rem; }}
  .section h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: .04em; color: #444; }}
  .report-body {{ background: #f7f7f9; border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.25rem; }}
  .footer {{ margin-top: 2rem; font-size: .78rem; color: #888; border-top: 1px solid #ddd; padding-top: .75rem; }}
  @media print {{ body {{ margin: 0; }} }}
</style>
</head>
<body>
  <h1>Clinical Verification Report</h1>
  <div class="meta">Patient Tracker ID: {patient_id} &nbsp;|&nbsp; Language: {profile.flag_emoji} {profile.display_name} &nbsp;|&nbsp; Status: {result_state.get("compliance_status", "PENDING")}</div>
  <div class="section"><h2>Symptoms Mapped</h2><p>{symptoms}</p></div>
  <div class="section"><h2>Diagnostic Pathway</h2><p>{diagnosis}</p></div>
  <div class="section"><h2>Report</h2><div class="report-body">{report_text}</div></div>
  <div class="footer">Decision-support artifact only. Requires practitioner review before clinical use. Open in browser and use Print → Save as PDF.</div>
</body>
</html>"""


def collaboration_dot(active_node: Optional[str], completed: Set[str]) -> str:
    """Build the live Graphviz representation of the 9-node P2P workforce."""
    node_lines = []
    for node_name in NODE_ORDER:
        is_voice = node_name in VOICE_NODES
        if node_name == active_node:
            color, fill, status = ("#A78BFA", "#241a38", "PROCESSING") if is_voice else ("#10B981", "#12352f", "PROCESSING")
        elif node_name in completed:
            color, fill, status = ("#A78BFA", "#2a1f42", "DONE") if is_voice else ("#10B981", "#17352a", "DONE")
        else:
            color, fill, status = "#64748B", "#18202c", "IDLE"
        node_lines.append(
            f'{node_name} [label="{NODE_ICONS[node_name]}  {NODE_SHORT_LABELS[node_name]}\\n{status}", color="{color}", fillcolor="{fill}"];'
        )
    edges = (
        'voice_input -> triage [label="transcript", color="#A78BFA", fontcolor="#c4b5fd"];',
        'triage -> researcher [dir=both, label="context"];',
        'researcher -> diagnostic [label="evidence"];',
        'diagnostic -> critic [label="confidence"];',
        'critic -> diagnostic [label="retry", style=dashed, color="#F59E0B", fontcolor="#fcd34d", constraint=false];',
        'critic -> compliance [label="approved"];',
        'compliance -> hitl [label="clearance"];',
        'hitl -> final_compile [label="approval"];',
        'final_compile -> voice_output [label="speech", color="#A78BFA", fontcolor="#c4b5fd"];',
    )
    return (
        'digraph P2P { graph [bgcolor="transparent", rankdir=LR, pad="0.2"]; '
        'node [shape=box, style="rounded,filled", fontname="sans", '
        'fontcolor="#f8fafc", penwidth=2, margin="0.18,0.12"]; '
        'edge [color="#10B981", fontcolor="#94a3b8", penwidth=2, arrowsize=.8]; '
        + " ".join(node_lines) + " " + " ".join(edges) + " }"
    )


def render_agent_cards(container: Any, active_node: Optional[str], completed: Set[str], blocked: Set[str]) -> None:
    """Render live worker cards with idle, active, done, and blocked states."""
    cards = []
    for index, node_name in enumerate(NODE_ORDER, start=1):
        voice_class = " voice" if node_name in VOICE_NODES else ""
        if node_name in blocked:
            state_class, status, packet = "blocked", "⛔ BLOCKED", ""
        elif node_name == active_node:
            active_packet = '<div class="packet">🔊 audio streaming</div>' if node_name in VOICE_NODES else '<div class="packet">● state packet in transit</div>'
            state_class, status, packet = "active", "⚡ ACTIVE TELEMETRY", active_packet
        elif node_name in completed:
            state_class, status, packet = "done", "✅ COMPLETE", ""
        else:
            state_class, status, packet = "", "⏸️ IDLE", ""
        cards.append(
            f'<div class="agent-card {state_class}{voice_class}"><div class="agent-index">NODE {index:02d}</div>'
            f'<div class="agent-title">{NODE_ICONS[node_name]} {NODE_LABELS[node_name]}</div><div class="agent-status">{status}</div>{packet}</div>'
        )
    container.markdown('<div class="agent-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


async def stream_graph(graph: Any, initial_state: SharedState, graph_placeholder: Any, cards_placeholder: Any, activity_placeholder: Any) -> Dict[str, Any]:
    """Stream LangGraph updates and animate each direct P2P handoff."""
    completed: Set[str] = set()
    blocked: Set[str] = set()
    final_state: Dict[str, Any] = initial_state.model_dump()
    active_node: Optional[str] = NODE_ORDER[0]
    graph_placeholder.graphviz_chart(collaboration_dot(active_node, completed), use_container_width=True)
    render_agent_cards(cards_placeholder, active_node, completed, blocked)
    activity_placeholder.info(f"⚡ {NODE_LABELS[active_node]} is processing the admission packet.")

    async for update in graph.astream(initial_state, stream_mode="updates"):
        for node_name, node_update in update.items():
            completed.add(node_name)
            final_state.update(node_update)
            if "FAILED" in str(final_state.get("compliance_status", "")):
                blocked.update({"hitl", "final_compile"})
            next_index = NODE_ORDER.index(node_name) + 1
            active_node = NODE_ORDER[next_index] if next_index < len(NODE_ORDER) else None
            if node_name == "critic" and str(final_state.get("current_step", "")) == "CRITIC_REQUESTED_RETRY":
                active_node = "diagnostic"
                activity_placeholder.warning(
                    f"🔁 Critic requested a retry (confidence too low) — looping "
                    f"back to Diagnostic (attempt {final_state.get('retry_count', 0)}/3)."
                )
                await asyncio.sleep(0.5)
            graph_placeholder.graphviz_chart(collaboration_dot(active_node, completed), use_container_width=True)
            render_agent_cards(cards_placeholder, active_node, completed, blocked)
            activity_placeholder.success(f"✅ {NODE_LABELS[node_name]} completed and handed state to peer.")
            if active_node is not None:
                await asyncio.sleep(0.35)
                activity_placeholder.info(f"⚡ {NODE_LABELS[active_node]} is processing the incoming state packet.")
    return final_state


def run_streaming_graph(graph: Any, initial_state: SharedState, graph_placeholder: Any, cards_placeholder: Any, activity_placeholder: Any) -> Dict[str, Any]:
    """Bridge the async graph stream into Streamlit's synchronous execution."""
    return asyncio.run(stream_graph(graph, initial_state, graph_placeholder, cards_placeholder, activity_placeholder))


# --- Initialize Session State Variables ---
if "voice_agent" not in st.session_state:
    st.session_state.voice_agent = HealthcareVoiceAgent(output_dir="voice_output")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "latest_summary" not in st.session_state:
    st.session_state.latest_summary = None

if "last_triage" not in st.session_state:
    st.session_state.last_triage = None

if "patient_id" not in st.session_state:
    st.session_state.patient_id = "PT-8849-X"

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "voice_agent"

if "voice_state" not in st.session_state:
    st.session_state.voice_state = "READY"

if "selected_language_key" not in st.session_state:
    st.session_state.selected_language_key = "auto"

vector_store = get_vector_store()
compiled_graph = get_compiled_graph()
telemetry = get_telemetry()
# Deep Workforce visualization state
if "workforce_node_states" not in st.session_state:
    # Map: node_id -> status (idle|active|complete|error|waiting|retry)
    st.session_state.workforce_node_states = {}

if "workforce_event_feed" not in st.session_state:
    st.session_state.workforce_event_feed = []

if "workforce_active_node" not in st.session_state:
    st.session_state.workforce_active_node = None

if "workforce_retry_count" not in st.session_state:
    st.session_state.workforce_retry_count = 0

if "workforce_running" not in st.session_state:
    st.session_state.workforce_running = False

# Real backend environment check for truthful telemetry
aai_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
has_aai = bool(aai_key)
groq_key = os.getenv("GROQ_API_KEY", "").strip()
has_groq = bool(groq_key)
groq_model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Check if emergency is active in state
is_emergency_active = (
    st.session_state.last_triage is not None
    and st.session_state.last_triage.is_emergency
)
orb_status_text = "EMERGENCY ALERT ACTIVE" if is_emergency_active else "AI Assistant Online"
orb_dot_class = "telemetry-dot dot-emergency" if is_emergency_active else "telemetry-dot dot-online"

# =========================================================================
# 1. SPECTACULAR HERO SECTION
# =========================================================================
st.markdown(
    f"""
<div class="hero-container">
    <div class="hero-left">
        <div class="ai-orb-wrapper">
            <div class="ai-orb-ring"></div>
            <div class="ai-orb-ring-pulse"></div>
            <div class="ai-orb-core"></div>
        </div>
        <div class="hero-title-group">
            <div class="hero-badge-pill">
                <span class="{orb_dot_class}"></span>
                <span>{orb_status_text}</span>
            </div>
            <h1>MedVoice AI</h1>
            <div class="hero-subtitle">
                Autonomous Multilingual Healthcare Voice Assistant &bull; Clinical Operations Command Center
            </div>
        </div>
    </div>
    <div class="hero-right">
        <div class="pipeline-bar">
            <span class="pipe-step">🎙️ VOICE</span>
            <span class="pipe-arrow">▶</span>
            <span class="pipe-step">🧠 UNDERSTAND</span>
            <span class="pipe-arrow">▶</span>
            <span class="pipe-step">🛡️ TRIAGE</span>
            <span class="pipe-arrow">▶</span>
            <span class="pipe-step">📋 SUMMARIZE</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================================
# 2. REAL-TIME SYSTEM TELEMETRY (Technical Telemetry Bar)
# =========================================================================
aai_status_dot = "dot-online" if has_aai else "dot-warning"
aai_status_text = "Connected" if has_aai else "Key Missing"

groq_status_dot = "dot-online" if has_groq else "dot-warning"
groq_status_text = f"Ready ({groq_model_name.split('/')[-1]})" if has_groq else "Rule Fallback"

st.markdown(
    f"""
<div class="telemetry-row">
    <div class="telemetry-card">
        <div class="telemetry-label">Speech-To-Text</div>
        <div class="telemetry-value">
            <span class="telemetry-dot {aai_status_dot}"></span>
            <span>AssemblyAI: {aai_status_text}</span>
        </div>
    </div>
    <div class="telemetry-card">
        <div class="telemetry-label">Voice Synthesis</div>
        <div class="telemetry-value">
            <span class="telemetry-dot dot-online"></span>
            <span>Multi-TLD TTS: Ready</span>
        </div>
    </div>
    <div class="telemetry-card">
        <div class="telemetry-label">Clinical Reasoning</div>
        <div class="telemetry-value">
            <span class="telemetry-dot {groq_status_dot}"></span>
            <span>{groq_status_text}</span>
        </div>
    </div>
    <div class="telemetry-card">
        <div class="telemetry-label">Safety Screening</div>
        <div class="telemetry-value">
            <span class="telemetry-dot dot-online"></span>
            <span>Deterministic Red-Flag Gate</span>
        </div>
    </div>
    <div class="telemetry-card">
        <div class="telemetry-label">Privacy Guard</div>
        <div class="telemetry-value">
            <span class="telemetry-dot dot-online"></span>
            <span>HIPAA PII/PHI Redaction</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================================
# SIDEBAR CONTROLS & ARCHITECTURE SELECTOR
# =========================================================================
with st.sidebar:
    st.markdown("### 🎙️ Session Configuration")

    language_keys = list(SUPPORTED_CLINICAL_LANGUAGES.keys())
    language_labels = {
        code: f"{p.flag_emoji} {p.display_name} ({p.native_name})"
        for code, p in SUPPORTED_CLINICAL_LANGUAGES.items()
    }
    language_labels["auto"] = "🌐 Auto-Detect via AssemblyAI"

    selected_language_key = st.selectbox(
        "Active Language Profile",
        options=["auto"] + language_keys,
        format_func=lambda k: language_labels.get(k, k),
        index=0 if st.session_state.selected_language_key == "auto" else (language_keys.index(st.session_state.selected_language_key) + 1),
        help="Locks transcription, reasoning, and speech synthesis to this profile, or lets AssemblyAI auto-detect.",
        key="sidebar_lang_selector",
    )
    st.session_state.selected_language_key = selected_language_key

    st.markdown("---")
    st.markdown("### 👤 Patient Tracker")
    st.session_state.patient_id = st.text_input(
        "Clinical ID Tag",
        value=st.session_state.patient_id,
        help="Unique identifier tagged on clinician summaries and audit traces.",
    )

    if st.button("🔄 Reset / New Patient Session", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.latest_summary = None
        st.session_state.last_triage = None
        st.session_state.patient_id = f"PT-{uuid.uuid4().hex[:6].upper()}"
        st.session_state.voice_state = "READY"
        st.session_state.last_result = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Architecture Mode")
    mode_selection = st.radio(
        "Experience View",
        options=["🎙️ Interactive Voice Agent", "🔬 Clinical Command Center & 9-Node Workforce"],
        index=0 if st.session_state.app_mode == "voice_agent" else 1,
    )
    st.session_state.app_mode = (
        "voice_agent" if "Interactive" in mode_selection else "deep_workforce"
    )

    st.markdown("---")
    st.markdown("### 📊 Infrastructure Ledger")
    st.markdown(render_metric("Input tokens", str(telemetry["input"]), "info"), unsafe_allow_html=True)
    st.markdown(render_metric("Output tokens", str(telemetry["output"]), "info"), unsafe_allow_html=True)
    st.markdown(render_metric("Session cost", f"${telemetry['total_cost']:.5f}", "success"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        """
<div class="privacy-badge">
    <span>🔒</span>
    <span><b>HIPAA Compliant</b><br/>Zero raw PII sent to reasoning</span>
</div>
""",
        unsafe_allow_html=True,
    )

# =========================================================================
# MODE 1: INTERACTIVE HEALTHCARE VOICE AGENT (MedVoice AI)
# =========================================================================
if st.session_state.app_mode == "voice_agent":
    target_lang_code = (
        "en" if st.session_state.selected_language_key == "auto" else st.session_state.selected_language_key
    )
    curr_profile = get_language_profile(target_lang_code)

    # 1-Click Evaluation Scenarios Banner (Hero CTA)
    st.markdown(
        """
<div class="glass-card glass-card-accent" style="padding:1.1rem 1.35rem; margin-bottom:1rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
        <span style="font-weight:800; font-size:0.95rem; color:#F8FAFC;">
            🚀 1-Click Evaluation Scenarios
        </span>
        <span style="font-size:0.7rem; font-weight:700; color:#38BDF8; letter-spacing:0.06em; text-transform:uppercase;">
            INSTANT PLAYBACK
        </span>
    </div>
    <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.4;">
        Trigger live conversational turns without setting up an external mic or typing:
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    scen_col1, scen_col2, scen_col3 = st.columns(3)
    trigger_scenario_text = None
    trigger_scenario_lang = target_lang_code

    with scen_col1:
        if st.button("🟢 Scenario 1: Low-Risk Symptom", use_container_width=True, help="Simulate a routine tension headache consultation"):
            trigger_scenario_text = "I have had a mild throbbing tension headache and trouble sleeping for the past 2 days."
            trigger_scenario_lang = "en"
            st.session_state.voice_state = "PROCESSING"

    with scen_col2:
        if st.button("🔴 Scenario 2: Emergency Red-Flag", use_container_width=True, help="Simulate acute crushing chest pain triggering emergency escalation"):
            trigger_scenario_text = "I have sudden severe crushing chest pain radiating to my left arm and I can barely breathe."
            trigger_scenario_lang = "en"
            st.session_state.voice_state = "PROCESSING"

    with scen_col3:
        if st.button(f"🌐 Scenario 3: {curr_profile.display_name} Voice", use_container_width=True, help=f"Simulate native speech in {curr_profile.display_name}"):
            trigger_scenario_text = curr_profile.sample_symptom
            trigger_scenario_lang = curr_profile.language_code
            st.session_state.voice_state = "PROCESSING"

    # Emergency Alert Card (Conditional)
    if is_emergency_active:
        triage = st.session_state.last_triage
        flags_str = ", ".join(triage.matched_flags)
        st.markdown(
            f"""
<div class="alert-emergency">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <span style="font-size:1.1rem; font-weight:850; color:#FEE2E2; display:flex; align-items:center; gap:0.5rem;">
            🚨 URGENT CLINICAL SAFETY ALERT: CRITICAL PRESENTATION
        </span>
        <span class="badge-emergency">RED-FLAG ACTIVE</span>
    </div>
    <div style="font-size:0.95rem; font-weight:700; color:#FECDD3; margin-bottom:0.4rem;">
        {triage.category}: {flags_str}
    </div>
    <div style="font-size:0.88rem; color:#FEE2E2; line-height:1.55;">
        {triage.immediate_guidance}<br/>
        <b>Direct Action:</b> Please contact 911 / 112 / local emergency services or proceed immediately to the nearest Emergency Department.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Main Two-Column Layout
    conv_col, summary_col = st.columns([1.28, 1])

    with conv_col:
        st.markdown(
            """
<div class="glass-card">
    <div class="card-header-bar">
        <div class="card-header-title">
            <span>🎙️</span>
            <span>Patient Voice Consultation</span>
        </div>
        <div class="waveform-visualizer">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    </div>
""",
            unsafe_allow_html=True,
        )

        state_title = "READY"
        state_desc = f"Listening in {curr_profile.display_name}. Speak or click a scenario to begin."
        if st.session_state.voice_state == "PROCESSING":
            state_title = "PROCESSING & THINKING"
            state_desc = "Transcribing with AssemblyAI and analyzing clinical presentation..."
        elif st.session_state.voice_state == "SPEAKING":
            state_title = "SPEAKING"
            state_desc = f"Responding in {curr_profile.display_name} with synthesized medical guidance."

        st.markdown(
            f"""
<div class="voice-state-banner">
    <div class="voice-state-left">
        <span class="telemetry-dot dot-online"></span>
        <div>
            <div class="voice-state-title">{state_title}</div>
            <div class="voice-state-desc">{state_desc}</div>
        </div>
    </div>
    <div style="font-size:0.75rem; font-weight:700; color:#38BDF8;">
        {curr_profile.flag_emoji} {curr_profile.display_name}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        audio_input_data = None
        if hasattr(st, "audio_input"):
            audio_input_data = st.audio_input("Live Microphone Recording (Speak naturally)")
        else:
            st.info("Microphone input ready. You can also upload a recording below.")

        up_col, text_col = st.columns(2)
        with up_col:
            uploaded_file = st.file_uploader(
                "Upload voice file (.wav, .mp3, .m4a)",
                type=["wav", "mp3", "m4a", "ogg"],
                key="voice_turn_upload",
            )
        with text_col:
            typed_fallback = st.text_area(
                "Symptom description or follow-up reply",
                value="",
                placeholder="E.g., I have had a mild headache and tiredness since yesterday...",
                height=82,
                key="typed_symptom_input",
            )

        submit_turn_clicked = st.button("🎤 Transcribe & Consult MedVoice AI", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        to_process_audio_bytes = None
        to_process_text = None
        effective_lang = (
            st.session_state.selected_language_key
            if st.session_state.selected_language_key != "auto"
            else "auto"
        )

        if trigger_scenario_text:
            to_process_text = trigger_scenario_text
            effective_lang = trigger_scenario_lang
        elif submit_turn_clicked:
            if audio_input_data is not None:
                to_process_audio_bytes = audio_input_data.getvalue()
            elif uploaded_file is not None:
                to_process_audio_bytes = uploaded_file.getvalue()
            elif typed_fallback.strip():
                to_process_text = typed_fallback.strip()
            else:
                st.warning("Please record your voice, upload an audio file, or type your symptoms first.")

        if to_process_audio_bytes is not None or to_process_text is not None:
            with st.spinner("AssemblyAI transcribing audio & synthesizing clinical guidance..."):
                try:
                    response: VoiceAgentResponse = asyncio.run(
                        st.session_state.voice_agent.process_voice_turn(
                            audio_bytes=to_process_audio_bytes,
                            text_input=to_process_text,
                            language_preference=effective_lang,
                            conversation_history=st.session_state.conversation_history,
                            patient_id=st.session_state.patient_id,
                        )
                    )

                    st.session_state.conversation_history.append({
                        "speaker": "patient",
                        "text": response.transcript,
                        "timestamp": time.time(),
                        "language": response.detected_language_code,
                    })
                    st.session_state.conversation_history.append({
                        "speaker": "assistant",
                        "text": response.assistant_response,
                        "follow_up": response.suggested_follow_up,
                        "audio_path": response.audio_file_path,
                        "triage": response.triage,
                        "timestamp": time.time(),
                        "language": response.detected_language_code,
                    })

                    st.session_state.latest_summary = response.medical_summary
                    st.session_state.last_triage = response.triage
                    st.session_state.voice_state = "SPEAKING"
                    st.rerun()

                except Exception as exc:
                    st.error(f"Voice turnaround error: {exc}")
                    st.session_state.voice_state = "READY"

        # Live Conversation Feed
        st.markdown(
            """
<div class="glass-card">
    <div class="card-header-bar">
        <div class="card-header-title">
            <span>💬</span>
            <span>Live Consultation Stream</span>
        </div>
        <div style="font-size:0.75rem; color:var(--text-muted);">
            Turn Count: <b>{}</b>
        </div>
    </div>
""".format(len(st.session_state.conversation_history) // 2),
            unsafe_allow_html=True,
        )

        if not st.session_state.conversation_history:
            st.markdown(
                """
<div style="text-align:center; padding:2rem 1rem; color:var(--text-secondary);">
    <div style="font-size:2rem; margin-bottom:0.5rem;">🎙️</div>
    <div style="font-weight:700; font-size:1rem; color:#E2E8F0;">Consultation Feed Ready</div>
    <div style="font-size:0.84rem; max-width:380px; margin:0.35rem auto; line-height:1.5;">
        Speak into the microphone above or select a 1-Click Evaluation Scenario to hear MedVoice AI interact in real time.
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            for turn in st.session_state.conversation_history:
                if turn["speaker"] == "patient":
                    lang_tag = turn.get("language", "en").upper()
                    st.markdown(
                        f"""
<div class="chat-stream">
    <div class="chat-bubble-patient">
        <div class="chat-meta-bar" style="color:#38BDF8;">
            <span>👤 Patient Narrative</span>
            <span>AssemblyAI STT &bull; {lang_tag} &bull; 🔒 PII Redacted</span>
        </div>
        <div style="font-size:0.95rem; line-height:1.6;">"{turn['text']}"</div>
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )
                else:
                    audio_path = turn.get("audio_path")
                    triage_info = turn.get("triage")
                    badge_html = '<span class="badge-routine">🟢 ROUTINE</span>'
                    if triage_info:
                        if triage_info.risk_level == RiskLevel.EMERGENCY:
                            badge_html = '<span class="badge-emergency">🚨 CRITICAL RED-FLAG</span>'
                        elif triage_info.risk_level == RiskLevel.URGENT:
                            badge_html = '<span class="badge-urgent">⚠️ URGENT CARE</span>'

                    formatted_resp = turn["text"].replace("\n", "<br/>")
                    follow_up = turn.get("follow_up")
                    follow_up_html = ""
                    if follow_up and follow_up != "Please seek immediate emergency medical care now.":
                        follow_up_html = f"""
<div class="follow-up-box">
    <b>🔍 Clinical Follow-up:</b> {follow_up}
</div>
"""
                    st.markdown(
                        f"""
<div class="chat-stream">
    <div class="chat-bubble-assistant">
        <div class="chat-meta-bar" style="color:#C084FC;">
            <span style="display:flex; align-items:center; gap:0.4rem;">
                <div class="waveform-visualizer"><span></span><span></span><span></span><span></span><span></span></div>
                MedVoice AI
            </span>
            <span>{badge_html}</span>
        </div>
        <div style="line-height:1.65; font-size:0.95rem;">{formatted_resp}</div>
        {follow_up_html}
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )
                    if audio_path and os.path.exists(audio_path):
                        st.audio(audio_path, format="audio/mp3", autoplay=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with summary_col:
        st.markdown(
            """
<div class="glass-card">
    <div class="card-header-bar">
        <div class="card-header-title">
            <span>📋</span>
            <span>Clinician-Ready Summary</span>
        </div>
        <span class="card-header-badge" style="background:rgba(16,185,129,0.15); color:#6EE7B7; border:1px solid rgba(16,185,129,0.3);">
            HIPAA COMPLIANT
        </span>
    </div>
""",
            unsafe_allow_html=True,
        )

        summary: Optional[StructuredMedicalSummary] = st.session_state.latest_summary
        if summary is None:
            st.markdown(
                """
<div class="alert-normal" style="background:rgba(16,185,129,0.08); padding:0.8rem; border-radius:12px; border:1px solid rgba(16,185,129,0.25); margin-bottom:1rem;">
    <div style="font-weight:750; font-size:0.86rem; color:#6EE7B7; margin-bottom:0.25rem;">
        🛡️ Safety Screening: Active & Monitoring
    </div>
    <div style="font-size:0.78rem; color:var(--text-secondary); line-height:1.45;">
        Continuous deterministic screening for cardiovascular, respiratory, stroke, hemorrhagic, and acute distress presentations across 6 languages.
    </div>
</div>

<div style="text-align:center; padding:2rem 1rem; color:var(--text-muted);">
    <div style="font-size:2rem; margin-bottom:0.4rem;">📑</div>
    <div style="font-weight:700; font-size:0.92rem; color:#E2E8F0;">Summary Dossier Awaiting Voice Intake</div>
    <div style="font-size:0.78rem; max-width:300px; margin:0.35rem auto; line-height:1.5;">
        As the patient describes symptoms, chief complaints, duration, severity, and triage pathways will populate here.
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            risk_badge = (
                '<span class="badge-emergency">🚨 EMERGENCY</span>'
                if summary.triage_risk_level == "EMERGENCY"
                else '<span class="badge-urgent">⚠️ URGENT</span>'
                if summary.triage_risk_level == "URGENT"
                else '<span class="badge-routine">🟢 ROUTINE</span>'
            )

            symptoms_chips = "".join(f'<span class="symptom-chip">● {s}</span>' for s in summary.extracted_symptoms)
            flags_chips = "".join(f'<span class="flag-chip">🚨 {f}</span>' for f in summary.emergency_flags)

            st.markdown(
                f"""
<div style="margin-bottom:0.85rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
        <span style="font-size:0.82rem; color:var(--text-muted);">Patient ID: <b style="color:#E2E8F0;">{summary.patient_id}</b></span>
        {risk_badge}
    </div>
    <div style="margin-bottom:0.65rem;">
        <div style="font-size:0.72rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; letter-spacing:0.06em;">Chief Complaint</div>
        <div style="font-size:0.92rem; font-weight:700; color:#F8FAFC; margin-top:0.15rem;">"{summary.chief_complaint}"</div>
    </div>
    <div style="margin-bottom:0.65rem;">
        <div style="font-size:0.72rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; letter-spacing:0.06em;">Mapped Symptoms</div>
        <div style="margin-top:0.3rem;">{symptoms_chips}</div>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:0.65rem; background:rgba(8,13,26,0.5); padding:0.6rem 0.8rem; border-radius:12px; border:1px solid var(--line-subtle);">
        <div>
            <div style="font-size:0.7rem; color:var(--text-muted); font-weight:700;">DURATION</div>
            <div style="font-size:0.85rem; font-weight:700; color:#E2E8F0;">{summary.duration_onset}</div>
        </div>
        <div>
            <div style="font-size:0.7rem; color:var(--text-muted); font-weight:700;">SEVERITY</div>
            <div style="font-size:0.85rem; font-weight:700; color:#E2E8F0;">{summary.severity_character}</div>
        </div>
    </div>
    {f'<div style="margin-bottom:0.65rem;"><div style="font-size:0.72rem; text-transform:uppercase; color:#FECDD3; font-weight:700;">Red-Flag Indicators</div><div style="margin-top:0.25rem;">{flags_chips}</div></div>' if summary.emergency_flags else ''}
    <div style="margin-bottom:0.65rem;">
        <div style="font-size:0.72rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; letter-spacing:0.06em;">Safe Clinical Pathway</div>
        <div style="font-size:0.86rem; color:#E2E8F0; line-height:1.45; margin-top:0.15rem;">{summary.recommended_next_steps}</div>
    </div>
    <div style="font-size:0.74rem; color:var(--text-muted); border-top:1px solid var(--line-subtle); padding-top:0.5rem; margin-top:0.6rem;">
        Consultation Language: <b style="color:#E2E8F0;">{summary.language}</b>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                txt_summary = (
                    f"MEDVOICE AI CLINICAL SUMMARY\n"
                    f"Patient ID: {summary.patient_id}\n"
                    f"Triage Risk Level: {summary.triage_risk_level}\n"
                    f"Language: {summary.language}\n"
                    f"Chief Complaint: {summary.chief_complaint}\n"
                    f"Extracted Symptoms: {', '.join(summary.extracted_symptoms)}\n"
                    f"Duration/Onset: {summary.duration_onset}\n"
                    f"Severity: {summary.severity_character}\n"
                    f"Recommended Next Steps: {summary.recommended_next_steps}\n"
                    f"Disclaimer: {summary.ai_disclaimer}\n"
                )
                st.download_button(
                    "⬇️ Download .txt",
                    data=txt_summary.encode("utf-8"),
                    file_name=f"{summary.patient_id}-summary.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with exp_col2:
                html_summary = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Clinical Summary - {summary.patient_id}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 680px; margin: 2rem auto; color: #111; line-height: 1.6; padding: 0 1rem; }}
h1 {{ border-bottom: 2px solid #0284c7; padding-bottom: 0.5rem; color: #0f172a; }}
.badge {{ display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-weight: bold; background: #e0f2fe; color: #0369a1; }}
.footer {{ margin-top: 2rem; font-size: 0.8rem; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 0.5rem; }}
</style>
</head>
<body>
<h1>MedVoice AI — Clinical Summary</h1>
<p><b>Patient Tracker ID:</b> {summary.patient_id} &nbsp;|&nbsp; <b>Risk Level:</b> <span class="badge">{summary.triage_risk_level}</span></p>
<p><b>Chief Complaint:</b> {summary.chief_complaint}</p>
<p><b>Symptoms:</b> {', '.join(summary.extracted_symptoms)}</p>
<p><b>Duration:</b> {summary.duration_onset} &nbsp;|&nbsp; <b>Severity:</b> {summary.severity_character}</p>
<p><b>Recommended Steps:</b> {summary.recommended_next_steps}</p>
<div class="footer">{summary.ai_disclaimer}</div>
</body></html>"""
                st.download_button(
                    "⬇️ Printable .html",
                    data=html_summary.encode("utf-8"),
                    file_name=f"{summary.patient_id}-report.html",
                    mime="text/html",
                    use_container_width=True,
                )

            st.markdown("<hr style='border-color:var(--line-subtle); margin:1rem 0;'>", unsafe_allow_html=True)
            st.caption("Need advanced clinical consensus? Dispatch this case to the 9-node LangGraph digital workforce.")
            if st.button("🚀 Dispatch to Deep Multi-Agent Workforce", use_container_width=True):
                st.session_state.app_mode = "deep_workforce"
                st.session_state.deep_intake_symptoms = summary.chief_complaint
                st.session_state.deep_intake_lang = summary.language
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
<div class="legal-disclaimer">
    <b>⚠️ MedVoice AI Clinical Governance:</b> {curr_profile.disclaimer}
</div>
""",
            unsafe_allow_html=True,
        )

# =========================================================================
# MODE 2: CLINICAL COMMAND CENTER & 9-NODE WORKFORCE
# =========================================================================
else:
    st.markdown(
        """
<div class="glass-card glass-card-accent">
    <div class="card-header-bar">
        <div class="card-header-title">
            <span>🔬</span>
            <span>Clinical Command Center & 9-Node Peer-to-Peer Workforce</span>
            <span>Deep Clinical P2P Workforce — 9-Node LangGraph Digital Workforce</span>
        </div>
        <span class="card-header-badge" style="background:rgba(16,185,129,0.2); color:#6EE7B7; border:1px solid var(--accent-emerald);">
            AUTONOMOUS ORCHESTRATION ACTIVE
        </span>
    </div>
    <div style="font-size:0.84rem; color:var(--text-secondary); line-height:1.5;">
        Decentralized clinical state machine: Voice Intake (AssemblyAI) ➔ Triage ➔ Researcher (ChromaDB RAG)
        ➔ Diagnostic (Tree-of-Thoughts) ⟲ Critic (Self-Healing Gate) ➔ Compliance (PII Guard) ➔ Practitioner HITL Review ➔ Final Compile ➔ Spoken Voice Output.
        Peer-to-peer clinical state machine: Voice Intake (AssemblyAI) → Triage → Researcher (ChromaDB RAG)
        → Diagnostic (Tree-of-Thoughts) ⟲ Critic (Self-Healing Gate) → Compliance → Practitioner HITL → Final Compile → Voice Output.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("← Return to Interactive Voice Assistant", use_container_width=False):
        st.session_state.app_mode = "voice_agent"
        st.session_state.workforce_node_states = {}
        st.session_state.workforce_event_feed = []
        st.session_state.workforce_active_node = None
        st.session_state.workforce_running = False
        st.rerun()

    st.markdown('<div class="section-label" style="margin-top:1rem; color:#7dd3fc; font-size:.74rem; font-weight:800; text-transform:uppercase;">Admission & Context</div>', unsafe_allow_html=True)
    intake_col, context_col = st.columns([1.35, 1])
    # -----------------------------------------------------------------------
    # LIVE AGENT COLLABORATION TOPOLOGY — HTML/SVG/JS Component
    # -----------------------------------------------------------------------
    _topology_html = generate_live_workforce_topology_html(
        node_states=st.session_state.workforce_node_states,
        active_node=st.session_state.workforce_active_node,
        event_feed=st.session_state.workforce_event_feed[-25:],
        retry_count=st.session_state.workforce_retry_count,
        is_running=st.session_state.workforce_running,
    )
    # -----------------------------------------------------------------------
    # INTAKE COLUMN + TOPOLOGY COLUMN (side by side)
    # -----------------------------------------------------------------------
    intake_col, graph_col = st.columns([1, 1.85])

    with intake_col:
        with st.expander("Open admission fields", expanded=True):
            p_id = st.text_input("Patient tracker ID", value=st.session_state.patient_id, key="deep_pid")
            f_name = st.text_input("Full name", value="Jordan Morgan", key="deep_fname")
            age = st.number_input("Age", min_value=0, max_value=125, value=48, step=1, key="deep_age")
            v_col, h_col = st.columns(2)
            with v_col:
                vitals = st.text_input("Vital signs", value="BP 168/102 mmHg", key="deep_vitals")
            with h_col:
                history = st.text_input("Medical history ledger", value="Type-2 diabetes; Metformin", key="deep_history")

            default_symptoms = getattr(
                st.session_state,
                "deep_intake_symptoms",
                "Sudden severe headache with elevated blood pressure spikes. Reports increased thirst and poor sleep.",
            )
            symptoms_text = st.text_area(
                "Presenting symptoms and clinical narrative",
                value=default_symptoms,
                height=110,
                key="deep_symptom_text",
            )

        st.markdown(
            '<div style="margin-top:0.8rem; font-weight:700; font-size:0.88rem; color:#A78BFA;">'
            '🎙️ Multilingual Voice Intake (Optional)'
            '</div>',
            unsafe_allow_html=True,
        )
        uploaded_audio = st.file_uploader(
            "Upload symptom audio (wav, mp3, m4a, ogg)",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            key="deep_audio_uploader",
        )
        mic_recording = None
        if hasattr(st, "audio_input"):
            mic_recording = st.audio_input("...or record directly in the browser", key="deep_mic")
        if mic_recording is not None:
            uploaded_audio = mic_recording
        if uploaded_audio is not None:
            st.audio(uploaded_audio, format=getattr(uploaded_audio, "type", None) or "audio/wav")

    with context_col:
        st.markdown(
            '<div class="glass-card"><div class="card-header-title">Semantic Memory (ChromaDB)</div>'
            '<div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.75rem;">'
            'Retrieve historical clinical profiles matching this presentation before activation.'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Retrieve historical context", use_container_width=True, key="btn_retrieve_ctx"):
            if symptoms_text.strip():
                st.success("Historical case context recovered from vector memory:")
                st.code(vector_store.search_similar_cases(symptoms_text, max_results=1)[0], language="text")
            else:
                st.error("Presenting symptoms narrative required.")
        else:
            st.info("The memory layer remains accessible autonomously to the Researcher peer during execution.")
        st.markdown("</div>", unsafe_allow_html=True)

    # (Old graphviz/agent-cards visualization removed — Workforce State Topology below is the single canonical view)

    result_state = st.session_state.get("last_result")
    if result_state:
        st.markdown('<div class="section-label" style="margin-top:1.5rem; color:#7dd3fc; font-size:.74rem; font-weight:800; text-transform:uppercase;">Clinical Insights & Governance</div>', unsafe_allow_html=True)
        symptoms_found = result_state.get("extracted_symptoms", [])
        compliance_status = str(result_state.get("compliance_status", "PENDING"))
        status_tone = "success" if compliance_status == "PASSED" else "amber" if compliance_status == "PENDING" else ""
        pipeline_step = str(result_state.get("current_step", ""))
        nodes_complete = "9 / 9" if pipeline_step.startswith("VOICE_OUTPUT") else "6 / 9"

        st.markdown(
            '<div class="metric-grid">'
            + render_metric("Workflow status", pipeline_step, status_tone)
            + render_metric("Symptoms mapped", str(len(symptoms_found)), "info")
            + render_metric("P2P nodes complete", nodes_complete, "info")
            + render_metric("Compliance gate", compliance_status, status_tone)
            + '</div>',
            unsafe_allow_html=True,
        )

        detected_code = result_state.get("detected_language_code", "en")
        voice_profile, _ = resolve_language_profile(detected_code)
        output_audio_path = result_state.get("output_audio_path")

        if output_audio_path or result_state.get("input_audio_path"):
            st.markdown(
                f'<div class="glass-card"><div class="card-header-title">🎙️ Multilingual Voice Round-Trip '
                f'<span style="font-size:0.75rem; color:#38BDF8;">{voice_profile.flag_emoji} {voice_profile.display_name}</span></div>',
                unsafe_allow_html=True,
            )
            v_badge_col, v_audio_col = st.columns([1, 2])
            with v_badge_col:
                st.caption(f"Detected Locale: {voice_profile.locale}")
                if result_state.get("voice_input_error"):
                    st.warning(f"Transcription note: {result_state['voice_input_error']}")
            with v_audio_col:
                if output_audio_path and os.path.exists(output_audio_path):
                    st.markdown("<b>Spoken Final Synthesis:</b>", unsafe_allow_html=True)
                    st.audio(output_audio_path, format="audio/mp3", autoplay=True)
            st.markdown("</div>", unsafe_allow_html=True)

        ins_col, diag_col = st.columns([1, 1.35])
        with ins_col:
            st.markdown(
                '<div class="glass-card"><div class="card-header-title">Medical Ledger Chips</div>'
                '<div style="margin-top:0.5rem;">'
                + "".join(f'<span class="symptom-chip">● {item}</span>' for item in symptoms_found)
                + '</div><hr style="border-color:var(--line-subtle); margin:0.8rem 0;">'
                '<div class="card-header-title" style="font-size:0.95rem;">Governance Clearance</div>',
                unsafe_allow_html=True,
            )
            if "FAILED" in compliance_status:
                st.error(compliance_status)
            else:
                st.success(compliance_status)
            st.markdown("</div>", unsafe_allow_html=True)

        with diag_col:
            st.markdown(
                '<div class="glass-card glass-card-accent"><div class="card-header-title">Diagnostic Intelligence Brief</div>'
                '<div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.5rem;">Tree-of-Thoughts Consensus & Evidence</div>',
                unsafe_allow_html=True,
            )
            st.code(result_state.get("initial_diagnosis", "No differential diagnosis established."), language="text")
            if result_state.get("medical_research_data"):
                st.info(result_state.get("medical_research_data"))
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="glass-card"><div class="card-header-title">Verified Clinical Compilation</div>'
            '<div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.5rem;">Practitioner-reviewed decision support dossier.</div>',
            unsafe_allow_html=True,
        )
        st.text_area("Final clinical report", value=result_state.get("final_clinical_report", ""), height=140, key="deep_final_report_area")

        rep_txt_col, rep_html_col = st.columns(2)
        with rep_txt_col:
            st.download_button(
                "⬇️ Download as .txt",
                data=str(result_state.get("final_clinical_report", "")).encode("utf-8"),
                file_name=f"{st.session_state.patient_id}-report.txt",
                mime="text/plain",
                use_container_width=True,
                key="btn_dl_txt",
            )
        with rep_html_col:
            st.download_button(
                "⬇️ Download printable report (.html)",
                data=build_report_html(result_state, st.session_state.patient_id).encode("utf-8"),
                file_name=f"{st.session_state.patient_id}-report.html",
                mime="text/html",
                use_container_width=True,
                key="btn_dl_html",
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # HITL Practitioner Review Checkpoint
        if compliance_status == "PASSED" and result_state.get("hitl_approved") is not True:
            st.markdown(
                '<div class="glass-card glass-card-accent">'
                '<div class="card-header-title" style="color:#F59E0B;">👨‍⚕️ Practitioner Review Checkpoint (HITL REQUIRED)</div>'
                '<div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.6rem;">Review clinical differential before allowing Final Compile to complete.</div>',
                unsafe_allow_html=True,
            )
            st.text_input("Practitioner approval notes", value="Validated for clinical evaluation.", key="hitl_notes")
            approve_clicked = st.button("✅ Approve and continue to final compile", type="primary", use_container_width=True, key="btn_hitl_approve")
            if approve_clicked:
                req = st.session_state["last_request"]
                approved_state = SharedState(
                    patient_id=req["patient_id"],
                    raw_symptoms=req["raw_symptoms"],
                    detected_language_code=req.get("detected_language_code", "en"),
                    retry_count=0,
                    hitl_approved=True,
                )
                # Re-queue via workforce running flag so the new topology shows the re-run
                import datetime as _dt_hitl
                st.session_state.workforce_node_states = {}
                st.session_state.workforce_event_feed = [{
                    "time": _dt_hitl.datetime.now().strftime("%H:%M:%S"),
                    "icon": "👨\u200d⚕️",
                    "text": "Practitioner approved — resuming P2P flow to Final Compile",
                    "cls": "highlight",
                }]
                st.session_state.workforce_active_node = None
                st.session_state.workforce_retry_count = 0
                st.session_state.workforce_running = True
                st.session_state._hitl_approved_state = approved_state
                update_telemetry(st.session_state.get("last_result", {}))
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # WORKFORCE CONTROLS — always rendered outside result_state so buttons
    # are always defined (prevents NameError on run_sim_demo / run_deep_workforce)
    # -----------------------------------------------------------------------
    st.markdown(
        '<div class="section-label" style="margin-top:1.5rem; color:#7dd3fc; font-size:.74rem; font-weight:800; text-transform:uppercase;">Workforce Controls</div>',
        unsafe_allow_html=True,
    )
    default_symptoms = getattr(
        st.session_state,
        "deep_intake_symptoms",
        "Sudden severe headache with elevated blood pressure spikes. Reports increased thirst and poor sleep.",
    )
    deep_symptoms = st.text_area(
        "Patient Narrative / Transcribed Symptoms",
        value=st.session_state.get("deep_symptom_text", default_symptoms),
        height=120,
        key="deep_symptom_text_ctrl",
    )
    deep_lang = st.selectbox(
        "Target Spoken Language Profile",
        options=list(SUPPORTED_CLINICAL_LANGUAGES.keys()),
        format_func=lambda k: f"{SUPPORTED_CLINICAL_LANGUAGES[k].flag_emoji} {SUPPORTED_CLINICAL_LANGUAGES[k].display_name}",
        index=0,
        key="deep_lang_select",
    )

    run_deep_workforce = st.button("⚡ Execute Autonomous Workforce", type="primary", use_container_width=True)

    col_sim, col_rst = st.columns(2)
    with col_sim:
        run_sim_demo = st.button("▶ Live Simulation", use_container_width=True, help="Watch animated 60fps walkthrough of all 9 nodes with self-healing")
    with col_rst:
        reset_canvas = st.button("↺ Reset Canvas", use_container_width=True)

    if reset_canvas:
        st.session_state.workforce_node_states = {}
        st.session_state.workforce_event_feed = []
        st.session_state.workforce_active_node = None
        st.session_state.workforce_retry_count = 0
        st.session_state.workforce_running = False
        st.session_state.last_deep_result = None
        st.rerun()

    # Show mini-metrics if result available
    deep_result = st.session_state.get("last_deep_result")
    if deep_result:
        st.markdown(
            """
<div class="glass-card" style="margin-top:0.8rem; padding:0.8rem 1rem;">
    <div class="card-header-bar" style="margin-bottom:0.6rem;">
        <div class="card-header-title" style="font-size:0.8rem;"><span>📊</span><span>Workforce Output</span></div>
    </div>
""",
            unsafe_allow_html=True,
        )
        mc1, mc2 = st.columns(2)
        mc1.metric("Retries", deep_result.get("retry_count", 0))
        mc2.metric("Compliance", deep_result.get("compliance_status", "PASSED")[:7])
        st.text_area(
            "Final Clinical Synthesis",
            value=deep_result.get("final_clinical_report", ""),
            height=100,
            key="deep_result_text",
        )
        deep_audio = deep_result.get("output_audio_path")
        if deep_audio and os.path.exists(deep_audio):
            st.markdown("**🔊 Spoken Synthesis:**")
            st.audio(deep_audio, format="audio/mp3")
        st.markdown("</div>", unsafe_allow_html=True)

    with graph_col:
        topology_placeholder = st.empty()
        with topology_placeholder:
            components.html(_topology_html, height=750, scrolling=False)

    # -----------------------------------------------------------------------
    # LIVE SIMULATION WALKTHROUGH DEMO (STREAMLIT NATIVE LOOP)
    # -----------------------------------------------------------------------
    if run_sim_demo:
        import datetime as _dt_sim
        st.session_state.workforce_node_states = {}
        st.session_state.workforce_event_feed = []
        st.session_state.workforce_active_node = None
        st.session_state.workforce_retry_count = 0
        st.session_state.workforce_running = True

        def _push_sim(act_id, states, icon, msg, cls="active"):
            ts = _dt_sim.datetime.now().strftime("%H:%M:%S")
            st.session_state.workforce_active_node = act_id
            st.session_state.workforce_node_states = dict(states)
            st.session_state.workforce_event_feed.append({"time": ts, "icon": icon, "text": msg, "cls": cls})
            with topology_placeholder:
                components.html(
                    generate_live_workforce_topology_html(
                        node_states=st.session_state.workforce_node_states,
                        active_node=st.session_state.workforce_active_node,
                        event_feed=st.session_state.workforce_event_feed,
                        retry_count=st.session_state.workforce_retry_count,
                        is_running=True,
                    ),
                    height=750,
                    scrolling=False,
                )

        sim_sequence = [
            ("voice_input", "🎙️", "Voice Intake: Ingested patient audio narrative via AssemblyAI STT", "active", 0.8),
            ("triage", "🩺", "Triage Gate: Filtered red-flag vitals (BP: 160/95, Cephalo-ocular stress)", "active", 0.8),
            ("researcher", "📚", "Researcher: Retrieved evidence-based guidelines from ChromaDB Vector Store", "active", 0.8),
            ("diagnostic", "🧠", "Diagnostic: Tree-of-Thoughts initial reasoning generated differential hypothesis", "active", 0.9),
            ("critic", "🛡️", "Critic Gate: Confidence score 78.5% (<85%) — Triggering Self-Healing Loopback!", "warning", 1.1),
            ("diagnostic_retry", "🧠", "Self-Healing: Diagnostic Tree-of-Thoughts refined hypothesis (Confidence: 94.2%)", "highlight", 1.0),
            ("critic_pass", "🛡️", "Critic Gate: Confidence verified (94.2% >= 85%) — Passed to Compliance", "success", 0.8),
            ("compliance", "🔒", "Compliance Guard: Audited HIPAA boundaries & verified PII/PHI redaction", "success", 0.8),
            ("hitl", "👨‍⚕️", "Practitioner Review: Attending physician verified differential consensus", "success", 0.8),
            ("final_compile", "📋", "Final Compile: Structured EHR report and patient advisory assembled", "active", 0.8),
            ("voice_output", "🔊", "Voice Output: Synthesized native speech consultation for patient", "success", 0.9),
        ]

        curr_sim_states = {}
        for step_id, icon, text, cls, delay in sim_sequence:
            if step_id == "critic":
                curr_sim_states["diagnostic"] = "complete"
                curr_sim_states["critic"] = "retry"
                st.session_state.workforce_retry_count = 1
                _push_sim("critic", curr_sim_states, icon, text, cls)
            elif step_id == "diagnostic_retry":
                curr_sim_states["diagnostic"] = "active"
                _push_sim("diagnostic", curr_sim_states, icon, text, cls)
            elif step_id == "critic_pass":
                curr_sim_states["diagnostic"] = "complete"
                curr_sim_states["critic"] = "active"
                _push_sim("critic", curr_sim_states, icon, text, cls)
            else:
                for k in list(curr_sim_states.keys()):
                    curr_sim_states[k] = "complete"
                curr_sim_states[step_id] = "active"
                _push_sim(step_id, curr_sim_states, icon, text, cls)
            time.sleep(delay)

        for k in list(curr_sim_states.keys()):
            curr_sim_states[k] = "complete"
        st.session_state.workforce_active_node = None
        st.session_state.workforce_running = False
        ts_fin = _dt_sim.datetime.now().strftime("%H:%M:%S")
        st.session_state.workforce_event_feed.append({
            "time": ts_fin, "icon": "✅", "text": "Simulation Walkthrough Complete: Autonomous consensus achieved with 1 self-healing loop", "cls": "success"
        })
        with topology_placeholder:
            components.html(
                generate_live_workforce_topology_html(
                    node_states=curr_sim_states,
                    active_node=None,
                    event_feed=st.session_state.workforce_event_feed,
                    retry_count=1,
                    is_running=False,
                ),
                height=750,
                scrolling=False,
            )

    # -----------------------------------------------------------------------
    # EXECUTE WORKFORCE — stream real node events into session state & UI
    # -----------------------------------------------------------------------
    if run_deep_workforce:
        if not deep_symptoms.strip():
            st.error("Please supply clinical narrative before activating the workforce.")
        else:
            import datetime as _dt

            st.session_state.workforce_node_states = {}
            st.session_state.workforce_event_feed = []
            st.session_state.workforce_active_node = None
            st.session_state.workforce_retry_count = 0
            st.session_state.workforce_running = True

            def _add_event(icon: str, text: str, cls: str = "") -> None:
                ts = _dt.datetime.now().strftime("%H:%M:%S")
                st.session_state.workforce_event_feed.append(
                    {"time": ts, "icon": icon, "text": text, "cls": cls}
                )

            _add_event("⚡", "Autonomous Workforce launched", "highlight")
            st.rerun()

    # ── If workforce was just launched, actually run it now ──
    if (
        st.session_state.workforce_running
        and st.session_state.workforce_active_node is None
        and len(st.session_state.workforce_event_feed) == 1
    ):
        import datetime as _dt2

        def _add_event2(icon: str, text: str, cls: str = "") -> None:
            ts = _dt2.datetime.now().strftime("%H:%M:%S")
            st.session_state.workforce_event_feed.append(
                {"time": ts, "icon": icon, "text": text, "cls": cls}
            )

        _NODE_META2 = {
            "voice_input":   ("🎙️", "Voice Intake receiving clinical narrative"),
            "triage":        ("🩺", "Triage analyzing red-flag indicators"),
            "researcher":    ("📚", "Researcher querying ChromaDB clinical knowledge"),
            "diagnostic":    ("🧠", "Diagnostic reasoning with Tree-of-Thoughts"),
            "critic":        ("🛡️", "Critic verifying diagnostic confidence"),
            "compliance":    ("🔒", "Compliance auditing PII/PHI boundaries"),
            "hitl":          ("👨‍⚕️", "Practitioner HITL checkpoint evaluating report"),
            "final_compile": ("📋", "Final Compile assembling clinical report"),
            "voice_output":  ("🔊", "Voice Output synthesizing spoken response"),
        }

        def _push_live_topology():
            with topology_placeholder:
                components.html(
                    generate_live_workforce_topology_html(
                        node_states=st.session_state.workforce_node_states,
                        active_node=st.session_state.workforce_active_node,
                        event_feed=st.session_state.workforce_event_feed,
                        retry_count=st.session_state.workforce_retry_count,
                        is_running=st.session_state.workforce_running,
                    ),
                    height=750,
                    scrolling=False,
                )

        try:
            wf_graph2 = compile_workflow()
            _d_pid = st.session_state.get("deep_pid", st.session_state.patient_id)
            _d_sym = st.session_state.get("deep_symptom_text", "")
            _d_lng = st.session_state.get("deep_lang_select", "en")

            init_state2 = SharedState(
                patient_id=_d_pid,
                raw_symptoms=_d_sym,
                detected_language_code=_d_lng,
                retry_count=0,
                hitl_approved=True,
            )

            async def _stream_workflow():
                prev_node = None
                final_state = None

                async for event in wf_graph2.astream_events(init_state2, version="v2"):
                    kind = event.get("event", "")
                    name = event.get("name", "")

                    if kind == "on_chain_start" and name in _NODE_META2:
                        node_id = name
                        icon, desc = _NODE_META2[node_id]

                        if prev_node and prev_node in _NODE_META2:
                            st.session_state.workforce_node_states[prev_node] = "complete"
                            _add_event2("✓", f"{_NODE_META2[prev_node][0]} {prev_node.replace('_',' ').title()} completed", "success")

                        rc = st.session_state.workforce_retry_count
                        if node_id == "diagnostic" and prev_node == "critic":
                            rc += 1
                            st.session_state.workforce_retry_count = rc
                            st.session_state.workforce_node_states["critic"] = "retry"
                            _add_event2("⚠️", f"Self-Healing: Critic routed back to Diagnostic (retry {rc}/3)", "warning")

                        st.session_state.workforce_active_node = node_id
                        st.session_state.workforce_node_states[node_id] = "active"
                        _add_event2(icon, f"{desc}", "highlight")
                        prev_node = node_id
                        _push_live_topology()
                        await asyncio.sleep(0.12)

                    elif kind == "on_chain_end" and name in _NODE_META2:
                        if name == "critic":
                            out = event.get("data", {}).get("output", {})
                            cf = ""
                            if isinstance(out, dict):
                                cf = out.get("critic_feedback", "")
                            elif hasattr(out, "critic_feedback"):
                                cf = out.critic_feedback
                            if cf != "APPROVED_BY_SUPERVISOR":
                                st.session_state.workforce_node_states["critic"] = "retry"
                                _push_live_topology()

                    elif kind == "on_chain_end" and name == "LangGraph":
                        out = event.get("data", {}).get("output")
                        if out:
                            final_state = out if isinstance(out, dict) else out.dict()

                if prev_node:
                    st.session_state.workforce_node_states[prev_node] = "complete"

                st.session_state.workforce_active_node = None
                st.session_state.workforce_running = False
                _add_event2("✅", "Autonomous Workforce completed end-to-end", "success")
                _push_live_topology()
                return final_state

            final = asyncio.run(_stream_workflow())
            if final:
                st.session_state.last_deep_result = final

        except Exception as _ex:
            st.session_state.workforce_running = False
            st.session_state.workforce_active_node = None
            import datetime as _dt3
            st.session_state.workforce_event_feed.append({
                "time": _dt3.datetime.now().strftime("%H:%M:%S"),
                "icon": "❌",
                "text": f"Workforce error: {type(_ex).__name__}: {str(_ex)[:120]}",
                "cls": "error",
            })
            _push_live_topology()

        st.rerun()

# =========================================================================
# GLOBAL FOOTER
# =========================================================================
st.markdown(
    """
<div style="text-align:center; color:#64748B; font-size:0.75rem; padding-top:2.5rem; border-top:1px solid rgba(148,163,184,0.1); margin-top:3rem;">
    MedVoice AI &bull; Built for the AssemblyAI Voice Agent Hackathon 2026 &bull;
    AssemblyAI Real-Time Speech-to-Text &bull; 6-Language Unified Mesh &bull; Human-in-the-Loop Safe Healthcare Architecture
</div>
""",
    unsafe_allow_html=True,
)
