"""
AI-DisasterGuard — Explainable Message Generator & Multilingual Dictionary
Phase 5.4: Adaptive Alert Intelligence + Personalized Risk Communication
"""

from typing import Dict, Any, List, Optional
from ml.alerts import AlertCategory, AlertSeverity

# Controlled Multilingual Emergency Terminology Dictionary
EMERGENCY_DICTIONARY = {
    "en": {
        "WHAT": "WHAT",
        "WHERE": "WHERE",
        "WHEN": "WHEN",
        "WHY": "WHY",
        "WHAT_TO_DO": "WHAT TO DO",
        "CONFIDENCE": "CONFIDENCE",
        "SOURCE": "SOURCE",
        "OBSERVED": "OBSERVED",
        "PREDICTED": "PREDICTED",
        "RECOMMENDED": "RECOMMENDED",
        "FLOOD_WARNING": "Flood Warning",
        "CRITICAL_FLOOD_WARNING": "Critical Flood Warning",
        "FLOOD_WATCH": "Flood Watch",
        "WEATHER_ADVISORY": "Weather Advisory",
        "HEAVY_RAINFALL_WARNING": "Heavy Rainfall Warning",
        "EVACUATION_ADVISORY": "Evacuation Advisory",
        "EMERGENCY_SAFETY_ALERT": "Emergency Safety Alert",
        "SYSTEM_INFORMATION": "System Information",
        "ADVICE_AVOID_WATER": "Avoid entering or driving through floodwaters.",
        "ADVICE_HIGH_GROUND": "Be prepared to move to higher ground if advised by emergency officials.",
        "ADVICE_CHARGE_PHONE": "Keep your mobile phone charged and emergency lights ready.",
        "ADVICE_FOLLOW_OFFICIAL": "Follow instructions from authorized disaster management personnel.",
        "ADVICE_USE_SOS": "Use the Emergency SOS button immediately if you require urgent rescue.",
        "ADVICE_EVACUATION_MAY_BE_ADVISABLE": "Evacuation may be advisable. Follow instructions from authorized authorities.",
        "HONESTY_NOTE": "Predictive risk estimate. Acknowledging confirms receipt only (Acknowledged ≠ Safe)."
    },
    "te": {
        "WHAT": "ఏమిటి",
        "WHERE": "ఎక్కడ",
        "WHEN": "ఎప్పుడు",
        "WHY": "ఎందుకు",
        "WHAT_TO_DO": "చేయవలసిన పనులు",
        "CONFIDENCE": "విశ్వసనీయత",
        "SOURCE": "మూలం",
        "OBSERVED": "గమనించిన సమాచారం",
        "PREDICTED": "అంచనా వేసిన ముప్పు",
        "RECOMMENDED": "సిఫార్సు చేయబడిన రక్షణ చర్యలు",
        "FLOOD_WARNING": "వరద హెచ్చరిక",
        "CRITICAL_FLOOD_WARNING": "తీవ్రమైన వరద హెచ్చరిక",
        "FLOOD_WATCH": "వరద నిఘా సమాచారం",
        "WEATHER_ADVISORY": "వాతావరణ సూచన",
        "HEAVY_RAINFALL_WARNING": "భారీ వర్ష హెచ్చరిక",
        "EVACUATION_ADVISORY": "సురక్షిత ప్రాంతాలకు తరలింపు సలహా",
        "EMERGENCY_SAFETY_ALERT": "అత్యవసర భద్రతా హెచ్చరిక",
        "SYSTEM_INFORMATION": "వ్యవస్థ సమాచారం",
        "ADVICE_AVOID_WATER": "వరద నీటిలో నడవకండి లేదా వాహనాలు నడపకండి.",
        "ADVICE_HIGH_GROUND": "అధికారులు ఆదేశిస్తే వెంటనే ఎత్తైన ప్రదేశాలకు వెళ్లడానికి సిద్ధంగా ఉండండి.",
        "ADVICE_CHARGE_PHONE": "మీ మొబైల్ ఫోన్‌ను ఛార్జ్ చేసి ఎమర్జెన్సీ లైట్లను సిద్ధంగా ఉంచండి.",
        "ADVICE_FOLLOW_OFFICIAL": "విపత్తు నిర్వహణ అధికారుల ఆదేశాలను పాటించండి.",
        "ADVICE_USE_SOS": "మీకు తక్షణ రక్షణ అవసరమైతే వెంటనే ఎమర్జెన్సీ SOS బటన్ నొక్కండి.",
        "ADVICE_EVACUATION_MAY_BE_ADVISABLE": "సురక్షిత ప్రాంతాలకు వెళ్లడం మంచిది. అధికారిక సూచనలు పాటించండి.",
        "HONESTY_NOTE": "ఇది ముందస్తు అంచనా మాత్రమే. రసీదు నిర్ధారణ మాత్రమే (స్వీకరించడం ≠ సురక్షితం)."
    },
    "hi": {
        "WHAT": "क्या",
        "WHERE": "कहाँ",
        "WHEN": "कब",
        "WHY": "क्यों",
        "WHAT_TO_DO": "क्या करें",
        "CONFIDENCE": "विश्वसनीयता",
        "SOURCE": "स्रोत",
        "OBSERVED": "देखा गया",
        "PREDICTED": "पूर्वानुमानित",
        "RECOMMENDED": "सुझाव",
        "FLOOD_WARNING": "बाढ़ चेतावनी",
        "CRITICAL_FLOOD_WARNING": "गंभीर बाढ़ चेतावनी",
        "FLOOD_WATCH": "बाढ़ निगरानी",
        "WEATHER_ADVISORY": "मौसम सलाह",
        "HEAVY_RAINFALL_WARNING": "भारी वर्षा चेतावनी",
        "EVACUATION_ADVISORY": "सुरक्षित स्थान पर जाने की सलाह",
        "EMERGENCY_SAFETY_ALERT": "आपातकालीन सुरक्षा चेतावनी",
        "SYSTEM_INFORMATION": "सिस्टम जानकारी",
        "ADVICE_AVOID_WATER": "बाढ़ के पानी में जाने या वाहन चलाने से बचें।",
        "ADVICE_HIGH_GROUND": "यदि अधिकारी सलाह दें तो तुरंत ऊंचे स्थानों पर जाने के लिए तैयार रहें।",
        "ADVICE_CHARGE_PHONE": "अपना मोबाइल फोन चार्ज रखें और आपातकालीन लाइट तैयार रखें।",
        "ADVICE_FOLLOW_OFFICIAL": "अधिकृत आपदा प्रबंधन कर्मियों के निर्देशों का पालन करें।",
        "ADVICE_USE_SOS": "यदि आपको तत्काल सहायता चाहिए तो तुरंत आपातकालीन SOS बटन का उपयोग करें।",
        "ADVICE_EVACUATION_MAY_BE_ADVISABLE": "सुरक्षित स्थान पर जाना उचित हो सकता है। अधिकृत निर्देशों का पालन करें।",
        "HONESTY_NOTE": "यह पूर्वानुमानित जोखिम अनुमान है। पावती केवल प्राप्ति की पुष्टि करती है (स्वीकृत ≠ सुरक्षित)।"
    }
}

