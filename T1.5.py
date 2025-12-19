import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ---------------- CONFIG ----------------
API_KEY = "26d1a0d4fcfd0879dad42e9ec6c5b158"   # Your actual OpenWeatherMap API key
CITY = "Mumbai"
UNITS = "metric"                # "metric" (Celsius), "imperial" (F), or "standard"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
# ---------------------------------------

def fetch_weather(city: str, api_key: str, units: str = "metric") -> dict:
    """
    Try fetching forecast first. If unauthorized, fall back to current weather.
    """
    params = {"q": city, "appid": api_key, "units": units}
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        if resp.status_code == 401:
            print("Forecast not available for this key, falling back to current weather...")
            resp = requests.get(WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        raise

def forecast_to_dataframe(forecast_json: dict) -> pd.DataFrame:
    """
    Convert forecast or current weather JSON to a Pandas DataFrame.
    Handles both list (forecast) and single record (current weather).
    """
    records = []

    if "list" in forecast_json:  # Forecast data
        for item in forecast_json.get("list", []):
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            wind = item.get("wind", {})
            dt_txt = item.get("dt_txt")
            records.append({
                "dt": item.get("dt"),
                "dt_txt": pd.to_datetime(dt_txt),
                "temp": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "temp_min": main.get("temp_min"),
                "temp_max": main.get("temp_max"),
                "pressure": main.get("pressure"),
                "humidity": main.get("humidity"),
                "weather_main": weather.get("main"),
                "weather_desc": weather.get("description"),
                "wind_speed": wind.get("speed"),
                "wind_deg": wind.get("deg"),
                "date": pd.to_datetime(dt_txt).date()
            })
    else:  # Current weather data
        main = forecast_json.get("main", {})
        weather = forecast_json.get("weather", [{}])[0]
        wind = forecast_json.get("wind", {})
        dt = forecast_json.get("dt")
        dt_txt = datetime.fromtimestamp(dt)
        records.append({
            "dt": dt,
            "dt_txt": dt_txt,
            "temp": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "temp_min": main.get("temp_min"),
            "temp_max": main.get("temp_max"),
            "pressure": main.get("pressure"),
            "humidity": main.get("humidity"),
            "weather_main": weather.get("main"),
            "weather_desc": weather.get("description"),
            "wind_speed": wind.get("speed"),
            "wind_deg": wind.get("deg"),
            "date": dt_txt.date()
        })

    return pd.DataFrame(records)

def plot_dashboard(df: pd.DataFrame, city: str):
    """
    Plot either forecast (multiple points) or current weather (single point).
    """
    sns.set_style("whitegrid")

    if len(df) > 1:  # Forecast data
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))
        sns.lineplot(data=df, x="dt_txt", y="temp", marker="o", ax=axes[0])
        axes[0].set_title(f"Temperature Forecast for {city}")
        axes[0].tick_params(axis="x", rotation=45)

        # Fixed plotting with proper color/marker arguments
        axes[1].plot(df["dt_txt"], df["temp"], color="red", marker="o", label="Temp")
        axes[1].plot(df["dt_txt"], df["feels_like"], color="orange", marker="x", label="Feels Like")
        axes[1].set_ylabel("Temperature (°C)")
        ax2 = axes[1].twinx()
        ax2.plot(df["dt_txt"], df["humidity"], color="blue", marker="s", label="Humidity")
        axes[1].legend(loc="upper left")
        axes[1].set_title(f"Temperature, Feels Like & Humidity – {city}")
        axes[1].tick_params(axis="x", rotation=45)

        df_box = df.copy()
        df_box["date"] = df_box["date"].astype(str)
        sns.boxplot(data=df_box, x="date", y="temp", ax=axes[2])
        axes[2].set_title(f"Temperature Distribution by Day – {city}")
        axes[2].set_xlabel("Date")
        axes[2].set_ylabel("Temperature (°C)")

        plt.tight_layout()
        plt.show()

    else:  # Current weather data
        fig, ax = plt.subplots(figsize=(8, 5))
        metrics = ["temp", "feels_like", "temp_min", "temp_max", "humidity"]
        sns.barplot(x=metrics, y=[df[m].iloc[0] for m in metrics], ax=ax)
        ax.set_title(f"Current Weather Metrics – {city}")
        ax.set_ylabel("Values")
        plt.tight_layout()
        plt.show()

def main():
    print(f"Fetching weather data for {CITY}...")
    try:
        weather_json = fetch_weather(CITY, API_KEY, UNITS)
        df = forecast_to_dataframe(weather_json)
        print("Sample of fetched data:")
        print(df.head())
        plot_dashboard(df, CITY)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
