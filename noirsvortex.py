import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import textwrap

def get_stock_data(ticker, period='1y'):
    """
    Fetch stock data from Yahoo Finance
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

def analyze_trend(data, ticker):
    """
    Analyze the stock trend and generate explanations
    """
    explanations = []
    
    # Basic information
    current_price = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100
    
    explanations.append(f"Current Price: ${current_price:.2f}")
    explanations.append(f"Daily Change: {'+' if price_change >= 0 else ''}{price_change:.2f} ({'+' if pct_change >= 0 else ''}{pct_change:.2f}%)")
    
    # 50-day and 200-day moving averages
    if len(data) >= 200:
        ma_50 = data['Close'].rolling(window=50).mean()
        ma_200 = data['Close'].rolling(window=200).mean()
        
        current_ma50 = ma_50.iloc[-1]
        current_ma200 = ma_200.iloc[-1]
        
        explanations.append(f"\n50-day Average: ${current_ma50:.2f}")
        explanations.append(f"200-day Average: ${current_ma200:.2f}")
        
        # Golden/Death cross analysis
        if ma_50.iloc[-1] > ma_200.iloc[-1] and ma_50.iloc[-2] <= ma_200.iloc[-2]:
            explanations.append("\n🌟 Golden Cross detected! This is a bullish signal where the 50-day average crosses above the 200-day average, often indicating a potential upward trend.")
        elif ma_50.iloc[-1] < ma_200.iloc[-1] and ma_50.iloc[-2] >= ma_200.iloc[-2]:
            explanations.append("\n⚠️ Death Cross detected! This is a bearish signal where the 50-day average crosses below the 200-day average, often indicating a potential downward trend.")
    
    # Recent performance
    week_ago = data.index[-1] - timedelta(days=7)
    if week_ago in data.index:
        week_ago_price = data.loc[week_ago, 'Close']
        week_change = (current_price - week_ago_price) / week_ago_price * 100
        explanations.append(f"\n1-week change: {'+' if week_change >= 0 else ''}{week_change:.2f}%")
    
    month_ago = data.index[-1] - timedelta(days=30)
    if month_ago in data.index:
        month_ago_price = data.loc[month_ago, 'Close']
        month_change = (current_price - month_ago_price) / month_ago_price * 100
        explanations.append(f"1-month change: {'+' if month_change >= 0 else ''}{month_change:.2f}%")
    
    year_ago = data.index[-1] - timedelta(days=365)
    if year_ago in data.index:
        year_ago_price = data.loc[year_ago, 'Close']
        year_change = (current_price - year_ago_price) / year_ago_price * 100
        explanations.append(f"1-year change: {'+' if year_change >= 0 else ''}{year_change:.2f}%")
    
    # Support and resistance levels (simplified)
    if len(data) >= 20:
        support = data['Close'].tail(20).min()
        resistance = data['Close'].tail(20).max()
        explanations.append(f"\nRecent Support (low): ${support:.2f}")
        explanations.append(f"Recent Resistance (high): ${resistance:.2f}")
        
        if current_price >= resistance * 0.98:
            explanations.append("\n⚠️ Note: The price is near resistance. This might be a challenging level to break through.")
        elif current_price <= support * 1.02:
            explanations.append("\n⚠️ Note: The price is near support. This might be a level where the price finds buyers.")
    
    # Volume analysis
    avg_volume = data['Volume'].mean()
    recent_volume = data['Volume'].iloc[-1]
    volume_ratio = recent_volume / avg_volume
    
    explanations.append(f"\nRecent Trading Volume: {recent_volume:,} shares")
    explanations.append(f"Average Volume: {avg_volume:,.0f} shares")
    
    if volume_ratio > 1.5:
        explanations.append("\n📈 Higher than average volume recently. Significant volume can confirm price movements - more buyers/sellers are participating.")
    elif volume_ratio < 0.7:
        explanations.append("\n📉 Lower than average volume recently. Low volume might mean less conviction in the current price movement.")
    
    return "\n".join(explanations)

def plot_stock_data(data, ticker):
    """
    Create visualizations of the stock data
    """
    plt.figure(figsize=(14, 10))
    
    # Price chart
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['Close'], label='Closing Price', color='blue')
    
    # Add moving averages if we have enough data
    if len(data) >= 50:
        ma_50 = data['Close'].rolling(window=50).mean()
        plt.plot(data.index, ma_50, label='50-day MA', color='orange', linestyle='--')
    
    if len(data) >= 200:
        ma_200 = data['Close'].rolling(window=200).mean()
        plt.plot(data.index, ma_200, label='200-day MA', color='red', linestyle='--')
    
    plt.title(f'{ticker} Stock Price and Trends')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)
    
    # Format x-axis for dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    # Volume chart
    plt.subplot(2, 1, 2)
    plt.bar(data.index, data['Volume'], color='gray', alpha=0.7)
    plt.title('Trading Volume')
    plt.ylabel('Volume')
    plt.xlabel('Date')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def main():
    print("Stock Market Analyzer")
    print("---------------------")
    
    ticker = input("Enter stock ticker (e.g., AAPL, MSFT, TSLA): ").upper()
    period = input("Enter time period to analyze (1m, 3m, 6m, 1y, 2y, 5y, max): ") or '1y'
    
    try:
        data = get_stock_data(ticker, period)
        if data.empty:
            print(f"\nNo data found for {ticker}. Please check the ticker symbol.")
            return
        
        print("\nFetching data and analyzing trends...\n")
        
        # Generate analysis
        analysis = analyze_trend(data, ticker)
        
        # Print analysis with wrapping for better readability
        print("Stock Analysis Summary:")
        print("-----------------------")
        for line in analysis.split('\n'):
            print("\n".join(textwrap.wrap(line, width=80)))
        
        # Plot the data
        plot_stock_data(data, ticker)
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()