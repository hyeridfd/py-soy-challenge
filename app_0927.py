import streamlit as st


# ===================== 페이지 설정 =====================
st.set_page_config(
    page_title="두믈리에 챌린지",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timezone
import pytz
import os
import textwrap
import streamlit.components.v1 as components
from supabase import create_client, Client


# ===================== Supabase =====================
# pip install supabase openpyxl

@st.cache_resource
def supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

def insert_response_row(row: dict) -> bool:
    """17개 컬럼을 tasting_responses에 1행 insert"""
    try:
        supabase.table("tasting_responses").insert(row).execute()
        return True
    except Exception as e:
        st.error(f"❌ 데이터 저장 오류: {e}")
        return False

def fetch_all_responses_df() -> pd.DataFrame:
    """전체 응답 로드 (DataFrame)"""
    try:
        res = supabase.table("tasting_responses").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(res.data or [])
        if not df.empty and "제출시간" in df.columns:
            df["제출시간(KST)"] = pd.to_datetime(df["제출시간"], utc=True)\
                                     .dt.tz_convert("Asia/Seoul")\
                                     .dt.strftime("%Y-%m-%d %H:%M:%S")
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

def fetch_org_responses_df(org: str) -> pd.DataFrame:
    """소속 정확 일치로 필터"""
    try:
        res = supabase.table("tasting_responses").select("*").eq("소속", org).execute()
        df = pd.DataFrame(res.data or [])
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

# ===================== Plotly =====================
PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}


