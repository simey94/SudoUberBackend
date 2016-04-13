import sys
sys.path.append("../..")
sys.path.append("..")

import requests
import json


class cat_fact_collector_service():
    def find_cat_facts(self, no_of_facts):
        url = "http://catfacts-api.appspot.com/api/facts?number="
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            from BeautifulSoup import BeautifulSoup
        url += str(no_of_facts)
        print url
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html)
        print soup
        catFacts = json.loads(str(soup))
        cat_facts_list = catFacts["facts"]
        for item in catFacts["facts"]:
            print str(item).split("\"\",")
        return cat_facts_list

cf = cat_fact_collector_service()
cf.find_cat_facts(5)

