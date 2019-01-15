#!/usr/bin/env python3
import operator
import json
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

"""
Скрипт для расчета оценок для заданного пользователя
"""

INFILE = 'data.csv'
OUTFILE = 'data-new.csv'
DAYFILE = 'context_day.csv'
PLACEFILE = 'context_place.csv'
FILMDB = 'films'
ID = 8


# Считывание данных из файла
x = {}
userDict = dict()
with open(INFILE) as data:
    data.readline()
    for line in data:
        x = line.split(', ')
        x.append(x.pop().strip())
        userDict[int(x[0].replace("User ", ""))] = x[1::]

for user in userDict:
    userDict[user] = list(map(int, userDict[user]))
#Считывание данных уже из другого файла
x = {}
dayDict = dict()
with open(DAYFILE) as data:
    data.readline()
    for line in data:
        x = line.split(', ')
        x.append(x.pop().strip())
        dayDict[int(x[0].replace("User ", ""))] = x[1::]
#Все еще считывание данных
x = {}
placeDict = dict()
with open(PLACEFILE) as data:
    data.readline()
    for line in data:
        x = line.split(', ')
        x.append(x.pop().strip())
        placeDict[int(x[0].replace("User ", ""))] = x[1::]

keyUserMovies = userDict[ID]
moviesCount = len(keyUserMovies)

similarity = {}
for user in userDict:
    similarMovies = list()
    userMovies = userDict[user]

    for i in range(0, moviesCount):
        if keyUserMovies[i] != -1 and userMovies[i] != -1:
            similarMovies.append(i)

    firstSum = 0
    secondSum = 0
    thirdSum = 0

    for i in similarMovies:
        firstSum += userMovies[i] * keyUserMovies[i]
        secondSum += userMovies[i]**2
        thirdSum += keyUserMovies[i]**2

    secondSum = round(secondSum ** 0.5, 3)
    thirdSum = round(thirdSum ** 0.5, 3)
    sim = round(firstSum / (secondSum * thirdSum), 3)
    similarity[user] = sim

del similarity[ID]
sorted_sim = sorted(similarity.items(), key=operator.itemgetter(1),
                    reverse=True)
sorted_sim = sorted_sim[0:7]

def avgRank(id : int):
    list = [x for x in userDict[id] if x != -1]
    return round(sum(list) / float(len(list)),3)

filmRecommends = {}
for filmIndex, filmRate in enumerate(keyUserMovies):
    if filmRate == -1:
        firstSum = 0
        secondSum = 0
        for user, sim in sorted_sim:
            if userDict[user][filmIndex] != -1:
                firstSum += round(sim*(userDict[user][filmIndex] - avgRank(user)),3)
                secondSum += abs(sim)
        suggestedRank = avgRank(ID) + (firstSum/secondSum)

        # Применяем формулу для расчёта оценки фильма
        filmRecommends[filmIndex+1] = round(suggestedRank, 3)


def recommend2(dayData, placeData):
    """
    Рекомендует фильм на основе дополнительных данных
    """
    filmsToRecommend = {}
    for filmIndex, film in enumerate(keyUserMovies):
        if film == -1:
            for user, sim in sorted_sim:
                if not filmIndex in filmsToRecommend.keys():
                    filmsToRecommend[filmIndex] = 0
                if ( dayData[user][filmIndex] == 'Sat' or \
                     dayData[user][filmIndex] == 'Sun' ) and \
                    placeData[user][filmIndex] == 'h' and \
                   sim > 0.8:
                   filmsToRecommend[filmIndex] += float(sim)
    return filmsToRecommend

maxV = bestFilm = -1
for k, v in recommend2(dayDict, placeDict).items():
    if v > maxV:
        maxV = v
        bestFilm = k+1

res2 = None
if bestFilm > -1:
    # res2 = {
    # "movie {}".format(bestFilm): maxV
    # }
    res2 = "movie {}".format(bestFilm)

# def get_films(recommendFilmUri):
#     query = """SELECT DISTINCT ?name WHERE {
#   ?film wdt:P31 wd:Q11424.
#   ?film wdt:P1476 ?name.
#   ?film wdt:P1411 ?nomination.
#   {
#   SELECT ?nomination WHERE {
#   ?nomination wdt:P31 wd:Q19020.
#   wd:""" + recommendFilmUri + """ wdt:P1411 ?nomination.
# }}
# }
#     """
#     sparql.setQuery(query)
#     sparql.setReturnFormat(JSON)
#     print(sparql.query())
#     return sparql.query().convert()


bestFilmName = ''
with open(FILMDB) as f:
        cnt = 0
        for line in f.readlines():
            if cnt == bestFilm:
                bestFilmName = line.strip()
            cnt +=1

wikiData = requests.get('https://www.wikidata.org/w/api.php', {
    'action': 'wbgetentities',
    'titles': bestFilmName,
    'sites': 'enwiki',
    'props': '',
    'format': 'json'
}).json()
bestFilmUri = list(wikiData['entities'])[0]
print(bestFilmUri)

query = """SELECT ?filmLabel ?cost WHERE {
  ?film wdt:P31 wd:Q11424.
  ?film wdt:P2130 ?cost.
  ?selectedfilm wdt:P2130 ?selectedcost.
  filter(?selectedfilm= wd:"""+bestFilmUri+""" && ?cost> ?selectedcost)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
}
"""
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
sparqlResults = sparql.query().convert()
sparqlFilms = []
for result in sparqlResults["results"]["bindings"]:
    sparqlFilms.append(result["filmLabel"]["value"])

print(json.dumps({
    "User": ID,
    "1) Guessed Ratings": {"movie {}".format(k):v for k,v in filmRecommends.items()},
    "2) Recommended film": res2 + " - " + bestFilmName,
    "3) SPARQL Query": sparqlFilms
}, sort_keys=True, indent = 4))
