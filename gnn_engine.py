# gnn_engine.py
# Age-aware GNN inference for PharmaGraph.
# Supports: infants, children, adults, elderly.
# Mock implementation — swap for real pre-trained GNN in production.

# ============================================================
# AGE GROUP DEFINITIONS
# ============================================================
AGE_GROUPS = {
    "infant": (0, 2),
    "child": (3, 12),
    "adult": (13, 64),
    "elderly": (65, 120),
}

# Drugs contraindicated in specific age groups
AGE_CONTRAINDICATIONS = {
    "infant": ["codeine", "aspirin", "ibuprofen", "promethazine", "tetracycline"],
    "child": ["codeine", "aspirin", "tetracycline", "promethazine"],
    "adult": [],
    "elderly": ["glyburide", "diphenhydramine", "amitriptyline", "diazepam"],
}

# Weight-based dose limits (mg/kg) — simplified
WEIGHT_DOSE_LIMITS = {
    "paracetamol": {"infant": 10, "child": 15, "adult": 15, "elderly": 12},
    "ibuprofen": {"infant": 5, "child": 10, "adult": 10, "elderly": 8},
    "amoxicillin": {"infant": 20, "child": 25, "adult": 25, "elderly": 20},
    "codeine": {"infant": 0, "child": 0, "adult": 1, "elderly": 0.5},
}


# ============================================================
# AGE UTILITIES
# ============================================================
def get_age_group(age):
    """Determine age group from age in years."""
    for group, (low, high) in AGE_GROUPS.items():
        if low <= age <= high:
            return group
    return "adult"


def check_age_contraindications(drug_name, age_group):
    """Check if a drug is contraindicated for the age group."""
    contraindicated = AGE_CONTRAINDICATIONS.get(age_group, [])
    for drug in contraindicated:
        if drug in drug_name.lower():
            return {
                "risk": "DANGER",
                "reason": f"{drug_name} is contraindicated for {age_group}s",
                "side_effect": "Severe adverse reaction",
            }
    return None


# ============================================================
# BASE GNN PREDICTION (Mock)
# ============================================================
def _base_gnn_predict(drug_a, drug_b=None):
    """Original GNN logic — mock lookup table."""

    dangerous_pairs = {
        # Classic dangerous pairs
        ("warfarin", "aspirin"): {"risk": "DANGER", "side_effect": "Severe bleeding"},
        ("warfarin", "ibuprofen"): {"risk": "DANGER", "side_effect": "Severe bleeding"},
        ("allopurinol", "mercaptopurine"): {"risk": "DANGER", "side_effect": "Bone marrow suppression"},
        ("metformin", "contrast_dye"): {"risk": "HIGH_RISK", "side_effect": "Lactic acidosis"},

        # Double paracetamol (common in fever + cold combinations)
        ("paracetamol", "paracetamol"): {"risk": "DANGER", "side_effect": "Liver toxicity (double dose)"},
        ("paracetamol", "aceclofenac"): {"risk": "HIGH_RISK", "side_effect": "Liver stress (both contain paracetamol)"},

        # Pediatric risks
        ("codeine", "promethazine"): {"risk": "DANGER", "side_effect": "Respiratory depression"},
        ("codeine", "paracetamol"): {"risk": "HIGH_RISK", "side_effect": "Respiratory depression risk"},

        # NSAID combinations
        ("aceclofenac", "diclofenac"): {"risk": "DANGER", "side_effect": "Severe GI bleeding (double NSAID)"},
        ("aceclofenac", "dexamethasone"): {"risk": "DANGER", "side_effect": "Stomach ulceration (NSAID + steroid)"},
        ("diclofenac", "dexamethasone"): {"risk": "DANGER", "side_effect": "Stomach ulceration (NSAID + steroid)"},

        # Template prescription
        ("paracetamol", "amoxicillin"): {"risk": "MODERATE", "side_effect": "Reduced antibiotic absorption"},
        ("paracetamol", "ascorbic_acid"): {"risk": "MODERATE", "side_effect": "Increased liver stress"},
        ("guaifenesin", "paracetamol"): {"risk": "MODERATE", "side_effect": "CNS depression"},
    }

    if drug_b:
        key = (drug_a.lower(), drug_b.lower())
        key_rev = (drug_b.lower(), drug_a.lower())
        if key in dangerous_pairs:
            return dict(dangerous_pairs[key])
        if key_rev in dangerous_pairs:
            return dict(dangerous_pairs[key_rev])

    single_drug_effects = {
        "warfarin": {"risk": "MODERATE", "side_effects": [{"side_effect": "bleeding", "confidence": 0.87}]},
        "paracetamol": {"risk": "MODERATE", "side_effects": [{"side_effect": "liver stress", "confidence": 0.60}]},
        "ibuprofen": {"risk": "MODERATE", "side_effects": [{"side_effect": "GI upset", "confidence": 0.55}]},
        "aspirin": {"risk": "MODERATE", "side_effects": [{"side_effect": "bleeding", "confidence": 0.70}]},
        "metformin": {"risk": "MODERATE", "side_effects": [{"side_effect": "lactic acidosis", "confidence": 0.45}]},
        "codeine": {"risk": "HIGH_RISK", "side_effects": [{"side_effect": "respiratory depression", "confidence": 0.75}]},
        "guaifenesin": {"risk": "MODERATE", "side_effects": [{"side_effect": "drowsiness", "confidence": 0.55}]},
        "amoxicillin": {"risk": "MODERATE", "side_effects": [{"side_effect": "GI upset", "confidence": 0.50}]},
    }

    if drug_a.lower() in single_drug_effects:
        return dict(single_drug_effects[drug_a.lower()])

    return {"risk": "SAFE", "side_effects": []}


