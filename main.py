from os import write
import numpy as np
import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

st.set_page_config(layout="wide")


header = st.beta_container()
dataset = st.beta_container()

#load the data

page = requests.get("http://insideairbnb.com/get-the-data.html")
soup = BeautifulSoup(page.content, 'html.parser')
content = soup.find("div",{"class" : "contentContainer"})

place = content.find_all("h2")



# For US only
location_dict = defaultdict(list)
location = []

for i in range(len(place)):
    if (place[i].get_text().find('United States') != -1):
        
        loc = place[i].get_text().split(',')
        if len(loc) > 3:
            loc[0] = ','.join(loc[:-2])
            loc[1] = loc[-2]
            location.append(loc[:2])
        else:
            location.append(loc[:-1])


for city,state in location:
    location_dict[state].append(city)   




with header:
    st.markdown("<h1 style='text-align: center; color: black;'>Airbnb Housing Analysis</h1>", unsafe_allow_html=True)
    #st.title('Airbnb Housing Analysis')
    country_col, state_col, city_col = st.beta_columns(3)
    #st.sidebar.title("Select Location")
    country_col.subheader("Choose Country")
    state_col.subheader("Choose State")
    city_col.subheader("Choose City")
    country = country_col.selectbox("",["United States"])
    if country == 'United States':
        selected_state = state_col.selectbox('',list(location_dict.keys()))
        if selected_state in location_dict.keys():            
            selected_city = city_col.selectbox("", location_dict[selected_state])

selected_city = re.sub('[,]+',' ',selected_city) #remove comma
selected_city = re.sub('[.?!]+','',selected_city) #remove other punctuation
selected_city = re.sub('[ ]+','-',selected_city) #put hyphen in white spaces for getting the data
table = content.find('table', attrs={'class':f"table table-hover table-striped {selected_city.lower()}"})
table_body = table.find('tbody')

rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    link = cols[2].find('a').get('href')

    if link[-11:] == 'reviews.csv': #filtering links
        reviews_url = link
        #st.write(reviews_url)
        break

for row in rows:
    cols = row.find_all('td')
    link = cols[2].find('a').get('href')        
        
    if link[-12:] == 'listings.csv' :
        listings_url = link
        #st.write(listings_url)
        break

for row in rows:
    cols = row.find_all('td')
    link = cols[2].find('a').get('href')        
            
    if link[-18:] == 'neighbourhoods.csv' :
        neighbourhoods_url = link
        #st.write(neighbourhoods_url)
        break

        
# loac the csv data files       
    
@st.cache
def load_review_data(url):
    data = pd.read_csv(url)
    return data

@st.cache
def load_listings_data(url):
    data = pd.read_csv(url)
    return data

@st.cache
def load_neighbourhoods_data(url):
    data = pd.read_csv(url)
    return data

review_data = load_review_data(reviews_url)
listings_data = load_listings_data(listings_url)
#neighbourhoods_data = load_neighbourhoods_data(neighbourhoods_url)


# st.dataframe(review_data)
#st.dataframe(listings_data.columns)
#st.dataframe(neighbourhoods_data)



st.table(listings_data.groupby("room_type").price.mean().reset_index()\
.round(2).sort_values("price", ascending=False)\
.assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

st.subheader('Map of all listings')

st.map(listings_data)

