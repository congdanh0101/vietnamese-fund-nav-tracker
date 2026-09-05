import pandas as pd
import nav
from datetime import datetime
import math

def initAllTransaction():
    print('Init all transactions')
    initTransactionVCBF()
    initTransactionVMEEF()
    initTransactionDCDS()
    # mergedAllTransaction()
    
def initTransactionVCBF():
    print('Init transactions for VCBFBCF')
    initTransaction('VCBFBCF','data_init_trans/Opened-Funds - VCBFBCF.csv', 'data_trans/VCBFBCF_transaction.csv')

def initTransactionVMEEF():
    print('Init transactions for VMEEF')
    initTransaction('VMEEF', 'data_init_trans/Opened-Funds - VMEEF.csv', 'data_trans/VMEEF_transaction.csv')
    
def initTransactionDCDS():
    print('Init transactions for DCDS')
    initTransaction('DCDS', 'data_init_trans/Opened-Funds - DCDS.csv', 'data_trans/DCDS_transaction.csv')

def initTransaction(fund_code, inputFile, outputFile):
    
    df = pd.read_csv(inputFile)
    cols_to_keep = [
            'Ngày khớp lệnh', 
            'NAV/CQQ khớp lệnh', 
            'Khối lượng khớp lệnh', 
            'Giá trị khớp lệnh', 
            'Vốn đầu tư'
        ]
    
    #  Lọc lấy đúng 5 cột và loại bỏ dòng tổng (dòng bị trống ngày)
    df_filtered = df[cols_to_keep].dropna(subset=['Ngày khớp lệnh'])
    df_filtered.insert(1, 'Mã CCQ', fund_code)

    money_cols = ['NAV/CQQ khớp lệnh', 'Khối lượng khớp lệnh', 'Giá trị khớp lệnh', 'Vốn đầu tư']    
    for col in money_cols:
        df_filtered[col] = df_filtered[col].apply(lambda x: format_money(x, swap=True))
        
        
    #  Chuyển định dạng ngày từ dd/MM/yyyy sang yyyy-MM-dd
    df_filtered['Ngày khớp lệnh'] = pd.to_datetime(df_filtered['Ngày khớp lệnh'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    df_filtered = df_filtered.sort_values(by='Ngày khớp lệnh', ascending=True)
    
    df_filtered.to_csv(outputFile, index=False)
    
def format_money(val_str, swap = True):
        if pd.isna(val_str): return val_str
        s = str(val_str).strip()
        has_vn = 'VN₫' in s
        has_d = 'đ' in s and not has_vn
        
        # Bỏ các ký tự chữ và làm sạch chuỗi số
        clean_num = s.replace('VN₫', '').replace('đ', '')
        if swap == True:
            clean_num = clean_num.replace('.', '').replace(',', '.').strip()
        else:
            clean_num = clean_num.replace(',', '').strip()
        try:
            num = float(clean_num)
            formatted = f"{num:,.2f}"

            if has_vn or has_d: return f"{formatted} VN₫"
            else: return formatted
        except:
            return val_str

def add_daily_transaction(fund_code, transaction_date, investment_value, file_path, transaction_type = 'SIP'):
    
    if transaction_date is None:
        transaction_date = datetime.now().strftime('%Y-%m-%d')
    
    df = pd.read_csv(file_path)
    
    condition = (df['Mã CCQ'] == fund_code) & (df['Ngày khớp lệnh'] == transaction_date) & (transaction_type == 'SIP')
    match = df[condition]    
    if not match.empty:
        print(f"Transaction SIP for {fund_code} at {transaction_date} has been existed")
        return
    
    nav_val = nav.getNavByFundCodeAndDate(fund_code, transaction_date)
    
    if nav_val is None:
        print("Hủy thêm giao dịch do không lấy được NAV.")
        return
    
    # nav_val = float(nav_str.replace(',', ''))
    raw_volume = investment_value / nav_val
    volume_floored = math.floor(raw_volume * 100) / 100
    transaction_value = volume_floored * nav_val
    
    volume_str = f"{volume_floored:,.2f}"
    transaction_value_str = f"{transaction_value:,.2f}"
    investment_value_str = f"{int(investment_value):,.2f}"
    # volume = investment_value / nav_val
    # 1. Tạo bản ghi giao dịch mới
    new_data = pd.DataFrame([{
        'Ngày khớp lệnh': transaction_date,               # Dạng YYYY-MM-DD
        'Mã CCQ': fund_code,
        'NAV/CQQ khớp lệnh': f"{float(nav_val):,.2f} VN₫",
        'Khối lượng khớp lệnh': volume_str,
        'Giá trị khớp lệnh': f"{transaction_value_str} VN₫",
        'Vốn đầu tư': f"{investment_value_str} VN₫"
    }])
    
    
    df_updated = pd.concat([df, new_data], ignore_index=True)
    
    # 3. Sắp xếp lại theo thứ tự ngày tăng dần
    df_updated['Ngay_temp'] = pd.to_datetime(df_updated['Ngày khớp lệnh'])
    df_updated = df_updated.sort_values(by='Ngay_temp', ascending=True).drop(columns=['Ngay_temp'])
    
    money_cols = ['NAV/CQQ khớp lệnh', 'Khối lượng khớp lệnh', 'Giá trị khớp lệnh', 'Vốn đầu tư']    
    for col in money_cols:
        df_updated[col] = df_updated[col].apply(lambda x: format_money(x, swap=False))
    
    # 4. Lưu đè lại file tổng
    df_updated.to_csv(file_path, index=False)
    print(f"Đã thêm giao dịch ngày {transaction_date} cho {fund_code} thành công!")
    

def mergedAllTransaction():
    print('Merge transaction')
    file_list = ['VCBFBCF_transaction.csv', 'VMEEF_transaction.csv', 'DCDS_transaction.csv']
    dfs = []
    for file in file_list:
        df = pd.read_csv(f"data_trans/{file}")
        dfs.append(df)

    # 3. Gộp (merge/concat) các DataFrame lại thành một
    merged_df = pd.concat(dfs, ignore_index=True)

    # 4. Sắp xếp theo cột 'Ngày khớp lệnh'
    # Chuyển tạm sang định dạng Datetime để sắp xếp đúng thứ tự thời gian
    merged_df['Ngay_temp'] = pd.to_datetime(merged_df['Ngày khớp lệnh'])

    # Mẹo: ascending=True (từ cũ đến mới) hoặc ascending=False (từ mới đến cũ)
    merged_df = merged_df.sort_values(by='Ngay_temp', ascending=True)

    # Xóa cột tạm thời
    merged_df = merged_df.drop(columns=['Ngay_temp'])

    money_cols = ['NAV/CQQ khớp lệnh', 'Khối lượng khớp lệnh', 'Giá trị khớp lệnh', 'Vốn đầu tư']    
    for col in money_cols:
        merged_df[col] = merged_df[col].apply(lambda x: format_money(x, swap=False))

    # 5. Lưu kết quả ra file CSV gộp chung
    merged_df.to_csv('data_trans/All_Transactions_Merged.csv', index=False)

# initAllTransaction()