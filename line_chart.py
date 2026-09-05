import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 1. Đọc và làm sạch dữ liệu giao dịch
df_trans = pd.read_csv("data_trans/All_Transactions_Merged.csv")
df_trans["Ngày khớp lệnh"] = pd.to_datetime(df_trans["Ngày khớp lệnh"])
df_trans["Khối lượng khớp lệnh"] = df_trans["Khối lượng khớp lệnh"].astype(float)

for col in ["NAV/CQQ khớp lệnh", "Giá trị khớp lệnh", "Vốn đầu tư"]:
    df_trans[col] = (
        df_trans[col]
        .astype(str)
        .str.replace(" VN₫", "")
        .str.replace(",", "")
        .astype(float)
    )

# 2. Đọc dữ liệu lịch sử NAV
df_nav = pd.read_csv("nav_history_all.csv")
df_nav["navDate"] = pd.to_datetime(df_nav["navDate"])

# Lọc NAV từ ngày giao dịch đầu tiên
min_date = df_trans["Ngày khớp lệnh"].min()
df_nav_filtered = df_nav[df_nav["navDate"] >= min_date]

# 3. Tính toán Vốn và Giá trị tài sản theo từng ngày
dates = sorted(df_nav_filtered["navDate"].unique())
portfolio_records = []

for d in dates:
    trans_till_d = df_trans[df_trans["Ngày khớp lệnh"] <= d]
    total_von = trans_till_d["Vốn đầu tư"].sum()

    total_value = 0.0
    for fund in df_trans["Mã CCQ"].unique():
        fund_trans = trans_till_d[trans_till_d["Mã CCQ"] == fund]
        total_units = fund_trans["Khối lượng khớp lệnh"].sum()

        if total_units > 0:
            nav_latest = (
                df_nav[(df_nav["code"] == fund) & (df_nav["navDate"] <= d)]
                .sort_values("navDate")
                .iloc[-1]["nav"]
            )
            total_value += total_units * nav_latest

    portfolio_records.append(
        {
            "Date": d,
            "Von": total_von,
            "GiaTri": total_value,
            "LoiNhuan": total_value - total_von,
        }
    )

df_chart = pd.DataFrame(portfolio_records)
df_chart["TiLeLoiNhuan"] = (df_chart["LoiNhuan"] / df_chart["Von"]) * 100

# 4. Tính toán các giá trị Max/Min để giới hạn mây chuẩn tuyệt đối
y_upper = np.maximum(df_chart["GiaTri"], df_chart["Von"])  # Đường biên trên
y_lower = np.minimum(df_chart["GiaTri"], df_chart["Von"])  # Đường biên dưới

# 5. Vẽ biểu đồ Plotly
fig = go.Figure()

# -------------------------------------------------------------
# DẢI MÂY XANH (LÃI): Vẽ đường Vốn trước -> Fill lên Biên Trên
# -------------------------------------------------------------
fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["Von"],
        mode="lines",
        line=dict(color="gray", width=2.25),
        name="Vốn đầu tư",
        showlegend=True,
        hoverinfo="skip",
    )
)

fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=y_upper,
        mode="lines",
        line=dict(width=0),  # Ẩn đường viền phụ
        fill="tonexty",  # Tô màu từ đường Vốn lên y_upper
        fillcolor="rgba(46, 204, 113, 0.25)",  # Mây Xanh
        name="Mây Lãi",
        showlegend=False,
        hoverinfo="skip",
    )
)

# -------------------------------------------------------------
# DẢI MÂY ĐỎ (LỖ): Vẽ đường Vốn trước -> Fill xuống Biên Dưới
# -------------------------------------------------------------
fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["Von"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    )
)

fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=y_lower,
        mode="lines",
        line=dict(width=0),  # Ẩn đường viền phụ
        fill="tonexty",  # Tô màu từ đường Vốn xuống y_lower
        fillcolor="rgba(231, 76, 60, 0.25)",  # Mây Đỏ
        name="Mây Lỗ",
        showlegend=False,
        hoverinfo="skip",
    )
)

# -------------------------------------------------------------
# ĐƯỜNG GIÁ TRỊ TÀI SẢN THỰC TẾ & TRACE HOVER
# -------------------------------------------------------------
fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["GiaTri"],
        mode="lines",
        line=dict(color="#1f77b4", width=2.25),  # Đường Giá trị tài sản
        name="Giá trị tài sản",
        customdata=df_chart[["Von", "LoiNhuan", "TiLeLoiNhuan"]],
        hovertemplate=(
            "<b>Ngày:</b> %{x|%d/%m/%Y}<br>"
            + "<b>Vốn đầu tư:</b> %{customdata[0]:,.0f} VN₫<br>"
            + "<b>Giá trị tài sản:</b> %{y:,.0f} VN₫<br>"
            + "<b>Lợi nhuận:</b> %{customdata[1]:+,.0f} VN₫<br>"
            + "<b>Tỉ lệ lợi nhuận:</b> %{customdata[2]:+.2f}%<extra></extra>"
        )
    )
)

# Tinh chỉnh giao diện
fig.update_layout(
    title="Biểu đồ Tổng Giá trị Tài sản vs Vốn Đầu tư",
    xaxis_title="Ngày",
    yaxis_title="Số tiền (VN₫)",
    hovermode="x unified",
    template="plotly_white",
)

fig.show()