# ===================== CSS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    .stApp { background: #ffffff; font-family: 'Noto Sans KR', sans-serif; }
    .main-header { text-align: center; padding: 40px 0; background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.05)); border-radius: 25px; margin-bottom: 30px; border: 2px solid rgba(52, 152, 219, 0.2); position: relative; overflow: hidden; }
    .main-header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #3498db, #2980b9, #1e88e5); }
    .main-title { font-size: 3.5rem; font-weight: 700; background: linear-gradient(45deg, #3498db, #2980b9, #1e88e5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .subtitle { font-size: 1.3rem; color: #7f8c8d; font-weight: 300; margin-top: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border-radius: 20px; padding: 10px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.1); justify-content: center !important; display: flex !important; width: 100%; }
    .stTabs [data-baseweb="tab"] { height: 60px; padding: 0 35px; background: transparent; border-radius: 15px; color: #34495e; font-weight: 500; font-size: 1.1rem; border: none; transition: all 0.3s ease; min-width: 250px; }
    .stTabs [data-baseweb="tab"]:hover { background: rgba(52, 152, 219, 0.1); transform: translateY(-2px); }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #3498db, #2980b9) !important; color: white !important; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }
    .section-header { color: #2980b9; font-size: 2rem; font-weight: 600; text-align: center; margin: 30px 0; padding: 20px; background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.05)); border-radius: 15px; border: 2px solid rgba(52, 152, 219, 0.2); }
    .brand-card { background: rgba(255, 255, 255, 0.9); border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 2px solid rgba(52, 152, 219, 0.1); transition: all 0.3s ease; position: relative; overflow: hidden; }
    .brand-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #3498db, #2980b9); }
    .brand-name { font-size: 1.4rem; font-weight: 600; color: #2980b9; margin-bottom: 10px; }
    .brand-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.15); border-color: rgba(52, 152, 219, 0.3); }
    .sample-card { background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 25px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 2px solid rgba(52, 152, 219, 0.1); transition: all 0.3s ease; }
    .sample-title { font-size: 1.6rem; font-weight: 600; color: #2980b9; text-align: center; margin-bottom: 20px; padding: 15px; background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.05)); border-radius: 10px; }
    .results-summary { background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.1)); border-radius: 20px; padding: 30px; margin: 25px 0; border: 2px solid rgba(52, 152, 219, 0.2); position: relative; }
    .results-summary::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #3498db, #2980b9, #1e88e5); border-radius: 20px 20px 0 0; }
    /* Mobile tweaks */
    @media (max-width: 768px) {
      :root { --pad-x: 12px; }
      section[data-testid="stMain"] .block-container{ padding-left: var(--pad-x) !important; padding-right: var(--pad-x) !important; }
      .main-header { padding: 24px 0; }
      .main-title{ font-size: 2rem; }
      .subtitle{ font-size: 1rem; }
      .section-header{ font-size: 1.3rem; padding: 14px; margin: 18px 0; }
      .sample-card{ padding: 18px; }
      .sample-title{ font-size: 1.2rem; }
      div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
      div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
      .js-plotly-plot, .plot-container { height: auto !important; }
      .stTabs [data-baseweb="tab"]{ min-width: auto; padding: 0 16px; height: 48px; font-size: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ===================== 도메인 데이터 =====================
BRANDS = {
    "A": {"taste_profile": {"진함": 4, "단맛": 1}},
    "B": {"taste_profile": {"진함": 3, "단맛": 4}},
    "C": {"taste_profile": {"진함": 1, "단맛": 2}},
    "D": {"taste_profile": {"진함": 2, "단맛": 3}},
}
SAMPLES = ['1', '2', '3', '4']

# ===================== 유틸 =====================
def create_modern_taste_profile(taste_data, title):
    fig = go.Figure()
    categories = ['☕ 진함', '🧊 단맛']
    values = [taste_data.get('진함', 0), taste_data.get('단맛', 0)]
    colors = ['#2980b9', '#3498db']
    fig.add_trace(go.Bar(
        y=categories, x=values, orientation='h', marker_color=colors,
        text=[f"{val}/4" for val in values], textposition='inside',
        textfont=dict(color='white', size=14, family='Noto Sans KR')
    ))
    fig.update_layout(
        title={'text': title, 'x': 0.5, 'xanchor': 'center'},
        xaxis=dict(range=[0, 4], showgrid=True, gridcolor='rgba(52, 152, 219, 0.2)'),
        height=200, showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.8)', margin=dict(l=80, r=50, t=60, b=50),
        font=dict(family='Noto Sans KR', color='#2c3e50')
    )
    return fig

def display_brand_rankings():
    st.markdown('<div class="section-header">📊 브랜드 맛 특성 순위</div>', unsafe_allow_html=True)
    brands_by_intensity = sorted(BRANDS.items(), key=lambda x: x[1]["taste_profile"]["진함"], reverse=True)
    brands_by_sweetness = sorted(BRANDS.items(), key=lambda x: x[1]["taste_profile"]["단맛"], reverse=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div style="background: rgba(52, 152, 219, 0.1); padding: 20px; border-radius: 15px; border: 2px solid rgba(52, 152, 219, 0.2);"><h4 style="color: #2980b9; text-align: center; margin-bottom: 15px;">진함 순위</h4>""", unsafe_allow_html=True)
        for i, (brand, info) in enumerate(brands_by_intensity, 1):
            intensity = info["taste_profile"]["진함"]
            emoji_bar = "🔵" * intensity + "⚪" * (4 - intensity)
            medal = ["🥇", "🥈", "🥉", "🏅"][i-1]
            st.markdown(f"""<div style="margin: 10px 0; padding: 10px; background: white; border-radius: 10px;"><strong>{medal} {i}위: {brand}</strong><br>{emoji_bar} ({intensity}/4)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style="background: rgba(52, 152, 219, 0.1); padding: 20px; border-radius: 15px; border: 2px solid rgba(52, 152, 219, 0.2);"><h4 style="color: #2980b9; text-align: center; margin-bottom: 15px;">단맛 순위</h4>""", unsafe_allow_html=True)
        for i, (brand, info) in enumerate(brands_by_sweetness, 1):
            sweetness = info["taste_profile"]["단맛"]
            emoji_bar = "🔵" * sweetness + "⚪" * (4 - sweetness)
            medal = ["🥇", "🥈", "🥉", "🏅"][i-1]
            st.markdown(f"""<div style="margin: 10px 0; padding: 10px; background: white; border-radius: 10px;"><strong>{medal} {i}위: {brand}</strong><br>{emoji_bar} ({sweetness}/4)</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===================== 앱 =====================
def main():
    sb = supabase_client()
    st.markdown("<style>/* CSS */</style>", unsafe_allow_html=True)
    # st.markdown("""
    # <div class="main-header">
    #     <h1 class="main-title">두믈리에 챌린지</h1>
    #     <p class="subtitle">자연의 맛을 찾아가는 특별한 여행</p>
    # </div>
    # """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 홈", "🚀 챌린지", "🔧 관리자"])
    with tab1: home_page()
    with tab2: challenge_page()
    with tab3: admin_dashboard()

    if st.session_state.get("jump_to_challenge"):
        components.html("""
            <script>
            const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
            let target = -1;
            tabs.forEach((el, i) => { if (el.innerText.includes('🚀 챌린지')) target = i; });
            if (target >= 0) tabs[target].click();
            </script>
        """, height=0, width=0)
        st.session_state["jump_to_challenge"] = False

    # 하단 배너
    st.markdown("""
    <div class="bottom-banner-wrap">
      <div class="bottom-banner">
          <div style="font-weight: 600; margin-bottom: 5px;">서울대학교 정밀푸드솔루션 연구실</div>
          <div style="opacity: 0.9;">SNU Precision Food Solution Laboratory</div>
          <div style="margin-top: 8px; font-size: 0.8rem; opacity: 0.8;">© 2025 Seoul National University.</div>
          <div style="margin-top: 8px; font-size: 0.8rem; opacity: 0.8;">본 프로그램은 연구 목적으로 개발되었습니다.</div>
      </div>
    </div>
    <style>
    .bottom-banner-wrap{ position: sticky; bottom: 0; z-index: 1000; margin: 0 !important; --banner-gap: 100px; }
    .bottom-banner-wrap::before{ content: ''; display: block; height: var(--banner-gap); }
    .bottom-banner{ background: linear-gradient(135deg, #3498db, #2980b9); padding: 16px 0; text-align: center; color: #fff; font-size: 0.9rem; font-weight: 500; border-top: 1px solid rgba(255,255,255,0.2); width: 100vw; margin-left: calc(50% - 50vw); }
    </style>
    """, unsafe_allow_html=True)

def home_page():
    st.markdown("""
        <div style="background: rgba(52, 152, 219, 0.05); padding: 30px; border-radius: 20px; border: 2px solid rgba(52, 152, 219, 0.1); margin: 20px 0;">
            <h3 style="color: #2980b9; margin-bottom: 20px;">🥛 두믈리에 챌린지란?</h3>
            <p style="font-size: 18px; line-height: 1.8; color: #2c3e50;">
                <strong>두믈리에 챌린지</strong>는 <strong>네 가지 다른 브랜드의 두유</strong>를 시음하고 
                각각의 맛 특성을 평가한 후, 어떤 브랜드인지 맞춰보는 
                <strong>블라인드 테스트</strong>입니다.
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #34495e; margin-top: 20px;">
                당신의 미각은 얼마나 정확할까요? 진정한 <strong style="color: #2980b9;">두믈리에(두유 소믈리에)</strong>가 되어보세요!
            </p>
        </div>
    """, unsafe_allow_html=True)

    steps = [
        {"icon": "📝", "title": "참여자 정보 입력", "desc": "이름, 성별, 연령, 소속을 입력합니다"},
        {"icon": "👀", "title": "브랜드 소개",     "desc": "네 가지 브랜드의 맛 프로필을 확인합니다"},
        {"icon": "👅", "title": "시음 평가",       "desc": "각 두유의 맛을 평가하고 브랜드를 선택합니다"},
        {"icon": "🎉", "title": "결과 확인",       "desc": "평가 결과를 확인하고 제출합니다"}
    ]

    st.markdown("""
    <style>
      .home-steps{ display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:16px; margin-top:10px; }
      .home-step-card{ background:#fff; border-radius:18px; border:2px solid rgba(52,152,219,.12); box-shadow:0 8px 24px rgba(0,0,0,.08); padding:36px 20px; min-height:240px; display:flex; flex-direction:column; justify-content:space-between; align-items:center; }
      @media (max-width:768px){ .home-steps{ grid-template-columns:1fr; gap:18px; } .home-step-card{ min-height:220px; } .home-steps{ padding-bottom:calc(env(safe-area-inset-bottom) + 90px); } }
    </style>
    """, unsafe_allow_html=True)

    cards = ['<div class="home-steps">']
    for i, step in enumerate(steps, start=1):
        cards.append(
            textwrap.dedent(f"""
            <div class="home-step-card">
              <div style="font-size:48px;line-height:1">{step['icon']}</div>
              <div style="color:#2980b9;font-weight:700;font-size:18px;text-align:center;margin:8px 0">
                Step {i}<br>{step['title']}
              </div>
              <div style="color:#7f8c8d;font-size:14px;line-height:1.5;text-align:center">
                {step['desc']}
              </div>
            </div>
            """).strip()
        )
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 챌린지 시작하기", key="home_start_challenge", use_container_width=True):
            st.session_state["jump_to_challenge"] = True
            st.session_state.step = 1
            st.rerun()

def challenge_page():
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'participant_info' not in st.session_state: st.session_state.participant_info = {}
    if 'taste_evaluations' not in st.session_state: st.session_state.taste_evaluations = {}

    with st.container():
        # 1단계: 참여자 정보
        if st.session_state.step == 1:
            st.markdown('<div class="section-header">참여자 정보 입력</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("이름", key="name", placeholder="이름을 입력하세요(ex. 김스누)")
                gender = st.text_input("성별", key='gender', placeholder="성별을 입력하세요(ex. 남/여)")
            with col2:
                age = st.text_input("연령", key='age', placeholder="연령을 입력하세요(ex. 35)")
                organization = st.text_input("소속", key="organization", placeholder="소속을 입력하세요(ex. 푸드테크 최고책임자)")
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("다음 단계로", key="step1_next", use_container_width=True):
                    if name and gender and age and organization:
                        st.session_state.participant_info = {
                            "name": name, "gender": gender, "age": age, "organization": organization
                        }
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("모든 정보를 입력해주세요.")

        # 2단계: 브랜드 소개
        elif st.session_state.step == 2:
            st.markdown('<div class="section-header">🥛 네 가지 두유 브랜드 소개</div>', unsafe_allow_html=True)
            brand_list = sorted(BRANDS.keys())
            for i in range(0, len(brand_list), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(brand_list):
                        brand = brand_list[i + j]
                        with cols[j]:
                            st.markdown(f"""<div class="brand-card"><h3 class="brand-name">{brand}</h3></div>""", unsafe_allow_html=True)
                            fig = create_modern_taste_profile(BRANDS[brand]["taste_profile"], f"{brand} 맛 프로필")
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                            cleanness = BRANDS[brand]["taste_profile"]["진함"]
                            sweetness = BRANDS[brand]["taste_profile"]["단맛"]
                            st.markdown("**맛 특성:**")
                            st.markdown(f"단맛: {'🔵' * sweetness}{'⚪' * (4-sweetness)} ({sweetness}/4)")
                            st.markdown(f"진함: {'🔵' * cleanness}{'⚪' * (4-cleanness)} ({cleanness}/4)")
                            if not (i == len(brand_list) - 2 and j == 1):
                                st.markdown("---")
            display_brand_rankings()
            st.info("📝 각 브랜드의 맛 특성을 확인하신 후, 다음 단계에서 실제 시음을 진행해주세요!")
            col_prev, col_next = st.columns([1, 1])
            with col_prev:
                if st.button("⬅️ 이전 단계로", key="step2_prev", use_container_width=True):
                    st.session_state.step = 1; st.rerun()
            with col_next:
                if st.button("시음 평가하기 ➡️", key="step2_next", use_container_width=True):
                    st.session_state.step = 3; st.rerun()

        # 3단계: 시음 평가
        elif st.session_state.step == 3:
            st.markdown("""
                <div class="section-header eval">
                    <h1 class="main-title">시음 평가</h1>
                    <p class="subtitle">1, 2, 3, 4 두유를 시음하고 각각의 맛을 평가해주세요.</p>
                </div>
                """, unsafe_allow_html=True)

            samples = SAMPLES

            def get_selected_brands():
                return [st.session_state.get(f"{s}_brand", "선택하세요") for s in samples if st.session_state.get(f"{s}_brand", "선택하세요") != "선택하세요"]

            def get_available_brands(current_sample):
                selected = get_selected_brands()
                current = st.session_state.get(f"{current_sample}_brand", "선택하세요")
                opts = ["선택하세요"]
                for b in BRANDS.keys():
                    if b not in selected or b == current:
                        opts.append(b)
                return opts

            for row in range(2):
                col1, col2 = st.columns(2)
                for col_idx, col in enumerate([col1, col2]):
                    idx = row * 2 + col_idx
                    if idx < len(samples):
                        sample = samples[idx]
                        with col:
                            st.markdown(f"""<div class="sample-card"><div class="sample-title">🥛 {sample}_두유</div></div>""", unsafe_allow_html=True)
                            sweetness = st.slider("**1) 단맛 정도**", 1, 4, 2, help="1: 달지 않음, 4: 달큰함", key=f"{sample}_sweetness")
                            st.markdown(f"현재 값: {sweetness}/4 {'🔵' * sweetness}{'⚪' * (4-sweetness)}")
                            cleanness = st.slider("**2) 맛의 진함**", 1, 4, 2, help="1: 매우 깔끔함, 4: 매우 진함", key=f"{sample}_cleanness")
                            st.markdown(f"현재 값: {cleanness}/4 {'🔵' * cleanness}{'⚪' * (4-cleanness)}")
                            available = get_available_brands(sample)
                            current_selection = st.session_state.get(f"{sample}_brand", "선택하세요")
                            if current_selection not in available: current_selection = "선택하세요"
                            selected_brand = st.selectbox("**3) 어떤 브랜드일까요?**", available, index=available.index(current_selection) if current_selection in available else 0, key=f"{sample}_brand")
                            if selected_brand != "선택하세요":
                                dups = [s for s in samples if s != sample and st.session_state.get(f"{s}_brand") == selected_brand]
                                if dups:
                                    st.warning(f"⚠️ {selected_brand}는 {', '.join(dups)} 샘플에서도 선택되었습니다! (각 브랜드는 한 번만)")
                            fig = create_modern_taste_profile({"진함": cleanness, "단맛": sweetness}, f"{sample} 두유 평가")
                            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

            st.markdown('<div class="section-header">📋 현재 선택 현황</div>', unsafe_allow_html=True)
            status_df = pd.DataFrame([{
                "샘플": f"{s}_두유",
                "선택한 브랜드": st.session_state.get(f"{s}_brand", "선택하세요"),
                "상태": "✅ 완료" if st.session_state.get(f"{s}_brand", "선택하세요") != "선택하세요" else "❌ 미완료"
            } for s in samples])
            st.dataframe(status_df, use_container_width=True)

            all_completed = all([st.session_state.get(f"{s}_brand", "선택하세요") != "선택하세요" for s in samples])
            selected = get_selected_brands()
            has_duplicates = len(selected) != len(set(selected))
            if all_completed and not has_duplicates:
                st.success("🎉 모든 두유 평가가 완료되었습니다!")
            elif not all_completed:
                st.warning("⚠️ 모든 두유의 브랜드를 선택해주세요.")
            elif has_duplicates:
                st.error("❌ 중복된 브랜드가 선택되었습니다. 각 브랜드는 한 번만 선택.")

            col_prev, col_next = st.columns([1, 1])
            with col_prev:
                if st.button("⬅️ 이전 단계로", key="step3_prev", use_container_width=True):
                    st.session_state.step = 2; st.rerun()
            with col_next:
                if all_completed and not has_duplicates:
                    if st.button("평가 완료하기 ➡️", key="step3_complete", use_container_width=True):
                        st.session_state.taste_evaluations = {
                            s: {"진함": st.session_state[f"{s}_cleanness"], "단맛": st.session_state[f"{s}_sweetness"], "선택브랜드": st.session_state[f"{s}_brand"]}
                            for s in samples
                        }
                        st.session_state.step = 4; st.rerun()

        # 4단계: 결과 제출
        elif st.session_state.step == 4:
            st.markdown('<div class="section-header">🎉 평가 완료!</div>', unsafe_allow_html=True)
            participant = st.session_state.participant_info
            st.markdown(f"""
            <div class="results-summary">
                <h3 style="color: #2980b9; margin-bottom: 20px;">📋 평가 결과 요약</h3>
                <p><strong>참여자:</strong> {participant['name']} ({participant['gender']}, {participant['age']}세)</p>
                <p><strong>소속:</strong> {participant['organization']}</p>
            </div>
            """, unsafe_allow_html=True)

            results_data = []
            for s in SAMPLES:
                ev = st.session_state.taste_evaluations.get(s, {"진함": 0, "단맛": 0, "선택브랜드": "선택안함"})
                results_data.append({
                    '샘플': f'{s}_두유',
                    '진함 (1-4)': f"{ev['진함']}/4 {'🔵' * ev['진함']}{'⚪' * (4-ev['진함'])}",
                    '단맛 (1-4)': f"{ev['단맛']}/4 {'🔵' * ev['단맛']}{'⚪' * (4-ev['단맛'])}",
                    '예상 브랜드': ev['선택브랜드']
                })
            st.dataframe(pd.DataFrame(results_data), use_container_width=True)

            submit_clicked = False
            col_prev, col_submit, col_reset = st.columns([1, 1, 1])
            with col_prev:
                if st.button("⬅️ 이전 단계", key="step4_prev", use_container_width=True):
                    st.session_state.step = 3; st.rerun()
            with col_submit:
                submit_clicked = st.button("➡️ 최종 제출 (Supabase 저장)", key="step4_submit", use_container_width=True)
            with col_reset:
                if st.button("🔄 새로 시작", key="step4_reset", use_container_width=True):
                    for key in list(st.session_state.keys()): del st.session_state[key]
                    st.rerun()

            if submit_clicked:
                # 17개 컬럼 dict 구성
                kst = pytz.timezone('Asia/Seoul')
                now_kst = datetime.now(kst)
                row = {
                    "이름": participant["name"],
                    "성별": participant["gender"],
                    "연령": participant["age"],
                    "소속": participant["organization"],
                    # 제출시간은 UTC로 저장 (timestamptz)
                    "제출시간": now_kst.astimezone(timezone.utc).isoformat()
                }
                for s in SAMPLES:
                    ev = st.session_state.taste_evaluations.get(s, {"진함": "", "단맛": "", "선택브랜드": ""})
                    row[f"{s}_진함"] = str(ev.get("진함", ""))
                    row[f"{s}_단맛"] = str(ev.get("단맛", ""))
                    row[f"{s}_선택브랜드"] = ev.get("선택브랜드", "")

                if insert_response_row(row):
                    st.markdown("""
                    <div style="width:100%;text-align:center;font-size:1.5rem;font-weight:600;color:#2980b9;margin:20px 0 10px;padding:16px;">
                        제출이 완료되었습니다! 참여해주셔서 감사합니다.
                    </div>
                    """, unsafe_allow_html=True)

                    # 정답/오답 피드백 (예시 정답)
                    correct_answers = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
                    details, correct_count, wrong_samples = [], 0, []
                    for s in SAMPLES:
                        chosen = st.session_state.taste_evaluations.get(s, {}).get('선택브랜드', '')
                        answer = correct_answers.get(s, '')
                        is_correct = (chosen == answer)
                        if is_correct: correct_count += 1
                        else: wrong_samples.append(f"{s}번(정답 {answer}, 선택 {chosen or '미선택'})")
                        details.append({"샘플": f"{s}번", "정답": answer, "선택": chosen or "미선택", "결과": "✅ 정답" if is_correct else "❌ 오답"})
                    wrong_count = len(SAMPLES) - correct_count
                    if wrong_count == 0:
                        st.success("🏆 4개의 두유 브랜드를 모두 맞추셨습니다. 진정한 두믈리에입니다!")
                        st.balloons()
                    else:
                        st.info(f"결과 요약: {correct_count}/4개 정답, {wrong_count}개 오답")
                    if wrong_samples:
                        st.markdown("**오답 항목:** " + ", ".join(wrong_samples))
                    st.dataframe(pd.DataFrame(details), use_container_width=True)
                else:
                    st.error("제출 중 오류가 발생했습니다. 다시 시도해주세요.")

def admin_dashboard():
    admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_password")
    if admin_password != "admin123":
        st.warning("⚠️ 관리자 비밀번호를 입력해주세요.")
        return

    if st.button("📊 전체 데이터 보기", key="admin_show_all", use_container_width=True):
        show_all_data()

    st.markdown('<div class="section-header">🏢 소속별 결과 분석</div>', unsafe_allow_html=True)
    organization_filter = st.text_input("분석할 소속명을 입력하세요", key="admin_org_filter")
    if organization_filter:
        if st.button("📈 분석하기", use_container_width=True):
            show_organization_analysis(organization_filter)

def show_all_data():
    df = fetch_all_responses_df()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.markdown('<div class="section-header">📈 기본 통계</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("총 참여자", len(df))
        with col2:
            if '소속' in df.columns: st.metric("참여 소속 수", df['소속'].nunique())
        with col3:
            if '성별' in df.columns:
                male_count = (df['성별'].astype(str).str.contains('남')).sum()
                st.metric("남성(키워드 매칭)", male_count)
        with col4:
            if '성별' in df.columns:
                female_count = (df['성별'].astype(str).str.contains('여')).sum()
                st.metric("여성(키워드 매칭)", female_count)
    else:
        st.info("아직 데이터가 없습니다.")

def show_organization_analysis(organization_filter):
    samples = ['1', '2', '3', '4']
    df = fetch_org_responses_df(organization_filter)
    if df.empty:
        st.info(f"'{organization_filter}' 소속의 데이터가 없습니다.")
        return

    st.write(f"📈 **{organization_filter}** 소속 참여자: {len(df)}명")

    correct_answers = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    all_correct_participants = []
    for _, row in df.iterrows():
        correct_count = sum(1 for s in samples if row.get(f'{s}_선택브랜드') == correct_answers[s])
        if correct_count == 4:
            all_correct_participants.append(row.get('이름', ''))

    if all_correct_participants:
        names = ', '.join([n for n in all_correct_participants if n])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 25px;
                    border-radius: 20px; text-align: center; font-size: 1.5rem; font-weight: 700;">
            🏆 완벽한 두믈리에 탄생 🏆<br>
            <span style="font-size:1.2rem; font-weight:500;">{names}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🎯 아직 네 개 브랜드를 모두 맞춘 참여자가 없습니다.")

    detailed_results = []
    for _, row in df.iterrows():
        result = {'이름': row.get('이름', ''), '성별': row.get('성별', ''), '연령': row.get('연령', '')}
        correct_count = 0
        for s in samples:
            selected_brand = row.get(f'{s}_선택브랜드', '')
            is_correct = selected_brand == correct_answers[s]
            if is_correct: correct_count += 1
            result[f'{s}_선택'] = selected_brand
            result[f'{s}_정답'] = '✅' if is_correct else '❌'
            result[f'{s}_진함'] = row.get(f'{s}_진함', '')
            result[f'{s}_단맛'] = row.get(f'{s}_단맛', '')
        result['총_정답수'] = f"{correct_count}/4"
        detailed_results.append(result)

    results_df = pd.DataFrame(detailed_results)
    st.markdown('<div class="section-header">📋 상세 결과</div>', unsafe_allow_html=True)
    results_df['정답순서'] = results_df['총_정답수'].apply(lambda x: int(x.split('/')[0]))
    results_df = results_df.sort_values('정답순서', ascending=False).drop('정답순서', axis=1)
    st.dataframe(results_df, use_container_width=True)

    st.markdown('<div class="section-header">📊 정답률 분석</div>', unsafe_allow_html=True)
    accuracy_data = []
    for s in samples:
        correct_count = sum(1 for _, r in df.iterrows() if r.get(f'{s}_선택브랜드') == correct_answers[s])
        accuracy_rate = (correct_count / len(df)) * 100 if len(df) else 0.0
        accuracy_data.append({'샘플': f'{s}\n({correct_answers[s]})', '정답률': accuracy_rate, '정답자수': correct_count, '전체': len(df)})
    accuracy_df = pd.DataFrame(accuracy_data)

    fig_bar = go.Figure(data=[go.Bar(
        x=accuracy_df['샘플'],
        y=accuracy_df['정답률'],
        text=[f"{rate:.1f}%<br>({c}/{t})" for rate, c, t in zip(accuracy_df['정답률'], accuracy_df['정답자수'], accuracy_df['전체'])],
        textposition='auto',
        marker_color=['#3498db', '#2980b9', '#1e88e5', '#1976d2']
    )])
    fig_bar.update_layout(
        title=f"{organization_filter} 브랜드별 정답률",
        xaxis_title="두유 샘플", yaxis_title="정답률 (%)", yaxis=dict(range=[0, 100]),
        height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Noto Sans KR', color='#2c3e50')
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)

    total_correct = accuracy_df['정답자수'].sum()
    total_attempts = len(df) * 4
    overall_accuracy = (total_correct / total_attempts) * 100 if total_attempts else 0.0
    col1, col2 = st.columns([2, 8])
    with col1:
        st.metric(label="전체 정답률", value=f"{overall_accuracy:.1f}%", delta=f"{total_correct}/{total_attempts}")
        st.metric(label="완벽한 정답자", value=f"{len(all_correct_participants)}명", delta=f"{len(all_correct_participants)}/{len(df)}")
    with col2:
        st.markdown("브랜드별 상세 정답률")
        subcols = st.columns(len(accuracy_df))
        for scol, (_, row) in zip(subcols, accuracy_df.iterrows()):
            with scol:
                st.metric(label=row['샘플'].replace('\n', ' '), value=f"{row['정답률']:.1f}%", delta=f"{row['정답자수']}/{row['전체']}")

if __name__ == "__main__":
    main()