class MessageGenerator:
    """
    Generates explainable, 7-part structured emergency messages with controlled
    multilingual support and fallback safety.
    """

    @staticmethod
    def get_term(term_key: str, lang: str = "en") -> str:
        """Fetch localized term with guaranteed English fallback."""
        lang_dict = EMERGENCY_DICTIONARY.get(lang, EMERGENCY_DICTIONARY["en"])
        if term_key in lang_dict:
            return lang_dict[term_key]
        return EMERGENCY_DICTIONARY["en"].get(term_key, term_key)

    @staticmethod
    def generate_message(
        category: str,
        severity: str,
        location_name: str,
        peak_horizon: str,
        peak_risk: int,
        confidence_score: float,
        uncertainty_score: float,
        rationale: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Construct structured 7-element emergency communication payload.
        """
        lang = language.lower() if language.lower() in EMERGENCY_DICTIONARY else "en"
        terms = EMERGENCY_DICTIONARY[lang]

        cat_title = MessageGenerator.get_term(category, lang)

        # 1. WHAT
        what = f"{cat_title}: {severity} risk level ({peak_risk}/100)"

        # 2. WHERE
        where = location_name

        # 3. WHEN
        when = f"Projected peak at {peak_horizon} horizon"

        # 4. WHY
        why = rationale

        # 5. WHAT TO DO (Controlled actionable bullet points)
        instructions = [
            MessageGenerator.get_term("ADVICE_AVOID_WATER", lang),
            MessageGenerator.get_term("ADVICE_CHARGE_PHONE", lang),
            MessageGenerator.get_term("ADVICE_FOLLOW_OFFICIAL", lang)
        ]
        if severity in [AlertSeverity.CRITICAL.value, AlertSeverity.WARNING.value]:
            instructions.insert(1, MessageGenerator.get_term("ADVICE_HIGH_GROUND", lang))
            instructions.append(MessageGenerator.get_term("ADVICE_USE_SOS", lang))

        if category == AlertCategory.EVACUATION_ADVISORY.value:
            instructions.insert(0, MessageGenerator.get_term("ADVICE_EVACUATION_MAY_BE_ADVISABLE", lang))

        # 6. CONFIDENCE
        conf_level = "HIGH" if confidence_score >= 0.75 else ("MEDIUM" if confidence_score >= 0.50 else "LOW")
        confidence_str = (
            f"{conf_level} ({confidence_score * 100:.0f}%, uncertainty {uncertainty_score * 100:.0f}%)"
        )

        # 7. SOURCE
        source = "AI-DisasterGuard Predictive Multi-Horizon Early Warning Engine"

        # Full plain-text format
        full_text = (
            f"{terms['WHAT']}: {what}\n"
            f"{terms['WHERE']}: {where}\n"
            f"{terms['WHEN']}: {when}\n"
            f"{terms['WHY']}: {why}\n"
            f"{terms['WHAT_TO_DO']}:\n" + "\n".join(f"• {inst}" for inst in instructions) + "\n"
            f"{terms['CONFIDENCE']}: {confidence_str}\n"
            f"{terms['SOURCE']}: {source}"
        )

        return {
            "language": lang,
            "title": f"[{cat_title}] {severity} - {location_name}",
            "headline": what,
            "full_message": full_text,
            "elements": {
                "what": what,
                "where": where,
                "when": when,
                "why": why,
                "what_to_do": instructions,
                "confidence": confidence_str,
                "source": source
            },
            "evidence_distinction": {
                "observed": f"Observed local sensor telemetry and radar rain accumulation.",
                "predicted": f"Predicted peak risk score {peak_risk}/100 at {peak_horizon}.",
                "recommended": "Protective guidance formulated for citizen decision-support."
            },
            "honesty_disclaimer": MessageGenerator.get_term("HONESTY_NOTE", lang)
        }
