import streamlit as st
import datetime
from astropy.time import Time
from astroquery.simbad import Simbad
from astroquery.jplhorizons import Horizons

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="NEXT SPACE",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تصميم الواجهة (CSS) - ألوان فلكية (سماوي وأزرق)
st.markdown("""
<style>
    .main {
        background-color: #0a0f18;
    }
    /* تنسيق بطاقات البيانات */
    .astro-card {
        background: #111b27;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #00d4ff;
        margin: 15px 0;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
        border-bottom: 1px solid rgba(0, 212, 255, 0.1);
    }
    .card-title {
        color: #00d4ff;
        font-weight: bold;
        font-size: 1.25rem;
        margin-bottom: 10px;
    }
    .key {
        color: #88a0b5;
        font-size: 0.9rem;
        padding: 8px 5px;
    }
    .val {
        color: #ffffff;
        font-weight: 500;
        font-size: 1rem;
    }
    /* تصميم مربعات الكواكب والمجرات */
    .planet-box {
        text-align: center;
        padding: 15px;
        border-radius: 20px;
        background: rgba(0, 212, 255, 0.07);
        border: 1px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .planet-box:hover {
        background: rgba(0, 212, 255, 0.18);
        border-color: #00d4ff;
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    /* تحسين أزرار الاستكشاف */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: transparent;
        color: #00d4ff;
        border: 1px solid #00d4ff;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #0a0f18;
    }
</style>
""", unsafe_allow_html=True)

