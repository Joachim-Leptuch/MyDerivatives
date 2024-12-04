import streamlit as st

st.set_page_config(
    page_title='Option Pricer',
    page_icon="⚛",
    layout='centered',
    initial_sidebar_state="expanded"
)

### ---- PAGE SETUP ----

pricer_page = st.Page(
    page = "pages/pricer.py",
    title = "Options Pricer",
)

### ---- NAVIGATION SETUP ----
pg = st.navigation({
    "Derivatives & Exotics": [pricer_page],
})

# ---- SHARED ON ALL PAGES ----
# st.logo("link")
st.sidebar.text("Created by Joachim Leptuch.")
linkedin_url = "https://www.linkedin.com/in/joachim-l-954610212/"

st.sidebar.write("Linkedin : [Joachim Leptuch](%s)" % linkedin_url)
st.sidebar.write("Contact : joachim.leptuch@edu.escp.eu")

### ---- RUN NAVIGATION ----
pg.run()