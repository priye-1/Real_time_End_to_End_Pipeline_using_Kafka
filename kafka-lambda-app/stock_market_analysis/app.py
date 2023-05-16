import os
import json
from json import dumps
from kafka import KafkaProducer
from data_ops import (
    get_stock_data, clean_stock_data, send_producer_data
)

# load environment variable

BOOTSTRAP_SERVER = os.environ.get('BOOTSTRAP_SERVER')


def kafka_stock_analysis_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy
        -integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    """

    stock_data = get_stock_data()

    cleaned_stock_data = clean_stock_data(stock_data)

    kafka_producer = KafkaProducer(
        bootstrap_servers=[BOOTSTRAP_SERVER],
        value_serializer=lambda x: dumps(x).encode('utf-8')
    )

    topic_name = "stock-market-analysis"

    send_producer_data(cleaned_stock_data, kafka_producer, topic_name)

    return {
        "statusCode": 200,
        "data":  cleaned_stock_data[0:5],
        "body": json.dumps({
            "message": "Data uploaded to kafka client"
        }),
    }
