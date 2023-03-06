#%% Import Packages
import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px

#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Past Oscar Winners')


#%% Functions
def fixFootnotes(messyNum):
    messyNum = str(messyNum)
    if "(" in messyNum:
        messyNum = messyNum.split("(")[0].strip()
    elif "[" in messyNum:
        messyNum = messyNum.split("[")[0].strip()
    clean = int(messyNum)
    return clean

@st.cache
def grab_past_winners():
    url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
    dfs = pd.read_html(url)
    df = dfs[0]
    df['Awards'] = df['Awards'].apply(fixFootnotes)
    df['Nominations'] = df['Nominations'].apply(fixFootnotes)
    return df

#%% Main App
appDetails = """
Created by: [Bogdan Tudose](https://www.linkedin.com/in/tudosebogdan/) \n
Date: Feb 12, 2022 \n
Purpose: Showcase Python dashboards with Streamlit package \n
From the left sidebar menu choose one of the pages:
- Oscar 2022 Nominees - View this year's nominations broken down by movie and category in an interactive bar chart. Categories can also be filtered in a dropdown.
- Oscar 2022 Predictions - Make predictions for the top categories and compare your answers with other people around the world.
- Past Oscar Winners - Interesting stats of past Oscar winners, including a chart of # of nominations vs # of awards.
- Best Picture Emoji Quiz - Just for fun quiz, match the emoji with the correct Best Picture Nominee. 
Article explaining the app: https://bit.ly/OscarsAppArticle
"""
with st.expander("See app info"):
    st.write(appDetails)

st.title("Past Oscar Winners")
aLinks = '''Live source from: <a href="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films" target="_blank">https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films</a><br>'''
st.markdown(aLinks, unsafe_allow_html=True)
pastWinnersDF = grab_past_winners()
figPastWinners = px.scatter(pastWinnersDF, x='Nominations', y='Awards',
               color='Year', hover_name='Film', title='Nominations vs Awards')
figPastWinnersJitter = px.strip(pastWinnersDF, x='Nominations', y='Awards',
               color='Year', hover_name='Film', title='Nominations vs Awards')

st.plotly_chart(figPastWinnersJitter) #strip plot creates a jitter plot (slightly offsets markers for overlaping pts)
st.write(pastWinnersDF)
