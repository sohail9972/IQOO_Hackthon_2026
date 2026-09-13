# PharmaGraph

### On-Device Polypharmacy Risk Engine

A privacy-first AI system that reads prescriptions, detects dangerous drug interactions, and speaks warnings in 13 Indian languages — all on-device.

*Built for iQOO City Battles 2026 — HealthTech Track (Chennai)*

---

## The Problem

| Statistic | Reality |
|---|---|
| 40% of seniors take 5 or more medications daily | Polypharmacy is the norm, not the exception |
| 4 drugs = 6 pairs to check | Combinatorial explosion begins immediately |
| 10 drugs = 45 pairs to check | Beyond human capability |
| Existing tools only check pairs | They ignore age, weight, and lab results |
| English-only interfaces | Elderly Indians can't read the warnings |
| No lab results for most patients | Personalization is impossible for them |

**Real-world consequence:** Helena Lambert, 76, died because a pharmacist ignored a drug interaction warning. The warning existed. It was well-known. It was still missed.

---

## The Solution

PharmaGraph runs entirely on-device and provides seven layers of safety:

| Step | What Happens | Technology |
|---|---|---|
| 1. Scan | Camera captures the prescription | Android Camera |
| 2. Read | Vision AI extracts drug names | Gemma 4 E2B (multimodal) |
| 3. Verify | Regex layer flags uncertain drugs | Pattern matching |
| 4. Analyze | GNN finds dangerous interactions | Graph Neural Network |
| 5. Reason | SLM adjusts risk for age and labs | drug-v6 (Qwen2.5-1.5B) |
| 6. Speak | Warning in the patient's language | Android TTS (13 languages) |
| 7. Alert | Guardian receives SMS if dangerous | Android SmsManager |

All on-device. No cloud. No prescription data leaves the device.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    iQOO 15 Phone                             │
│                    On-Device Processing                      │
│                                                                │
│  ┌──────────────┐                                             │
│  │    Camera    │                                             │
│  │ Prescription │                                             │
│  │    Scan      │                                             │
│  └──────┬───────┘                                             │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │       Gemma 4 E2B / OCR              │                     │
│  │       Prescription → Drug Text       │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │       Regex Verification Layer       │                     │
│  │       GREEN / YELLOW / RED           │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │           Drug Normalizer            │                     │
│  │       Brand → Generic Names          │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │       GNN Drug Interaction Engine    │                     │
│  │       Pairwise Interaction Analysis  │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │             drug-v6 SLM              │                     │
│  │      Age + Weight + Lab Reasoning    │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                     │
│  │          Warning Generator           │                     │
│  │        13 Indian Languages           │                     │
│  └──────┬───────────────────────────────┘                     │
│         │                                                     │
│      ┌──┴──────────┐                                          │
│      ▼             ▼                                          │
│  ┌────────┐    ┌──────────────┐                                │
│  │  TTS   │    │ Guardian SMS │                                │
│  │ Voice  │    │    Alert     │                                │
│  └────────┘    └──────────────┘                                │
│                                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Safety Pipeline

```
Prescription Image
        │
        ▼
     OCR / Vision
        │
        ▼
Raw Prescription Text
        │
        ▼
Stage A Drug Extraction
        │
        ▼
Drug-v6 SLM
        │
        ▼
Drug Normalization
        │
        ▼
Deterministic Verification
        │
        ▼
Verified Drug List
        │
        ▼
Interaction Engine
        │
        ▼
Risk Analysis
        │
        ▼
Localized Warning
        │
   ┌────┼────┐
   ▼    ▼    ▼
  UI   TTS  SMS
```

**Safety principle:** AI models assist with extraction, normalization, and reasoning. Final interaction/risk decisions should be grounded in deterministic or trusted medical data rather than allowing an LLM to invent drug interactions.

---

## Technology Stack

### On-Device Models

| Model | Size | Purpose | Format |
|---|---|---|---|
| drug-v6 | ~986 MB | Natural language → CogLang query / medication reasoning | GGUF (Q4_K_M) |
| Gemma 4 E2B | ~1.5 GB | Vision OCR for prescriptions | GGUF + mmproj |
| GNN | — | Pairwise drug interaction analysis | Python / Kotlin |

### Runtimes

| Component | Technology |
|---|---|
| SLM inference | llama.cpp |
| Vision inference | llama.cpp / multimodal runtime |
| NPU acceleration | Qualcomm Hexagon v81 |
| Mobile application | Native Android / Kotlin |
| OCR | Android ML Kit / Vision model |
| Voice output | Android TextToSpeech |
| Guardian alerts | Android SmsManager |
| Build system | Gradle / Kotlin DSL |

---

## Project Structure

