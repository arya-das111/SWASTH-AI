import React, { useState, useEffect } from 'react';
import { 
  Shield, Activity, BarChart2, Landmark, AlertTriangle, 
  Clipboard, CheckCircle2, AlertOctagon, 
  Users, Check, RefreshCw, Eye, TrendingUp, X, ThumbsUp, ThumbsDown,
  LogOut
} from 'lucide-react';

const API_BASE = window.location.hostname.includes('vercel.app')
  ? 'https://api-gamma-pearl.vercel.app/api/v1'
  : 'http://localhost:8000/api/v1';

// Static translation dictionary to enable instant hot-swapping
const STATIC_DICT: any = {
  "en-IN": {},
  "hi-IN": {
    "Lucknow Command Oversight Panel": "लखनऊ कमांड ओवरसाइट पैनल",
    "Uttar Pradesh Healthcare Dashboard": "उत्तर प्रदेश स्वास्थ्य सेवा डैशबोर्ड",
    "State Analytics Portal": "राज्य विश्लेषण पोर्टल",
    "25 Active Facilities (20 PHCs, 5 CHCs)": "25 सक्रिय सुविधाएं (20 पीएचसी, 5 सीएचसी)",
    "Refresh Live Metrics": "लाइव मेट्रिक्स रीफ्रेश करें",
    "State Level": "राज्य स्तर",
    "Lucknow District": "लखनऊ जिला",
    "Stock Heatmap": "स्टॉक हीटमैप",
    "Redistributions": "पुनर्वितरण",
    "Beds & Redirects": "बिस्तर और पुनर्निर्देशन",
    "Attendance & Gaps": "उपस्थिति और अंतराल",
    "FDSI Compliance": "एफडीएसआई अनुपालन",
    "Early Warnings": "प्रारंभिक चेतावनी",
    "Oversight Scores": "ओवरसाइट स्कोर",
    "Total Districts Tracked": "कुल ट्रैक किए गए जिले",
    "Total Health Facilities": "कुल स्वास्थ्य सुविधाएं",
    "State-wide Flagged Facilities": "राज्य-व्यापी ध्वजांकित सुविधाएं",
    "District Alerts Outstanding": "जिला अलर्ट बकाया",
    "District Performance Leaderboard": "जिला प्रदर्शन लीडरबोर्ड",
    "Rank": "रैंक",
    "District": "जिला",
    "Oversight Score": "ओवरसाइट स्कोर",
    "Total Facilities": "कुल सुविधाएं",
    "Bed Occupancy": "बिस्तर अधिभोग",
    "Attendance Rate": "उपस्थिति दर",
    "Action": "कार्रवाई",
    "Enter Command": "कमांड दर्ज करें",
    "Oversight Scores Leaderboard": "ओवरसाइट स्कोर लीडरबोर्ड",
    "Active District Alerts Queue": "सक्रिय जिला अलर्ट कतार",
    "Medicine Inventory Ledger": "दवा सूची बही",
    "Ward Bed Management": "वार्ड बेड प्रबंधन",
    "Roster Check-In / Out": "रोस्टर चेक-इन / आउट",
    "Diagnostic Audit Checklist": "नैदानिक ऑडिट चेकलिस्ट",
    "Staff Attendance": "कर्मचारी उपस्थिति",
    "Bed Occupancy Avg": "बिस्तर अधिभोग औसत",
    "OPD Consultations": "ओपीडी परामर्श",
    "IPD Admissions": "आईपीडी प्रवेश",
    "Diagnostics Compliance": "नैदानिक अनुपालन",
    "District Alerts Center": "जिला अलर्ट केंद्र",
    "Pending": "लंबित",
    "Critical": "गंभीर",
    "Lucknow Critical Drugs Availability Matrix": "लखनऊ महत्वपूर्ण दवा उपलब्धता मैट्रिक्स",
    "Facility": "सुविधा",
    "Type": "प्रकार",
    "Block": "ब्लॉक",
    "AI Stock Redistribution recommendations": "एआई स्टॉक पुनर्वितरण अनुशंसाएँ",
    "Matched drug transfer suggestions from surplus facilities to deficit targets within 50 km": "50 किमी के भीतर अधिशेष सुविधाओं से घाटे के लक्ष्यों में मिलान दवा हस्तांतरण सुझाव",
    "Approve": "स्वीकार करें",
    "Reject": "अस्वीकार करें",
    "Ward Filter": "वार्ड फ़िल्टर",
    "Available Beds & Redirect Options: ": "उपलब्ध बिस्तर और पुनर्निर्देशन विकल्प: ",
    "Available Beds": "उपलब्ध बिस्तर",
    "Total Beds": "कुल बिस्तर",
    "Distance (Mohanlalganj PHC)": "दूरी (मोहनलालगंज पीएचसी)",
    "Doctor Coverage Gaps Today": "आज डॉक्टरों का कवरेज अंतराल",
    "Facilities where no Medical Officer (MO) has checked in today": "ऐसी सुविधाएं जहां आज किसी भी चिकित्सा अधिकारी (एमओ) ने चेक-इन नहीं किया है",
    "Absenteeism Warning List": "अनुपस्थिति चेतावनी सूची",
    "Staff members with > 3 absences in the last 30 days": "पिछले 30 दिनों में 3 से अधिक अनुपस्थिति वाले कर्मचारी",
    "FDSI Mandated Free Diagnostics Compliance Gaps": "एफडीएसआई अनिवार्य मुफ्त निदान अनुपालन अंतराल",
    "National standard requires 10 diagnostic test categories available free of charge at CHCs/PHCs": "राष्ट्रीय मानक के अनुसार सीएचसी/पीएचसी में 10 नैदानिक ​​परीक्षण श्रेणियां निःशुल्क उपलब्ध होना आवश्यक है",
    "Missing Mandated Tests": "लापता अनिवार्य परीक्षण",
    "Active District Alerts Queue ": "सक्रिय जिला अलर्ट कतार ",
    "No active alerts currently logged.": "वर्तमान में कोई सक्रिय अलर्ट लॉग नहीं है।",
    "Resolve": "सुलझाएं",
    "Detected Statistical Outliers & Spikes": "सांख्यिकीय आउटलेर और स्पाइक्स का पता चला",
    "Confirm": "पुष्टि करें",
    "Dismiss": "खारिज करें",
    "Oversight Score:": "ओवरसाइट स्कोर:",
    "Stock Reliability:": "स्टॉक विश्वसनीयता:",
    "Attendance rate:": "उपस्थिति दर:",
    "Bed Turnover:": "बिस्तर टर्नओवर:",
    "Diagnostics Compliance:": "नैदानिक अनुपालन:",
    "Diagnostic Explainer:": "नैदानिक स्पष्टीकरण:",
    "Outbreak Hotspots": "आउटब्रेक हॉटस्पॉट",
    "Disease Outbreak Hotspot Prediction": "रोग प्रकोप हॉटस्पॉट पूर्वानुमान",
    "Analyzing rolling 14-day patient footfall logs to identify localized epidemic surges and project transmission patterns.": "स्थानीय महामारी के प्रकोप की पहचान करने के लिए 14-दिन के रोगी संख्या लॉग का विश्लेषण।",
    "Suspected Outbreak": "संदिग्ध प्रकोप",
    "Recommended Actions:": "अनुशंसित कार्रवाई:"
  },
  "ta-IN": {
    "Lucknow Command Oversight Panel": "லக்னோ கட்டளை கண்காணிப்பு குழு",
    "Uttar Pradesh Healthcare Dashboard": "உத்தரபிரதேச சுகாதார டாஷ்போர்டு",
    "State Analytics Portal": "மாநில பகுப்பாய்வு போர்டல்",
    "25 Active Facilities (20 PHCs, 5 CHCs)": "25 செயலில் உள்ள வசதிகள் (20 PHC, 5 CHC)",
    "Refresh Live Metrics": "மெட்ரிக்ஸை புதுப்பி",
    "State Level": "மாநில நிலை",
    "Lucknow District": "லக்னோ மாவட்டம்",
    "Stock Heatmap": "இருப்பு வரைபடம்",
    "Redistributions": "மறுபகிர்வுகள்",
    "Beds & Redirects": "படுக்கைகள் & திசைதிருப்பல்",
    "Attendance & Gaps": "வருகை & இடைவெளிகள்",
    "FDSI Compliance": "FDSI இணக்கம்",
    "Early Warnings": "முன்னெச்சரிக்கைகள்",
    "Oversight Scores": "கண்காணிப்பு மதிப்பெண்கள்",
    "Total Districts Tracked": "கண்காணிக்கப்படும் மொத்த மாவட்டங்கள்",
    "Total Health Facilities": "மொத்த சுகாதார வசதிகள்",
    "State-wide Flagged Facilities": "மாநில அளவிலான குறிக்கப்பட்ட வசதிகள்",
    "District Alerts Outstanding": "மாவட்ட எச்சரிக்கைகள் நிலுவை",
    "District Performance Leaderboard": "மாவட்ட செயல்திறன் தரவரிசை",
    "Rank": "தரவரிசை",
    "District": "மாவட்டம்",
    "Oversight Score": "கண்காணிப்பு மதிப்பெண்",
    "Total Facilities": "மொத்த வசதிகள்",
    "Bed Occupancy": "படுக்கை இருப்பு",
    "Attendance Rate": "வருகை விகிதம்",
    "Action": "செயல்",
    "Enter Command": "கட்டளையிடு",
    "Oversight Scores Leaderboard": "கண்காணிப்பு தரவரிசை",
    "Active District Alerts Queue": "செயலில் உள்ள மாவட்ட எச்சரிக்கைகள்",
    "Medicine Inventory Ledger": "மருந்து இருப்புப் பதிவேடு",
    "Ward Bed Management": "வார்டு படுக்கை மேலாண்மை",
    "Roster Check-In / Out": "பணிப்பதிவு வருகை / வெளியேற்றம்",
    "Diagnostic Audit Checklist": "கண்டறிதல் தணிக்கை சரிபார்ப்பு பட்டியல்",
    "Staff Attendance": "ஊழியர் வருகை",
    "Bed Occupancy Avg": "படுக்கை இருப்பு சராசரி",
    "OPD Consultations": "வெளிநோயாளி ஆலோசனை",
    "IPD Admissions": "உள்நோயாளி அனுமதி",
    "Diagnostics Compliance": "கண்டறிதல் இணக்கம்",
    "District Alerts Center": "மாவட்ட எச்சரிக்கை மையம்",
    "Pending": "நிலுவையில் உள்ளது",
    "Critical": "தீவிரமானது",
    "Lucknow Critical Drugs Availability Matrix": "லக்னோ முக்கிய மருந்து இருப்பு மேட்ரிக்ஸ்",
    "Facility": "வசதி",
    "Type": "வகை",
    "Block": "வட்டாரம்",
    "AI Stock Redistribution recommendations": "AI இருப்பு மறுபகிர்வு பரிந்துரைகள்",
    "Matched drug transfer suggestions from surplus facilities to deficit targets within 50 km": "50 கிமீக்குள் உபரி வசதிகளிலிருந்து பற்றாக்குறை இலக்குகளுக்கு மருந்து பரிமாற்ற பரிந்துரைகள்",
    "Approve": "ஒப்புதல் அளிக்கவும்",
    "Reject": "நிராகரி",
    "Ward Filter": "வார்டு வடிகட்டி",
    "Available Beds & Redirect Options: ": "படுக்கைகள் & திசைதிருப்பல் விருப்பங்கள்: ",
    "Available Beds": "கிடைக்கக்கூடிய படுக்கைகள்",
    "Total Beds": "மொத்த படுக்கைகள்",
    "Distance (Mohanlalganj PHC)": "தொலைவு (மோகன்லால்கஞ்ச் PHC)",
    "Doctor Coverage Gaps Today": "இன்றைய மருத்துவர் பற்றாக்குறை",
    "Facilities where no Medical Officer (MO) has checked in today": "இன்று எந்த மருத்துவ அதிகாரியும் வருகை தராத வசதிகள்",
    "Absenteeism Warning List": "ஊழியர் வராமை எச்சரிக்கை பட்டியல்",
    "Staff members with > 3 absences in the last 30 days": "கடந்த 30 நாட்களில் 3 முறைக்கு மேல் வருகை தராத ஊழியர்கள்",
    "FDSI Mandated Free Diagnostics Compliance Gaps": "FDSI கட்டாய இலவச கண்டறிதல் இணக்க இடைவெளிகள்",
    "National standard requires 10 diagnostic test categories available free of charge at CHCs/PHCs": "CHCs/PHCs களில் 10 வகையான கண்டறியும் சோதனைகள் இலவசமாக கிடைக்க வேண்டும் என்பது தேசிய விதி",
    "Missing Mandated Tests": "இல்லாத கட்டாய சோதனைகள்",
    "Active District Alerts Queue ": "செயலில் உள்ள மாவட்ட எச்சரிக்கைகள் ",
    "No active alerts currently logged.": "செயலில் உள்ள எச்சரிக்கைகள் எதுவும் இல்லை.",
    "Resolve": "தீர்க்கவும்",
    "Detected Statistical Outliers & Spikes": "கண்டறியப்பட்ட புள்ளியியல் மாற்றங்கள்",
    "Confirm": "உறுதிப்படுத்து",
    "Dismiss": "நிராகரி",
    "Oversight Score:": "கண்காணிப்பு மதிப்பெண்:",
    "Stock Reliability:": "இருப்பு நம்பகத்தன்மை:",
    "Attendance rate:": "வருகை விகிதம்:",
    "Bed Turnover:": "படுக்கை சுழற்சி:",
    "Diagnostics Compliance:": "கண்டறிதல் இணக்கம்:",
    "Diagnostic Explainer:": "தணிக்கை விளக்கம்:",
    "Outbreak Hotspots": "தொற்றுநோய் ஹாட்ஸ்பாட்கள்",
    "Disease Outbreak Hotspot Prediction": "நோய் பரவல் ஹாட்ஸ்பாட் கணிப்பு",
    "Analyzing rolling 14-day patient footfall logs to identify localized epidemic surges and project transmission patterns.": "உள்ளூர் தொற்றுநோய் பரவலைக் கண்டறிய 14-நாள் நோயாளி வருகைப் பதிவை பகுப்பாய்வு செய்கிறது.",
    "Suspected Outbreak": "சந்தேகிக்கப்படும் தொற்று",
    "Recommended Actions:": "பரிந்துரைக்கப்பட்ட நடவடிக்கைகள்:"
  }
};

