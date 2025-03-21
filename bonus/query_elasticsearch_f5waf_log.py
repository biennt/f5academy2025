#import
import os
import json
import time
import requests
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv(override=True)
api_url = 'https://api.telegram.org/bot{token}/{method}'.format
TELEGRAM_ACCESS_TOKEN = os.getenv('TELE_API_KEY', 'your-key-if-not-using-env')
chat_id = "-4560815562"

########################################
def query_es(violation_rating, time_relative, maxsize):
    ES_API_KEY = os.getenv('ES_API_KEY', 'your-key-if-not-using-env')
    es = "https://192.168.0.2:9200/"
    index_pattern = "f5waf-*"
    query = { 
         "range": {"violation_rating": {"gte": violation_rating}},
         "range": {"@timestamp": {"gte": "now-" + time_relative}}
     }
    client = Elasticsearch(es, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    resp = client.search(index=index_pattern, size=maxsize, query=query)
    documents = []
    count = 0
    for hit in resp["hits"]["hits"]:
        logobj = hit["_source"]
        del logobj["message"]
        del logobj["event"]
        documents.append(logobj)
        count += 1
    print(f"There are {count} documents with violation_rating greater than or equal {violation_rating}, in the last {time_relative} returned")
    return documents
########################################
# send sms to telegram using simple http requests
def telegram_command(name, data):
    url = api_url(token=TELEGRAM_ACCESS_TOKEN, method=name)
    try:
        res = requests.post(url=url, json=data)
    except Exception(ex):
        print(ex)
    return res
def telegram_sendMessage(text: str):
    return telegram_command('sendMessage', {
        'text': text,
        'chat_id': chat_id,
        'parse_mode': 'markdown',
        'disable_notification': not True})
#################################################
# Main
interval = 20

while True:
    print("---------------------------------------------------------")
    es_response = query_es(5,"5s",10)
    if len(es_response) > 0:
        print("Site is under attacked")
        supportIDs = ""
        for event in es_response:
            supportIDs += "\n" + event['support_id']
        telegram_sendMessage("**Site is under attacked!**\n Support IDs are: \n" + supportIDs)
    else:
        print("Site is safe")
    print(f"Sleep for {interval} seconds")
    time.sleep(interval)
