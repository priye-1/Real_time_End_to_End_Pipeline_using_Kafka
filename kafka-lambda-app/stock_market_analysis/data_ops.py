import pandas as pd
import requests
from time import sleep
from typing import List, Dict
from datetime import datetime


def get_stock_data() -> List[Dict]:
    """Function to scrape data from CNN API

    Returns:
        json: Stock market results

    Sample output:
        [
            {
                'name': 'Nasdaq',
                'symbol': 'COMP-USA',
                'current_price': 12284.74316868,
                'prev_close_price': 12328.5065042,
                'price_change_from_prev_close': -43.76333552000142,
                'percent_change_from_prev_close': -0.003549767808865769,
                'prev_close_date': '2023-05-11',
                'sort_order_index': 0,
                'last_updated': '2023-05-12T21:16:26+00:00',
                'event_timestamp': '2023-05-12T21:16:26+00:00',
                'status': 'UNKNOWN',
                'next_status': 'UNKNOWN',
                'next_status_change': '2023-05-12T13:30:21.109002+00:00',
                'country': {'name': 'United States', 'code': 'USA', 'region': 'Americas'},
                'refresh_interval_in_seconds': 0
            }
        ]
    """

    today_date = datetime.now().strftime("%Y-%m-%d")

    url = f"https://production.dataviz.cnn.io/markets/world/regions/Americas,Asia-Pacific,Europe/{today_date}"

    payload = {}
    headers = {
        'authority': 'production.dataviz.cnn.io',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,my-ZG;q=0.8,my;q=0.7',
        'cache-control': 'no-cache',
        'origin': 'https://edition.cnn.com',
        'pragma': 'no-cache',
        'referer': 'https://edition.cnn.com/',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def clean_stock_data(uncleaned_stock_data: List[Dict]) -> List[Dict]:
    """_summary_

    Args:
        uncleaned_stock_data (List[Dict]): _description_
    """

    def format_date(date):
        date_list = date.split("T")
        date_string2 = date_list[-1].split("+")[0].split(".")[0]
        return f"{date_list[0]} {date_string2}"

    stock_df = pd.DataFrame(uncleaned_stock_data).drop(
                [
                    "sort_order_index", "event_timestamp",
                    "next_status", "next_status_change",
                    "status", "refresh_interval_in_seconds"
                ],
                axis=1
            )
    stock_df['country_name'] = stock_df['country'].apply(
            lambda item: item['name']
        )
    stock_df['country_code'] = stock_df['country'].apply(
            lambda item: item['code']
        )
    stock_df['country_region'] = stock_df['country'].apply(
            lambda item: item['region']
        )
    stock_df["last_updated"] = stock_df["last_updated"].apply(
            lambda item: format_date(item)
        )
    stock_df = stock_df.drop(["country"], axis=1)

    return stock_df.to_dict(orient='records')


def send_producer_data(cleaned_stock_data: List[Dict], kafka_producer: object, topic_name: str):
    """Function to send data to kafka producer

    Args:
        stock_data (list): _description_
        producer (object): _description_
        bucket_name (str): _description_

    Returns:
        NoReturn: _description_
    """
    for stock in cleaned_stock_data:
        kafka_producer.send(
            topic_name,
            value=stock
        )

        sleep(3)
