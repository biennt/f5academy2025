import os
import json
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from openai import OpenAI

load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

maxsize = 100
es = "https://192.168.0.2:9200/"
es_apikey = "T28tbWtwVUJ3Z21wVWRHcks3WVE6SDIwNWZybXNSZWV6SHZEY3lPQ3k3Zw=="
index_pattern = "f5waf-*"
query = {"range": {"@timestamp": {"gte": "now-10m"}}}

client = Elasticsearch(es, api_key=es_apikey,verify_certs=False, ssl_show_warn=False)
resp = client.search(index=index_pattern, size=maxsize, query=query)

documents = ""
count = 0
for hit in resp["hits"]["hits"]:
    logobj = hit["_source"]
    del logobj['message']
    del logobj['event']
    if logobj["violation_rating"] > 2:
        #print("----------------------------------------------")
        json_formatted_str = json.dumps(logobj, indent=2)
        #print(json_formatted_str)
        documents += "\n" + json_formatted_str
        count += 1

if count == 0:
    print("There is nothing to analyze")
    quit()
print("Number of hits: {}".format(resp["hits"]["total"]["value"]))
print(f"Max size: {maxsize}")
print(f"Number of records with 'violation_rating > 2': {count}")

########################################
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

