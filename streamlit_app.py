import streamlit as st
import pandas as pd 
from deta import Deta
import plotly.express as px

st.title("Oscars 2022 Predictions")

deta = Deta(st.secrets["project_key"])
db = deta.Base("oscar_bets_test")

cols = ['name','email','password','city','best_movie','best_director','best_actor','best_actress']
safeCols = cols.copy()
safeCols.remove('email')
safeCols.remove('password')

def grab_predictions():

    db_content = db.fetch().items
    df = pd.DataFrame(db_content)
    df = df[cols]
    return df

df = grab_predictions()
emails = df['email'].to_list()
# st.write(emails)

best_movies = ['Belfast','CODA',"Don't Look Up","Drive My Car","Dune","King Richard","Licorice Pizza","Nightmare Alley","The Power of the Dog","West Side Story"]
best_directors = ['Kenneth Branagh – Belfast',
                    'Ryusuke Hamaguchi – Drive My Car',
                    'Paul Thomas Anderson – Licorice Pizza',
                    'Jane Campion – The Power of the Dog',
                    'Steven Spielberg – West Side Story']
best_actors = ['Javier Bardem – Being the Ricardos as Desi Arnaz',
                'Benedict Cumberbatch – The Power of the Dog as Phil Burbank',
                'Andrew Garfield – Tick, Tick... Boom! as Jonathan Larson',
                'Will Smith – King Richard as Richard Williams',
                'Denzel Washington – The Tragedy of Macbeth as Lord Macbeth']
best_actress = ['Jessica Chastain – The Eyes of Tammy Faye as Tammy Faye Bakker',
                'Olivia Colman – The Lost Daughter as Leda Caruso',
                'Penélope Cruz – Parallel Mothers as Janis Martínez Moreno',
                'Nicole Kidman – Being the Ricardos as Lucille Ball',
                'Kristen Stewart – Spencer as Diana, Princess of Wales']

st.write("Enter your predictions below")
with st.form("my_picks"):
    st.write("Predictions Forms")
    user_name = st.text_input("Your name (First Last)")
    user_email = st.text_input("Your email")
    user_city = st.text_input("Your city")
    password = st.text_input("A 'safe word' to retrieve your picks (do NOT use a real password)")
    best_movie_pick = st.selectbox('What movie will win the best picture?',best_movies)
    best_director_pick = st.selectbox('Who will win best director?', best_directors)
    best_actor_pick = st.selectbox('Who will win the best actor?', best_actors)
    best_actress_pick = st.selectbox('Who will win the best actress?', best_actress)
    submit_btn = st.form_submit_button("Save Picks")


    if submit_btn:
        if user_email in emails:
            currentUserDF = df[df['email'] == user_email] 
            checkPass = currentUserDF.iloc[0]['password']
            if checkPass == password:
                checkOK= True
            else:
                checkOK = False
        else:
            checkOK = True
        

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

# db_content = db.fetch().items
# df = pd.DataFrame(db_content)
if st.checkbox('Show predictions by person'):
    safeDF = df[safeCols]
    adminPass = st.text_input('Admin Password')
    if adminPass == st.secrets['admin_pass']:
        st.dataframe(df)
    else:
        st.dataframe(safeDF)

if st.checkbox('Show summary picks'):
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
            fig = px.histogram(df, x=colName, color="name", hover_name="city", barmode='stacked', labels={colName:pick}).update_xaxes(categoryorder="total descending")
            st.plotly_chart(fig)