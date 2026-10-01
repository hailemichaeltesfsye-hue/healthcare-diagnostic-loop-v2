# MedVoice AI: Multilingual Healthcare Voice Assistant

> **Official Submission for the AssemblyAI Voice Agent Hackathon 2026**  
> *Real-time speech-driven clinical intake, dynamic follow-up questioning, emergency red-flag triage, and structured medical summaries across 6 languages.*

---

## 1. Project Name
**MedVoice AI** — Autonomous Multilingual Healthcare Voice Assistant & Clinical Triaging Agent.

---

## 2. Problem
Healthcare triage and patient intake face critical bottlenecks worldwide:
- **Language Barriers:** Over 40% of non-native patients struggle to articulate acute symptoms in clinical intake forms, resulting in delayed care and misdiagnoses.
- **Form Fatigue:** Traditional typing-based symptom checkers are inaccessible to patients who are elderly, visually impaired, distressed, or experiencing motor difficulties.
- **Missed Emergencies:** Generic chatbots treat life-threatening symptoms (stroke, myocardial infarction, anaphylaxis) with the same casual pacing as routine questions, failing to immediately escalate red-flag conditions.
- **Doctor Burnout:** Clinicians spend up to 50% of their workday translating unstructured patient narratives into structured clinical documentation.

---

## 3. Solution
**MedVoice AI** transforms clinical intake into a natural, safe, and voice-first conversational experience:
1. **Listens with AssemblyAI:** Captures patient speech with high accuracy across multilingual accents and noisy environments.
2. **Screens for Emergencies First:** Instantly checks for red-flag triggers (cardiovascular, respiratory, stroke, hemorrhagic, anaphylaxis) before engaging in prolonged dialogue.
3. **Engages in Adaptive Dialogue:** Empathizes, clarifies symptom duration, location, and severity with focused clinical follow-ups.
4. **Protects Patient Privacy:** Deterministically redacts PII/PHI (names, phones, SSNs, national IDs) prior to LLM reasoning.
5. **Generates Structured Medical Summaries:** Produces clinician-ready, standardized documentation (Chief Complaint, Symptoms, Duration, Severity, Risk Level, Safe Next Steps).
6. **Speaks Back Naturally:** Synthesizes localized spoken responses with multi-TLD resilience and browser Web Speech API fallback.
7. **Bridges to Multi-Agent Consensus:** Optionally dispatches conversational records into a 9-node peer-to-peer LangGraph diagnostic workforce.

---

## 4. Why Voice?
In healthcare, voice is not merely an interface option—it is the **most human, accessible, and informative medium**:
- **Speed & Urgency:** Patients under distress speak 3x faster than they type and convey emotional tone, breathlessness, and distress that text boxes erase.
- **Universal Accessibility:** Voice bridges health literacy gaps, enabling illiterate, elderly, or physically impaired patients to describe their condition freely.
- **Global Inclusivity:** Acoustic speech allows native speakers of languages with complex or non-Latin scripts (Amharic, Arabic, Hindi, Chinese) to seek immediate guidance without keyboard struggle.

---

## 5. Why AssemblyAI?
MedVoice AI relies on **AssemblyAI** as its core speech-to-text intelligence foundation:
- **High-Accuracy Speech-to-Text:** Handles medical terminology, anatomical phrasing, and diverse accents with precision.
- **Automatic Language Detection:** Seamlessly identifies the spoken language out of clinical profiles without requiring manual pre-selection.
- **Low-Latency Streaming & Transcription:** Enables rapid turnaround between patient utterance and clinical reasoning.
- **Production Developer SDK:** Clean Python SDK (`assemblyai >= 1.6`) with flexible configuration for audio streams, in-memory buffers, and media files.

---

