import streamlit as st
import streamlit.components.v1 as components
import datetime
from zoneinfo import ZoneInfo
import threading
import requests

# ==========================================
# 1. การตั้งค่าหน้าจอ (ต้องอยู่บรรทัดแรกเสมอ)
# ==========================================
st.set_page_config(page_title="Maths Studio", page_icon="🔢", layout="wide")

# ฟังก์ชันดึง IP Address
def get_user_ip():
    try:
        # พยายามดึงจาก Header ของ Streamlit (สำหรับตอนขึ้น Cloud)
        headers = st.context.headers
        if "X-Forwarded-For" in headers:
            return headers["X-Forwarded-For"].split(",")[0]
        # กรณีรันเครื่องตัวเอง หรือ Header โดนบล็อก
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown IP"

# ==========================================
# 2. ระบบจำค่า IP และเวลาเข้าใช้งาน (ครั้งแรกครั้งเดียว)
# ==========================================
if 'entry_info' not in st.session_state:
    now = datetime.datetime.now(ZoneInfo("Asia/Bangkok"))
    st.session_state.entry_info = {
        "ip": get_user_ip(),
        "time": now.strftime('%d/%m/%Y %H:%M:%S')
    }
    # พิมพ์ลง Log ฝั่ง Server
    print(f"📌 [LOG] New Access | IP: {st.session_state.entry_info['ip']} | Time: {st.session_state.entry_info['time']}")

