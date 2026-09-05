import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# 1. ĐỌC VÀ XỬ LÝ DỮ LIỆU CỦA BIỂU ĐỒ 1 (CCQ & TOTAL)
# ==============================================================================
df_total_asset = pd.read_csv("total_asset.csv")


def clean_num(val):
  if pd.isna(val):
    return 0.0
  return float(
      str(val)
      .replace(" VN₫", "")
      .replace("%", "")
      .replace(",", "")
      .replace("+", "")
      .strip()
  )


df_total_asset["Von"] = df_total_asset["Tổng vốn đầu tư"].apply(clean_num)
df_total_asset["GiaTri"] = df_total_asset["Giá trị tài sản hiện tại"].apply(
    clean_num
)
df_total_asset["LoiNhuan"] = df_total_asset["Lợi nhuận (VNĐ)"].apply(clean_num)
df_total_asset["TiLe"] = df_total_asset["Tỷ lệ lợi nhuận (%)"].apply(clean_num)

df_ccq = df_total_asset[df_total_asset["Mã CCQ"] != "TỔNG CỘNG"].copy()
df_sum = df_total_asset[df_total_asset["Mã CCQ"] == "TỔNG CỘNG"].copy()
df_plot = pd.concat([df_ccq, df_sum], ignore_index=True)

# ==============================================================================
# 2. ĐỌC VÀ XỬ LÝ DỮ LIỆU CỦA BIỂU ĐỒ 2 (LỊCH SỬ BIẾN ĐỘNG NAV/TÀI SẢN)
# ==============================================================================
df_trans = pd.read_csv("data_trans/All_Transactions_Merged.csv")
df_trans["Ngày khớp lệnh"] = pd.to_datetime(df_trans["Ngày khớp lệnh"])
df_trans["Khối lượng khớp lệnh"] = df_trans["Khối lượng khớp lệnh"].astype(
    float
)

for col in ["NAV/CQQ khớp lệnh", "Giá trị khớp lệnh", "Vốn đầu tư"]:
  df_trans[col] = (
      df_trans[col]
      .astype(str)
      .str.replace(" VN₫", "")
      .str.replace(",", "")
      .astype(float)
  )

df_nav = pd.read_csv("nav_history_all.csv")
df_nav["navDate"] = pd.to_datetime(df_nav["navDate"])

min_date = df_trans["Ngày khớp lệnh"].min()
df_nav_filtered = df_nav[df_nav["navDate"] >= min_date]

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

  portfolio_records.append({
      "Date": d,
      "Von": total_von,
      "GiaTri": total_value,
      "LoiNhuan": total_value - total_von,
  })

df_chart = pd.DataFrame(portfolio_records)
df_chart["TiLeLoiNhuan"] = (df_chart["LoiNhuan"] / df_chart["Von"]) * 100

y_upper = np.maximum(df_chart["GiaTri"], df_chart["Von"])
y_lower = np.minimum(df_chart["GiaTri"], df_chart["Von"])

# TẠO HOVERTEXT HTML TÙY CHỈNH CHO LINE CHART (ĐỔI MÀU LÃI/LỖ & TỈ LỆ)
hover_texts_line = []
for idx, row in df_chart.iterrows():
  color = "#2ecc71" if row["LoiNhuan"] >= 0 else "#e74c3c"
  ht = (
      f"<b>Ngày:</b> {row['Date'].strftime('%d/%m/%Y')}<br>"
      f"<b>Vốn:</b> {row['Von']:,.0f} VN₫<br>"
      f"<b>Giá trị:</b> {row['GiaTri']:,.0f} VN₫<br>"
      f"<b>Lãi/Lỗ:</b> <span style='color:{color};"
      f" font-weight:bold;'>{row['LoiNhuan']:+,.0f} VN₫</span><br>"
      f"<b>Tỉ lệ:</b> <span style='color:{color};"
      f" font-weight:bold;'>{row['TiLeLoiNhuan']:+.2f}%</span>"
  )
  hover_texts_line.append(ht)

# ==============================================================================
# 3. TẠO TỔNG THỂ DASHBOARD (3 HÀNG)
# ==============================================================================
fig = make_subplots(
    rows=3,
    cols=2,
    specs=[
        [{"colspan": 2, "type": "xy"}, None],
        [{"colspan": 2, "type": "xy"}, None],
        [{"type": "domain"}, {"type": "domain"}],
    ],
    subplot_titles=(
        "<b>1. Diễn biến Lịch sử Vốn vs Giá trị Tài sản</b>",
        "<b>2. So sánh Vốn, Giá trị & Lãi/Lỗ theo Mã CCQ Hiện tại</b>",
        "<b>3. Tỷ trọng Vốn đầu tư</b>",
        "<b>4. Tỷ trọng Giá trị tài sản</b>",
    ),
    vertical_spacing=0.08,
)

