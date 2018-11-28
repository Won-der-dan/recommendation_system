#!/usr/bin/env python3
import operator
import json

"""
Скрипт для расчета оценок для заданного пользователя
"""

INFILE = 'data.csv'
OUTFILE = 'data-new.csv'
DAYFILE = 'context_day.csv'
PLACEFILE = 'context_place.csv'
ID = 9


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

    secondSum = secondSum ** 0.5
    thirdSum = thirdSum ** 0.5
    sim = round(firstSum / (secondSum * thirdSum), 3)
    similarity[user] = sim

del similarity[ID]
sorted_sim = sorted(similarity.items(), key=operator.itemgetter(1),
                    reverse=True)
sorted_sim = sorted_sim[0:7]

def avgRank(id : int):
    list = [x for x in userDict[id] if x != -1]
    return sum(list) / float(len(list))

filmRecommends = {}
for filmIndex, filmRate in enumerate(keyUserMovies):
    if filmRate == -1:
        firstSum = 0
        secondSum = 0
        for user, sim in sorted_sim:
            firstSum += sim*(userDict[user][filmIndex] - avgRank(user))
            secondSum += float(abs(sim))

        suggestedRank = avgRank(ID) + (firstSum/secondSum)

        # Применяем формулу для расчёта оценки фильма
        filmRecommends[filmIndex] = round(suggestedRank, 3)


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
        bestFilm = k

res2 = None
if bestFilm > -1:
    res2 = {
    "movie {}".format(bestFilm): maxV
    }

print(json.dumps({
    "user": ID,
    1: {"movie {}".format(k):v for k,v in filmRecommends.items()},
    2: res2
}, indent=4))
