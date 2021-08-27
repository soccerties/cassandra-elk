#!/usr/bin/env python

from elasticsearch6 import Elasticsearch
import requests
import logging
import os
import argparse
import sys
import json

parser = argparse.ArgumentParser(description="This script exports all dashboards and objects for Kibana and saves them as json files.")

parser.add_argument('-e', '--elasticsearch', help="ElasticSearch host to get Kibana data from.", default="localhost")
parser.add_argument('-k', '--kibana', help="Kibana host to export dashboards from.", default="localhost")
parser.add_argument('-i', '--index', help="The ElasticSearch index name with Kibana data.", default=".kibana")
parser.add_argument('-d', '--destination', help="Directory to save dashboard json files to.", default=os.path.join(os.getcwd(), 'kibana', 'dashboards'))
parser.add_argument('-v', '--verbose', help="Enable verbose logging output.", action="store_true")

args = parser.parse_args()

if args.verbose:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

l = logging.getLogger()
l.setLevel(log_level)
o_h = logging.StreamHandler(sys.stdout)
l.addHandler(o_h)

l.debug("Script arguments: {}".format(args))

kibana_export_url = 'http://'+args.kibana+':5601/api/kibana/dashboards/export'

l.debug("Connecting to ElasticSearch")
es_url = 'http://'+args.elasticsearch+':9200'
es = Elasticsearch(es_url)

l.debug("Querying dashboards")
es_search = {"query": {"match": {"type": "dashboard"}}}
es_dashboards = es.search(index=args.index, body=es_search, filter_path=['hits.hits._id', 'hits.hits._source.dashboard.title'])


def export_dashboard(dashboard_id):
    l.debug("Exporting Dashboard: {}".format(dashboard_id))
    r = requests.get(kibana_export_url + "?dashboard={}".format(dashboard_id))
    return json.loads(r.content)


def write_dashboard_file(dashboard_filename, dashboard_json):
    l.debug("Writing dashboard file {}".format(dashboard_filename))
    with open(os.path.join(args.destination, dashboard_filename), "w") as dashboard_file:
        dashboard_file.write(json.dumps(dashboard_json, indent=2, sort_keys=True))


if len(es_dashboards) > 0:
    dashboards = {}
    for hit in es_dashboards["hits"]["hits"]:
        l.debug("Found Dashboard {}".format(hit["_id"]))

        dashboard_id = hit["_id"].split(":")[1]
        dashboard_title = hit["_source"]["dashboard"]["title"]

        dashboard_json = export_dashboard(dashboard_id)

        dashboard_filename = dashboard_title.replace(" ", "_").lower() + ".json"
        l.info("Saving dashboard to {}".format(dashboard_filename))
        write_dashboard_file(dashboard_filename, dashboard_json)
else:
    l.info("No dashboards found to export.")

l.info("Finished")
