import streamlit as st
import numpy as np
import streamlit.components.v1 as components
import pandas as pd
import os,ast,json,time, eventregistry, calendar, pytz,base64,pathlib
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from nltk.corpus import stopwords
from eventregistry import *
from datetime import datetime
from datetime import timedelta
from io import BytesIO

st.set_page_config(layout="wide")
appOpsi = ['News Analytics','Twitter Analytics']
col1 = st.sidebar
#STARTUP FUNCTION
def selectApp():
    with col1:
        st.markdown("**Apps Selection**")
        selectedOpsi = st.selectbox("",(appOpsi[0],appOpsi[1]))
    return selectedOpsi

def header():
    #image
    image = Image.open('logo-polgov.png')
    st.image(image, width=200, height=100)

    #HEADER
    st.markdown("""
    # Data Analytics Tools
    Explore and Visualize Various Dataset
    """)
    return

def about():
    expandAbout = st.beta_expander("About")
    expandAbout.markdown("""
    * **PolGov Data Analytics** consist of 2 applications. Each application equipped with tools to crawl, preprocess, filter, classify, and visualize dataset.
    * **News Analytics**            : analyze news dataset from _Eventregistry API_.
    * **Twitter Analytics**         : analyze twitter dataset from _Twitter API_.
    * **Crafted** by Big Data Analytics Laboratory, PolGov, Fisipol, UGM (2021).
    """)
    return

def newsHead():
    st.markdown("""
    # News Analytics
    """)
    return

def crawlFunc(apiKey,qStr,artCount,saved):
    er = EventRegistry(apiKey = apiKey)
    q = QueryArticlesIter.initWithComplexQuery(qStr)
    q.setRequestedResult(RequestArticlesInfo(count = artCount,
        returnInfo = ReturnInfo(
            articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True))))
    res = er.execQuery(q)
    resCount=res["articles"]["totalResults"]
    df=pd.DataFrame(res['articles']['results'])
    st.write("CRAWLING %d ARTICLE %d TOTAL ARTICLE"%(artCount,resCount))
    st.write("DONE !")
    csv_desktop(df, saved)
    st.markdown("### DATAFRAME PREVIEW")
    st.dataframe(df.head(10))
    return

