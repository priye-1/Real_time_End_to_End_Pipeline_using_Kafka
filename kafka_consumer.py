import os
import re
import json
from time import sleep
from json import loads
from kafka import KafkaConsumer
from s3fs import S3FileSystem

BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')
AWS_KEY = os.getenv('AWS_KEY')
AWS_SECRET = os.getenv('AWS_SECRET')

topic_name = "stock-market-analysis"

consumer_object = KafkaConsumer(
    topic_name,
    bootstrap_servers=BOOTSTRAP_SERVER,
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

s3 = S3FileSystem(
    key=AWS_KEY,
    secret=AWS_SECRET,
    client_kwargs={
        'region_name': 'eu-north-1'
    }
)

s3_objects = s3.ls('kafka-stock-market-project-priye')
file_numbers = list(map(lambda x: re.findall("[0-9]+", x)[0], s3_objects))
highest_s3_file_number = max([int(x) for x in file_numbers])

for count, data in enumerate(consumer_object, start=highest_s3_file_number + 1):
    with s3.open(f"s3://kafka-stock-market-project-priye/stock_market_{count}.json", 'w') as file:
        json.dump(data.value, file)
    print(data.value)
    sleep(3)
