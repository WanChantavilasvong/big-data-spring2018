import json
import time
import threading
from datetime import datetime
import tweepy
import jsonpickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline
import os
os.chdir('week-04')

#Import keys from the python file
from twitter_keys import api_key, api_secret

#Twitter authenticator with rate limit function
def auth(key, secret):
  auth = tweepy.AppAuthHandler(key, secret)
  api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
  # Print error and exit if there is an authentication error
  if (not api):
      print ("Can't Authenticate")
      sys.exit(-1)
  else:
      return api
api = auth(api_key, api_secret)

#Parser
def parse_tweet(tweet):
    p = pd.Series()
    if tweet.coordinates != None:
        p['lat'] = tweet.coordinates['coordinates'][0]
        p['lon'] = tweet.coordinates['coordinates'][1]
    else:
        p['lat'] = None
        p['lon'] = None
    p['location'] = tweet.user.location
    p['id'] = tweet.id_str
    p['content'] = tweet.text
    p['user'] = tweet.user.screen_name
    p['user_id'] = tweet.user.id_str
    p['time'] = str(tweet.created_at)
    return p
#Scraper (parser embedded) - modified from Bhaskar Karambelkar (https://www.karambelkar.info/2015/01/how-to-use-twitters-search-rest-api-most-effectively./)
def get_tweets(geo, out_file, search_term = '', tweet_per_query = 100, tweet_max = 150, since_id = None, max_id = -1, write = False):
    tweet_count = 0
    all_tweets = pd.DataFrame()
    while tweet_count < tweet_max:
        try:
            if (max_id <= 0):
                if (not since_id):
                    new_tweets = api.search(q = search_term, rpp = tweet_per_query, geocode = geo)
                else:
                    new_tweets = api.search(q = search_term, rpp = tweet_per_query, geocode = geo, since_id = since_id)
            else:
                if (not since_id):
                    new_tweets = api.search(q = search_term, rpp = tweet_per_query, geocode = geo, max_id = str(max_id - 1))
                else:
                    new_tweets = api.search(q = search_term, rpp = tweet_per_query, geocode = geo, max_id = str(max_id - 1), since_id = since_id)
            if (not new_tweets):
                print("No more tweets found")
                break
            for tweet in new_tweets:
                all_tweets = all_tweets.append(parse_tweet(tweet), ignore_index = True)
            max_id = new_tweets[-1].id
            tweet_count += len(new_tweets)
        except tweepy.TweepError as e: # exit if any error
            print("Error : " + str(e))
            break
    print (f"Downloaded {tweet_count} tweets.")
    if write == True:
        all_tweets.to_json(out_file)
    return all_tweets

#-----------------------------------------------------------
##STEP 1
#Set variables and run the scraper with an output 'tweets.json'
latlng = '42.359416,-71.093993' # set a lat lng
radius = '5mi' # set search distance
geocode_query = latlng + ',' + radius # see tweepy API reference for format specifications
file_name = 'data/tweets.json' # set output file location
t_max = 80000 # set threshold number of Tweets. Note that it's possible to get more than one
get_tweets(geo = geocode_query, tweet_max = t_max, write = True, out_file = file_name)

#----------------------------
##SUB-STEP: Reading in json file
tweets = pd.read_json('data/tweets.json')
tweets.shape

#----------------------------
##SUB-STEP: Cleaning Data
#Clean out tweets without location values
tweets = tweets[tweets['location'] != '']
tweets = tweets[tweets['location'] != ' ']
tweets = tweets[tweets['location'] != '  ']
len(tweets)

#Clean duplicates
tweets.drop_duplicates(subset = 'content', keep = False, inplace = True)
len(tweets)

#Clean location names
#Boston, MA
tweets_cln = tweets[tweets['location'].str.contains("Boston")]['location']
tweets_cln = tweets[tweets['location'].str.contains("boston")]['location']
tweets_cln = tweets[tweets['location'].str.contains("BOSTON")]['location']
tweets_cln = tweets[tweets['location'].str.contains("BOS")]['location']
tweets_cln = tweets[tweets['location'].str.contains("Roxbury")]['location']
tweets_cln = tweets[tweets['location'].str.contains("Allston")]['location']
tweets_cln = tweets[tweets['location'].str.contains("Dorchester")]['location']
tweets['location'].replace(tweets_cln, 'Boston, MA', inplace = True)

#Cambridge, MA
tweets_cln = tweets[tweets['location'].str.contains("Cambridge")]['location']
tweets_cln = tweets[tweets['location'].str.contains("cambridge")]['location']
tweets_cln = tweets[tweets['location'].str.contains("CAMBRIDGE")]['location']
tweets['location'].replace(tweets_cln, 'Cambridge, MA', inplace = True)