def newsAppOpsi():
    expandCrawl  = col1.beta_expander("Crawling")
    expandPrep   = col1.beta_expander("Preprocessing")
    expandFilter = col1.beta_expander("Filtering")
    expandLabel  = col1.beta_expander("Labeling")
    expandSave   = col1.beta_expander("Save File")
    expandVisual = col1.beta_expander("Visualize")
    expandView   = col1.beta_expander("View Item")

    stats=[]

    if expandCrawl.checkbox("News Crawling"):
        apiKey = st.text_input("EventRegistry API Key", '')
        qStr   = st.text_area("Query String (IN JSON OBJECT FORMAT)")
        saved  = st.text_input("Save as")+'_raw.csv'
        b1,b2,b3=st.beta_columns([1,8,1])

        if len(apiKey)>10:
            if len(qStr)>0:
                if len(saved)>8:
                    artSelect = b1.radio("Article Count",('All', 'Custom'))
                    if artSelect == 'All':
                        b2.write('Download all article.')
                        b3.text("")
                        b3.text("")
                        if b3.button("CRAWL"):
                            st.write('Crawling process')
                            try:
                                crawlFunc(apiKey,qStr,artCount,saved)
                            except:
                                st.markdown("### Error in **API Key** or **Query** !")
                                st.markdown("Example of API KEY : 12345678-1234-1234-1234-1234567890ab")
                                obj={"$query": {}}
                                st.markdown("Example of Query   :"+json.dumps(obj,indent=3))
                    else:
                        artCount=b2.number_input("Download some article.",min_value=0,step=1)
                        if artCount>0:
                            b3.text("")
                            b3.text("")
                            if b3.button("CRAWL"):
                                st.write('Crawling process')
                                try:
                                    crawlFunc(apiKey,qStr,artCount,saved)
                                except:
                                    st.markdown("### Error in **API Key** or **Query** !")
                                    st.markdown("Example of API KEY : 12345678-1234-1234-1234-1234567890ab")
                                    obj={"$query": {}}
                                    st.markdown("Example of Query   :"+json.dumps(obj, indent=3))

        # st.markdown("DEVELOPMENT PROCESS")
        # barProg = st.progress(0)
        # maxN=104
        # iterShow=st.empty()
        # for i in np.arange(maxN+1):
        #     time.sleep(0.1)
        #     barProg.progress(i/maxN)
        #     iterShow.text(f"[{i}/{maxN}] downloaded")
    else:

        #CHOOSE LOAD
        if expandPrep.checkbox("Load Dataset"):
            df=selectFile()
            stats.append(0)
            #CHOOSE LOAD->PREP
            if expandPrep.checkbox("Clean & Parse Dataset"):
                df=parseDF(df)
                if 'ind' in list(df['lang']) and 'eng' in list(df['lang']):
                    df=cleanColumnENG(df)
                    df=cleanColumnID(df)
                elif 'ind' in list(df['lang']):
                    df=cleanColumnID(df)
                else:
                    df=cleanColumnENG(df)
                stats.append(1)

            #CHOOSE FILTER
            if expandFilter.checkbox("Filter by Date Range"):
                df=filterByDateShow(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Language"):
                df=filterByLang(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by News Source Title"):
                df=filterByNewsSourceTitle(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by News Author"):
                df=filterByNewsAuthor(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Categories Label"):
                df=filterByCategoriesLabel(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Concepts Wiki"):
                df=filterByConceptsWiki(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Concepts Location"):
                df=filterByConceptsLoc(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Concepts Person"):
                df=filterByConceptsPerson(df)
                stats.append(2)
            if expandFilter.checkbox("Filter by Concepts Organization"):
                df=filterByConceptsOrg(df)
                stats.append(2)

            #CHOOSE LABEL
            if expandLabel.checkbox("Labeling"):
                dictLabel=labelingShow()
                df=filterPascaDF(df,dictLabel)
                stats.append(3)
            if expandLabel.checkbox("Filter by Label Isu"):
                df=filterByLabelIsu(df)
                stats.append(2)
        try:
            dataStatus(stats)
            showDF(df)
            #CHOOSE VIEW
            if expandView.checkbox("View Item"):
                showItem(df)
            #CHOOSE SAVE FILE
            if expandSave.checkbox("Save"):
                saveShow(df)
                stats.append(4)
            #CHOOSE VISUAL BY DATE
            if expandVisual.checkbox("Visualize"):
                st.markdown("### ***VISUALIZATION***")
                with expandVisual:
                    timeOpsi=["Timeline by Day (Style 1)","Timeline by Day (Style 2)","Timeline by Month (Style 1)", "Timeline by Month (Style 2)"]
                    timeStyle = st.selectbox("Timeline Style Selection",(timeOpsi))

                    newsMediaOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    newsMediaSelect = st.selectbox("News Media Selection",(newsMediaOpsi))

                    newsAuthorOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    newsAuthorSelect = st.selectbox("News Author Selection",(newsAuthorOpsi))

                    conceptsLocOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    conceptsLocSelect = st.selectbox("Concepts Location Selection",(conceptsLocOpsi))

                    conceptsPersonOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    conceptsPersonSelect = st.selectbox("Concepts Person Selection",(conceptsPersonOpsi))

                    conceptsOrgOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    conceptsOrgSelect = st.selectbox("Concepts Organization Selection",(conceptsOrgOpsi))

                    conceptsWikiOpsi=["Row 0 to 20","Row 21 to 40","Row 41 to 60","Row 61 to 80","Row 81 to 100","Row > 100"]
                    conceptsWikiSelect = st.selectbox("Concepts Wiki Selection",(conceptsWikiOpsi))

                    catLabOpsi=['News Category Plot','Category Plot Level 1','Category Plot Level 2','Category Plot Level 3']
                    catLabSelect=st.selectbox("Category Label Plot Style",catLabOpsi)

                #PLOT TIMELINE
                if timeStyle==timeOpsi[0]:
                    sLineTime(df)
                elif timeStyle==timeOpsi[1]:
                    mLineTime(df)
                elif timeStyle==timeOpsi[2]:
                    sBarTime(df)
                elif timeStyle==timeOpsi[3]:
                    mBarTime(df)

                #PLOT NEWS MEDIA
                viz1,viz2=st.beta_columns([1,1])
                with viz1:
                    if newsMediaSelect==newsMediaOpsi[0]:
                        newsMedia(df,0,20)
                    elif newsMediaSelect==newsMediaOpsi[1]:
                        newsMedia(df,21,40)
                    elif newsMediaSelect==newsMediaOpsi[2]:
                        newsMedia(df,41,60)
                    elif newsMediaSelect==newsMediaOpsi[3]:
                        newsMedia(df,61,80)
                    elif newsMediaSelect==newsMediaOpsi[4]:
                        newsMedia(df,81,100)
                    elif newsMediaSelect==newsMediaOpsi[5]:
                        newsMedia(df,100,101)

                #PLOT NEWS AUTHOR
                with viz2:
                    if newsAuthorSelect==newsAuthorOpsi[0]:
                        newsAuthor(df,0,20)
                    elif newsAuthorSelect==newsAuthorOpsi[1]:
                        newsAuthor(df,21,40)
                    elif newsAuthorSelect==newsAuthorOpsi[2]:
                        newsAuthor(df,41,60)
                    elif newsAuthorSelect==newsAuthorOpsi[3]:
                        newsAuthor(df,61,80)
                    elif newsAuthorSelect==newsAuthorOpsi[4]:
                        newsAuthor(df,81,100)
                    elif newsAuthorSelect==newsAuthorOpsi[5]:
                        newsAuthor(df,100,101)

                #PLOT CONCEPTS LOC
                with viz1:
                    if conceptsLocSelect==conceptsLocOpsi[0]:
                        conceptsLocPlot(df,0,20)
                    elif conceptsLocSelect==conceptsLocOpsi[1]:
                        conceptsLocPlot(df,21,40)
                    elif conceptsLocSelect==conceptsLocOpsi[2]:
                        conceptsLocPlot(df,41,60)
                    elif conceptsLocSelect==conceptsLocOpsi[3]:
                        conceptsLocPlot(df,61,80)
                    elif conceptsLocSelect==conceptsLocOpsi[4]:
                        conceptsLocPlot(df,81,100)
                    elif conceptsLocSelect==conceptsLocOpsi[5]:
                        conceptsLocPlot(df,100,101)

                #PLOT CONCEPTS PERSON
                with viz2:
                    if conceptsPersonSelect==conceptsPersonOpsi[0]:
                        conceptsPersonPlot(df,0,20)
                    elif conceptsPersonSelect==conceptsPersonOpsi[1]:
                        conceptsPersonPlot(df,21,40)
                    elif conceptsPersonSelect==conceptsPersonOpsi[2]:
                        conceptsPersonPlot(df,41,60)
                    elif conceptsPersonSelect==conceptsPersonOpsi[3]:
                        conceptsPersonPlot(df,61,80)
                    elif conceptsPersonSelect==conceptsPersonOpsi[4]:
                        conceptsPersonPlot(df,81,100)
                    elif conceptsPersonSelect==conceptsPersonOpsi[5]:
                        conceptsPersonPlot(df,100,101)

                #PLOT CONCEPTS ORGANIZATION
                with viz1:
                    if conceptsOrgSelect==conceptsOrgOpsi[0]:
                        conceptsOrgPlot(df,0,20)
                    elif conceptsOrgSelect==conceptsOrgOpsi[1]:
                        conceptsOrgPlot(df,21,40)
                    elif conceptsOrgSelect==conceptsOrgOpsi[2]:
                        conceptsOrgPlot(df,41,60)
                    elif conceptsOrgSelect==conceptsOrgOpsi[3]:
                        conceptsOrgPlot(df,61,80)
                    elif conceptsOrgSelect==conceptsOrgOpsi[4]:
                        conceptsOrgPlot(df,81,100)
                    elif conceptsOrgSelect==conceptsOrgOpsi[5]:
                        conceptsOrgPlot(df,100,101)

                #PLOT CONCEPTS WIKI
                with viz2:
                    if conceptsWikiSelect==conceptsWikiOpsi[0]:
                        conceptsWikiPlot(df,0,20)
                    elif conceptsWikiSelect==conceptsWikiOpsi[1]:
                        conceptsWikiPlot(df,21,40)
                    elif conceptsWikiSelect==conceptsWikiOpsi[2]:
                        conceptsWikiPlot(df,41,60)
                    elif conceptsWikiSelect==conceptsWikiOpsi[3]:
                        conceptsWikiPlot(df,61,80)
                    elif conceptsWikiSelect==conceptsWikiOpsi[4]:
                        conceptsWikiPlot(df,81,100)
                    elif conceptsWikiSelect==conceptsWikiOpsi[5]:
                        conceptsWikiPlot(df,100,101)

                #PLOT CATEGORY LAB
                with viz1:
                    if catLabSelect==catLabOpsi[0]:
                        catLabNews(df)
                    elif catLabSelect==catLabOpsi[1]:
                        catMoz(df,1)
                    elif catLabSelect==catLabOpsi[2]:
                        catMoz(df,2)
                    else:
                        catMoz(df,3)
                with viz2:
                    if catLabSelect==catLabOpsi[0]:
                        catLabNewsBar(df)
                    elif catLabSelect==catLabOpsi[1]:
                        catMozBar(df,1)
                    elif catLabSelect==catLabOpsi[2]:
                        catMozBar(df,2)
                    else:
                        catMozBar(df,3)

                #PLOT LABEL ISU
                with viz1:
                    try:
                        plotLabelIsu(df)
                    except:
                        pass

                #SAVE PLOT EXCEL
                savePlotExcel(df)
        except:
            pass
    return

def twitterHead():
    st.markdown("""
    # Twitter Analytics
    """)
    return

def twitterAppOpsi():
    with col1:
        expandCrawl  = st.beta_expander("Crawling")
        expandPrep   = st.beta_expander("Preprocessing")
        expandFilter = st.beta_expander("Filtering")
        expandClass  = st.beta_expander("Classifying")
        expandVisual = st.beta_expander("Visualize")
    return

def dataStatus(stats):
    statsInfo="### ***"
    stats=sorted(stats)
    for i in stats:
        if i==0:
            statsInfo+="LOADED"
        elif i==1:
            statsInfo+=" -> PREPROCESSED"
        elif i==2:
            statsInfo+=" -> FILTERED"
        elif i==3:
            statsInfo+=" -> LABELED"
        else:
            statsInfo+=" -> SAVED"
    statsInfo+="***"
    st.markdown(statsInfo)
    return

#FUNCTIONAL


def selectFile():
    st.markdown(
        """
        ### ***SELECT FILE***
        """
    )

    fname = st.file_uploader("Upload a file", type=("csv", "xlsx"))
    try:
        df=pd.read_csv(fname)
        return df
    except:
        pass
    return

def showDF(df):
    try:
        st.dataframe(df.head(5))
        st.markdown("""Total Column: %d | Total Row: %d"""%(len(df.columns),len(df)))
    except:
        st.markdown("**Warning**: Dataset Not Found!")
    return

def konsepWiki(row):
    row=ast.literal_eval(row)
    a=[]
    for i in row:
        if i['type']=='wiki':
            for j in i['label'].values():
                a.append(j.lower())
    return a
def konsepLoc(row):
    row=ast.literal_eval(row)
    a=[]
    for i in row:
        if i['type']=='loc':
            for j in i['label'].values():
                a.append(j.lower())
    return a
def konsepPerson(row):
    row=ast.literal_eval(row)
    a=[]
    for i in row:
        if i['type']=='person':
            for j in i['label'].values():
                a.append(j.lower())
    return a
def konsepOrg(row):
    row=ast.literal_eval(row)
    a=[]
    for i in row:
        if i['type']=='org':
            for j in i['label'].values():
                a.append(j.lower())
    return a
def parseConcept(df):
    df['concepts_wiki']  =df['concepts'].apply(lambda x: konsepWiki(x))
    df['concepts_loc']   =df['concepts'].apply(lambda x: konsepLoc(x))
    df['concepts_person']=df['concepts'].apply(lambda x: konsepPerson(x))
    df['concepts_org']   =df['concepts'].apply(lambda x: konsepOrg(x))
    return df
def parseOther(df):
    df['newsSourceTitle'] =df['source'].apply(lambda x: ast.literal_eval(x)['title'].lower())
    df['newsAuthor']      =df['authors'].apply(lambda x: [i['name'].lower() for i in ast.literal_eval(x)])
    df['categories_label']=df['categories'].apply(lambda x: [i['label'].lower() for i in ast.literal_eval(x)])
    return df
@st.cache(allow_output_mutation=True)
def parseDF(df):
    df=parseOther(df)
    df=parseConcept(df)
    return df
@st.cache
def cleanText(row):
    row         =re.sub(r"http\S+", "", row)
    row         =re.sub('\n',' ',row)
    row         =' '.join([i for i in row.split(' ') if i[:1]!='#' and i[:1]!='@']).lower()
    row         =re.sub(r'[^\w\s]',' ',row)
    return row

def stopwordID(row):
    script_dir = os.path.dirname(__file__)
    file_path  = os.path.join(script_dir, "id.stopwords.02.01.2016.txt")
    fptr       = open(file_path, 'r')
    stopID     = re.split('\n', fptr.read())
    row        = " ".join([i for i in row.split(" ") if i not in stopID])
    return row

def stopwordGen(row):
    script_dir = os.path.dirname(__file__)
    file_path  = os.path.join(script_dir, "generalStopword.txt")
    fptr       = open(file_path, 'r')
    stop     = re.split('\n', fptr.read())
    row        = " ".join([i for i in row.split(" ") if i not in stop])
    return row
@st.cache(allow_output_mutation=True)
def cleanColumnID(df):
    df['body']=df['body'].apply(lambda x : str(x).replace('\r', '').replace('\n', ''))
    df['body_clean']=df['body'].str.lower()
    df['body_clean']=df['body_clean'].apply(cleanText)
    df['body_clean']=df['body_clean'].apply(stopwordID)
    df['body_clean']=df['body_clean'].apply(stopwordGen)
    return df
@st.cache(allow_output_mutation=True)
def cleanColumnENG(df):
    #Buat stopword remover
    stop = stopwords.words('english')
    df['body']=df['body'].apply(lambda x : str(x).replace('\r', '').replace('\n', ''))
    df['body_clean']=df['body'].str.lower()
    df['body_clean']=df['body_clean'].apply(cleanText)
    df['body_clean'] = df['body_clean'].apply(lambda x: " ".join([item for item in x.split(" ") if item not in stop]))
    df['body_clean']=df['body_clean'].apply(stopwordGen)
    return df

def showItem(df):
    with col1:
        st.markdown(
            """
            ### **ITEM PREVIEW**
            """
        )
        selectedColumn=st.selectbox('View Item From Column',sorted(df.columns))
        rowNum  = st.text_input("Row Number","0")
    item=df[selectedColumn][int(rowNum)]
    st.markdown("""
    ### ***VIEW ITEM FROM: *** (**column** %s **row number** %s)
    """%(selectedColumn,rowNum))

    if selectedColumn=='concepts':
        item=ast.literal_eval(item)
        item=json.dumps({"concepts": item}, indent=3)
        st.code("DATA TYPE: "+str(type(item)))
        st.code(item,language='json')
    elif selectedColumn=='categories':
        item=ast.literal_eval(item)
        item=json.dumps({"categories": item}, indent=3)
        st.code("DATA TYPE: "+str(type(item)))
        st.code(item,language='json')
    elif selectedColumn=="label_isu":
        st.code("UNIQUE DATA: "+str(list(set(list(df['label_isu'])))))
        for i in list(set(list(df['label_isu']))):
            st.code("COUNT OF "+str(i)+" : "+str(len(df[df['label_isu']==i])))
        item=df[selectedColumn][int(rowNum)]
        st.code(item,language='json')
    else:
        st.code("DATA TYPE: "+str(type(item)))
        st.code(item,language='json')
    return

def filterByDateShow(df):
    st.markdown("---")
    st.markdown("#### **DATE RANGE SELECTION**")
    st.markdown("RAW DATA DATERANGE: from **%s** until **%s**"%(min(df['date']),max(df['date'])))
    global fdcol1,fdcol2,fdcol3
    fdcol1, fdcol2,fdcol3= st.beta_columns([1,1,2])
    df['date'] = pd.to_datetime(df['date'])
    minDate    = min(df['date'])
    maxDate    = max(df['date'])
    start_date = fdcol1.date_input("Start Date",value=minDate,min_value=minDate,max_value=maxDate)
    end_date   = fdcol2.date_input("End Date",value=maxDate,min_value=minDate,max_value=maxDate)
    df=filterByDate(df,start_date,end_date)
    fdcol3.markdown("\n")
    fdcol3.markdown("\n")
    fdcol3.markdown("RESULT DATA DATERANGE: from **%s** until **%s**"%(min(df['date']),max(df['date'])))
    return df
@st.cache(allow_output_mutation=True)
def filterByDate(df,start_date,end_date):
    df=df[(df['date'] >= str(start_date)) & (df['date'] <= str(end_date+ timedelta(days=1)))]
    return df

def filterByLang(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY LANGUAGE**")
    selectedColumn='lang'
    columnUniqueItem=sorted(list(set(list(df[selectedColumn]))))
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df=runFilter(df,selectedColumn,selectedItem)
    return df

def filterByNewsSourceTitle(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS SOURCE TITLE**")
    selectedColumn='newsSourceTitle'
    columnUniqueItem=sorted(list(set(list(df[selectedColumn]))))
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df=runFilter(df,selectedColumn,selectedItem)
    return df

def filterByNewsAuthor(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS SOURCE AUTHOR**")
    selectedColumn='newsAuthor'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=checkItemInListFunc(df,selectedColumn,selectedItem)
    df=filterCheckFunc(df)
    return df

def filterByCategoriesLabel(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS CATEGORIES LABEL**")
    selectedColumn='categories_label'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=checkItemInListFunc(df,selectedColumn,selectedItem)
    df=filterCheckFunc(df)
    return df

def filterByConceptsWiki(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS CONCEPTS WIKI**")
    selectedColumn='concepts_wiki'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=checkItemInListFunc(df,selectedColumn,selectedItem)
    df=filterCheckFunc(df)
    return df

def filterByConceptsLoc(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS CONCEPTS Location**")
    selectedColumn='concepts_loc'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=df[selectedColumn].apply(lambda x: checkItemInList(x,selectedItem))
    df=filterCheckFunc(df)
    return df

def filterByConceptsPerson(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS CONCEPTS PERSONS**")
    selectedColumn='concepts_person'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=checkItemInListFunc(df,selectedColumn,selectedItem)
    df=filterCheckFunc(df)
    return df

def filterByConceptsOrg(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY NEWS CONCEPTS WIKI**")
    selectedColumn='concepts_org'
    columnUniqueItem=colUniqueItemFunc(df,selectedColumn)
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df['filterCheck']=checkItemInListFunc(df,selectedColumn,selectedItem)
    df=filterCheckFunc(df)
    return df

def filterByLabelIsu(df):
    st.markdown("---")
    st.markdown("#### **FILTER BY label_isu**")
    selectedColumn='label_isu'
    columnUniqueItem=sorted(list(set(list(df[selectedColumn]))))
    selectedItem= st.multiselect('Select Item', columnUniqueItem, columnUniqueItem)
    st.write("Selected %d from %d item"%(len(selectedItem),len(columnUniqueItem)))
    df=runFilter(df,selectedColumn,selectedItem)
    return df

@st.cache
def checkItemInList(row,columnUniqueItem):
    res=None
    for i in row:
        if i in columnUniqueItem:
            res=True
            break
        else:
            res=False
    return res
@st.cache
def runFilter(df,selectedColumn,selectedItem):
    df=df[df[selectedColumn].isin(selectedItem)]
    return df
@st.cache
def filterCheckFunc(df):
    df=df[df['filterCheck']==True]
    return df
@st.cache
def colUniqueItemFunc(df,selectedColumn):
    columnUniqueItem=sorted(list(set([a for b in df[selectedColumn].tolist() for a in b])))
    return columnUniqueItem
@st.cache(allow_output_mutation=True)
def checkItemInListFunc(df,selectedColumn,selectedItem):
    df['filterCheck']=df[selectedColumn].apply(lambda x: checkItemInList(x,selectedItem))
    return df['filterCheck']
@st.cache
def filterDict(row,dfilter):
    row=row.lower()
    n=0
    x=[]
    for k in dfilter.keys():
        for v in dfilter[k]:
            v=v.lower()
            if v[:1]==' ' and v[-1:]==' ':
                a=list(v)
            else:
                a=v.split(' ')
            if len(a)>1:
                nd=0
                for j in a:
                    if j in row.split(' '):
                        nd+=1
                if nd>=len(a):
                    n+=1
                    x.append(k)
            elif v in row:
                n+=1
                x.append(k)
    if len(x)==0:
        x="isu lainnya"
    else:
        x=str(list(set(x))[0])
    return x
@st.cache(allow_output_mutation=True)
def filterPascaDF(df,dfilter):
    df['label_isu']=df['body_clean'].apply(lambda x : filterDict(x,dfilter))
    return df

def labelingShow():
    st.markdown("---")
    ai1,ai2=st.beta_columns([1,5])
    k1 =ai1.text_input("Label 1",value="")
    v1 =ai2.text_area("Keywords 1",value="")

    for i in range(3):
        ai1.write("\n")
    k2 =ai1.text_input("Label 2",value="")
    v2 =ai2.text_area("Keywords 2",value="")

    for i in range(3):
        ai1.write("\n")
    k3 =ai1.text_input("Label 3",value="")
    v3 =ai2.text_area("Keywords 3",value="")

    dictLabel={k1:v1.split(","),k2:v2.split(","),k3:v3.split(",")}
    ritem=[""," ","\n"]
    if '' in dictLabel:
        del dictLabel['']
    for x in list(dictLabel.keys()):
        if dictLabel[x] == [""]:
            del dictLabel[x]
        else:
            dictLabel[x]=[x.strip() for x in dictLabel[x] if x.strip() not in ritem]
    return dictLabel

def saveShow(df):
    st.markdown("---")
    st.markdown("""#### ***SAVE FILE***""")
    svcol1, svcol2= st.beta_columns([1,5])
    LoadOpsi  = ['CSV','Excel']
    selectedLoadOpsi = svcol1.selectbox('Save As',(LoadOpsi[0],LoadOpsi[1]))
    if selectedLoadOpsi == LoadOpsi[0]:
        with svcol2:
            saved = st.text_input("Filename", "")+".csv"
            if len(saved)>0:
                try:
                    st.markdown(csv_link(df, saved),unsafe_allow_html=True)
                except:
                    csv_desktop(df, saved)

    else:
        with svcol2:
            saved = st.text_input("Filename", "")+".xlsx"
            if len(saved)>0:
                try:
                    st.markdown(excel_link(df, saved), unsafe_allow_html=True)
                except:
                    excel_desktop(df, saved)
    return

def savePlotExcel(df):
    st.markdown("---")
    st.markdown("""#### ***SAVE PLOT FILE TO EXCEL***""")
    saved = st.text_input("Filename", "")+"_plot.xlsx"
    # desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    # saved2=str(desktop)+'/'+saved
    # if len(saved)>5:
    #     if st.button("SAVE"):
    #         saveDFPlot(df,saved2)
    #         st.write("SAVED TO: " +saved2)
    # saved = st.text_input("Filename", "")+".xlsx"
    if len(saved)>0:
        try:
            st.markdown(excel_link(df, saved), unsafe_allow_html=True)
    return

def csv_desktop(df, saved):
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    saved2=str(desktop)+'/'+saved
    if isinstance(df,pd.DataFrame):
        df=df.to_csv(saved2,index=False)
        if len(saved)>0:
            st.write("SAVED TO: " +saved2)
    return

def excel_desktop(df, saved):
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    saved2=str(desktop)+'/'+saved
    if isinstance(df,pd.DataFrame):
        df=df.to_excel(saved2,index=False)
        if len(saved)>0:
            st.write("SAVED TO: " +saved2)
    return

def csv_link(df, saved):
    if isinstance(df,pd.DataFrame):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="{saved}">Download CSV File</a>'

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index = False, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) # Tried with '0%' and '#,##0.00' also.
    worksheet.set_column('A:A', None, format1) # Say Data are in column A
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def excel_link(df, saved):
    if isinstance(df,pd.DataFrame):
        val = to_excel(df)
        b64 = base64.b64encode(val).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{saved}">Download Excel File</a>'

def mLineTime(df,plotStat=True):
    dfDateIsu=df[['date','label_isu']]
    dfDateIsu=dfDateIsu.sort_values(by='date')
    dfDateIsu=dfDateIsu.groupby(["date", "label_isu"])["date"].count().reset_index(name="freq")

    fig = px.line(dfDateIsu, x="date", y="freq", title='Timeline',template="plotly_white",line_group="label_isu",color="label_isu")
    fig.update_layout(
        font_family="Arial",
        font_size=14,
        showlegend=True
    )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Article : %d ***"%(sum(dfDateIsu['freq'])))
    return dfDateIsu
def sLineTime(df,plotStat=True):
    dfDate=pd.DataFrame(pd.to_datetime(df['date']))
    dfDate=pd.DataFrame(dfDate['date'].value_counts().rename_axis('date').reset_index(name='freq'))
    dfDate=dfDate.sort_values(by='date')
    fig = px.line(dfDate, x="date", y="freq", title='Timeline',template="plotly_white")
    fig.update_layout(
        font_family="Arial",
        font_size=14
    )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Article : %d ***"%(sum(dfDate['freq'])))
    return dfDate
def mBarTime(df,plotStat=True):
    dfMonthIsu=df[['date','label_isu']]
    dfMonthIsu['date']=pd.to_datetime(dfMonthIsu['date'])
    dfMonthIsu['monthYear'] = dfMonthIsu['date'].dt.strftime('%Y-%m')
    dfMonthIsu=dfMonthIsu.sort_values(by='date')
    dfMonthIsu=dfMonthIsu.groupby(["monthYear", "label_isu"])["monthYear"].count().reset_index(name="freq")

    fig = px.bar(dfMonthIsu, x="monthYear", y="freq", title='Timeline',template="plotly_white",color="label_isu")
    fig.update_layout(
        font_family="Arial",
        font_size=14,
        showlegend=True
    )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Article : %d ***"%(sum(dfMonthIsu['freq'])))
    return dfMonthIsu
def sBarTime(df,plotStat=True):
    dfMonth=pd.DataFrame(pd.to_datetime(df['date']))
    dfMonth['monthYear'] = dfMonth['date'].dt.strftime('%Y-%m')
    dfMonth=pd.DataFrame(dfMonth['monthYear'].value_counts().rename_axis('monthYear').reset_index(name='freq'))
    dfMonth=dfMonth.sort_values(by='monthYear')
    fig = px.bar(dfMonth, x="monthYear", y="freq", title='Timeline',template="plotly_white")
    fig.update_layout(
        font_family="Arial",
        font_size=14
    )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Article : %d ***"%(sum(dfMonth['freq'])))
    return dfMonth
def newsMedia(df,startRow,endRow,plotStat=True):
    dfNewsTitle=pd.DataFrame(df['newsSourceTitle'])
    dfNewsTitle=pd.DataFrame(dfNewsTitle['newsSourceTitle'].value_counts().rename_axis('newsSourceTitle').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfNewsTitle[startRow:len(dfNewsTitle)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="newsSourceTitle", x="freq", title='News Media [Row %d to %d]'%(startRow,len(dfNewsTitle)),template="plotly_white",text='freq', height=600,color='freq')
    else:
        dfPlot=dfNewsTitle[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="newsSourceTitle", x="freq", title='News Media [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq', height=600,color='freq')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        font_family="Arial",
        font_size=14
    )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Media : %d ***"%(len(dfNewsTitle)))
    return dfNewsTitle

def newsAuthor(df,startRow,endRow,plotStat=True):
    df=df['newsAuthor'].apply(lambda x: ast.literal_eval(str(x)))
    dfNewsAuthor= pd.DataFrame([item for sublist in df for item in sublist]).reset_index()
    dfNewsAuthor= dfNewsAuthor.rename(columns={0: 'newsAuthor'})
    dfNewsAuthor=pd.DataFrame(dfNewsAuthor['newsAuthor'].value_counts().rename_axis('newsAuthor').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfNewsAuthor[startRow:len(dfNewsAuthor)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="newsAuthor", x="freq", title='News Author [Row %d to %d]'%(startRow,len(dfNewsAuthor)),template="plotly_white",text='freq',color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    else:
        dfPlot=dfNewsAuthor[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="newsAuthor", x="freq", title='News Author [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq',height=600,color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total News Author : %d ***"%(len(dfNewsAuthor)))
    return dfNewsAuthor

def conceptsLocPlot(df,startRow,endRow,plotStat=True):
    df=df['concepts_loc'].apply(lambda x: ast.literal_eval(str(x)))
    dfConceptsLoc= pd.DataFrame([item for sublist in df for item in sublist]).reset_index()
    dfConceptsLoc= dfConceptsLoc.rename(columns={0: 'concepts_loc'})
    dfConceptsLoc=pd.DataFrame(dfConceptsLoc['concepts_loc'].value_counts().rename_axis('concepts_loc').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfConceptsLoc[startRow:len(dfConceptsLoc)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_loc", x="freq", title='Concepts Location [Row %d to %d]'%(startRow,len(dfConceptsLoc)),template="plotly_white",text='freq',color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    else:
        dfPlot=dfConceptsLoc[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_loc", x="freq", title='Concepts Location [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq',height=600,color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Concepts Location : %d ***"%(len(dfConceptsLoc)))
    return dfConceptsLoc

def conceptsPersonPlot(df,startRow,endRow,plotStat=True):
    df=df['concepts_person'].apply(lambda x: ast.literal_eval(str(x)))
    dfConceptsPerson= pd.DataFrame([item for sublist in df for item in sublist]).reset_index()
    dfConceptsPerson= dfConceptsPerson.rename(columns={0: 'concepts_person'})
    dfConceptsPerson=pd.DataFrame(dfConceptsPerson['concepts_person'].value_counts().rename_axis('concepts_person').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfConceptsPerson[startRow:len(dfConceptsPerson)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_person", x="freq", title='Concepts Location [Row %d to %d]'%(startRow,len(dfConceptsPerson)),template="plotly_white",text='freq',color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    else:
        dfPlot=dfConceptsPerson[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_person", x="freq", title='Concepts Person [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq',height=600,color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Concepts Person : %d ***"%(len(dfConceptsPerson)))
    return dfConceptsPerson

def conceptsOrgPlot(df,startRow,endRow,plotStat=True):
    df=df['concepts_org'].apply(lambda x: ast.literal_eval(str(x)))
    dfConceptsOrg= pd.DataFrame([item for sublist in df for item in sublist]).reset_index()
    dfConceptsOrg= dfConceptsOrg.rename(columns={0: 'concepts_org'})
    dfConceptsOrg=pd.DataFrame(dfConceptsOrg['concepts_org'].value_counts().rename_axis('concepts_org').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfConceptsOrg[startRow:len(dfConceptsOrg)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_org", x="freq", title='Concepts Organization [Row %d to %d]'%(startRow,len(dfConceptsOrg)),template="plotly_white",text='freq',color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    else:
        dfPlot=dfConceptsOrg[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_org", x="freq", title='Concepts Organization [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq',height=600,color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Concepts Organization : %d ***"%(len(dfConceptsOrg)))
    return dfConceptsOrg

def conceptsWikiPlot(df,startRow,endRow,plotStat=True):
    df=df['concepts_wiki'].apply(lambda x: ast.literal_eval(str(x)))
    dfConceptsWiki= pd.DataFrame([item for sublist in df for item in sublist]).reset_index()
    dfConceptsWiki= dfConceptsWiki.rename(columns={0: 'concepts_wiki'})
    dfConceptsWiki=pd.DataFrame(dfConceptsWiki['concepts_wiki'].value_counts().rename_axis('concepts_wiki').reset_index(name='freq'))
    if endRow>100:
        dfPlot=dfConceptsWiki[startRow:len(dfConceptsWiki)]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_wiki", x="freq", title='Concepts Wiki [Row %d to %d]'%(startRow,len(dfConceptsWiki)),template="plotly_white",text='freq',color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    else:
        dfPlot=dfConceptsWiki[startRow:endRow]
        dfPlot=dfPlot.sort_values(by='freq')
        fig = px.bar(dfPlot, y="concepts_wiki", x="freq", title='Concepts Wiki [Row %d to %d]'%(startRow,endRow),template="plotly_white",text='freq',height=600,color='freq')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Concepts Wiki : %d ***"%(len(dfConceptsWiki)))
    return dfConceptsWiki

def catLabNews(df,plotStat=True):
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    dfCatLab=df['categories_label'].apply(lambda x: ast.literal_eval(str(x)))
    dfCatLab= pd.DataFrame([item for sublist in dfCatLab for item in sublist]).reset_index()
    dfCatLab= dfCatLab.rename(columns={0: 'categories_label'})
    dfCatLab=pd.DataFrame(dfCatLab['categories_label'].value_counts().rename_axis('categories_label').reset_index(name='freq'))
    dfNewsCat=dfCatLab[dfCatLab['categories_label'].apply(lambda x: x.startswith('news/'))]
    dfNewsCat['categories_label']=dfNewsCat['categories_label'].apply(lambda x: x.split('/')[1])
    fig = go.Figure(data=[go.Pie(labels=dfNewsCat['categories_label'],
                                 values=dfNewsCat['freq'])])
    fig.update_layout(title_text='Categories Label')
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    #fig.show()
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Categories Label : %d ***"%(len(dfNewsCat)))
    return dfNewsCat

def parseLevel(row,levelNum):
    try:
        row=row.split('/')[levelNum]
    except:
        row=''
    return row
def catMoz(df,levelNum,plotStat=True):
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    dfCatLab=df['categories_label'].apply(lambda x: ast.literal_eval(str(x)))
    dfCatLab= pd.DataFrame([item for sublist in dfCatLab for item in sublist]).reset_index()
    dfCatLab= dfCatLab.rename(columns={0: 'categories_label'})
    dfCatLab=pd.DataFrame(dfCatLab['categories_label'].value_counts().rename_axis('categories_label').reset_index(name='freq'))
    dfMozCat=dfCatLab[dfCatLab['categories_label'].apply(lambda x: x.startswith('dmoz/'))]
    dfMozCat['level1']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,1))
    dfMozCat['level2']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,2))
    dfMozCat['level3']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,3))
    dfMozCatSave=dfMozCat
    if levelNum==3:
        dfMozCat=dfMozCat[dfMozCat['level3']!='']
        fig = px.sunburst(dfMozCat, path=['level1', 'level2', 'level3'], values='freq', color='level3')
        fig =go.Figure(go.Sunburst(
                labels=fig['data'][0]['labels'].tolist(),
                parents=fig['data'][0]['parents'].tolist(),
                values=fig['data'][0]['values'].tolist(),
                ids=fig['data'][0]['ids'].tolist()
                            )
                )
        fig.update_traces(marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text='Categories Label')
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfMozCat['level3'])))))
    elif levelNum==2:
        dfMozCat=dfMozCat[dfMozCat['level2']!='']
        fig = px.sunburst(dfMozCat, path=['level1', 'level2'], values='freq', color='level2')
        fig =go.Figure(go.Sunburst(
                labels=fig['data'][0]['labels'].tolist(),
                parents=fig['data'][0]['parents'].tolist(),
                values=fig['data'][0]['values'].tolist(),
                ids=fig['data'][0]['ids'].tolist()
                            )
                )
        fig.update_traces(marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text='Categories Label')
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfMozCat['level2'])))))
    else:
        dfMozCat=dfMozCat[dfMozCat['level1']!='']
        fig = px.sunburst(dfMozCat, path=['level1'], values='freq', color='level1')
        fig =go.Figure(go.Sunburst(
                labels=fig['data'][0]['labels'].tolist(),
                parents=fig['data'][0]['parents'].tolist(),
                values=fig['data'][0]['values'].tolist(),
                ids=fig['data'][0]['ids'].tolist()
                            )
                )
        fig.update_traces(textinfo='label+value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        fig.update_layout(title_text='Categories Label')
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfMozCat['level1'])))))
    return dfMozCatSave

def catLabNewsBar(df,plotStat=True):
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    dfCatLab=df['categories_label'].apply(lambda x: ast.literal_eval(str(x)))
    dfCatLab= pd.DataFrame([item for sublist in dfCatLab for item in sublist]).reset_index()
    dfCatLab= dfCatLab.rename(columns={0: 'categories_label'})
    dfCatLab=pd.DataFrame(dfCatLab['categories_label'].value_counts().rename_axis('categories_label').reset_index(name='freq'))
    dfNewsCat=dfCatLab[dfCatLab['categories_label'].apply(lambda x: x.startswith('news/'))]
    dfNewsCat['categories_label']=dfNewsCat['categories_label'].apply(lambda x: x.split('/')[1])
    dfNewsCat=dfNewsCat.sort_values(by='freq',ascending=False)
    fig = px.bar(dfNewsCat, y="categories_label", x="freq",
                 title='Categories Label',
                 template="plotly_white",
                 text='freq',
                 color='categories_label')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        font_family="Arial",
        font_size=14
    )
    #fig.show()
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Categories Label : %d ***"%(len(dfNewsCat)))
    return

def catMozBar(df,levelNum,plotStat=True):
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    dfCatLab=df['categories_label'].apply(lambda x: ast.literal_eval(str(x)))
    dfCatLab= pd.DataFrame([item for sublist in dfCatLab for item in sublist]).reset_index()
    dfCatLab= dfCatLab.rename(columns={0: 'categories_label'})
    dfCatLab=pd.DataFrame(dfCatLab['categories_label'].value_counts().rename_axis('categories_label').reset_index(name='freq'))
    dfMozCat=dfCatLab[dfCatLab['categories_label'].apply(lambda x: x.startswith('dmoz/'))]
    dfMozCat['level1']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,1))
    dfMozCat['level2']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,2))
    dfMozCat['level3']=dfMozCat['categories_label'].apply(lambda x: parseLevel(x,3))
    if levelNum==3:
        dfMozCat=dfMozCat[dfMozCat['level3']!='']
        dfPlot=dfMozCat.groupby(['level1','level3'])['freq'].agg('sum').reset_index()
        fig = px.bar(dfPlot.sort_values(by=['level1','freq'],ascending=[False,True]), y="level3", x="freq",
                 title='Categories Label',
                 template="plotly_white",
                 text='freq',
                 color='level1')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfPlot['level3'])))))
    elif levelNum==2:
        dfMozCat=dfMozCat[dfMozCat['level2']!='']
        dfPlot=dfMozCat.groupby(['level1','level2'])['freq'].agg('sum').reset_index()
        fig = px.bar(dfPlot.sort_values(by=['level1','freq'],ascending=[False,True]), y="level2", x="freq",
                 title='Categories Label',
                 template="plotly_white",
                 text='freq',
                 color='level1')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfPlot['level2'])))))
    else:
        dfMozCat=dfMozCat[dfMozCat['level1']!='']
        dfPlot=dfMozCat.groupby(['level1'])['freq'].agg('sum').reset_index()
        fig = px.bar(dfPlot.sort_values(by=['freq'],ascending=False), y="level1", x="freq",
                 title='Categories Label',
                 template="plotly_white",
                 text='freq',
                 color='level1')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            font_family="Arial",
            font_size=14
        )
        if plotStat:
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("***Total Categories Label : %d ***"%(len(list(set(dfPlot['level1'])))))
    #fig.update_layout(title_text='Categories Label')
    #fig.show()
    return

