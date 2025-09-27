# ===================== MUST BE FIRST =====================
import streamlit as st
st.set_page_config(page_title="두믈리에 챌린지", page_icon="🥛", layout="wide", initial_sidebar_state="collapsed")
# ========================================================

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
import pytz
import textwrap
import streamlit.components.v1 as components

# ---------- Supabase ----------
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]  # 서버사이드 키
    return create_client(url, key)

# ---------- Plotly ----------
PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}

# ---------- CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    .stApp { background:#fff; font-family:'Noto Sans KR', sans-serif; }
    .main-header { text-align:center; padding:40px 0; background:linear-gradient(135deg, rgba(52,152,219,.1), rgba(41,128,185,.05)); border-radius:25px; margin-bottom:30px; border:2px solid rgba(52,152,219,.2); position:relative; overflow:hidden; }
    .main-header::before { content:''; position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg,#3498db,#2980b9,#1e88e5); }
    .main-title { font-size:3.0rem; font-weight:700; background:linear-gradient(45deg,#3498db,#2980b9,#1e88e5); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:10px; }
    .subtitle { font-size:1.1rem; color:#7f8c8d; }
    .section-header { color:#2980b9; font-size:1.6rem; font-weight:600; text-align:center; margin:26px 0; padding:14px; background:linear-gradient(135deg, rgba(52,152,219,.08), rgba(41,128,185,.05)); border-radius:14px; border:2px solid rgba(52,152,219,.18); }
    .brand-card { background:#fff; border-radius:20px; padding:22px; box-shadow:0 10px 30px rgba(0,0,0,.06); border:2px solid rgba(52,152,219,.1); position:relative; }
    .brand-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#3498db,#2980b9); }
    .brand-name { font-size:1.25rem; font-weight:700; color:#2980b9; margin-bottom:8px; }
    .sample-card { background:#fff; border-radius:20px; padding:22px; margin:16px 0; box-shadow:0 10px 30px rgba(0,0,0,.06); border:2px solid rgba(52,152,219,.1); }
    .sample-title { font-size:1.35rem; font-weight:700; color:#2980b9; text-align:center; margin-bottom:14px; padding:12px; background:linear-gradient(135deg, rgba(52,152,219,.08), rgba(41,128,185,.05)); border-radius:10px; }
    .results-summary { background:linear-gradient(135deg, rgba(52,152,219,.08), rgba(41,128,185,.08)); border-radius:16px; padding:22px; margin:18px 0; border:2px solid rgba(52,152,219,.18); }
    .stButton > button { background:linear-gradient(135deg,#3498db,#2980b9); color:#fff; border:none; border-radius:12px; padding:12px 22px; font-weight:700; box-shadow:0 4px 14px rgba(52,152,219,.28); }
    .stButton > button:hover { transform:translateY(-1px); box-shadow:0 6px 18px rgba(52,152,219,.36); }
    @media (max-width:768px) {
      :root { --pad-x: 12px; }
      section[data-testid="stMain"] .block-container{ padding-left:var(--pad-x)!important; padding-right:var(--pad-x)!important; }
      .main-title{ font-size:2.0rem; }
    }
</style>
""", unsafe_allow_html=True)

# ---------- Domain ----------
BRANDS = {
    "A": {"taste_profile": {"진함": 4, "단맛": 1}},
    "B": {"taste_profile": {"진함": 3, "단맛": 4}},
    "C": {"taste_profile": {"진함": 1, "단맛": 2}},
    "D": {"taste_profile": {"진함": 2, "단맛": 3}},
}
SAMPLES = ["1", "2", "3", "4"]

# ---------- Helpers ----------
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
        plot_bgcolor='rgba(255,255,255,0.8)', margin=dict(l=80, r=50, t=50, b=40),
        font=dict(family='Noto Sans KR', color='#2c3e50')
    )
    return fig

def display_brand_rankings():
    st.markdown('<div class="section-header">📊 브랜드 맛 특성 순위</div>', unsafe_allow_html=True)
    by_intensity = sorted(BRANDS.items(), key=lambda x: x[1]["taste_profile"]["진함"], reverse=True)
    by_sweet = sorted(BRANDS.items(), key=lambda x: x[1]["taste_profile"]["단맛"], reverse=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="brand-card"><div class="brand-name">진함 순위</div>""", unsafe_allow_html=True)
        for i, (b, info) in enumerate(by_intensity, 1):
            v = info["taste_profile"]["진함"]; bar = "🔵"*v + "⚪"*(4-v); medal = ["🥇","🥈","🥉","🏅"][i-1]
            st.markdown(f"- {medal} {i}위 {b}: {bar} ({v}/4)")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="brand-card"><div class="brand-name">단맛 순위</div>""", unsafe_allow_html=True)
        for i, (b, info) in enumerate(by_sweet, 1):
            v = info["taste_profile"]["단맛"]; bar = "🔵"*v + "⚪"*(4-v); medal = ["🥇","🥈","🥉","🏅"][i-1]
            st.markdown(f"- {medal} {i}위 {b}: {bar} ({v}/4)")
        st.markdown("</div>", unsafe_allow_html=True)

def insert_response_row(row: dict) -> bool:
    try:
        sb = get_supabase()
        sb.table("tasting_responses").insert(row).execute()
        return True
    except Exception as e:
        st.error(f"❌ 데이터 저장 오류: {e}")
        return False

def fetch_all_responses_df() -> pd.DataFrame:
    try:
        sb = get_supabase()
        res = sb.table("tasting_responses").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(res.data or [])
        if not df.empty and "제출시간" in df.columns:
            df["제출시간(KST)"] = pd.to_datetime(df["제출시간"], utc=True).dt.tz_convert("Asia/Seoul").dt.strftime("%Y-%m-%d %H:%M:%S")
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

def fetch_org_responses_df(org: str) -> pd.DataFrame:
    try:
        sb = get_supabase()
        res = sb.table("tasting_responses").select("*").eq("소속", org).execute()
        return pd.DataFrame(res.data or [])
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

# ---------- Pages ----------
def main():
    # ✅ 페이지 맨 위에서 CSS 먼저 추가
    st.markdown("""
    <style>
    /* 탭 중앙 정렬 */
    .stTabs [data-baseweb="tab-list"]{
      display: flex !important;
      justify-content: center !important;
      width: 100%;
      gap: 12px;
    }
    .stTabs [data-baseweb="tab"]{
      min-width: 0;
      padding: 0 20px;
    }

    /* 본문 가운데 정렬 */
    section[data-testid="stMain"] .block-container{
      max-width: 1100px;
      margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # ✅ 헤더
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">두믈리에 챌린지</h1>
        <p class="subtitle">자연의 맛을 찾아가는 특별한 여행</p>
    </div>
    """, unsafe_allow_html=True)

    # ✅ 탭 생성
    tab1, tab2, tab3 = st.tabs(["🏠 홈", "🚀 챌린지", "🔧 관리자"])
    with tab1:
        home_page()
    with tab2:
        challenge_page()
    with tab3:
        admin_dashboard()

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
          <div style="font-weight:600; margin-bottom:5px;">서울대학교 정밀푸드솔루션 연구실</div>
          <div style="opacity:.9;">SNU Precision Food Solution Laboratory</div>
          <div style="margin-top:8px; font-size:.8rem; opacity:.8;">© 2025 Seoul National University. 연구 목적 프로그램</div>
      </div>
    </div>
    <style>
      .bottom-banner-wrap{ position:sticky; bottom:0; z-index:1000; --gap:80px; }
      .bottom-banner-wrap::before{ content:''; display:block; height:var(--gap); }
      .bottom-banner{ background:linear-gradient(135deg,#3498db,#2980b9); padding:14px 0; text-align:center; color:#fff; width:100vw; margin-left:calc(50% - 50vw); }
    </style>
    """, unsafe_allow_html=True)

def home_page():
    st.markdown("""
        <div style="background: rgba(52,152,219,.05); padding:24px; border-radius:16px; border:2px solid rgba(52,152,219,.12); margin: 12px 0;">
            <h3 style="color:#2980b9; margin-bottom:10px;">🥛 두믈리에 챌린지란?</h3>
            <p style="font-size:16px; line-height:1.7; color:#2c3e50;">
                네 가지 두유를 시음하고 맛 특성을 평가한 뒤, 어떤 브랜드인지 맞춰보는 블라인드 테스트입니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

    steps = [
        {"icon":"📝","title":"참여자 정보 입력","desc":"이름, 성별, 연령, 소속을 입력합니다"},
        {"icon":"👀","title":"브랜드 소개","desc":"네 가지 브랜드의 맛 프로필을 확인합니다"},
        {"icon":"👅","title":"시음 평가","desc":"각 두유의 맛을 평가하고 브랜드를 선택합니다"},
        {"icon":"🎉","title":"결과 확인","desc":"평가 결과를 확인하고 제출합니다"},
    ]

    st.markdown("""
    <style>
      .home-steps{ display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:12px; margin-top:8px; }
      .home-step-card{ background:#fff; border-radius:16px; border:2px solid rgba(52,152,219,.12); box-shadow:0 6px 20px rgba(0,0,0,.06); padding:28px 16px; min-height:200px; display:flex; flex-direction:column; justify-content:space-between; align-items:center; }
      @media (max-width:768px){ .home-steps{ grid-template-columns:1fr; gap:14px; } .home-step-card{ min-height:180px; } }
    </style>
    """, unsafe_allow_html=True)

    cards = ['<div class="home-steps">']
    for i, s in enumerate(steps, start=1):
        cards.append(textwrap.dedent(f"""
        <div class="home-step-card">
          <div style="font-size:40px;line-height:1">{s['icon']}</div>
          <div style="color:#2980b9;font-weight:700;font-size:16px;text-align:center;margin:6px 0">
            Step {i}<br>{s['title']}
          </div>
          <div style="color:#7f8c8d;font-size:13px;line-height:1.5;text-align:center">{s['desc']}</div>
        </div>
        """).strip())
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        if st.button("🚀 챌린지 시작하기", use_container_width=True, key="home_start"):
            st.session_state["jump_to_challenge"] = True
            st.session_state.step = 1
            st.rerun()

def challenge_page():
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'participant_info' not in st.session_state: st.session_state.participant_info = {}
    if 'taste_evaluations' not in st.session_state: st.session_state.taste_evaluations = {}

    # 1단계
    if st.session_state.step == 1:
        st.markdown('<div class="section-header">참여자 정보 입력</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            name = st.text_input("이름", key="name", placeholder="예) 김스누")
            gender = st.text_input("성별", key="gender", placeholder="예) 남/여")
        with c2:
            age = st.text_input("연령", key="age", placeholder="예) 35")
            organization = st.text_input("소속", key="organization", placeholder="예) 푸드테크 최고책임자")
        st.markdown("<br>", unsafe_allow_html=True)
        cc1,cc2,cc3 = st.columns([1,2,1])
        with cc2:
            if st.button("다음 단계로", use_container_width=True, key="next1"):
                if name and gender and age and organization:
                    st.session_state.participant_info = {"name":name,"gender":gender,"age":age,"organization":organization}
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("모든 정보를 입력해주세요.")

    # 2단계
    elif st.session_state.step == 2:
        st.markdown('<div class="section-header">🥛 네 가지 두유 브랜드 소개</div>', unsafe_allow_html=True)
        lst = sorted(BRANDS.keys())
        for i in range(0, len(lst), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(lst):
                    b = lst[i+j]
                    with cols[j]:
                        st.markdown(f"""<div class="brand-card"><div class="brand-name">{b}</div></div>""", unsafe_allow_html=True)
                        fig = create_modern_taste_profile(BRANDS[b]["taste_profile"], f"{b} 맛 프로필")
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
                        jin = BRANDS[b]["taste_profile"]["진함"]; dan = BRANDS[b]["taste_profile"]["단맛"]
                        st.markdown(f"- 단맛: {'🔵'*dan}{'⚪'*(4-dan)} ({dan}/4)")
                        st.markdown(f"- 진함: {'🔵'*jin}{'⚪'*(4-jin)} ({jin}/4)")
                        if not (i == len(lst) - 2 and j == 1): st.markdown("---")
        display_brand_rankings()
        st.info("📝 특성을 확인하셨다면, 다음 단계에서 실제 시음을 진행해주세요!")
        p,n = st.columns(2)
        with p:
            if st.button("⬅️ 이전 단계로", use_container_width=True, key="prev2"):
                st.session_state.step = 1; st.rerun()
        with n:
            if st.button("시음 평가하기 ➡️", use_container_width=True, key="next2"):
                st.session_state.step = 3; st.rerun()

    # 3단계
    elif st.session_state.step == 3:
        st.markdown('<div class="section-header">시음 평가</div>', unsafe_allow_html=True)

        def selected_brands():
            return [st.session_state.get(f"{s}_brand","선택하세요") for s in SAMPLES if st.session_state.get(f"{s}_brand","선택하세요")!="선택하세요"]

        def available_for(sample):
            used = selected_brands()
            cur = st.session_state.get(f"{sample}_brand","선택하세요")
            opts = ["선택하세요"]
            for b in BRANDS.keys():
                if b not in used or b == cur: opts.append(b)
            return opts

        for row in range(2):
            c1,c2 = st.columns(2)
            for col, idx in zip([c1,c2], [row*2, row*2+1]):
                if idx < len(SAMPLES):
                    s = SAMPLES[idx]
                    with col:
                        st.markdown(f"""<div class="sample-card"><div class="sample-title">🥛 {s}_두유</div></div>""", unsafe_allow_html=True)
                        sweet = st.slider("**1) 단맛 정도**", 1, 4, 2, help="1: 달지 않음, 4: 달큰함", key=f"{s}_sweetness")
                        st.markdown(f"현재 값: {sweet}/4 {'🔵'*sweet}{'⚪'*(4-sweet)}")
                        deep = st.slider("**2) 맛의 진함**", 1, 4, 2, help="1: 매우 깔끔함, 4: 매우 진함", key=f"{s}_cleanness")
                        st.markdown(f"현재 값: {deep}/4 {'🔵'*deep}{'⚪'*(4-deep)}")
                        opts = available_for(s)
                        cur = st.session_state.get(f"{s}_brand","선택하세요")
                        if cur not in opts: cur = "선택하세요"
                        chosen = st.selectbox("**3) 어떤 브랜드일까요?**", opts, index=opts.index(cur), key=f"{s}_brand")
                        if chosen != "선택하세요":
                            dups = [x for x in SAMPLES if x!=s and st.session_state.get(f"{x}_brand")==chosen]
                            if dups:
                                st.warning(f"⚠️ {chosen}는 {', '.join(dups)} 샘플에서도 선택! (브랜드는 1회만)")
                        fig = create_modern_taste_profile({"진함": deep, "단맛": sweet}, f"{s} 두유 평가")
                        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

        st.markdown('<div class="section-header">📋 현재 선택 현황</div>', unsafe_allow_html=True)
        status_df = pd.DataFrame([{
            "샘플": f"{s}_두유",
            "선택한 브랜드": st.session_state.get(f"{s}_brand","선택하세요"),
            "상태": "✅ 완료" if st.session_state.get(f"{s}_brand","선택하세요")!="선택하세요" else "❌ 미완료"
        } for s in SAMPLES])
        st.dataframe(status_df, use_container_width=True)

        all_done = all([st.session_state.get(f"{s}_brand","선택하세요")!="선택하세요" for s in SAMPLES])
        used = selected_brands()
        dup = len(used)!=len(set(used))
        if all_done and not dup: st.success("🎉 모든 두유 평가가 완료되었습니다!")
        elif not all_done: st.warning("⚠️ 모든 두유의 브랜드를 선택해주세요.")
        elif dup: st.error("❌ 중복된 브랜드가 선택되었습니다. 각 브랜드는 1회만.")

        p,n = st.columns(2)
        with p:
            if st.button("⬅️ 이전 단계로", use_container_width=True, key="prev3"):
                st.session_state.step = 2; st.rerun()
        with n:
            if all_done and not dup:
                if st.button("평가 완료하기 ➡️", use_container_width=True, key="done3"):
                    st.session_state.taste_evaluations = {
                        s: {"진함": st.session_state[f"{s}_cleanness"], "단맛": st.session_state[f"{s}_sweetness"], "선택브랜드": st.session_state[f"{s}_brand"]}
                        for s in SAMPLES
                    }
                    st.session_state.step = 4; st.rerun()

    # 4단계
    elif st.session_state.step == 4:
        st.markdown('<div class="section-header">🎉 평가 완료!</div>', unsafe_allow_html=True)
        pinfo = st.session_state.participant_info
        st.markdown(f"""
        <div class="results-summary">
            <h4 style="color:#2980b9; margin-bottom:10px;">📋 평가 결과 요약</h4>
            <p><strong>참여자:</strong> {pinfo['name']} ({pinfo['gender']}, {pinfo['age']}세)</p>
            <p><strong>소속:</strong> {pinfo['organization']}</p>
        </div>
        """, unsafe_allow_html=True)

        table_rows = []
        for s in SAMPLES:
            ev = st.session_state.taste_evaluations.get(s, {"진함":0, "단맛":0, "선택브랜드":"선택안함"})
            table_rows.append({
                "샘플": f"{s}_두유",
                "진함 (1-4)": f"{ev['진함']}/4 {'🔵'*ev['진함']}{'⚪'*(4-ev['진함'])}",
                "단맛 (1-4)": f"{ev['단맛']}/4 {'🔵'*ev['단맛']}{'⚪'*(4-ev['단맛'])}",
                "예상 브랜드": ev["선택브랜드"]
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        c_prev, c_submit, c_reset = st.columns([1,1,1])
        with c_prev:
            if st.button("⬅️ 이전 단계", key="prev4", use_container_width=True):
                st.session_state.step = 3; st.rerun()
        submitted = False
        with c_submit:
            submitted = st.button("➡️ 최종 제출", key="submit4", use_container_width=True)
        with c_reset:
            if st.button("🔄 새로 시작", key="reset4", use_container_width=True):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

        if submitted:
            # 17개 컬럼으로 저장
            kst = pytz.timezone("Asia/Seoul")
            now_kst = datetime.now(kst)
            row = {
                "이름": pinfo["name"],
                "성별": pinfo["gender"],
                "연령": pinfo["age"],
                "소속": pinfo["organization"],
                "제출시간": now_kst.astimezone(timezone.utc).isoformat()
            }
            for s in SAMPLES:
                ev = st.session_state.taste_evaluations.get(s, {"진함":"", "단맛":"", "선택브랜드":""})
                row[f"{s}_진함"] = str(ev.get("진함",""))
                row[f"{s}_단맛"] = str(ev.get("단맛",""))
                row[f"{s}_선택브랜드"] = ev.get("선택브랜드","")

            if insert_response_row(row):
                st.success("✅ 제출이 완료되었습니다! 참여해주셔서 감사합니다.")
                # 간단 피드백 예시
                answers = {'1':'A','2':'B','3':'C','4':'D'}
                details, correct = [], 0
                for s in SAMPLES:
                    chosen = st.session_state.taste_evaluations.get(s,{}).get("선택브랜드","")
                    ok = (chosen == answers[s])
                    if ok: correct += 1
                    details.append({"샘플": f"{s}번", "정답": answers[s], "선택": chosen or "미선택", "결과": "✅" if ok else "❌"})
                st.info(f"결과 요약: {correct}/4개 정답")
                st.dataframe(pd.DataFrame(details), use_container_width=True)
            else:
                st.error("저장 중 오류가 발생했습니다. 다시 시도해주세요.")

def admin_dashboard():
    pwd = st.text_input("관리자 비밀번호", type="password", key="admin_password")
    if pwd != "admin123":
        st.warning("⚠️ 관리자 비밀번호를 입력해주세요.")
        return

    if st.button("📊 전체 데이터 보기", key="admin_show_all", use_container_width=True):
        show_all_data()

    st.markdown('<div class="section-header">🏢 소속별 결과 분석</div>', unsafe_allow_html=True)
    org = st.text_input("분석할 소속명을 입력하세요", key="admin_org")
    if org and st.button("📈 분석하기", use_container_width=True, key="admin_analyze"):
        show_organization_analysis(org)

def show_all_data():
    df = fetch_all_responses_df()
    if df.empty:
        st.info("아직 데이터가 없습니다.")
        return
    st.dataframe(df, use_container_width=True)
    st.markdown('<div class="section-header">📈 기본 통계</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("총 참여자", len(df))
    with c2:
        if '소속' in df.columns: st.metric("참여 소속 수", df['소속'].nunique())
    with c3:
        if '성별' in df.columns: st.metric("남성(키워드)", (df['성별'].astype(str).str.contains('남')).sum())
    with c4:
        if '성별' in df.columns: st.metric("여성(키워드)", (df['성별'].astype(str).str.contains('여')).sum())

def show_organization_analysis(org):
    samples = ['1','2','3','4']
    df = fetch_org_responses_df(org)
    if df.empty:
        st.info(f"'{org}' 소속의 데이터가 없습니다.")
        return

    st.write(f"📈 **{org}** 소속 참여자: {len(df)}명")
    answers = {'1':'A','2':'B','3':'C','4':'D'}
    all_correct = []
    for _, r in df.iterrows():
        if sum(1 for s in samples if r.get(f"{s}_선택브랜드")==answers[s]) == 4:
            all_correct.append(r.get("이름",""))
    if all_correct:
        st.success("🏆 완벽한 두믈리에: " + ", ".join([x for x in all_correct if x]))
    else:
        st.info("🎯 아직 네 개 브랜드를 모두 맞춘 참여자가 없습니다.")

    detailed = []
    for _, r in df.iterrows():
        row = {"이름": r.get("이름",""), "성별": r.get("성별",""), "연령": r.get("연령","")}
        ok = 0
        for s in samples:
            sel = r.get(f"{s}_선택브랜드","")
            good = sel == answers[s]
            if good: ok += 1
            row[f"{s}_선택"] = sel
            row[f"{s}_정답"] = "✅" if good else "❌"
            row[f"{s}_진함"] = r.get(f"{s}_진함","")
            row[f"{s}_단맛"] = r.get(f"{s}_단맛","")
        row["총_정답수"] = f"{ok}/4"
        detailed.append(row)
    resdf = pd.DataFrame(detailed)
    st.markdown('<div class="section-header">📋 상세 결과</div>', unsafe_allow_html=True)
    resdf["정렬키"] = resdf["총_정답수"].str.split("/").str[0].astype(int)
    resdf = resdf.sort_values("정렬키", ascending=False).drop(columns=["정렬키"])
    st.dataframe(resdf, use_container_width=True)

    # 정답률 막대
    acc = []
    for s in samples:
        c = sum(1 for _, r in df.iterrows() if r.get(f"{s}_선택브랜드")==answers[s])
        acc.append({"샘플": f"{s} ({answers[s]})", "정답률": (c/len(df))*100, "정답자수": c, "전체": len(df)})
    accdf = pd.DataFrame(acc)
    fig = go.Figure(data=[go.Bar(
        x=accdf["샘플"], y=accdf["정답률"],
        text=[f"{r:.1f}% ({c}/{t})" for r,c,t in zip(accdf["정답률"], accdf["정답자수"], accdf["전체"])],
        textposition="auto", marker_color=['#3498db','#2980b9','#1e88e5','#1976d2']
    )])
    fig.update_layout(title=f"{org} 브랜드별 정답률", yaxis=dict(range=[0,100]), height=380,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Noto Sans KR', color='#2c3e50'))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    total_correct = accdf["정답자수"].sum()
    total = len(df)*4
    overall = (total_correct/total)*100 if total else 0.0
    m1,m2 = st.columns([2,8])
    with m1:
        st.metric("전체 정답률", f"{overall:.1f}%", f"{total_correct}/{total}")
        st.metric("완벽한 정답자", f"{len(all_correct)}명", f"{len(all_correct)}/{len(df)}")
    with m2:
        st.markdown("브랜드별 상세 정답률")
        cols = st.columns(len(accdf))
        for c, (_, r) in zip(cols, accdf.iterrows()):
            with c:
                st.metric(r["샘플"], f"{r['정답률']:.1f}%", f"{r['정답자수']}/{r['전체']}")

if __name__ == "__main__":
    main()
