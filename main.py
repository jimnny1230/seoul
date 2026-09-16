import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 한글 폰트 설정
# (Streamlit Cloud에서 한글이 깨지지 않으려면 packages.txt에
#  fonts-nanum 을 함께 추가해야 합니다 — 안내 참고)
# ---------------------------------------------------------
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title="서울 100년 기온 변화", page_icon="🌡️", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year
    return df


df = load_data()

st.title("🌡️ 서울, 100년의 기온 변화")
st.write(
    "서울 관측소의 일별 기온 기록을 바탕으로, 지난 100여 년 동안 "
    "연평균 기온이 어떻게 변해왔는지 한눈에 살펴봅니다."
)

# 연도별 평균 계산 (관측 일수가 적은 첫 해/마지막 해는 제외)
yearly = (
    df.groupby("연도")
    .agg(평균기온=("평균기온", "mean"), 관측일수=("평균기온", "count"))
    .reset_index()
)
yearly_full = yearly[yearly["관측일수"] >= 300].reset_index(drop=True)

min_year = int(yearly_full["연도"].min())
max_year = int(yearly_full["연도"].max())

st.sidebar.header("⚙️ 설정")
year_range = st.sidebar.slider(
    "살펴볼 연도 범위",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)
show_trend = st.sidebar.checkbox("추세선 표시", value=True)

filtered = yearly_full[
    (yearly_full["연도"] >= year_range[0]) & (yearly_full["연도"] <= year_range[1])
].reset_index(drop=True)

# ---------------------------------------------------------
# 그래프
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 5.5))
ax.plot(
    filtered["연도"],
    filtered["평균기온"],
    color="#1f77b4",
    linewidth=1.5,
    marker="o",
    markersize=3,
    label="연평균 기온",
)

if show_trend and len(filtered) > 1:
    coef = np.polyfit(filtered["연도"], filtered["평균기온"], 1)
    trend_line = np.poly1d(coef)
    ax.plot(
        filtered["연도"],
        trend_line(filtered["연도"]),
        color="#d62728",
        linestyle="--",
        linewidth=2,
        label=f"추세선 (10년당 {coef[0] * 10:+.2f}℃)",
    )

ax.set_title("서울 연평균 기온 변화", fontsize=16, pad=12)
ax.set_xlabel("연도")
ax.set_ylabel("연평균 기온 (℃)")
ax.grid(alpha=0.3)
ax.legend()

st.pyplot(fig)

# ---------------------------------------------------------
# 요약 정보
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("선택한 기간", f"{year_range[0]} ~ {year_range[1]}년")

max_row = filtered.loc[filtered["평균기온"].idxmax()]
min_row = filtered.loc[filtered["평균기온"].idxmin()]

col2.metric(
    "가장 더웠던 해",
    f"{max_row['평균기온']:.1f} ℃",
    f"{int(max_row['연도'])}년",
)
col3.metric(
    "가장 추웠던 해",
    f"{min_row['평균기온']:.1f} ℃",
    f"{int(min_row['연도'])}년",
)

with st.expander("📋 연도별 데이터 보기"):
    st.dataframe(
        filtered[["연도", "평균기온"]]
        .rename(columns={"평균기온": "연평균 기온(℃)"})
        .round(2)
        .set_index("연도")
    )

st.caption("데이터 출처: 서울 관측소(지점번호 108) 일별 기온 자료")
