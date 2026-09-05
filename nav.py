import requests
import csv
import pandas as pd
from datetime import datetime

url = "https://api.fmarket.vn/res/product/get-nav-history"

def fetchNav():
    products = [
        {"code": "DCDS", "productId": 28},
        {"code": "VCBFBCF", "productId": 32},
        {"code": "VMEEF", "productId": 68}
    ]

    all_nav_data = []

    # 2. Vòng lặp call API cho từng mã CCQ
    for prod in products:
        code = prod["code"]
        product_id = prod["productId"]
        
        print(f"Đang lấy dữ liệu cho mã: {code} (productId: {product_id})...")
        
        payload = {
            "isAllData": 0,
            "productId": product_id,
            "navPeriod": "navToBeginning"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                data_list = res_json.get("data", [])
                
                # Duyệt qua từng bản ghi và chèn thêm cột "code"
                for item in data_list:
                    item["code"] = code  # Thêm cột mã CCQ vào dict
                    all_nav_data.append(item)
                    
                print(f"-> Lấy thành công {len(data_list)} dòng.")
            else:
                print(f"-> Lỗi API cho {code}: Status {response.status_code}")
                
        except Exception as e:
            print(f"-> Lỗi khi kết nối API cho {code}: {e}")

    # 3. Tiến hành Sắp xếp (Sort) danh sách gộp theo ngày navDate
    if all_nav_data:
        # Sort theo chuỗi 'navDate' (dạng YYYY-MM-DD sort chuỗi đúng thứ tự ngày tháng)
        all_nav_data.sort(key=lambda x: x.get("navDate", ""))
        
        output_file = "nav_history_all.csv"
        
        # 4. Xác định tên các cột cho CSV (Bao gồm cả cột 'code' vừa thêm)
        # Sắp xếp thứ tự cột cho đẹp (Ví dụ: code, id, navDate, nav, productId, createdAt)
        fieldnames = ["code", "nav", "navDate"]
        
        # Ghi ra duy nhất 1 file CSV
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_nav_data)
            
        print(f"\n✅ ĐÃ HOÀN THÀNH! Đã lưu tổng cộng {len(all_nav_data)} dòng vào file '{output_file}'.")
    else:
        print("\n❌ Không lấy được dữ liệu nào!")
        
def getNavByFundCodeAndDate(fund_code, date = None):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    df_nav_history = pd.read_csv('nav_history_all.csv')
    condition = (df_nav_history['code'] == fund_code) & (df_nav_history['navDate'] == date)
    match = df_nav_history[condition]
    
    if not match.empty:
        nav_val = match['nav'].values[0];
        nav_val_formatted = f"{float(nav_val):,.2f}";
        print(f"{fund_code} NAV/CQQ at {date}: { nav_val_formatted} đ")
        return nav_val
    else:
        print(f"Không tìm thấy NAV cho mã '{fund_code}' vào ngày '{date}'")
        return None
    
nav_val = getNavByFundCodeAndDate('VCBFBCF', '2026-08-28')
