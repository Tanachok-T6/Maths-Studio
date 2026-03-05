import streamlit as st
import streamlit.components.v1 as components
import datetime
from zoneinfo import ZoneInfo
import threading
import pandas as pd  # เพิ่ม Pandas
import requests      # เพิ่ม Requests
import plotly.graph_objects as go # เพิ่ม Plotly
import firebase_admin # เพิ่ม Firebase
from firebase_admin import credentials, firestore

# ==========================================
# 1. การตั้งค่าหน้าจอ
# ==========================================
st.set_page_config(page_title="Maths Studio Pro", page_icon="🔢", layout="wide")

# ==========================================
# 2. ระบบ Firebase Setup (Safe Mode)
# ==========================================
def init_firebase():
    try:
        if not firebase_admin._apps:
            # ในการใช้งานจริงต้องมีไฟล์ .json จาก Firebase และใส่ใน Streamlit Secrets
            # cred = credentials.Certificate(st.secrets["firebase_key"])
            # firebase_admin.initialize_app(cred)
            pass
    except Exception as e:
        st.sidebar.warning("Firebase ยังไม่ได้เชื่อมต่อ (ต้องตั้งค่า Key ก่อน)")

init_firebase()

# ==========================================
# 3. ตกแต่ง UI (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .school-title { 
        position: fixed; top: 14px; left: 50%; transform: translateX(-50%); 
        z-index: 9999; font-size: 26px; font-weight: 800; color: #0d6efd;
    }
</style>
<div class="school-title">CRMS6 MATHS STUDIO</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. ระบบ Log และ Tracking (Requests & Pandas)
# ==========================================
@st.cache_data
def get_user_ip():
    try:
        # ใช้ requests ดึง IP ของผู้ใช้งานเบื้องต้น
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return "Unknown"

user_ip = get_image_base64 = get_user_ip()

# สร้าง Dataจำลองสำหรับการวิเคราะห์ (Pandas)
usage_data = pd.DataFrame({
    "Grid Size": ["2x2", "3x3", "4x4", "5x5"],
    "Difficulty": ["Basic", "Standard", "Advanced", "Expert"],
    "Estimated Terms": [4, 9, 16, 25]
})

