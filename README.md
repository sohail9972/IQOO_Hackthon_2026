# PharmaGraph

**On-Device Polypharmacy Risk Engine**

A privacy-first AI system that reads prescriptions, detects dangerous drug interactions, and speaks warnings in 13 Indian languages — all on-device.

## The Problem

- 40% of seniors take 5+ medications daily
- With 4 drugs, there are 6 pairs to check. With 10 drugs, 45 pairs.
- Existing tools only check pairs, ignore age/weight, and only work in English
- Most patients have no recent lab results

## The Solution

1. **Scan** — Camera captures prescription
2. **Read** — Gemma 4 E2B (vision) extracts drug names
3. **Verify** — Regex layer flags uncertain drugs
4. **Analyze** — GNN finds dangerous interactions
5. **Reason** — SLM adjusts risk based on age, weight, labs
6. **Speak** — Warning in Tamil, Hindi, Telugu + 10 more
7. **Alert** — Guardian receives SMS if danger detected

**All on-device. No cloud. No data leak.**

## Architecture
