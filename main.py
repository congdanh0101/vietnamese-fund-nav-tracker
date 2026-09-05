import chart
import nav
import transaction
import asset
import pandas as pd
import json

AMOUNT = 300000

def main():
    nav.fetchNav()
    start_date = pd.Timestamp('2026-08-01').date()
    # start_date = pd.Timestamp.today().normalize().replace(day=1)
    # start_date = pd.Timestamp.today().normalize()
    end_date = start_date + pd.DateOffset(months=2)
    FUND_INFO = loadInfoSIP()
    for date in pd.date_range(start=start_date, end=end_date, freq="B"):
        date_str = date.strftime("%Y-%m-%d")
        transaction.add_daily_transaction(FUND_INFO[0], date_str, FUND_INFO[1], f"data_trans/{FUND_INFO[0]}_transaction.csv", 'SIP')
            
    # transaction.add_daily_transaction(FUND_INFO[0], None, FUND_INFO[1], f"data_trans/{FUND_INFO[0]}_transaction.csv", 'SIP')
    transaction.mergedAllTransaction()
    asset.generate_total_asset()
    chart.overall_chart()
    chart.line_chart()
    chart.column_chart()

def loadInfoSIP():
    with open('config/sip_fund_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    FUND_CODE = config["fund_code"]
    AMOUNT = config["amount"]
    return [FUND_CODE, AMOUNT]
    

if __name__=="__main__":
    # print(loadInfoSIP())
    main()
    # vn_holidays = holidays.VN(years=range(pd.Timestamp.today().year, 2030))
    # for date in pd.date_range(start=pd.Timestamp.today().normalize(), end="2027-12-31", freq="B"):
    #     if date not in vn_holidays:
    #         date_str = date.strftime("%Y-%m-%d")
    #         print(date_str)
