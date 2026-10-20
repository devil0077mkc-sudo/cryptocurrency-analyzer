import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
coins = input("Enter the symbol of Cryptocurrency to track (e.g. BTC): ")

url = f"https://api.coingecko.com/api/v3/coins/{coins}/market_chart?vs_currency=usd&days=30&interval=daily"
response = requests.get(url)


# now cleaning data and coverting to dataframes
data = response.json()

prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])

prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
volumes["timestamp"] = pd.to_datetime(volumes["timestamp"], unit="ms")

df = prices.merge(volumes, on="timestamp").set_index("timestamp")
# print(df.to_string())

# moving averages
df["sma_7"] = df["price"].rolling(window=7).mean()

# daily returns
df["daily_returns"] = df["price"].pct_change() * 100

# volatility
volatility = np.std(df["daily_returns"].dropna())

# print(df.round(2).to_string())
# print(f"volatility : {volatility:.2f}%")

# ploting charts
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
)
ax1.plot(df.index, df["price"], label="Price (USD)", linewidth=2)
ax1.plot(df.index, df["sma_7"], label="7-Day-SMA", linestyle="--")
ax1.set_title(f"{coins} - 30 Day Trend| Volatility: {volatility:.2f}%")
ax1.set_ylabel("Price(USD)")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.bar(df.index, df["volume"], width=0.8, color="gray")
ax2.set_ylabel("Volume")
ax2.grid(alpha=0.3)

ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig("crypto_analysis.png", dpi=150)
plt.show()
