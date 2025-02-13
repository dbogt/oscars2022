#%% Import Packages
import streamlit as st
import pandas as pd 
import plotly.express as px
import oscarUDFs as osc

#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Oscars 2024')


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


#%% Pick Year
year = st.sidebar.selectbox("Select Year", ('2024','2023','2022'))
csvs = {'2022': "Oscars2022_Nominees.csv", '2023':"Oscars2023_Nominees.csv", '2024':"Oscars2024_Nominees.csv" }
baftas = {'2022':'75th', '2023':'76th', '2024':'77th'}
oscars = {'2022':'94th', '2023':'95th', '2024':'96th'} 

#%% Data
csv = csvs[year]
urlBAFTA = f"https://en.wikipedia.org/wiki/{baftas[year]}_British_Academy_Film_Awards"
urlOSCARS = f"https://en.wikipedia.org/wiki/{oscars[year]}_Academy_Awards"

st.sidebar.write(urlBAFTA)
st.sidebar.write(urlOSCARS)

#%% Import Data
nominees = osc.grab_nominees(csv) 
nominations = osc.oscars_vs_bafta(urlBAFTA, urlOSCARS)
# st.write(nominees)
selectPage = st.sidebar.selectbox("Select Page", ("Oscars Nominees", "Oscars vs BAFTA"))

if selectPage == "Oscars Nominees":
    st.title(f"🏆Oscars {year} Nominees🎥")
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
elif selectPage == "Oscars vs BAFTA":
    st.header("Oscars vs BAFTA Nominations")
    figOscVsBAFTA = px.strip(nominations, x='Nominations_OSCAR', y='Nominations_BAFTA',
                     hover_name='Film', title=f'{year} Oscar Nominations vs BAFTA Nominations')
    st.plotly_chart(figOscVsBAFTA) #strip plot creates a jitter plot (slightly offsets markers for overlaping pts)
    st.write(nominations)
