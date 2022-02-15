import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px

st.set_page_config(layout="wide",page_title='Oscars Predictions')

deta = Deta(st.secrets["project_key"])
db = deta.Base("oscar_bets_test")

cols = ['name','email','password','city','best_movie','best_director','best_actor','best_actress']
safeCols = cols.copy()
safeCols.remove('email')
safeCols.remove('password')

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
    
def grab_predictions():
    db_content = db.fetch().items
    df = pd.DataFrame(db_content)
    df = df[cols]
    return df

nominees = grab_nominees()
df = grab_predictions()
emails = df['email'].to_list()

best_movies = nominees[nominees['Category']=='Best Picture']['Nominee'].drop_duplicates().sort_values()
best_directors = nominees[nominees['Category']=='Best Director']['Nominee Full'].drop_duplicates().sort_values()
best_actors = nominees[nominees['Category']=='Best Actor']['Nominee Full'].drop_duplicates().sort_values()
best_actress = nominees[nominees['Category']=='Best Actress']['Nominee Full'].drop_duplicates().sort_values()

#%% Main App
selectPage = st.sidebar.selectbox("Select Page",
    ("Oscar 2022 Nominees", "Oscar 2022 Predictions","Past Oscar Winners", "Best Picture Emoji Quiz"))

appDetails = """
Created by: Bogdan Tudose, bogdan.tudose@marqueegroup.ca \n
Date: Feb 12, 2022 \n
From the left sidebar menu choose one of the pages:
- Oscar 2022 Nominees
- Oscar 2022 Predictions
- Past Oscar Winners

Page descriptions:
- Oscar 2022 Nominees - View this year's nominations broken down by movie and category in an interactive bar chart. Categories can also be filtered in a dropdown.
- Oscar 2022 Predictions - Make predictions for the top categories and compare your answers with other people around the world.
- Past Oscar Winners - Interesting stats of past Oscar winners, including a chart of # of nominations vs # of awards.
- Best Picture Emoji Quiz - Just for fun quiz, match the emoji with the correct Best Picture Nominee. 
"""
with st.expander("See app info"):
    st.write(appDetails)

if selectPage == "Oscar 2022 Nominees":
    st.title("🏆Oscars 2022 Nominees🎥")
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

elif selectPage == "Oscar 2022 Predictions":
    st.title("Oscars 2022 Predictions")
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
                    db.put({"name": user_name,"email": user_email,
                            'password':password,
                            'best_movie':best_movie_pick,
                            'best_director':best_director_pick,
                            'best_actor':best_actor_pick,
                            'best_actress':best_actress_pick,
                            'city':user_city,
                            'key':user_email})
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
elif selectPage == "Past Oscar Winners":
    st.title("Past Oscar Winners")
    aLinks = '''Live source from: <a href="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films" target="_blank">https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films</a><br>'''
    st.markdown(aLinks, unsafe_allow_html=True)
    pastWinnersDF = grab_past_winners()
    figPastWinners = px.scatter(pastWinnersDF, x='Nominations', y='Awards',
                     color='Year', hover_name='Film', title='Nominations vs Awards')
    figPastWinnersJitter = px.strip(pastWinnersDF, x='Nominations', y='Awards',
                     color='Year', hover_name='Film', title='Nominations vs Awards')

    # st.plotly_chart(figPastWinners) #scatter plot doesn't show all data points due to overlap
    st.plotly_chart(figPastWinnersJitter) #strip plot creates a jitter plot (slightly offsets markers for overlaping pts)
    st.write(pastWinnersDF)

else:
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
                    if answerPicks[str(x)] == correctAnswers[x-1]:
                        score+=1
                st.write("You correctly picked {} out of 10 movies.".format(score))
                if score < 3:
                    st.write("We know it's COVID and you haven't gone to a movie theatre in ages, but have you been living under a rock?🗿")
                elif score < 6:
                    st.write("Nice try, but you might want to text💬 a friend next time. Just don't do it during a movie.")
                elif score <10:
                    st.write("Wow, almost perfect! Are you a 🤢🍅 critic?")
                else:
                    st.write("Whoa 100%! You are ready to host the Oscars! 🎤🎬🏆")

                # st.write("Your picks")
                # st.write(answerPicks)
