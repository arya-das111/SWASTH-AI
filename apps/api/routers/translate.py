from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/translate",
    tags=["Multilingual Support"]
)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en-IN"
    target_lang: str = "hi-IN"

# Dictionary of pre-translated UI terms for Hindi and Tamil fallbacks
TRANSLATION_DICT = {
    "hi-IN": {
        "Lucknow Command Oversight Panel": "लखनऊ कमांड ओवरसाइट पैनल",
        "Lucknow District Healthcare Command Center": "लखनऊ जिला स्वास्थ्य सेवा कमांड सेंटर",
        "Redistribution Recommendations": "पुनर्वितरण अनुशंसाएँ",
        "Oversight Scores": "ओवरसाइट स्कोर",
        "Oversight Scores Leaderboard": "ओवरसाइट स्कोर लीडरबोर्ड",
        "Active District Alerts Queue": "सक्रिय जिला अलर्ट कतार",
        "Medicine Inventory Ledger": "दवा सूची बही",
        "Ward Bed Management": "वार्ड बेड प्रबंधन",
        "Roster Check-In / Out": "रोस्टर चेक-इन / आउट",
        "Diagnostic Audit Checklist": "नैदानिक ऑडिट चेकलिस्ट",
        "Staff Attendance": "कर्मचारी उपस्थिति",
        "Bed Occupancy": "बेड अधिभोग",
        "Inventory Health": "इन्वेंटरी स्वास्थ्य",
        "OPD Consultations": "ओपीडी परामर्श",
        "IPD Admissions": "आईपीडी प्रवेश",
        "Check In": "चेक इन",
        "Check Out": "चेक आउट",
        "Diagnostics Audit": "नैदानिक ऑडिट",
        "Log Out": "लॉग आउट",
        "Online Mode": "ऑनलाइन मोड",
        "Offline Mode": "ऑफ़लाइन मोड",
        "Total expected daily patients": "कुल अपेक्षित दैनिक रोगी",
        "Oversight Score": "ओवरसाइट स्कोर",
        "Stock Reliability": "स्टॉक विश्वसनीयता",
        "Attendance rate": "उपस्थिति दर",
        "Bed Turnover": "बेड टर्नओवर",
        "Diagnostics Compliance": "नैदानिक अनुपालन",
        "District aggregate": "जिला कुल",
        "Available Beds": "उपलब्ध बिस्तर",
        "Coverage Gaps": "कवरेज अंतराल",
        "Active Alerts": "सक्रिय अलर्ट",
        "Why flagged?": "क्यों ध्वजांकित किया गया?"
    },
    "ta-IN": {
        "Lucknow Command Oversight Panel": "லக்னோ கட்டளை கண்காணிப்பு குழு",
        "Lucknow District Healthcare Command Center": "லக்னோ மாவட்ட சுகாதார கட்டளை மையம்",
        "Redistribution Recommendations": "மறுபகிர்வு பரிந்துரைகள்",
        "Oversight Scores": "கண்காணிப்பு மதிப்பெண்கள்",
        "Oversight Scores Leaderboard": "கண்காணிப்பு தரவரிசை",
        "Active District Alerts Queue": "செயலில் உள்ள மாவட்ட எச்சரிக்கைகள்",
        "Medicine Inventory Ledger": "மருந்து இருப்புப் பதிவேடு",
        "Ward Bed Management": "வார்டு படுக்கை மேலாண்மை",
        "Roster Check-In / Out": "பணிப்பதிவு வருகை / வெளியேற்றம்",
        "Diagnostic Audit Checklist": "கண்டறிதல் தணிக்கை சரிபார்ப்பு பட்டியல்",
        "Staff Attendance": "ஊழியர் வருகை",
        "Bed Occupancy": "படுக்கை இருப்பு",
        "Inventory Health": "இருப்பு நலம்",
        "OPD Consultations": "வெளிநோயாளி ஆலோசனை",
        "IPD Admissions": "உள்நோயாளி அனுமதி",
        "Check In": "வருகை பதிவு",
        "Check Out": "வெளியேற்ற பதிவு",
        "Diagnostics Audit": "கண்டறிதல் தணிக்கை",
        "Log Out": "வெளியேறு",
        "Online Mode": "ஆன்லைன் பயன்முறை",
        "Offline Mode": "ஆஃப்லைன் பயன்முறை",
        "Total expected daily patients": "தினசரி எதிர்பார்க்கப்படும் நோயாளிகள்",
        "Oversight Score": "கண்காணிப்பு மதிப்பெண்",
        "Stock Reliability": "இருப்பு நம்பகத்தன்மை",
        "Attendance rate": "வருகை விகிதம்",
        "Bed Turnover": "படுக்கை சுழற்சி",
        "Diagnostics Compliance": "கண்டறிதல் இணக்கம்",
        "District aggregate": "மாவட்ட மொத்தம்",
        "Available Beds": "கிடைக்கக்கூடிய படுக்கைகள்",
        "Coverage Gaps": "இருப்பு இடைவெளி",
        "Active Alerts": "செயலில் உள்ள எச்சரிக்கைகள்",
        "Why flagged?": "ஏன் குறிக்கப்பட்டது?"
    }
}

@router.post("")
async def translate_text(
    payload: TranslationRequest,
    current_user: models.User = Depends(auth.get_current_user)
):
    text = payload.text
    source_lang = payload.source_lang
    target_lang = payload.target_lang
    
    # Return original text if target is English (default base) or matches source
    if target_lang == "en-IN" or source_lang == target_lang:
        return {"translated_text": text}
        
    # Check if pre-translated static UI term exists
    lang_dict = TRANSLATION_DICT.get(target_lang)
    if lang_dict and text in lang_dict:
        return {"translated_text": lang_dict[text]}
        
    # Try calling the Sarvam AI Translation API if key is present
    sarvam_key = os.environ.get("SARVAM_API_KEY")
    if sarvam_key:
        try:
            url = "https://api.sarvam.ai/translate"
            headers = {
                "api-subscription-key": sarvam_key,
                "Content-Type": "application/json"
            }
            body = {
                "input": text,
                "source_language_code": source_lang,
                "target_language_code": target_lang,
                "model": "sarvam-translate:v1"
            }
            
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=body, timeout=8.0)
                if res.status_code == 200:
                    data = res.json()
                    return {"translated_text": data.get("translated_text", text)}
        except Exception as e:
            # Fallback on connection errors
            pass
            
    # Mock Translation Fallback (Appends language specific indicators to text for demonstrative purposes)
    translated = text
    if target_lang == "hi-IN":
        translated = f"[Hindi] {text}"
    elif target_lang == "ta-IN":
        translated = f"[Tamil] {text}"
    elif target_lang == "te-IN":
        translated = f"[Telugu] {text}"
        
    return {"translated_text": translated}
