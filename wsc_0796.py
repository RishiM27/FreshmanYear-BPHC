import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as make_subplots
import os

#  RSI 
def calculate_rsi(data, periods=14):
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=periods).mean()
    avg_loss = pd.Series(loss).rolling(window=periods).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    data['RSI'] = rsi
    return data

# MACD
def calculate_macd(data, slow_period=26, fast_period=12, signal_period=9):
    data['EMA_12'] = data['Close'].ewm(span=fast_period, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=slow_period, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['MACD_Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    return data

# Bollinger Bands
def calculate_bollinger_bands(data, window=20):
    data['SMA_20'] = data['Close'].rolling(window=window).mean()
    data['Bollinger_Upper'] = data['SMA_20'] + (2 * data['Close'].rolling(window=window).std())
    data['Bollinger_Lower'] = data['SMA_20'] - (2 * data['Close'].rolling(window=window).std())
    return data

data_dir = r'C:\Users\DUDU\Downloads\drive-download-20240903T191432Z-001'
stock_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
stock_data_with_indicators = {}

for files in stock_files:
    file_path = os.path.join(data_dir, files)
    stock_data = pd.read_csv(file_path, parse_dates=['Date'])
    stock_data = calculate_rsi(stock_data)
    stock_data = calculate_macd(stock_data)
    stock_data = calculate_bollinger_bands(stock_data)

    stock_data_with_indicators[files] = stock_data

# Finding top stocks
top_stocks = []

for stock, data in stock_data_with_indicators.items():
    latest_data = data.iloc[-1]
    rsi = latest_data['RSI']
    macd = latest_data['MACD']
    macd_signal = latest_data['MACD_Signal']
# CRITERIA LIST:
# RSI between 40 and 60, and MACD just crossed above MACD_Signal
    if 40 < rsi < 60 and macd> macd_signal:
        top_stocks.append((stock, rsi, macd, macd_signal))
# Sorting stocks via MACD - MACD Signal difference (strongest signal first)
top_stocks_sorted = sorted(top_stocks, key=lambda x: x[2] - x[3], reverse=True)
#Selecting top 3-4 stocks
top_3_to_4_stocks = top_stocks_sorted[:4]
print("Top 3 to 4 Stocks:")
for stock in top_3_to_4_stocks:
    print(f"{stock[0]}: RSI={stock[1]:.2f}, MACD Signal={stock[3]:.2f}")

# Plotting Function
def plot_stock_with_indicators(stock_name, stock_data):
    fig = make_subplots.make_subplots(rows=3, cols=1, shared_xaxes=True,
                                      vertical_spacing=0.1,
                                      subplot_titles=(f'{stock_name} Closing Price with Bollinger Bands',
                                                      'RSI', 'MACD'))
    
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Bollinger_Upper'],
                             line=dict(color='rgba(173, 216, 230, 0.4)'), name='Upper Bollinger Band'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Bollinger_Lower'],
                             line=dict(color='rgba(173, 216, 230, 0.4)'), name='Lower Bollinger Band'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Close'], 
                             line=dict(color='blue', width=1.5), name='Closing Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['RSI'], 
                             line=dict(color='red'), name='RSI'), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['MACD'], 
                             line=dict(color='green'), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['MACD_Signal'], 
                             line=dict(color='orange'), name='MACD Signal'), row=3, col=1)

    fig.update_layout(title=f'{stock_name} Stock Analysis', showlegend=False, height=800)
    
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    
    fig.show()

for stock in stock_files:
    stock_name = stock.replace('.csv', '')
    plot_stock_with_indicators(stock_name, stock_data_with_indicators[stock])
