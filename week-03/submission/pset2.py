import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from itertools import cycle, islice
%matplotlib inline


import datetime as dt
df = pd.read_csv('week-03/data/skyhook_2017-07.csv', sep=',')
df['date_new'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df['weekday'] = df['date_new'].apply(lambda x: x.weekday() + 1)
df['weekday'].replace(7, 0, inplace = True)

for i in range(0, 168, 24):
  j = range(0,168,1)[i - 5] #account for Eastern time (-5:00)
  if (j > i):
    df.drop(df[
    (df['weekday'] == (i/24)) &
    (
    ( (df['hour'] < j) & (df['hour'] > i + 18) ) |
    ( (df['hour'] > i + 18 ) & (df['hour'] < j) )
    )
    ].index, inplace = True)
  else:
    df.drop(df[
    (df['weekday'] == (i/24)) &
    (
    (df['hour'] < j) | (df['hour'] > i + 18 )
    )
    ].index, inplace = True)
#-----------------------------------------------------------
## Problem 1: Create a Bar Chart of Total Activity by Day
df.groupby('date')['count'].sum().plot.bar(title ="Total pings by date", figsize=(18, 6), color="#FFC39C").set(xlabel='Date', ylabel='Number of pings')
#-----------------------------------------------------------
## Problem 2: Modify the Hour Column
for i in range(0,168,24): #i is unadjusted Greenwich time (0:00)
    j = range(0,168,1)[i - 5] #adjusted to the Eastern time (-5:00) [ex. if i=0, j=163]
    if (j > i):
        df['hour_new'] = 23-(df['hour']%24) #loop back the iteration
    else:
        df['hour_new'] = df['hour']%24 #find a divmod when the iteration is not in the negative range
#-----------------------------------------------------------
## Problem 3: Create a Timestamp Column
from datetime import timedelta
df['timestamp'] = df['date_new'] + pd.to_timedelta(df['hour_new'], unit='h')
#-----------------------------------------------------------
## Problem 4: Create Two Line Charts of Activity by Hour
#line plot of total activity by timestamp--a line graph that displays the total number of GPS pings in each hour over the course of
df.groupby('timestamp')['count'].sum().plot(title ="Total Pings by Timestamp", figsize=(18,6), color="gray").set(xlabel='Timestamp', ylabel='Number of Pings')
#bar chart of summed counts by hours of the day
df.groupby('hour_new')['count'].sum().plot.bar(title ="Total pings by hour of day", figsize=(18, 6), color="#FFC39C").set(xlabel='Hour of day', ylabel='Number of pings')
#-----------------------------------------------------------
## Problem 5: Create a Shaded Scatterplot by activity
#Timeseries 1: 2017-07-03 (Monday), because it has the day with the highest number of pings.
#   This is the day before the 4th of July. However, because it is a holiday before the big party, we can see how people also use the parks/unusual routes more.
#   One highlight that shows up on this day specifically is the park near Forest Hill.
df170703 = df.loc[df['date'] == "2017-07-03"] #create a dataframe from the specific timeframe for scatter plot
#iterated from: Nehal J Wani's code found in https://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-object-to-dataframe
df170703_freq = df170703.groupby( ['lon','lat'] )['count'].sum().to_frame(name = 'count').reset_index() #create a new dataframe with count columns for
df170703_freq.plot.scatter(x='lon', y='lat', s=(df170703_freq['count']/150), title ="Total pings by location on July 3,2017", figsize=(10, 10), color='#FFC39C', edgecolor='black')

#Timeseries 2: 2017-07-06 (Thursday), because it has the highest peak in pings at a certain hour.
#   This time series not only shows a concentration of commute routes, but it is also an exception because it shows what seem to be an event up in Winthrop.
#   Two highlights from this scatter plot is the concentration of people using the I-93 and the event location itself.
df170706 = df.loc[df['date'] == "2017-07-06"] #create a dataframe from the specific timeframe for scatter plot
df170706_freq = df170706.groupby( ['lon','lat'] )['count'].sum().to_frame(name = 'count').reset_index() #create a new dataframe with count columns for
df170706_freq.plot.scatter(x='lon', y='lat', s=(df170706_freq['count']/150), title ="Total pings by location on July 6, 2017", figsize=(10, 10), color='#FFC39C', edgecolor='black')
#Timeseries 3: 2017-07-06 17:00:00, because it is the highest peak in pings at a certain hour.
#   It is interesting that the peak of pings occur only at 5PM, and there is nothing before or after the event.
#   Furthermore, because this data is aggregated at the hour level,it  also does not show how this large amount of people slowly disagregate into nearby areas.
df170706.groupby('timestamp')['count'].sum() #show that in the 17:00:00 hour, there is the peak in pings. It also resonates with end of work hour.
df170706_17 = df.loc[df['timestamp'] == pd.Timestamp('2017-07-06 17:00:00')] #create a dataframe from the specific timeframe for scatter plot
df170706_17_freq = df170706_17.groupby( ['lon','lat']  )['count'].sum().to_frame(name = 'count').reset_index() #create a new dataframe with count columns for
df170706_17_freq.plot.scatter(x='lon', y='lat', s=(df170706_17_freq['count']/150), title ="Total pings by location at 5pm of July 6, 2017", figsize=(10, 10), color='#FFC39C', edgecolor='black')
#Timeseries 4: 2017-07-06 19:00:00 -- two hours after the peak and the usual off work hour.
#   This hour in generally assumption shows a concentration in people's commute back home after work.
#   A highlight is on the concentration of people using the I-93 only towards the southern part of Boston and not the north.
df170706_19 = df.loc[df['timestamp'] == pd.Timestamp('2017-07-06 19:00:00')] #create a dataframe from the specific timeframe for scatter plot
df170706_19_freq = df170706_19.groupby( ['lon','lat']  )['count'].sum().to_frame(name = 'count').reset_index() #create a new dataframe with count columns for
df170706_19_freq.plot.scatter(x='lon', y='lat', s=(df170706_19_freq['count']/150), title ="Total pings by location at 7pm of July 6, 2017", figsize=(10, 10), color='#FFC39C', edgecolor='black')
#-----------------------------------------------------------
##Problem 6: Analyze Your (Very) Preliminary Findings
#(1) A phenomenon that the data make visible (for example, how location services are utilized over the course of a day and why this might be).
#   There are multiple phenomena which were described under each time series above. In comparison, the first two plots, which depict two different
#   types of days, there is an obvious concentration of people within the Boston downtown area on a "usual weekday" versus a more spatially distributed
#   population on a holiday.As for the last two plots, timing of commute shows an interesting behaviours: 1) people either tend to hang around Downtown
#   areas before going home, or 2) people's directions to their home may relate to the hours of work their jobs require.

#(2) A shortcoming in the completeness of the data that becomes obvious when it is visualized.
#   One shortcoming of this data is that it is recorded hourly and not at a smaller time scale. In a city such as Boston, where commutes are often in a
#   10-to-15-minute timeframe, hourly records, cannot explain the actual movements of people. This data can help show areas of traffic congestion, or
#   how large groups of people assemble and disassemble themselves.

#(3) How this data could help us identify vulnerabilities related to climate change in the greater Boston area.
#   The concentration of people using the I-93 shows a high vulnerability to climate change. As I-93 is very close to the coast, it is at higher climatic
#   risks for storms, sea level rise, etc. The vulnerability that accompanies it is the fact that a large population depends on this route with not a lot
#   of other interstate alternatives that can take on this mass. Thus, if climate change continues to grow more severe, the frequency of the cut off of I-93
#   will prevent many people to commute to work, which can affects their much needed income.
#-----------------------------------------------------------