# ==========================================
# 5. แถบเครื่องมือด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    # แสดงโลโก้
    try:
        st.image("IMAGE/logo_CRMS6.png", width=150)
    except:
        st.write("📌 [Logo CRMS6]")

    st.header("🔢 Control Panel")
    grid_choice = st.radio(
        "เลือกขนาดตาราง:",["2x2 (Basic)", "3x3 (Standard)", "4x4 (Advanced)", "5x5 (Expert)"], 
        index=0
    )
    
    st.markdown("---")
    st.write(f"🌐 Your IP: `{user_ip}`") # แสดง IP ที่ดึงมาด้วย requests
    
    # แสดงกราฟวิเคราะห์ขนาด (Plotly)
    fig = go.Figure(data=[go.Bar(x=usage_data['Grid Size'], y=usage_data['Estimated Terms'], marker_color='#0d6efd')])
    fig.update_layout(title="Complexity Chart", height=200, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

# กำหนดขนาด size
size = int(grid_choice.split("x")[0])

# ==========================================
# 6. ส่วนประกอบตาราง (HTML Logic)
# ==========================================
# (คงเดิมจากโค้ดที่คุณมี เพื่อให้ระบบคำนวณยังทำงานได้แม่นยำ)
vlines = "".join([f'<div class="line vline" style="left: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])
hlines = "".join([f'<div class="line hline" style="top: {80 + (i * 100)}px;"></div>' for i in range(size + 1)])
top_inputs = "".join([f'<div class="input-cell"><input id="top{i}" class="gamebox" placeholder="T{i+1}" autocomplete="off"></div>' for i in range(size)])
left_and_results = ""
for j in range(size):
    left_and_results += f'<div class="input-cell"><input id="left{j}" class="gamebox" placeholder="L{j+1}" autocomplete="off"></div>'
    for i in range(size):
        left_and_results += f'<div class="result-cell" id="res_{j}_{i}"></div>'

# ==========================================
# 7. HTML/JS Interface
# ==========================================
# (ใช้การวาดเส้นที่แม่นยำและระบบแสดงผล Sup/X ที่คุณต้องการ)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Sarabun', sans-serif; display: flex; flex-direction: column; align-items: center; background: transparent; }}
        .app-container {{ background: white; padding: 40px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); position: relative; }}
        .grid-wrapper {{ display: grid; grid-template-columns: 80px repeat({size}, 100px); grid-template-rows: 80px repeat({size}, 100px); position: relative; z-index: 2; }}
        .lines-container {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 1; pointer-events: none; }}
        .line {{ position: absolute; background: #000; }}
        .vline {{ width: 2px; top: 0; bottom: 0; }}
        .hline {{ height: 2px; left: 0; right: 0; }}
        input.gamebox {{ width: 60px; height: 38px; text-align: center; border: 1px solid #ddd; border-radius: 8px; font-weight: 600; }}
        .result-cell {{ display: flex; justify-content: center; align-items: center; font-size: 18px; font-weight: 700; color: #dc3545; }}
        #finalResultBox {{ margin-top: 30px; padding: 15px 40px; background: #0d6efd; color: white; border-radius: 50px; display: none; text-align: center; font-size: 22px; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="app-container">
        <div class="grid-wrapper">
            <div class="lines-container">{vlines}{hlines}</div>
            <div style="display:flex; justify-content:center; align-items:center;">🔢</div>
            {top_inputs}
            {left_and_results}
        </div>
        <div id="finalResultBox"></div>
    </div>
    <script>
        const size = {size};
        function parse(s) {{ 
            s = s.toLowerCase().replace(/\\s/g, ''); 
            if(!s) return {{c:0, p:0}}; 
            if(!s.includes('x')) {{
                if(s.includes('^')) {{
                    let p=s.split('^'); return {{c:Math.pow(parseFloat(p[0]),parseFloat(p[1])), p:0}};
                }}
                return {{c:parseFloat(s)||0, p:0}};
            }}
            let parts = s.split('x'); 
            let c = parts[0]==='' ? 1 : (parts[0]==='-' ? -1 : parseFloat(parts[0])); 
            let p = parts[1] ? (parseInt(parts[1].replace('^',''))||1) : 1;
            return {{c, p}};
        }}
        function fmt(c, p) {{
            if(c===0) return ""; if(p===0) return c;
            let x = p===1 ? "x" : "x^"+p;
            return c===1 ? x : (c===-1 ? "-"+x : c+x);
        }}
        function update() {{
            let tops=[], lefts=[], allFilled=true;
            for(let i=0; i<size; i++) {{ let v=document.getElementById('top'+i).value; if(!v)allFilled=false; tops.push(parse(v)); }}
            for(let j=0; j<size; j++) {{ let v=document.getElementById('left'+j).value; if(!v)allFilled=false; lefts.push(parse(v)); }}
            if(!allFilled) return;
            let finalMap={{}};
            for(let j=0; j<size; j++) {{
                for(let i=0; i<size; i++) {{
                    let c=tops[i].c*lefts[j].c, p=tops[i].p+lefts[j].p;
                    document.getElementById(`res_${{j}}_${{i}}`).innerText = fmt(c, p);
                    finalMap[p]=(finalMap[p]||0)+c;
                }}
            }}
            let res = Object.keys(finalMap).sort((a,b)=>b-a).filter(p=>finalMap[p]!==0).map((p,i)=>{{
                let c=finalMap[p], s=fmt(c,p); return (i>0&&c>0?" + ":" ")+s;
            }}).join("");
            const box = document.getElementById('finalResultBox');
            box.innerText = res || "0"; box.style.display='block';
        }}
        document.querySelectorAll('input').forEach(i => i.addEventListener('input', update));
    </script>
</body>
</html>
"""

# แสดงผล Component
components.html(html_code, height=(200 + size*100))

# ==========================================
# 8. Footer (Pandas Data Table)
# ==========================================
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📊 ข้อมูลทางสถิติตาราง")
    st.dataframe(usage_data, use_container_width=True) # แสดงผลตารางด้วย Pandas
with col_b:
    st.subheader("🕒 System Info")
    bangkok_now = datetime.datetime.now(ZoneInfo("Asia/Bangkok"))
    st.info(f"เวลาปัจจุบัน: {bangkok_now.strftime('%H:%M:%S')}")
    st.write("สถานะระบบ: 🟢 ออนไลน์")