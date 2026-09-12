# dynamic_engine.py
# Dynamic age-aware risk engine using the loaded SLM.
# Replaces all hardcoded contraindication lists, dose limits, and templates.
# FIX: Drug names stay in English, all context in native language.
from translator import translate_to_indic
import re

# The SLM will be injected from pharmagraph_demo.py
_llm = None

def set_llm(llm_instance):
    """Inject the loaded SLM instance."""
    global _llm
    _llm = llm_instance


# ============================================================
# LANGUAGE NAMES
# ============================================================
LANG_NAMES = {
    "en": "English", "ta": "Tamil", "hi": "Hindi", "te": "Telugu",
    "ml": "Malayalam", "kn": "Kannada", "bn": "Bengali", "mr": "Marathi",
    "gu": "Gujarati", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
    "ur": "Urdu",
}


# ============================================================
# 1. DYNAMIC AGE CONTRAINDICATION CHECK
# ============================================================
def is_contraindicated(drug_name, age):
    """
    Ask the SLM if this drug is safe for this age.
    Returns (contraindicated: bool, reason: str).
    """
    if _llm is None:
        return False, "SLM not loaded"

    prompt = (
        f"<|im_start|>system\n"
        f"You are a clinical pharmacologist. Answer with YES or NO only.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Is the drug {drug_name} safe for a {age}-year-old patient?\n"
        f"Answer YES or NO only.\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    output = _llm.create_completion(
        prompt=prompt,
        max_tokens=5,
        temperature=0,
        stop=["<|im_end|>", "\n", ".", " "]
    )
    answer = output['choices'][0]['text'].strip().upper()

    if "NO" in answer:
        reason_prompt = (
            f"<|im_start|>system\n"
            f"You are a clinical pharmacologist. Answer in one short sentence.\n"
            f"<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Why is {drug_name} contraindicated for a {age}-year-old? Answer in one sentence.\n"
            f"<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        reason_out = _llm.create_completion(
            prompt=reason_prompt,
            max_tokens=60,
            temperature=0.3,
            stop=["<|im_end|>", "\n\n"]
        )
        reason = reason_out['choices'][0]['text'].strip()
        return True, reason or f"{drug_name} is not safe for a {age}-year-old."

    return False, ""


# ============================================================
# 2. DYNAMIC WEIGHT-BASED DOSING
# ============================================================
def compute_weight_dose(drug_name, weight_kg, age):
    """
    Ask the SLM for weight-based dosing guidance.
    Returns (safe: bool, guidance: str).
    """
    if _llm is None:
        return True, "SLM not loaded"

    prompt = (
        f"<|im_start|>system\n"
        f"You are a pediatric and geriatric pharmacologist. Be concise.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"For a {age}-year-old patient weighing {weight_kg} kg, "
        f"is the standard adult dose of {drug_name} safe?\n"
        f"Answer with one of: SAFE, REDUCE, or AVOID. Then one short sentence.\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    output = _llm.create_completion(
        prompt=prompt,
        max_tokens=80,
        temperature=0.2,
        stop=["<|im_end|>", "\n\n"]
    )
    result = output['choices'][0]['text'].strip().upper()

    if "AVOID" in result or "REDUCE" in result:
        return False, result
    return True, result


# ============================================================
# 3. DYNAMIC WARNING GENERATION (FIXED)
#    Drug names in English, all context in native language.
# ============================================================
def generate_dynamic_warning(risk_data, patient_profile, lang="en"):
    """
    Two-stage SLM pipeline:
      Stage 1: Generate clinical warning in English (reliable)
      Stage 2: Translate to target language (SLM-based)
    """
    if _llm is None:
        return f"WARNING: {risk_data.get('risk', 'UNKNOWN')} risk detected."

    age = patient_profile.get("age", 30)
    weight = patient_profile.get("weight_kg", "unknown")
    drug = risk_data.get("drug", "medication")
    risk = risk_data.get("risk", "UNKNOWN")
    side_effect = risk_data.get("side_effect") or \
                  (risk_data.get("side_effects", [{}])[0].get("side_effect")
                   if risk_data.get("side_effects") else "adverse effect")
    reason = risk_data.get("reason", "")

    # ============================================================
    # STAGE 1: Generate clinical warning in English
    # ============================================================
    stage1_prompt = (
        f"<|im_start|>system\n"
        f"You are a medical safety assistant. Write a SHORT warning in English.\n"
        f"Maximum 2 sentences. Simple words.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Patient age: {age}\n"
        f"Drug: {drug}\n"
        f"Risk: {risk}\n"
        f"Side effect: {side_effect}\n"
        f"Reason: {reason}\n\n"
        f"Write the warning in English.\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    stage1_output = _llm.create_completion(
        prompt=stage1_prompt,
        max_tokens=100,
        temperature=0.2,
        stop=["<|im_end|>", "\n\n"]
    )
    english_warning = stage1_output['choices'][0]['text'].strip()

    # If English was requested, return stage 1 output
    if lang == "en":
        return english_warning

    # ============================================================
    # STAGE 2: Translate the English warning to target language
    # ============================================================
    lang_name = LANG_NAMES.get(lang, "English")

    stage2_prompt = (
        f"<|im_start|>system\n"
        f"You are a translator. Translate English medical warnings into {lang_name}.\n"
        f"CRITICAL RULES:\n"
        f"1. Keep drug names in ENGLISH (Warfarin, Aspirin, Codeine).\n"
        f"2. Translate everything else into {lang_name} script.\n"
        f"3. Do NOT use Roman letters for non-drug words.\n"
        f"4. Output ONLY the translation. No explanations.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Translate this into {lang_name}:\n"
        f"{english_warning}\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    stage2_output = _llm.create_completion(
        prompt=stage2_prompt,
        max_tokens=200,
        temperature=0.2,
        stop=["<|im_end|>", "\n\n\n"]
    )
    translated = stage2_output['choices'][0]['text'].strip()

    return translated if translated else english_warning