## 6. Main Features
- **🎙️ Real-Time Voice Intake:** In-browser live microphone recording (`st.audio_input`), external audio file upload, or keyboard fallback.
- **🚨 Clinical Emergency & Red-Flag Detection:** Real-time screening for critical presentations (chest pain, stroke FAST criteria, respiratory distress, severe bleeding, anaphylaxis) with immediate emergency escalation.
- **🌐 Unified 6-Language Mesh:** Full round-trip speech recognition, clinical reasoning, report generation, and voice synthesis across 6 global languages.
- **📋 Clinician-Ready Structured Summary:** Real-time compilation of Chief Complaint, Extracted Symptoms, Duration, Severity, Triage Risk, and Safe Next Steps with 1-click `.txt` and printable `.html` downloads.
- **🔄 Dynamic Clinical Follow-Up:** Asks one targeted, empathetic question per turn to resolve ambiguities before finalizing the record.
- **🛡️ Healthcare Safety Boundaries:** Strictly non-diagnostic; clearly communicates AI limitations and never prescribes dosages or replaces physicians.
- **🔒 Deterministic PII/PHI Redaction:** Regex-based sanitization of identifiers before any cloud reasoning.
- **⚡ Deep P2P Workforce Mode:** 9-node LangGraph digital workforce with Tree-of-Thoughts reasoning, self-healing critic retry loop (up to 3 retries), ChromaDB RAG, and Human-In-The-Loop practitioner review.

---

## 7. Six-Language Support
MedVoice AI operates on a single canonical `LanguageProfile` abstraction (`src/voice/language_support.py`):

| Language | Code | Native Name | Locale | Flag | STT Engine | TTS Voice Code |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **English** | `en` | English | `en-US` | 🇬🇧 | AssemblyAI (`en`) | `en` (multi-TLD) |
| **Amharic** | `am` | አማርኛ | `am-ET` | 🇪🇹 | AssemblyAI (`am`) | `am` (sanitized) |
| **Arabic** | `ar` | العربية | `ar-SA` | 🇸🇦 | AssemblyAI (`ar`) | `ar` (RTL layout) |
| **Chinese** | `zh` | 中文 | `zh-CN` | 🇨🇳 | AssemblyAI (`zh`) | `zh-CN` |
| **French** | `fr` | Français | `fr-FR` | 🇫🇷 | AssemblyAI (`fr`) | `fr` |
| **Hindi** | `hi` | हिन्दी | `hi-IN` | 🇮🇳 | AssemblyAI (`hi`) | `hi` |

*Every profile includes tailored LLM reasoning instructions, localized medical disclaimers, emergency dispatch warnings, and 1-click test sentences.*

---

## 8. Healthcare Safety Approach
Safety is embedded at every layer of MedVoice AI:
1. **No Doctor Claims:** The agent explicitly identifies as an AI assistant on every conversational turn.
2. **No Definitive Diagnoses:** Uses differential exploratory language (e.g., *"Possible causes include..."* or *"These symptoms warrant examination by..."*).
3. **No Prescription of Drugs:** Prohibits recommending pharmaceutical dosages or off-label treatments.
4. **Deterministic Emergency Gate:** Emergency symptoms bypass prolonged question trees and trigger immediate dispatch guidance to 911 / 112 / local emergency rooms.
5. **Human-in-the-Loop Oversight:** Provides a dedicated review checkpoint where clinical practitioners evaluate and sign off on synthesized reports before archiving.

---

## 9. Architecture

```
                                  ┌────────────────────────┐
                                  │      Patient Voice     │
                                  └───────────┬────────────┘
                                              │ (Live Mic / Upload)
                                              ▼
                                 ╔══════════════════════════╗
                                 ║   AssemblyAI STT Engine  ║
                                 ║  • Language Auto-Detect  ║
                                 ║  • Speech-to-Text Stream ║
                                 ╚════════════┬═════════════╝
                                              │ Transcript & Confidence
                                              ▼
                                 ┌──────────────────────────┐
                                 │   PII / PHI Redaction    │
                                 └────────────┬─────────────┘
                                              │ Safe Narrative
                                              ▼
                                 ╔══════════════════════════╗
                                 ║ Emergency / Red-Flag Gate║
                                 ║  • Cardiovascular Check  ║
                                 ║  • Stroke (FAST) Check   ║
                                 ║  • Respiratory Distress  ║
                                 ╚════════════╤═════════════╝
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      │                                               │
             [CRITICAL RED-FLAG]                                  [ROUTINE / URGENT]
                      │                                               │
                      ▼                                               ▼
         ┌────────────────────────┐                      ┌────────────────────────┐
         │ Immediate ER Alert     │                      │ Semantic RAG (ChromaDB)│
         │ & 911 Dispatch Advice  │                      └────────────┬───────────┘
         └────────────┬───────────┘                                   │ Clinical Evidence
                      │                                               ▼
                      │                                  ┌────────────────────────┐
                      │                                  │ Groq Clinical Reasoner │
                      │                                  │ • Follow-up question   │
                      │                                  │ • Symptom mapping      │
                      │                                  └────────────┬───────────┘
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              │
                                              ▼
                                 ╔══════════════════════════╗
                                 ║ Clinician Medical Summary║
                                 ║  (Chief Complaint, Risk, ║
                                 ║   Symptoms, Next Steps)  ║
                                 ╚════════════╤═════════════╝
                                              │
                                              ▼
                                 ╔══════════════════════════╗
                                 ║ Multilingual Synthesis   ║
                                 ║ • Hardened Multi-TLD TTS ║
                                 ║ • Web Speech Fallback    ║
                                 ╚════════════╤═════════════╝
                                              │ Spoken Response
                                              ▼
                                  ┌────────────────────────┐
                                  │     Patient Hearing    │
                                  └────────────────────────┘
```

---

## 10. Technology Stack
- **Speech Recognition:** AssemblyAI SDK (`assemblyai >= 1.6`)
- **Speech Synthesis:** Hardened Google TTS (`gTTS >= 2.5`) with multi-TLD retry & browser speech synthesis fallback
- **Multi-Agent Orchestration:** LangGraph (`langgraph >= 0.1`) & Pydantic AI (`pydantic >= 2.0`)
- **Clinical Reasoning Engine:** Groq API (`groq >= 0.9`, running `openai/gpt-oss-120b`)
- **Semantic Memory / Vector DB:** ChromaDB (`chromadb >= 0.4`)
- **Frontend Dashboard:** Streamlit (`streamlit >= 1.39`) with custom responsive CSS dark theme
- **Language / Runtime:** Python 3.11+

---

## Project Structure

```
ai-driven-healthcare-diagnostic-loop/
├── app.py                          # Streamlit dashboard — live motion graph UI, voice intake/output, exports
├── pyproject.toml                  # Project metadata and dependencies
├── uv.lock                         # Locked dependency versions
├── .env.example                    # Template for required environment variables
│
├── scripts/
│   ├── run_voice_loop.py           # CLI: run one case end-to-end from an audio file
│   ├── purge_voice_outputs.py      # CLI: sweep old synthesized-report MP3s off disk (PHI retention)
│   └── test_groq.py                # Standalone Groq connectivity smoke test
│
└── src/
    ├── graph/                      # Orchestration layer: state, nodes, routing, graph assembly
    │   ├── state.py                #   SharedState — the single typed object passed between all nodes
    │   ├── nodes.py                #   Thin async adapters binding each agent to the graph
    │   ├── edges.py                #   Conditional routing logic (critic retry gate, compliance branch)
    │   └── pipeline.py             #   compile_workflow() — assembles the 9-node LangGraph StateGraph
    │
    ├── agents/                     # The clinical reasoning workforce
    │   ├── triage.py                #   Symptom extraction (Groq LLM + rule-based fallback)
    │   ├── researcher.py            #   Medical reference lookup via MCP tools
    │   ├── diagnostic.py            #   Tree-of-Thoughts diagnostic reasoning + confidence scoring
    │   ├── critic.py                #   Self-healing retry gate (reads diagnostic_confidence)
    │   ├── compliance.py            #   PII/legal screening + localized final report composition
    │   └── supervisor.py            #   Legacy sequential runner (not wired into compile_workflow)
    │
    ├── llm/                        # Shared LLM plumbing used by triage/diagnostic/compliance
    │   └── groq_client.py           #   Retrying, JSON-mode Groq wrapper + token/cost accounting
    │
    ├── compliance/                 # Deterministic PII/PHI screening (no LLM involved)
    │   ├── pii_redaction.py         #   Regex-based email/SSN/card/ID/phone detection + redaction
    │   └── halt_templates.py        #   Static, pre-translated halt notices (6 languages)
    │
    ├── voice/                      # The multilingual voice round-trip
    │   ├── language_support.py      #   Single source of truth: language codes ↔ display names ↔ flags
    │   ├── transcription_service.py #   AssemblyAI wrapper (speech → text + language detection)
    │   ├── synthesis_service.py     #   gTTS wrapper (text → speech in the patient's language)
    │   ├── nodes.py                  #   voice_input_node / voice_output_node (LangGraph adapters)
    │   └── retention.py              #   Purge helper for old synthesized-report MP3s
    │
    ├── db/
    │   └── vector_store.py           # ChromaDB — retrieves historical patient context for reasoning
    │
    └── mcp_server/                  # Custom Model Context Protocol tool server
        ├── server.py                 #   MCP server implementation
        └── tools.py                  #   Exposed tools (medical guidelines, drug interactions, etc.)
```

## Module Guide

### `src/graph/` — Orchestration
The strictly-typed `SharedState` (Pydantic) is the only thing passed between nodes — no untyped dicts, no hidden agent context. `pipeline.py` assembles the full 9-node graph, including the conditional edges that make the critic retry loop and the compliance short-circuit actually work (previously dormant code in `edges.py` that nothing else in the repo ever triggered).

### `src/agents/` — Clinical Reasoning
Each agent prefers a Groq-backed LLM call and falls back to deterministic, English-only rules if `GROQ_API_KEY` is missing or a call fails — a transient LLM outage degrades the loop instead of crashing it (`current_step` gets a `_FALLBACK` suffix so this is visible on the dashboard).

### `src/llm/` — Shared Reasoning Infrastructure
One hardened Groq client (retries, JSON-mode parsing, token/cost accounting) used by every agent that reasons over patient data, instead of each hand-rolling its own.

### `src/compliance/` — Deterministic PII/PHI Screening
PII/legal-risk detection is regex-based pattern matching in Python, not an LLM's judgment call. This is auditable, testable offline, and — critically — means that when risk is detected, **zero patient content is ever sent to a third-party LLM**; the halt notice is a static, pre-written template per language instead of an LLM generation. Triage's LLM prompt is also built from the redacted text, since triage runs before compliance and would otherwise leak PII one step earlier.

> This is one layer of defense-in-depth (regex pattern matching), not a complete HIPAA de-identification solution. Have it reviewed against your actual regulatory requirements before relying on it in production.

### `src/voice/` — Multilingual Voice Round-Trip
`voice_input_node` and `voice_output_node` bookend the clinical pipeline and are no-ops for text-only runs, so nothing here breaks existing text-based callers. Raw patient audio is deleted immediately after transcription (success or failure) since it's PHI; synthesized report MP3s persist for playback but should be swept periodically with `scripts/purge_voice_outputs.py`.

### `src/db/` and `src/mcp_server/`
Unchanged from the original architecture: an in-memory ChromaDB store for historical patient context, and a custom MCP tool server the researcher agent queries for medical guidelines and drug-interaction checks.

---

## 11. Local Setup

### Prerequisites
- Python 3.11+
- Git

### Installation
```bash
# 1. Clone repository
git clone https://github.com/your-username/medvoice-ai.git
cd medvoice-ai

# 2. Install all dependencies (uses uv — installs Python 3.11 venv automatically)
uv sync

# 3. Copy and fill in your API keys
cp .env.example .env
# Edit .env with your ASSEMBLYAI_API_KEY and GROQ_API_KEY
```

---

## 12. Environment Variables
Create a `.env` file in the project root (see `.env.example`):

```bash
# AssemblyAI API Key (Required for speech-to-text)
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Groq API Key (Required for clinical reasoning)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Override Groq model (default: openai/gpt-oss-120b)
GROQ_MODEL=openai/gpt-oss-120b

# Set to false for browser Streamlit app (browser plays audio natively)
VOICE_AUTO_PLAY=false
```

---

## 13. How to Test & Use MedVoice AI

### Step 1: Launch the Application
Start the Streamlit application using `uv`:
```bash
uv run streamlit run app.py
```
*(Or if you have your virtual environment activated: `streamlit run app.py`)*

Open your browser to: **`http://localhost:8501`**

---

### CLI Utilities & Batch Execution

Run one case end-to-end directly from an audio file via the autonomous diagnostic loop:
`ash
uv run python scripts/run_voice_loop.py path/to/symptoms.wav --auto-approve
`

