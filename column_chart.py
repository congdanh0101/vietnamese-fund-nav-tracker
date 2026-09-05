import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Đọc và làm sạch dữ liệu
df = pd.read_csv("total_asset.csv")


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


df["Von"] = df["Tổng vốn đầu tư"].apply(clean_num)
df["GiaTri"] = df["Giá trị tài sản hiện tại"].apply(clean_num)
df["LoiNhuan"] = df["Lợi nhuận (VNĐ)"].apply(clean_num)
df["TiLe"] = df["Tỷ lệ lợi nhuận (%)"].apply(clean_num)

# Tách dữ liệu từng CCQ (cho Pie Chart) và toàn bộ (cho Column Chart)
df_ccq = df[df["Mã CCQ"] != "TỔNG CỘNG"].copy()
df_total = df[df["Mã CCQ"] == "TỔNG CỘNG"].copy()
df_plot = pd.concat([df_ccq, df_total], ignore_index=True)

# 2. Tạo Subplots (2 Hàng): Hàng 1 chứa Column Chart, Hàng 2 chứa 2 Pie Charts
fig = make_subplots(
    rows=2,
    cols=2,
    specs=[
        [{"colspan": 2, "type": "xy"}, None],  # Hàng 1 gộp 2 cột
        [{"type": "domain"}, {"type": "domain"}],  # Hàng 2 chia làm 2 hình tròn
    ],
    subplot_titles=(
        "<b>1. So sánh Vốn, Giá trị & Lãi/Lỗ theo Mã CCQ</b>",
        "<b>2. Tỷ trọng Vốn đầu tư</b>",
        "<b>3. Tỷ trọng Giá trị tài sản hiện tại</b>",
    ),
    vertical_spacing=0.15,
)

# --- HÀNG 1: BIỂU ĐỒ CỘT (COLUMN CHART) ---
# Vốn
fig.add_trace(
    go.Bar(
        x=df_plot["Mã CCQ"],
        y=df_plot["Von"],
        name="Vốn đầu tư",
        marker_color="#7f7f7f",
        text=[f"{v:,.0f} VN₫" for v in df_plot["Von"]],
        textposition="outside",
        hovertemplate="%{x} - Vốn: %{y:,.0f} VN₫<extra></extra>",
    ),
    row=1,
    col=1,
)

# Giá trị hiện tại
fig.add_trace(
    go.Bar(
        x=df_plot["Mã CCQ"],
        y=df_plot["GiaTri"],
        name="Giá trị hiện tại",
        marker_color="#1f77b4",
        text=[f"{v:,.0f} VN₫" for v in df_plot["GiaTri"]],
        textposition="outside",
        hovertemplate="%{x} - Giá trị: %{y:,.0f} VN₫<extra></extra>",
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Bar(
        x=df["Mã CCQ"],
        y=df["LoiNhuan"],
        name="Lợi nhuận (VN₫)",
        marker_color=["#2ecc71" if v >= 0 else "#e74c3c" for v in df["LoiNhuan"]],
        text=[
            f"{v:+,.0f} VN₫<br>({t:+.2f}%)"
            for v, t in zip(df["LoiNhuan"], df["TiLe"])
        ],
        textposition="outside",
        hovertemplate=(
            "%{x}<br>Lãi/Lỗ: %{y:+,.0f} VN₫<br>Tỷ lệ:"
            " %{customdata:+.2f}%<extra></extra>"
        ),
        customdata=df["TiLe"],
    )
)

# --- HÀNG 2: 2 BIỂU ĐỒ TRÒN (PIE CHARTS) ---
# Pie 1: Tỷ trọng Vốn
fig.add_trace(
    go.Pie(
        labels=df_ccq["Mã CCQ"],
        values=df_ccq["Von"],
        textinfo="label+percent",
        hovertemplate=(
            "%{label}<br>Vốn: %{value:,.0f} VN₫<br>Tỷ trọng:"
            " %{percent}<extra></extra>"
        ),
        hole=0.4,  # Tạo lỗ ở giữa dạng Donut chart
    ),
    row=2,
    col=1,
)

# Pie 2: Tỷ trọng Giá trị hiện tại
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
    row=2,
    col=2,
)

# 3. Cấu hình giao diện tổng thể
fig.update_layout(
    title="<b>BÁO CÁO PHÂN TÍCH VÀ PHÂN BỔ TÀI SẢN DANH MỤC CCQ</b>",
    barmode="group",
    bargap=0.35,
    bargroupgap=0.1,
    template="plotly_white",
    height=850,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),
)

fig.update_yaxes(title_text="Số tiền (VN₫)", row=1, col=1)

fig.show()