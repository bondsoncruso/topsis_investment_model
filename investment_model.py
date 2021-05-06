import pandas as pd
import streamlit as st
import requests
import numpy as np
import yfinance as yf



api_key = '3c6a61599dac605610c6c9dff5e0d742'
api_key_input = st.sidebar.text_input('API key from financial modeling prep')
api_key_button = st.sidebar.button('Submit')
if api_key_button:
    api_key = api_key_input
    
st.title('Ranking Companies with TOPSIS')

st.write('TOPSIS, known as Technique for Order of Preference by Similarity to Ideal Solution, is a multi-criteria decision analysis method. It compares a set of alternatives based on a pre-specified criterion. The method is used in the business across various industries, every time we need to make an analytical decision based on collected data.')
st.write("""
Here we are comparing several companies and finding out 
which one has the strongest financials. These companies 
are our alternatives set. To combine them together and 
decide which one is the strongest, we need to employ some reliable 
metrics. We are using indicators derived from financial statements like ROA 
(return on assets), ROE (return on equity),etc.
These indicators will form our criteria set.
\n
The logic of TOPSIS is based on the 
concept that the chosen alternative should have the shortest 
geometric distance from the best solution and the longest geometric 
distance from the worst solution.
""")
sector = st.selectbox('Select a sector',['Consumer Cyclical', 'Energy', 'Technology', 'Industrials', 'Financial Services', 'Basic Materials', 'Communication Services', 'Consumer Defensive', 'Healthcare', 'Real Estate', 'Utilities', 'Industrial Goods', 'Financial', 'Services', 'Conglomerates'],2)

marketcap = str(1000000000)

url = (f'https://financialmodelingprep.com/api/v3/stock-screener?marketCapMoreThan={marketcap}&betaMoreThan=1&volumeMoreThan=10000&sector={sector}&exchange=NASDAQ&dividendMoreThan=0&limit=1000&apikey={api_key}')

#get companies based on criteria defined about
screener = requests.get(url).json()


#add selected companies to a list
companies = []
for item in screener:
	companies.append(item['symbol'])

value_ratios ={}
#get the financial ratios
count = 0
for company in companies:
	try:
		if count <5:
			count = count + 1
			fin_ratios = requests.get(f'https://financialmodelingprep.com/api/v3/ratios-ttm/{company}?apikey={api_key}').json()
			value_ratios[company] = {}
			value_ratios[company]['ROE'] = fin_ratios[0]['returnOnEquityTTM']
			value_ratios[company]['ROA'] = fin_ratios[0]['returnOnAssetsTTM']
			value_ratios[company]['ROCE'] = fin_ratios[0]['returnOnCapitalEmployedTTM']
			value_ratios[company]['Quick_Ratio'] = fin_ratios[0]['quickRatioTTM']
			value_ratios[company]['Interest_Coverage'] = fin_ratios[0]['interestCoverageTTM']
			value_ratios[company]['Gross_Profit_Margin'] = fin_ratios[0]['grossProfitMarginTTM']
			value_ratios[company]['PB'] = fin_ratios[0]['priceToBookRatioTTM']
			value_ratios[company]['PS'] = fin_ratios[0]['priceToSalesRatioTTM']
			value_ratios[company]['PEG'] = fin_ratios[0]['pegRatioTTM']
			value_ratios[company]['PE'] = fin_ratios[0]['peRatioTTM']
			
	except:
		pass
def topsis(ratios):
    df = pd.DataFrame.from_dict(ratios,orient='index')
    df2 = np.sqrt(np.square(df).sum())
    df3 = df/df2
    columncount = df.shape[1]
    weights = np.empty([1,columncount])
    weights.fill(1/columncount)
    norm_weighted = df3 * weights
    positive_value_db = norm_weighted.iloc[:,:6]
    negative_value_db = norm_weighted.iloc[:,6:10]
    positive_solution_1db = np.max(positive_value_db)
    positive_solution_2db = np.min(negative_value_db)
    positive_solution = pd.concat([positive_solution_1db, positive_solution_2db])
    positive_solution_1db = np.min(positive_value_db)
    positive_solution_2db = np.max(negative_value_db)
    negative_solution = pd.concat([positive_solution_1db, positive_solution_2db])
    final_positive_matrix = np.sqrt(np.sum(np.square(norm_weighted-positive_solution),1))
    final_negative_matrix = np.sqrt(np.sum(np.square(norm_weighted-negative_solution),1))
    relative_closeness = final_negative_matrix/(final_negative_matrix+final_positive_matrix)
    relative_closeness = relative_closeness.sort_values(ascending=False)
    relative_closeness = relative_closeness.to_frame()
    relative_closeness.reset_index(level=0, inplace=True)
    relative_closeness.rename(columns={0:'Score','index':'Ticker'},inplace=True)
    return relative_closeness

def get_name(ticker):
    ticker = str(ticker)
    name = yf.Ticker(ticker)
    company_name = name.info['longName']
    return company_name

if st.button('Search'):
    relative_closeness = topsis(value_ratios)
    relative_closeness['Company Name'] = relative_closeness.apply(lambda row: get_name(row.Ticker), axis = 1)
    st.table(relative_closeness)

