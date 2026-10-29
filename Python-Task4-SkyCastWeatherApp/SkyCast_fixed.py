import os
import datetime
import requests
import customtkinter as ctk
from dotenv import load_dotenv

# SkyCast - Weather App
# Keep your API key in a .env file: API_KEY=your_openweathermap_api_key

load_dotenv(r"C:\Users\aakan\OneDrive\Desktop\SkyCast\.env")
API_KEY = os.getenv("API_KEY")

BG = "#080F1F"
PANEL = "#111D33"
CARD = "#1C2D49"
ACCENT = "#60A5FA"
PALE_BLUE = "#BFDBFE"
MUTED = "#94A3B8"
WHITE = "#F8FAFC"
GREEN = "#34D399"
RED = "#F87171"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("SkyCast - Weather App")
app.geometry("950x800")
app.minsize(850, 700)
app.configure(fg_color=BG)
content_frame = ctk.CTkScrollableFrame(
    app,
    fg_color=BG,
    corner_radius=0
)
content_frame.pack(fill="both", expand=True)

current_temp_c = None
use_fahrenheit = False
recent_cities = []


def weather_emoji_from_code(code):
    if code == 0:
        return "☀️"
    if code == 1:
        return "🌤️"
    if code == 2:
        return "⛅"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 56, 57):
        return "🌦️"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌤️"


def weather_emoji_from_main(main):
    mapping = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Haze": "🌫️",
    }
    return mapping.get(main, "🌤️")


def toggle_temperature():
    global use_fahrenheit
    if current_temp_c is None:
        return

    use_fahrenheit = not use_fahrenheit
    if use_fahrenheit:
        temperature_label.configure(
            text=f"{(current_temp_c * 9 / 5) + 32:.1f}°F"
        )
        unit_button.configure(text="Switch to °C")
    else:
        temperature_label.configure(text=f"{current_temp_c:.1f}°C")
        unit_button.configure(text="Switch to °F")


def update_recent_cities(city):
    city = city.strip()
    if not city:
        return
    recent_cities[:] = [item for item in recent_cities if item.lower() != city.lower()]
    recent_cities.insert(0, city)
    del recent_cities[5:]

    for child in recent_buttons_frame.winfo_children():
        child.destroy()

    for item in recent_cities:
        ctk.CTkButton(
            recent_buttons_frame,
            text=item,
            width=90,
            height=26,
            corner_radius=13,
            fg_color=CARD,
            hover_color="#2B4266",
            text_color=PALE_BLUE,
            font=("Segoe UI", 11),
            command=lambda name=item: search_recent_city(name),
        ).pack(side="left", padx=(0, 6))


def search_recent_city(city):
    city_entry.delete(0, "end")
    city_entry.insert(0, city)
    get_weather()


def render_hourly(hourly, current_time):
    for child in hourly_items_frame.winfo_children():
        child.destroy()

    future_indices = [
        i for i, value in enumerate(hourly["time"]) if value > current_time
    ][:6]

    if not future_indices:
        ctk.CTkLabel(
            hourly_items_frame,
            text="Hourly forecast is not available right now.",
            text_color=MUTED,
            font=("Segoe UI", 12),
        ).pack(anchor="w")
        return

    for index in future_indices:
        hour = hourly["time"][index][-5:]
        temp = hourly["temperature_2m"][index]
        emoji = weather_emoji_from_code(hourly["weather_code"][index])

        item = ctk.CTkFrame(hourly_items_frame, fg_color="transparent")
        item.pack(side="left", expand=True, fill="x", padx=4)

        ctk.CTkLabel(
            item,
            text=hour,
            font=("Segoe UI", 11, "bold"),
            text_color=PALE_BLUE,
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            item,
            text=emoji,
            font=("Segoe UI Emoji", 21),
        ).pack(pady=1)

        ctk.CTkLabel(
            item,
            text=f"{temp:.0f}°",
            font=("Segoe UI", 12, "bold"),
            text_color=WHITE,
        ).pack(pady=(2, 0))


def render_daily(daily):
    for child in daily_cards_frame.winfo_children():
        child.destroy()

    count = min(5, len(daily["time"]))
    for index in range(count):
        date_value = datetime.datetime.strptime(
            daily["time"][index], "%Y-%m-%d"
        )
        day = "Today" if index == 0 else date_value.strftime("%a")

        emoji = weather_emoji_from_code(daily["weather_code"][index])
        maximum = daily["temperature_2m_max"][index]
        minimum = daily["temperature_2m_min"][index]

        day_card = ctk.CTkFrame(
            daily_cards_frame,
            fg_color=CARD,
            corner_radius=16,
            height=155,
            border_width=1,
            border_color="#263B5C",
        )
        day_card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        day_card.pack_propagate(False)

        ctk.CTkLabel(
            day_card,
            text=day,
            font=("Segoe UI", 13, "bold"),
            text_color=PALE_BLUE,
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            day_card,
            text=emoji,
            font=("Segoe UI Emoji", 29),
        ).pack(pady=3)

        ctk.CTkLabel(
            day_card,
            text=f"{maximum:.0f}°  /  {minimum:.0f}°",
            font=("Segoe UI", 12, "bold"),
            text_color=WHITE,
        ).pack(pady=(5, 2))

        ctk.CTkLabel(
            day_card,
            text="High / Low",
            font=("Segoe UI", 10),
            text_color=MUTED,
        ).pack(pady=(0, 7))