# ============================================================
# AGE ADJUSTMENT
# ============================================================
def adjust_for_age(gnn_result, age, weight_kg=None):
    """
    Adjust GNN risk based on age and weight.

    Rules:
      - Infants: escalate all MODERATE risks to HIGH_RISK
      - Children: check weight; escalate if underweight
      - Elderly: escalate MODERATE to HIGH_RISK (reduced kidney function)
      - Adults: no adjustment
    """
    age_group = get_age_group(age)
    result = dict(gnn_result)
    result["age_group"] = age_group

    if age_group == "infant":
        if result.get("risk") == "MODERATE":
            result["risk"] = "HIGH_RISK"
            result["reason"] = "Infant — all drug risks escalated"
        elif result.get("risk") == "SAFE":
            result["risk"] = "MODERATE"
            result["reason"] = "Infant — monitor closely"

    elif age_group == "child" and weight_kg:
        result["weight_context"] = f"Child weight: {weight_kg} kg"
        if weight_kg < 15:
            if result.get("risk") == "MODERATE":
                result["risk"] = "HIGH_RISK"
                result["reason"] = "Low weight — dose adjustment needed"

    elif age_group == "elderly":
        if result.get("risk") == "MODERATE":
            result["risk"] = "HIGH_RISK"
            result["reason"] = "Elderly — reduced kidney function likely"

    return result


# ============================================================
# MAIN PREDICTION FUNCTION (age-aware)
# ============================================================
def gnn_predict(drug_a, drug_b=None, age=None, weight_kg=None):
    """
    Age-aware GNN prediction.

    Args:
        drug_a: primary drug name
        drug_b: optional second drug
        age: patient age in years (optional)
        weight_kg: patient weight in kg (optional, for children)

    Returns:
        dict with risk, side_effect(s), reason
    """
    # Age contraindication check first
    if age:
        age_group = get_age_group(age)
        contra = check_age_contraindications(drug_a, age_group)
        if contra:
            return contra
        if drug_b:
            contra_b = check_age_contraindications(drug_b, age_group)
            if contra_b:
                return contra_b

    # Base prediction
    result = _base_gnn_predict(drug_a, drug_b)

    # Age adjustment
    if age:
        result = adjust_for_age(result, age, weight_kg)

    return result


def adjust_for_labs(gnn_result, labs):
    """
    Dynamic risk adjustment based on patient lab results.
    If creatinine is elevated, escalate MODERATE to HIGH_RISK.
    """
    result = dict(gnn_result)
    if labs and labs.get("creatinine", 0) > 1.5:
        if result.get("risk") == "MODERATE":
            result["risk"] = "HIGH_RISK"
            result["reason"] = "Elevated creatinine + drug interaction"
        elif result.get("risk") == "DANGER":
            result["reason"] = "Elevated creatinine worsens this interaction"
    return result