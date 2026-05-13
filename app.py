import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ───────────────────────────────────────────────
# 페이지 설정
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="경의중앙선은 왜 항상 기다리는가?",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%); color: #e6edf3; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #161b22 0%, #0d1117 100%); border-right: 1px solid #30363d; }
.hero-banner {
    background: linear-gradient(90deg, #1a2a4a 0%, #0d1a2e 40%, #1a1a2e 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.hero-banner::before { content: "🚆"; position: absolute; right: 2rem; top: 50%;
    transform: translateY(-50%); font-size: 6rem; opacity: 0.08; }
.hero-title { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #58a6ff; margin: 0; }
.hero-sub { color: #8b949e; font-size: 0.9rem; margin-top: 0.4rem; }
.metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 1.2rem 1.5rem; text-align: center; transition: border-color 0.2s; }
.metric-card:hover { border-color: #58a6ff; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #58a6ff; }
.metric-label { font-size: 0.78rem; color: #8b949e; margin-top: 0.3rem; }
.section-header { display: flex; align-items: center; gap: 0.6rem;
    margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #30363d; }
.section-number { background: #1f6feb; color: white; font-family: 'Space Mono', monospace;
    font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; }
.section-title { font-size: 1.05rem; font-weight: 600; color: #e6edf3; margin: 0; }
.sql-box { background: #0d1117; border: 1px solid #30363d; border-left: 3px solid #58a6ff;
    border-radius: 8px; padding: 1rem 1.2rem; font-family: 'Space Mono', monospace;
    font-size: 0.78rem; color: #79c0ff; white-space: pre-wrap; line-height: 1.7; }
.insight-box { background: linear-gradient(135deg, #0e2a20 0%, #0d1117 100%);
    border: 1px solid #238636; border-radius: 8px; padding: 1rem 1.2rem;
    font-size: 0.88rem; color: #3fb950; line-height: 1.7; margin-top: 0.8rem; }
.insight-box strong { color: #56d364; }
.error-box { background: #2d1215; border: 1px solid #f85149; border-radius: 10px;
    padding: 1.5rem; text-align: center; color: #f85149; }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# DB 연결
# ───────────────────────────────────────────────
DB_PATH = "railway.db"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, get_connection())

if not os.path.exists(DB_PATH):
    st.markdown(f"""
    <div class="error-box">
        <h2>🚨 railway.db 파일을 찾을 수 없어요!</h2>
        <p style="color:#8b949e; margin-top:1rem;">
            <code>railway.db</code> 파일을 <code>app.py</code>와 같은 폴더에 넣고<br>
            <code>streamlit run app.py</code>를 다시 실행해주세요.<br><br>
            📁 현재 폴더: <code>{os.getcwd()}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ───────────────────────────────────────────────
# 사이드바
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚆 경의중앙선 분석")
    st.markdown("**경의중앙선은 왜 항상 기다리는가?**")
    st.markdown("---")
    st.markdown("### 📅 월 선택")
    selected_month = st.selectbox("분석 월", options=[1, 2, 3],
                                   format_func=lambda x: f"2026년 {x}월")
    st.markdown("### 🚉 노선 구간 선택")
    selected_line = st.selectbox("경의중앙선 구간",
                                  ["경의선+중앙선 (전체)", "경의선만", "중앙선만"])
    if selected_line == "경의선만":
        line_filter = "= '경의선'"
    elif selected_line == "중앙선만":
        line_filter = "= '중앙선'"
    else:
        line_filter = "IN ('경의선', '중앙선')"
    st.markdown("---")
    st.markdown("### 📌 분석 주제")
    st.info("수요는 많고 공급은 부족한\n광역철도의 배차 불균형 분석")
    st.markdown("① 시간대별 승하차 패턴")
    st.markdown("② 노선별 수송량 비교")
    st.markdown("③ 역별 이용량 랭킹")
    st.markdown("---")
    st.caption("데이터: 코레일 광역철도 2026년 1~3월")

# ───────────────────────────────────────────────
# 히어로 배너
# ───────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">경의중앙선은 왜 항상 기다리는가?</div>
    <div class="hero-sub">수요는 많고 공급은 부족한 광역철도의 배차 불균형 | 2026년 1~3월 코레일 공공데이터 분석</div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# KPI 카드
# ───────────────────────────────────────────────
try:
    kpi = run_query(f"""
        SELECT
            COUNT(DISTINCT 역명)                            AS 역수,
            SUM(total)                                      AS 총이용객,
            SUM(t07) + SUM(t08) + SUM(t09)                 AS 아침피크,
            SUM(t17) + SUM(t18) + SUM(t19)                 AS 저녁피크
        FROM 시간대별승하차
        WHERE 노선명 {line_filter} AND 월 = {selected_month} AND 구분 = '승차'
    """).iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, f"{int(kpi['역수'])}개", "분석 역 수"),
        (c2, f"{int(kpi['총이용객']):,}명", f"{selected_month}월 총 승차"),
        (c3, f"{int(kpi['아침피크']):,}명", "아침 피크 (7~9시)"),
        (c4, f"{int(kpi['저녁피크']):,}명", "저녁 피크 (17~19시)"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div>'
                        f'<div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
except Exception as e:
    st.warning(f"KPI 오류: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# 차트 ①  시간대별 승하차 패턴
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">01</span>
    <span class="section-title">시간대별 승하차 패턴 — 언제 가장 붐비는가?</span>
</div>
""", unsafe_allow_html=True)

TIME_LABELS = ["06시이전","07시","08시","09시","10시","11시","12시",
               "13시","14시","15시","16시","17시","18시","19시",
               "20시","21시","22시","23시","24시이후"]
TIME_COLS   = ["t06","t07","t08","t09","t10","t11","t12",
               "t13","t14","t15","t16","t17","t18","t19",
               "t20","t21","t22","t23","t24"]

SQL_01 = f"""
SELECT 구분,
    SUM(t06) AS t06, SUM(t07) AS t07, SUM(t08) AS t08, SUM(t09) AS t09,
    SUM(t10) AS t10, SUM(t11) AS t11, SUM(t12) AS t12, SUM(t13) AS t13,
    SUM(t14) AS t14, SUM(t15) AS t15, SUM(t16) AS t16, SUM(t17) AS t17,
    SUM(t18) AS t18, SUM(t19) AS t19, SUM(t20) AS t20, SUM(t21) AS t21,
    SUM(t22) AS t22, SUM(t23) AS t23, SUM(t24) AS t24
FROM 시간대별승하차
WHERE 노선명 {line_filter} AND 월 = {selected_month}
GROUP BY 구분
"""

try:
    df01 = run_query(SQL_01)
    color_map = {"승차": "#58a6ff", "하차": "#f0883e"}
    fig01 = go.Figure()
    for _, row in df01.iterrows():
        구분 = row["구분"]
        fig01.add_trace(go.Bar(
            name=구분,
            x=TIME_LABELS,
            y=[int(row[c]) for c in TIME_COLS],
            marker_color=color_map.get(구분, "#8b949e"),
            hovertemplate=f"<b>{구분}</b><br>%{{x}}<br>%{{y:,}}명<extra></extra>",
        ))
    for x0, x1, label in [("06시이전","09시","🌅 출근 피크"),("17시","19시","🌆 퇴근 피크")]:
        fig01.add_vrect(x0=x0, x1=x1, fillcolor="#f85149", opacity=0.08,
                        layer="below", line_width=0,
                        annotation_text=label, annotation_position="top left",
                        annotation_font_color="#f85149", annotation_font_size=11)
    fig01.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", height=420,
        xaxis=dict(gridcolor="#21262d", title="시간대"),
        yaxis=dict(gridcolor="#21262d", title="이용객 수 (명)"),
        legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="#30363d"),
        margin=dict(l=0, r=0, t=20, b=20),
    )
    st.plotly_chart(fig01, use_container_width=True)

    col_s, col_i = st.columns([1, 1])
    with col_s:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_01.strip()}</div>', unsafe_allow_html=True)
    with col_i:
        승차행 = df01[df01["구분"] == "승차"]
        if not 승차행.empty:
            peak_idx = 승차행[TIME_COLS].iloc[0].idxmax()
            peak_label = TIME_LABELS[TIME_COLS.index(peak_idx)]
            peak_val = int(승차행[TIME_COLS].iloc[0].max())
            st.markdown(f"""
            <div class="insight-box">
            💡 <strong>인사이트</strong><br><br>
            {selected_month}월 경의중앙선의 최대 승차 피크는
            <strong>{peak_label}대</strong>로 <strong>{peak_val:,}명</strong>이 이용했습니다.<br><br>
            07~09시 출근, 17~19시 퇴근 시간대에 승차가 집중되는
            전형적인 통근 노선 패턴이 나타납니다.<br><br>
            이 시간대에 배차 간격이 길어질 경우 혼잡도와 지연의
            <strong>악순환</strong>이 발생할 수 있습니다.
            </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"차트 ① 오류: {e}")

# ═══════════════════════════════════════════════
# 차트 ②  노선별 수송량 비교
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">02</span>
    <span class="section-title">노선별 수송량 비교 — 경의중앙선의 위치는?</span>
</div>
""", unsafe_allow_html=True)

SQL_02 = """
SELECT 노선명,
    COALESCE(m01,0) AS "1월",
    COALESCE(m02,0) AS "2월",
    COALESCE(m03,0) AS "3월",
    COALESCE(m01,0) + COALESCE(m02,0) + COALESCE(m03,0) AS "1분기합계"
FROM 노선별수송
WHERE 구분 = '승차'
  AND 노선명 NOT IN ('ITX-청춘','ITX-마음','ITX-새마을','무궁화')
  AND m03 IS NOT NULL
GROUP BY 노선명
HAVING "1분기합계" > 0
ORDER BY "1분기합계" DESC
"""

try:
    df02 = run_query(SQL_02).drop_duplicates(subset=["노선명"]).reset_index(drop=True)
    df02["색상"] = df02["노선명"].apply(
        lambda x: "#f85149" if x in ["경의선","중앙선"] else "#30363d")
    df02["라벨"] = df02["노선명"].apply(
        lambda x: f"⚡ {x}" if x in ["경의선","중앙선"] else x)

    fig02 = px.bar(df02, x="1분기합계", y="라벨", orientation="h",
                   text="1분기합계", color="색상", color_discrete_map="identity",
                   labels={"1분기합계": "1분기 총 승차 인원 (명)", "라벨": ""})
    fig02.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig02.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", showlegend=False, height=480,
        yaxis=dict(autorange="reversed", gridcolor="#21262d"),
        xaxis=dict(gridcolor="#21262d"),
        margin=dict(l=0, r=100, t=20, b=20),
    )
    st.plotly_chart(fig02, use_container_width=True)

    col_s2, col_i2 = st.columns([1, 1])
    with col_s2:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_02.strip()}</div>', unsafe_allow_html=True)
    with col_i2:
        총합 = int(df02[df02["노선명"].isin(["경의선","중앙선"])]["1분기합계"].sum())
        경의순위 = int(df02[df02["노선명"]=="경의선"].index[0]) + 1 if "경의선" in df02["노선명"].values else "-"
        중앙순위 = int(df02[df02["노선명"]=="중앙선"].index[0]) + 1 if "중앙선" in df02["노선명"].values else "-"
        st.markdown(f"""
        <div class="insight-box">
        💡 <strong>인사이트</strong><br><br>
        경의선은 전체 광역철도 노선 중 <strong>{경의순위}위</strong>,
        중앙선은 <strong>{중앙순위}위</strong>의 수송 규모입니다.<br><br>
        경의중앙선 합산 1분기 승차 인원은 <strong>{총합:,}명</strong>으로
        적지 않은 수요를 보유하고 있습니다.<br><br>
        그럼에도 배차 간격이 긴 것은 <strong>수요 대비 공급 부족</strong>의
        구조적 문제로, 통근자들의 일상적 불편으로 직결됩니다.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📊 전체 노선 수송량 데이터 보기"):
        st.dataframe(df02[["노선명","1월","2월","3월","1분기합계"]].style.format(
            {"1월":"{:,}","2월":"{:,}","3월":"{:,}","1분기합계":"{:,}"}),
            use_container_width=True)
except Exception as e:
    st.error(f"차트 ② 오류: {e}")

# ═══════════════════════════════════════════════
# 차트 ③  역별 이용량 랭킹
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
    <span class="section-number">03</span>
    <span class="section-title">역별 이용량 랭킹 — 어느 역이 가장 붐비는가?</span>
</div>
""", unsafe_allow_html=True)

SQL_03 = f"""
SELECT
    노선명, 역명,
    SUM(total)                                          AS 총이용객,
    SUM(t07) + SUM(t08) + SUM(t09)                     AS 아침피크,
    SUM(t17) + SUM(t18) + SUM(t19)                     AS 저녁피크,
    ROUND(
        (SUM(t07)+SUM(t08)+SUM(t09)+SUM(t17)+SUM(t18)+SUM(t19))
        * 100.0 / NULLIF(SUM(total), 0), 1
    )                                                   AS 피크집중도
FROM 시간대별승하차
WHERE 노선명 {line_filter} AND 월 = {selected_month} AND 구분 = '승차'
GROUP BY 노선명, 역명
ORDER BY 총이용객 DESC
"""

try:
    df03 = run_query(SQL_03)
    top_n = st.slider("상위 몇 개 역 표시?", 5, len(df03), min(20, len(df03)), 5)
    df03_top = df03.head(top_n)

    fig03 = px.bar(
        df03_top, x="총이용객", y="역명", orientation="h",
        color="피크집중도", color_continuous_scale=["#1f6feb","#e3b341","#f85149"],
        text="총이용객",
        hover_data={"노선명":True,"아침피크":True,"저녁피크":True,"피크집중도":True},
        labels={"총이용객":"총 승차 인원 (명)","역명":"","피크집중도":"피크 집중도(%)"},
    )
    fig03.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig03.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e6edf3", height=max(400, top_n * 28),
        yaxis=dict(autorange="reversed", gridcolor="#21262d"),
        xaxis=dict(gridcolor="#21262d"),
        coloraxis_colorbar=dict(title="피크<br>집중도(%)", tickfont=dict(color="#8b949e")),
        margin=dict(l=0, r=80, t=20, b=20),
    )
    st.plotly_chart(fig03, use_container_width=True)

    col_s3, col_i3 = st.columns([1, 1])
    with col_s3:
        st.markdown("**🗄️ 사용 SQL**")
        st.markdown(f'<div class="sql-box">{SQL_03.strip()}</div>', unsafe_allow_html=True)
    with col_i3:
        top1 = df03.iloc[0]
        high_peak = df03.nlargest(1, "피크집중도").iloc[0]
        st.markdown(f"""
        <div class="insight-box">
        💡 <strong>인사이트</strong><br><br>
        {selected_month}월 가장 많은 승객이 이용한 역은
        <strong>{top1['역명']}</strong>으로 총 <strong>{int(top1['총이용객']):,}명</strong>이
        승차했습니다.<br><br>
        피크 집중도가 가장 높은 역은 <strong>{high_peak['역명']}</strong>
        (<strong>{high_peak['피크집중도']:.1f}%</strong>)으로,
        출퇴근 6시간에 이용량이 집중되어 있습니다.<br><br>
        이런 역들을 중심으로 <strong>출퇴근 시간대 증편</strong>이
        가장 시급합니다.
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📊 전체 역 상세 데이터 보기"):
        st.dataframe(df03.style.format({
            "총이용객":"{:,}","아침피크":"{:,}","저녁피크":"{:,}","피크집중도":"{:.1f}%"}),
            use_container_width=True)
except Exception as e:
    st.error(f"차트 ③ 오류: {e}")

# ───────────────────────────────────────────────
# 푸터
# ───────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#484f58; font-size:0.78rem; padding:1rem;
            border-top:1px solid #21262d;">
    🚆 경의중앙선 배차 불균형 분석 대시보드 &nbsp;|&nbsp;
    데이터: 코레일 광역철도 시간대별 승하차인원 2026년 1~3월 &nbsp;|&nbsp;
    분석: 수요 대비 공급 부족의 구조적 문제
</div>
""", unsafe_allow_html=True)
