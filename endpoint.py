import requests
import json
from pymongo import MongoClient
import numpy as np
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host':'localhost','port':9200}])

Client = MongoClient("mongodb://165.22.225.229:27017/")
db = Client["focus"]
collection = db["profile"]

response = requests.post('https://maltem.progessi.com/api/control/profilesExport', data={"login.username" : "xadmfocus", "login.password" : "M@dMx%2022::)VetY%1" })

data = response.json()['data']
data = data.replace("[", "").replace("]", "").replace("},{", "}@@{")
data = data.split("@@")

status_type = ['Ongoing IC', 'Incoming IC', 'Hirings', 'Candidates']
for t in data:
    t = json.loads(t)
    salary = np.random.randint(1000, 2000)
    t.update({"Salary":salary})
    status = np.random.choice(status_type, p=[0.1, 0.1, 0.1, 0.7])
    t.update({"Status":status})
    res = es.index(index='profile',doc_type='profile',body=t)
    collection.insert_one(t)

print('Done')