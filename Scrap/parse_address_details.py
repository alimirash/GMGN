import json
import csv
import os
from bs4 import BeautifulSoup

def extract_address_info(address,response):
    soup = BeautifulSoup(response, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    if not script_tag:
        print("The specified script tag was not found.")
        return
    
    json_data = json.loads(script_tag.string)
    props = json_data.get("props", {})
    page_props = props.get("pageProps", {})
    address_info = page_props.get("addressInfo", {})
    json_path = os.path.join("results" , "json")
    os.makedirs(json_path, exist_ok=True)
    with open(rf'{json_path}\\{address}.json', 'w', encoding='utf-8') as json_file:
        json.dump(address_info, json_file, indent=4, ensure_ascii=False)

    fieldnames = [
        "address","winrate","pnl","pnl_7d","pnl_30d","realized_profit","realized_profit_7d",
        "realized_profit_30d","unrealized_profit","unrealized_pnl","eth_balance","sol_balance",
        "trx_balance","balance","total_value","all_pnl","total_profit","total_profit_pnl",
        "total_value","buy_30d","sell_30d","buy_7d","sell_7d","buy","sell",
        "history_bought_cost","token_avg_cost","token_sold_avg_profit","token_num","profit_num",
        "pnl_lt_minus_dot5_num","pnl_minus_dot5_0x_num","pnl_lt_2x_num","pnl_2x_5x_num","pnl_gt_5x_num",
        "last_active_timestamp","tags","tag_rank","followers_count","is_contract","updated_at",
        "refresh_requested_at","avg_holding_peroid","name","avatar","ens","twitter_bind",
        "twitter_fans_num","twitter_username","twitter_name",
    ]
    csv_path = os.path.join("results" , "csv")
    os.makedirs(csv_path , exist_ok=True)
    with open(rf'{csv_path}\\{address}.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(address_info)

    print("JSON and CSV files have been saved successfully.")
