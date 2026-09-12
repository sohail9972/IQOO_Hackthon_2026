# translator.py
# OFFLINE translation for medical warnings.
# No internet required. No API keys. 100% reliable.
# Drug names stay in English (universal medical convention).

# Common phrases used in SLM-generated warnings
PHRASES = {
    "ta": {
        "call your doctor immediately": "உடனே உங்கள் மருத்துவரை அணுகவும்",
        "call their doctor immediately": "உடனே அவர்களின் மருத்துவரை அணுகவும்",
        "contact your doctor": "உங்கள் மருத்துவரை தொடர்பு கொள்ளுங்கள்",
        "do not take": "எடுக்க வேண்டாம்",
        "do not give": "கொடுக்க வேண்டாம்",
        "high risk": "அதிக ஆபத்து",
        "danger": "ஆபத்து",
        "bleeding risk": "இரத்தப்போக்கு ஆபத்து",
        "increased bleeding risk": "அதிகரித்த இரத்தப்போக்கு ஆபத்து",
        "liver damage": "கல்லீரல் பாதிப்பு",
        "kidney function": "சிறுநீரக செயல்பாடு",
        "decreased renal function": "குறைந்த சிறுநீரக செயல்பாடு",
        "respiratory depression": "சுவாச தளர்ச்சி",
        "adverse effect": "பக்க விளைவு",
        "elderly patients": "முதிய நோயாளிகள்",
        "children": "குழந்தைகள்",
        "infants": "கைக்குழந்தைகள்",
        "safe": "பாதுகாப்பானது",
        "unsafe": "பாதுகாப்பற்றது",
        "take as prescribed": "மருத்துவர் சொன்னபடி எடுத்துக்கொள்ளுங்கள்",
        "monitor": "கண்காணிக்கவும்",
        "for": "க்கு",
    },
    "hi": {
        "call your doctor immediately": "तुरंत अपने डॉक्टर को बुलाएं",
        "call their doctor immediately": "तुरंत उनके डॉक्टर को बुलाएं",
        "contact your doctor": "अपने डॉक्टर से संपर्क करें",
        "do not take": "न लें",
        "do not give": "न दें",
        "high risk": "उच्च जोखिम",
        "danger": "खतरा",
        "bleeding risk": "रक्तस्राव का खतरा",
        "increased bleeding risk": "बढ़ा हुआ रक्तस्राव का खतरा",
        "liver damage": "लीवर की क्षति",
        "kidney function": "गुर्दे की कार्यप्रणाली",
        "decreased renal function": "कम गुर्दे की कार्यप्रणाली",
        "respiratory depression": "श्वसन अवसाद",
        "adverse effect": "प्रतिकूल प्रभाव",
        "elderly patients": "बुजुर्ग रोगी",
        "children": "बच्चे",
        "infants": "शिशु",
        "safe": "सुरक्षित",
        "unsafe": "असुरक्षित",
        "take as prescribed": "डॉक्टर के अनुसार लें",
        "monitor": "निगरानी करें",
        "for": "के लिए",
    },
    "te": {
        "call your doctor immediately": "వెంటనే మీ వైద్యుడిని సంప్రదించండి",
        "do not take": "తీసుకోవద్దు",
        "high risk": "అధిక ప్రమాదం",
        "danger": "ప్రమాదం",
        "bleeding risk": "రక్తస్రావం ప్రమాదం",
        "liver damage": "కాలేయ నష్టం",
        "kidney function": "మూత్రపిండాల పనితీరు",
        "adverse effect": "ప్రతికూల ప్రభావం",
        "elderly patients": "వృద్ధ రోగులు",
        "children": "పిల్లలు",
        "safe": "సురక్షితం",
    },
    "ml": {
        "call your doctor immediately": "ഉടൻ നിങ്ങളുടെ ഡോക്ടറെ വിളിക്കുക",
        "do not take": "കഴിക്കരുത്",
        "high risk": "ഉയർന്ന അപകടം",
        "danger": "അപകടം",
        "bleeding risk": "രക്തസ്രാവ സാധ്യത",
        "adverse effect": "പ്രതികൂല ഫലം",
        "elderly patients": "വൃദ്ധ രോഗികൾ",
        "children": "കുട്ടികൾ",
        "safe": "സുരക്ഷിതം",
    },
    "kn": {
        "call your doctor immediately": "ತಕ್ಷಣ ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "do not take": "ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ",
        "high risk": "ಹೆಚ್ಚಿನ ಅಪಾಯ",
        "danger": "ಅಪಾಯ",
        "bleeding risk": "ರಕ್ತಸ್ರಾವದ ಅಪಾಯ",
        "adverse effect": "ಪ್ರತಿಕೂಲ ಪರಿಣಾಮ",
        "elderly patients": "ವೃದ್ಧ ರೋಗಿಗಳು",
        "children": "ಮಕ್ಕಳು",
        "safe": "ಸುರಕ್ಷಿತ",
    },
}


def translate_to_indic(text, lang_code):
    """Offline phrase-level translation. Preserves English drug names."""
    if lang_code == "en" or not text:
        return text
    if lang_code not in PHRASES:
        return text

    result = text
    # Replace longer phrases first (most specific → least specific)
    phrases = sorted(PHRASES[lang_code].items(), key=lambda x: -len(x[0]))
    for eng, native in phrases:
        # Case-insensitive replace
        import re
        result = re.sub(re.escape(eng), native, result, flags=re.IGNORECASE)

    return result