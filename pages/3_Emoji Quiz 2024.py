#%% Import Packages
import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px
import oscarUDFs as osc


#%% Streamlit Config Settings
st.set_page_config(layout="wide",page_title='Best Picture Emoji Quiz 2024')

csv = "Oscars2024_Nominees.csv"
#%% Import Data
nominees = osc.grab_nominees(csv) 
best_movies = nominees[nominees['Category']=='Best Picture']['Nominee'].drop_duplicates().sort_values()


#%% Main App
appDetails = """
Created by: [Bogdan Tudose](https://www.linkedin.com/in/tudosebogdan/) \n
Date: Jan 29, 2024 \n
- Best Picture Emoji Quiz - Just for fun quiz, match the emoji with the correct Best Picture Nominee. 
"""
with st.expander("See app info"):
    st.write(appDetails)

st.title("Best Picture Emoji Quiz - 2024")
correctAnswers = st.secrets["quizResults"]['quiz_answers']
st.write("Select the best picture nominee for each set of emojis.")
quizMode = st.radio('Quiz Difficulty',('Easy','Hard'))
answerOptions = ['Pick an answer'] + list(best_movies)
answerPicks = {}
col1, col2 = st.columns(2)
with col1:
    st.header("1. 👱‍♀️🎀🏰")
    st.header("2. 🧍‍♂️🕰️🔙")
    st.header("3. 🔪🌸🌛")
    st.header("4. 👨‍🔬💣⚛️")
    st.header("5. 🎼👨‍🎤🎶")
    st.header("6. 🇺🇸✍️📖")
    st.header("7. ⏳🔄❤️")
    st.header("8. 🚫🏞️🧐")
    st.header("9. ❌💸🧸")
    st.header("10. 👤🔍⛰️⬇️")
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
