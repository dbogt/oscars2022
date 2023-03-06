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
def grab_nominees():
    df = pd.read_csv("Oscars2022_Nominees.csv")
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
    urlBAFTA = "https://en.wikipedia.org/wiki/75th_British_Academy_Film_Awards"
    urlOSCARS = "https://en.wikipedia.org/wiki/94th_Academy_Awards"
    dfs = pd.read_html(urlBAFTA)
    baftas = dfs[2]
    dfs = pd.read_html(urlOSCARS)
    oscars = dfs[3]
    nominations = baftas.merge(oscars, how='outer',on=['Film'], suffixes=("_BAFTA","_OSCAR"))
    nominations = nominations.fillna(0)
    return nominations

    
def grab_predictions():
    db_content = db.fetch().items
    df = pd.DataFrame(db_content)
    df = df[cols]
    return df

#%% Import Data
nominees = grab_nominees() 
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

st.title("Best Picture Emoji Quiz")
correctAnswers = st.secrets["quizResults"]['quiz_answers']
st.write("Select the best picture nominee for each set of emojis.")
quizMode = st.radio('Quiz Difficulty',('Easy','Hard'))
answerOptions = ['Pick an answer'] + list(best_movies)
answerPicks = {}
col1, col2 = st.columns(2)
with col1:
    st.header("1. 🚫👀⬆️")
    st.header("2. 💾🚗")
    st.header("3. 🍬🍕")
    st.header("4. 🧭⬅📖")
    st.header("5. 🔔🏃🏼‍♀️")
    st.header("6. 🔌🐶")
    st.header("7. 👨‍💻🅰")
    st.header("8. 💤😱🎳")
    st.header("9. 🏜️🐛")
    st.header("10. 👑🎾")
with col2:    
    with st.form("quiz_form"):
        for x in range(1,11):
            if quizMode == "Easy":
                answerPicks[str(x)] = st.selectbox(str(x), answerOptions)
            else:
                answerPicks[str(x)] = st.text_input(str(x))

        submit_quiz = st.form_submit_button("Submit Answers")
        if submit_quiz:
            score = 0
            for x in range(1,11):
                if answerPicks[str(x)].strip().lower() == correctAnswers[x-1].strip().lower():
                    score+=1
            st.write("You correctly picked {} out of 10 movies.".format(score))
            if score < 3:
                st.write("We know it's COVID and you haven't gone to a movie theatre in ages, but have you been living under a rock?🗿")
            elif score < 6:
                st.write("Nice try, but you might want to text💬 a friend next time. Just don't do it during a movie.")
            elif score < 10:
                st.write("Wow, almost perfect! Are you a 🤢🍅 critic?")
            else:
                st.write("Whoa 100%! You are ready to host the Oscars! 🎤🎬🏆")
