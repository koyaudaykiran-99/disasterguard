export type EmergencySituationType =
  | 'FLOOD'
  | 'TRAPPED'
  | 'MEDICAL'
  | 'HEAVY_RAIN'
  | 'EVACUATION';

export type LanguageCode = 'te' | 'en' | 'hi';

export interface EmergencyGuidanceEntry {
  situation: EmergencySituationType;
  title: Record<LanguageCode, string>;
  message: Record<LanguageCode, string>;
  priority: 'CRITICAL' | 'HIGH' | 'URGENT';
  actionIcon: string;
  recommendedAction: Record<LanguageCode, string>;
}

export const EMERGENCY_GUIDANCE_CATALOG: Record<EmergencySituationType, EmergencyGuidanceEntry> = {
  FLOOD: {
    situation: 'FLOOD',
    title: {
      te: 'వరద హెచ్చరిక',
      en: 'Flood Threat Alert',
      hi: 'बाढ़ चेतावनी',
    },
    message: {
      te: 'వరద పరిస్థితి ఉంది. వెంటనే ఎత్తైన మరియు సురక్షితమైన ప్రదేశానికి వెళ్లండి. నీటిలో నడవకండి.',
      en: 'Severe flood situation active. Immediately move to high ground and avoid walking through floodwaters.',
      hi: 'बाढ़ की स्थिति है। तुरंत ऊंचे और सुरक्षित स्थान पर जाएं। बहते पानी में न चलें।',
    },
    priority: 'CRITICAL',
    actionIcon: 'Waves',
    recommendedAction: {
      te: 'ఎత్తైన భవనాలు లేదా గుర్తింపు పొందిన పునరావాస కేంద్రాలకు చేరుకోండి.',
      en: 'Seek elevated structures or designated relief shelters.',
      hi: 'ऊंची इमारतों या नामित राहत शिविरों में जाएं।',
    },
  },
  TRAPPED: {
    situation: 'TRAPPED',
    title: {
      te: 'చిక్కుకుపోయిన వారి సమాచారం',
      en: 'Trapped Person Protocol',
      hi: 'फंसे हुए व्यक्ति की सूचना',
    },
    message: {
      te: 'మీరు చిక్కుకుపోయినట్లయితే భయపడకండి. మీ లొకేషన్ పంపబడింది. సహాయం వచ్చే వరకు సురక్షితంగా ఉండండి.',
      en: 'Do not panic if you are trapped. Your GPS distress coordinates have been received. Stay safe until rescue arrives.',
      hi: 'यदि आप फंसे हुए हैं तो घबराएं नहीं। आपकी लोकेशन प्राप्त हो गई है। बचाव दल आने तक सुरक्षित रहें।',
    },
    priority: 'CRITICAL',
    actionIcon: 'Users',
    recommendedAction: {
      te: 'ఫోన్ బ్యాటరీ ఆదా చేయండి, శబ్ద సంకేతాలు ఇవ్వండి లేదా రంగు వస్త్రం ప్రదర్శించండి.',
      en: 'Conserve device battery, make sound signals, or display a bright cloth.',
      hi: 'फोन की बैटरी बचाएं, आवाज के संकेत दें या चमकीला कपड़ा दिखाएं।',
    },
  },
  MEDICAL: {
    situation: 'MEDICAL',
    title: {
      te: 'వైద్య అత్యవసర సహాయం',
      en: 'Medical Emergency Protocol',
      hi: 'चिकित्सा आपातकाल',
    },
    message: {
      te: 'వైద్య సహాయం అవసరం అని గుర్తించబడింది. అత్యవసర బృందం సమాచారం అందుకుంది.',
      en: 'Medical emergency identified. Disaster emergency response team notified.',
      hi: 'चिकित्सा आपातकाल की पहचान की गई है। आपातकालीन टीम को सूचित कर दिया गया है।',
    },
    priority: 'CRITICAL',
    actionIcon: 'HeartPulse',
    recommendedAction: {
      te: 'గాయపడిన వారిని పొడి మరియు సురక్షిత స్థలంలో ఉంచండి, రక్తస్రావం ఆపడానికి ఒత్తిడి ఉంచండి.',
      en: 'Keep patient warm and dry; apply direct pressure to any bleeding wounds.',
      hi: 'मरीज को सूखे व सुरक्षित स्थान पर रखें, रक्तस्राव रोकने के लिए दबाव बनाएं।',
    },
  },
  HEAVY_RAIN: {
    situation: 'HEAVY_RAIN',
    title: {
      te: 'భారీ వర్ష సూచన',
      en: 'Heavy Rainfall Warning',
      hi: 'भारी बारिश की चेतावनी',
    },
    message: {
      te: 'భారీ వర్ష సూచన ఉంది. బయటకు వెళ్లకండి, విద్యుత్ స్తంభాలకు దూరంగా ఉండండి.',
      en: 'Heavy rainfall advisory in effect. Stay indoors and avoid electrical poles and fallen wires.',
      hi: 'भारी बारिश की चेतावनी। घर के अंदर रहें और बिजली के खंभों से दूर रहें।',
    },
    priority: 'HIGH',
    actionIcon: 'CloudRain',
    recommendedAction: {
      te: 'విద్యుత్ పరికరాలు ఆపివేయండి, పవర్ బ్యాంక్ మరియు తాగునీరు సిద్ధంగా ఉంచుకోండి.',
      en: 'Switch off main electrical breakers; keep power banks and fresh drinking water ready.',
      hi: 'मेन बिजली का स्विच बंद करें; पावर बैंक और पीने का पानी तैयार रखें।',
    },
  },
  EVACUATION: {
    situation: 'EVACUATION',
    title: {
      te: 'తక్షణ తరలింపు ఆదేశం',
      en: 'Immediate Evacuation Order',
      hi: 'तत्काल निकासी आदेश',
    },
    message: {
      te: 'వెంటనే సురక్షిత ప్రాంతానికి లేదా సహాయ శిబిరానికి తరలి వెళ్ళండి.',
      en: 'Evacuate immediately to the designated safe zone or relief shelter.',
      hi: 'तुरंत निर्दिष्ट सुरक्षित क्षेत्र या राहत शिविर में जाएं।',
    },
    priority: 'CRITICAL',
    actionIcon: 'ShieldAlert',
    recommendedAction: {
      te: 'ముఖ్యమైన పత్రాలు, మందులు మరియు ఆహారం తీసుకొని సమీప సహాయ శిబిరానికి వెళ్లండి.',
      en: 'Take identification documents, essential medications, and proceed via elevated corridors.',
      hi: 'आवश्यक दस्तावेज व दवाइयां लेकर ऊंचे सुरक्षित रास्तों से शिविर की ओर जाएं।',
    },
  },
};

