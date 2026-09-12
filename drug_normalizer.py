# drug_normalizer.py
BRAND_TO_GENERIC = {
    # From the template prescription
    "expectorant": {"generic": ["guaifenesin"], "class": "Expectorant"},
    "paracetamol": {"generic": ["paracetamol"], "class": "Analgesic"},
    "anti-biotic": {"generic": ["amoxicillin"], "class": "Antibiotic"},
    "vitamin c": {"generic": ["ascorbic acid"], "class": "Vitamin"},
    "vitamin d": {"generic": ["cholecalciferol"], "class": "Vitamin"},
    
    # Common drugs
    "warfarin": {"generic": ["warfarin"], "class": "Anticoagulant"},
    "aspirin": {"generic": ["aspirin"], "class": "NSAID"},
    "ibuprofen": {"generic": ["ibuprofen"], "class": "NSAID"},
}

def normalize_drug(brand_name):
    key = brand_name.lower().strip()
    if key in BRAND_TO_GENERIC:
        return BRAND_TO_GENERIC[key]
    for brand, data in BRAND_TO_GENERIC.items():
        if brand in key:
            return data
    return {"generic": [key], "class": "Unknown"}

def expand_to_generics(drug_list):
    """Expand list of drug dicts or strings to flat list of generics."""
    generics = []
    for drug in drug_list:
        name = drug["name"] if isinstance(drug, dict) else drug
        norm = normalize_drug(name)
        for g in norm["generic"]:
            generics.append(g)
    return list(set(generics))