#%% Import Packages
import pandas as pd 

#%% Functions
@st.cache_data
def grab_nominees(csv):
    #csv = "Oscars2023_Nominees.csv"
    df = pd.read_csv(csv,encoding='latin1')
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

urlBase = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
@st.cache_data
def grab_past_winners(url=urlBase):
    dfs = pd.read_html(url)
    df = dfs[0]
    df['Awards'] = df['Awards'].apply(fixFootnotes)
    df['Nominations'] = df['Nominations'].apply(fixFootnotes)
    return df

urlBAFTA2023 = "https://en.wikipedia.org/wiki/76th_British_Academy_Film_Awards"
urlOSCARS2023 = "https://en.wikipedia.org/wiki/95th_Academy_Awards"
@st.cache
def oscars_vs_bafta(urlBafta=urlBAFTA2023, urlOSCARS=urlOSCARS2023):
    dfs = pd.read_html(urlBAFTA, match='Nominations')
    baftas = dfs[0]
    baftas['Film'] = baftas['Film'].apply(lambda x: x.split('[')[0].strip()) #sometimes footnotes in film name e.g. "[0]"
    dfs = pd.read_html(urlOSCARS, match='Nominations')
    oscars = dfs[0]
    nominations = baftas.merge(oscars, how='outer',on=['Film'], suffixes=("_BAFTA","_OSCAR"))
    nominations = nominations.fillna(0)
    return nominations
