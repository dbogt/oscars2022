#%% Import Packages
import streamlit as st
import pandas as pd 
import plotly.express as px

#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Oscars Predictions')


#%% Functions
@st.cache
def grab_nominees2023():
    df = pd.read_csv("Oscars2023_Nominees.csv",encoding='latin1')
    df['Count'] = 1
    df['Nominee Full'] = df.apply(lambda x: x['Nominee'] + " (" + x['Movie'] + ")", axis=1)
    return df

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

@st.cache
def oscars_vs_bafta():
    urlBAFTA = "https://en.wikipedia.org/wiki/76th_British_Academy_Film_Awards"
    urlOSCARS = "https://en.wikipedia.org/wiki/95th_Academy_Awards"
    dfs = pd.read_html(urlBAFTA)
    baftas = dfs[2]
    dfs = pd.read_html(urlOSCARS)
    oscars = dfs[4]
    nominations = baftas.merge(oscars, how='outer',on=['Film'], suffixes=("_BAFTA","_OSCAR"))
    nominations = nominations.fillna(0)
    return nominations

    

#%% Import Data
nominees = grab_nominees2023() 

#Nominees options for dropdowns
best_movies = nominees[nominees['Category']=='Best Picture']['Nominee'].drop_duplicates().sort_values()
best_directors = nominees[nominees['Category']=='Best Director']['Nominee Full'].drop_duplicates().sort_values()
best_actors = nominees[nominees['Category']=='Best Actor']['Nominee Full'].drop_duplicates().sort_values()
best_actress = nominees[nominees['Category']=='Best Actress']['Nominee Full'].drop_duplicates().sort_values()

#%% Main App
appDetails = """
Created by: [Bogdan Tudose](https://www.linkedin.com/in/tudosebogdan/) \n
Date: March 5, 2023 \n
Purpose: Showcase Python dashboards with Streamlit package \n
From the left sidebar menu choose one of the pages:
- Oscar 2023 Nominees - View this year's nominations broken down by movie and category in an interactive bar chart. Categories can also be filtered in a dropdown.
- Oscar 2023 Predictions - Make predictions for the top categories and compare your answers with other people around the world.
- Past Oscar Winners - Interesting stats of past Oscar winners, including a chart of # of nominations vs # of awards.
- Best Picture Emoji Quiz - Just for fun quiz, match the emoji with the correct Best Picture Nominee. 
Article explaining the app: https://bit.ly/OscarsAppArticle
"""
with st.expander("See app info"):
    st.write(appDetails)

selectPage = st.sidebar.selectbox("Select Page", ("Oscar 2023 Nominees", "Oscar 2023 Predictions"))

if selectPage == "Oscar 2023 Nominees":
    st.title("🏆Oscars 2023 Nominees🎥")
    nomineesFilter = nominees.copy()
    filterCategories = st.multiselect("Filter by category (leave blank to show all)", nominees['Category'].unique())
    if len(filterCategories)>0:
        nomineesFilter = nomineesFilter[nomineesFilter['Category'].isin(filterCategories)]
    nominationsOutput = st.radio('Output type',('Chart','Count Summary','Detailed Table'))
    if nominationsOutput == 'Detailed Table':
        st.header('Nominations Details')
        st.write(nomineesFilter)
    elif nominationsOutput == 'Count Summary':
        st.header("# of Nominations by Movie")
        st.write(nomineesFilter['Movie'].value_counts())
    else:
        st.header("Nominations Breakdown by Movie")
        figNom = px.bar(nomineesFilter, x='Movie', y='Count', color="Category", hover_name="Nominee", barmode='stack', height=600).update_xaxes(categoryorder="total descending")
        st.plotly_chart(figNom)
    st.header("Oscars vs BAFTA Nominations")
    nominations = oscars_vs_bafta()
    figOscVsBAFTA = px.strip(nominations, x='Nominations_OSCAR', y='Nominations_BAFTA',
                     hover_name='Film', title='2023 Oscar Nominations vs BAFTA Nominations')
    st.plotly_chart(figOscVsBAFTA) #strip plot creates a jitter plot (slightly offsets markers for overlaping pts)
    st.write(nominations)
             