```
PharmaGraph/
│
├── README.md
│
├── gnn_engine.py
├── dynamic_engine.py
├── pharmagraph_demo.py
├── prescription_ocr.py
├── prescription_verifier.py
├── drug_normalizer.py
├── translator.py
├── guardian_alert.py
│
├── test_drug.py
├── test_ocr.py
│
├── models/
│   ├── drug-v6-q4_k_m.gguf
│   ├── gemma-4-E2B-it-Q4_K_M.gguf
│   ├── mmproj-BF16.gguf
│   ├── coglang.gbnf
│   └── SYSTEM_v6d.txt
│
└── android/
    └── PharmaGraph/
        ├── app/
        ├── build.gradle.kts
        ├── settings.gradle.kts
        └── ...
```

> Model files are intentionally excluded from Git because of their size.

---

## Laptop Prototype

### Quick Start

**Prerequisites**

```bash
pip install llama-cpp-python gtts requests deep-translator
```

**Run the Full Pipeline**

```bash
python pharmagraph_demo.py
```

**Test the SLM**

```bash
python test_drug.py
```

**Test OCR**

```bash
python test_ocr.py
```

### Models Required

> Models are not included in this repository because of their size.

**drug-v6**

```bash
hf download zhpy2004/coglang-drug-distill \
  drug-v6-q4_k_m.gguf \
  --local-dir ./models
```

**Gemma 4 E2B**

```bash
hf download unsloth/gemma-4-E2B-it-GGUF \
  --local-dir ./models
```

**Additional Files**

The following files are required for the CogLang pipeline:

```
models/
├── coglang.gbnf
└── SYSTEM_v6d.txt
```

---

## Android Application

### Target Device

- **Device:** iQOO 15
- **Platform:** Android
- **Architecture:** arm64-v8a
- **Runtime:** Native Kotlin
- **Inference:** On-device
- **Acceleration:** Qualcomm Hexagon NPU

### Primary Demo Flow

```
Camera
   ↓
Prescription Image
   ↓
ML Kit OCR
   ↓
Drug Candidate Extraction
   ↓
drug-v6 SLM
   ↓
Drug Normalization
   ↓
Deterministic Verification
   ↓
Drug Interaction Analysis
   ↓
Risk Classification
   ↓
Localized Warning
   ↓
Android TTS
   ↓
Guardian Notification / SMS
```

> The application requires a prescription scan before analysis. Manual drug text should not bypass the prescription scanning workflow in the production/demo path.

### Drug-v6 Integration

The Android application uses drug-v6 as the medication-language reasoning layer.

**Example:**

OCR:

```
Tab Asparin 75mg
1-0-1
```

Drug-v6 can interpret the candidate:

```json
[
  {
    "raw_name": "Asparin",
    "candidate_name": "Aspirin",
    "confidence": 0.92
  }
]
```

The candidate is then validated against trusted medication data before it becomes a verified medication.

### Important Safety Boundary

```
OCR
  ↓
Candidate
  ↓
drug-v6
  ↓
Candidate Correction
  ↓
Trusted Verification
  ↓
Verified Drug
```

Drug-v6 must not be treated as the final authority for:

- Drug interactions
- Dosage recommendations
- Diagnosis
- Contraindications
- Medical emergencies
- Final clinical risk

---

## Drug Interaction Engine

For n medications, the number of possible pairs is:

```
n × (n - 1)
─────────────
     2
```

Examples:

```
4 drugs  →  6 pairs
5 drugs  → 10 pairs
6 drugs  → 15 pairs
7 drugs  → 21 pairs
8 drugs  → 28 pairs
9 drugs  → 36 pairs
10 drugs → 45 pairs
```

PharmaGraph models medications as nodes and potential interactions as edges.

```
       Drug A
       /    \
      /      \
 Drug B ---- Drug C
      \      /
       \    /
       Drug D
```

The prototype currently uses a deterministic/mock interaction layer for demonstration.

Production integration can replace this with a validated drug-interaction knowledge graph or trained interaction model.

---

## Risk Model

PharmaGraph separates identification confidence from medical risk.

**Identification Confidence**

```
GREEN
  ↓
High confidence

YELLOW
  ↓
Needs verification

RED
  ↓
Uncertain / unsafe to automatically accept
```

**Medical Risk**

```
SAFE
MODERATE
HIGH_RISK
DANGER
```

This separation prevents an uncertain OCR result from being incorrectly interpreted as a medical risk classification.

---

## 13 Indian Languages Supported

| Language | Code | TTS |
|---|---|---|
| English | en | ✅ |
| Tamil | ta | ✅ |
| Hindi | hi | ✅ |
| Telugu | te | ✅ |
| Malayalam | ml | ✅ |
| Kannada | kn | ✅ |
| Bengali | bn | ✅ |
| Marathi | mr | ✅ |
| Gujarati | gu | ✅ |
| Punjabi | pa | ✅ |
| Odia | or | ✅ |
| Assamese | as | ✅ |
| Urdu | ur | ✅ |

**Localization Principle**

Drug names remain in English where appropriate because medication names are generally standardized and recognizable across medical contexts.

The surrounding warning and instructions are localized into the patient's selected language.

---

## Example Warning Flow

**Input**

Prescription:

```
Warfarin 5mg
Aspirin 75mg
```