# ==========================================
# 3. แถบเครื่องมือด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    # แสดงโลโก้
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("IMAGE/logo_CRMS6.png", use_container_width=True)
        except: pass

    st.header("🔢 Maths Studio")
    
    # --- ส่วนแสดงข้อมูลผู้ใช้งาน ---
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="margin: 0; font-size: 0.8rem; color: #666;">🌐 IP Address:</p>
        <p style="margin: 0; font-weight: bold; color: #0d6efd; font-size: 1rem;">{st.session_state.entry_info['ip']}</p>
        <hr style="margin: 10px 0;">
        <p style="margin: 0; font-size: 0.8rem; color: #666;">🕒 เวลาที่เข้าสู่ระบบ:</p>
        <p style="margin: 0; font-weight: bold; color: #333; font-size: 0.9rem;">{st.session_state.entry_info['time']}</p>
    </div>
    """, unsafe_allow_html=True)

    grid_choice = st.radio(
        "เลือกขนาดตาราง:",["2x2 (Basic)", "3x3 (Standard)", "4x4 (Advanced)", "5x5 (Expert)"], 
        index=0
    )
    st.markdown("---")
    st.info("💡 วิธีใช้: พิมพ์ตัวเลขหรือพหุนามลงในช่องสีขาว ผลลัพธ์จะคำนวณอัตโนมัติ")

# ==========================================
# 4. ปรับแต่งหน้าเว็บ (CSS)
# ==========================================
st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .stApp { background-color: #f8f9fa !important; }

    /* --- ส่วนด้านบน (Header) --- */
    .school-title { 
        position: fixed; 
        top: 14px; 
        left: 50%; 
        transform: translateX(-50%); 
        z-index: 999999; 
        font-size: 26px; 
        font-weight: 800; 
        color: #FFFFFF !important; /* เปลี่ยนเป็นสีขาว */
        pointer-events: none; 
    }

    /* --- ส่วนแถบด้านข้าง (Sidebar) --- */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }

    /* บังคับตัวหนังสือทุกอย่างใน Sidebar ให้เป็นสีดำ */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p {
        color: #000000 !important;
    }

    /* บังคับสีปุ่ม Radio ให้เป็นสีดำ */
    div[data-testid="stRadio"] label p {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* ปรับแต่งความชัดเจนของ Logo และ Icon ใน Sidebar */
    [data-testid="stSidebar"] img {
        filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));
    }
</style>
<div class="school-title">CRMS6</div>
""", unsafe_allow_html=True)
# ==========================================
# 5. โครงสร้างตารางคำนวณ (เหมือนเดิมเพื่อให้ระบบทำงานแม่นยำ)
# ==========================================
size = int(grid_choice.split("x")[0])
vlines = "".join([f'<div class="line vline" style="left: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])
hlines = "".join([f'<div class="line hline" style="top: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])
top_inputs = "".join([f'<div class="input-cell"><input id="top{i}" class="gamebox" placeholder="T{i+1}" autocomplete="off"></div>' for i in range(size)])
left_and_results = ""
for j in range(size - 1, -1, -1):
    left_and_results += f'<div class="input-cell"><input id="left{j}" class="gamebox" placeholder="L{j+1}" autocomplete="off"></div>'
    for i in range(size):
        left_and_results += f'<div class="result-cell" id="res_{j}_{i}"></div>'

# ==========================================
# 6. HTML/JS
# ==========================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500;700&family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Sarabun', sans-serif; display: flex; flex-direction: column; align-items: center; background: transparent; padding: 20px; }}
        .app-container {{ background: white; padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); position: relative; display: inline-block; }}
        .grid-wrapper {{ display: grid; grid-template-columns: 80px repeat({size}, 100px); grid-template-rows: 80px repeat({size}, 100px); position: relative; z-index: 2; }}
        .lines-container {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; z-index: 1; }}
        .line {{ position: absolute; background-color: #000; }}
        .vline {{ width: 2px; top: 0; bottom: 0; }}
        .hline {{ height: 2px; left: 0; right: 0; }}
        .input-cell, .result-cell {{ display: flex; justify-content: center; align-items: center; }}
        input.gamebox {{ width: 60px; height: 38px; text-align: center; border: 1px solid #ced4da; border-radius: 8px; font-weight: 600; outline: none; }}
        .result-cell {{ font-size: 20px; font-weight: 700; color: #dc3545; font-family: 'Roboto Mono', monospace; }}
        #finalResultBox {{ margin-top: 30px; padding: 15px 40px; background: linear-gradient(135deg, #0d6efd, #0056b3); color: white; border-radius: 100px; font-size: 24px; font-weight: 600; display: none; text-align: center; }}
        sup {{ font-size: 0.6em; vertical-align: super; }}
    </style>
</head>
<body>
    <div class="app-container">
        <div class="grid-wrapper">
            <div class="lines-container">{vlines}{hlines}</div>
            <div></div>{top_inputs}{left_and_results}
        </div>
        <div id="finalResultBox"></div>
    </div>
    <script>
        const size = {size};
        function parse(s) {{ 
            s = s.toLowerCase().replace(/\\s/g, ''); 
            if(!s) return {{c:0, p:0}}; 
            if(!s.includes('x')) return {{c:parseFloat(s)||0, p:0}}; 
            let parts = s.split('x'); 
            let c = parts[0]==='' ? 1 : (parts[0]==='-' ? -1 : parseFloat(parts[0])); 
            let p = 1; if(parts[1] && parts[1].startsWith('^')) p = parseInt(parts[1].slice(1)) || 0; 
            return {{c, p}}; 
        }}
        function fmt(c, p) {{ 
            if(c===0) return ""; if(p===0) return c; 
            let res = (c===1) ? "x" : (c===-1 ? "-x" : c+"x"); 
            if(p!==1) res += "<sup>"+p+"</sup>"; 
            return res; 
        }}
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
            let terms = Object.keys(finalMap).map(Number).sort((a,b)=>b-a).filter(p=>finalMap[p]!==0).map((p,i)=>{{ 
                let c=finalMap[p], s=fmt(c, p); 
                return (i>0 && c>0) ? " + "+s : (c<0 ? " "+s : s); 
            }});
            const box = document.getElementById('finalResultBox');
            box.innerHTML = terms.join('') || "0"; box.style.display='block';
        }}
        document.querySelectorAll('input').forEach(el => el.addEventListener('input', update));
    </script>
</body>
</html>
"""

components.html(html_code, height=400 + (size * 100))