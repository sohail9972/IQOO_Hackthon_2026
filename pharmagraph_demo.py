# pharmagraph_demo.py
# PharmaGraph: Universal on-device polypharmacy risk engine.
# FULLY DYNAMIC — no hardcoded contraindications, dose limits, or templates.
# SLM reasons about age, weight, and generates warnings fresh.

from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar
from gnn_engine import gnn_predict, adjust_for_labs, get_age_group
from dynamic_engine import set_llm, dynamic_age_risk, generate_dynamic_warning
from gtts import gTTS
import re
import os

# ============================================================
# 1. CONFIGURE PATHS
# ============================================================
MODEL_PATH = r"D:\Iqoo_Practice_Project\models\drug-v6-q4_k_m.gguf"
GRAMMAR_PATH = r"D:\Iqoo_Practice_Project\models\coglang.gbnf"
SYSTEM_PATH = r"D:\Iqoo_Practice_Project\models\SYSTEM_v6d.txt"

LANG_NAMES = {
    "en": "English", "ta": "Tamil", "hi": "Hindi", "te": "Telugu",
    "ml": "Malayalam", "kn": "Kannada", "bn": "Bengali", "mr": "Marathi",
    "gu": "Gujarati", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
    "ur": "Urdu",
}

# ============================================================
# 2. LOAD SLM
# ============================================================
print("Loading SLM...")
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4, verbose=False)
grammar = LlamaGrammar.from_file(GRAMMAR_PATH)
with open(SYSTEM_PATH, "r", encoding="utf-8") as f:
    system_prompt = f.read()
print("SLM loaded.\n")

# Inject SLM into dynamic engine
set_llm(llm)


# ============================================================
# 3. CORE: SLM translates NL → CogLang
# ============================================================
def nl_to_coglang(user_input):
    prompt = (f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
              f"<|im_start|>user\n{user_input}<|im_end|>\n"
              f"<|im_start|>assistant\n")
    output = llm.create_completion(prompt=prompt, grammar=grammar,
                                   max_tokens=64, temperature=0, stop=["<|im_end|>"])
    return output['choices'][0]['text'].strip()


def parse_coglang(query):
    match = re.match(r'Traverse\["([^"]+)",\s*"([^"]+)"\]', query)
    if match:
        return {"operator": "Traverse", "drug": match.group(1), "relation": match.group(2)}
    match = re.match(r'Get\["([^"]+)",\s*"([^"]+)"\]', query)
    if match:
        return {"operator": "Get", "drug": match.group(1), "attribute": match.group(2)}
    return {"error": "Unknown query format", "raw": query}


# ============================================================
# 4. TTS
# ============================================================
def speak_warning(text, lang_code="ta"):
    try:
        tts = gTTS(text=text, lang=lang_code)
        filename = f"warning_{lang_code}.mp3"
        tts.save(filename)
        os.system(f"start {filename}")
        print(f"[AUDIO] Playing {lang_code} warning...")
    except Exception as e:
        print(f"[AUDIO] TTS error: {e}")


# ============================================================
# 5. FULLY DYNAMIC PIPELINE — Single drug
# ============================================================
def pharmagraph_dynamic(user_input, patient_profile, lang="en", speak=False):
    """
    Fully dynamic pipeline:
      NL → CogLang (SLM) → Dynamic age risk (SLM reasons)
      → Lab adjustment → Dynamic warning (SLM writes)
    No hardcoded contraindications, doses, or templates.
    """
    age = patient_profile.get("age", 30)
    weight_kg = patient_profile.get("weight_kg")

    print("=" * 60)
    print(f"[USER] {user_input}  (Lang: {lang}, Age: {age}, Weight: {weight_kg})")

    # Step 1: SLM translates NL → CogLang
    coglang = nl_to_coglang(user_input)
    print(f"[SLM]  {coglang}")

    parsed = parse_coglang(coglang)
    if "error" in parsed:
        print(f"[ERROR] {parsed}")
        return
    drug = parsed["drug"]
    print(f"[PARSE] drug={drug}")

    # Step 2: Dynamic age risk — SLM reasons about safety
    age_risk = dynamic_age_risk(drug, age, weight_kg)
    print(f"[AGE-RISK] {age_risk['risk']} — {age_risk['reason']}")

    # Step 3: Lab adjustment
    if patient_profile.get("creatinine", 0) > 1.5:
        if age_risk["risk"] in ["SAFE", "MODERATE"]:
            age_risk["risk"] = "HIGH_RISK"
            age_risk["reason"] += "; elevated creatinine"

    # Step 4: Dynamic warning — SLM writes it in target language
    age_risk["drug"] = drug
    warning_text = generate_dynamic_warning(age_risk, patient_profile, lang)
    print(f"[WARNING-{lang.upper()}] {warning_text}")

    if speak:
        speak_warning(warning_text, lang_code=lang)

    print("=" * 60 + "\n")
    return warning_text


