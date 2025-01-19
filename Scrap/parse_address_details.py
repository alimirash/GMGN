import os
import csv
import json
import sqlite3
from bs4 import BeautifulSoup
from config.configs import DB_PATH

def extract_address_info(address, response):
    soup = BeautifulSoup(response, 'html.parser')
    script_tag = soup.find(
        'script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    if not script_tag:
        print("The specified script tag was not found.")
        return "Failure"

    json_data = json.loads(script_tag.string)
    props = json_data.get("props", {})
    page_props = props.get("pageProps", {})
    address_info = page_props.get("addressInfo", {})
    if isinstance(address_info.get('tags'), list):
        address_info['tags'] = json.dumps(address_info['tags'])
    if isinstance(address_info.get('tag_rank'), dict):
        address_info['tag_rank'] = json.dumps(address_info['tag_rank'])

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO results (
                address, twitter_bind, twitter_fans_num, twitter_username, twitter_name,
                ens, avatar, name, eth_balance, sol_balance, trx_balance, balance,
                total_value, unrealized_profit, unrealized_pnl, realized_profit, pnl,
                pnl_7d, pnl_30d, realized_profit_7d, realized_profit_30d, winrate,
                all_pnl, total_profit, total_profit_pnl, buy_30d, sell_30d, buy_7d,
                sell_7d, buy, sell, history_bought_cost, token_avg_cost,
                token_sold_avg_profit, token_num, profit_num, pnl_lt_minus_dot5_num,
                pnl_minus_dot5_0x_num, pnl_lt_2x_num, pnl_2x_5x_num, pnl_gt_5x_num,
                last_active_timestamp, tags, tag_rank, followers_count, is_contract,
                updated_at, refresh_requested_at, avg_holding_peroid, name,
                avatar, ens, twitter_bind, twitter_fans_num, twitter_username,
                twitter_name
            ) VALUES (
                :address, :twitter_bind, :twitter_fans_num, :twitter_username, :twitter_name,
                :ens, :avatar, :name, :eth_balance, :sol_balance, :trx_balance, :balance,
                :total_value, :unrealized_profit, :unrealized_pnl, :realized_profit, :pnl,
                :pnl_7d, :pnl_30d, :realized_profit_7d, :realized_profit_30d, :winrate,
                :all_pnl, :total_profit, :total_profit_pnl, :buy_30d, :sell_30d, :buy_7d,
                :sell_7d, :buy, :sell, :history_bought_cost, :token_avg_cost,
                :token_sold_avg_profit, :token_num, :profit_num, :pnl_lt_minus_dot5_num,
                :pnl_minus_dot5_0x_num, :pnl_lt_2x_num, :pnl_2x_5x_num, :pnl_gt_5x_num,
                :last_active_timestamp, :tags, :tag_rank, :followers_count, :is_contract,
                :updated_at, :refresh_requested_at, :avg_holding_peroid, :name,
                :avatar, :ens, :twitter_bind, :twitter_fans_num, :twitter_username,
                :twitter_name
            )
        """, address_info)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "Failure"
    finally:
        conn.close()

    return "Successful"
