# Telugu Emergency Guidance Specification

## 1. Overview
During severe weather and flood crises in Andhra Pradesh and Telangana, timely and culturally appropriate guidance in Telugu (తెలుగు) is critical for citizen survival.

## 2. Required Contextual Guidance Catalog
The Citizen App integrates the official Telugu safety advisories across 5 primary disaster scenarios:

| Situation | Telugu Title | Telugu Message | English Translation |
|---|---|---|---|
| **FLOOD** | వరద హెచ్చరిక | "వరద పరిస్థితి ఉంది. వెంటనే ఎత్తైన మరియు సురక్షితమైన ప్రదేశానికి వెళ్లండి. నీటిలో నడవకండి." | Severe flood situation active. Immediately move to high ground and avoid walking through floodwaters. |
| **TRAPPED** | చిక్కుకుపోయిన వారి సమాచారం | "మీరు చిక్కుకుపోయినట్లయితే భయపడకండి. మీ లొకేషన్ పంపబడింది. సహాయం వచ్చే వరకు సురక్షితంగా ఉండండి." | Do not panic if you are trapped. Your GPS distress coordinates have been received. Stay safe until rescue arrives. |
| **MEDICAL** | వైద్య అత్యవసర సహాయం | "వైద్య సహాయం అవసరం అని గుర్తించబడింది. అత్యవసర బృందం సమాచారం అందుకుంది." | Medical emergency identified. Disaster emergency response team notified. |
| **HEAVY RAIN** | భారీ వర్ష సూచన | "భారీ వర్ష సూచన ఉంది. బయటకు వెళ్లకండి, విద్యుత్ స్తంభాలకు దూరంగా ఉండండి." | Heavy rainfall advisory in effect. Stay indoors and avoid electrical poles and fallen wires. |
| **EVACUATION** | తక్షణ తరలింపు ఆదేశం | "వెంటనే సురక్షిత ప్రాంతానికి లేదా సహాయ శిబిరానికి తరలి వెళ్ళండి." | Evacuate immediately to the designated safe zone or relief shelter. |

## 3. Language Switcher & Localization Architecture
- **Supported Locales**: English (\`en\`), Telugu (\`te\`), Hindi (\`hi\`). Default locale: \`te\` (Telugu).
- **Global Context**: \`LanguageContext.tsx\` stores language choice in \`localStorage\` (\`disasterguard_language_pref\`).
- **LanguageSelector Component**: Accessible 3D segmented button group with clear native language labels (\`తెలుగు\`, \`English\`, \`हिन्दी\`).
- **Context-Aware Triggering**: \`ActiveSOSQueueCard\` automatically inspects triage results and message content to display the most urgent Telugu advisory first.
- **Telugu Voice STT**: Speech recorded in Telugu is transcribed, displayed with Telugu script in both citizen app and command centre, and streamed as audio.
