import React, { useState, useEffect } from 'react';
import { 
  Shield, Activity, Package, Clock, AlertTriangle, 
  CheckCircle2, Plus, Minus, FileText, 
  LogOut, Check, AlertOctagon, Wifi, WifiOff 
} from 'lucide-react';

const API_BASE = window.location.hostname.includes('vercel.app')
  ? 'https://api-gamma-pearl.vercel.app/api/v1'
  : 'http://localhost:8000/api/v1';

// Static translation dictionary to enable instant hot-swapping
const STATIC_DICT: any = {
  "en-IN": {},
  "hi-IN": {
    "Frontline Health Center Portal": "फ्रंटलाइन स्वास्थ्य केंद्र पोर्टल",
    "Dashboard": "डैशबोर्ड",
    "Inventory (Stock)": "इन्वेंटरी (स्टॉक)",
    "Patient Footfall": "रोगी संख्या",
    "Bed Wards": "बिस्तर वार्ड",
    "Attendance": "उपस्थिति",
    "Diagnostics Audit": "नैदानिक ऑडिट",
    "Log Out": "लॉग आउट",
    "Online Mode": "ऑनलाइन मोड",
    "Offline Mode": "ऑफ़लाइन मोड",
    "Inventory Health": "इन्वेंटरी स्वास्थ्य",
    "Bed Occupancy": "बिस्तर अधिभोग",
    "Staff Attendance": "कर्मचारी उपस्थिति",
    "Diagnostic Compliance": "नैदानिक अनुपालन",
    "Facility AI Composite Performance": "सुविधा एआई समग्र प्रदर्शन",
    "Status:": "स्थिति:",
    "Adequate Oversight": "पर्याप्त निरीक्षण",
    "Patient Footfall Today": "आज रोगियों की संख्या",
    "OPD Consultations": "ओपीडी परामर्श",
    "IPD Admissions": "आईपीडी प्रवेश",
    "Operational Routine Checklist": "परिचालन दिनचर्या चेकलिस्ट",
    "Medicine Inventory Ledger": "दवा सूची बही",
    "Medicine Name": "दवा का नाम",
    "Batch": "बैच",
    "Quantity": "मात्रा",
    "Status": "स्थिति",
    "AI Stockout Projection": "एआई स्टॉकआउट अनुमान",
    "Log Stock Movement": "स्टॉक मूवमेंट लॉग करें",
    "Select SKU": "एसकेयू चुनें",
    "Movement Type": "मूवमेंट प्रकार",
    "Notes": "नोट्स",
    "Log Movement": "मूवमेंट लॉग करें",
    "Register New SKU": "नया एसकेयू पंजीकृत करें",
    "Add to Inventory": "इन्वेंटरी में जोड़ें",
    "Log Patient Counts": "रोगी संख्या लॉग करें",
    "Department": "विभाग",
    "OPD Count": "ओपीडी संख्या",
    "IPD Count": "आईपीडी संख्या",
    "Submit Today's Count": "आज की संख्या सबमिट करें",
    "Ward Bed Management": "वार्ड बेड प्रबंधन",
    "Occupied": "भरे हुए",
    "occupied /": "भरे हुए /",
    "total": "कुल",
    "Roster Check-In / Out": "रोस्टर चेक-इन / आउट",
    "Mark daily arrival and departure at your health post": "अपने स्वास्थ्य केंद्र पर दैनिक आगमन और प्रस्थान दर्ज करें",
    "Roster Status:": "रोस्टर स्थिति:",
    "Check In": "चेक इन",
    "Check Out": "चेक आउट",
    "Diagnostic Audit Checklist": "नैदानिक ऑडिट चेकलिस्ट",
    "Select Test Category": "परीक्षण श्रेणी चुनें",
    "Availability Status": "उपलब्धता स्थिति",
    "Reagent Stock (Vials/Tests remaining)": "अभिकर्मक स्टॉक (शीशियां/परीक्षण शेष)",
    "Auditor Notes": "ऑडिटर नोट्स",
    "ACTIVE FACILITY ALERTS": "सक्रिय सुविधा अलर्ट",
    "Realtime Geolocation Status": "वास्तविक समय स्थान स्थिति",
    "Acquiring live coordinates...": "लाइव निर्देशांक प्राप्त कर रहा है...",
    "Location Access Denied": "स्थान पहुंच अस्वीकृत",
    "Location unavailable": "स्थान अनुपलब्ध"
  },
  "ta-IN": {
    "Frontline Health Center Portal": "முன்னணி சுகாதார மைய போர்டல்",
    "Dashboard": "டாஷ்போர்டு",
    "Inventory (Stock)": "சரக்கு இருப்பு",
    "Patient Footfall": "நோயாளி வருகை",
    "Bed Wards": "படுக்கை வார்டுகள்",
    "Attendance": "வருகை",
    "Diagnostics Audit": "கண்டறிதல் தணிக்கை",
    "Log Out": "வெளியேறு",
    "Online Mode": "ஆன்லைன் பயன்முறை",
    "Offline Mode": "ஆஃப்லைன் பயன்முறை",
    "Inventory Health": "இருப்பு நலம்",
    "Bed Occupancy": "படுக்கை இருப்பு",
    "Staff Attendance": "ஊழியர் வருகை",
    "Diagnostic Compliance": "கண்டறிதல் இணக்கம்",
    "Facility AI Composite Performance": "வசதி AI கூட்டு செயல்திறன்",
    "Status:": "நிலை:",
    "Adequate Oversight": "போதுமான மேற்பார்வை",
    "Patient Footfall Today": "இன்றைய நோயாளி வருகை",
    "OPD Consultations": "வெளிநோயாளி ஆலோசனை",
    "IPD Admissions": "உள்நோயாளி அனுமதி",
    "Operational Routine Checklist": "செயல்பாட்டு வழக்கமான சரிபார்ப்பு பட்டியல்",
    "Medicine Inventory Ledger": "மருந்து இருப்புப் பதிவேடு",
    "Medicine Name": "மருந்தின் பெயர்",
    "Batch": "தொகுதி",
    "Quantity": "அளவு",
    "Status": "நிலை",
    "AI Stockout Projection": "AI பற்றாக்குறை கணிப்பு",
    "Log Stock Movement": "இருப்பு இயக்கத்தை பதிவு செய்",
    "Select SKU": "SKU ஐத் தேர்ந்தெடு",
    "Movement Type": "இயக்க வகை",
    "Notes": "குறிப்புகள்",
    "Log Movement": "இயக்கத்தை பதிவு செய்",
    "Register New SKU": "புதிய SKU ஐ பதிவு செய்",
    "Add to Inventory": "இருப்பில் சேர்",
    "Log Patient Counts": "நோயாளி எண்ணிக்கையை பதிவு செய்",
    "Department": "துறை",
    "OPD Count": "OPD எண்ணிக்கை",
    "IPD Count": "IPD எண்ணிக்கை",
    "Submit Today's Count": "இன்றைய எண்ணிக்கையைச் சமர்ப்பி",
    "Ward Bed Management": "வார்டு படுக்கை மேலாண்மை",
    "Occupied": "ஆக்கிரமிக்கப்பட்டுள்ளது",
    "occupied /": "ஆக்கிரமிக்கப்பட்டுள்ளது /",
    "total": "மொத்தம்",
    "Roster Check-In / Out": "பணிப்பதிவு வருகை / வெளியேற்றம்",
    "Mark daily arrival and departure at your health post": "சுகாதார நிலையத்தில் தினசரி வருகை மற்றும் புறப்பாட்டைக் குறிக்கவும்",
    "Roster Status:": "வருகை நிலை:",
    "Check In": "வருகை பதிவு",
    "Check Out": "வெளியேற்ற பதிவு",
    "Diagnostic Audit Checklist": "கண்டறிதல் தணிக்கை சரிபார்ப்பு பட்டியல்",
    "Select Test Category": "சோதனை வகையைத் தேர்ந்தெடு",
    "Availability Status": "இருப்பு நிலை",
    "Reagent Stock (Vials/Tests remaining)": "பரிசோதனை பொருள் இருப்பு (மீதமுள்ளவை)",
    "Auditor Notes": "தணிக்கையாளர் குறிப்புகள்",
    "ACTIVE FACILITY ALERTS": "செயலில் உள்ள வசதி எச்சரிக்கைகள்",
    "Realtime Geolocation Status": "உண்மைநேர இருப்பிட நிலை",
    "Acquiring live coordinates...": "நேரடி ஒருங்கிணைப்புகளைப் பெறுகிறது...",
    "Location Access Denied": "இருப்பிட அணுகல் மறுக்கப்பட்டது",
    "Location unavailable": "இருப்பிடம் கிடைக்கவில்லை"
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
  
  // Navigation & Language
  const [activeTab, setActiveTab] = useState('dashboard');
  const [lang, setLang] = useState<string>(localStorage.getItem('lang') || 'en-IN');
  
  // Connectivity & Offline states
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [offlineQueue, setOfflineQueue] = useState<any[]>(
    JSON.parse(localStorage.getItem('offlineQueue') || '[]')
  );
  const [toastMessage, setToastMessage] = useState<string>('');

  // Data state
  const [facDashboard, setFacDashboard] = useState<any>(null);
  const [stockItems, setStockItems] = useState<any[]>([]);
  const [stockForecasts, setStockForecasts] = useState<any[]>([]);
  const [bedStatus, setBedStatus] = useState<any[]>([]);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [diagnosticsCatalog, setDiagnosticsCatalog] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  
  // Form states
  const [movSkuId, setMovSkuId] = useState('');
  const [movType, setMovType] = useState('out');
  const [movQty, setMovQty] = useState(1);
  const [movNote, setMovNote] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Footfall Form
  const [footfallDept, setFootfallDept] = useState('General');
  const [opdCount, setOpdCount] = useState(10);
  const [ipdCount, setIpdCount] = useState(1);
  
  // Diagnostics Form
  const [selectedTestId, setSelectedTestId] = useState('');
  const [diagStatus, setDiagStatus] = useState('available');
  const [reagentQty, setReagentQty] = useState(100);
  const [diagNotes, setDiagNotes] = useState('');

  // Add SKU Form
  const [newSkuName, setNewSkuName] = useState('');
  const [newSkuGeneric, setNewSkuGeneric] = useState('');
  const [newSkuCategory] = useState('Analgesic');
  const [newSkuUnit] = useState('tablets');
  const [newSkuQty] = useState(100);
  const [newSkuMin] = useState(50);
  const [newSkuMax] = useState(500);

  // Real-time Geolocation tracking state
  const [gpsLat, setGpsLat] = useState<number | null>(null);
  const [gpsLon, setGpsLon] = useState<number | null>(null);
  const [gpsStatus, setGpsStatus] = useState<string>('initializing');

  // Real-time Geolocation Watch
  useEffect(() => {
    if (!token) return;
    
    if (!navigator.geolocation) {
      setGpsStatus('unsupported');
      return;
    }
    
    setGpsStatus('searching');
    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        setGpsLat(position.coords.latitude);
        setGpsLon(position.coords.longitude);
        setGpsStatus('active');
      },
      (error) => {
        console.error('Geolocation watch error:', error);
        setGpsStatus('denied');
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
    
    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, [token]);

  // Monitor connectivity
  useEffect(() => {
    const pingInterval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.status === 401) {
          // Token expired, handle logout but stay online
          setIsOnline(true);
        } else {
          setIsOnline(true);
        }
      } catch (e) {
        setIsOnline(false);
      }
    }, 4000);

    return () => clearInterval(pingInterval);
  }, [token]);

  // Handle Sync Queue when online
  useEffect(() => {
    if (isOnline && offlineQueue.length > 0 && token) {
      syncOfflineQueue();
    }
  }, [isOnline, token, offlineQueue]);

  useEffect(() => {
    if (token) {
      fetchUserData(token);
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      loadModuleData();
    }
  }, [user, activeTab]);

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

  const loadModuleData = async () => {
    if (!token || !user) return;
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Load active alerts
      const alertsRes = await fetch(`${API_BASE}/alerts?status_str=active`, { headers });
      if (alertsRes.ok) setAlerts(await alertsRes.json());

      if (activeTab === 'dashboard') {
        const dashRes = await fetch(`${API_BASE}/dashboard/facility/${user.facility_id}`, { headers });
        if (dashRes.ok) {
          const rawDash = await dashRes.json();
          // Translate dynamic fields if Hindi or Tamil selected
          if (lang !== 'en-IN') {
            rawDash.flag_reasons = await Promise.all(
              rawDash.flag_reasons.map((r: string) => fetchDynamicTranslation(r, lang))
            );
          }
          setFacDashboard(rawDash);
        }
      }
      
      if (activeTab === 'inventory') {
        const stockRes = await fetch(`${API_BASE}/stock/items`, { headers });
        if (stockRes.ok) {
          const data = await stockRes.json();
          setStockItems(data);
          if (data.length > 0 && !movSkuId) {
            setMovSkuId(data[0].sku_id);
          }
        }
        // const summaryRes = await fetch(`${API_BASE}/stock/summary`, { headers });
        // if (summaryRes.ok) setStockSummary(await summaryRes.json());

        // Fetch AI Forecast Projections
        const forecastRes = await fetch(`${API_BASE}/stock/forecast/bulk?facility_id=${user.facility_id}`, { headers });
        if (forecastRes.ok) setStockForecasts(await forecastRes.json());
      }

      if (activeTab === 'beds') {
        const bedsRes = await fetch(`${API_BASE}/beds/status`, { headers });
        if (bedsRes.ok) setBedStatus(await bedsRes.json());
      }

      if (activeTab === 'attendance') {
        const attRes = await fetch(`${API_BASE}/attendance`, { headers });
        if (attRes.ok) setAttendance(await attRes.json());
      }

      if (activeTab === 'diagnostics') {
        const catalogRes = await fetch(`${API_BASE}/diagnostics/tests`, { headers });
        if (catalogRes.ok) {
          const data = await catalogRes.json();
          setDiagnosticsCatalog(data);
          if (data.length > 0) {
            setSelectedTestId(data[0].test_id);
          }
        }
      }
    } catch (err) {
      console.error('Error fetching module data', err);
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

  const syncOfflineQueue = async () => {
    setToastMessage('Syncing queued actions...');
    const queue = [...offlineQueue];
    let syncedCount = 0;

    for (const item of queue) {
      try {
        const res = await fetch(item.url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(item.payload)
        });
        if (res.ok) {
          syncedCount++;
        }
      } catch (err) {
        console.error('Sync failed for item', item, err);
        // Stop flushing if server disconnects again
        break;
      }
    }

    const remaining = queue.slice(syncedCount);
    setOfflineQueue(remaining);
    localStorage.setItem('offlineQueue', JSON.stringify(remaining));

    if (syncedCount > 0) {
      setToastMessage(`✅ Back online! Synced ${syncedCount} items successfully.`);
      loadModuleData();
      setTimeout(() => setToastMessage(''), 5000);
    } else {
      setToastMessage('');
    }
  };

  const queueOfflineAction = (url: string, payload: any, actionName: string) => {
    const newItem = { url, payload, createdAt: new Date().toISOString() };
    const newQueue = [...offlineQueue, newItem];
    setOfflineQueue(newQueue);
    localStorage.setItem('offlineQueue', JSON.stringify(newQueue));
    setFormSuccess(`Saved Offline: ${actionName} queued (offline).`);
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
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
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
    setActiveTab('dashboard');
  };

  const submitStockMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!movSkuId) return;
    setFormSuccess('');
    setError('');

    const payload = {
      sku_id: movSkuId,
      movement_type: movType,
      quantity: movQty,
      reference_note: movNote
    };

    if (!isOnline) {
      // Optimistic UI updates
      const sku = stockItems.find(x => x.sku_id === movSkuId);
      if (sku) {
        sku.quantity = movType === 'in' ? sku.quantity + movQty : Math.max(0, sku.quantity - movQty);
        setStockItems([...stockItems]);
      }
      queueOfflineAction(`${API_BASE}/stock/movements`, payload, 'Stock Movement');
      setMovQty(1);
      setMovNote('');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/stock/movements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setFormSuccess('Stock movement logged successfully!');
        setMovQty(1);
        setMovNote('');
        loadModuleData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to log movement');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const submitRegisterSku = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSuccess('');
    setError('');

    const payload = {
      medicine_name: newSkuName,
      generic_name: newSkuGeneric,
      category: newSkuCategory,
      unit: newSkuUnit,
      quantity: newSkuQty,
      min_threshold: newSkuMin,
      max_threshold: newSkuMax
    };

    if (!isOnline) {
      // Optimistic addition
      const mockSku = {
        sku_id: 'temp-' + Math.random(),
        ...payload,
        batch_no: 'TEMP-BATCH'
      };
      setStockItems([...stockItems, mockSku]);
      queueOfflineAction(`${API_BASE}/stock/items`, payload, 'Register SKU');
      setNewSkuName('');
      setNewSkuGeneric('');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/stock/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setFormSuccess('New stock item registered!');
        setNewSkuName('');
        setNewSkuGeneric('');
        loadModuleData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to register item');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const submitFootfall = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSuccess('');
    setError('');

    const payload = {
      department: footfallDept,
      opd_count: opdCount,
      ipd_count: ipdCount
    };

    if (!isOnline) {
      if (facDashboard) {
        facDashboard.footfall.opd += opdCount;
        facDashboard.footfall.ipd += ipdCount;
        setFacDashboard({ ...facDashboard });
      }
      queueOfflineAction(`${API_BASE}/footfall`, payload, 'Patient Footfall');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/footfall`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setFormSuccess(`Logged today's counts for ${footfallDept} successfully!`);
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to log footfall');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleBedAdjustment = async (wardType: string, change: number, currentOcc: number, total: number) => {
    const nextOcc = currentOcc + change;
    if (nextOcc < 0 || nextOcc > total) return;
    setError('');

    // Optimistically update UI
    const targetWard = bedStatus.find(x => x.ward_type === wardType);
    if (targetWard) {
      targetWard.occupied_beds = nextOcc;
      setBedStatus([...bedStatus]);
    }

    const payload = {
      ward_type: wardType,
      total_beds: total,
      occupied_beds: nextOcc
    };

    if (!isOnline) {
      queueOfflineAction(`${API_BASE}/beds/status`, payload, 'Beds status');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/beds/status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        loadModuleData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to update beds');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleStaffCheckin = async () => {
    setError('');
    const payload = {
      latitude: gpsLat,
      longitude: gpsLon
    };
    if (!isOnline) {
      queueOfflineAction(`${API_BASE}/attendance/checkin`, payload, 'Roster Check-in');
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/attendance/checkin`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        loadModuleData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Check-in failed');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleStaffCheckout = async () => {
    setError('');
    if (!isOnline) {
      queueOfflineAction(`${API_BASE}/attendance/checkout`, {}, 'Roster Check-out');
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/attendance/checkout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        loadModuleData();
      } else {
        const data = await res.json();
        setError(data.detail || 'Check-out failed');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const submitDiagnosticsAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTestId) return;
    setFormSuccess('');
    setError('');

    const payload = {
      test_id: selectedTestId,
      status: diagStatus,
      reagent_stock: reagentQty,
      notes: diagNotes
    };

    if (!isOnline) {
      queueOfflineAction(`${API_BASE}/diagnostics/audit`, payload, 'Diagnostic Audit');
      setDiagNotes('');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/diagnostics/audit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setFormSuccess('Diagnostic audit checklist submitted!');
        setDiagNotes('');
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to submit audit');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      const res = await fetch(`${API_BASE}/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        loadModuleData();
      }
    } catch (err) {
      console.error('Error resolving alert', err);
    }
  };

  const getMyAttendanceStatus = () => {
    if (attendance.length === 0) return t('Not Marked');
    // For simplicity return latest record
    return attendance[attendance.length - 1].status.toUpperCase();
  };

  // Multilingual translation lookup (Static Dictionary with Sarvam Dynamic fallback)
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
                <Activity size={48} color="#10b981" style={{ margin: '0 auto 12px' }} />
                <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Swasth AI — Facility Portal</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
                  Log clinical details and medicine logistics
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
                    placeholder="e.g. pharmacist_phc1"
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
                  Access Portal
                </button>
              </form>

              <div style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Seed roles:<br />
                Pharmacist: <code>pharmacist_phc1</code> / <code>password123</code><br />
                Nurse: <code>nurse_phc1</code> / <code>password123</code><br />
                Med Officer: <code>mo_phc1</code> / <code>password123</code>
              </div>
            </div>
          </div>
          <footer style={{ padding: '16px', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Swasth AI © 2026. India Frontline Health Public Good.
          </footer>
        </div>
      ) : (
        /* Logged In Monolithic UI */
        <div style={{ flex: 1, display: 'flex', flexDirection: 'row' }}>
          {/* Navigation Sidebar */}
          <aside className="glass" style={{ width: '260px', margin: '16px 0 16px 16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '12px', borderRight: '1px solid var(--border)' }}>
            <div style={{ padding: '24px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '32px' }}>
                <Activity size={28} color="#10b981" />
                <span style={{ fontWeight: 700, letterSpacing: '0.5px' }}>SWASTH PORTAL</span>
              </div>
              
              <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {[
                  { id: 'dashboard', label: t('Dashboard'), icon: Activity },
                  { id: 'inventory', label: t('Inventory (Stock)'), icon: Package },
                  { id: 'footfall', label: t('Patient Footfall'), icon: FileText },
                  { id: 'beds', label: t('Bed Wards'), icon: Shield },
                  { id: 'attendance', label: t('Attendance'), icon: Clock },
                  { id: 'diagnostics', label: t('Diagnostics Audit'), icon: CheckCircle2 }
                ].map(item => (
                  <button
                    key={item.id}
                    onClick={() => { setActiveTab(item.id); setFormSuccess(''); setError(''); }}
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
            </div>
            
            <div style={{ padding: '16px', borderTop: '1px solid var(--border)' }}>
              {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--primary)', color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
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
            {/* Header info */}
            {user && (
              <div className="glass" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '12px' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{t('Frontline Health Center Portal')}</h2>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Lucknow District | Block: Mohanlalganj</p>
                </div>
                
                {/* Language & Connectivity Selector */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  {/* Offline Warning Banner */}
                  {!isOnline ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', padding: '6px 12px', borderRadius: '100px', background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', fontWeight: 600 }}>
                      <WifiOff size={14} /> {t('Offline Mode')} ({offlineQueue.length} queued)
                    </span>
                  ) : (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', padding: '6px 12px', borderRadius: '100px', background: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 600 }}>
                      <Wifi size={14} /> {t('Online Mode')}
                    </span>
                  )}

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
            )}

            {/* Sync success toast */}
            {toastMessage && (
              <div className="fade-in shadow-glow" style={{ background: 'var(--primary)', color: '#000', padding: '12px 20px', borderRadius: '8px', fontWeight: 700, fontSize: '0.9rem', position: 'fixed', top: '24px', right: '24px', zIndex: 1100 }}>
                {toastMessage}
              </div>
            )}

            {/* Active Alerts Banner */}
            {alerts.length > 0 && (
              <div className="glass fade-in" style={{ padding: '12px 16px', borderLeft: '4px solid var(--danger)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertOctagon size={14} /> {t('ACTIVE FACILITY ALERTS')}
                </span>
                <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '4px' }}>
                  {alerts.map(a => (
                    <div key={a.alert_id} className="glass" style={{ padding: '10px 14px', minWidth: '280px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(239, 68, 68, 0.05)', borderRadius: '6px', fontSize: '0.8rem' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden' }}>
                        <span style={{ fontWeight: 600, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{a.title}</span>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{a.message}</span>
                      </div>
                      <button 
                        onClick={() => handleResolveAlert(a.alert_id)} 
                        style={{ padding: '4px 8px', background: 'var(--primary)', color: '#000', borderRadius: '4px', cursor: 'pointer', fontWeight: 700 }}
                      >
                        Resolve
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error & Success Messages */}
            {error && (
              <div className="fade-in" style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid var(--danger)', padding: '14px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <AlertTriangle color="#ef4444" size={20} />
                <span style={{ color: '#ef4444', fontWeight: 500, fontSize: '0.9rem' }}>{error}</span>
              </div>
            )}
            {formSuccess && (
              <div className="fade-in" style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid var(--primary)', padding: '14px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 color="#10b981" size={20} />
                <span style={{ color: '#10b981', fontWeight: 500, fontSize: '0.9rem' }}>{formSuccess}</span>
              </div>
            )}

            {/* Dashboard View */}
            {activeTab === 'dashboard' && facDashboard && (
              <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Highlights grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px', borderLeft: facDashboard.stock.stockouts > 0 ? '3px solid var(--danger)' : '1px solid var(--border)' }}>
                    <Package size={24} color="#10b981" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Inventory Health')}</span>
                    <span style={{ fontSize: '1.6rem', fontWeight: 700 }}>{facDashboard.stock.total_skus} SKUs</span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{facDashboard.stock.below_threshold} Low</span> | <span style={{ color: facDashboard.stock.stockouts > 0 ? '#ef4444' : 'inherit' }}>{facDashboard.stock.stockouts} Out</span>
                      <span style={{ display: 'block', marginTop: '2px', color: 'var(--primary)' }}>↓ 2% vs last week</span>
                    </div>
                  </div>
                  <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px', borderLeft: facDashboard.beds.occupancy_rate > 85.0 ? '3px solid var(--danger)' : '1px solid var(--border)' }}>
                    <Shield size={24} color="#3b82f6" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Bed Occupancy')}</span>
                    <span style={{ fontSize: '1.6rem', fontWeight: 700 }}>{facDashboard.beds.occupied_beds} / {facDashboard.beds.total_beds}</span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{facDashboard.beds.occupancy_rate}% occupied</span>
                      <span style={{ display: 'block', marginTop: '2px', color: 'var(--primary)' }}>→ vs yesterday</span>
                    </div>
                  </div>
                  <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px', borderLeft: facDashboard.attendance.attendance_rate < 80.0 ? '3px solid var(--danger)' : '1px solid var(--border)' }}>
                    <Clock size={24} color="#f59e0b" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Staff Attendance')}</span>
                    <span style={{ fontSize: '1.6rem', fontWeight: 700 }}>{facDashboard.attendance.present} / {facDashboard.attendance.scheduled}</span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{facDashboard.attendance.attendance_rate}% present rate</span>
                      <span style={{ display: 'block', marginTop: '2px', color: 'var(--primary)' }}>↑ vs roster</span>
                    </div>
                  </div>
                  <div className="glass" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px', borderLeft: facDashboard.diagnostics.compliance_rate < 80.0 ? '3px solid var(--danger)' : '1px solid var(--border)' }}>
                    <CheckCircle2 size={24} color="var(--info)" />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Diagnostic Compliance')}</span>
                    <span style={{ fontSize: '1.6rem', fontWeight: 700 }}>{facDashboard.diagnostics.available_total} / {facDashboard.diagnostics.mandated_total}</span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{facDashboard.diagnostics.compliance_rate}% compliance</span>
                      <span style={{ display: 'block', marginTop: '2px', color: 'var(--primary)' }}>→ vs last week</span>
                    </div>
                  </div>
                </div>

                {/* Score & Footfall Section */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  {/* AI Score */}
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <h3 style={{ fontWeight: 600, fontSize: '1.1rem' }}>{t('Facility AI Composite Performance')}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                      <div style={{ width: '90px', height: '90px', borderRadius: '50%', border: '6px solid var(--primary-light)', borderTopColor: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{facDashboard.composite_score}</span>
                      </div>
                      <div>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Status:')} </span>
                        <span style={{ fontWeight: 600, color: facDashboard.is_flagged ? '#ef4444' : '#10b981' }}>
                          {facDashboard.is_flagged ? 'Flagged / Action Needed' : t('Adequate Oversight')}
                        </span>
                        {facDashboard.is_flagged && facDashboard.flag_reasons.length > 0 && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                            {facDashboard.flag_reasons.map((r: string) => (
                              <div key={r}>• {r}</div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Footfall today */}
                  <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <h3 style={{ fontWeight: 600, fontSize: '1.1rem' }}>{t('Patient Footfall Today')}</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div className="glass" style={{ padding: '14px', background: 'rgba(255,255,255,0.01)' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('OPD Consultations')}</span>
                        <span style={{ fontSize: '1.6rem', fontWeight: 700, display: 'block', marginTop: '4px' }}>{facDashboard.footfall.opd}</span>
                      </div>
                      <div className="glass" style={{ padding: '14px', background: 'rgba(255,255,255,0.01)' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('IPD Admissions')}</span>
                        <span style={{ fontSize: '1.6rem', fontWeight: 700, display: 'block', marginTop: '4px' }}>{facDashboard.footfall.ipd}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Operations guide checklist */}
                <div className="glass" style={{ padding: '24px', background: 'rgba(16, 185, 129, 0.02)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <h3 style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--primary)' }}>{t('Operational Routine Checklist')}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Check size={16} color="var(--primary)" />
                      <span>Log into Attendance panel daily before 10:00 AM to mark roster presence.</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Check size={16} color="var(--primary)" />
                      <span>Record drug dispensing logs in the Inventory Panel immediately upon prescription fulfillment.</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Check size={16} color="var(--primary)" />
                      <span>Admit/discharge patients from General & Maternity bed grids to keep live occupancy accurate.</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Check size={16} color="var(--primary)" />
                      <span>Perform diagnostic audits and report FDSI test availability metrics weekly.</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Inventory View */}
            {activeTab === 'inventory' && (
              <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '20px' }}>
                {/* Main Stock Table */}
                <div className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{t('Medicine Inventory Ledger')}</h3>
                  
                  <div style={{ overflowX: 'auto', maxHeight: '550px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                          <th style={{ padding: '12px' }}>{t('Medicine Name')}</th>
                          <th style={{ padding: '12px' }}>{t('Batch')}</th>
                          <th style={{ padding: '12px' }}>{t('Quantity')}</th>
                          <th style={{ padding: '12px' }}>{t('Status')}</th>
                          <th style={{ padding: '12px' }}>{t('AI Stockout Projection')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stockItems.map(item => {
                          const isStockout = item.quantity === 0;
                          const isLow = item.quantity < item.min_threshold;
                          let statusText = 'Adequate';
                          let statusColor = '#10b981';
                          let bgColor = 'rgba(16, 185, 129, 0.1)';
                          
                          if (isStockout) {
                            statusText = 'Stockout';
                            statusColor = '#ef4444';
                            bgColor = 'rgba(239, 68, 68, 0.1)';
                          } else if (isLow) {
                            statusText = 'Low Stock';
                            statusColor = '#f59e0b';
                            bgColor = 'rgba(245, 158, 11, 0.1)';
                          }
                          
                          // Find forecast projection
                          const fc = stockForecasts.find(x => x.sku_id === item.sku_id);
                          const daysOut = fc ? fc.days_until_stockout : null;
                          const dateOut = fc ? fc.projected_stockout_date : null;
                          
                          let fcText = 'Checking...';
                          let fcColor = 'var(--text-secondary)';
                          
                          if (daysOut !== null) {
                            if (daysOut === 999) {
                              fcText = t('Safe (>30 days)');
                              fcColor = '#10b981';
                            } else if (daysOut < 7) {
                              fcText = `Critical: ${daysOut} days (${dateOut})`;
                              fcColor = '#ef4444';
                            } else if (daysOut < 15) {
                              fcText = `Warning: ${daysOut} days (${dateOut})`;
                              fcColor = '#f59e0b';
                            } else {
                              fcText = `${daysOut} days (${dateOut})`;
                              fcColor = 'var(--text-secondary)';
                            }
                          }
                          
                          return (
                            <tr key={item.sku_id} style={{ borderBottom: '1px solid var(--border)' }}>
                              <td style={{ padding: '12px', fontWeight: 500 }}>{item.medicine_name}</td>
                              <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{item.batch_no}</td>
                              <td style={{ padding: '12px', fontWeight: 600 }}>{item.quantity} {item.unit}</td>
                              <td style={{ padding: '12px' }}>
                                <span style={{ padding: '4px 8px', borderRadius: '4px', background: bgColor, color: statusColor, fontSize: '0.75rem', fontWeight: 600 }}>
                                  {statusText}
                                </span>
                              </td>
                              <td style={{ padding: '12px', fontWeight: 600, color: fcColor }}>
                                {fcText}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Logistics Action Panel */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {/* Log stock movement */}
                  <div className="glass" style={{ padding: '24px' }}>
                    <h4 style={{ fontWeight: 600, marginBottom: '16px' }}>{t('Log Stock Movement')}</h4>
                    <form onSubmit={submitStockMovement} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Select SKU')}</label>
                        <select 
                          value={movSkuId} 
                          onChange={(e) => setMovSkuId(e.target.value)}
                          style={{ padding: '10px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                        >
                          {stockItems.map(x => (
                            <option key={x.sku_id} value={x.sku_id} style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>
                              {x.medicine_name} ({x.batch_no})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Movement Type')}</label>
                        <select 
                          value={movType} 
                          onChange={(e) => setMovType(e.target.value)}
                          style={{ padding: '10px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                        >
                          <option value="out" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Dispensed (Out)</option>
                          <option value="in" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Received (In)</option>
                          <option value="wastage" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Wastage</option>
                          <option value="expired" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Expired</option>
                        </select>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Quantity')}</label>
                        <input 
                          type="number" 
                          min="1" 
                          value={movQty} 
                          onChange={(e) => setMovQty(parseInt(e.target.value) || 1)}
                          style={{ padding: '10px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                        />
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('Notes')}</label>
                        <input 
                          type="text" 
                          value={movNote} 
                          onChange={(e) => setMovNote(e.target.value)}
                          placeholder="e.g. Patient prescription"
                          style={{ padding: '10px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                        />
                      </div>

                      <button type="submit" className="glow-btn" style={{ width: '100%', padding: '10px' }}>
                        {t('Log Movement')}
                      </button>
                    </form>
                  </div>

                  {/* Register New SKU */}
                  <div className="glass" style={{ padding: '24px' }}>
                    <h4 style={{ fontWeight: 600, marginBottom: '16px' }}>{t('Register New SKU')}</h4>
                    <form onSubmit={submitRegisterSku} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <input 
                        type="text" 
                        required
                        placeholder={t('Medicine Name')} 
                        value={newSkuName}
                        onChange={(e) => setNewSkuName(e.target.value)}
                        style={{ padding: '10px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                      />
                      <input 
                        type="text" 
                        placeholder="Generic Name" 
                        value={newSkuGeneric}
                        onChange={(e) => setNewSkuGeneric(e.target.value)}
                        style={{ padding: '10px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)' }}
                      />
                      <button type="submit" className="glow-btn" style={{ width: '100%', padding: '10px' }}>
                        {t('Add to Inventory')}
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            )}

            {/* Patient Footfall View */}
            {activeTab === 'footfall' && (
              <div className="fade-in" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '32px 0' }}>
                <div className="glass" style={{ width: '100%', maxWidth: '480px', padding: '32px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText color="var(--primary)" /> {t('Log Patient Counts')}
                  </h3>
                  
                  <form onSubmit={submitFootfall} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Department')}</label>
                      <select 
                        value={footfallDept} 
                        onChange={(e) => setFootfallDept(e.target.value)}
                        style={{ padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                      >
                        <option value="General" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>General OPD</option>
                        <option value="Emergency" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Emergency Ward</option>
                        <option value="Maternity" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Maternity Clinic</option>
                        <option value="Pediatric" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Pediatric Ward</option>
                      </select>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('OPD Count')}</label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <button type="button" onClick={() => setOpdCount(x => Math.max(0, x - 5))} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', cursor: 'pointer' }}>-</button>
                          <span style={{ fontSize: '1.2rem', fontWeight: 600, flex: 1, textAlign: 'center' }}>{opdCount}</span>
                          <button type="button" onClick={() => setOpdCount(x => x + 5)} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', cursor: 'pointer' }}>+</button>
                        </div>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('IPD Count')}</label>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <button type="button" onClick={() => setIpdCount(x => Math.max(0, x - 1))} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', cursor: 'pointer' }}>-</button>
                          <span style={{ fontSize: '1.2rem', fontWeight: 600, flex: 1, textAlign: 'center' }}>{ipdCount}</span>
                          <button type="button" onClick={() => setIpdCount(x => x + 1)} style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '6px', cursor: 'pointer' }}>+</button>
                        </div>
                      </div>
                    </div>

                    <button type="submit" className="glow-btn" style={{ width: '100%', padding: '12px' }}>
                      {t("Submit Today's Count")}
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* Beds View */}
            {activeTab === 'beds' && (
              <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{t('Ward Bed Management')}</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                  {bedStatus.map(w => {
                    const percentage = (w.occupied_beds / w.total_beds * 100) || 0;
                    let alertColor = '#10b981';
                    if (percentage > 85.0) alertColor = '#ef4444';
                    else if (percentage > 60.0) alertColor = '#f59e0b';
                    
                    return (
                      <div key={w.status_id} className="glass" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{w.ward_type} Ward</span>
                          <span style={{ color: alertColor, fontWeight: 700 }}>{percentage.toFixed(0)}% {t('Occupied')}</span>
                        </div>
                        
                        {/* Progress Bar */}
                        <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${percentage}%`, background: alertColor, transition: 'width 0.3s' }}></div>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            {w.occupied_beds} {t('occupied /')} {w.total_beds} {t('total')}
                          </span>
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button 
                              onClick={() => handleBedAdjustment(w.ward_type, -1, w.occupied_beds, w.total_beds)}
                              className="glass" 
                              style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', borderRadius: '6px' }}
                            >
                              <Minus size={16} />
                            </button>
                            <button 
                              onClick={() => handleBedAdjustment(w.ward_type, 1, w.occupied_beds, w.total_beds)}
                              className="glass" 
                              style={{ width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', borderRadius: '6px' }}
                            >
                              <Plus size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Attendance View */}
            {activeTab === 'attendance' && (
              <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px', alignItems: 'center', padding: '32px 0' }}>
                <div className="glass" style={{ width: '100%', maxWidth: '440px', padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px', textAlign: 'center' }}>
                  <Clock size={48} color="var(--primary)" />
                  <div>
                    <h3 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{t('Roster Check-In / Out')}</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
                      {t('Mark daily arrival and departure at your health post')}
                    </p>
                  </div>

                  <div className="glass" style={{ padding: '16px 32px', width: '100%', background: 'rgba(255,255,255,0.02)' }}>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Roster Status:')} </span>
                    <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{getMyAttendanceStatus()}</span>
                  </div>

                  {/* Real-time location tracking status */}
                  <div className="glass" style={{ padding: '12px 24px', width: '100%', display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                      📍 {t('Realtime Geolocation Status')}
                    </span>
                    {gpsStatus === 'active' && gpsLat !== null && gpsLon !== null ? (
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>
                        Lat: {gpsLat.toFixed(6)}, Lon: {gpsLon.toFixed(6)}
                      </span>
                    ) : gpsStatus === 'searching' ? (
                      <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--warning)', animation: 'pulse 1.5s infinite' }}>
                        {t('Acquiring live coordinates...')}
                      </span>
                    ) : gpsStatus === 'denied' ? (
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--danger)' }}>
                        ⚠️ {t('Location Access Denied')}
                      </span>
                    ) : (
                      <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)' }}>
                        {t('Location unavailable')}
                      </span>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '16px', width: '100%' }}>
                    <button 
                      onClick={handleStaffCheckin} 
                      className="glow-btn" 
                      style={{ flex: 1, padding: '14px', background: '#10b981', color: '#000', boxShadow: 'none' }}
                    >
                      {t('Check In')}
                    </button>
                    <button 
                      onClick={handleStaffCheckout} 
                      className="glow-btn" 
                      style={{ flex: 1, padding: '14px', background: '#3b82f6', color: '#fff', boxShadow: 'none' }}
                    >
                      {t('Check Out')}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Diagnostics View */}
            {activeTab === 'diagnostics' && (
              <div className="fade-in" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '32px 0' }}>
                <div className="glass" style={{ width: '100%', maxWidth: '480px', padding: '32px' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 color="var(--primary)" /> {t('Diagnostic Audit Checklist')}
                  </h3>

                  <form onSubmit={submitDiagnosticsAudit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Select Test Category')}</label>
                      <select 
                        value={selectedTestId} 
                        onChange={(e) => setSelectedTestId(e.target.value)}
                        style={{ padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                      >
                        {diagnosticsCatalog.map(x => (
                          <option key={x.test_id} value={x.test_id} style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>
                            {x.test_name} {x.is_mandated ? '(FDSI Mandated)' : ''}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Availability Status')}</label>
                      <select 
                        value={diagStatus} 
                        onChange={(e) => setDiagStatus(e.target.value)}
                        style={{ padding: '12px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                      >
                        <option value="available" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Available ✅</option>
                        <option value="limited" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Limited Stock ⚠️</option>
                        <option value="unavailable" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Unavailable ❌</option>
                      </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Reagent Stock (Vials/Tests remaining)')}</label>
                      <input 
                        type="number" 
                        value={reagentQty} 
                        onChange={(e) => setReagentQty(parseInt(e.target.value) || 0)}
                        style={{ padding: '12px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)' }}
                      />
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('Auditor Notes')}</label>
                      <textarea 
                        value={diagNotes} 
                        onChange={(e) => setDiagNotes(e.target.value)}
                        placeholder="Reagent status remarks..."
                        rows={3}
                        style={{ padding: '12px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-primary)', resize: 'none' }}
                      />
                    </div>

                    <button type="submit" className="glow-btn" style={{ width: '100%', padding: '12px' }}>
                      {t('Submit Audit')}
                    </button>
                  </form>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
