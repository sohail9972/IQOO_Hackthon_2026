package com.pharmagraph.app

import java.util.Locale

class WarningTemplateProvider {

    data class Template(
        val languageName: String,
        val locale: Locale,
        val dangerPrefix: String,
        val warningPrefix: String,
        val safeMessage: String,
        val interactionText: String,
        val actionText: String
    )

    private val templates = mapOf(
        "English" to Template("English", Locale.ENGLISH, "DANGER", "WARNING", "Safe to use.", "Interacting drugs:", "Action:"),
        "Tamil" to Template("Tamil", Locale("ta", "IN"), "ஆபத்து", "எச்சரிக்கை", "பாதுகாப்பானது.", "தொடர்புடைய மருந்துகள்:", "நடவடிக்கை:"),
        "Hindi" to Template("Hindi", Locale("hi", "IN"), "खतरा", "चेतावनी", "सुरक्षित है।", "परस्पर क्रिया करने वाली दवाएं:", "कार्रवाई:"),
        "Telugu" to Template("Telugu", Locale("te", "IN"), "ప్రమాదం", "హెచ్చరిక", "సురక్షితం.", "ప్రభావితం చేసే మందులు:", "చర్య:"),
        "Malayalam" to Template("Malayalam", Locale("ml", "IN"), "അപകടം", "മുന്നറിയിപ്പ്", "സുരക്ഷിതമാണ്.", "പ്രതിപ്രവർത്തിക്കുന്ന മരുന്നുകൾ:", "നടപടി:"),
        "Kannada" to Template("Kannada", Locale("kn", "IN"), "ಅಪಾಯ", "ಎಚ್ಚರಿಕೆ", "ಸುರಕ್ಷಿತವಾಗಿದೆ.", "ಪರಸ್ಪರ ಪರಿಣಾಮ ಬೀರುವ ಔಷಧಿಗಳು:", "ಕ್ರಮ:"),
        "Bengali" to Template("Bengali", Locale("bn", "IN"), "বিপদ", "সতর্কবার্তা", "নিরাপদ।", "পারস্পরিক ক্রিয়াশীল ওষুধ:", "পদক্ষেপ:"),
        "Marathi" to Template("Marathi", Locale("mr", "IN"), "धोका", "इशारा", "सुरक्षित आहे.", "परस्पर क्रिया करणारी औषधे:", "कृती:"),
        "Gujarati" to Template("Gujarati", Locale("gu", "IN"), "જોખમ", "ચેતવણી", "સુરક્ષિત છે.", "પરસ્પર અસર કરતી દવાઓ:", "પગલું:"),
        "Punjabi" to Template("Punjabi", Locale("pa", "IN"), "ਖ਼ਤਰਾ", "ਚੇਤਾਵਨੀ", "ਸੁਰੱਖਿਅਤ ਹੈ।", "ਆਪਸੀ ਪ੍ਰਭਾਵ ਪਾਉਣ ਵਾਲੀਆਂ ਦਵਾਈਆਂ:", "ਕਾਰਵਾਈ:"),
        "Odia" to Template("Odia", Locale("or", "IN"), "ବିପଦ", "ସତର୍କତା", "ସୁରକ୍ଷିତ।", "ପ୍ରତିକ୍ରିୟା କରୁଥିବା ଔଷଧ:", "ପଦକ୍ଷેପ:"),
        "Assamese" to Template("Assamese", Locale("as", "IN"), "বিপদ", "সতর্কবাণী", "নিৰাপদ।", "পাৰস্পৰিক ক্ৰিয়া কৰা ঔষধ:", "ব্যৱস্থা:"),
        "Urdu" to Template("Urdu", Locale("ur", "PK"), "خطرہ", "انتباہ", "محفوظ ہے۔", "باہمی اثر کرنے والی ادویات:", "کارروائی:")
    )

    fun getLanguages(): List<String> = templates.keys.toList().sorted()

    fun getTemplate(languageName: String): Template = templates[languageName] ?: templates["English"]!!

    fun formatWarning(languageName: String, result: LlamaService.AnalysisResult): String {
        val template = getTemplate(languageName)
        val prefix = when (result.riskLevel.uppercase()) {
            "DANGER" -> template.dangerPrefix
            "WARNING" -> template.warningPrefix
            "SAFE" -> return template.safeMessage
            else -> result.riskLevel // Fallback for unexpected risk levels
        }
        
        return "$prefix. ${template.interactionText} ${result.interactingDrugs}. ${result.explanation}. ${template.actionText} ${result.recommendedAction}"
    }
}
