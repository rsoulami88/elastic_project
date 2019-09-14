import os
import pandas as pd
from flask import Flask
from flask import request
#from pymongo import MongoClient
from bson.json_util import dumps
from werkzeug.utils import secure_filename
from flask_cors import CORS
#from read_pdf import *
#from nlp_extract import *
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host':'','port':9200}])

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '../public/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def count_pres(res):
    count_pres = []
    for i in res:
        list = i['_source']['Sales']
        count = 0
        for j in list:
            if j['type_activity'] == 'presentation':
                count = count + 1
        count_pres.append({"count_pres": count})
    return count_pres


def count_pos(res):
    count_pos = []
    for i in res:
        list = i['_source']['Sales']
        count = 0
        for j in list:
            if j['type_activity'] == 'positionning':
                count = count + 1
        count_pos.append({"count_pos": count})
    return count_pos


@app.route('/get', methods = ['GET'])
def get():
    status = request.args.get('status', default= 'Ongoing IC', type = str)
    page = request.args.get('page', default= 1, type = int)
    search = request.args.get('search', default= status, type = str)
    function = request.args.get('function', default= 1, type = str)
    bu = request.args.get('bu', default= 1, type = str)
    count_query = []
    BU = []
    Mobility = []
    Seniority = []
    if search != status:
        query = {
                            "multi_match" : {
                                "query":    search,
                                "fields": [ "function", "firstName", "Status" ]
                            }
                        }
        count_query.append(query)
    query = [{
                        "multi_match" : {
                            "query":    search, 
                            "fields": [ "function", "firstName", "Status" ]
                        }
                    }]
    query_status = {"term": {"Status.keyword": status}}
    query.append(query_status)
    if function != 1:
        query_function = { "match": { "function": function}}
        query.append(query_function)
        count_query.append(query_function)
    if bu != 1:
        query_bu = { "match": { "bu": bu}}
        query.append(query_bu)
        count_query.append(query_bu)
    try:
        res = es.search(index="consultant", body={
            "from": (page - 1) * 15,
            "size" : 15,
            "query": {
                "bool": {
                    "must": query
                }
            }})
        bu_list = es.search(index="consultant", body={
            "query": {
                "bool": {
                    "must": query
                }
            },
            "size": 0,
            "aggs": {
                "group_by_status": {
                    "terms": {
                        "field": "bu.keyword"
                    }
                }
            }
        })
        Lists = bu_list['aggregations']['group_by_status']['buckets']
        for i in Lists:
            BU.append(i['key'])

        mobility_list = es.search(index="consultant", body={
            "query": {
                "bool": {
                    "must": query
                }
            },
            "size": 0,
            "aggs": {
                "group_by_status": {
                    "terms": {
                        "field": "Mobility.keyword"
                    }
                }
            }
        })
        Lists = mobility_list['aggregations']['group_by_status']['buckets']
        for i in Lists:
            Mobility.append(i['key'])

        seniority_list = es.search(index="consultant", body={
            "query": {
                "bool": {
                    "must": query
                }
            },
            "size": 0,
            "aggs": {
                "group_by_status": {
                    "terms": {
                        "field": "seniority.keyword"
                    }
                }
            }
        })
        Lists = seniority_list['aggregations']['group_by_status']['buckets']
        for i in Lists:
            Seniority.append(i['key'])

        range_salary = es.search(index="consultant", body={
            "size": 0,
            "aggs": {
                "min_salary": {"min": {"field": "Salary"}},
                "max_salary": {"max": {"field": "Salary"}}
            }
        })
        max_salary = range_salary['aggregations']['max_salary']['value']
        min_salary = range_salary['aggregations']['min_salary']['value']
        count = es.search(index="consultant", body={
            "query": {
                "bool": {
                    "must": count_query
                }
            },
            "size": 0,
            "aggs": {
                "group_by_status": {
                    "terms": {
                        "field": "Status.keyword"
                        }
                    }
            }
        })
        counts = count['aggregations']['group_by_status']['buckets']
        dictio = {
            "Candidates": 0,
            "Incoming IC": 0,
            "Ongoing IC": 0,
            "Hirings": 0
        }
        for count in counts:
            dictio.update({count["key"]: count["doc_count"]})
        count_presentation = count_pres(res['hits']['hits'])
        for i in range(len(res['hits']['hits'])):
            res['hits']['hits'][i].update(count_presentation[i])
        count_posi = count_pos(res['hits']['hits'])
        for i in range(len(res['hits']['hits'])):
            res['hits']['hits'][i].update(count_posi[i])
        return dumps({'data' : res['hits']['hits'], 'counts': dictio, 'filters': {"bu": BU, "mobility": Mobility, "seniority": Seniority, "min_salary": min_salary, "max_salary": max_salary},'nb_page': int(dictio[status]/15) if dictio[status] - int(dictio[status]/15)*15 == 0 else int(dictio[status]/15) + 1})
    except ValueError as e:
        return dumps({'error' : str(e)})


@app.route('/home', methods = ['GET'])
def home():
    status = request.args.get('status', default= 'Ongoing IC', type = str)
    page = request.args.get('page', default= 1, type = int)
    try:
        res = es.search(index="consultant", body={
            "from": (page - 1) * 15,
            "size" : 15,
            "query": {
                "bool": {
                    "must": [
                        { "match": { "Status": status}}
                    ]
                }
            }})
        count = es.search(index="consultant", body={
            "size": 0,
            "aggs": {
                "group_by_status": {
                    "terms": {
                        "field": "Status.keyword"
                        }
                    }
            }
        })
        counts = count['aggregations']['group_by_status']['buckets']
        dictio = {
            "Candidates": 0,
            "Incoming IC": 0,
            "Ongoing IC": 0,
            "Hirings": 0
        }
        for count in counts:
            dictio.update({count["key"]: count["doc_count"]})
        return dumps({'data' : res['hits']['hits'], 'counts': dictio, 'nb_page': int(dictio[status]/15) if dictio[status] - int(dictio[status]/15)*15 == 0 else int(dictio[status]/15) + 1})
    except ValueError as e:
        return dumps({'error' : str(e)})

