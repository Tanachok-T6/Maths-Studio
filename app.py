import streamlit as st
import streamlit.components.v1 as components
import datetime
from zoneinfo import ZoneInfo
import threading
import requests # เพิ่มสำหรับดึง IP กรณี headers ปกติถูกปิดกั้น

# ==========================================
# 1. การตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรกเสมอ)
# ==========================================
st.set_page_config(page_title="Maths Studio", page_icon="🔢", layout="wide")

# ฟังก์ชันดึง IP Address ของผู้ใช้งาน
def get_user_ip():
    # พยายามดึงจาก Header ของ Streamlit (ใช้ได้ดีบน Cloud/Proxies)
    headers = st.context.headers
    if "X-Forwarded-For" in headers:
        return headers["X-Forwarded-For"].split(",")[0]
    # ถ้าไม่ได้ ให้ใช้บริการภายนอกช่วย (fallback)
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Unknown"

# ==========================================
# 2. ระบบ Log ตรวจจับคนเข้า-ออกเว็บ + IP
# ==========================================
class ActiveUserTracker:
    def __init__(self):
        self.active_users = 0
        self.lock = threading.Lock()

    def add_user(self):
        with self.lock:
            self.active_users += 1
            return self.active_users

    def remove_user(self):
        with self.lock:
            self.active_users -= 1
            return self.active_users

@st.cache_resource
def get_tracker():
    return ActiveUserTracker()

class UserSession:
    def __init__(self, tracker, ip):
        self.tracker = tracker
        self.ip = ip
        current_users = self.tracker.add_user()
        now = datetime.datetime.now(ZoneInfo("Asia/Bangkok")).strftime('%H:%M:%S')
        # แจ้ง Log ใน Console/Server ว่า IP ไหนเข้ามา
        print(f"[{now}] 🟢 IP: {self.ip} เข้าใช้งาน | ออนไลน์อยู่: {current_users} คน")

    def __del__(self):
        current_users = self.tracker.remove_user()
        import datetime
        from zoneinfo import ZoneInfo
        now = datetime.datetime.now(ZoneInfo("Asia/Bangkok")).strftime('%H:%M:%S')
        print(f"[{now}] 🔴 IP: {self.ip} ออกจากแอป | ออนไลน์เหลือ: {current_users} คน")

tracker = get_tracker()
user_ip = get_user_ip() # ดึง IP ของเครื่องปัจจุบัน

if 'session_tracker' not in st.session_state:
    st.session_state.session_tracker = UserSession(tracker, user_ip)

# ==========================================
# 3. แถบเครื่องมือด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("IMAGE/logo_CRMS6.png", use_container_width=True)
        except Exception:
            pass

    st.header("🔢 Maths Studio")
    # แสดง IP Address ที่ Sidebar ให้ผู้ใช้เห็น
    st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #ddd;'>🌐 IP ของคุณ: <b>{user_ip}</b></div>", unsafe_allow_html=True)
    st.write("")
    
    grid_choice = st.radio(
        "เลือกขนาดตาราง:",["2x2 (Basic)", "3x3 (Standard)", "4x4 (Advanced)", "5x5 (Expert)"], 
        index=0
    )
    st.markdown("---")
    st.info("💡 วิธีใช้: พิมพ์ตัวเลขหรือพพหุนามลงในช่องสีขาว ผลลัพธ์จะคำนวณและจัดกลุ่มให้อัตโนมัติ")

# ปรับแต่งพื้นหลังและ Title (CSS)
st.markdown("""
<style>
    .stApp, .stApp > header { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    .school-title { 
        position: fixed; top: 14px; left: 50%; transform: translateX(-50%); 
        z-index: 999999; font-size: 26px; font-weight: 800; color: #333 !important; 
        pointer-events: none; 
    }
</style>
<div class="school-title">CRMS6</div>
""", unsafe_allow_html=True)

