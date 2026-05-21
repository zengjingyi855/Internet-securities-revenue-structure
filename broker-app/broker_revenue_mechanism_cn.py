# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="互联网证券收入机制演示器",
    layout="wide"
)

# ============================================================
# Low-saturation red theme
# ============================================================
FONT_FAMILY = '"Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC", Arial, sans-serif'

st.markdown(
    f"""
    <style>
    :root {{
        --bg-main: #F7F2EF;
        --bg-panel: #FFFFFF;
        --bg-soft: #EFE6E0;
        --text-main: #222222;
        --text-muted: #646464;
        --line-soft: #DDD0C8;
        --red-main: #8F4A45;
        --red-dark: #6E3935;
        --red-soft: #C9A39B;
        --red-light: #E7D4CE;
        --shadow: rgba(90, 54, 49, 0.10);
    }}

    html, body, [class*="css"], .stApp {{
        font-family: {FONT_FAMILY};
    }}

    .stApp {{
        background: var(--bg-main);
        color: var(--text-main);
    }}

    h1, h2, h3, h4, p, div, span, label {{
        font-family: {FONT_FAMILY};
    }}

    .block-container {{
        padding-top: 2.1rem;
        padding-bottom: 2.5rem;
        max-width: 1260px;
    }}

    .top-band {{
        background: linear-gradient(135deg, #FFFFFF 0%, #F1E5DF 100%);
        border: 1px solid var(--line-soft);
        border-left: 8px solid var(--red-main);
        border-radius: 22px;
        padding: 1.35rem 1.55rem;
        box-shadow: 0 12px 30px var(--shadow);
        margin-bottom: 1.25rem;
    }}

    .main-title {{
        font-size: 2.15rem;
        font-weight: 760;
        color: var(--text-main);
        line-height: 1.18;
        margin-bottom: 0.55rem;
    }}

    .subtitle {{
        font-size: 1.02rem;
        color: var(--text-muted);
        line-height: 1.75;
        max-width: 1050px;
    }}

    .section-label {{
        font-size: 0.82rem;
        font-weight: 760;
        letter-spacing: 0.10em;
        color: var(--red-dark);
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }}

    .panel {{
        background: var(--bg-panel);
        border: 1px solid var(--line-soft);
        border-radius: 20px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 10px 24px var(--shadow);
        min-height: 100%;
    }}

    .metric-card {{
        background: var(--bg-panel);
        border: 1px solid var(--line-soft);
        border-top: 6px solid var(--red-main);
        border-radius: 18px;
        padding: 1.05rem 1.15rem;
        box-shadow: 0 10px 24px var(--shadow);
        min-height: 138px;
    }}

    .metric-name {{
        font-size: 0.86rem;
        color: var(--text-muted);
        font-weight: 680;
        margin-bottom: 0.4rem;
    }}

    .metric-value {{
        font-size: 1.9rem;
        font-weight: 780;
        color: var(--text-main);
        margin-bottom: 0.25rem;
        line-height: 1.15;
    }}

    .metric-note {{
        font-size: 0.9rem;
        color: var(--text-muted);
        line-height: 1.5;
    }}

    .callout {{
        background: #F0E4DF;
        border: 1px solid #D8C3BB;
        border-left: 6px solid var(--red-main);
        border-radius: 16px;
        padding: 0.95rem 1.1rem;
        color: var(--text-main);
        line-height: 1.7;
        box-shadow: 0 8px 18px rgba(90, 54, 49, 0.06);
    }}

    .callout strong {{
        color: var(--red-dark);
    }}

    .small-note {{
        font-size: 0.88rem;
        color: var(--text-muted);
        line-height: 1.65;
    }}

    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label {{
        color: var(--text-main);
        font-weight: 700;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--text-main);
    }}

    hr {{
        border: none;
        height: 1px;
        background: var(--line-soft);
        margin: 1.1rem 0;
    }}

    .stDataFrame {{
        border-radius: 16px;
        overflow: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Teaching assumptions
# These are intentionally dimensionless weights, not company data.
# ============================================================
MECHANISM_ASSUMPTIONS = {
    "传统券商模式": {
        "description": "收入主要依赖显性交易佣金。交易次数越多，佣金型收入占比越高；资产留存和交易变现的作用相对较弱。",
        "commission_weight": 8.0,
        "transaction_monetization_weight": 0.2,
        "asset_retention_weight": 0.6,
        "advisory_fee_weight": 0.0,
    },
    "零佣金互联网券商模式": {
        "description": "显性佣金被压低甚至归零，但平台通过交易变现、资产留存和利息类收入重构收入来源。",
        "commission_weight": 0.0,
        "transaction_monetization_weight": 1.8,
        "asset_retention_weight": 1.4,
        "advisory_fee_weight": 0.0,
    },
    "智能投顾模式": {
        "description": "收入不再主要依赖交易频率，而是更依赖账户资产规模和持续性的资产管理服务。",
        "commission_weight": 0.0,
        "transaction_monetization_weight": 0.0,
        "asset_retention_weight": 0.2,
        "advisory_fee_weight": 1.6,
    },
}

REVENUE_COLORS = {
    "显性佣金": "#9A5A55",
    "交易变现": "#B9867E",
    "资产留存与息差": "#7D5A55",
    "资产管理服务": "#C6A49D",
}

PLOTLY_FONT = "Microsoft YaHei, SimHei, Noto Sans CJK SC, Source Han Sans SC, Arial, sans-serif"

# ============================================================
# Calculation functions
# ============================================================
def calculate_mechanism_scores(model_name: str, account_scale: int, monthly_trades: int) -> pd.DataFrame:
    """
    This function generates illustrative mechanism scores.
    The scores are not real revenue estimates and do not represent any broker's actual income.
    """

    assumptions = MECHANISM_ASSUMPTIONS[model_name]

    # Normalize the account input so it works as a scale factor rather than a currency estimate.
    account_factor = account_scale / 10_000

    commission_score = monthly_trades * assumptions["commission_weight"]
    transaction_monetization_score = monthly_trades * assumptions["transaction_monetization_weight"]
    asset_retention_score = account_factor * 10 * assumptions["asset_retention_weight"]
    advisory_fee_score = account_factor * 10 * assumptions["advisory_fee_weight"]

    df = pd.DataFrame(
        {
            "收入来源": [
                "显性佣金",
                "交易变现",
                "资产留存与息差",
                "资产管理服务",
            ],
            "收入结构指数": [
                commission_score,
                transaction_monetization_score,
                asset_retention_score,
                advisory_fee_score,
            ],
        }
    )

    total_score = df["收入结构指数"].sum()
    if total_score > 0:
        df["结构占比"] = df["收入结构指数"] / total_score
    else:
        df["结构占比"] = 0

    return df


def calculate_all_models(account_scale: int, monthly_trades: int) -> pd.DataFrame:
    rows = []
    for model_name in MECHANISM_ASSUMPTIONS:
        df = calculate_mechanism_scores(model_name, account_scale, monthly_trades)
        rows.append(
            {
                "商业模式": model_name,
                "综合收入结构指数": df["收入结构指数"].sum(),
                "显性佣金": df.loc[df["收入来源"] == "显性佣金", "结构占比"].iloc[0],
                "交易变现": df.loc[df["收入来源"] == "交易变现", "结构占比"].iloc[0],
                "资产留存与息差": df.loc[df["收入来源"] == "资产留存与息差", "结构占比"].iloc[0],
                "资产管理服务": df.loc[df["收入来源"] == "资产管理服务", "结构占比"].iloc[0],
            }
        )
    return pd.DataFrame(rows)


def format_score(value: float) -> str:
    return f"{value:,.1f}"


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


# ============================================================
# Header
# ============================================================
st.markdown(
    """
    <div class="top-band">
        <div class="section-label">Interactive teaching model</div>
        <div class="main-title">互联网证券收入机制演示器</div>
        <div class="subtitle">
            本工具用“收入结构指数”展示不同证券服务模式下，收入来源如何从显性佣金转向交易变现、资产留存与息差、资产管理服务等方向。
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# Inputs and key message
# ============================================================
left_col, right_col = st.columns([0.92, 1.08], gap="large")

with left_col:
    st.markdown('<div class="section-label">参数设置</div>', unsafe_allow_html=True)

    selected_model = st.selectbox(
        "选择证券服务模式",
        list(MECHANISM_ASSUMPTIONS.keys()),
        index=1
    )

    account_scale = st.slider(
        "账户资产规模情景",
        min_value=1_000,
        max_value=100_000,
        value=10_000,
        step=1_000,
        help="该输入仅用于控制资产规模情景，不代表真实客户数据。"
    )

    monthly_trades = st.slider(
        "月均交易次数情景",
        min_value=1,
        max_value=50,
        value=5,
        step=1,
        help="该输入仅用于控制交易活跃度情景，不代表真实客户数据。"
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**当前模式逻辑**")
    st.write(MECHANISM_ASSUMPTIONS[selected_model]["description"])

    st.markdown(
        """
        <div class="small-note">
        注：“交易变现”是对订单流变现、交易相关返佣、流量导流等交易活动货币化机制的简化代理变量。
        </div>
        """,
        unsafe_allow_html=True
    )

with right_col:
    score_df = calculate_mechanism_scores(selected_model, account_scale, monthly_trades)
    total_score = score_df["收入结构指数"].sum()
    largest_item = score_df.sort_values("收入结构指数", ascending=False).iloc[0]

    metric_col_1, metric_col_2 = st.columns(2, gap="medium")

    with metric_col_1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-name">综合收入结构指数</div>
                <div class="metric-value">{format_score(total_score)}</div>
                <div class="metric-note">该数值是机制演示指数，不是美元收入，也不是财务预测。</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col_2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-name">主导收入来源</div>
                <div class="metric-value">{largest_item["收入来源"]}</div>
                <div class="metric-note">该来源在当前情景下占比 {format_percent(largest_item["结构占比"])}。</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="callout">
        <strong>解释：</strong>
        零佣金并不意味着证券平台收入消失，而是意味着收入从显性的交易佣金，
        转向更隐性的交易变现、资产留存与息差收入。智能投顾模式则进一步把收入重心转向资产规模和持续服务。
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# Chart
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">收入结构拆解</div>', unsafe_allow_html=True)

chart_df = score_df.sort_values("收入结构指数", ascending=True).copy()
chart_df["颜色"] = chart_df["收入来源"].map(REVENUE_COLORS)

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_df["收入结构指数"],
        y=chart_df["收入来源"],
        orientation="h",
        text=[format_score(v) for v in chart_df["收入结构指数"]],
        textposition="outside",
        marker=dict(
            color=chart_df["颜色"],
            line=dict(color="rgba(80, 50, 45, 0.22)", width=1)
        ),
        hovertemplate="<b>%{y}</b><br>收入结构指数：%{x:.1f}<extra></extra>",
    )
)