const STORAGE_KEY = 'disasterguard_guidance_cache_v1';

class EmergencyGuidanceService {
  private cache: Record<string, any> = {};

  constructor() {
    this.loadCache();
  }

  private loadCache() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        this.cache = JSON.parse(raw);
      }
    } catch (e) {
      console.warn('[EmergencyGuidanceService] Cache read error:', e);
    }
  }

  public getGuidanceForSituation(situation: EmergencySituationType, lang: LanguageCode = 'te'): EmergencyGuidanceEntry {
    return EMERGENCY_GUIDANCE_CATALOG[situation] || EMERGENCY_GUIDANCE_CATALOG.FLOOD;
  }

  public getMessage(situation: EmergencySituationType, lang: LanguageCode = 'te'): string {
    const entry = EMERGENCY_GUIDANCE_CATALOG[situation] || EMERGENCY_GUIDANCE_CATALOG.FLOOD;
    return entry.message[lang] || entry.message.te;
  }

  public getAction(situation: EmergencySituationType, lang: LanguageCode = 'te'): string {
    const entry = EMERGENCY_GUIDANCE_CATALOG[situation] || EMERGENCY_GUIDANCE_CATALOG.FLOOD;
    return entry.recommendedAction[lang] || entry.recommendedAction.te;
  }

  public cacheRemoteGuidance(sosId: number, data: any) {
    try {
      this.cache['sos_' + sosId] = {
        data,
        timestamp: Date.now(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.cache));
    } catch (e) {
      console.warn('[EmergencyGuidanceService] Cache write error:', e);
    }
  }

  public getCachedRemoteGuidance(sosId: number) {
    return this.cache['sos_' + sosId]?.data || null;
  }
}

export const emergencyGuidanceService = new EmergencyGuidanceService();