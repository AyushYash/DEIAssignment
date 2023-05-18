#!/usr/bin/env python
# coding: utf-8

# In[56]:


#importing necessary libraries
import pandas as pd
import requests
from slack_sdk import WebClient
import os
from datetime import datetime
import time


# In[85]:


#function to get the top 3 states with the highest number of COVID-19 deaths
def get_top_states(df):
    sorted_states = df.groupby('state')['deaths'].sum().reset_index()
    top_states = sorted_states.nlargest(3, 'deaths')
    return top_states.values.tolist()


# In[86]:


#function to format the Slack message
def format_slack_message(states, month, total_deaths):
    message = f"Top 3 states with the highest number of COVID-19 deaths for the month of {month}\n"
    message += f"Month - {month}\n"
    for i, (state_name, deaths) in enumerate(states):
        percentage = (deaths / total_deaths) * 100
        message += f"State #{i+1} ({state_name}) - {deaths} deaths, {percentage: .2f}% of total US deaths \n"
    message += f"\nTotal US Deaths: {total_deaths}"
    return message


# In[44]:


#sharePoint file URL
sharepoint_file_url = 'https://qure1-my.sharepoint.com/:x:/g/personal/karan_chilwal_qure_ai/EUWNL7AT7mBEp1ogB-M1mgoBkltB2MGCdO_HAjTo-uXYzQ?rtime=zdg9qdpW20g'


# In[20]:


#local file path to save the downloaded file
local_file_path = r'C:\Users\ayush\Documents\covid-19-state-level-data.xlsx'


# In[21]:


#download the file 
response = requests.get(sharepoint_file_url)
with open(local_file_path, 'wb') as file:
    file.write(response.content)


# In[80]:


#read the excel file
df = pd.read_excel(local_file_path, engine='openpyxl', names=['Index', 'date', 'state', 'fips', 'cases', 'deaths'], parse_dates=['date'])


# In[66]:


# Define the months for which we are posting messages
months = ['March', 'April', 'May', 'June']


# In[67]:


#define the interval between the messages (in seconds)
interval = 60


# In[90]:


for month in months:
    #filter data for the current month
    current_month = datetime.strptime(month, "%B").strftime("%B")
    month_data = df[df['date'].dt.month == datetime.strptime(month, "%B").month]
    
    #calculate the total deaths for the current month
    total_deaths = month_data['deaths'].sum()
    
    #Fetch the top states for the current month
    top_states = get_top_states(month_data)
    
    #format the slack message for the current month
    message= format_slack_message(top_states, current_month, total_deaths)
    
    #send the message to slack using the webhook
    webhook_url = 'https://hooks.slack.com/services/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'
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload)
    
    #check the response status
    if response.status_code == 200:
        print(f"Message sent successfully to Slack for {current_month}!")
    else:
        print(f"Error sending message to Slack for {current_month}: {response.text}")
        
    #Sleep for the specified time interval
    time.sleep(interval)


# In[ ]:




