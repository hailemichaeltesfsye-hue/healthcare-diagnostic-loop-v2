# MedVoice AI — Hackathon Video Presentation Script

> **AssemblyAI – Voice Agent Hackathon 2026**  
> **Duration:** 2 Minutes 45 Seconds  
> **Presenter:** Lead Engineer / Submitter  
> **Target Audience:** Hackathon Judges, AssemblyAI Evaluation Team, Healthcare Technologists

---

## Video Timeline & Scene Breakdown

```
0:00 ─── 0:15   The Problem: Healthcare Triage Bottlenecks
0:15 ─── 0:35   Introducing MedVoice AI
0:35 ─── 1:15   Live Voice Conversation & Follow-Up Reasoning
1:15 ─── 1:35   Multilingual Power: Amharic, Arabic, French, Chinese, Hindi
1:35 ─── 1:55   Clinical Safety: Emergency & Red-Flag Escalation
1:55 ─── 2:15   Clinician-Ready Structured Medical Summary & Deep Mode
2:15 ─── 2:30   AssemblyAI Integration & Architectural Flow
2:30 ─── 2:45   Impact, Real-World Vision & Closing
```

---

### [0:00 – 0:15] Scene 1: The Problem
- **Visual:** Presenter on camera or title slide with headline: *"Patient Intake is Broken: Language Barriers, Clunky Forms, and Missed Emergencies."*
- **Speaker Narration:**
  > *"When people feel sick or distressed, the last thing they should have to do is fight with confusing dropdown menus or fill out 20-page forms in a language they barely speak. Today, non-native speakers face diagnostic delays, while critical emergencies get lost in generic chatbots. Healthcare needs a voice."*

---

### [0:15 – 0:35] Scene 2: Introducing MedVoice AI
- **Visual:** Switch to live screen recording of the **MedVoice AI** interface (`http://localhost:8501`). Show the glowing live status: `● ASSEMBLYAI CONNECTED | REAL-TIME TRIAGE ACTIVE`.
- **Speaker Narration:**
  > *"Meet MedVoice AI — an autonomous, multilingual healthcare voice assistant built on AssemblyAI for the 2026 Voice Agent Hackathon. MedVoice AI allows patients to speak naturally in their native language, asks intelligent clinical follow-up questions, detects life-threatening emergencies in real-time, and delivers structured medical summaries for clinicians."*

---

### [0:35 – 1:15] Scene 3: Live Voice Conversation
- **Visual:** Click the microphone widget or click **`[ 🟢 Scenario 1: Low-Risk Symptom ]`**.
  - Show the audio recording waveform moving.
  - Transcript appears immediately: *"I have had a mild throbbing tension headache and trouble sleeping for the past 2 days."*
  - MedVoice AI responds out loud with natural speech:
    *"I understand you're experiencing a dull tension headache along with sleep difficulty over the last two days. To better assess your situation: Is the discomfort accompanied by any sensitivity to light or nausea?"*
  - Point to the live triage badge: `🟢 ROUTINE`.
- **Speaker Narration:**
  > *"Notice how natural that was. AssemblyAI captured the patient's speech with zero delay. Rather than jumping to an unwarranted diagnosis, MedVoice AI acted like an empathetic triage nurse—evaluating symptom onset and asking a focused clinical follow-up question."*

---

### [1:15 – 1:35] Scene 4: Multilingual Demonstration
- **Visual:** Select **Amharic (አማርኛ)** or **Arabic (العربية)** or **French (Français)** in the dropdown.
  - Click **`[ 🌐 Scenario 3: Amharic Voice ]`**.
  - Show the Ethiopic transcript: *"ላለፉት ሁለት ቀናት ከባድ የራስ ምታት እና ማዞር አለብኝ።"*
  - The voice agent immediately speaks back in fluent Amharic audio.
  - Highlight the 6-language switcher in the sidebar: English, Amharic, Arabic, Chinese, French, and Hindi.
- **Speaker Narration:**
  > *"Here is where MedVoice AI truly shines: full six-language inclusivity. The system doesn't just translate text; it runs on a centralized language architecture. The speech recognition, medical reasoning, and voice synthesis happen end-to-end in Amharic, Arabic, French, Chinese, Hindi, or English."*

---

### [1:35 – 1:55] Scene 5: Emergency & Red-Flag Escalation
- **Visual:** Click **`[ 🔴 Scenario 2: Emergency Red-Flag ]`**.
  - Patient statement: *"I have sudden severe crushing chest pain radiating to my left arm and I can barely breathe."*
  - Instantly, the UI shifts to **Red Alert**:
    - Pulsing red badge: `🚨 CRITICAL EMERGENCY DETECTED`.
    - Spoken response: *"CRITICAL RED-FLAG ALERT: Your reported symptoms indicate a potential medical emergency. Please call 911 or proceed immediately to the nearest Emergency Department."*
- **Speaker Narration:**
  > *"Watch what happens during an acute emergency. If a patient presents with symptoms of a myocardial infarction or stroke, our deterministic safety layer instantly halts routine questioning. It fires an immediate red-flag alert and speaks urgent emergency dispatch guidance directly to the patient."*

---

### [1:55 – 2:15] Scene 6: Structured Medical Summary & Deep Workforce
- **Visual:** Highlight the **Structured Medical Summary** panel on the right:
  - Chief Complaint, Mapped Symptoms chips, Duration, Severity, and Recommended Next Steps.
  - Click **`⬇️ Printable .html`** to show the instant clinical document.
  - Click **`[ 🚀 Dispatch to Deep Multi-Agent Workforce ]`** and show the 9-node LangGraph state graph animating across Triage, Researcher (ChromaDB RAG), Diagnostic Tree-of-Thoughts, and Self-Healing Critic retries.
- **Speaker Narration:**
  > *"For healthcare providers, MedVoice AI saves hours of administrative charting. It automatically converts the voice encounter into a structured, clinician-ready medical record. And if advanced consensus is needed, one click dispatches the case into our 9-node LangGraph autonomous workforce."*

---

### [2:15 – 2:30] Scene 7: AssemblyAI Architecture
- **Visual:** Display the architecture diagram showing `Mic → AssemblyAI STT → PII Redaction → Emergency Gate → Groq Reasoner → Multilingual TTS → Spoken Output`.
- **Speaker Narration:**
  > *"Under the hood, AssemblyAI is the voice engine that makes this possible—providing high-fidelity transcription, automatic language detection, and low-latency turnaround even in noisy environments, paired with deterministic safety guardrails and Groq LLM reasoning."*

---

### [2:30 – 2:45] Scene 8: Impact & Conclusion
- **Visual:** Return to presenter or product hero screen with GitHub link and demo URL.
- **Speaker Narration:**
  > *"MedVoice AI doesn't replace doctors—it empowers patients, eliminates language barriers, and ensures emergencies are caught in seconds, not hours. Thank you to AssemblyAI for inspiring the next generation of voice-first healthcare agents!"*

---

## Recording Tips for Maximum Hackathon Score
1. **Audio Quality:** Use a clean USB microphone or headset for recording your narration.
2. **Screen Resolution:** Record at 1080p (1920x1080) with browser zoom set to 100% or 110% so all UI elements and badges are crisp.
3. **Sound On:** Ensure the system audio recording is enabled so the judges can clearly hear MedVoice AI speaking back in English, Amharic, etc.!
4. **Pacing:** Keep mouse movements smooth and intentional. Use the 1-click scenario buttons to demonstrate instant reactivity.
