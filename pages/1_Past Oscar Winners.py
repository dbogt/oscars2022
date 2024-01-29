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

def grab_other_awards():
    df = pd.read_excel("oscars comparison to sag.xlsx", sheet_name=1, header=3)
    df2 = pd.read_excel("oscars comparison to sag.xlsx", sheet_name=0, header=2, nrows=5)
    return df, df2


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

pastWinnersDF = grab_past_winners()
otherAwardsDF, summaryDF = grab_other_awards()

st.title("Past Oscar Winners")
selectPage = st.sidebar.selectbox("Select Page", ("Nominations vs Awards", "Oscars vs Other Awards"))
if selectPage == "Nominations vs Awards":
    aLinks = '''Live source from: <a href="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films" target="_blank">https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films</a><br>'''
    st.markdown(aLinks, unsafe_allow_html=True)
    
    figPastWinners = px.scatter(pastWinnersDF, x='Nominations', y='Awards',
                   color='Year', hover_name='Film', title='Nominations vs Awards')
    figPastWinnersJitter = px.strip(pastWinnersDF, x='Nominations', y='Awards',
                   color='Year', hover_name='Film', title='Nominations vs Awards')
    
    st.plotly_chart(figPastWinnersJitter) #strip plot creates a jitter plot (slightly offsets markers for overlaping pts)
    st.write(pastWinnersDF)
else:
    st.header("Oscars vs Other Awards")
    awardsDetails = """
    Sources and details of other awards:
    - SAG - <a href="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films" target="_blank">Screen Actors Guild Awards</a>: Awarded since 1995, overlaps in 5 major categories with Osacars (best leading and supporting actor/actress, best picture). Categories can also be filtered in a dropdown.
    - BAFTA - <a href="https://en.wikipedia.org/wiki/British_Academy_Film_Awards" target="_blank">British Academy Film Awards</a>: Similar categories to Oscars, but more focus on international films. Much lower correlations to Oscars than the SAG awards.
    - PGA - <a href="https://en.wikipedia.org/wiki/Producers_Guild_of_America_Awards" target="_blank">Producters Guild of America Awards</a>: Awarded since 1990, overlaps in 3 major categories with Osacars (producer for Best Picutre, Best Animated, Best Documentary). Analysis below only shown for Best Picture.
    - DGA - <a href="https://en.wikipedia.org/wiki/Directors_Guild_of_America_Award_for_Outstanding_Directing_%E2%80%93_Feature_Film" target="_blank">Directors Guild of America Award</a>: Great predictor to Oscars Best Director. Used here to compare for Best Picture.
    """
    st.markdown(awardsDetails, unsafe_allow_html=True)
    st.write(summaryDF)
    st.write(otherAwardsDF)