x_max = max(50, chart_df["收入结构指数"].max() * 1.28)

fig.update_layout(
    title=dict(
        text=f"收入结构指数拆解：{selected_model}",
        font=dict(size=21, color="#222222", family=PLOTLY_FONT),
        x=0.01
    ),
    plot_bgcolor="#F7F2EF",
    paper_bgcolor="#F7F2EF",
    height=430,
    margin=dict(l=10, r=75, t=70, b=42),
    xaxis=dict(
        title=dict(
            text="收入结构指数，非真实金额",
            font=dict(color="#4A4A4A", family=PLOTLY_FONT)
        ),
        range=[0, x_max],
        showgrid=True,
        gridcolor="#DDD0C8",
        zeroline=False,
        tickfont=dict(color="#4A4A4A", family=PLOTLY_FONT)
    ),
    yaxis=dict(
        title="",
        tickfont=dict(color="#222222", size=14, family=PLOTLY_FONT)
    ),
    showlegend=False,
    font=dict(family=PLOTLY_FONT, color="#222222")
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Composition table
# ============================================================
st.markdown('<div class="section-label">当前情景输出</div>', unsafe_allow_html=True)

display_df = score_df.copy()
display_df["收入结构指数"] = display_df["收入结构指数"].map(format_score)
display_df["结构占比"] = display_df["结构占比"].map(format_percent)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# Cross-model comparison
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">同一情景下的模式对比</div>', unsafe_allow_html=True)

comparison_df = calculate_all_models(account_scale, monthly_trades)

comparison_display = comparison_df.copy()
comparison_display["综合收入结构指数"] = comparison_display["综合收入结构指数"].map(format_score)

for col in ["显性佣金", "交易变现", "资产留存与息差", "资产管理服务"]:
    comparison_display[col] = comparison_display[col].map(format_percent)

st.dataframe(
    comparison_display,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# Visible assumptions
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">预设教学假设</div>', unsafe_allow_html=True)

assumption_rows = []
for model_name, item in MECHANISM_ASSUMPTIONS.items():
    assumption_rows.append(
        {
            "商业模式": model_name,
            "佣金依赖权重": item["commission_weight"],
            "交易变现权重": item["transaction_monetization_weight"],
            "资产留存权重": item["asset_retention_weight"],
            "资产管理权重": item["advisory_fee_weight"],
        }
    )

st.dataframe(
    pd.DataFrame(assumption_rows),
    use_container_width=True,
    hide_index=True
)

st.markdown(
    """
    <div class="callout">
    <strong>使用说明：</strong>
    上表中的权重不是经验估计值，也不是任何券商披露的真实财务数据。
    本工具的目的，是帮助理解不同互联网证券模式下收入来源的相对变化，而不是计算实际收入。
    </div>
    """,
    unsafe_allow_html=True
)
