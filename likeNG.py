from livefunc import *

selectedOpsi= selectApp()
headCont = st.beta_container()
with headCont:
    header()
    about()
if selectedOpsi == appOpsi[0]:
    newsHead()
    newsAppOpsi()
elif selectedOpsi == appOpsi[1]:
    twitterHead()
    twitterAppOpsi()