Sweep synthesized-report MP3s older than 24 hours:
`ash
uv run python scripts/purge_voice_outputs.py --hours 24
`

---

### Step 2: Test Core Capabilities in the Browser

#### 1. 🚀 Test 1-Click Evaluation Scenarios (Instant Playback)
Located at the top of the interface under **1-Click Hackathon Evaluation Scenarios**:
- **🟢 Scenario 1: Low-Risk Symptom Consultation**
  - Click `[ 🟢 Scenario 1: Low-Risk Symptom ]`
  - **Result:** Simulates a patient reporting a mild tension headache. MedVoice AI evaluates symptoms, asks an empathetic follow-up question regarding light sensitivity, provides natural spoken audio response, and tags triage as `🟢 ROUTINE`.
- **🔴 Scenario 2: Emergency Red-Flag Escalation**
  - Click `[ 🔴 Scenario 2: Emergency Red-Flag ]`
  - **Result:** Simulates an acute crushing chest pain presentation. MedVoice AI triggers the **🚨 Critical Emergency Alert**, halts routine questioning, speaks immediate emergency guidance (911 / ER dispatch), and sets triage to `🔴 EMERGENCY`.
- **🌐 Scenario 3: Native Multilingual Voice**
  - In the left sidebar, change the **Active Language Profile** to **Amharic (አማርኛ)**, **Arabic (العربية)**, **French (Français)**, **Chinese (中文)**, or **Hindi (हिन्दी)**.
  - Click `[ 🌐 Scenario 3 ]`.
  - **Result:** MedVoice AI communicates natively in that language with localized script, reasoning, and speech synthesis.

#### 2. 🎙️ Test Live Microphone or Audio Upload
1. In the central **Patient Voice Consultation** card:
   - Click the microphone widget to record your voice live:
     > *"I have had mild stomach cramps and feel slightly nauseous since yesterday."*
   - Or upload an audio file (`.wav`, `.mp3`, `.m4a`, `.ogg`).
2. Click **`🎤 Transcribe & Consult MedVoice AI`**.
3. **AssemblyAI** transcribes the speech in real-time, redacts any sensitive PII, screens for red-flags, consults the clinical RAG vector store, reasons via Groq, and generates natural spoken audio.

#### 3. 📋 Test Clinician-Ready Documentation & Export
1. Observe the **Clinician-Ready Summary** card on the right updating live with:
   - Patient Tracker ID
   - Chief Complaint
   - Mapped Symptoms chips
   - Duration & Severity
   - Safe Clinical Next Steps
2. Click **`⬇️ Printable .html`** to open and print a clinical admission report.
3. Click **`⬇️ Download .txt`** to export the structured text dossier.

#### 4. 🔬 Test the Deep 9-Node Multi-Agent Workforce
1. In the sidebar under **🧭 Architecture Mode**, switch to **`🔬 Deep Clinical P2P Workforce`** *(or click `🚀 Dispatch to Deep Multi-Agent Workforce` from the summary card)*.
2. View the interactive **Graphviz topology** visualizing the 9-node digital workforce:
   - Voice Intake (AssemblyAI) ➔ Triage ➔ Researcher (ChromaDB RAG) ➔ Diagnostic (Tree-of-Thoughts) ⟲ Critic (Self-Healing Gate) ➔ Compliance ➔ Practitioner HITL ➔ Voice Output (gTTS).
3. Click **`⚡ Execute Autonomous Workforce`** to stream clinical state packets across all peer nodes and generate a multi-agent consensus report with spoken audio.

---

## 14. Example Conversations

### Scenario 1: Low-Risk Symptom Consultation (English)
> **Patient (Voice):** *"I've had a dull tension headache for the past two days and I've been feeling unusually tired."*  
> **MedVoice AI (Spoken Response):** *"I understand you're experiencing a dull tension headache along with fatigue over the last two days. To better assess your situation: Is the discomfort accompanied by any sensitivity to light or nausea, and have you been able to sleep normally?"*  
> **Triage Status:** `🟢 ROUTINE`  
> **Summary Generated:** Tension headache, duration: 2 days, severity: mild/dull.