# ============================================================
# 6. FULLY DYNAMIC PIPELINE — Prescription image
# ============================================================
def process_prescription_dynamic(image_path, patient_profile, lang="en", speak=False):
    """
    Fully dynamic prescription pipeline.
    OCR → Regex verify → Normalize → Dynamic per-drug risk → Dynamic warning.
    """
    from prescription_ocr import extract_drugs_from_image
    from drug_normalizer import expand_to_generics

    age = patient_profile.get("age", 30)
    weight_kg = patient_profile.get("weight_kg")
    age_group = get_age_group(age)

    print("=" * 60)
    print(f"[SCAN] {image_path}")
    print(f"[PATIENT] Age: {age} ({age_group}), Weight: {weight_kg} kg")

    # Step 1: OCR + regex verification
    verified, summary = extract_drugs_from_image(image_path)
    generics = expand_to_generics(verified)
    print(f"[NORM] Generics: {generics}")

    # Step 2: Dynamic per-drug risk assessment
    risks = []
    for drug in generics:
        r = dynamic_age_risk(drug, age, weight_kg)
        if r["risk"] in ["DANGER", "HIGH_RISK", "MODERATE"]:
            risks.append(r)

    # Step 3: Pairwise interaction check
    for i, a in enumerate(generics):
        for b in generics[i+1:]:
            pair_result = gnn_predict(a, b, age=age, weight_kg=weight_kg)
            if pair_result.get("risk") in ["DANGER", "HIGH_RISK"]:
                risks.append({
                    "drug": f"{a} + {b}",
                    "risk": pair_result["risk"],
                    "side_effect": pair_result.get("side_effect", "interaction"),
                    "reason": pair_result.get("reason", "")
                })

    print(f"[RISKS] {len(risks)} found")

    # Step 4: Dynamic cumulative warning — SLM writes it
    if risks:
        warning_text = generate_cumulative_dynamic_warning(risks, patient_profile, lang)
    else:
        warning_text = generate_dynamic_warning(
            {"risk": "SAFE", "drug": ", ".join(generics), "reason": "No issues found"},
            patient_profile, lang
        )

    print(f"[WARNING] {warning_text}")

    if speak:
        speak_warning(warning_text, lang_code=lang)

    print("=" * 60 + "\n")
    return warning_text


def generate_cumulative_dynamic_warning(risks, patient_profile, lang="en"):
    """SLM writes a cumulative warning for multiple findings."""
    age = patient_profile.get("age", 30)
    weight = patient_profile.get("weight_kg", "unknown")

    findings = []
    for r in risks:
        findings.append(f"- {r['drug']}: {r['risk']} ({r.get('reason', 'no reason')})")
    findings_text = "\n".join(findings)

    lang_name = LANG_NAMES.get(lang, "English")

    prompt = (
        f"<|im_start|>system\n"
        f"You are a medical safety assistant. Generate urgent warnings in {lang_name}.\n"
        f"Maximum 4 sentences. Simple words. Speak to the patient/parent.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Patient: {age} years old, {weight} kg\n\n"
        f"Findings:\n{findings_text}\n\n"
        f"Generate one clear warning in {lang_name}.\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    output = llm.create_completion(
        prompt=prompt,
        max_tokens=250,
        temperature=0.3,
        stop=["<|im_end|>", "\n\n\n"]
    )
    return output['choices'][0]['text'].strip()


# ============================================================
# 7. TEST ALL AGE GROUPS
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PHARMAGRAPH — FULLY DYNAMIC, ALL AGES")
    print("=" * 60 + "\n")

    # Demo 1: Infant + codeine
    print("\n### DEMO 1: INFANT + CODEINE ###\n")
    pharmagraph_dynamic(
        "codeine side effects",
        {"age": 0, "weight_kg": 8},
        lang="en"
    )

    # Demo 2: Child + codeine
    print("\n### DEMO 2: CHILD + CODEINE ###\n")
    pharmagraph_dynamic(
        "codeine side effects",
        {"age": 6, "weight_kg": 20},
        lang="en"
    )

    # Demo 3: Adult + warfarin
    print("\n### DEMO 3: ADULT + WARFARIN ###\n")
    pharmagraph_dynamic(
        "warfarin interactions",
        {"age": 30, "weight_kg": 70},
        lang="en"
    )

    # Demo 4: Elderly + warfarin + elevated creatinine
    print("\n### DEMO 4: ELDERLY + WARFARIN + CREATININE 2.5 ###\n")
    pharmagraph_dynamic(
        "warfarin interactions",
        {"age": 72, "weight_kg": 65, "creatinine": 2.5},
        lang="en"
    )

    # Demo 5: Tamil warning for elderly
    print("\n### DEMO 5: TAMIL WARNING ###\n")
    pharmagraph_dynamic(
        "warfarin interactions",
        {"age": 72, "weight_kg": 65, "creatinine": 2.5},
        lang="ta"
    )

    print("\n" + "=" * 60)
    print("ALL DYNAMIC DEMOS COMPLETE")
    print("=" * 60)