**Processing**

```
OCR
 ↓
Warfarin
Aspirin
 ↓
Verification
 ↓
Interaction Engine
 ↓
Potential serious interaction detected
```

**Output**

```
Risk: DANGER

Finding:
Potential severe bleeding risk from the
Warfarin + Aspirin combination.

Action:
Please consult a qualified healthcare
professional before taking these medicines
together.
```

**Voice**

```
Android TextToSpeech
        ↓
Selected Language
        ↓
Spoken Warning
```

**Guardian**

If the configured safety policy triggers an alert:

```
PharmaGraph Alert:

A potentially dangerous medication
combination was detected.

Please check the patient's medication
plan and contact a healthcare professional.
```

---

## Medication Window & Guardian Alert

PharmaGraph can associate medications with a medication window.

Example:

```
Morning:
08:00 – 10:00

Afternoon:
13:00 – 15:00

Night:
20:00 – 22:00
```

Example reminder:

```
PharmaGraph medication reminder:

Aspirin 75 mg is scheduled for the
08:00 AM – 10:00 AM medication window.
```

The system should describe the medication as scheduled or that a window has started.

It should not claim that the medication was consumed unless an actual adherence signal confirms consumption.

---

## Guardian SMS

The Android application can use:

- Android SmsManager

SMS state should be tracked explicitly:

```
SMS_REQUESTED
      ↓
SMS_SENT

or

SMS_FAILED

or

PERMISSION_DENIED
```

The application must never display **"SMS Sent"** when the Android SMS operation actually failed or permission was denied.

If SMS is unavailable, the application can fall back to a local notification.

---

## Privacy

PharmaGraph is designed around an on-device-first architecture.

```
Prescription
     ↓
Camera
     ↓
On-device OCR
     ↓
On-device SLM
     ↓
On-device interaction analysis
     ↓
On-device warning
```

The core medication analysis does not require sending prescription images to a cloud AI service.

**Privacy Goals**

- No mandatory cloud OCR
- No mandatory cloud LLM
- Prescription images remain local
- Drug extraction runs locally
- Medication reasoning runs locally
- Warning generation runs locally
- TTS runs locally
- Guardian communication is explicitly user-configured

---

## What Works

The current prototype has demonstrated:

- ✅ SLM translation
- ✅ CogLang grammar-constrained output
- ✅ Printed prescription OCR
- ✅ Handwritten prescription OCR prototype
- ✅ Drug candidate extraction
- ✅ Deterministic drug verification
- ✅ Drug interaction detection for prototype pairs
- ✅ Age-aware reasoning prototype
- ✅ Multilingual warning templates
- ✅ On-device SLM deployment
- ✅ Qualcomm Hexagon v81 inference verification
- ✅ Guardian SMS logic
- ✅ Native Android camera workflow
- ✅ Android TTS integration

---

## Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| Messy handwriting | OCR accuracy can decrease significantly | User confirmation |
| Ambiguous drug names | Incorrect identification is possible | Deterministic verification |
| SLM multilingual generation | Free-form multilingual output may be inconsistent | Localized fixed warning templates |
| Prototype GNN | Current interaction knowledge is limited | Integrate validated interaction knowledge graph |
| TTS pronunciation | English medication names may be pronounced using English phonetics | Intentional medical naming convention |
| SMS | Depends on Android permissions/network/carrier | Local notification fallback |
| Clinical validation | Prototype is not clinically validated | Professional medical review required |

---

## Safety Disclaimer

PharmaGraph is a technology prototype and is not a medical device or a replacement for a doctor, pharmacist, or other qualified healthcare professional.

The system is intended to demonstrate:

- On-device AI
- Prescription OCR
- Medication normalization
- Drug interaction analysis
- Risk communication
- Multilingual accessibility
- Guardian notification

Users should not change, stop, start, or combine medications based solely on PharmaGraph output.

Potentially dangerous results should be verified with a qualified healthcare professional.

---

## Impact

| Metric | Value |
|---|---|
| Potential users in India | 340M+ |
| Seniors taking 5+ medications | 40% |
| Adverse drug event cost reference | $177B annually |
| Interaction complexity | 45 pairs for 10 drugs |
| Accessibility | 13 Indian languages |
| Privacy | On-device-first |

> Impact statistics are directional problem statements for the prototype and should be validated against current primary sources before being used as formal clinical or market claims.

---

## Roadmap

| Phase | Status | Milestone |
|---|---|---|
| Phase 1 | ✅ Complete | Working laptop prototype |
| Phase 2 | ✅ Complete | Phone deployment with SLM |
| Phase 3 | ✅ Complete | NPU inference verification |
| Phase 4 | 🚧 In Progress | Native Android camera + OCR + SLM + TTS + SMS |
| Phase 5 | 🔮 Future | Production-grade drug interaction knowledge graph |
| Phase 6 | 🔮 Future | ABDM integration and hospital pilot |
| Phase 7 | 🔮 Future | Clinical validation and real-world evaluation |