### Scenario 2: Emergency Red-Flag (Cardiovascular)
> **Patient (Voice):** *"I have sudden severe crushing chest pain radiating to my left arm and I can barely catch my breath."*  
> **MedVoice AI (Spoken Response):** *"🚨 CRITICAL RED-FLAG ALERT: Your reported symptoms indicate a potential medical emergency. Please call 911 (or your local emergency services) or go to the nearest emergency department immediately. Do not drive yourself."*  
> **Triage Status:** `🔴 EMERGENCY` (Category: Cardiovascular & Respiratory)  
> **Action:** Immediate ER dispatch guidance; routine questioning halted.

### Scenario 3: Multilingual Consultation (Amharic)
> **Patient (Voice):** *"ላለፉት ሁለት ቀናት ከባድ የራስ ምታት እና ማዞር አለብኝ።"*  
> **MedVoice AI (Spoken Response):** *"ጤና ይስጥልኝ። የገለጹትን ከባድ የራስ ምታት እና የማዞር ስሜት ተረድቻለሁ። ሁኔታውን በይበልጥ ለመረዳት፦ ሕመሙ ድንገት የቀሰቀሰ ነው ወይስ ቀስ በቀስ? እንዲሁም የማየት ችግር ወይም ትኩሳት አጋጥሞዎታል?"*  
> **Triage Status:** `🟢 ROUTINE / EVALUATION`  
> **Language:** 🇪🇹 አማርኛ (Amharic)

---

## 15. Automated Test Suite
Run the comprehensive hackathon verification suite:
```bash
# Run via pytest (recommended — uses the project venv automatically):
uv run python -m pytest tests/ -v

# Or run directly as a script (uses asyncio.run internally):
uv run python tests/test_hackathon_suite.py
```
**Verification Scope:**
- `[PASS]` Centralized 6-Language profile integrity
- `[PASS]` Emergency & red-flag detection across all categories
- `[PASS]` Deterministic PII/PHI redaction
- `[PASS]` Multilingual speech synthesis across all 6 languages
- `[PASS]` Real AssemblyAI Speech-to-Text API connectivity
- `[PASS]` Multi-turn conversational adaptation & structured medical summaries

---

## 16. Limitations
- **Decision-Support Only:** MedVoice AI is an informational triage assistant, not a licensed medical professional.
- **No Physical Examination:** Acoustic and linguistic analysis cannot measure blood pressure, perform palpation, or take electrocardiograms.
- **Audio Environment:** Excessive background noise or simultaneous multiple speakers can degrade speech transcription confidence.

---

## 17. Future Improvements
- **Direct WebRTC Real-Time Audio Streaming:** Integrating AssemblyAI WebSocket streaming directly with browser audio worklets for sub-300ms turn-taking.
- **Acoustic Biomarker Analysis:** Detecting vocal tremors, dyspnea (shortness of breath during pauses), and cough characteristics from raw spectrograms.
- **EHR/FHIR Native Integration:** Automatic dispatch of structured summaries into Epic and Cerner electronic health records.
- **Offline Edge Mode:** Deploying quantized local Whisper/VOSK models on low-connectivity rural health tablets.

---

## Configuration Reference

| Variable | Required | Purpose |
|---|---|---|
| `GROQ_API_KEY` | For real LLM reasoning | Triage/diagnostic/compliance fall back to rule-based logic without it |
| `ASSEMBLYAI_API_KEY` | For voice input | Required only if a patient uploads/records audio |
| `GROQ_MODEL` | No | Override the default Groq model (`openai/gpt-oss-120b`) |
| `VOICE_AUTO_PLAY` | No | `true` (default) for CLI use; set `false` for the Streamlit app, which plays audio client-side instead |
| `KEEP_VOICE_AUDIO_ARTIFACTS` | No | `true` disables automatic deletion of raw input audio — debugging only, never recommended in production |

---

## Author

**Hailemichael Tesfaye Mekuria**
[LinkedIn](https://www.linkedin.com/in/hailemichael-tesfaye-2b7114401/) · [GitHub](https://github.com/hailemichaeltesfsye-hue)

---

## License & Disclaimer
This project is licensed under the Apache 2.0 License.

**Clinical Disclaimer:** MedVoice AI is designed for demonstration and research purposes under the AssemblyAI Voice Agent Hackathon 2026. It does not provide medical diagnosis or treatment. In a medical emergency, immediately contact local emergency services.