# 3. الوظائف البرمجية (Functions)
@st.cache_data(ttl=600)
def get_astro_info(name: str):
    """جلب بيانات أجرام النظام الشمسي من NASA JPL"""
    bodies = {
        "sun": "10", "mercury": "199", "venus": "299",
        "earth": "399", "mars": "499", "jupiter": "599",
        "saturn": "699", "uranus": "799", "neptune": "899"
    }
    bid = bodies.get(name.lower())
    if not bid:
        return None
    try:
        obj = Horizons(id=bid, location="500", epochs=Time.now().jd)
        eph = obj.ephemerides()[0]
        return {
            "Object": name.capitalize(),
            "RA (Right Ascension)": f"{eph['RA']:.2f}°",
            "DEC (Declination)": f"{eph['DEC']:.2f}°",
            "Distance (AU)": f"{eph['delta']:.4f}",
            "Apparent Mag": f"{eph['V']:.2f}",
            "Source": "JPL Horizons"
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_deep_space_info(name: str):
    """جلب بيانات النجوم والمجرات باستخدام مكتبة Simbad"""
    try:
        result = Simbad.query_object(name)
        if result is not None:
            return {
                "Object": name.capitalize(),
                "RA (J2000)": str(result['RA'][0]),
                "DEC (J2000)": str(result['DEC'][0]),
                "Coordinates": "Equatorial",
                "Source": "Simbad Astronomical Database"
            }
        return None
    except Exception:
        return None

def format_data_card(title, data: dict):
    """تحويل البيانات إلى بطاقة HTML أنيقة"""
    if not data:
        return ""
    rows = "".join([
        f"<tr><td class='key'>{k}</td><td class='val'>{v}</td></tr>"
        for k, v in data.items() if k != "Source"
    ])
    return f"""
    <div class='astro-card'>
        <div class='card-title'>🔭 {title} Real-time Data</div>
        <table style='width:100%; border-collapse: collapse;'>{rows}</table>
        <div style='font-size:0.7rem; color:#445; margin-top:10px; text-align:right;'>Data: {data.get('Source')}</div>
    </div>
    """

# 4. بناء هيكل الصفحة
st.title("🚀 NEXT SPACE BOT")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# قسم استكشاف الكواكب (رسومات وأزرار)
st.subheader("☀️ Solar System Exploration")
planet_icons = {
    "Sun": "https://cdn-icons-png.flaticon.com/128/2698/2698194.png",
    "Mercury": "https://cdn-icons-png.flaticon.com/128/3594/3594165.png",
    "Venus": "https://cdn-icons-png.flaticon.com/128/3594/3594240.png",
    "Earth": "https://cdn-icons-png.flaticon.com/128/2240/2240608.png",
    "Mars": "https://cdn-icons-png.flaticon.com/128/3594/3594304.png",
    "Jupiter": "https://cdn-icons-png.flaticon.com/128/3594/3594336.png",
    "Saturn": "https://cdn-icons-png.flaticon.com/128/3594/3594359.png",
    "Uranus": "https://cdn-icons-png.flaticon.com/128/3594/3594406.png",
    "Neptune": "https://cdn-icons-png.flaticon.com/128/3594/3594432.png"
}

# إنشاء شبكة الكواكب
cols = st.columns(len(planet_icons))
selected_object = None

for i, (name, url) in enumerate(planet_icons.items()):
    with cols[i]:
        st.markdown(
            f"<div class='planet-box'><img src='{url}' width='55'><br>"
            f"<b><small style='color:#00d4ff;'>{name}</small></b></div>",
            unsafe_allow_html=True
        )
        if st.button("Explore", key=f"btn_{name}"):
            selected_object = name

# قسم استكشاف النجوم والمجرات
st.subheader("🌌 Deep Space (Galaxies & Stars)")
deep_icons = {
    "Andromeda": "https://cdn-icons-png.flaticon.com/128/8939/8939527.png",
    "Sirius": "https://cdn-icons-png.flaticon.com/128/1806/1806963.png",
    "Betelgeuse": "https://cdn-icons-png.flaticon.com/128/1806/1806963.png",
    "Triangulum": "https://cdn-icons-png.flaticon.com/128/8939/8939527.png",
    "Vega": "https://cdn-icons-png.flaticon.com/128/1806/1806963.png"
}

cols_deep = st.columns(len(deep_icons))
for i, (name, url) in enumerate(deep_icons.items()):
    with cols_deep[i]:
        st.markdown(
            f"<div class='planet-box'><img src='{url}' width='55'><br>"
            f"<b><small style='color:#00d4ff;'>{name}</small></b></div>",
            unsafe_allow_html=True
        )
        if st.button("Explore", key=f"btn_{name}"):
            selected_object = name

# معالجة الضغط على الكواكب أو المجرات من الأزرار
if selected_object:
    st.session_state.chat_history.append({"role": "user", "content": f"Show me data for {selected_object}"})
    
    # محاولة جلب البيانات (كوكب أو نجم/مجرة)
    data = get_astro_info(selected_object)
    if not data:
        data = get_deep_space_info(selected_object)
        
    if data:
        card_html = format_data_card(selected_object, data)
        st.session_state.chat_history.append({"role": "assistant", "content": card_html})
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": "Could not fetch data."})

st.divider()

# 5. منطقة الدردشة والبحث
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"], unsafe_allow_html=True)

# شريط البحث اليدوي (أسفل الصفحة)
if prompt_input := st.chat_input("Search for planets, stars, or galaxies (e.g., Mars, Andromeda, Sirius)..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        found = False
        
        # 1. البحث في الكواكب أولاً
        for p in planet_icons.keys():
            if p.lower() in prompt_input.lower():
                data = get_astro_info(p)
                res = format_data_card(p, data)
                st.markdown(res, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": res})
                found = True
                break
        
        # 2. البحث في النجوم والمجرات إذا لم يكن كوكباً
        if not found:
            data = get_deep_space_info(prompt_input)
            if data:
                res = format_data_card(prompt_input.capitalize(), data)
                st.markdown(res, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": res})
                found = True

        # 3. في حال عدم العثور على أي نتيجة
        if not found:
            response = "🛰️ I couldn't find data for that object. Please check the spelling or try a known planet, star, or galaxy."
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# 6. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/128/2056/2056411.png", width=80)
    st.header("📊 Dashboard")
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.rerun()
    st.divider()
    st.caption("Live connection to JPL Horizons & Simbad active.")

# 7. التذييل (Footer)
st.markdown("""
<div style='border:2px solid #00d4ff; padding:20px; border-radius:15px;
background:rgba(0, 212, 255, 0.05); margin-top:60px; direction:ltr;'>
    <div style='color:#00d4ff; font-weight:bold; text-align:center; margin-bottom:15px; font-size:1.2rem;'>
        Working Team & Supervision
    </div>
    <div style='display:flex; justify-content:space-around; text-align:center; font-size:0.95rem; flex-wrap:wrap;'>
        <div><b style='color:#81b1c9;'>Student</b><br><span style='color:white;'>Doaa Rashid Ahmed</span></div>
        <div><b style='color:#81b1c9;'>Supervised by</b><br><span style='color:white;'>COMPUTER DOCTOR<br>Dr. Imad J. Mohammed</span></div>
    </div>
    <div style='text-align:center; color:#445; font-size:0.75rem; margin-top:20px; border-top:1px solid rgba(0,212,255,0.1); padding-top:10px;'>
        © 2026 Department of Astronomy and Space - University of Baghdad
    </div>
</div>
""", unsafe_allow_html=True)