def get_weather():
    global current_temp_c

    city = city_entry.get().strip()
    if not city:
        status_label.configure(
            text="Please enter a city name.", text_color=RED
        )
        return

    if not API_KEY:
        status_label.configure(
            text="API key not found. Check your .env file.", text_color=RED
        )
        return

    status_label.configure(text="Fetching weather...", text_color=ACCENT)
    search_button.configure(state="disabled")

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": API_KEY, "units": "metric"},
            timeout=10,
        )

        if response.status_code == 404:
            status_label.configure(
                text="City not found. Please try again.", text_color=RED
            )
            return

        response.raise_for_status()
        data = response.json()

        city_label.configure(text=f"{data['name']}, {data['sys'].get('country', '')}")
        current_temp_c = data["main"]["temp"]
        if use_fahrenheit:
            temperature_label.configure(
                text=f"{(current_temp_c * 9 / 5) + 32:.1f}°F"
            )
            unit_button.configure(text="Switch to °C")
        else:
            temperature_label.configure(text=f"{current_temp_c:.1f}°C")
            unit_button.configure(text="Switch to °F")

        main_condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"].title()
        icon = weather_emoji_from_main(main_condition)
        condition_label.configure(text=f"{icon}  {description}")
        weather_icon_label.configure(text=icon)
        humidity_label.configure(text=f"💧  Humidity  {data['main']['humidity']}%")
        wind_label.configure(text=f"🌬️  Wind  {data['wind']['speed']} m/s")

        forecast_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "current": "temperature_2m",
                "hourly": "temperature_2m,precipitation_probability,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=10,
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        render_hourly(
            forecast_data["hourly"],
            forecast_data["current"]["time"],
        )
        render_daily(forecast_data["daily"])
        recent_section.pack(pady=(0, 8), anchor="center")
        welcome_frame.pack_forget()
        weather_card.pack(fill="x", padx=100, pady=(0, 12))
        hourly_panel.pack(fill="x", padx=50, pady=(0, 10))
        daily_panel.pack(fill="x", padx=50, pady=(0, 12))

        update_recent_cities(data["name"])
        status_label.configure(text="Weather updated successfully!", text_color=GREEN)

    except requests.Timeout:
        status_label.configure(
            text="Request timed out. Please try again.", text_color=RED
        )
    except requests.HTTPError:
        status_label.configure(
            text="Unable to fetch weather. Check your API key or try again.",
            text_color=RED,
        )
    except (requests.RequestException, KeyError, ValueError) as error:
        status_label.configure(
            text="Forecast unavailable. Check your connection and try again.",
            text_color=RED,
        )
    finally:
        search_button.configure(state="normal")


# Header
title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
title_frame.pack(pady=(12, 0))

ctk.CTkLabel(
    title_frame, text="🌤️", font=("Segoe UI Emoji", 29)
).pack(side="left", padx=(0, 6))

ctk.CTkLabel(
    title_frame, text="Sky", font=("Segoe UI", 32, "bold"), text_color=WHITE
).pack(side="left")

ctk.CTkLabel(
    title_frame, text="Cast", font=("Segoe UI", 32, "bold"), text_color=ACCENT
).pack(side="left")


ctk.CTkLabel(
    content_frame,
    text="Your Weather, Our Priority",
    font=("Segoe UI", 13),
    text_color="#CBD5E1",
).pack(pady=(0, 10))


# Search row
search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
search_frame.pack(pady=(0, 2))



city_entry = ctk.CTkEntry(
    search_frame,
    width=330,
    height=40,
    placeholder_text="Enter city name",
    font=("Segoe UI", 14),
)

city_entry.pack(side="left", padx=(0, 10))
city_entry.bind("<Return>", lambda event: get_weather())

search_button = ctk.CTkButton(
    search_frame,
    text="Search",
    width=100,
    height=40,
    font=("Segoe UI", 13, "bold"),
    command=get_weather,
)
search_button.pack(side="left")

status_label = ctk.CTkLabel(content_frame,
    text="Enter a city to check the weather.",
    font=("Segoe UI", 11),
    text_color=MUTED,
)
status_label.pack(pady=(4, 0))


# Welcome section
welcome_frame = ctk.CTkFrame(
    content_frame,
    fg_color=PANEL,
    corner_radius=24,
    border_width=1,
    border_color="#263B5C",
    height=240,
)
welcome_frame.pack(fill="x", padx=100, pady=(24, 18))
welcome_frame.pack_propagate(False)