#Sommerville, MA
tweets_cln = tweets[tweets['location'].str.contains("Somerville")]['location']
tweets_cln = tweets[tweets['location'].str.contains("somerville")]['location']
tweets['location'].replace(tweets_cln, 'Somerville, MA', inplace = True)

#Brookline, MA
tweets_cln = tweets[tweets['location'].str.contains("Brookline")]['location']
tweets_cln = tweets[tweets['location'].str.contains("brookline")]['location']
tweets['location'].replace(tweets_cln, 'Brookline, MA', inplace = True)

#Malden, MA
tweets_cln = tweets[tweets['location'].str.contains("Malden")]['location']
tweets['location'].replace(tweets_cln, 'Malden, MA', inplace = True)

#Medford, MA
tweets_cln = tweets[tweets['location'].str.contains("Medford")]['location']
tweets['location'].replace(tweets_cln, 'Medford, MA', inplace = True)

#Everett, MA
tweets_cln = tweets[tweets['location'].str.contains("Everett")]['location']
tweets['location'].replace(tweets_cln, 'Everett, MA', inplace = True)

#Chelsea, MA
tweets_cln = tweets[tweets['location'].str.contains("Chelsea")]['location']
tweets['location'].replace(tweets_cln, 'Chelsea, MA', inplace = True)

#Others that are none of the above
tweets_cln = tweets[
    (tweets['location'] != 'Boston, MA') &
    (tweets['location'] != 'Cambridge, MA') &
    (tweets['location'] != 'Somerville, MA') &
    (tweets['location'] != 'Brookline, MA') &
    (tweets['location'] != 'Malden, MA') &
    (tweets['location'] != 'Medford, MA') &
    (tweets['location'] != 'Everett, MA') &
    (tweets['location'] != 'Chelsea, MA')
    ]['location']
tweets['location'].replace(tweets_cln, 'Others', inplace = True)

#Number checks while cleaning
tweets_cln
len(tweets_cln)
len(tweets['location'].unique())
len(tweets)

#-----------------------------------------------------------
##STEP 2: Pie chart of user-defined locations
#Count data
count_tweets = tweets.groupby('location')['id'].count().sort_values().to_frame(name = 'count')
count_tweets

#Create pie chart
#control font size for legibility, original source link: https://stackoverflow.com/questions/7082345/how-to-set-the-labels-size-on-a-pie-chart-in-python
plt.rcParams['font.size'] = 7

#color and code, original source link link: https://stackoverflow.com/questions/35488666/matplotlib-pandas-pie-chart-label-mistakes
colors = ['#191970','#001CF0','#0038E2','#0055D4','#0071C6','#008DB8','#00AAAA','#00C69C','#00E28E','#00FF80']
fig = plt.figure(figsize=[10, 10])
ax = fig.add_subplot(111)
explode = (0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 0, 0)
ax.pie(count_tweets['count'], labels= count_tweets.index.get_values(), labeldistance=1.05, shadow=False, colors=colors, explode=explode)
ax.axis('equal')
ax.set_title('Proportions of tweets by user-defined locations')
plt.tight_layout()
plt.show()

#-----------------------------------------------------------
##STEP 3: Scatter plot from lat lon
'''grading note: bringing in csv to view scatterplot and look at cleaned data'''
tweets = pd.read_csv('/Users/phoebe/Dropbox (MIT)/big-data/data/pset3_CSVs/Chantavilasvong, Wan/36741619-tweets_data.csv')
tweets.head()
np.shape(tweets)
tweets['location'].unique()
tweets['lon'].unique()
tweets['lat'].unique()

''' wan, it looks like your code below is not working because your dataset has some lat and lon values that are not actually lats or lons. in the lon data, you seem to have some dates and in the lat data, you seem to have some locations (e.g. Boston, MA). this may have happened during the parsing stage. your code looks correct below, but i have to deduct some points since i'm unable to run it with the data as is. - phoebe'''

#Check number of rows with coordinates
tweets_geo = tweets[tweets['lon'].notnull() & tweets['lat'].notnull()]
len(tweets_geo)
#Create a new dataframe with 3 columns: lon, lat, and count of the same coordinates
tweets_geo = tweets_geo.groupby(['lon','lat'])['id'].count().to_frame(name = 'count').reset_index()
#create a new dataframe with count columns for
#Scatter plot with dot size as the count variable
tweets_geo.plot.scatter(x='lon', y='lat', s=(tweets_geo['count']*20), title ="Amount of tweets by geographic location", figsize=(10, 10), color='black', edgecolor='white').set(xlabel='Longitude', ylabel='Latitude')

