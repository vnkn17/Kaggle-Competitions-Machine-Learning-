import numpy as np
import pandas as pd
import csv
import itertools
import hashlib
from sklearn.metrics import mean_absolute_error
#from sklearn import kmeans
# Predict via the user-specific median.
# If the user has no data, use the global median.

user_file = 'profiles.csv'
train_file = 'train.csv'
test_file  = 'test.csv'
soln_file  = 'user_median.csv'

# Load the training data.
user_data = {}
train_data = {}
artist_data = {}
age_data = {}
sex_data = {}
country_data = {}
training_data = {}
artist_sex_data = {}

with open(user_file, 'r') as user_fh:
    user_csv = csv.reader(user_fh, delimiter=',', quotechar='"')
    #rows=[r for r in train_csv]
    next(user_csv, None)
    #for row in itertools.islice(train_csv, 0, 150000):
    for row in user_csv:
        user   = row[0]
        sex =    row[1]
        age  =   row[2]
        Country = row[3]
    
        if not user in user_data:
            user_data[user] = {}
        if(sex == 'f'):
            sex_data[user] = 1
        elif(sex == 'm'):
            sex_data[user] = 2
        else:
            sex_data[user] = 0
        #for x in sex_data:
        #    print sex_data[x]

            #for y in sex_data[x]:
            #    print sex_data[x][y]


with open(train_file, 'r') as train_fh:
    train_csv = csv.reader(train_fh, delimiter=',', quotechar='"')
    #rows=[r for r in train_csv]
    next(train_csv, None)
    #for row in itertools.islice(train_csv, 0, 150000):
    for row in train_csv:
        user   = row[0]
        artist = row[1]
        plays  = row[2]
    
        if not user in train_data:
            train_data[user] = {}
        if not artist in artist_data:
            artist_data[artist] = {}
        train_data[user][artist] = int(plays)
        artist_data[artist][user] = int(plays)
        training_data[user] = int(plays)
    """
    for x in train_data:
        print x
        for y in train_data[x]:
            print train_data[x][y]
    
"""
# Gender Medians

malemedian = 0
femalemedian = 0
malectr = 0
femalectr = 0
for user, gender in sex_data.iteritems():
    if training_data.has_key(user):
        if sex_data[user] == 2:
            malemedian += training_data[user]
            malectr = malectr+1
        elif sex_data[user] == 1:
            femalemedian += training_data[user]
            femalectr = femalectr+1
print malemedian/malectr
print femalemedian/femalectr

"""
# Age Medians

# Compute the global median and per-user median.
plays_array  = []
user_medians = {}
user_means = {}
print len(train_data)
for user, user_data in train_data.iteritems():
    user_plays = []
    for artist, plays in user_data.iteritems():
        plays_array.append(plays)
        user_plays.append(plays)
    user_medians[user] = np.median(np.array(user_plays))
    user_means[user] = np.mean(np.array(user_plays))
global_median = np.median(np.array(plays_array))
print global_median
print np.mean(np.array(plays_array))
artist_plays = []
artist_medians = {}
for artist, art_data in artist_data.iteritems():
    artist_plays = []
    for user, plays in art_data.iteritems():
        artist_plays.append(plays)
    artist_medians[artist] =  np.median(np.array(artist_plays))
# Cross - Validation .

# Write out test solutions.
"""
median = 0
with open(test_file, 'r') as test_fh:
    test_csv = csv.reader(test_fh, delimiter=',', quotechar='"')
    next(test_csv, None)

    with open(soln_file, 'w') as soln_fh:
        soln_csv = csv.writer(soln_fh,
                              delimiter=',',
                              quotechar='"',
                              quoting=csv.QUOTE_MINIMAL)
        soln_csv.writerow(['Id', 'plays'])

        for row in test_csv:
            id     = row[0]
            user   = row[1]
            artist = row[2]
            # Calculate a likelihood profile for a given user.

            if user in user_medians and artist in artist_medians:
                median = (user_medians[user] + user_means[user])/2 * np.power(artist_medians[artist]/global_median,.3) 
                soln_csv.writerow([id, median])
            elif user in user_medians:
                soln_csv.writerow([id, user_medians[user]])
            else:
                print "User", id, "not in training data."
                soln_csv.writerow([id, global_median])
"""
ctr = 0
sum = 0

#min = 300
#for i in xrange(200, 500, 10):
with open(train_file, 'r') as train_test_fh:
    train_test_csv = csv.reader(train_test_fh, delimiter=',', quotechar='"')
    next(train_test_csv, None)
    #for row in itertools.islice(train_test_csv, 150000, None):
    for row in train_test_csv:
        ctr = ctr + 1
        user   = row[0]
        artist = row[1]
        plays = row[2]
        if user in user_medians and artist in artist_medians:
            median = user_medians[user] * np.power(artist_medians[artist]/global_median, .23)
            #float(i)/1000
        sum += np.absolute(median - int(plays))
    #if(sum/ctr < min):
    #    min = sum/ctr
        
print sum/ctr