ctk.CTkLabel(
    welcome_frame,
    text="🌤️",
    font=("Segoe UI Emoji", 64),
).pack(pady=(20, 4))

ctk.CTkLabel(
    welcome_frame,
    text="Your Weather Starts Here",
    font=("Segoe UI", 23, "bold"),
    text_color=WHITE,
).pack(pady=(0, 6))

ctk.CTkLabel(
    welcome_frame,
    text="Search your city to discover its weather",
    font=("Segoe UI", 13),
    text_color=MUTED,
).pack()

# Recent searches
recent_section = ctk.CTkFrame(content_frame, fg_color="transparent")
recent_section.pack_forget()

ctk.CTkLabel(
    recent_section,
    text="Recent Searches",
    font=("Segoe UI", 11, "bold"),
    text_color=MUTED,
).pack(side="left", padx=(0, 10))

recent_buttons_frame = ctk.CTkFrame(
    recent_section,
    fg_color="transparent"
)
recent_buttons_frame.pack(side="left")

# Current weather card
weather_card = ctk.CTkFrame(content_frame,
    fg_color=PANEL,
    corner_radius=26,
    border_width=1,
    border_color="#263B5C",
    height=285,
)
weather_card.pack(fill="x", padx=100, pady=(0, 12))
weather_card.pack_propagate(False)
weather_card.pack_forget()

city_label = ctk.CTkLabel(
    weather_card,
    text="Your City",
    font=("Segoe UI", 21, "bold"),
    text_color=WHITE,
)
city_label.pack(pady=(12, 0))

temperature_label = ctk.CTkLabel(
    weather_card,
    text="--°C",
    font=("Segoe UI", 55, "bold"),
    text_color=ACCENT,
)
temperature_label.pack(pady=(0, 0))

unit_button = ctk.CTkButton(
    weather_card,
    text="Switch to °F",
    width=105,
    height=29,
    corner_radius=14,
    command=toggle_temperature,
)
unit_button.pack(pady=(0, 4))

condition_label = ctk.CTkLabel(
    weather_card,
    text="Weather condition",
    font=("Segoe UI", 14),
    text_color="#E2E8F0",
)
condition_label.pack(pady=(0, 0))

weather_icon_label = ctk.CTkLabel(
    weather_card,
    text="🌤️",
    font=("Segoe UI Emoji", 38),
)
weather_icon_label.pack(pady=(0, 0))

details_frame = ctk.CTkFrame(weather_card, fg_color="transparent")
details_frame.pack(pady=(0, 6))

humidity_label = ctk.CTkLabel(
    details_frame,
    text="💧  Humidity  --%",
    font=("Segoe UI", 12, "bold"),
    text_color=PALE_BLUE,
    fg_color=CARD,
    corner_radius=12,
    width=190,
    height=34,
)
humidity_label.pack(side="left", padx=5)

wind_label = ctk.CTkLabel(
    details_frame,
    text="🌬️  Wind  -- m/s",
    font=("Segoe UI", 12, "bold"),
    text_color=PALE_BLUE,
    fg_color=CARD,
    corner_radius=12,
    width=190,
    height=34,
)
wind_label.pack(side="left", padx=5)

# Hourly forecast: one subtle panel, no individual cards
hourly_panel = ctk.CTkFrame(content_frame,
    fg_color=PANEL,
    corner_radius=20,
    border_width=1,
    border_color="#263B5C",
)
hourly_panel.pack(fill="x", padx=50, pady=(0, 10))
hourly_panel.pack_forget()

ctk.CTkLabel(
    hourly_panel,
    text="☁  HOURLY FORECAST  ·  NEXT 6 HOURS",
    font=("Segoe UI", 15, "bold"),
    text_color=ACCENT,
).pack(anchor="w", padx=16, pady=(10, 2))

hourly_items_frame = ctk.CTkFrame(hourly_panel, fg_color="transparent")
hourly_items_frame.pack(fill="x", padx=10, pady=(2, 10))

# Five-day forecast: larger, separate cards
daily_panel = ctk.CTkFrame(content_frame,
    fg_color=PANEL,
    corner_radius=22,
    border_width=1,
    border_color="#263B5C",
)
daily_panel.pack(fill="x", padx=50, pady=(0, 12))
daily_panel.pack_forget()

ctk.CTkLabel(
    daily_panel,
    text="▦  5-DAY FORECAST",
    font=("Segoe UI", 16, "bold"),
    text_color=ACCENT,
).pack(anchor="w", padx=16, pady=(12, 2))

daily_cards_frame = ctk.CTkFrame(daily_panel, fg_color="transparent")
daily_cards_frame.pack(fill="x", padx=10, pady=(0, 10))

# Hide weather results until search
weather_card.pack_forget()
hourly_panel.pack_forget()
daily_panel.pack_forget()

app.mainloop()