#----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------
##STEP 4: Collect tweets containing search term "flood".
#Set variables and run the scraper with an output 'flood.json'
latlng = '42.359416,-71.093993' # set a lat lng
radius = '5mi' # set search distance
geocode_query = latlng + ',' + radius # see tweepy API reference for format specifications
file_name = 'data/flood.json' # set output file location
t_max = 2000 # set threshold number of Tweets. Note that it's possible to get more than one
get_tweets(geo = geocode_query, search_term = 'flood', tweet_max = t_max, write = True, out_file = file_name)

#----------------------------
##SUB-STEP: Reading in json file
flood = pd.read_json('data/flood.json')
flood.shape

#-----------------------------------------------------------
##STEP 5: Clean the search term data as with the previous data.
#Clean out tweets without location values
flood = flood[flood['location'] != '']
flood = flood[flood['location'] != ' ']
len(flood)

#Clean duplicates
flood.drop_duplicates(subset = 'content', keep = False, inplace = True)
len(flood)

#Clean location names
#Boston, MA
flood_cln = flood[flood['location'].str.contains("Boston")]['location']
flood_cln = flood[flood['location'].str.contains("boston")]['location']
flood_cln = flood[flood['location'].str.contains("BOSTON")]['location']
flood_cln = flood[flood['location'].str.contains("Roxbury")]['location']
flood_cln = flood[flood['location'].str.contains("Dorchester")]['location']
flood['location'].replace(flood_cln, 'Boston, MA', inplace = True)

#Cambridge, MA
flood_cln = flood[flood['location'].str.contains("Cambridge")]['location']
flood['location'].replace(flood_cln, 'Cambridge, MA', inplace = True)

#Sommerville, MA
flood_cln = flood[flood['location'].str.contains("Somerville")]['location']
flood_cln = flood[flood['location'].str.contains("somerville")]['location']
flood['location'].replace(flood_cln, 'Somerville, MA', inplace = True)

#Others that are none of the above
flood_cln = flood[
    (flood['location'] != 'Boston, MA') &
    (flood['location'] != 'Cambridge, MA') &
    (flood['location'] != 'Somerville, MA')
    ]['location']
flood['location'].replace(flood_cln, 'Others', inplace = True)

#Number checks while cleaning
flood['location'].unique()
len(flood_cln)
len(flood['location'].unique())
len(flood)

#-----------------------------
##SUBSTEP: Pie chart of user-defined locations
#Count data
count_flood = flood.groupby('location')['id'].count().sort_values().to_frame(name = 'count')
count_flood

#Create pie chart
#control font size for legibility, original source link: https://stackoverflow.com/questions/7082345/how-to-set-the-labels-size-on-a-pie-chart-in-python
plt.rcParams['font.size'] = 8
#color and code, original source link link: https://stackoverflow.com/questions/35488666/matplotlib-pandas-pie-chart-label-mistakes
colors = ['#0071C6','#008DB8','#00AAAA','#00C69C']
fig = plt.figure(figsize=[7, 7])
ax = fig.add_subplot(111)
ax.pie(count_flood['count'], labels= count_flood.index.get_values(), labeldistance=1.05, shadow=False, colors=colors, autopct='%1.1f%%')
ax.axis('equal')
ax.set_title("Proportions of tweets containing 'flood' by user-defined locations")
plt.tight_layout()
plt.show()

#-----------------------------------------------------------
##STEP 6: Scatter plot from available lat lon
'''grading note: bringing in csv to view scatterplot and look at cleaned data'''
flood = pd.read_csv('/Users/phoebe/Dropbox (MIT)/big-data/data/pset3_CSVs/Chantavilasvong, Wan/36741597-flood_data.csv')
flood.head()
np.shape(flood)
flood['location'].unique()
flood['lon'].unique()

#Check number of rows with coordinates
flood_geo = flood[flood['lon'].notnull() & flood['lat'].notnull()]
len(flood_geo)

#Create a new dataframe with 3 columns: lon, lat, and count of the same coordinates
flood_geo = flood_geo.groupby(['lon','lat'])['id'].count().to_frame(name = 'count').reset_index() #create a new dataframe with count columns for
#Scatter plot with dot size as the count variable
flood_geo.plot.scatter(x='lon', y='lat', s=(flood_geo['count']*10), title ="Amount of tweets containing 'flood' by geographic location", figsize=(10, 10), color='black').set(xlabel='Longitude', ylabel='Latitude')

#-----------------------------------------------------------
##STEP 7: Export to csv
tweets.to_csv('tweets_data.csv', sep=',', encoding='utf-8')
flood.to_csv('flood_data.csv', sep=',', encoding='utf-8')
