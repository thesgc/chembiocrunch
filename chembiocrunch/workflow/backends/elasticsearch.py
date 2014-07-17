from __future__ import absolute_import

import csv

import json

from django.db import models

from elasticsearch import Elasticsearch, NotFoundError, RequestError
from elasticsearch.helpers import bulk
from elasticsearch.client import IndicesClient
from wagtail.wagtailsearch.backends.base import BaseSearch
from wagtail.wagtailsearch.indexed import Indexed
from wagtail.wagtailsearch.utils import normalise_query_string
from django.template.defaultfilters import slugify    
        







class ElasticSearchDataProcessor():
    def __init__(self, workflowpage_id, revision_id, params, just_testing_string=""):
        # Get settings
        self.es_urls = params.pop('URLS', ['http://localhost:9200'])
        self.es_index = params.pop('INDEX', '%scalc_workflow_%d_r%d' % (just_testing_string, workflowpage_id, revision_id))
        self.es_timeout = params.pop('TIMEOUT', 5)
        self.es_force_new = params.pop('FORCE_NEW', False)
        self.es_type = "%scalc_workflow_%d_r%d" % (just_testing_string, workflowpage_id, revision_id)
        # Get ElasticSearch interface
        # Any remaining params are passed into the ElasticSearch constructor
        self.es = Elasticsearch(
            urls=self.es_urls,
            timeout=self.es_timeout,
            force_new=self.es_force_new,
            **params)
        self.iclient = IndicesClient(self.es)

    def reset_index(self):
        # Delete old index
        try:
            self.es.indices.delete(self.es_index)
        except NotFoundError:
            pass

        # Settings
        INDEX_SETTINGS = {
            "settings": {
 
            }
        }

        # Create new index
        self.es.indices.create(self.es_index, INDEX_SETTINGS)

    def add_type(self):
        # Put mapping
        self.es.indices.put_mapping(index=self.es_index, doc_type=self.es_type, body={
        self.es_type: {
	                "dynamic_templates": [
		                {
		                "template_2" : {
		                    "match" : "*",
		                    "match_mapping_type" : "string",
		                    "mapping" : {
		                        "type" : "string",
		                        "index" : "not_analyzed"
		                    }
		                }
		            },
	           	]
            }
        })

    def refresh_index(self):
        self.es.indices.refresh(self.es_index)

    def add(self, doc):
        # Add to index
        self.es.index(self.es_index, self.es_type, doc)

    def add_bulk(self, obj_list):
        # Group all objects by their type

        actions = []
        for obj in obj_list:
            action = {
                '_index': self.es_index,
                '_type': self.es_type,
                '_id' : obj["_id"]
            }
            action.update(obj)
            actions.append(action)
        return bulk(self.es, actions)

    def delete(self, obj):
		return NotImplemented



    def get_mappings(self):

        return self.iclient.get_mapping(self.es_index, self.es_type).get(self.es_index,{}).get("mappings",{}).get(self.es_type,{}).get("properties",{})
 


    def get_terms_agregation(self):
        fields = self.get_mappings()
        aggs = {slugify(field) : {"terms" : {"field" : field , "size": 10000, "order" : { "_term" : "asc" }} } for field in fields}
        body = {"query":    {  "match_all":{} },"aggs" : aggs,"size": 0}
        response = self.es.search(self.es_index, self.es_type, body=body).get("aggregations",{})
        #elasticsearch does not allow funny characters in field names but we want them
       
        results = {field : response.get(slugify(field)).get('buckets') for field in fields}

        return results

    def choices(self, results):
        choices = []
        for field, value in results.iteritems():
            print field
            for item in value:
                choices.append(("%s___%s" % (field, item["key"]),"%s___%s" % (field, item["key"])))
        return choices

    def count(self):
        return self.es.count(self.es_index,self.es_type).get("count",0)


    def get_preview(self):
        body = {
                    "query":  { "match_all":{}},
                    "size" :100
                }
        data = self.es.search(self.es_index, self.es_type, body=body)
        hits = [hit.get("_source") for hit in data.get("hits",{}).get("hits")]
        data["hits"] = hits
        return data



    def process_filter(self):
        pass