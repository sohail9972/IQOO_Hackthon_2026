# prescription_verifier.py
# Regex-based verification layer for LLM-extracted drug names.
# Sits BETWEEN the LLM OCR and the normalization step.

import re

# ============================================================
# KNOWN DRUG NAME PATTERNS
# ============================================================
# Patterns for Indian brand names
DRUG_PATTERNS = [
    # Indian brand suffixes
    r'.*-CV$', r'.*-SP$', r'.*-D$', r'.*-DS$', r'.*-XR$', r'.*-SR$', r'.*-CR$',
    r'.*-AV$', r'.*-AR$', r'.*-OD$', r'.*-BD$',
    # Common prefixes
    r'^Dexa.*', r'^Amox.*', r'^Azith.*', r'^Ceft.*', r'^Cefp.*',
    r'^Panto.*', r'^Ome.*', r'^Rabe.*', r'^Esome.*',
    # Specific drugs from your test cases
    r'^Baclofen$', r'^Baclofe$',  # Allow slight misreads
    r'^Ecosprin.*', r'^Ecospon.*',
    r'^Shelcal.*', r'^Nurokind.*', r'^Flupentixol.*',
    r'^Paracetamol$', r'^Ibuprofen$', r'^Aspirin$', r'^Warfarin$',
    r'^Metformin$', r'^Aceclofenac$', r'^Diclofenac$',
    r'^Cetirizine$', r'^Phenylephrine$', r'^Chymotrypsin$',
    r'^Cefpodoxime$', r'^Clavulanic.*', r'^Serratiopeptidase$',
    r'^Guaifenesin$', r'^Amoxicillin$', r'^Ascorbic.*', r'^Cholecalciferol$',
    # Template prescription drugs
    r'^Expectorant$', r'^Anti-biotic$', r'^Anti_biotic$',
    r'^Vitamin [A-Z]$', r'^Vitamin [A-Z][0-9]*$',
]

# Generic drug name pattern (alphanumeric with hyphens)
GENERIC_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9\-_]{2,25}$')

# Dosage patterns
DOSAGE_PATTERN = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*(mg|ml|mcg|g|IU|tabs?|caps?|tablet)\b',
    re.IGNORECASE
)

# Frequency patterns (Indian prescription format)
FREQUENCY_PATTERN = re.compile(
    r'\b(\d-\d-\d|\d-\d|\d\+|OD|BD|TDS|QID|SOS|HS|STAT)\b',
    re.IGNORECASE
)


def is_valid_drug_name(name):
    """
    Check if a string looks like a valid drug name using regex patterns.
    Returns (is_valid, reason).
    """
    name = name.strip()

    if len(name) < 3:
        return False, "Name too short"
    if len(name) > 30:
        return False, "Name too long"

    # Check against known patterns
    for pattern in DRUG_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True, f"Matches known drug pattern"

    # Check generic pattern
    if GENERIC_PATTERN.match(name):
        return True, "Matches generic drug pattern"

    return False, "No matching drug name pattern"


def extract_dosage(text):
    """Extract dosage from text."""
    match = DOSAGE_PATTERN.search(text)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return None


def extract_frequency(text):
    """Extract frequency from text."""
    match = FREQUENCY_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def cross_validate_drugs(llm_drugs, raw_ocr_text):
    """
    Cross-validate LLM-extracted drug names against raw OCR text.

    Args:
        llm_drugs: list of dicts from LLM: [{"name": "...", "dose": "...", "freq": "..."}]
        raw_ocr_text: full raw text from the model

    Returns:
        list of dicts with verification status (GREEN/YELLOW/RED)
    """
    verified = []

    for drug in llm_drugs:
        name = drug.get("name", "").strip()
        if not name:
            continue

        # Pattern check
        pattern_valid, pattern_reason = is_valid_drug_name(name)

        # Presence check in raw text
        present_in_raw = name.lower() in raw_ocr_text.lower()

        # Cross-validate dosage from raw text
        extracted_dose = drug.get("dose") or extract_dosage(raw_ocr_text) or ""

        # Cross-validate frequency from raw text
        extracted_freq = drug.get("freq") or extract_frequency(raw_ocr_text) or ""

        # Determine confidence
        if pattern_valid and present_in_raw:
            status = "GREEN"
            confidence = "HIGH"
            reason = "LLM + regex agree"
        elif pattern_valid or present_in_raw:
            status = "YELLOW"
            confidence = "MEDIUM"
            reason = pattern_reason if pattern_valid else "Found in text only"
        else:
            status = "RED"
            confidence = "LOW"
            reason = "No pattern match, not in raw text"

        verified.append({
            "name": name,
            "dose": extracted_dose,
            "freq": extracted_freq,
            "status": status,
            "confidence": confidence,
            "reason": reason,
            "pattern_valid": pattern_valid,
            "present_in_raw": present_in_raw,
        })

    return verified


def display_verification(verified_drugs):
    """Pretty-print verification results."""
    print("\n" + "=" * 60)
    print("PRESCRIPTION VERIFICATION RESULTS")
    print("=" * 60)

    icons = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "❌"}

    for drug in verified_drugs:
        icon = icons[drug["status"]]
        print(f"{icon} {drug['name']:<22} | {drug['dose'] or 'N/A':<10} | "
              f"{drug['freq'] or 'N/A':<8} | {drug['confidence']}")
        print(f"   └─ {drug['reason']}")

    print("=" * 60)

    green = sum(1 for d in verified_drugs if d["status"] == "GREEN")
    yellow = sum(1 for d in verified_drugs if d["status"] == "YELLOW")
    red = sum(1 for d in verified_drugs if d["status"] == "RED")

    print(f"Summary: {green} high-confidence, {yellow} need confirmation, {red} flagged")
    print("=" * 60 + "\n")

    return {"green": green, "yellow": yellow, "red": red}


def get_high_confidence_drugs(verified_drugs):
    """Return only GREEN drugs (for auto-proceeding)."""
    return [d for d in verified_drugs if d["status"] == "GREEN"]


def get_uncertain_drugs(verified_drugs):
    """Return YELLOW + RED drugs (for user confirmation)."""
    return [d for d in verified_drugs if d["status"] in ["YELLOW", "RED"]]