#%% Import Packages
import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px

#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Oscars Predictions')

#%% Deta Database Connection
deta = Deta(st.secrets["project_key"])
db = deta.Base("oscar_bets_test")

cols = ['name','email','password','city','best_movie','best_director','best_actor','best_actress']
safeCols = cols.copy()
safeCols.remove('email')
safeCols.remove('password')

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

    
def grab_predictions():
    db_content = db.fetch().items
    df = pd.DataFrame(db_content)
    df = df[cols]
    return df

#%% Import Data
nominees = grab_nominees2023() 
df = grab_predictions()
emails = df['email'].to_list()

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

elif selectPage == "Oscar 2023 Predictions":
    st.title("Oscars 2023 Predictions")
    if st.checkbox('Make Predictions'):
        st.header("Predictions")
        st.write("Enter your predictions below")
        with st.form("my_picks"):
            st.write("Predictions Forms")
            user_name = st.text_input("Your name (First Last)")
            user_email = st.text_input("Your email")
            user_city = st.text_input("Your city")
            password = st.text_input("A 'safe word' to retrieve your picks (do NOT use a real password)", type="password")
            best_movie_pick = st.selectbox('What movie will win the best picture?',best_movies)
            best_director_pick = st.selectbox('Who will win best director?', best_directors)
            best_actor_pick = st.selectbox('Who will win the best actor?', best_actors)
            best_actress_pick = st.selectbox('Who will win the best actress?', best_actress)
            submit_btn = st.form_submit_button("Save Picks")

            if submit_btn:
                checkOK = True
                if user_email in emails:
                    currentUserDF = df[df['email'] == user_email] 
                    checkPass = currentUserDF.iloc[0]['password']
                    if checkPass != password:
                        checkOK= False

                if checkOK:
                    st.write("Thank you!")
                    st.balloons()
                    db.put({"name": user_name, "email": user_email, 'password':password,
                            'best_movie':best_movie_pick, 'best_director':best_director_pick,
                            'best_actor':best_actor_pick, 'best_actress':best_actress_pick,
                            'city':user_city, 'key':user_email})
                    df = grab_predictions()
                else:
                    st.write("Incorrect password, try again or submit with another email!")

    if st.checkbox('Show predictions by person'):
        safeDF = df[safeCols]
        adminPass = st.text_input('Admin Password',type="password")
        if adminPass == st.secrets['admin_pass']:
            st.dataframe(df)
        else:
            st.dataframe(safeDF)

    if st.checkbox('Show summary picks'):
        df['Count'] = 1
        summaryDict = {'Best Movie':'best_movie',
                        'Best Director':'best_director',
                        'Best Actor':'best_actor',
                        'Best Actress':'best_actress'}
        summaryPicks = st.multiselect("Pick categories to show",summaryDict.keys())
        outputType = st.radio('Output type',('Tables','Bar Charts'))
        for pick in summaryPicks:
            colName = summaryDict[pick]
            st.header(pick)
            if outputType == 'Tables':
                st.write(df[colName].value_counts())
            else:
                fig = px.bar(df, x=colName, y='Count', color="city", hover_name="name", barmode='stack', labels={colName:pick}).update_xaxes(categoryorder="total descending")
                st.plotly_chart(fig)
             
