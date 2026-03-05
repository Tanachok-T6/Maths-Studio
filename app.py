import streamlit as st
import streamlit.components.v1 as components
import datetime
from zoneinfo import ZoneInfo
import threading
import requests

# ==========================================
# 1. ระบบ Log และ Tracking (เข้า-ออก และ IP)
# ==========================================
class GlobalTracker:
    def __init__(self):
        self.active_count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.active_count += 1
            return self.active_count

    def decrement(self):
        with self.lock:
            self.active_count -= 1
            return self.active_count

@st.cache_resource
def get_global_tracker():
    return GlobalTracker()

def get_user_ip():
    try:
        # พยายามดึงจาก Header (Cloud)
        headers = st.context.headers
        if "X-Forwarded-For" in headers:
            return headers["X-Forwarded-For"].split(",")[0]
        # Fallback ดึงจาก API ภายนอก
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown IP"

# คลาสตรวจจับ Session (เมื่อคนปิดแถบ __del__ จะทำงานในบางกรณีบน Server)
class SessionMonitor:
    def __init__(self, tracker, ip):
        self.tracker = tracker
        self.ip = ip
        self.start_time = datetime.datetime.now(ZoneInfo("Asia/Bangkok")).strftime('%H:%M:%S')
        count = self.tracker.increment()
        print(f"🟢 [ENTRY] IP: {self.ip} | เวลา: {self.start_time} | ออนไลน์อยู่: {count} คน")

    def __del__(self):
        count = self.tracker.decrement()
        now = datetime.datetime.now(ZoneInfo("Asia/Bangkok")).strftime('%H:%M:%S')
        print(f"🔴 [EXIT]  IP: {self.ip} | เวลา: {now} | ออนไลน์เหลือ: {count} คน")

# เรียกใช้งาน Tracker
global_tracker = get_global_tracker()
user_ip = get_user_ip()

if 'monitor' not in st.session_state:
    st.session_state.monitor = SessionMonitor(global_tracker, user_ip)

