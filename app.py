import streamlit as st
import sys
import contextlib
import time
from datetime import date, timedelta

from models import FlightSearchParams
from agents import flight_searcher, spot_analyzer, itinerary_optimizer
from tasks import create_search_task, create_analyze_task, create_optimize_task
from crewai import Crew, Process

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Agentic Flight & Layover Optimizer",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# PREMIUM AESTHETICS (CSS INJECTION)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;700&display=swap');

    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505;
        color: #E2E8F0;
    }
    
    /* Main container background with subtle animated gradient */
    .stApp {
        background: radial-gradient(circle at 15% 50%, rgba(20, 30, 48, 1) 0%, rgba(36, 59, 85, 0) 50%),
                    radial-gradient(circle at 85% 30%, rgba(15, 32, 39, 1) 0%, rgba(32, 58, 67, 0) 50%),
                    #050505;
        background-attachment: fixed;
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 25px;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 210, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .card-icon {
        font-size: 24px;
        margin-right: 10px;
        vertical-align: middle;
    }

    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #F8FAFC;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }

    .card-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    /* Custom Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: #FFFFFF;
        border: none;
        padding: 14px 32px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 50px;
        box-shadow: 0 8px 25px rgba(58, 123, 213, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        font-family: 'Outfit', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(0, 210, 255, 0.6);
        background: linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%);
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* Terminal Console Log Styling */
    .terminal-log {
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        background-color: #0b0f19;
        color: #39ff14;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        height: 400px;
        overflow-y: auto;
        font-size: 0.85rem;
        line-height: 1.6;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .terminal-log::-webkit-scrollbar {
        width: 8px;
    }
    .terminal-log::-webkit-scrollbar-thumb {
        background-color: #334155;
        border-radius: 4px;
    }

    /* Hide standard st.code background to use custom HTML */
    .stCodeBlock {
        display: none !important; 
    }
    
    /* Result Markdown Styling */
    .result-container {
        color: #F1F5F9;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .result-container h1, .result-container h2, .result-container h3 {
        color: #00d2ff;
        margin-top: 1.5rem;
    }
    .result-container ul {
        background: rgba(0, 0, 0, 0.2);
        padding: 20px 40px;
        border-radius: 12px;
        border-left: 4px solid #3a7bd5;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------
class StreamlitRedirect:
    """Redirects stdout to a Streamlit placeholder with custom terminal styling."""
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.output = ""
    def write(self, text):
        self.output += text
        # Use custom HTML for the terminal instead of st.code for better styling
        html_content = f"""
        <div class="terminal-log" id="terminal-log">
            {self.output.replace('\n', '<br>')}
        </div>
        <script>
            var objDiv = document.getElementById("terminal-log");
            objDiv.scrollTop = objDiv.scrollHeight;
        </script>
        """
        self.placeholder.markdown(html_content, unsafe_allow_html=True)
    def flush(self):
        pass

# ---------------------------------------------------------
# UI LAYOUT
# ---------------------------------------------------------

st.markdown("<h1>🌌 Agentic Flight & Layover Optimizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.1rem; color:#94A3B8; margin-bottom: 2rem;'>新潟大学の夏休み期間を利用したボランティア・トランジット観光向けマルチエージェント最適化システム</p>", unsafe_allow_html=True)

# --- SIDEBAR (INPUTS) ---
with st.sidebar:
    st.markdown("<h2 style='font-size:1.5rem; margin-bottom: 1rem;'>⚙️ 検索パラメータ</h2>", unsafe_allow_html=True)
    
    st.markdown("### 📍 空港設定")
    origin_choice = st.selectbox("出発地 (Origin)", ["KIJ", "HND", "NRT", "Custom"], index=0)
    origin = st.text_input("出発空港コード", value="KIJ").upper() if origin_choice == "Custom" else origin_choice

    dest_choice = st.selectbox("目的地 (Destination)", ["BER", "FRA", "MUC", "Custom"], index=0)
    destination = st.text_input("目的空港コード", value="BER").upper() if dest_choice == "Custom" else dest_choice

    st.markdown("### 📅 日程範囲")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        departure_date_start = st.date_input("開始日", value=date(2026, 8, 1))
    with col_d2:
        departure_date_end = st.date_input("終了日", value=date(2026, 8, 10))

    st.markdown("### 🕒 希望出発・到着時間帯")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        departure_time_start = st.time_input("出発 (以降)", value=None)
        arrival_time_start = st.time_input("到着 (以降)", value=None)
    with col_t2:
        departure_time_end = st.time_input("出発 (以前)", value=None)
        arrival_time_end = st.time_input("到着 (以前)", value=None)

    st.markdown("### ⏳ レイオーバー (乗り継ぎ)")
    st.info("💡 建築巡礼プランを作成するには、長時間のレイオーバー(例: 10〜24時間)を含めてください。")
    min_layover, max_layover = st.slider("時間範囲", 0, 48, (10, 24), 1)

    st.markdown("### ✈️ フライト制限")
    max_transfers = st.slider("最大乗り継ぎ回数", 0, 3, 2)
    max_flight_hours = st.number_input("最大総飛行時間 (時間)", min_value=1, value=35)

    st.markdown("### 💼 オプション")
    include_carry_on = st.toggle("機内持ち込み手荷物", value=True)
    include_checked_bag = st.toggle("受託手荷物", value=True)
    excluded_airlines_str = st.text_input("除外航空会社 (例: CA, MU)", value="")
    excluded_airlines = [x.strip().upper() for x in excluded_airlines_str.split(",") if x.strip()]

    st.markdown("### 🎯 旅行の目的・トランジットでやりたいこと")
    desired_activities = st.text_area("自由記述", value="ブルータリズム建築や旧ソ連時代の廃墟を巡りたい", height=100)

# --- MAIN DASHBOARD ---
col_left, col_right = st.columns([1, 1.4], gap="large")

with col_left:
    st.markdown("""
        <div class="glass-card">
            <div class="card-title"><span class="card-icon">🤖</span> AIエージェント管理</div>
            <div class="card-subtitle">
                設定されたパラメータに基づき、<b>Flight Searcher</b>、<b>Spot Analyzer</b>、<b>Itinerary Optimizer</b>の3つのエージェントが協調して最適なルートを探索します。
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    run_button = st.button("🚀 最適な旅程を生成する")
    
    st.markdown("""
        <div class="glass-card" style="margin-top: 25px;">
            <div class="card-title"><span class="card-icon">📡</span> リアルタイム思考ログ</div>
            <div class="card-subtitle">エージェントの推論とAPIコールの状況を監視します。</div>
    """, unsafe_allow_html=True)
    
    log_placeholder = st.empty()
    log_placeholder.markdown("""
        <div class="terminal-log">
            > Waiting for execution...<br>
            > Ready to launch autonomous agents.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class="glass-card" style="min-height: 800px;">
            <div class="card-title"><span class="card-icon">✨</span> 提案された旅程</div>
            <div class="card-subtitle">エージェントによって統合・最適化された3つのプランがここに表示されます。</div>
    """, unsafe_allow_html=True)
    
    results_placeholder = st.empty()
    results_placeholder.markdown("""
        <div style="text-align:center; padding: 100px 0; color: #475569;">
            <div style="font-size: 60px; margin-bottom: 20px;">🗺️</div>
            <p>左側の「最適な旅程を生成する」ボタンを押して開始してください。</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# EXECUTION LOGIC
# ---------------------------------------------------------
if run_button:
    search_params = FlightSearchParams(
        origin=origin,
        destination=destination,
        departure_date_start=departure_date_start.strftime("%Y-%m-%d"),
        departure_date_end=departure_date_end.strftime("%Y-%m-%d"),
        max_transfers=max_transfers,
        max_flight_hours=max_flight_hours if max_flight_hours > 0 else None,
        departure_time_start=departure_time_start.strftime("%H:%M") if departure_time_start else None,
        departure_time_end=departure_time_end.strftime("%H:%M") if departure_time_end else None,
        arrival_time_start=arrival_time_start.strftime("%H:%M") if arrival_time_start else None,
        arrival_time_end=arrival_time_end.strftime("%H:%M") if arrival_time_end else None,
        min_layover_hours=min_layover,
        max_layover_hours=max_layover,
        include_carry_on=include_carry_on,
        include_checked_bag=include_checked_bag,
        excluded_airlines=excluded_airlines,
        desired_activities=desired_activities
    )
    
    params_json = search_params.model_dump_json(indent=2)
    
    search_task = create_search_task(params_json)
    analyze_task = create_analyze_task(params_json)
    optimize_task = create_optimize_task(params_json)

    flight_crew = Crew(
        agents=[flight_searcher, spot_analyzer, itinerary_optimizer],
        tasks=[search_task, analyze_task, optimize_task],
        process=Process.sequential,
        verbose=True
    )
    
    with st.spinner("エージェントが協調して最適なルートを構築中... (LM Studioで処理中)"):
        log_redirect = StreamlitRedirect(log_placeholder)
        
        # Clear previous result
        results_placeholder.empty()
        
        with contextlib.redirect_stdout(log_redirect):
            try:
                final_output = flight_crew.kickoff()
                
                # Render results beautifully
                results_html = f"""
                <div class="result-container">
                    {final_output}
                </div>
                """
                # Note: CrewAI outputs markdown. st.markdown handles it natively.
                # We wrap it in a div for targeted CSS styling.
                results_placeholder.markdown(f'<div class="result-container">{final_output}</div>', unsafe_allow_html=True)
                
                st.balloons()
            except Exception as e:
                error_msg = f"""
                <div style="color: #ef4444; background: rgba(239,68,68,0.1); padding: 15px; border-radius: 8px; border: 1px solid #ef4444;">
                    <strong>エラーが発生しました:</strong> {e}<br><br>
                    ※ LM Studio (localhost:1234) が起動しており、モデルがロードされているか確認してください。
                </div>
                """
                results_placeholder.markdown(error_msg, unsafe_allow_html=True)