def plotLabelIsu(df,plotStat=True):
    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
    dfLabelIsu=pd.DataFrame(df['label_isu'].value_counts().rename_axis('label_isu').reset_index(name='freq'))
    fig = go.Figure(data=[go.Pie(labels=dfLabelIsu['label_isu'],
                                 values=dfLabelIsu['freq'])])
    fig.update_layout(title_text='Label Isu')
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    if plotStat:
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("***Total Isu  : %d ***"%(len(dfLabelIsu)))
    return dfLabelIsu

def saveDFPlot(df,saved):
    writer = pd.ExcelWriter(saved)
    try:
        sBarTime(df,plotStat=False).to_excel(writer, "Timeline by Month", index=False)
    except:
        pass
    try:
        mBarTime(df,plotStat=False).to_excel(writer, "Timeline by Month_Isu", index=False)
    except:
        pass
    try:
        sLineTime(df,plotStat=False).to_excel(writer, "Timeline by Date", index=False)
    except:
        pass
    try:
        mLineTime(df,plotStat=False).to_excel(writer, "Timeline by Date_Isu", index=False)
    except:
        pass
    try:
        newsMedia(df,0,20,plotStat=False).to_excel(writer, "News Media", index=False)
    except:
        pass
    try:
        newsAuthor(df,0,20,plotStat=False).to_excel(writer, "News Author", index=False)
    except:
        pass
    try:
        conceptsLocPlot(df,0,20,plotStat=False).to_excel(writer, "Concepts Location", index=False)
    except:
        pass
    try:
        conceptsPersonPlot(df,0,20,plotStat=False).to_excel(writer, "Concepts Person", index=False)
    except:
        pass
    try:
        conceptsOrgPlot(df,0,20,plotStat=False).to_excel(writer, "Concepts Organization", index=False)
    except:
        pass
    try:
        conceptsWikiPlot(df,0,20,plotStat=False).to_excel(writer, "Concepts Wiki", index=False)
    except:
        pass
    try:
        catLabNews(df,plotStat=False).to_excel(writer, "News Categories", index=False)
    except:
        pass
    try:
        catMoz(df,1,plotStat=False).to_excel(writer, "Detailed News Categories", index=False)
    except:
        pass
    try:
        plotLabelIsu(df,plotStat=False).to_excel(writer, "Label Isu", index=False)
    except:
        pass
    writer.save()
    return
