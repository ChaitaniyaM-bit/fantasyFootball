#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


# In[3]:


# Using pro-football-reference 2023 Fantasy Football Data
# https://www.pro-football-reference.com/years/2023/fantasy.htm


# In[4]:


df = pd.read_csv(r'2023.csv')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
df.columns


# In[5]:


#Data Cleaning

#Dropping unneccessary columns

df.drop(['Rk', '2PM', '2PP', 'DKPt', 'FDPt', 'VBD', 'PosRank', 'OvRank', 'PPR', 'Fmb', 'GS'], axis=1, inplace=True)


# In[29]:


df.head()


# In[7]:


# Reformating the Player name column to remove  
# the * and + sometimes found after the player's name using a Lambda function

df['Player'] = df['Player'].apply(lambda x: x.split('*')[0])


# In[8]:


df.head()


# In[9]:


#Renaming cryptic values like TD, TD.1, TD.2, etc...

df.rename({
'TD': 'PassingTD',
'TD.1': 'RushingTD',
'TD.2': 'ReceivingTD',
'TD.3': 'TotalTD',
'Yds': 'PassingYDs',
'Yds.1': 'RushingYDs',
'Yds.2': 'ReceivingYDs',
'Att': 'PassingAtt',
'Att.1': 'RushingAtt'
}, axis=1, inplace=True)


# In[10]:


df.columns


# In[11]:


#Creating a separate DF for each position

rb_df = df[df['FantPos'] == 'RB']
qb_df = df[df['FantPos'] == 'QB']
wr_df = df[df['FantPos'] == 'WR']
te_df = df[df['FantPos'] == 'TE']


# In[12]:


# We can now assign relevant columns to the appropriate Dataframe
#For example, we don't want to measure passing statistics for wide receivers or runningbacks

rushingGroup = ['RushingAtt', 'RushingYDs', 'Y/A', 'RushingTD']
receivingGroup = ['Tgt', 'Rec', 'ReceivingYDs', 'Y/R', 'ReceivingTD']
passingGroup = ['PassingAtt', 'PassingYDs', 'PassingTD', 'Int', 'FantPt']

def transformColumns(df, newColumnList):
    df = df[['Player', 'Tm', 'Age', 'G'] + newColumnList + ['FL']]
    return df


# In[13]:


rb_df = transformColumns(rb_df, rushingGroup+receivingGroup)
wr_df = transformColumns(wr_df, rushingGroup+receivingGroup)
te_df = transformColumns(te_df, receivingGroup)
qb_df = transformColumns(qb_df, rushingGroup+passingGroup)


# In[30]:


qb_df.head()


# In[15]:


# I want to first take a look at the most important position 
# in football and the position that holds the most weight in Fantasy Football scoring - The Quarterback.
# The question: Is it better to select a "running Quarterback"? In other words, a quarterback that relies on his feet
# as much as he relies on his arm. 

#Since 2019, the overall QB1 in Fantasy Football has scored at least 4 rushing TDs and run for at least 350 yards every year


# In[16]:


#To help eliminate Outliers, we want to only look at starting QBs, these are usually QBs that play 75%
# of games in the regular season, as injuries will sideline most players for 3-4 games. 

qb_df_new = qb_df[qb_df['G'] >= 13]


# In[17]:


sns.set_style('whitegrid')

fig, ax = plt.subplots()
fig.set_size_inches(15, 10)

plot = sns.regplot(
x=qb_df_new['RushingYDs'],
y=qb_df_new['FantPt'],
scatter=True,)

plt.title('Quarterback Rushing Yds vs Total Fantasy Pts', fontdict=None, loc='center', pad=None)


# In[18]:


#The data shows weaker correlation between the amount of Rushing Yards by a QB and their total fantasy points throughout the season. 
#At first glance, we see QB's scoring 250+ Fantasy Points at all sorts of ranges of Rushing Yards. 
#This suggests that last years QBs class went against the historical norm of rushing QBs leading fantasy scoring.


# In[19]:


#Next we will take a look at the running back position to gauge what qualities result in higher fantasy points being scored


# In[20]:


#Calculating fantasy points scored in a full PPR league

rb_df['FantasyPoints'] = rb_df['RushingYDs']*0.1 + rb_df['RushingTD']*6 + rb_df['Rec'] 
+ rb_df['ReceivingYDs']*0.1 + rb_df ['ReceivingTD']*6 - rb_df['FL']*2


# In[21]:


#Create new column for Fantasy points per game.
rb_df['FantasyPoints/GM'] = rb_df['FantasyPoints']/rb_df['G']
rb_df['FantasyPoints/GM'] = rb_df['FantasyPoints/GM'].apply(lambda x: round(x, 2))


# In[22]:


#Create new column for usage per game. Usage is defined as # of targets + carries
rb_df['Usage/GM'] = (rb_df['RushingAtt'] + rb_df['Tgt'])/rb_df['G']

#round each row value to two decimal places
rb_df['Usage/GM'] = rb_df['Usage/GM'].apply(lambda x: round(x, 2))


# In[23]:


sns.set_style('whitegrid')

#create a canvas with matplotlib
fig, ax = plt.subplots()
fig.set_size_inches(15, 10)

#basic regression scatter plot with trendline
plot = sns.regplot(
x=rb_df['Usage/GM'],
y=rb_df['FantasyPoints/GM'],
scatter=True,)

plt.title('Running Back Usage vs Fantasy Pts/Game', fontdict=None, loc='center', pad=None)


# In[24]:


#As we see in this regression plot, a Running Back's usage is HIGHLY correlated with their fantasy points. 
#In short, we want a running back that is getting the ball often


# In[25]:


#Using the same sets of running back data, we can also quickly look at if efficiency matters
#A running back's efficiency is measured as the number of touchdowns they score per ball carry

#How does efficiency correlate to fantasy football performance?
rb_df['TD/Usage'] = (rb_df['RushingTD']+ rb_df['ReceivingTD'])/(rb_df['RushingAtt'] + rb_df['Tgt'])
fig, ax = plt.subplots()
fig.set_size_inches(15, 10)

rb_df = rb_df[rb_df['RushingAtt'] > 20]
plot = sns.regplot(
x=rb_df['TD/Usage'],
y=rb_df['FantasyPoints/GM'],
scatter=True)

plt.title('Running Back Efficiency vs Fantasy Pts/Game', fontdict=None, loc='center', pad=None)


# In[26]:


#As we can see here, the efficiency is hardly as correlated to their fantasy points as usage. 
#Meaning, we want to opt in for a runningback that is getting plenty of touches and is the go to running back on their team
#We do not wan to prioritize a runningback that is getting high touchdowns per carry


# In[ ]:




