#%% Import Packages
import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px

#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Oscars Stats')



#%% Main App
appDetails = """
Created by: [Bogdan Tudose](https://www.linkedin.com/in/tudosebogdan/) \n
Date: Jan 29, 2024 \n
Purpose: Showcase Python dashboards with Streamlit package \n
From the left sidebar menu choose one of the pages:
- Oscar Nominees - View this year's and past year's nominations broken down by movie and category in an interactive bar chart. Categories can also be filtered in a dropdown.
- Past Oscar Winners - Interesting stats of past Oscar winners, including a chart of # of nominations vs # of awards.
- Best Picture Emoji Quiz - Just for fun quiz, match the emoji with the correct Best Picture Nominee. 
Article explaining the app: https://bit.ly/OscarsAppArticle
"""

st.title("🏆Oscars Stats🎥")
st.write(appDetails)
