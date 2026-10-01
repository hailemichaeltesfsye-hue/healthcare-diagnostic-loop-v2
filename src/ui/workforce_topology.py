"""
Live AI Agent Collaboration Topology Visualization for MedVoice AI.

Renders an interactive, futuristic, NASA-grade 9-node neural collaboration mesh
representing the autonomous peer-to-peer clinical workforce:
1. Voice Intake (AssemblyAI STT)
2. Clinical Triage (Red-Flag Urgency Gate)
3. Medical Researcher (ChromaDB RAG)
4. Diagnostic Reasoning (Tree-of-Thoughts)
5. Critic / Self-Healing (Supervisory Verifier)
6. Compliance Guard (PII/PHI & Regulatory Boundary)
7. Practitioner Review (Human-in-the-Loop Checkpoint)
8. Final Compile (Clinical Synthesis)
9. Multilingual Voice Output (gTTS Audio Engine)

Includes:
- Animated SVG data packet particles moving along handoff connections.
- Specialized Self-Healing reverse loop (Critic -> Diagnostic) with warning pulse.
- Real-time telemetry HUD overlay with active agent focus.
- 9-stage progression ribbon.
- Live agent event stream with autoscroll.
- Client-side interactive walkthrough demo engine for instant hackathon demonstrations.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

# Canonical definition of the 9 real workforce nodes
WORKFORCE_NODES = [
    {
        "id": "voice_input",
        "name": "Voice Intake",
        "short_name": "Intake",
        "icon": "🎙️",
        "sub": "AssemblyAI STT",
        "status_active": "● RECEIVING",
        "status_idle": "STANDBY",
        "left": "11.5%",
        "top": "27%",
        "packet_out": "clinical narrative",
        "edge_out": "edge-vi-tr",
        "part_out": "part-vi-tr",
        "next": "triage",
    },
    {
        "id": "triage",
        "name": "Clinical Triage",
        "short_name": "Triage",
        "icon": "🩺",
        "sub": "Red-Flag Gate",
        "status_active": "● ANALYZING",
        "status_idle": "STANDBY",
        "left": "31.25%",
        "top": "27%",
        "packet_out": "symptoms & red-flags",
        "edge_out": "edge-tr-re",
        "part_out": "part-tr-re",
        "next": "researcher",
    },
    {
        "id": "researcher",
        "name": "Medical Researcher",
        "short_name": "Research",
        "icon": "📚",
        "sub": "ChromaDB RAG",
        "status_active": "● QUERYING RAG",
        "status_idle": "STANDBY",
        "left": "51.0%",
        "top": "27%",
        "packet_out": "clinical context",
        "edge_out": "edge-re-di",
        "part_out": "part-re-di",
        "next": "diagnostic",
    },
    {
        "id": "diagnostic",
        "name": "Diagnostic Reasoning",
        "short_name": "Reasoning",
        "icon": "🧠",
        "sub": "Tree-of-Thoughts",
        "status_active": "● REASONING",
        "status_idle": "STANDBY",
        "left": "70.8%",
        "top": "27%",
        "packet_out": "differential diagnosis",
        "edge_out": "edge-di-cr",
        "part_out": "part-di-cr",
        "next": "critic",
    },
    {
        "id": "critic",
        "name": "Critic / Verifier",
        "short_name": "Critic",
        "icon": "🛡️",
        "sub": "Self-Healing Loop",
        "status_active": "● VERIFYING",
        "status_idle": "STANDBY",
        "left": "90.1%",
        "top": "27%",
        "packet_out": "verified consensus",
        "edge_out": "edge-cr-co",
        "part_out": "part-cr-co",
        "next": "compliance",
    },
    {
        "id": "compliance",
        "name": "Compliance Guard",
        "short_name": "Compliance",
        "icon": "🔒",
        "sub": "PII / PHI Guard",
        "status_active": "● AUDITING PII",
        "status_idle": "STANDBY",
        "left": "80.2%",
        "top": "73%",
        "packet_out": "compliance audit",
        "edge_out": "edge-co-hi",
        "part_out": "part-co-hi",
        "next": "hitl",
    },
    {
        "id": "hitl",
        "name": "Practitioner HITL",
        "short_name": "HITL Review",
        "icon": "👨‍⚕️",
        "sub": "Physician Review",
        "status_active": "● REVIEWING",
        "status_idle": "STANDBY",
        "left": "57.3%",
        "top": "73%",
        "packet_out": "physician sign-off",
        "edge_out": "edge-hi-fc",
        "part_out": "part-hi-fc",
        "next": "final_compile",
    },
    {
        "id": "final_compile",
        "name": "Final Compile",
        "short_name": "Synthesis",
        "icon": "📋",
        "sub": "Report Compiler",
        "status_active": "● COMPILING",
        "status_idle": "STANDBY",
        "left": "34.4%",
        "top": "73%",
        "packet_out": "final EHR synthesis",
        "edge_out": "edge-fc-vo",
        "part_out": "part-fc-vo",
        "next": "voice_output",
    },
    {
        "id": "voice_output",
        "name": "Voice Output",
        "short_name": "Voice Out",
        "icon": "🔊",
        "sub": "Multilingual TTS",
        "status_active": "● SYNTHESIZING",
        "status_idle": "STANDBY",
        "left": "11.5%",
        "top": "73%",
        "packet_out": "spoken consultation",
        "edge_out": "edge-vo-vi",
        "part_out": "part-vo-vi",
        "next": "voice_input",
    },
]


def generate_live_workforce_topology_html(
    node_states: Optional[Dict[str, str]] = None,
    active_node: Optional[str] = None,
    event_feed: Optional[List[Dict[str, Any]]] = None,
    retry_count: int = 0,
    is_running: bool = False,
    active_packet_label: Optional[str] = None,
) -> str:
    """Generate self-contained HTML/CSS/SVG/JS for the live collaboration topology."""
    node_states = node_states or {}
    event_feed = event_feed or []

    # Prepare JSON serializations for JS
    node_states_json = json.dumps(node_states)
    active_node_json = json.dumps(active_node)
    event_feed_json = json.dumps(event_feed[-25:])
    retry_count_int = int(retry_count)
    is_running_bool = "true" if is_running else "false"
    nodes_meta_json = json.dumps(WORKFORCE_NODES)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}

  :root {{
    --bg-base: #060B14;
    --bg-surface: rgba(11, 19, 36, 0.85);
    --border-subtle: rgba(56, 189, 248, 0.12);
    --accent-cyan: #38BDF8;
    --accent-teal: #06B6D4;
    --accent-emerald: #10B981;
    --accent-amber: #F59E0B;
    --accent-rose: #F43F5E;
    --accent-indigo: #818CF8;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
  }}

  body {{
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-primary);
    overflow: hidden;
  }}

  .topology-container {{
    width: 100%;
    min-height: 720px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    background: radial-gradient(circle at 50% 15%, rgba(14, 30, 58, 0.95) 0%, rgba(6, 11, 20, 0.98) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
  }}

  /* Ambient neural grid pattern */
  .topology-container::before {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(56, 189, 248, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56, 189, 248, 0.02) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
    border-radius: 20px;
  }}

  /* Ambient glowing spot behind diagnostic & critic */
  .neural-spotlight {{
    position: absolute;
    width: 380px;
    height: 240px;
    top: 15%;
    right: 10%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
    filter: blur(40px);
  }}

  /* =========================================================================
     TOP TELEMETRY HUD BAR
     ========================================================================= */
  .telemetry-hud {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 14px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.16);
    border-radius: 12px;
    backdrop-filter: blur(12px);
    position: relative;
    z-index: 15;
    flex-shrink: 0;
  }}

  .hud-left {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .radar-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--accent-emerald);
    box-shadow: 0 0 10px var(--accent-emerald);
    position: relative;
  }}
  .radar-dot::after {{
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 1.5px solid var(--accent-emerald);
    animation: radarPulse 1.8s cubic-bezier(0, 0.2, 0.8, 1) infinite;
  }}
  .radar-dot.idle {{ background: #475569; box-shadow: none; }}
  .radar-dot.idle::after {{ display: none; }}
  .radar-dot.running {{ background: var(--accent-cyan); box-shadow: 0 0 12px var(--accent-cyan); }}
  .radar-dot.running::after {{ border-color: var(--accent-cyan); }}
  .radar-dot.retry {{ background: var(--accent-amber); box-shadow: 0 0 14px var(--accent-amber); }}
  .radar-dot.retry::after {{ border-color: var(--accent-amber); }}

  @keyframes radarPulse {{
    0% {{ transform: scale(1); opacity: 1; }}
    100% {{ transform: scale(2.6); opacity: 0; }}
  }}

  .hud-title {{
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
  }}

  .hud-center {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .agent-focus-chip {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 3px 12px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 700;
    color: var(--accent-cyan);
    letter-spacing: 0.02em;
    transition: all 0.3s ease;
  }}
  .agent-focus-chip.idle {{
    background: rgba(71, 85, 105, 0.18);
    border-color: rgba(71, 85, 105, 0.3);
    color: var(--text-muted);
  }}
  .agent-focus-chip.retry {{
    background: rgba(245, 158, 11, 0.18);
    border-color: rgba(245, 158, 11, 0.5);
    color: #FCD34D;
  }}

  .activity-phase-dots {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.63rem;
    color: var(--text-muted);
    font-weight: 600;
  }}
  .phase-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #334155;
    transition: all 0.3s ease;
  }}
  .phase-dot.active {{
    background: var(--accent-cyan);
    box-shadow: 0 0 6px var(--accent-cyan);
    transform: scale(1.3);
  }}
  .phase-dot.complete {{
    background: var(--accent-emerald);
  }}

  .hud-right {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .hud-btn {{
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #E0F2FE;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .hud-btn:hover {{
    background: rgba(56, 189, 248, 0.22);
    border-color: var(--accent-cyan);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(56, 189, 248, 0.2);
  }}
  .hud-btn:active {{
    transform: translateY(0);
  }}

  .retry-counter-pill {{
    font-size: 0.65rem;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 12px;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: var(--accent-amber);
    display: none;
  }}
  .retry-counter-pill.visible {{ display: flex; align-items: center; gap: 4px; }}

  /* =========================================================================
     SELF-HEALING HERO BANNER
     ========================================================================= */
  .self-healing-banner {{
    display: none;
    align-items: center;
    gap: 10px;
    padding: 7px 16px;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.18) 0%, rgba(239, 68, 68, 0.18) 100%);
    border: 1px solid rgba(245, 158, 11, 0.5);
    border-radius: 12px;
    position: relative;
    z-index: 15;
    animation: pulseHealing 1.5s ease-in-out infinite;
  }}
  .self-healing-banner.visible {{ display: flex; }}

  @keyframes pulseHealing {{
    0%, 100% {{ box-shadow: 0 0 10px rgba(245, 158, 11, 0.15); }}
    50% {{ box-shadow: 0 0 24px rgba(245, 158, 11, 0.35); }}
  }}

  .heal-beacon {{ font-size: 1.1rem; animation: strobeAlert 0.8s ease infinite alternate; }}
  @keyframes strobeAlert {{
    from {{ transform: scale(1); }}
    to {{ transform: scale(1.18); }}
  }}
  .heal-title {{
    font-size: 0.72rem;
    font-weight: 800;
    color: #FDE68A;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  .heal-desc {{
    font-size: 0.65rem;
    color: #FCD34D;
    font-weight: 500;
  }}

  /* =========================================================================
     STEPPER PROGRESS RIBBON
     ========================================================================= */
  .stepper-ribbon {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 14px;
    background: rgba(11, 19, 36, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 10px;
    position: relative;
    z-index: 15;
    flex-shrink: 0;
  }}

  .step-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    position: relative;
    flex: 1;
  }}

  .step-node-bubble {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #1E293B;
    border: 1.5px solid #475569;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    color: #94A3B8;
    transition: all 0.3s ease;
  }}
  .step-node-bubble.active {{
    background: var(--accent-cyan);
    border-color: #E0F2FE;
    color: #04101E;
    font-weight: 800;
    box-shadow: 0 0 10px var(--accent-cyan);
    transform: scale(1.15);
  }}
  .step-node-bubble.complete {{
    background: var(--accent-emerald);
    border-color: #A7F3D0;
    color: #022C22;
    font-weight: 800;
  }}
  .step-node-bubble.retry {{
    background: var(--accent-amber);
    border-color: #FDE68A;
    color: #451A03;
    font-weight: 800;
    box-shadow: 0 0 10px var(--accent-amber);
  }}

  .step-label {{
    font-size: 0.53rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    text-align: center;
    line-height: 1;
  }}
  .step-label.active {{ color: var(--accent-cyan); font-weight: 700; }}
  .step-label.complete {{ color: var(--accent-emerald); }}
  .step-label.retry {{ color: var(--accent-amber); }}

  .step-connector {{
    position: absolute;
    top: 11px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: rgba(71, 85, 105, 0.35);
    z-index: -1;
    transition: background 0.4s ease;
  }}
  .step-connector.complete {{ background: rgba(16, 185, 129, 0.7); }}
  .step-connector.active {{ background: rgba(56, 189, 248, 0.8); box-shadow: 0 0 6px var(--accent-cyan); }}

  /* =========================================================================
     MAIN CANVAS & SVG LAYER
     ========================================================================= */
  .canvas-stage {{
    flex: 1;
    position: relative;
    min-height: 440px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  #topology-svg {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 5;
  }}

  /* SVG EDGES */
  .svg-edge-path {{
    fill: none;
    stroke: rgba(71, 85, 105, 0.3);
    stroke-width: 1.8;
    stroke-linecap: round;
    transition: stroke 0.4s ease, stroke-width 0.4s ease;
  }}
  .svg-edge-path.active {{
    stroke: var(--accent-cyan);
    stroke-width: 2.8;
    filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.7));
  }}
  .svg-edge-path.complete {{
    stroke: rgba(16, 185, 129, 0.55);
    stroke-width: 2.0;
  }}
  .svg-edge-path.neural-crosslink {{
    stroke: rgba(99, 102, 241, 0.18);
    stroke-width: 1.2;
    stroke-dasharray: 4 4;
  }}
  .svg-edge-path.neural-crosslink.pulsing {{
    stroke: rgba(129, 140, 248, 0.5);
    stroke-width: 1.6;
    animation: pulseCrosslink 2s ease-in-out infinite;
  }}

  @keyframes pulseCrosslink {{
    0%, 100% {{ opacity: 0.2; }}
    50% {{ opacity: 0.8; stroke: var(--accent-cyan); }}
  }}

  /* RETRY REVERSE ARCH */
  .svg-edge-path.retry-arch {{
    stroke: rgba(245, 158, 11, 0.4);
    stroke-width: 2.0;
    stroke-dasharray: 6 4;
  }}
  .svg-edge-path.retry-arch.active {{
    stroke: var(--accent-amber);
    stroke-width: 3.2;
    stroke-dasharray: none;
    filter: drop-shadow(0 0 10px rgba(245, 158, 11, 0.8));
    animation: retryArchFlow 1s linear infinite;
  }}

  /* EMERGENCY HALT BYPASS */
  .svg-edge-path.emergency-path {{
    stroke: rgba(244, 63, 94, 0.25);
    stroke-width: 1.5;
    stroke-dasharray: 5 4;
  }}
  .svg-edge-path.emergency-path.active {{
    stroke: var(--accent-rose);
    stroke-width: 2.5;
    filter: drop-shadow(0 0 8px rgba(244, 63, 94, 0.7));
  }}

  /* SVG PARTICLES */
  .svg-particle {{
    display: none;
  }}
  .svg-particle.active {{ display: block; }}
  .svg-particle circle {{
    fill: #38BDF8;
    filter: drop-shadow(0 0 4px #38BDF8) drop-shadow(0 0 12px rgba(56, 189, 248, 0.8));
  }}
  .svg-particle.retry circle {{
    fill: #F59E0B;
    filter: drop-shadow(0 0 6px #F59E0B) drop-shadow(0 0 16px rgba(245, 158, 11, 0.9));
  }}
  .svg-particle.complete circle {{
    fill: #10B981;
    filter: drop-shadow(0 0 4px #10B981);
  }}

  /* DATA PACKET BADGES ON SVG */
  .svg-packet-badge {{
    font-size: 0.54rem;
    font-weight: 700;
    fill: #7DD3FC;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    text-anchor: middle;
    opacity: 0;
    transition: opacity 0.3s ease;
  }}
  .svg-packet-badge.active {{
    opacity: 1;
    animation: packetPulse 1.6s ease-in-out infinite;
  }}
  @keyframes packetPulse {{
    0%, 100% {{ opacity: 0.65; }}
    50% {{ opacity: 1; fill: #FFFFFF; filter: drop-shadow(0 0 4px #38BDF8); }}
  }}

  /* =========================================================================
     NODE CARDS (HTML GLASSMORPHISM OVERLAY)
     ========================================================================= */
  .node-card {{
    position: absolute;
    background: rgba(11, 19, 36, 0.88);
    border: 1.5px solid rgba(148, 163, 184, 0.18);
    border-radius: 14px;
    padding: 9px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 108px;
    text-align: center;
    transform: translate(-50%, -50%);
    backdrop-filter: blur(14px);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 10;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
  }}

  .node-card:hover {{
    transform: translate(-50%, -50%) scale(1.04);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 10px 25px rgba(56, 189, 248, 0.15);
  }}

  /* IDLE STATE */
  .node-card.idle {{
    opacity: 0.72;
    border-color: rgba(71, 85, 105, 0.25);
  }}
  .node-card.idle:hover {{ opacity: 0.95; }}

  /* IDLE BREATHING */
  .node-card.idle-breathe {{
    animation: gentleBreathe 5s ease-in-out infinite;
  }}
  @keyframes gentleBreathe {{
    0%, 100% {{ opacity: 0.7; }}
    50% {{ opacity: 0.88; border-color: rgba(56, 189, 248, 0.25); }}
  }}

  /* ACTIVE STATE */
  .node-card.active {{
    opacity: 1;
    background: linear-gradient(145deg, rgba(14, 38, 64, 0.94) 0%, rgba(10, 24, 45, 0.94) 100%);
    border-color: var(--accent-cyan);
    box-shadow:
      0 0 0 1.5px rgba(56, 189, 248, 0.6),
      0 0 25px rgba(56, 189, 248, 0.35),
      0 0 50px rgba(56, 189, 248, 0.12),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transform: translate(-50%, -50%) scale(1.08);
    z-index: 14;
    animation: activeGlowPulse 2.0s ease-in-out infinite;
  }}

  @keyframes activeGlowPulse {{
    0%, 100% {{
      box-shadow:
        0 0 0 1.5px rgba(56, 189, 248, 0.6),
        0 0 25px rgba(56, 189, 248, 0.35),
        0 0 50px rgba(56, 189, 248, 0.12);
    }}
    50% {{
      box-shadow:
        0 0 0 2px rgba(56, 189, 248, 0.9),
        0 0 35px rgba(56, 189, 248, 0.55),
        0 0 70px rgba(56, 189, 248, 0.2);
    }}
  }}

  /* COMPLETED STATE */
  .node-card.complete {{
    opacity: 1;
    border-color: rgba(16, 185, 129, 0.65);
    background: linear-gradient(145deg, rgba(10, 30, 22, 0.92) 0%, rgba(6, 20, 15, 0.92) 100%);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.2), inset 0 1px 0 rgba(16, 185, 129, 0.15);
  }}

  /* RETRY / SELF-HEALING STATE */
  .node-card.retry {{
    opacity: 1;
    border-color: var(--accent-amber);
    background: linear-gradient(145deg, rgba(45, 28, 6, 0.94) 0%, rgba(30, 18, 4, 0.94) 100%);
    box-shadow:
      0 0 0 1.5px rgba(245, 158, 11, 0.7),
      0 0 30px rgba(245, 158, 11, 0.4),
      0 0 60px rgba(245, 158, 11, 0.15);
    transform: translate(-50%, -50%) scale(1.08);
    z-index: 14;
    animation: retryAlarm 1s ease-in-out infinite;
  }}

  @keyframes retryAlarm {{
    0%, 100% {{ border-color: rgba(245, 158, 11, 0.6); box-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }}
    50% {{ border-color: #FCD34D; box-shadow: 0 0 40px rgba(245, 158, 11, 0.6); }}
  }}

  /* CHECKMARK COMPLETION BADGE */
  .node-badge-complete {{
    position: absolute;
    top: -5px;
    right: -5px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--accent-emerald);
    border: 2px solid #060B14;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.62rem;
    color: #FFFFFF;
    font-weight: 900;
    opacity: 0;
    transform: scale(0.5);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }}
  .node-card.complete .node-badge-complete {{
    opacity: 1;
    transform: scale(1);
  }}

  /* NODE CARD INTERNALS */
  .node-icon-box {{
    font-size: 1.35rem;
    line-height: 1;
    margin-bottom: 2px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
  }}

  .node-name-text {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-primary);
    line-height: 1.2;
    white-space: nowrap;
  }}

  .node-sub-text {{
    font-size: 0.58rem;
    color: var(--text-muted);
    font-weight: 500;
    line-height: 1.1;
    white-space: nowrap;
  }}

  .node-live-status {{
    font-size: 0.56rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    letter-spacing: 0.04em;
    margin-top: 3px;
    background: rgba(71, 85, 105, 0.25);
    color: #94A3B8;
    transition: all 0.3s ease;
    white-space: nowrap;
  }}
  .node-card.active .node-live-status {{
    background: rgba(56, 189, 248, 0.2);
    color: var(--accent-cyan);
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
  }}
  .node-card.complete .node-live-status {{
    background: rgba(16, 185, 129, 0.2);
    color: #6EE7B7;
  }}
  .node-card.retry .node-live-status {{
    background: rgba(245, 158, 11, 0.25);
    color: #FDE68A;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
  }}

  /* =========================================================================
     LIVE AGENT ACTIVITY STREAM (TERMINAL FEED)
     ========================================================================= */
  .event-stream-box {{
    max-height: 125px;
    overflow-y: auto;
    background: rgba(5, 10, 20, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 12px;
    padding: 8px 12px;
    position: relative;
    z-index: 15;
    flex-shrink: 0;
    scrollbar-width: thin;
    scrollbar-color: rgba(56, 189, 248, 0.3) transparent;
  }}

  .event-stream-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.62rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent-cyan);
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
  }}

  .event-stream-entries {{
    display: flex;
    flex-direction: column;
    gap: 3px;
  }}

  .event-stream-row {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    font-size: 0.64rem;
    padding: 2px 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.03);
    animation: slideInRow 0.3s ease;
  }}
  @keyframes slideInRow {{
    from {{ opacity: 0; transform: translateY(-4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .event-time-stamp {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.58rem;
    color: #475569;
    white-space: nowrap;
    flex-shrink: 0;
  }}

  .event-agent-icon {{
    font-size: 0.72rem;
    flex-shrink: 0;
  }}

  .event-msg-text {{
    color: var(--text-secondary);
    line-height: 1.35;
    flex: 1;
  }}
  .event-msg-text.highlight {{ color: #F1F5F9; font-weight: 600; }}
  .event-msg-text.warning {{ color: #FDE68A; font-weight: 600; }}
  .event-msg-text.success {{ color: #6EE7B7; font-weight: 600; }}
  .event-msg-text.error {{ color: #FCA5A5; font-weight: 600; }}

  .event-status-tag {{
    font-size: 0.52rem;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
  }}
  .event-status-tag.active {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-cyan); }}
  .event-status-tag.success {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; }}
  .event-status-tag.warning {{ background: rgba(245, 158, 11, 0.2); color: #FCD34D; }}
  .event-status-tag.error {{ background: rgba(244, 63, 94, 0.2); color: #FDA4AF; }}
</style>
</head>
<body>

<div class="topology-container" id="topoContainer">
  <div class="neural-spotlight"></div>

  <!-- =======================================================================
       1. TOP TELEMETRY HUD BAR
       ======================================================================= -->
  <div class="telemetry-hud">
    <div class="hud-left">
      <div class="radar-dot idle" id="hudRadarDot"></div>
      <span class="hud-title">LIVE WORKFORCE MESH &bull; 9 NODES</span>
    </div>

    <div class="hud-center">
      <div class="agent-focus-chip idle" id="hudFocusChip">
        <span id="hudFocusIcon">●</span>
        <span id="hudFocusText">IDLE — Ready to Execute</span>
      </div>
      <div class="activity-phase-dots">
        <span>PHASE:</span>
        <div class="phase-dot" id="phaseDot1" title="Intake"></div>
        <div class="phase-dot" id="phaseDot2" title="Reasoning"></div>
        <div class="phase-dot" id="phaseDot3" title="Verification"></div>
        <div class="phase-dot" id="phaseDot4" title="Compliance"></div>
        <div class="phase-dot" id="phaseDot5" title="Output"></div>
      </div>
    </div>

    <div class="hud-right">
      <div class="retry-counter-pill" id="hudRetryPill">
        <span>↩ RETRY:</span>
        <span id="hudRetryCount">0</span>/3
      </div>
      <button class="hud-btn" id="btnSimWalkthrough" title="Play animated 60fps walkthrough of the 9-node workforce">
        <span>▶</span><span>Simulate Handoff Loop</span>
      </button>
      <button class="hud-btn" id="btnResetTopology" title="Reset nodes to standby">
        <span>↺</span><span>Reset</span>
      </button>
    </div>
  </div>

  <!-- =======================================================================
       2. SELF-HEALING REVISION HERO BANNER
       ======================================================================= -->
  <div class="self-healing-banner" id="heroHealingBanner">
    <span class="heal-beacon">⚠️</span>
    <div style="flex:1;">
      <div class="heal-title">AUTONOMOUS SELF-HEALING LOOP ACTIVATED</div>
      <div class="heal-desc" id="healBannerSub">
        Critic detected diagnostic confidence below 85% &bull; Routing back to Diagnostic Tree-of-Thoughts for hypothesis refinement (Attempt 1/3)
      </div>
    </div>
  </div>

  <!-- =======================================================================
       3. 9-STAGE STEPPER PROGRESS RIBBON
       ======================================================================= -->
  <div class="stepper-ribbon" id="stepperRibbon">
    <!-- Built dynamically by JavaScript -->
  </div>

  <!-- =======================================================================
       4. MAIN CANVAS STAGE WITH SVG EDGES & HTML CARDS
       ======================================================================= -->
  <div class="canvas-stage" id="canvasStage">

    <!-- SVG CONNECTION MESH (960 x 460 ViewBox) -->
    <svg id="topology-svg" viewBox="0 0 960 460" preserveAspectRatio="xMidYMid meet">
      <defs>
        <!-- Arrowhead Markers -->
        <marker id="arrowCyan" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 9 3.5, 0 7" fill="#38BDF8"/>
        </marker>
        <marker id="arrowEmerald" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 9 3.5, 0 7" fill="#10B981"/>
        </marker>
        <marker id="arrowAmber" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 9 3.5, 0 7" fill="#F59E0B"/>
        </marker>
        <marker id="arrowMuted" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 9 3.5, 0 7" fill="rgba(71,85,105,0.45)"/>
        </marker>
        <marker id="arrowRose" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
          <polygon points="0 0, 9 3.5, 0 7" fill="#F43F5E"/>
        </marker>

        <!-- Glow Filters -->
        <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3.0" result="coloredBlur"/>
          <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-amber" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="4.0" result="coloredBlur"/>
          <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      <!-- NEURAL LATTICE / CROSS-LINKS (P2P COLLABORATION AURA) -->
      <!-- Triage <-> Diagnostic crosslink -->
      <path id="cross-tr-di" class="svg-edge-path neural-crosslink" d="M 300,165 C 440,215 540,215 680,165"/>
      <!-- Researcher <-> Critic crosslink -->
      <path id="cross-re-cr" class="svg-edge-path neural-crosslink" d="M 490,90 C 620,60 740,60 865,90"/>
      <!-- Diagnostic <-> HITL crosslink -->
      <path id="cross-di-hi" class="svg-edge-path neural-crosslink" d="M 680,165 C 680,240 550,240 550,305"/>

      <!-- 1. Voice Intake -> Triage -->
      <path id="edge-vi-tr" class="svg-edge-path" d="M 165,125 L 245,125" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-vi-tr"><textPath href="#edge-vi-tr" startOffset="50%">clinical narrative</textPath></text>

      <!-- 2. Triage -> Researcher -->
      <path id="edge-tr-re" class="svg-edge-path" d="M 355,125 L 435,125" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-tr-re"><textPath href="#edge-tr-re" startOffset="50%">symptoms & flags</textPath></text>

      <!-- 3. Researcher -> Diagnostic -->
      <path id="edge-re-di" class="svg-edge-path" d="M 545,125 L 625,125" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-re-di"><textPath href="#edge-re-di" startOffset="50%">clinical context</textPath></text>

      <!-- 4. Diagnostic -> Critic -->
      <path id="edge-di-cr" class="svg-edge-path" d="M 735,125 L 810,125" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-di-cr"><textPath href="#edge-di-cr" startOffset="50%">Tree-of-Thoughts</textPath></text>

      <!-- 5. Critic -> Compliance (Normal forward consensus) -->
      <path id="edge-cr-co" class="svg-edge-path" d="M 865,165 C 865,245 770,235 770,305" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-cr-co"><textPath href="#edge-cr-co" startOffset="50%">verified consensus</textPath></text>

      <!-- 5B. CRITIC -> DIAGNOSTIC (SELF-HEALING REVISION ARCH OVER THE TOP) -->
      <path id="edge-cr-di-retry" class="svg-edge-path retry-arch" d="M 865,85 C 865,22 680,22 680,85" marker-end="url(#arrowAmber)"/>
      <text class="svg-packet-badge" id="lbl-retry" style="fill:#F59E0B;"><textPath href="#edge-cr-di-retry" startOffset="50%">⚠️ self-healing revision</textPath></text>

      <!-- 6. Compliance -> HITL -->
      <path id="edge-co-hi" class="svg-edge-path" d="M 715,335 L 605,335" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-co-hi"><textPath href="#edge-co-hi" startOffset="50%">compliance audit</textPath></text>

      <!-- 7. HITL -> Final Compile -->
      <path id="edge-hi-fc" class="svg-edge-path" d="M 495,335 L 385,335" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-hi-fc"><textPath href="#edge-hi-fc" startOffset="50%">physician sign-off</textPath></text>

      <!-- 8. Final Compile -> Voice Output -->
      <path id="edge-fc-vo" class="svg-edge-path" d="M 275,335 L 165,335" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-fc-vo"><textPath href="#edge-fc-vo" startOffset="50%">structured report</textPath></text>

      <!-- 9. Voice Output -> Voice Intake (Continuous Clinical Lifecycle loop) -->
      <path id="edge-vo-vi" class="svg-edge-path" d="M 110,295 C 75,240 75,220 110,165" marker-end="url(#arrowMuted)"/>
      <text class="svg-packet-badge" id="lbl-vo-vi"><textPath href="#edge-vo-vi" startOffset="50%">voice dialogue</textPath></text>

      <!-- Emergency Compliance Halt Path (Compliance directly to Voice Output) -->
      <path id="edge-co-vo-halt" class="svg-edge-path emergency-path" d="M 770,375 C 600,435 280,435 110,375" marker-end="url(#arrowRose)"/>
      <text class="svg-packet-badge" id="lbl-co-vo-halt" style="fill:#F43F5E;"><textPath href="#edge-co-vo-halt" startOffset="50%">emergency halt override</textPath></text>

      <!-- ===================================================================
           ANIMATED PARTICLES (ONE PER EDGE)
           =================================================================== -->
      <!-- vi -> tr -->
      <g class="svg-particle" id="part-vi-tr">
        <circle r="5.5"><animateMotion dur="1.3s" repeatCount="indefinite" rotate="auto"><mpath href="#edge-vi-tr"/></animateMotion></circle>
      </g>
      <!-- tr -> re -->
      <g class="svg-particle" id="part-tr-re">
        <circle r="5.5"><animateMotion dur="1.2s" repeatCount="indefinite" rotate="auto"><mpath href="#edge-tr-re"/></animateMotion></circle>
      </g>
      <!-- re -> di -->
      <g class="svg-particle" id="part-re-di">
        <circle r="5.5"><animateMotion dur="1.1s" repeatCount="indefinite" rotate="auto"><mpath href="#edge-re-di"/></animateMotion></circle>
      </g>
      <!-- di -> cr -->
      <g class="svg-particle" id="part-di-cr">
        <circle r="5.5"><animateMotion dur="1.1s" repeatCount="indefinite" rotate="auto"><mpath href="#edge-di-cr"/></animateMotion></circle>
      </g>
      <!-- cr -> co (forward) -->
      <g class="svg-particle" id="part-cr-co">
        <circle r="5.5"><animateMotion dur="1.4s" repeatCount="indefinite" rotate="auto"><mpath href="#edge-cr-co"/></animateMotion></circle>
      </g>
      <!-- CR -> DI RETRY (REVERSE PARTICLES - AMBER) -->
      <g class="svg-particle retry" id="part-retry">
        <circle r="6.5"><animateMotion dur="1.1s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1"><mpath href="#edge-cr-di-retry"/></animateMotion></circle>
      </g>
      <!-- co -> hi -->
      <g class="svg-particle" id="part-co-hi">
        <circle r="5.5"><animateMotion dur="1.2s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1"><mpath href="#edge-co-hi"/></animateMotion></circle>
      </g>
      <!-- hi -> fc -->
      <g class="svg-particle" id="part-hi-fc">
        <circle r="5.5"><animateMotion dur="1.1s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1"><mpath href="#edge-hi-fc"/></animateMotion></circle>
      </g>
      <!-- fc -> vo -->
      <g class="svg-particle" id="part-fc-vo">
        <circle r="5.5"><animateMotion dur="1.2s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1"><mpath href="#edge-fc-vo"/></animateMotion></circle>
      </g>
      <!-- vo -> vi -->
      <g class="svg-particle" id="part-vo-vi">
        <circle r="5.0"><animateMotion dur="1.8s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1"><mpath href="#edge-vo-vi"/></animateMotion></circle>
      </g>
    </svg>

    <!-- ===================================================================
         9 REAL NODE CARDS (ABSOLUTE POSITIONS ON THE CANVAS)
         =================================================================== -->
    <!-- 1. Voice Intake -->
    <div class="node-card idle" id="node-voice_input" style="left:11.5%; top:27%;" onclick="focusNode('voice_input')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🎙️</div>
      <div class="node-name-text">Voice Intake</div>
      <div class="node-sub-text">AssemblyAI STT</div>
      <div class="node-live-status" id="ns-voice_input">STANDBY</div>
    </div>

    <!-- 2. Clinical Triage -->
    <div class="node-card idle" id="node-triage" style="left:31.25%; top:27%;" onclick="focusNode('triage')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🩺</div>
      <div class="node-name-text">Triage</div>
      <div class="node-sub-text">Red-Flag Gate</div>
      <div class="node-live-status" id="ns-triage">STANDBY</div>
    </div>

    <!-- 3. Medical Researcher -->
    <div class="node-card idle" id="node-researcher" style="left:51.0%; top:27%;" onclick="focusNode('researcher')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">📚</div>
      <div class="node-name-text">Researcher</div>
      <div class="node-sub-text">ChromaDB RAG</div>
      <div class="node-live-status" id="ns-researcher">STANDBY</div>
    </div>

    <!-- 4. Diagnostic Reasoning -->
    <div class="node-card idle" id="node-diagnostic" style="left:70.8%; top:27%;" onclick="focusNode('diagnostic')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🧠</div>
      <div class="node-name-text">Diagnostic</div>
      <div class="node-sub-text">Tree-of-Thoughts</div>
      <div class="node-live-status" id="ns-diagnostic">STANDBY</div>
    </div>

    <!-- 5. Critic / Verifier -->
    <div class="node-card idle" id="node-critic" style="left:90.1%; top:27%;" onclick="focusNode('critic')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🛡️</div>
      <div class="node-name-text">Critic</div>
      <div class="node-sub-text">Self-Healing</div>
      <div class="node-live-status" id="ns-critic">STANDBY</div>
    </div>

    <!-- 6. Compliance Guard -->
    <div class="node-card idle" id="node-compliance" style="left:80.2%; top:73%;" onclick="focusNode('compliance')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🔒</div>
      <div class="node-name-text">Compliance</div>
      <div class="node-sub-text">PII / PHI Guard</div>
      <div class="node-live-status" id="ns-compliance">STANDBY</div>
    </div>

    <!-- 7. Practitioner HITL -->
    <div class="node-card idle" id="node-hitl" style="left:57.3%; top:73%;" onclick="focusNode('hitl')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">👨‍⚕️</div>
      <div class="node-name-text">HITL Review</div>
      <div class="node-sub-text">Physician Gate</div>
      <div class="node-live-status" id="ns-hitl">STANDBY</div>
    </div>

    <!-- 8. Final Compile -->
    <div class="node-card idle" id="node-final_compile" style="left:34.4%; top:73%;" onclick="focusNode('final_compile')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">📋</div>
      <div class="node-name-text">Final Compile</div>
      <div class="node-sub-text">Report Synthesizer</div>
      <div class="node-live-status" id="ns-final_compile">STANDBY</div>
    </div>

    <!-- 9. Voice Output -->
    <div class="node-card idle" id="node-voice_output" style="left:11.5%; top:73%;" onclick="focusNode('voice_output')">
      <div class="node-badge-complete">✓</div>
      <div class="node-icon-box">🔊</div>
      <div class="node-name-text">Voice Output</div>
      <div class="node-sub-text">Multilingual TTS</div>
      <div class="node-live-status" id="ns-voice_output">STANDBY</div>
    </div>

  </div><!-- /canvas-stage -->

  <!-- =======================================================================
       5. LIVE AGENT ACTIVITY STREAM (TERMINAL FEED)
       ======================================================================= -->
  <div class="event-stream-box" id="eventStreamBox">
    <div class="event-stream-header">
      <span>⚡ LIVE AGENT ACTIVITY &amp; P2P HANDOFF STREAM</span>
      <span style="font-size:0.55rem; color:#475569;">TELEMETRY ACTIVE</span>
    </div>
    <div class="event-stream-entries" id="eventStreamRows"></div>
  </div>

</div><!-- /topology-container -->

<script>
(function() {{
  'use strict';

  // ── INJECTED REAL STATE FROM PYTHON ──
  var nodeStates = {node_states_json};
  var activeNode = {active_node_json};
  var eventFeed  = {event_feed_json};
  var retryCount = {retry_count_int};
  var isRunning  = {is_running_bool};
  var NODES_DEF  = {nodes_meta_json};

  // Edge mappings
  var EDGE_MAPPINGS = {{
    'voice_input':   {{ next:'triage',        edge:'edge-vi-tr', part:'part-vi-tr', lbl:'lbl-vi-tr' }},
    'triage':        {{ next:'researcher',    edge:'edge-tr-re', part:'part-tr-re', lbl:'lbl-tr-re' }},
    'researcher':    {{ next:'diagnostic',    edge:'edge-re-di', part:'part-re-di', lbl:'lbl-re-di' }},
    'diagnostic':    {{ next:'critic',        edge:'edge-di-cr', part:'part-di-cr', lbl:'lbl-di-cr' }},
    'critic':        {{ next:'compliance',    edge:'edge-cr-co', part:'part-cr-co', lbl:'lbl-cr-co' }},
    'compliance':    {{ next:'hitl',          edge:'edge-co-hi', part:'part-co-hi', lbl:'lbl-co-hi' }},
    'hitl':          {{ next:'final_compile', edge:'edge-hi-fc', part:'part-hi-fc', lbl:'lbl-hi-fc' }},
    'final_compile': {{ next:'voice_output',  edge:'edge-fc-vo', part:'part-fc-vo', lbl:'lbl-fc-vo' }},
    'voice_output':  {{ next:'voice_input',   edge:'edge-vo-vi', part:'part-vo-vi', lbl:'lbl-vo-vi' }}
  }};

  var simTimer = null;
  var isSimulating = false;

  // ── 1. RENDER STEPPER RIBBON ──
  function renderStepperRibbon() {{
    var ribbon = document.getElementById('stepperRibbon');
    if (!ribbon) return;
    ribbon.innerHTML = '';

    NODES_DEF.forEach(function(n, idx) {{
      var item = document.createElement('div');
      item.className = 'step-item';

      var bubble = document.createElement('div');
      var status = (activeNode === n.id) ? 'active' : (nodeStates[n.id] || 'idle');
      bubble.className = 'step-node-bubble ' + status;
      bubble.id = 'step-bubble-' + n.id;
      bubble.innerHTML = (status === 'complete') ? '✓' : n.icon;
      item.appendChild(bubble);

      var lbl = document.createElement('div');
      lbl.className = 'step-label ' + status;
      lbl.id = 'step-label-' + n.id;
      lbl.textContent = n.short_name;
      item.appendChild(lbl);

      if (idx < NODES_DEF.length - 1) {{
        var connector = document.createElement('div');
        connector.className = 'step-connector ' + (status === 'complete' ? 'complete' : (status === 'active' ? 'active' : ''));
        connector.id = 'step-conn-' + n.id;
        item.appendChild(connector);
      }}

      ribbon.appendChild(item);
    }});
  }}

  // ── 2. APPLY NODE STATES TO CARDS & EDGES ──
  function applyWorkflowVisuals() {{
    NODES_DEF.forEach(function(n) {{
      var card = document.getElementById('node-' + n.id);
      var statusEl = document.getElementById('ns-' + n.id);
      if (!card) return;

      var currentStatus = nodeStates[n.id] || 'idle';
      if (activeNode === n.id) {{
        currentStatus = 'active';
      }}

      card.className = 'node-card ' + currentStatus;
      if (statusEl) {{
        if (currentStatus === 'active') {{
          statusEl.textContent = n.status_active;
        }} else if (currentStatus === 'complete') {{
          statusEl.textContent = '✓ COMPLETED';
        }} else if (currentStatus === 'retry') {{
          statusEl.textContent = '⚠️ RE-EVALUATING';
        }} else {{
          statusEl.textContent = 'STANDBY';
        }}
      }}
    }});

    // Update forward edges and animated particles
    Object.keys(EDGE_MAPPINGS).forEach(function(fromNode) {{
      var map = EDGE_MAPPINGS[fromNode];
      var toNode = map.next;
      var fromStatus = (activeNode === fromNode) ? 'active' : (nodeStates[fromNode] || 'idle');
      var toStatus   = (activeNode === toNode)   ? 'active' : (nodeStates[toNode]   || 'idle');

      var edgeEl = document.getElementById(map.edge);
      var partEl = document.getElementById(map.part);
      var lblEl  = document.getElementById(map.lbl);

      var isEdgeActive = (fromNode === activeNode || (fromStatus === 'active' && toStatus !== 'complete'));
      var isEdgeComplete = (fromStatus === 'complete' && (toStatus === 'complete' || toStatus === 'active'));

      if (edgeEl) {{
        edgeEl.className = 'svg-edge-path' +
          (isEdgeActive ? ' active' : '') +
          (isEdgeComplete ? ' complete' : '');
        if (isEdgeActive) {{
          edgeEl.setAttribute('marker-end', 'url(#arrowCyan)');
        }} else if (isEdgeComplete) {{
          edgeEl.setAttribute('marker-end', 'url(#arrowEmerald)');
        }} else {{
          edgeEl.setAttribute('marker-end', 'url(#arrowMuted)');
        }}
      }}

      if (partEl) {{
        partEl.className = 'svg-particle' + (isEdgeActive ? ' active' : (isEdgeComplete ? ' complete' : ''));
      }}

      if (lblEl) {{
        lblEl.className = 'svg-packet-badge' + (isEdgeActive ? ' active' : '');
      }}
    }});

    // Update Self-Healing Reverse Arch
    var criticStatus = (activeNode === 'critic') ? 'active' : (nodeStates['critic'] || 'idle');
    var isSelfHealing = (criticStatus === 'retry' || (retryCount > 0 && activeNode === 'diagnostic'));

    var retryArch = document.getElementById('edge-cr-di-retry');
    var retryPart = document.getElementById('part-retry');
    var retryLbl  = document.getElementById('lbl-retry');
    var healBanner = document.getElementById('heroHealingBanner');
    var healSubText = document.getElementById('healBannerSub');

    if (retryArch) {{
      retryArch.className = 'svg-edge-path retry-arch' + (isSelfHealing ? ' active' : '');
    }}
    if (retryPart) {{
      retryPart.className = 'svg-particle retry' + (isSelfHealing ? ' active' : '');
    }}
    if (retryLbl) {{
      retryLbl.className = 'svg-packet-badge' + (isSelfHealing ? ' active' : '');
    }}
    if (healBanner) {{
      healBanner.className = 'self-healing-banner' + (isSelfHealing ? ' visible' : '');
      if (healSubText) {{
        healSubText.textContent = 'Critic detected diagnostic confidence < 85% &bull; Routing back to Diagnostic Reasoning for clinical refinement (Attempt ' + (retryCount || 1) + '/3)';
      }}
    }}

    // Update Telemetry HUD
    updateTelemetryHUD();
    renderStepperRibbon();
  }}

  // ── 3. UPDATE TELEMETRY HUD ──
  function updateTelemetryHUD() {{
    var radarDot = document.getElementById('hudRadarDot');
    var focusChip = document.getElementById('hudFocusChip');
    var focusIcon = document.getElementById('hudFocusIcon');
    var focusText = document.getElementById('hudFocusText');
    var retryPill = document.getElementById('hudRetryPill');
    var retryText = document.getElementById('hudRetryCount');

    if (retryPill && retryText) {{
      retryText.textContent = retryCount;
      retryPill.className = 'retry-counter-pill' + (retryCount > 0 ? ' visible' : '');
    }}

    if (!isRunning && !activeNode && !isSimulating) {{
      if (radarDot) radarDot.className = 'radar-dot idle';
      if (focusChip) focusChip.className = 'agent-focus-chip idle';
      if (focusIcon) focusIcon.textContent = '●';
      if (focusText) focusText.textContent = 'IDLE — Ready to Execute';
      updatePhaseDots(0);
    }} else if (activeNode) {{
      var activeMeta = null;
      for (var i = 0; i < NODES_DEF.length; i++) {{
        if (NODES_DEF[i].id === activeNode) {{ activeMeta = NODES_DEF[i]; break; }}
      }}
      var isRetry = (activeNode === 'diagnostic' && retryCount > 0) || (nodeStates['critic'] === 'retry');
      if (radarDot) radarDot.className = 'radar-dot ' + (isRetry ? 'retry' : 'running');
      if (focusChip) focusChip.className = 'agent-focus-chip ' + (isRetry ? 'retry' : '');
      if (focusIcon && activeMeta) focusIcon.textContent = activeMeta.icon;
      if (focusText && activeMeta) {{
        focusText.textContent = activeMeta.name + ' (' + activeMeta.sub + ')';
      }}
      // Phase mapping: 1: intake/triage, 2: researcher/diagnostic, 3: critic, 4: compliance/hitl, 5: compile/output
      var phaseIdx = 1;
      if (activeNode === 'researcher' || activeNode === 'diagnostic') phaseIdx = 2;
      else if (activeNode === 'critic') phaseIdx = 3;
      else if (activeNode === 'compliance' || activeNode === 'hitl') phaseIdx = 4;
      else if (activeNode === 'final_compile' || activeNode === 'voice_output') phaseIdx = 5;
      updatePhaseDots(phaseIdx);
    }} else {{
      if (radarDot) radarDot.className = 'radar-dot running';
      if (focusChip) focusChip.className = 'agent-focus-chip';
      if (focusIcon) focusIcon.textContent = '⚡';
      if (focusText) focusText.textContent = 'Workforce Executing Autonomous Mesh…';
    }}
  }}

  function updatePhaseDots(activeIdx) {{
    for (var i = 1; i <= 5; i++) {{
      var dot = document.getElementById('phaseDot' + i);
      if (dot) {{
        dot.className = 'phase-dot' + (i === activeIdx ? ' active' : (i < activeIdx ? ' complete' : ''));
      }}
    }}
  }}

  // ── 4. RENDER LIVE EVENT STREAM ──
  function renderEventStream() {{
    var container = document.getElementById('eventStreamRows');
    if (!container) return;
    container.innerHTML = '';

    if (!eventFeed || eventFeed.length === 0) {{
      container.innerHTML = '<div class="event-stream-row"><span class="event-time-stamp">--:--:--</span><span class="event-agent-icon">ℹ️</span><span class="event-msg-text">Workforce mesh on standby. Trigger autonomous execution to view live handoffs.</span></div>';
      return;
    }}

    eventFeed.forEach(function(ev) {{
      var row = document.createElement('div');
      row.className = 'event-stream-row';

      var ts = document.createElement('span');
      ts.className = 'event-time-stamp';
      ts.textContent = ev.time || '--:--:--';
      row.appendChild(ts);

      var ic = document.createElement('span');
      ic.className = 'event-agent-icon';
      ic.textContent = ev.icon || '●';
      row.appendChild(ic);

      var txt = document.createElement('span');
      txt.className = 'event-msg-text ' + (ev.cls || '');
      txt.textContent = ev.text || '';
      row.appendChild(txt);

      var tag = document.createElement('span');
      tag.className = 'event-status-tag ' + (ev.cls || 'active');
      tag.textContent = (ev.cls || 'INFO').toUpperCase();
      row.appendChild(tag);

      container.appendChild(row);
    }});

    // Auto-scroll to bottom
    var box = document.getElementById('eventStreamBox');
    if (box) box.scrollTop = box.scrollHeight;
  }}

  // ── 5. IDLE BREATHING WHEN UNENGAGED ──
  function updateIdleBreath() {{
    NODES_DEF.forEach(function(n) {{
      var card = document.getElementById('node-' + n.id);
      if (!card) return;
      if (!isRunning && !activeNode && !isSimulating) {{
        card.classList.add('idle-breathe');
      }} else {{
        card.classList.remove('idle-breathe');
      }}
    }});
  }}

  // ── 6. INTERACTIVE 60FPS SIMULATION WALKTHROUGH DEMO ──
  window.runSimulationDemo = function() {{
    if (simTimer) clearTimeout(simTimer);
    isSimulating = true;
    retryCount = 0;
    nodeStates = {{}};
    activeNode = null;
    eventFeed = [];

    function addSimEvent(icon, text, cls) {{
      var d = new Date();
      var ts = [d.getHours(), d.getMinutes(), d.getSeconds()].map(function(v){{ return v<10?'0'+v:v; }}).join(':');
      eventFeed.push({{ time: ts, icon: icon, text: text, cls: cls }});
      renderEventStream();
    }}

    addSimEvent('⚡', 'Demo Walkthrough: Autonomous 9-Agent Peer Mesh initialized', 'highlight');

    // Sequence of steps with real handoffs and self-healing demonstration
    var demoSteps = [
      // 1. Voice Intake
      {{ node: 'voice_input', delay: 1000, icon: '🎙️', msg: 'Voice Intake: Ingested patient audio narrative via AssemblyAI STT', cls: 'active' }},
      // 2. Triage
      {{ node: 'triage', delay: 1400, icon: '🩺', msg: 'Triage Gate: Filtered red-flag vitals (BP: 160/95, Cephalo-ocular stress)', cls: 'active' }},
      // 3. Researcher
      {{ node: 'researcher', delay: 1500, icon: '📚', msg: 'Researcher: Retrieved evidence-based guidelines from ChromaDB Vector Store', cls: 'active' }},
      // 4. Diagnostic Reasoning (Initial Hypothesis)
      {{ node: 'diagnostic', delay: 1700, icon: '🧠', msg: 'Diagnostic: Tree-of-Thoughts initial reasoning generated differential hypothesis', cls: 'active' }},
      // 5. Critic detects confidence < 85% -> SELF HEALING!
      {{ node: 'critic', delay: 1600, icon: '🛡️', msg: 'Critic Gate: Confidence score 78.5% (<85%) &bull; Triggering Self-Healing Loopback!', cls: 'warning', retry: 1 }},
      // 6. Diagnostic Re-evaluates (Self-Healing in action!)
      {{ node: 'diagnostic', delay: 1800, icon: '🧠', msg: 'Self-Healing: Diagnostic Tree-of-Thoughts refined hypothesis (Confidence: 94.2%)', cls: 'highlight' }},
      // 7. Critic re-evaluates and approves
      {{ node: 'critic', delay: 1400, icon: '🛡️', msg: 'Critic Gate: Confidence verified (94.2% >= 85%) &bull; Passed to Compliance', cls: 'success' }},
      // 8. Compliance
      {{ node: 'compliance', delay: 1500, icon: '🔒', msg: 'Compliance Guard: Audited HIPAA boundaries & verified PII/PHI redaction', cls: 'success' }},
      // 9. Practitioner HITL
      {{ node: 'hitl', delay: 1500, icon: '👨‍⚕️', msg: 'Practitioner Review: Attending physician verified differential consensus', cls: 'success' }},
      // 10. Final Compile
      {{ node: 'final_compile', delay: 1400, icon: '📋', msg: 'Final Compile: Structured EHR report and patient advisory assembled', cls: 'active' }},
      // 11. Voice Output
      {{ node: 'voice_output', delay: 1600, icon: '🔊', msg: 'Voice Output: Synthesized native speech consultation for patient', cls: 'success' }}
    ];

    var stepIndex = 0;
    var prevNode = null;

    function executeNextStep() {{
      if (stepIndex >= demoSteps.length) {{
        if (prevNode) nodeStates[prevNode] = 'complete';
        activeNode = null;
        isSimulating = false;
        addSimEvent('✅', 'Demo Walkthrough Complete: Autonomous consensus achieved with 1 self-healing loop', 'success');
        applyWorkflowVisuals();
        return;
      }}

      var step = demoSteps[stepIndex];
      if (prevNode && prevNode !== step.node) {{
        nodeStates[prevNode] = 'complete';
      }}

      activeNode = step.node;
      nodeStates[step.node] = 'active';

      if (step.retry) {{
        retryCount = step.retry;
        nodeStates['critic'] = 'retry';
      }}

      addSimEvent(step.icon, step.msg, step.cls);
      applyWorkflowVisuals();

      prevNode = step.node;
      stepIndex++;
      simTimer = setTimeout(executeNextStep, step.delay);
    }}

    executeNextStep();
  }};

  // Reset topology
  window.resetTopology = function() {{
    if (simTimer) clearTimeout(simTimer);
    isSimulating = false;
    activeNode = null;
    retryCount = 0;
    nodeStates = {{}};
    eventFeed = [{{ time: '--:--:--', icon: '↺', text: 'Topology reset to standby state.', cls: 'highlight' }}];
    applyWorkflowVisuals();
    renderEventStream();
    updateIdleBreath();
  }};

  window.focusNode = function(nodeId) {{
    // Interactive card click focus
    activeNode = nodeId;
    applyWorkflowVisuals();
  }};

  // Attach button events
  function attachControls() {{
    var btnSim = document.getElementById('btnSimWalkthrough');
    var btnRes = document.getElementById('btnResetTopology');
    if (btnSim) btnSim.addEventListener('click', window.runSimulationDemo);
    if (btnRes) btnRes.addEventListener('click', window.resetTopology);
  }}

  // ── INIT ──
  function init() {{
    renderStepperRibbon();
    applyWorkflowVisuals();
    renderEventStream();
    updateIdleBreath();
    attachControls();
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', init);
  }} else {{
    init();
  }}
}})();
</script>
</body>
</html>
"""
    return html
