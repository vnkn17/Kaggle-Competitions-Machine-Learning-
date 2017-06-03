import numpy as np
import csv
from sklearn.metrics import mean_absolute_error
import requests
import json
import time
import random
from sklearn.cluster import KMeans
# Predict via the user-specific median.
# If the user has no data, use the global median.

train_file = 'train.csv'
artist_file = 'artists.csv'
test_file  = 'test.csv'
soln_file  = 'user_median.csv'
tags_file = 'tags.csv'
janksoln_file = 'jank.csv'

tags_dct = {}
classes = {}

with open(artist_file, 'r') as artist_fh:
    artist_csv = csv.reader(artist_fh, delimiter=',', quotechar='"')
    next(artist_csv, None)
    counter = 0
    for row in artist_csv:
        artist = row[0]
        # print(artist)
        response = requests.get("http://musicbrainz.org/ws/2/artist/" + artist + "?inc=tags&fmt=json")
        if 'tags' not in response.content:
            time.sleep(.5)
            continue
        lst = json.loads(response.content)["tags"]
        c = []
        for i in lst:
            if i['name'] == 'rock' or 'punk rock' or 'metal' or 'psychedelic rock' or 'rock and roll':
                c.append(0)
            if i['name'] == 'pop' or 'pop and chart':
                c.append(1)
            if i['name'] == 'contemporary r&b' or 'r&b' or 'rhythm & blues' or 'soul' or 'rnb':
                c.append(2)
            if i['name'] == 'electronica' or 'electronic' or 'electro pop':
                c.append(3)
            if i['name'] == 'indie' or 'alternative':
                c.append(4)
            if i['name'] == 'country-pop' or 'country':
                c.append(5)
            if i['name'] == 'rap' or 'hip hop':
                c.append(6)
            if i['name'] == 'orchestral' or 'classical' or 'instrumental':
                c.append(7)
            if i['name'] == 'european' or 'finnish' or 'german' or 'norwegian':
                c.append(8)
            if i['name'] == 'jazz' or 'blues':
                c.append(9)
        if c == []:
            c.append(10)
        # print c
        # c = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        classes[artist] = random.choice(c)
        if (counter % 100 == 0):
            print tags_dct
        counter+=1
        time.sleep(.75)

# Load the training data.
print("Loading training data.")
train_data = {}
artist_data = {}
with open(train_file, 'r') as train_fh:
    train_csv = csv.reader(train_fh, delimiter=',', quotechar='"')
    next(train_csv, None)
    for row in train_csv:
        user   = row[0]
        artist = row[1]
        plays  = row[2]
    
        if not user in train_data:
            train_data[user] = {}
        if not artist in train_data:
            artist_data[artist] = {}
        train_data[user][artist] = int(plays)
        artist_data[artist][user] = int(plays)

print("Calculating artist median.")
artist_plays = []
artist_medians = {}
for artist, art_data in artist_data.iteritems():
    artist_plays = []
    for user, plays in art_data.iteritems():
        artist_plays.append(plays)
    artist_medians[artist] =  np.median(np.array(artist_plays))


# Compute the global median and per-user median.
plays_array  = []
user_medians = {}
users_k = {}
v_cluster = np.zeros((len(train_data), 11))
user_ids = {}
val_dict = {}

# Compute the global median and per-user median.
plays_array  = []
user_medians = {}
for user, user_data in train_data.iteritems():
    user_plays = []
    for artist, plays in user_data.iteritems():
        plays_array.append(plays)
        user_plays.append(plays)

    user_medians[user] = np.median(np.array(user_plays))
global_median = np.median(np.array(plays_array))


print("Creating k-vectors")
usercounter = 0
for user, user_data in train_data.iteritems():
    user_ids[user] = (usercounter, 0)
    user_plays = []
    master = [[], [], [], [], [], [], [], [], [], [], []]
    for artist, plays in user_data.iteritems():
        # number of times they played it / artist median and average those values
        master[classes[artist]].append(plays * 1.0 / artist_medians[artist])
        # print classes[artist]
    val = 0
    # print master
    for cl in range(11):
        if (master[cl] == []):
            if not user in users_k:
                users_k[user] = {} 
            users_k[user][cl] = 0
        else:
            if not user in users_k:
                users_k[user] = {}
            users_k[user][cl] = np.mean(np.array(master[cl]))
        val += users_k[user][cl]
    val_dict[user] = val
    for cl in range(11):    
        v_cluster[usercounter][cl] = users_k[user][cl] / val
    usercounter+=1
# print v_cluster


clusters = [[], [], [], [], []]
centroids = []
print("Running K-Means.")
k = KMeans(n_clusters=5)
kmeans = k.fit(v_cluster)
pred = kmeans.predict(v_cluster)
for user, user_data in train_data.iteritems():
    user_ids[user] = (user_ids[user][0], pred[user_ids[user][0]])
    clusters[user_ids[user][1]].append(v_cluster[user_ids[user][0]])
for lst in clusters:
    centroids.append(np.mean(np.array(lst), axis=0))
print centroids


# Cross - Validation .


# Write out test solutions.
with open(test_file, 'r') as test_fh:
    test_csv = csv.reader(test_fh, delimiter=',', quotechar='"')
    next(test_csv, None)

    with open(janksoln_file, 'w') as janksoln_fh:
        janksoln_csv = csv.writer(janksoln_fh,
                              delimiter=',',
                              quotechar='"',
                              quoting=csv.QUOTE_MINIMAL)
        janksoln_csv.writerow(['Id', 'plays'])

        for row in test_csv:
            id     = row[0]
            user   = row[1]
            artist = row[2]

            pred_k = centroids[user_ids[user][1]] * val_dict[user]
            # print pred_k
            k = pred_k[classes[artist]]

            if k / val_dict[user] < .001 or classes[artist] == 10:
                if user in user_medians and artist in artist_medians:
                    median = user_medians[user] * np.power(artist_medians[artist]/global_median,.3) 
                    janksoln_csv.writerow([id, median])
                elif user in user_medians:
                    janksoln_csv.writerow([id, user_medians[user]])
                else:
                    print "User", id, "not in training data."
                    janksoln_csv.writerow([id, global_median])
            else:
                if user in user_medians and artist in artist_medians:
                    janksoln_csv.writerow([id, np.power(k, 0.3) * artist_medians[artist] * .15 + 
                    user_medians[user] * np.power(artist_medians[artist]/global_median,.16) * .85])
                elif user in user_medians:
                    janksoln_csv.writerow([id, user_medians[user]])
                else:
                    print "User", id, "not in training data."
                    janksoln_csv.writerow([id, global_median])




