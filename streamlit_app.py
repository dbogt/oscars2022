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

@st.cache
def grab_past_winners():
    url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
    dfs = pd.read_html(url)
    df = dfs[0]
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
    ("Oscar 2022 Nominees", "Oscar 2022 Predictions","Past Oscar Winners"))

if selectPage == "Oscar 2022 Nominees":
    st.title("Oscars 2022 Nominees")
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
else:
    st.title("Past Oscar Winners")
    pastWinnersDF = grab_past_winners()
    st.write(pastWinnersDF)