# ==========================================
# 2. การตั้งค่าหน้าจอและ UI
# ==========================================
st.set_page_config(page_title="Maths Studio Pro", page_icon="🔢", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    /* ส่วนหัวด้านบน - ตัวหนังสือสีขาว */
    .school-title { 
        position: fixed; top: 14px; left: 50%; transform: translateX(-50%); 
        z-index: 999999; font-size: 26px; font-weight: 800; 
        color: #FFFFFF !important; pointer-events: none; 
    }
    /* Sidebar - ตัวหนังสือสีดำ */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    .ip-box { 
        background-color: #f0f2f6; padding: 10px; border-radius: 10px; 
        text-align: center; border: 1px solid #ddd; margin-bottom: 10px;
    }
</style>
<div class="school-title">🏫 โรงเรียนเทศบาล 6 นครเชียงราย</div>
""", unsafe_allow_html=True)

with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image("IMAGE/logo_CRMS6.png", use_container_width=True)
    
    st.header("🔢 Maths Studio")
    
    # แสดงข้อมูล IP และจำนวนคนออนไลน์
    st.markdown(f"""
    <div class="ip-box">
        <small>🌐 IP Address:</small><br><b>{user_ip}</b><br>
        <small>👥 ออนไลน์ขณะนี้: <b>{global_tracker.active_count} คน</b></small>
    </div>
    """, unsafe_allow_html=True)

    grid_choice = st.radio("เลือกขนาดตาราง:",["2x2 (Basic)", "3x3 (Standard)", "4x4 (Advanced)", "5x5 (Expert)"], index=0)
    st.markdown("---")
    st.info("💡 วิธีใช้: พิมพ์ตัวเลขหรือพหุนาม (เช่น x, 2x^2) ลงในช่องสีขาว ผลลัพธ์จะคำนวณและจัดกลุ่มให้อัตโนมัติ")

# ==========================================
# 3. กำหนดขนาดและเส้น (ใช้ Logic เส้นที่คุณต้องการ)
# ==========================================
size = int(grid_choice.split("x")[0])

# วาดเส้นโดยใช้ range(size + 1) เพื่อให้ปิดกรอบตารางได้ครบ
vlines = "".join([f'<div class="line vline" style="left: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])
hlines = "".join([f'<div class="line hline" style="top: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])

top_inputs = "".join([f'<div class="input-cell"><input id="top{i}" class="gamebox" placeholder="T{i+1}" autocomplete="off"></div>' for i in range(size)])

left_and_results = ""
for j in range(size - 1, -1, -1):
    left_and_results += f'<div class="input-cell"><input id="left{j}" class="gamebox" placeholder="L{j+1}" autocomplete="off"></div>'
    for i in range(size):
        left_and_results += f'<div class="result-cell" id="res_{j}_{i}"></div>'

# ==========================================
# 4. โค้ด HTML/JS
# ==========================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Sarabun', sans-serif; display: flex; flex-direction: column; align-items: center; padding-top: 30px; background: transparent; }}
        .app-container {{ background: #ffffff; padding: 50px; border-radius: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); position: relative; display: inline-block; }}
        .grid-wrapper {{ display: grid; grid-template-columns: 80px repeat({size}, 100px); grid-template-rows: 80px repeat({size}, 100px); position: relative; z-index: 2; }}
        .input-cell {{ display: flex; justify-content: center; align-items: center; }}
        input.gamebox {{ width: 55px; height: 38px; text-align: center; border: 2px solid #dee2e6; border-radius: 8px; font-weight: 600; outline: none; }}
        .result-cell {{ display: flex; justify-content: center; align-items: center; font-size: 20px; font-weight: 700; color: #dc3545; font-family: 'Roboto Mono', monospace; }}
        
        /* ระบบเส้นที่คุณเลือก */
        .lines-container {{ position: absolute; top: 50px; left: 50px; right: 50px; bottom: 50px; pointer-events: none; z-index: 1; }}
        .line {{ position: absolute; background-color: #000; }}
        .vline {{ width: 2px; top: 0; bottom: 0; }}
        .hline {{ height: 2px; left: 0; right: 0; }}
        
        #finalResultBox {{ margin-top: 80px; padding: 20px 50px; background: linear-gradient(135deg, #0d6efd, #0056b3); color: white; border-radius: 100px; font-size: 26px; font-weight: 600; display: none; text-align: center; }}
        sup {{ font-size: 0.65em; vertical-align: super; }}
    </style>
</head>
<body>
    <div class="app-container">
        <div class="lines-container">{vlines}{hlines}</div>
        <div class="grid-wrapper"><div></div>{top_inputs}{left_and_results}</div>
    </div>
    <div id="finalResultBox"></div>
<script>
    const size = {size};
    function parse(s) {{ s = s.toLowerCase().replace(/\\s/g, ''); if(!s) return {{c:0, p:0}}; if(!s.includes('x')) return {{c:parseFloat(s)||0, p:0}}; let parts = s.split('x'); let c = parts[0]==='' ? 1 : (parts[0]==='-' ? -1 : parseFloat(parts[0])); let p = 1; if(parts[1] && parts[1].startsWith('^')) p = parseInt(parts[1].slice(1)) || 0; return {{c, p}}; }}
    function fmt(c, p) {{ if(c===0) return ""; if(p===0) return c; let res = (c===1) ? "x" : (c===-1 ? "-x" : c+"x"); if(p!==1) res += "<sup>"+p+"</sup>"; return res; }}
    function update() {{
        let tops=[], lefts=[], allFilled=true;
        for(let i=0; i<size; i++) {{ let v = document.getElementById('top'+i).value; if(!v) allFilled=false; tops.push(parse(v)); }}
        for(let j=0; j<size; j++) {{ let v = document.getElementById('left'+j).value; if(!v) allFilled=false; lefts.push(parse(v)); }}
        if(!allFilled) {{ document.getElementById('finalResultBox').style.display='none'; return; }}
        let finalMap={{}};
        for(let j=0; j<size; j++) {{
            for(let i=0; i<size; i++) {{
                let c = tops[i].c * lefts[j].c; let p = tops[i].p + lefts[j].p;
                document.getElementById(`res_${{j}}_${{i}}`).innerHTML = fmt(c, p);
                finalMap[p] = (finalMap[p]||0) + c;
            }}
        }}
        let terms = Object.keys(finalMap).map(Number).sort((a,b)=>b-a).filter(p=>finalMap[p]!==0).map((p,i)=>{{ let c=finalMap[p], s=fmt(c, p); if(i>0 && c>0) return " + "+s; if(c<0) return " "+s; return s; }});
        const box = document.getElementById('finalResultBox');
        box.innerHTML = terms.join('') || "0"; box.style.display='block';
    }}
    document.querySelectorAll('input').forEach(el => el.addEventListener('input', update));
</script>
</body>
</html>
"""
components.html(html_code, height=900)

# แสดงเวลาปัจจุบันด้านล่าง
bangkok_now = datetime.datetime.now(ZoneInfo("Asia/Bangkok"))
time_str = bangkok_now.strftime('%d/%m/%Y %H:%M:%S')
st.markdown(f"<p style='text-align: center; color: gray; margin-top: 20px;'>เข้าใช้งานล่าสุดเมื่อ: {time_str}</p>", unsafe_allow_html=True)