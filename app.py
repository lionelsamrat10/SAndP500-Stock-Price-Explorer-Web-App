import streamlit as st
import yfinance as yf
import pandas as pd
import base64
import matplotlib.pyplot as plt

# Title of the App
st.title("S&P 500 Stock Price Explorer")

# Description of the App
st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, matplotlib, yfinance
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
* **Created by: Samrat Mitra** [(lionelsamrat10)](https://github.com/lionelsamrat10/)
""")

# Creating a Sidebar
st.sidebar.header('User Input Features')

# Web scraping of S&P 500 data from Wikipedia
@st.cache
def load_data():
    # Take the url, from where you want to scrape the data
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    # html[0] means the first table from the website
    # We are storing that table as a Pandas Dataframe object
    df = html[0]
    return df

# Call the Function and create the Dataframe
df = load_data()

# Examining the Sectors (There are mostly 11 sectors in the S&P500 data)
# Get the Unique Sectors 
sectors_unique = df['GICS Sector'].unique()

# Aggregate the data
sector = df.groupby('GICS Sector')

# Sidebar - Sector Selection
sorted_sector_unique = sorted(sectors_unique)

# Get the selected sector
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering the data from the selected sectors in the sidebar
df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header('Display companies in the Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download S&P500 data in .csv format
# This function creates a hyperlink in our web app to download the data
def file_download(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(file_download(df_selected_sector), unsafe_allow_html=True)

# Let us use yfinance to download the stock data
data = yf.download(
        tickers = list(df_selected_sector[:10].Symbol),
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )
st.set_option('deprecation.showPyplotGlobalUse', False)
# Plot Closing Price of Query Symbol
def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot()

num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)