# (ส่วนที่ 4, 5 ของโค้ดเดิม คงที่ไว้ ไม่มีการเปลี่ยนแปลง)
size = int(grid_choice.split("x")[0])
vlines = "".join([f'<div class="line vline" style="left: {80 + (i * 100)}px;"></div>' for i in range(size)])
hlines = "".join([f'<div class="line hline" style="top: {80 + (i * 100)}px;"></div>' for i in range(size)])
top_inputs = "".join([f'<div class="input-cell"><input id="top{i}" class="gamebox" placeholder="T{i+1}" autocomplete="off"></div>' for i in range(size)])
left_and_results = ""
for j in range(size - 1, -1, -1):
    left_and_results += f'<div class="input-cell"><input id="left{j}" class="gamebox" placeholder="L{j+1}" autocomplete="off"></div>'
    for i in range(size):
        left_and_results += f'<div class="result-cell" id="res_{j}_{i}"></div>'

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500;700&family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Sarabun', sans-serif; margin: 0; padding: 20px 0; background: transparent; }}
        .scroll-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; display: flex; justify-content: center; padding-bottom: 20px; }}
        .app-container {{ background: #ffffff; padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); display: inline-flex; flex-direction: column; align-items: center; min-width: max-content; }}
        .grid-wrapper {{ display: grid; grid-template-columns: 80px repeat({size}, 100px); grid-template-rows: 80px repeat({size}, 100px); position: relative; z-index: 2; }}
        .lines-container {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 1; }}
        .line {{ position: absolute; background-color: #000; }}
        .vline {{ width: 2px; top: 10px; bottom: 10px; }}
        .hline {{ height: 2px; left: 10px; right: 10px; }}
        .input-cell, .result-cell {{ display: flex; justify-content: center; align-items: center; z-index: 2; }}
        input.gamebox {{ width: 60px; height: 40px; text-align: center; border: 1px solid #ced4da; border-radius: 8px; font-family: 'Sarabun', sans-serif; font-weight: 600; font-size: 16px; outline: none; transition: all 0.2s ease; }}
        input.gamebox:focus {{ border-color: #0d6efd; box-shadow: 0 0 0 3px rgba(13,110,253,0.25); }}
        .result-cell {{ font-size: 20px; font-weight: 700; color: #dc3545; font-family: 'Roboto Mono', monospace; }}
        #finalResultBox {{ margin-top: 30px; padding: 15px 40px; background: linear-gradient(135deg, #0d6efd, #0056b3); color: white; border-radius: 100px; font-size: 24px; font-weight: 600; display: none; text-align: center; box-shadow: 0 5px 15px rgba(13,110,253,0.3); word-break: break-all; }}
        sup {{ font-size: 0.65em; vertical-align: super; }}
    </style>
</head>
<body>
    <div class="scroll-wrapper">
        <div class="app-container">
            <div class="grid-wrapper">
                <div class="lines-container">{vlines}{hlines}</div>
                <div></div>
                {top_inputs}
                {left_and_results}
            </div>
            <div id="finalResultBox"></div>
        </div>
    </div>
<script>
    const size = {size};
    function parse(s) {{ 
        s = s.toLowerCase().replace(/\\s/g, ''); 
        if(!s) return {{c:0, p:0}}; 
        if(!s.includes('x')) return {{c:parseFloat(s)||0, p:0}}; 
        let parts = s.split('x'); 
        let c = parts[0]==='' ? 1 : (parts[0]==='-' ? -1 : parseFloat(parts[0])); 
        let p = 1; 
        if(parts[1] && parts[1].startsWith('^')) p = parseInt(parts[1].slice(1)) || 0; 
        return {{c, p}}; 
    }}
    function fmt(c, p) {{ 
        if(c===0) return ""; 
        if(p===0) return c; 
        let res = (c===1) ? "x" : (c===-1 ? "-x" : c+"x"); 
        if(p!==1) res += "<sup>"+p+"</sup>"; 
        return res; 
    }}
    function update() {{
        let tops=[], lefts=[], allFilled=true;
        for(let i=0; i<size; i++) {{ 
            let v = document.getElementById('top'+i).value; 
            if(!v) allFilled=false; 
            tops.push(parse(v)); 
        }}
        for(let j=0; j<size; j++) {{ 
            let v = document.getElementById('left'+j).value; 
            if(!v) allFilled=false; 
            lefts.push(parse(v)); 
        }}
        if(!allFilled) {{ document.getElementById('finalResultBox').style.display='none'; return; }}
        
        let finalMap={{}};
        for(let j=0; j<size; j++) {{
            for(let i=0; i<size; i++) {{
                let c = tops[i].c * lefts[j].c; 
                let p = tops[i].p + lefts[j].p;
                document.getElementById(`res_${{j}}_${{i}}`).innerHTML = fmt(c, p);
                finalMap[p] = (finalMap[p]||0) + c;
            }}
        }}
        let terms = Object.keys(finalMap).map(Number).sort((a,b)=>b-a).filter(p=>finalMap[p]!==0).map((p,i)=>{{ 
            let c=finalMap[p], s=fmt(c, p); 
            if(i>0 && c>0) return " + "+s; 
            if(c<0) return " "+s; 
            return s; 
        }});
        const box = document.getElementById('finalResultBox');
        box.innerHTML = terms.join('') || "0"; 
        box.style.display='block';
    }}
    document.querySelectorAll('input').forEach(el => el.addEventListener('input', update));
</script>
</body>
</html>
"""

height_calc = 400 + (size * 100)
components.html(html_code, height=height_calc)

# ==========================================
# 6. เวลาการเข้าสู่ระบบ
# ==========================================
time_placeholder = st.empty()
bangkok_now = datetime.datetime.now(ZoneInfo("Asia/Bangkok"))
time_str = bangkok_now.strftime('%d/%m/%Y %H:%M:%S')
time_placeholder.markdown(f"<p style='text-align: center; color: gray;'>เวลาปัจจุบัน: {time_str}</p>", unsafe_allow_html=True)