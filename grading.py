import operator

"""
Скрипт для расчета оценок для заданного пользователя
"""

INFILE = 'data.csv'
OUTFILE = 'data-new.csv'
ID = 9


x = {}
userDict = dict()
with open(INFILE) as data:
    data.readline()
    for line in data:
        x = line.split(', ')
        x.append(x.pop().strip())
        userDict[int(x[0].replace("User ", ""))] = x[1::]
        #print(userDict[x[0]])
#print(userDict)
for user in userDict:
    userDict[user] = list(map(int, userDict[user]))
    #print(user)

keyUserMovies = userDict[ID]
moviesCount = len(keyUserMovies)

similarity = {}
for user in userDict:
    similarMovies = list()
    userMovies = userDict[user]
    for i in range(1, moviesCount):
            #print(i)
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
sorted_sim = sorted(similarity.items(), key=operator.itemgetter(1), reverse=True)
sorted_sim.remove((ID, 1))
sorted_sim = sorted_sim[0:7:]
print(sorted_sim)

def avgRank(id : int):
    list = userDict[id]
    list = [x for x in list if x != -1]
    return sum(list) / float(len(list))

count = 0
for i in userDict[ID]:
    count += 1
    if i == -1:
        firstSum = 0
        secondSum = 0
        for user in sorted_sim:
            userRanks = userDict[user[0]]
            firstSum += user[1]*(userRanks[count-1] - avgRank(user[0]))
            secondSum += abs(user[1])
        suggestedRank = round(avgRank(ID) + (firstSum/secondSum), 3)
        keyUserMovies[count-1] = suggestedRank

print(keyUserMovies)