# ============================================================
# 4. HIGH-LEVEL: DYNAMIC RISK ASSESSMENT
# ============================================================
def dynamic_age_risk(drug_name, age, weight_kg=None):
    """
    Full dynamic assessment: contraindication + weight dosing.
    Returns a risk dict. Always includes a 'reason' string.
    """
    result = {"drug": drug_name, "risk": "SAFE", "reasons": []}

    # Check age contraindication
    contraindicated, reason = is_contraindicated(drug_name, age)
    if contraindicated:
        result["risk"] = "DANGER"
        result["reasons"].append(reason or f"{drug_name} is not safe for a {age}-year-old")
        result["reason"] = "; ".join(result["reasons"])
        return result

    # Check weight-based dosing for children
    if weight_kg and age < 13:
        safe, guidance = compute_weight_dose(drug_name, weight_kg, age)
        if not safe:
            result["risk"] = "HIGH_RISK"
            result["reasons"].append(guidance or "Weight-based dose adjustment needed")

    # Infant escalation
    if age < 2 and result["risk"] == "SAFE":
        result["risk"] = "MODERATE"
        result["reasons"].append("Infant — monitor closely")

    # Elderly escalation
    if age >= 65 and result["risk"] == "SAFE":
        result["risk"] = "MODERATE"
        result["reasons"].append("Elderly — reduced clearance likely")

    result["reason"] = "; ".join(result["reasons"]) if result["reasons"] else "No age-related concerns"
    return result


def generate_dynamic_warning(risk_data, patient_profile, lang="en"):
    """
    Stage 1: SLM (drug-v6) generates English clinical warning.
    Stage 2: IndicTrans2 translates to target language.
    Drug names remain in English.
    """
    from translator import translate_to_indic

    if _llm is None:
        return f"WARNING: {risk_data.get('risk', 'UNKNOWN')} risk detected."

    age = patient_profile.get("age", 30)
    weight = patient_profile.get("weight_kg", "unknown")
    drug = risk_data.get("drug", "medication")
    risk = risk_data.get("risk", "UNKNOWN")
    side_effect = risk_data.get("side_effect") or \
                  (risk_data.get("side_effects", [{}])[0].get("side_effect")
                   if risk_data.get("side_effects") else "adverse effect")
    reason = risk_data.get("reason", "")

    # ---------- Stage 1: SLM generates English warning ----------
    prompt = (
        f"<|im_start|>system\n"
        f"You are a medical safety assistant. Write a SHORT warning in English.\n"
        f"Maximum 2 sentences. Simple words.\n"
        f"If DANGER or HIGH_RISK, tell them to call their doctor immediately.\n"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"Patient age: {age}\n"
        f"Drug: {drug}\n"
        f"Risk: {risk}\n"
        f"Side effect: {side_effect}\n"
        f"Reason: {reason}\n\n"
        f"Write the warning.\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    output = _llm.create_completion(
        prompt=prompt,
        max_tokens=80,
        temperature=0.2,
        stop=["<|im_end|>", "\n\n"]
    )
    english_warning = output['choices'][0]['text'].strip()

    if lang == "en":
        return english_warning

    # ---------- Stage 2: Translate with IndicTrans2 ----------
    try:
        translated = translate_to_indic(english_warning, lang)
        return translated
    except Exception as e:
        print(f"[TRANSLATOR ERROR] {e}")
        return english_warning  # fallback to English