import os
import json
import time
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from openai import OpenAI
import requests
load_dotenv(override=True)
api_url = 'https://api.telegram.org/bot{token}/{method}'.format
TELEGRAM_ACCESS_TOKEN = os.getenv('TELE_API_KEY', 'your-key-if-not-using-env')
chat_id = "-4560815562"

########################################
def query_es():
    ES_API_KEY = os.getenv('ES_API_KEY', 'your-key-if-not-using-env')
    maxsize = 10
    es = "https://192.168.0.2:9200/"
    index_pattern = "f5waf-*"
    query = {"range": {"@timestamp": {"gte": "now-10m"}}}
    client = Elasticsearch(es, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    resp = client.search(index=index_pattern, size=maxsize, query=query)
    documents = ""
    for hit in resp["hits"]["hits"]:
        logobj = hit["_source"]
        del logobj['message']
        del logobj['event']
        if logobj["violation_rating"] > 2:
            json_formatted_str = json.dumps(logobj, indent=2)
            documents += "\n" + json_formatted_str
    return documents

########################################
def ask_gpt(documents):
    system_message = {
        "role": "system",
        "content": "You are a security specialist to help me analyse and summary logs from F5 BIG-IP WAF device."
    }
    question = "Give me a summary of the security events from the content below:\n"
    user_message = {
        "role": "user",
        "content": question + documents
    }
    messages = [system_message, user_message]
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')
    openai  = OpenAI()
    MODEL = "gpt-4o"
    stream = openai.chat.completions.create(model=MODEL, messages=messages, stream=True)
    response = ""
    print("------------------")
    for chunk in stream:
        word = chunk.choices[0].delta.content or ''
        response += word
        print(word,end='')
        print("")
    return response


def telegram_command(name, data):
    url = api_url(token=TELEGRAM_ACCESS_TOKEN, method=name)
    return requests.post(url=url, json=data)


def telegram_sendMessage(text: str):
    return telegram_command('sendMessage', {
        'text': text,
        'chat_id': chat_id,
        'parse_mode': 'markdown',
        'disable_notification': not True})

#################################################
interval = 10
while True:
    es_response = query_es()
    if len(es_response) > 0:
        text_2_send = "Site is under attacked\n"
        gpt_response = ask_gpt(es_response)
        text_2_send += gpt_response
        telegram_sendMessage(text_2_send)
    else:
        telegram_sendMessage("Site is safe")
    print(f"Sleep for {interval} seconds")
    time.sleep(interval)