# -------------------------------------------------------------
# HÀNG 1: LINE CHART (BIẾN ĐỘNG THEO THỜI GIAN)
# -------------------------------------------------------------
fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["Von"],
        mode="lines",
        line=dict(color="gray", width=2),
        name="Vốn đầu tư (Lịch sử)",
        legendgroup="history",
        hoverinfo="skip"
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=y_upper,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(46, 204, 113, 0.25)",
        showlegend=False,
        hoverinfo="skip",
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["Von"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=y_lower,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(231, 76, 60, 0.25)",
        showlegend=False,
        hoverinfo="skip",
    ),
    row=1,
    col=1,
)

# Đường Giá trị với Hovertext tùy chỉnh
fig.add_trace(
    go.Scatter(
        x=df_chart["Date"],
        y=df_chart["GiaTri"],
        mode="lines",
        line=dict(color="#1f77b4", width=2.25),
        name="Giá trị tài sản (Lịch sử)",
        legendgroup="history",
        text=hover_texts_line,
        hoverinfo="text",  # Hiển thị chính xác chuỗi HTML đã định dạng
    ),
    row=1,
    col=1,
)

# -------------------------------------------------------------
# HÀNG 2: COLUMN CHART (CỘT HIỆN TẠI)
# -------------------------------------------------------------
fig.add_trace(
    go.Bar(
        x=df_plot["Mã CCQ"],
        y=df_plot["Von"],
        name="Vốn đầu tư",
        marker_color="#7f7f7f",
        text=[f"{v:,.0f} VN₫" for v in df_plot["Von"]],
        textposition="outside",
        legendgroup="current",
        hovertemplate="%{x} - Vốn: %{y:,.0f} VN₫<extra></extra>",
    ),
    row=2,
    col=1,
)

fig.add_trace(
    go.Bar(
        x=df_plot["Mã CCQ"],
        y=df_plot["GiaTri"],
        name="Giá trị hiện tại",
        marker_color="#1f77b4",
        text=[f"{v:,.0f} VN₫" for v in df_plot["GiaTri"]],
        textposition="outside",
        legendgroup="current",
        hovertemplate="%{x} - Giá trị: %{y:,.0f} VN₫<extra></extra>",
    ),
    row=2,
    col=1,
)

fig.add_trace(
    go.Bar(
        x=df_plot["Mã CCQ"],
        y=df_plot["LoiNhuan"],
        name="Lợi nhuận",
        marker_color=[
            "#2ecc71" if v >= 0 else "#e74c3c" for v in df_plot["LoiNhuan"]
        ],
        text=[
            f"{v:+,.0f} VN₫<br>({t:+.2f}%)"
            for v, t in zip(df_plot["LoiNhuan"], df_plot["TiLe"])
        ],
        textposition="outside",
        legendgroup="current",
        customdata=df_plot["TiLe"],
        hovertemplate=(
            "%{x}<br>Lãi/Lỗ: %{y:+,.0f} VN₫<br>Tỷ lệ:"
            " %{customdata:+.2f}%<extra></extra>"
        ),
    ),
    row=2,
    col=1,
)

# -------------------------------------------------------------
# HÀNG 3: PIE CHARTS (TỶ TRỌNG)
# -------------------------------------------------------------
fig.add_trace(
    go.Pie(
        labels=df_ccq["Mã CCQ"],
        values=df_ccq["Von"],
        textinfo="label+percent",
        hovertemplate=(
            "%{label}<br>Vốn: %{value:,.0f} VN₫<br>Tỷ trọng:"
            " %{percent}<extra></extra>"
        ),
        hole=0.4,
    ),
    row=3,
    col=1,
)

fig.add_trace(
    go.Pie(
        labels=df_ccq["Mã CCQ"],
        values=df_ccq["GiaTri"],
        textinfo="label+percent",
        hovertemplate=(
            "%{label}<br>Giá trị: %{value:,.0f} VN₫<br>Tỷ trọng:"
            " %{percent}<extra></extra>"
        ),
        hole=0.4,
    ),
    row=3,
    col=2,
)

# ==============================================================================
# 4. CẤU HÌNH GIAO DIỆN TỔNG THỂ & ĐỊNH DẠNG KHUNG HOVER RÕ RÀNG
# ==============================================================================
fig.update_layout(
    title="<b>BÁO CÁO TOÀN DIỆN DANH MỤC ĐẦU TƯ CCQ</b>",
    template="plotly_white",
    height=1200,
    barmode="group",
    bargap=0.35,
    bargroupgap=0.1,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1
    ),
    # Cấu hình khung nền chữ khi rê chuột (Trắng, chữ xám đen, viền xám nhẹ)
    hoverlabel=dict(
        bgcolor="white",
        font_color="#2c3e50",
        font_size=13,
        font_family="Arial",
        bordercolor="#bdc3c7",
    ),
)

fig.update_yaxes(title_text="Số tiền (VN₫)", row=1, col=1)
fig.update_yaxes(title_text="Số tiền (VN₫)", row=2, col=1)
fig.update_xaxes(title_text="Thời gian", row=1, col=1)
fig.update_xaxes(title_text="Mã CCQ / Tổng danh mục", row=2, col=1)

# fig.show()

fig.write_html("reports/overall_chart.html")