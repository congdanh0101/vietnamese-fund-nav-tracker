import chart
import nav
import transaction
import asset
import pandas as pd
import holidays

AMOUNT = 300000

def main():
    nav.fetchNav()
    # start_date = pd.Timestamp.today().normalize().replace(day=1)
    start_date = pd.Timestamp.today().normalize()
    end_date = start_date + pd.DateOffset(months=3)
    for date in pd.date_range(start=start_date, end=end_date, freq="B"):
        date_str = date.strftime("%Y-%m-%d")
        transaction.add_daily_transaction("VCBFBCF", date_str, AMOUNT, "data_trans/VCBFBCF_transaction.csv")
            
    # transaction.add_daily_transaction('VCBFBCF',None,AMOUNT,'data_trans/VCBFBCF_transaction.csv')
    transaction.mergedAllTransaction()
    asset.generate_total_asset()
    chart.overall_chart()

if __name__=="__main__":
    main()
    # vn_holidays = holidays.VN(years=range(pd.Timestamp.today().year, 2030))
    # for date in pd.date_range(start=pd.Timestamp.today().normalize(), end="2027-12-31", freq="B"):
    #     if date not in vn_holidays:
    #         date_str = date.strftime("%Y-%m-%d")
    #         print(date_str)
