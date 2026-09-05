from datetime import datetime
import pandas as pd

def generate_total_asset(tx_file='data_trans/All_Transactions_Merged.csv', nav_file='nav_history_all.csv', output_file='total_asset.csv'):
    # 1. Đọc dữ liệu
    df_tx = pd.read_csv(tx_file)
    df_nav = pd.read_csv(nav_file)

    # 2. Xử lý làm sạch số liệu
    def parse_num(val):
        if pd.isna(val): return 0.0
        s = str(val).replace('VN₫', '').replace('đ', '').strip().replace(',', '')
        return float(s)

    df_tx['Khối lượng'] = df_tx['Khối lượng khớp lệnh'].apply(parse_num)
    df_tx['Vốn'] = df_tx['Vốn đầu tư'].apply(parse_num)

    # 3. Group by Mã CCQ
    total_asset = df_tx.groupby('Mã CCQ').agg(
        total_volume=('Khối lượng', 'sum'),
        total_investment=('Vốn', 'sum')
    ).reset_index()

    # 4. Lấy giá NAV mới nhất từ file lịch sử NAV
    df_nav['navDate'] = pd.to_datetime(df_nav['navDate'])
    latest_nav = df_nav.sort_values('navDate').groupby('code').last().reset_index()

    # 5. Gộp thông tin NAV và tính toán NAV trung bình
    df_merged = pd.merge(total_asset, latest_nav[['code', 'nav', 'navDate']], left_on='Mã CCQ', right_on='code', how='left')

    df_merged['avg_nav'] = df_merged['total_investment'] / df_merged['total_volume']
    df_merged['current_asset_val'] = df_merged['total_volume'] * df_merged['nav']
    df_merged['profit'] = df_merged['current_asset_val'] - df_merged['total_investment']
    df_merged['ratio_profit'] = (df_merged['profit'] / df_merged['total_investment']) * 100

    # Sắp xếp giảm dần theo giá trị số thực tế trước khi format
    df_merged = df_merged.sort_values(by='total_investment', ascending=False)

    # 6. Format dữ liệu hiển thị
    def fmt_money(val):
        return f"{val:,.2f} VN₫"
    
    def fmt_signed_money(val):
        if val > 0:
            return f"+{val:,.2f} VN₫"
        return f"{val:,.2f} VN₫"

    # Tạo danh sách các dòng chi tiết từng quỹ
    rows = []
    for _, row in df_merged.iterrows():
        rows.append({
            'Mã CCQ': row['Mã CCQ'],
            'NAV/CCQ trung bình': fmt_money(row['avg_nav']),
            'Tỷ lệ lợi nhuận (%)': f"{row['ratio_profit']:+.2f}%",
            'Lợi nhuận (VNĐ)': fmt_signed_money(row['profit']),
            'Giá trị tài sản hiện tại': fmt_money(row['current_asset_val']),
            'Tổng khối lượng': f"{row['total_volume']:,.2f}",
            'Tổng vốn đầu tư': fmt_money(row['total_investment']),
            'NAV hiện tại': fmt_money(row['nav']),
            'Cập nhật đến ngày': row['navDate'].strftime('%Y-%m-%d')
        })

    # 7. Tính toán & thêm dòng TỔNG CỘNG
    total_inv = df_merged['total_investment'].sum()
    total_asset_val = df_merged['current_asset_val'].sum()
    total_profit = total_asset_val - total_inv
    total_ratio = (total_profit / total_inv) * 100 if total_inv > 0 else 0.0
    latest_date = df_merged['navDate'].max().strftime('%Y-%m-%d')

    rows.append({
        'Mã CCQ': 'TỔNG CỘNG',
        'NAV/CCQ trung bình': '',
        'Tỷ lệ lợi nhuận (%)': f"{total_ratio:+.2f}%",
        'Lợi nhuận (VNĐ)': fmt_signed_money(total_profit),
        'Giá trị tài sản hiện tại': fmt_money(total_asset_val),
        'Tổng khối lượng': '',
        'Tổng vốn đầu tư': fmt_money(total_inv),
        'NAV hiện tại': '',
        'Cập nhật đến ngày': latest_date
    })

    # 8. Xuất file CSV
    df_export = pd.DataFrame(rows)
    df_export.to_csv(output_file, index=False)
    print(f"Đã xuất file '{output_file}' thành công!")

# Chạy tạo file
generate_total_asset()