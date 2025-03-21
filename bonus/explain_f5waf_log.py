#import
import os
import json
import time
import requests
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from openai import OpenAI

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
    documents = ""
    count = 0
    for hit in resp["hits"]["hits"]:
        logobj = hit["_source"]
        documents += "\n" + logobj['message']
        count += 1
    print(f"There are {count} documents with violation_rating greater than or equal {violation_rating}, in the last {time_relative} returned")
    return documents
########################################
def ask_gpt(documents):
    system_message = {
        "role": "system",
        "content": "You are a security specialist to help me analyse and summary logs from F5 BIG-IP WAF device."
    }
    question = "Give me a short summary of the security events which include only: \n"
    question += "client ip address, violation rating, violation, sig_names, URI, policy name, support id\n"
    question += "from the content below:\n"
    user_message = {
        "role": "user",
        "content": question + documents
    }
    messages = [system_message, user_message]
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')
    openai  = OpenAI()
    MODEL = "gpt-4o-mini"
    response = openai.chat.completions.create(model=MODEL, messages=messages, stream=False)
    return_content = response.choices[0].message.content
    return return_content
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
#telegram_sendMessage("this is a test")

while True:
    print("---------------------------------------------------------")
    text_2_send = ""
    es_response = query_es(5,"5s",10)
    if len(es_response) > 0:
        text_2_send = "Site is under attacked\n"
        gpt_response = ask_gpt(es_response)
        text_2_send += gpt_response
    else:
        text_2_send = "Site is safe"    
     
    print(text_2_send)
    telegram_sendMessage(text_2_send)
    print(f"Sleep for {interval} seconds")
    time.sleep(interval)
