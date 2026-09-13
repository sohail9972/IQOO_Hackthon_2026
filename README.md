# PharmaGraph

### On-Device Polypharmacy Risk Engine

**A privacy-first AI system that reads prescriptions, detects dangerous drug interactions, and speaks warnings in 13 Indian languages — all on-device.**

Built for **iQOO City Battles 2026 — HealthTech Track (Chennai)**

---

## The Problem

| Statistic | Reality |
| :--- | :--- |
| **40% of seniors** take 5 or more medications daily | Polypharmacy is the norm, not the exception |
| **4 drugs = 6 pairs** to check | Combinatorial explosion begins immediately |
| **10 drugs = 45 pairs** to check | Beyond human capability |
| **Existing tools** only check pairs | They ignore age, weight, and lab results |
| **English-only** interfaces | Elderly Indians can't read the warnings |
| **No lab results** for most patients | Personalization is impossible for them |

**Real-world consequence:** Helena Lambert, 76, died because a pharmacist ignored a drug interaction warning. The warning existed. It was well-known. It was still missed.

---

## The Solution

PharmaGraph runs entirely on-device and provides seven layers of safety:

| Step | What Happens | Technology |
| :--- | :--- | :--- |
| **1. Scan** | Camera captures the prescription | Android Camera |
| **2. Read** | Vision AI extracts drug names | Gemma 4 E2B (multimodal) |
| **3. Verify** | Regex layer flags uncertain drugs | Pattern matching |
| **4. Analyze** | GNN finds dangerous interactions | Graph Neural Network |
| **5. Reason** | SLM adjusts risk for age and labs | drug-v6 (Qwen2.5-1.5B) |
| **6. Speak** | Warning in the patient's language | Android TTS (13 languages) |
| **7. Alert** | Guardian receives SMS if dangerous | Android SmsManager |

**All on-device. No cloud. No prescription data leaves the device.**

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    iQOO 15 Phone                           │
│                    On-Device Processing                     │
│                                                             │
│  ┌──────────────┐                                           │
│  │    Camera    │                                           │
│  │ Prescription │                                           │
│  │    Scan      │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │       Gemma 4 E2B / OCR              │                   │
│  │       Prescription → Drug Text       │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │       Regex Verification Layer       │                   │
│  │       GREEN / YELLOW / RED           │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │           Drug Normalizer            │                   │
│  │       Brand → Generic Names           │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │       GNN Drug Interaction Engine    │                   │
│  │       Pairwise Interaction Analysis  │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │             drug-v6 SLM              │                   │
│  │      Age + Weight + Lab Reasoning     │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │          Warning Generator           │                   │
│  │        13 Indian Languages            │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                   │
│      ┌──┴──────────┐                                        │
│      ▼             ▼                                        │
│  ┌────────┐    ┌──────────────┐                             │
│  │  TTS   │    │ Guardian SMS │                             │
│  │ Voice  │    │    Alert     │                             │
│  └────────┘    └──────────────┘                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

