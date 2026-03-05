import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. การตั้งค่าหน้าจอ
# ==========================================
st.set_page_config(page_title="Maths Studio Pro", page_icon="🔢", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    .school-title { position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 999999; font-size: 26px; font-weight: 800; pointer-events: none; }
</style>
<div class="school-title">🏫 โรงเรียนเทศบาล 6 นครเชียงราย</div>
""", unsafe_allow_html=True)

with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: st.image("IMAGE/logo_CRMS6.png", use_container_width=True)
    st.header("🔢 Maths Studio")
    grid_choice = st.radio("เลือกขนาดตาราง:",["2x2 (Basic)", "3x3 (Standard)", "4x4 (Advanced)", "5x5 (Expert)"], index=0)
    st.markdown("---")
    st.info("💡 วิธีใช้: พิมพ์ตัวเลขหรือพหุนาม (เช่น x, 2x^2) ลงในช่องสีขาวตามตัวเลขที่กำหนด ผลลัพธ์จะคำนวณและจัดกลุ่มให้อัตโนมัติ ")

size = 2
if "3x3" in grid_choice: size = 3
if "4x4" in grid_choice: size = 4
if "5x5" in grid_choice: size = 5

# สร้าง HTML ส่วนประกอบ
vlines = "".join([f'<div class="line vline" style="left: {80 + (i * 100)}px;"></div>' for i in range(size)])
hlines = "".join([f'<div class="line hline" style="top: {80 + (i * 100)}px;"></div>' for i in range(size)])
top_inputs = "".join([f'<div class="input-cell"><input id="top{i}" class="gamebox" placeholder="T{i+1}" autocomplete="off"></div>' for i in range(size)])

# ตรงนี้คือจุดที่ปรับ: ให้ L เรียงจาก size ลงไปหา 1 (ให้ L1 อยู่ล่างสุด)
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
        body {{ font-family: 'Sarabun', sans-serif; display: flex; flex-direction: column; align-items: center; padding-top: 30px; }}
        .app-container {{ background: #ffffff; padding: 50px; border-radius: 24px; box-shadow: 0 15px 35px rgba(0,0,0,0.08); position: relative; }}
        .grid-wrapper {{ display: grid; grid-template-columns: 80px repeat({size}, 100px); grid-template-rows: 80px repeat({size}, 100px); position: relative; z-index: 2; }}
        .input-cell {{ display: flex; justify-content: center; align-items: center; }}
        input.gamebox {{ width: 55px; height: 38px; text-align: center; border: 2px solid #dee2e6; border-radius: 8px; font-weight: 600; }}
        .result-cell {{ display: flex; justify-content: center; align-items: center; font-size: 20px; font-weight: 700; color: #dc3545; font-family: 'Roboto Mono', monospace; }}
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
components.html(html_code, height=950)