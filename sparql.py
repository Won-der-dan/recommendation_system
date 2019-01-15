import json
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

recommendFilm = 'The Lord of the Rings: The Return of the King'

def get_films(recommendFilmUri):
    query = """SELECT DISTINCT ?name WHERE {
  ?film wdt:P31 wd:Q11424.
  ?film wdt:P1476 ?name.
  ?film wdt:P1411 ?nomination.
  {
  SELECT ?nomination WHERE {
  ?nomination wdt:P31 wd:Q19020.
  wd:""" + recommendFilmUri + """ wdt:P1411 ?nomination.
}}
}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()



films = requests.get('https://www.wikidata.org/w/api.php', {
    'action': 'wbgetentities',
    'titles': recommendFilm,
    'sites': 'enwiki',
    'props': '',
    'format': 'json'
}).json()
recommendFilmUri = list(films['entities'])[0]
print(recommendFilmUri)
results = get_films(recommendFilmUri)
print(results)
filmsArray = []
for result in results["results"]["bindings"]:
    filmsArray.append(result["name"]["value"])
# print(filmsArray)
json_file = dict()
json_file[recommendFilmUri] = filmsArray
with open('result.json', 'w') as outfile:
    json.dump(json_file, outfile, indent=4);
