# dashboard/streamlit_app.py

import streamlit as st

# ─── THIS MUST BE FIRST ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="☕ Starbucks Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ────────────────────────────────────────────────────────────────────────────────

import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'].str.replace('Reviewed ', ''), errors='coerce')
    df['Polarity'] = df['Review'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['Sentiment'] = df['Polarity'].apply(
        lambda p: 'Positive' if p > 0.1 else ('Negative' if p < -0.1 else 'Neutral')
    )
    return df

df = load_data('data/Starbucks_reviews_data.csv')

st.title("☕ Starbucks Sentiment Analysis")

# Sidebar filters
st.sidebar.header("Filter reviews")
date_min, date_max = st.sidebar.date_input(
    "Date range",
    value=[df['Date'].min(), df['Date'].max()]
)
locations = st.sidebar.multiselect(
    "Location", options=df['location'].unique(), default=df['location'].unique()
)
sentiments = st.sidebar.multiselect(
    "Sentiment", options=['Positive','Neutral','Negative'], default=['Positive','Neutral','Negative']
)

# Apply filters
mask = (
    (df['Date'] >= pd.to_datetime(date_min)) &
    (df['Date'] <= pd.to_datetime(date_max)) &
    df['location'].isin(locations) &
    df['Sentiment'].isin(sentiments)
)
filtered = df[mask]

# Sentiment distribution
st.subheader("Overall Sentiment Distribution")
fig_dist = px.histogram(
    filtered, x='Sentiment', color='Sentiment', barmode='group',
    category_orders={'Sentiment': ['Positive','Neutral','Negative']},
    title="Count of Reviews by Sentiment"
)
st.plotly_chart(fig_dist, use_container_width=True)

# Monthly trend
st.subheader("Monthly Sentiment Trend")
ts = (
    filtered
    .groupby([pd.Grouper(key='Date', freq='M'), 'Sentiment'])
    .size()
    .reset_index(name='Count')
)
fig_trend = px.line(
    ts, x='Date', y='Count', color='Sentiment',
    title="Monthly Count of Reviews by Sentiment"
)
st.plotly_chart(fig_trend, use_container_width=True)

# Word cloud
st.subheader("Common Words in Reviews")
all_text = " ".join(filtered['Review'].astype(str))
wc = WordCloud(width=800, height=400, max_words=100).generate(all_text)
st.image(wc.to_array(), caption="Word Cloud", use_column_width=True)

# Sample reviews with images
st.subheader("Sample Reviews")
for _, row in filtered.sample(min(5, len(filtered)), random_state=1).iterrows():
    st.markdown(f"**{row['name']}** — {row['location']} — `{row['Date'].date()}` — *{row['Sentiment']}*")
    st.write(row['Review'])
    links = eval(row['Image_Links'])
    if links and links != ['No Images']:
        st.image(links, width=200)
    st.markdown("---")