export default function App() {
  // Auth state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  
  // View Modes: 'state' or 'district'
  const [viewMode, setViewMode] = useState<'state' | 'district'>('district');
  const selectedDistrict = 'Lucknow';
  
  // Navigation & Language
  const [activeTab, setActiveTab] = useState('heatmap');
  const [lang, setLang] = useState<string>(localStorage.getItem('lang') || 'en-IN');
  
  // District Data
  const [districtDashboard, setDistrictDashboard] = useState<any>(null);
  const [districtMatrix, setDistrictMatrix] = useState<any>({ medicines: [], matrix: [] });
  const [bedRedirects, setBedRedirects] = useState<any[]>([]);
  const [selectedWard, setSelectedWard] = useState('General');
  const [coverageGaps, setCoverageGaps] = useState<any[]>([]);
  const [complianceGaps, setComplianceGaps] = useState<any[]>([]);
  const [absenteeismPatterns, setAbsenteeismPatterns] = useState<any[]>([]);
  
  // Phase 3 AI data
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [anomalyStats, setAnomalyStats] = useState<any>(null);
  const [facilityScores, setFacilityScores] = useState<any[]>([]);
  const [hotspots, setHotspots] = useState<any[]>([]);
  
  // State Data
  const [stateDashboard, setStateDashboard] = useState<any>(null);
  
  // Detail selection
  const [selectedFacilityId, setSelectedFacilityId] = useState<string | null>(null);
  const [selectedFacilityDetail, setSelectedFacilityDetail] = useState<any>(null);
  const [selectedFacilityScore, setSelectedFacilityScore] = useState<any>(null);

  useEffect(() => {
    if (token) {
      fetchUserData(token);
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      loadData();
    }
  }, [user, viewMode, activeTab, selectedWard, selectedDistrict]);

  const fetchUserData = async (authToken: string) => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error('Error fetching user data', err);
    }
  };

  const loadData = async () => {
    if (!token) return;
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      if (viewMode === 'state') {
        const res = await fetch(`${API_BASE}/dashboard/state`, { headers });
        if (res.ok) setStateDashboard(await res.json());
      } else {
        // District Mode
        const kpiRes = await fetch(`${API_BASE}/dashboard/district`, { headers });
        if (kpiRes.ok) setDistrictDashboard(await kpiRes.json());

        if (activeTab === 'heatmap') {
          const res = await fetch(`${API_BASE}/stock/district-heatmap`, { headers });
          if (res.ok) setDistrictMatrix(await res.json());
        }
        
        if (activeTab === 'beds') {
          const res = await fetch(`${API_BASE}/beds/availability?ward_type=${selectedWard}`, { headers });
          if (res.ok) setBedRedirects(await res.json());
        }
        
        if (activeTab === 'gaps') {
          const gapsRes = await fetch(`${API_BASE}/attendance/gaps`, { headers });
          if (gapsRes.ok) setCoverageGaps(await gapsRes.json());
          
          const patternRes = await fetch(`${API_BASE}/attendance/patterns`, { headers });
          if (patternRes.ok) setAbsenteeismPatterns(await patternRes.json());
        }

        if (activeTab === 'compliance') {
          const res = await fetch(`${API_BASE}/diagnostics/mandated-gaps`, { headers });
          if (res.ok) setComplianceGaps(await res.json());
        }

        if (activeTab === 'recos') {
          const res = await fetch(`${API_BASE}/recommendations?status=pending`, { headers });
          if (res.ok) {
            const data = await res.json();
            // Dynamically translate rationales if needed
            if (lang !== 'en-IN') {
              for (let item of data) {
                item.rationale = await fetchDynamicTranslation(item.rationale, lang);
              }
            }
            setRecommendations(data);
          }
        }

        if (activeTab === 'anomalies') {
          const res = await fetch(`${API_BASE}/anomalies`, { headers });
          if (res.ok) {
            const data = await res.json();
            if (lang !== 'en-IN') {
              for (let item of data) {
                item.message = await fetchDynamicTranslation(item.message, lang);
              }
            }
            setAnomalies(data);
          }
          const statsRes = await fetch(`${API_BASE}/anomalies/stats`, { headers });
          if (statsRes.ok) setAnomalyStats(await statsRes.json());
        }

        if (activeTab === 'scores') {
          const res = await fetch(`${API_BASE}/scores/district`, { headers });
          if (res.ok) setFacilityScores(await res.json());
        }

        if (activeTab === 'hotspots') {
          const res = await fetch(`${API_BASE}/anomalies/hotspots`, { headers });
          if (res.ok) setHotspots(await res.json());
        }
      }
    } catch (err) {
      console.error('Error loading dashboard data', err);
    }
  };

  const fetchDynamicTranslation = async (text: string, targetLang: string) => {
    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text,
          source_lang: 'en-IN',
          target_lang: targetLang
        })
      });
      if (res.ok) {
        const data = await res.json();
        return data.translated_text;
      }
    } catch (e) {
      console.error('Dynamic translation failed', e);
    }
    return text;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        if (data.role !== 'dho' && data.role !== 'system_admin' && data.role !== 'state_admin') {
          setError('Access Denied: Administrative credentials required.');
          return;
        }
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        if (data.role === 'state_admin') {
          setViewMode('state');
        } else {
          setViewMode('district');
        }
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Cannot connect to API server.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setUsername('');
    setPassword('');
    setViewMode('district');
    setActiveTab('heatmap');
  };

  const handleRecommendationDecision = async (recId: string, decision: 'accepted' | 'rejected') => {
    try {
      const res = await fetch(`${API_BASE}/recommendations/${recId}/decision?decision=${decision}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error('Error making recommendation decision', err);
    }
  };

  const handleClassifyAnomaly = async (alertId: string, classification: 'true_positive' | 'false_positive') => {
    try {
      const res = await fetch(`${API_BASE}/anomalies/${alertId}/classify?classification=${classification}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error('Error classifying anomaly', err);
    }
  };

  const viewFacilityDetail = async (facilityId: string) => {
    setSelectedFacilityId(facilityId);
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const detailRes = await fetch(`${API_BASE}/facilities/${facilityId}`, { headers });
      if (detailRes.ok) {
        setSelectedFacilityDetail(await detailRes.json());
      }
      const scoreRes = await fetch(`${API_BASE}/scores/facility/${facilityId}`, { headers });
      if (scoreRes.ok) {
        const rawScore = await scoreRes.json();
        if (lang !== 'en-IN') {
          rawScore.explainer = await fetchDynamicTranslation(rawScore.explainer, lang);
        }
        setSelectedFacilityScore(rawScore);
      }
    } catch (err) {
      console.error('Error fetching details', err);
    }
  };

  const t = (text: string) => {
    const langDict = STATIC_DICT[lang];
    if (langDict && text in langDict) {
      return langDict[text];
    }
    return text;
  };

  const changeLanguage = (newLang: string) => {
    setLang(newLang);
    localStorage.setItem('lang', newLang);
  };

  return (
    <div style={{ flex: 1, display: 'flex', minHeight: '100vh', background: 'var(--bg-base)' }}>
      {/* Login Screen */}
      {!token ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh', justifyContent: 'space-between' }}>
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '16px' }}>
            <div className="glass fade-in" style={{ width: '100%', maxWidth: '420px', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ textAlign: 'center' }}>
                <Landmark size={48} color="#3b82f6" style={{ margin: '0 auto 12px' }} />
                <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Swasth AI — Command Panel</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
                  District & State Health Oversight Login
                </p>
              </div>

              {error && (
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger)', padding: '12px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <AlertTriangle size={18} color="#ef4444" />
                  <span style={{ fontSize: '0.85rem', color: '#ef4444' }}>{error}</span>
                </div>
              )}

              <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Username</label>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. dho_lucknow"
                    style={{ width: '100%', padding: '12px 16px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Password</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    style={{ width: '100%', padding: '12px 16px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                  />
                </div>

                <button type="submit" disabled={loading} className="glow-btn" style={{ marginTop: '8px' }}>
                  Enter Command Center
                </button>
              </form>

              <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                DHO: <code>dho_lucknow</code> / <code>password123</code><br />
                State Admin: <code>admin</code> / <code>password123</code>
              </div>
            </div>
          </div>
          <footer style={{ padding: '16px', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Swasth AI Command Center © 2026.
          </footer>
        </div>
      ) : (
        /* Dashboard UI Workspace */
        <div style={{ flex: 1, display: 'flex', flexDirection: 'row' }}>
          {/* Sidebar Navigation */}
          <aside className="glass" style={{ width: '260px', margin: '16px 0 16px 16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '12px' }}>
            <div style={{ padding: '24px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '32px' }}>
                <Landmark size={28} color="#3b82f6" />
                <span style={{ fontWeight: 700, letterSpacing: '0.5px' }}>SWASTH COMMAND</span>
              </div>
              
              {/* State vs District Selection */}
              {user && (user.role === 'state_admin' || user.role === 'system_admin') && (
                <div style={{ display: 'flex', background: 'rgba(255,255,255,0.03)', padding: '4px', borderRadius: '8px', marginBottom: '24px' }}>
                  <button 
                    onClick={() => { setViewMode('state'); setSelectedFacilityId(null); }}
                    style={{ flex: 1, padding: '8px 4px', fontSize: '0.75rem', borderRadius: '6px', fontWeight: 600, background: viewMode === 'state' ? 'var(--primary)' : 'transparent', color: viewMode === 'state' ? '#000' : 'var(--text-secondary)', cursor: 'pointer' }}
                  >
                    {t('State Level')}
                  </button>
                  <button 
                    onClick={() => { setViewMode('district'); setSelectedFacilityId(null); }}
                    style={{ flex: 1, padding: '8px 4px', fontSize: '0.75rem', borderRadius: '6px', fontWeight: 600, background: viewMode === 'district' ? 'var(--primary)' : 'transparent', color: viewMode === 'district' ? '#000' : 'var(--text-secondary)', cursor: 'pointer' }}
                  >
                    {t('Lucknow District')}
                  </button>
                </div>
              )}

              {viewMode === 'district' ? (
                <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {[
                    { id: 'heatmap', label: t('Stock Heatmap'), icon: BarChart2 },
                    { id: 'recos', label: t('Redistributions'), icon: TrendingUp },
                    { id: 'beds', label: t('Beds & Redirects'), icon: Shield },
                    { id: 'gaps', label: t('Attendance & Gaps'), icon: Users },
                    { id: 'compliance', label: t('FDSI Compliance'), icon: Clipboard },
                    { id: 'anomalies', label: t('Early Warnings'), icon: AlertOctagon },
                    { id: 'hotspots', label: t('Outbreak Hotspots'), icon: Activity },
                    { id: 'scores', label: t('Oversight Scores'), icon: CheckCircle2 }
                  ].map(item => (
                    <button
                      key={item.id}
                      onClick={() => { setActiveTab(item.id); setSelectedFacilityId(null); setSelectedFacilityDetail(null); }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px 16px',
                        borderRadius: '8px',
                        width: '100%',
                        textAlign: 'left',
                        fontWeight: 500,
                        cursor: 'pointer',
                        background: activeTab === item.id ? 'var(--primary-light)' : 'transparent',
                        color: activeTab === item.id ? 'var(--primary)' : 'var(--text-secondary)',
                        transition: 'all 0.2s'
                      }}
                    >
                      <item.icon size={18} />
                      <span>{item.label}</span>
                    </button>
                  ))}
                </nav>
              ) : (
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <p style={{ fontWeight: 600, marginBottom: '12px' }}>State Administration Mode</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px', background: 'var(--primary-light)', color: 'var(--primary)', borderRadius: '6px' }}>
                      <TrendingUp size={16} /> District Oversight
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
              {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--primary)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                    {user.username[0].toUpperCase()}
                  </div>
                  <div style={{ overflow: 'hidden' }}>
                    <p style={{ fontSize: '0.85rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.username}</p>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{user.role.toUpperCase()}</p>
                  </div>
                </div>
              )}
              <button 
                onClick={handleLogout}
                style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '8px', padding: '10px', borderRadius: '8px', cursor: 'pointer', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444' }}
              >
                <LogOut size={16} />
                <span>{t('Log Out')}</span>
              </button>
            </div>
          </aside>

          {/* Main workspace */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px', gap: '16px', overflowY: 'auto' }}>
            {/* Topbar */}
            <div className="glass" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '12px' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>
                  {viewMode === 'state' ? t('Uttar Pradesh Healthcare Dashboard') : t('Lucknow Command Oversight Panel')}
                </h2>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  {viewMode === 'state' ? t('State Analytics Portal') : t('25 Active Facilities (20 PHCs, 5 CHCs)')}
                </p>
              </div>

              {/* Language Selector */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--border)', cursor: 'pointer', fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                  <RefreshCw size={16} />
                  <span>{t('Refresh Live Metrics')}</span>
                </button>

                <select
                  value={lang}
                  onChange={(e) => changeLanguage(e.target.value)}
                  style={{ padding: '8px 12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)', fontSize: '0.85rem', fontWeight: 500 }}
                >
                  <option value="en-IN" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>English</option>
                  <option value="hi-IN" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>हिन्दी</option>
                  <option value="ta-IN" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>தமிழ்</option>
                </select>
              </div>
            </div>

            {/* State Dashboard View */}
            {viewMode === 'state' && stateDashboard && (
              <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* State aggregates */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <Landmark size={24} color="var(--primary)" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Total Districts Tracked')}</span>
                    <span style={{ fontSize: '2rem', fontWeight: 700 }}>{stateDashboard.total_districts}</span>
                  </div>
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <Activity size={24} color="#10b981" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Total Health Facilities')}</span>
                    <span style={{ fontSize: '2rem', fontWeight: 700 }}>{stateDashboard.total_facilities}</span>
                  </div>
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '8px', borderLeft: '3px solid var(--danger)' }}>
                    <AlertTriangle size={24} color="#ef4444" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('State-wide Flagged Facilities')}</span>
                    <span style={{ fontSize: '2rem', fontWeight: 700, color: '#ef4444' }}>{stateDashboard.flagged_facilities}</span>
                  </div>
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <Shield size={24} color="#3b82f6" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('District Alerts Outstanding')}</span>
                    <span style={{ fontSize: '2rem', fontWeight: 700 }}>{stateDashboard.active_alerts}</span>
                  </div>
                </div>

                {/* Districts ranking */}
                <div className="glass" style={{ padding: '24px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '20px' }}>{t('District Performance Leaderboard')}</h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                          <th style={{ padding: '12px' }}>{t('Rank')}</th>
                          <th style={{ padding: '12px' }}>{t('District')}</th>
                          <th style={{ padding: '12px' }}>{t('Oversight Score')}</th>
                          <th style={{ padding: '12px' }}>{t('Total Facilities')}</th>
                          <th style={{ padding: '12px' }}>{t('Bed Occupancy')}</th>
                          <th style={{ padding: '12px' }}>{t('Attendance Rate')}</th>
                          <th style={{ padding: '12px' }}>{t('Action')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stateDashboard.districts.map((d: any, idx: number) => (
                          <tr key={d.district} style={{ borderBottom: '1px solid var(--border)' }}>
                            <td style={{ padding: '12px', fontWeight: 700 }}>#{idx + 1}</td>
                            <td style={{ padding: '12px', fontWeight: 600 }}>{d.district}</td>
                            <td style={{ padding: '12px' }}>
                              <span style={{ padding: '4px 8px', borderRadius: '4px', background: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 700 }}>
                                {d.health_score}
                              </span>
                            </td>
                            <td style={{ padding: '12px' }}>{d.active_facilities}</td>
                            <td style={{ padding: '12px' }}>{d.avg_bed_occupancy}%</td>
                            <td style={{ padding: '12px' }}>{d.attendance_rate}%</td>
                            <td style={{ padding: '12px' }}>
                              {d.district === 'Lucknow' ? (
                                <button 
                                  onClick={() => setViewMode('district')} 
                                  style={{ padding: '6px 12px', background: 'rgba(59,130,246,0.1)', color: '#3b82f6', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
                                >
                                  {t('Enter Command')}
                                </button>
                              ) : (
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Simulation Mode</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* District View */}
            {viewMode === 'district' && (
              <>
                {/* District Overview KPI cards */}
                {districtDashboard && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
                    <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <Landmark size={20} color="var(--primary)" />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Lucknow Facilities')}</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{districtDashboard.total_facilities} Active</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{districtDashboard.flagged_facilities} Flagged center(s)</span>
                    </div>
                    <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <Activity size={20} color="#10b981" />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('OPD Consultations')}</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{districtDashboard.footfall_today} today</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>+12% vs last week</span>
                    </div>
                    <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <Shield size={20} color="#3b82f6" />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Bed Occupancy Avg')}</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{districtDashboard.beds.occupancy_rate}%</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{districtDashboard.beds.occupied_beds} occupied beds</span>
                    </div>
                    <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <Users size={20} color="#f59e0b" />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Attendance Rate')}</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{districtDashboard.attendance.attendance_rate}%</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{districtDashboard.attendance.present_today} checked in</span>
                    </div>
                    <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: districtDashboard.alerts.critical > 0 ? '3px solid var(--danger)' : '1px solid var(--border)' }}>
                      <AlertTriangle size={20} color={districtDashboard.alerts.critical > 0 ? '#ef4444' : '#f59e0b'} />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('District Alerts Center')}</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 700, color: districtDashboard.alerts.critical > 0 ? '#ef4444' : 'inherit' }}>
                        {districtDashboard.alerts.total} {t('Pending')}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{districtDashboard.alerts.critical} {t('Critical')}</span>
                    </div>
                  </div>
                )}

                {/* District Sub-tab views */}
                {activeTab === 'heatmap' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '20px' }}>{t('Lucknow Critical Drugs Availability Matrix')}</h3>
                      <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                              <th style={{ padding: '12px' }}>{t('Facility')}</th>
                              <th style={{ padding: '12px' }}>{t('Type')}</th>
                              <th style={{ padding: '12px' }}>{t('Block')}</th>
                              {districtMatrix.medicines.map((med: string) => (
                                <th key={med} style={{ padding: '12px' }}>{med.split(' ')[0]}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {districtMatrix.matrix.map((row: any) => (
                              <tr key={row.facility_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td 
                                  onClick={() => viewFacilityDetail(row.facility_id)}
                                  style={{ padding: '12px', fontWeight: 600, color: 'var(--primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                                >
                                  <Eye size={14} /> {row.facility_name}
                                </td>
                                <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{row.type}</td>
                                <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{row.block}</td>
                                
                                {districtMatrix.medicines.map((med: string) => {
                                  const medData = row[med];
                                  let cellBg = 'rgba(16, 185, 129, 0.12)';
                                  let cellColor = '#10b981';
                                  let cellLabel = medData.quantity;
                                  
                                  if (medData.status === 'stockout') {
                                    cellBg = 'rgba(239, 68, 68, 0.15)';
                                    cellColor = '#ef4444';
                                    cellLabel = 'OUT';
                                  } else if (medData.status === 'low') {
                                    cellBg = 'rgba(245, 158, 11, 0.15)';
                                    cellColor = '#f59e0b';
                                  } else if (medData.status === 'no_stock') {
                                    cellBg = 'rgba(255,255,255,0.03)';
                                    cellColor = 'var(--text-muted)';
                                    cellLabel = 'N/A';
                                  }

                                  return (
                                    <td key={med} style={{ padding: '6px 12px' }}>
                                      <div style={{ padding: '6px 10px', borderRadius: '4px', background: cellBg, color: cellColor, fontWeight: 700, textAlign: 'center', fontSize: '0.8rem' }}>
                                        {cellLabel}
                                      </div>
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {/* Phase 3 Redistribution Recommendations */}
                {activeTab === 'recos' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '10px' }}>{t('AI Stock Redistribution recommendations')}</h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>{t('Matched drug transfer suggestions from surplus facilities to deficit targets within 50 km')}</p>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', maxHeight: '500px', overflowY: 'auto', padding: '4px' }}>
                        {recommendations.length === 0 ? (
                          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                            No active redistribution recommendations found. Stock levels are currently matched.
                          </div>
                        ) : (
                          recommendations.map(rec => (
                            <div key={rec.rec_id} className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', borderLeft: rec.urgency_score > 70 ? '4px solid var(--danger)' : '4px solid var(--primary)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{rec.resource_name}</span>
                                <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.04)', color: 'var(--text-secondary)' }}>
                                  {rec.distance_km} km away
                                </span>
                              </div>
                              
                              <div style={{ fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between' }}>
                                <div>
                                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>FROM (SURPLUS)</span>
                                  <span style={{ fontWeight: 600 }}>{rec.source_facility_name}</span>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>TO (DEFICIT)</span>
                                  <span style={{ fontWeight: 600 }}>{rec.target_facility_name}</span>
                                </div>
                              </div>
                              
                              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                                <strong>Rationale:</strong> {rec.rationale}
                              </div>
                              
                              <div style={{ display: 'flex', gap: '10px', marginTop: '4px' }}>
                                <button 
                                  onClick={() => handleRecommendationDecision(rec.rec_id, 'accepted')}
                                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '10px', background: '#10b981', color: '#000', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
                                >
                                  <Check size={16} /> {t('Approve')}
                                </button>
                                <button 
                                  onClick={() => handleRecommendationDecision(rec.rec_id, 'rejected')}
                                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', padding: '10px', background: 'transparent', border: '1px solid var(--border)', color: '#ef4444', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
                                >
                                  <X size={16} /> {t('Reject')}
                                </button>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'beds' && (
                  <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <h3 style={{ fontWeight: 600 }}>{t('Ward Filter')}</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {['General', 'Maternity', 'ICU', 'Pediatric'].map(w => (
                          <button
                            key={w}
                            onClick={() => setSelectedWard(w)}
                            style={{
                              padding: '12px', borderRadius: '6px', cursor: 'pointer', textAlign: 'left', fontWeight: 500,
                              background: selectedWard === w ? 'var(--primary-light)' : 'transparent',
                              color: selectedWard === w ? 'var(--primary)' : 'var(--text-secondary)'
                            }}
                          >
                            {w} Ward
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '20px' }}>{t('Available Beds & Redirect Options: ')}{selectedWard} Ward</h3>
                      <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                              <th style={{ padding: '12px' }}>{t('Facility')}</th>
                              <th style={{ padding: '12px' }}>{t('Block')}</th>
                              <th style={{ padding: '12px' }}>{t('Available Beds')}</th>
                              <th style={{ padding: '12px' }}>{t('Total Beds')}</th>
                              <th style={{ padding: '12px' }}>{t('Distance (Mohanlalganj PHC)')}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {bedRedirects.map(row => (
                              <tr key={row.facility_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={{ padding: '12px', fontWeight: 600 }}>{row.facility_name}</td>
                                <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{row.block}</td>
                                <td style={{ padding: '12px', color: '#10b981', fontWeight: 700 }}>{row.empty_beds} Vacant</td>
                                <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{row.total_beds}</td>
                                <td style={{ padding: '12px', fontWeight: 500 }}>{row.distance_km} km</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'gaps' && (
                  <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444' }}>
                        <AlertOctagon /> {t('Doctor Coverage Gaps Today')}
                      </h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Facilities where no Medical Officer (MO) has checked in today')}</p>
                      
                      {coverageGaps.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-secondary)' }}>
                          All health posts currently have doctors present today.
                        </div>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto', paddingRight: '4px' }}>
                          {coverageGaps.map(g => (
                            <div key={g.facility_id} className="glass" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid rgba(239,68,68,0.2)' }}>
                              <div>
                                <span style={{ fontWeight: 600 }}>{g.facility_name}</span>
                                <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-secondary)' }}>Block: {g.block} | Type: {g.type}</span>
                              </div>
                              <span style={{ color: '#ef4444', fontWeight: 600, fontSize: '0.85rem' }}>Doctor Absent</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', color: '#f59e0b' }}>
                        <Users /> {t('Absenteeism Warning List')}
                      </h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Staff members with > 3 absences in the last 30 days')}</p>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '400px', overflowY: 'auto', paddingRight: '4px' }}>
                        {absenteeismPatterns.map(p => (
                          <div key={p.staff_id} className="glass" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <span style={{ fontWeight: 600 }}>{p.name}</span>
                              <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-secondary)' }}>{p.role.toUpperCase()} | {p.facility_name}</span>
                            </div>
                            <span style={{ color: '#f59e0b', fontWeight: 700 }}>{p.absences_last_30_days} Absences</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'compliance' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '10px' }}>{t('FDSI Mandated Free Diagnostics Compliance Gaps')}</h3>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>{t('National standard requires 10 diagnostic test categories available free of charge at CHCs/PHCs')}</p>
                      <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                              <th style={{ padding: '12px' }}>{t('Facility')}</th>
                              <th style={{ padding: '12px' }}>{t('Block')}</th>
                              <th style={{ padding: '12px' }}>{t('Compliance Score')}</th>
                              <th style={{ padding: '12px' }}>{t('Missing Mandated Tests')}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {complianceGaps.map(g => (
                              <tr key={g.facility_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={{ padding: '12px', fontWeight: 600 }}>{g.facility_name}</td>
                                <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{g.block}</td>
                                <td style={{ padding: '12px' }}>
                                  <span style={{ fontWeight: 700, color: g.compliance_score > 80 ? '#10b981' : '#ef4444' }}>
                                    {g.compliance_score}%
                                  </span>
                                </td>
                                <td style={{ padding: '12px' }}>
                                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {g.missing_mandated_tests.map((t: any) => (
                                      <span key={t.test_id} style={{ padding: '4px 8px', borderRadius: '4px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', fontSize: '0.75rem', fontWeight: 500 }}>
                                        {t.test_name.split(' (')[0]}
                                      </span>
                                    ))}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {/* Phase 3 Early Warning Anomalies */}
                {activeTab === 'anomalies' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {anomalyStats && (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                        <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Total Anomalies Detected')}</span>
                          <span style={{ fontSize: '1.8rem', fontWeight: 700 }}>{anomalyStats.total_detected}</span>
                        </div>
                        <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px', borderLeft: '3px solid var(--danger)' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Active Unresolved')}</span>
                          <span style={{ fontSize: '1.8rem', fontWeight: 700, color: '#ef4444' }}>{anomalyStats.active_unresolved}</span>
                        </div>
                        <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('True Positives')}</span>
                          <span style={{ fontSize: '1.8rem', fontWeight: 700, color: '#10b981' }}>{anomalyStats.true_positives}</span>
                        </div>
                        <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('True Positive Precision')}</span>
                          <span style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary)' }}>{anomalyStats.true_positive_rate_percent}%</span>
                        </div>
                      </div>
                    )}

                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '20px' }}>{t('Detected Statistical Outliers & Spikes')}</h3>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '500px', overflowY: 'auto', paddingRight: '4px' }}>
                        {anomalies.length === 0 ? (
                          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                            No active early warning anomalies detected.
                          </div>
                        ) : (
                          anomalies.map(anom => {
                            let cardColor = '#ef4444';
                            if (anom.status === 'dismissed') cardColor = 'var(--text-muted)';
                            else if (anom.status === 'resolved') cardColor = '#10b981';
                            
                            return (
                              <div key={anom.alert_id} className="glass" style={{ padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: `4px solid ${cardColor}` }}>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <span style={{ fontWeight: 600, fontSize: '1.05rem' }}>{anom.title}</span>
                                    <span style={{ padding: '3px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.04)', color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                                      {anom.status}
                                    </span>
                                  </div>
                                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Facility: {anom.facility_name}</span>
                                  <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{anom.message}</p>
                                </div>
                                
                                {anom.status === 'active' && (
                                  <div style={{ display: 'flex', gap: '8px' }}>
                                    <button 
                                      onClick={() => handleClassifyAnomaly(anom.alert_id, 'true_positive')}
                                      style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '8px 12px', background: '#10b981', color: '#000', borderRadius: '6px', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem' }}
                                    >
                                      <ThumbsUp size={14} /> {t('Confirm')}
                                    </button>
                                    <button 
                                      onClick={() => handleClassifyAnomaly(anom.alert_id, 'false_positive')}
                                      style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '8px 12px', background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '6px', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem' }}
                                    >
                                      <ThumbsDown size={14} /> {t('Dismiss')}
                                    </button>
                                  </div>
                                )}
                              </div>
                            );
                          })
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'hotspots' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '10px' }}>{t('Disease Outbreak Hotspot Prediction')}</h3>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                        {t('Analyzing rolling 14-day patient footfall logs to identify localized epidemic surges and project transmission patterns.')}
                      </p>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', maxHeight: '550px', overflowY: 'auto', padding: '4px' }}>
                        {hotspots.length === 0 ? (
                          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                            {t('No outbreak hotspots or anomalies detected currently.')}
                          </div>
                        ) : (
                          hotspots.map(spot => {
                            let cardColor = '#10b981';
                            let bgClass = 'rgba(16, 185, 129, 0.03)';
                            if (spot.risk_level === 'HIGH') {
                              cardColor = '#ef4444';
                              bgClass = 'rgba(239, 68, 68, 0.04)';
                            } else if (spot.risk_level === 'MODERATE') {
                              cardColor = '#f59e0b';
                              bgClass = 'rgba(245, 158, 11, 0.04)';
                            }
                            
                            return (
                              <div key={spot.facility_id} className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', borderLeft: `4px solid ${cardColor}`, background: bgClass }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <div>
                                    <span style={{ fontWeight: 700, fontSize: '1.05rem' }}>{spot.facility_name}</span>
                                    <span style={{ fontSize: '0.75rem', display: 'block', color: 'var(--text-secondary)' }}>Block: {spot.block} | Type: {spot.type}</span>
                                  </div>
                                  <span style={{ padding: '4px 8px', borderRadius: '4px', background: cardColor, color: '#000', fontSize: '0.75rem', fontWeight: 700 }}>
                                    {spot.risk_level} RISK
                                  </span>
                                </div>
                                
                                <div style={{ fontSize: '0.85rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', background: 'rgba(0,0,0,0.02)', padding: '10px', borderRadius: '6px' }}>
                                  <div>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>RECENT 7d AVG</span>
                                    <span style={{ fontWeight: 600 }}>{spot.recent_avg} patients/day</span>
                                  </div>
                                  <div>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>BASELINE AVG</span>
                                    <span style={{ fontWeight: 600 }}>{spot.baseline_avg} patients/day</span>
                                  </div>
                                </div>
                                
                                <div>
                                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>SUSPECTED DIAGNOSIS:</span>
                                  <span style={{ fontWeight: 600, color: spot.risk_level === 'HIGH' ? '#ef4444' : 'inherit' }}>{t(spot.suspected_outbreak)}</span>
                                </div>
                                
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '12px', background: 'rgba(0,0,0,0.02)', border: '1px solid var(--border)', borderRadius: '6px' }}>
                                  <strong>{t('Recommended Actions:')}</strong> {t(spot.recommended_actions)}
                                </div>
                              </div>
                            );
                          })
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Phase 3 Facility Scores Ranking */}
                {activeTab === 'scores' && (
                  <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="glass" style={{ padding: '24px' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '20px' }}>{t('Oversight Scores Leaderboard')}</h3>
                      
                      <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                              <th style={{ padding: '12px' }}>{t('Rank')}</th>
                              <th style={{ padding: '12px' }}>{t('Facility')}</th>
                              <th style={{ padding: '12px' }}>{t('Block')}</th>
                              <th style={{ padding: '12px' }}>{t('Oversight Score')}</th>
                              <th style={{ padding: '12px' }}>{t('Stock Reliability')}</th>
                              <th style={{ padding: '12px' }}>{t('Attendance Rate')}</th>
                              <th style={{ padding: '12px' }}>{t('Diagnostic Compliance')}</th>
                              <th style={{ padding: '12px' }}>{t('Status')}</th>
                            </tr>
                          </thead>
                          <tbody>
                            {facilityScores.map((score, idx) => {
                              let statusLabel = 'Adequate';
                              let statusColor = '#10b981';
                              let statusBg = 'rgba(16, 185, 129, 0.1)';
                              
                              if (score.is_flagged) {
                                statusLabel = 'Flagged';
                                statusColor = '#ef4444';
                                statusBg = 'rgba(239, 68, 68, 0.1)';
                              } else if (score.composite_score < 75.0) {
                                statusLabel = 'Watch';
                                statusColor = '#f59e0b';
                                statusBg = 'rgba(245, 158, 11, 0.1)';
                              }

                              return (
                                <tr key={score.facility_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                  <td style={{ padding: '12px', fontWeight: 700 }}>#{idx + 1}</td>
                                  <td 
                                    onClick={() => viewFacilityDetail(score.facility_id)}
                                    style={{ padding: '12px', fontWeight: 600, color: 'var(--primary)', cursor: 'pointer' }}
                                  >
                                    {score.facility_name}
                                  </td>
                                  <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{score.block}</td>
                                  <td style={{ padding: '12px' }}>
                                    <span style={{ padding: '4px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.03)', fontWeight: 700 }}>
                                      {score.composite_score}
                                    </span>
                                  </td>
                                  <td style={{ padding: '12px' }}>{score.stock_reliability}%</td>
                                  <td style={{ padding: '12px' }}>{score.attendance_rate}%</td>
                                  <td style={{ padding: '12px' }}>{score.test_availability}%</td>
                                  <td style={{ padding: '12px' }}>
                                    <span style={{ padding: '4px 8px', borderRadius: '4px', background: statusBg, color: statusColor, fontSize: '0.75rem', fontWeight: 600 }}>
                                      {statusLabel}
                                    </span>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Details Modal (Drilldown) */}
            {selectedFacilityId && selectedFacilityDetail && (
              <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
                <div className="glass fade-in" style={{ width: '100%', maxWidth: '560px', padding: '32px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h3 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{selectedFacilityDetail.name}</h3>
                      <span style={{ fontSize: '0.8rem', padding: '3px 8px', borderRadius: '100px', background: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 600 }}>
                        {selectedFacilityDetail.type} Health Centre
                      </span>
                    </div>
                    <button onClick={() => { setSelectedFacilityId(null); setSelectedFacilityDetail(null); setSelectedFacilityScore(null); }} style={{ fontSize: '1.5rem', cursor: 'pointer', padding: '4px 8px' }}>&times;</button>
                  </div>
                  
                  {/* Detailed AI score breakdown */}
                  {selectedFacilityScore && (
                    <div className="glass" style={{ padding: '16px', background: 'rgba(255,255,255,0.02)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600 }}>{t('Oversight Score:')}</span>
                        <span style={{ padding: '4px 10px', borderRadius: '4px', background: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 700, fontSize: '1.1rem' }}>
                          {selectedFacilityScore.composite_score}
                        </span>
                      </div>
                      
                      <div style={{ height: '1px', background: 'var(--border)', margin: '4px 0' }}></div>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.85rem' }}>
                        <span>{t('Stock Reliability:')} <strong>{selectedFacilityScore.stock_reliability}%</strong></span>
                        <span>{t('Attendance rate:')} <strong>{selectedFacilityScore.attendance_rate}%</strong></span>
                        <span>{t('Bed Turnover:')} <strong>{selectedFacilityScore.bed_turnover}%</strong></span>
                        <span>{t('Diagnostics Compliance:')} <strong>{selectedFacilityScore.test_availability}%</strong></span>
                      </div>
                      
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: '6px' }}>
                        <strong>{t('Diagnostic Explainer:')}</strong> {selectedFacilityScore.explainer}
                      </p>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    <p><strong>District:</strong> {selectedFacilityDetail.district}</p>
                    <p><strong>Block:</strong> {selectedFacilityDetail.block}</p>
                    <p><strong>ABDM HFR ID:</strong> <code>{selectedFacilityDetail.hfr_id}</code></p>
                    <p><strong>Total Bed Capacity:</strong> {selectedFacilityDetail.total_bed_capacity} beds</p>
                    <p><strong>Latitude/Longitude:</strong> {selectedFacilityDetail.latitude} , {selectedFacilityDetail.longitude}</p>
                  </div>
                  
                  <button onClick={() => { setSelectedFacilityId(null); setSelectedFacilityDetail(null); setSelectedFacilityScore(null); }} className="glow-btn" style={{ width: '100%' }}>
                    Close Details
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
