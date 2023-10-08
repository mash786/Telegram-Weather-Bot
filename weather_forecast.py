import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token (replace with your own)
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# OpenWeatherMap API key (replace with your own)
API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY_HERE'

# Weather condition icons
weather_icons = {
    "01d": "☀️",  # Clear sky (day)
    "01n": "🌙",  # Clear sky (night)
    "02d": "🌤️",  # Few clouds (day)
    "02n": "🌤️",  # Few clouds (night)
    "03d": "🌥️",  # Scattered clouds (day)
    "03n": "🌥️",  # Scattered clouds (night)
    "04d": "☁️",  # Broken clouds (day)
    "04n": "☁️",  # Broken clouds (night)
    "09d": "🌧️",  # Shower rain (day)
    "09n": "🌧️",  # Shower rain (night)
    "10d": "🌦️",  # Rain (day)
    "10n": "🌦️",  # Rain (night)
    "11d": "⛈️",  # Thunderstorm (day)
    "11n": "⛈️",  # Thunderstorm (night)
    "13d": "❄️",  # Snow (day)
    "13n": "❄️",  # Snow (night)
    "50d": "🌫️",  # Mist (day)
    "50n": "🌫️",  # Mist (night)
}

# Command handler for the /start command
def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Weather Bot! Please send me your city name.")

# Command handler for the /forecast command
def forecast_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Please wait while I fetch the weather forecast for the next 5 days...")

    location = context.user_data.get('location')
    if location:
        weather_data = get_weather_forecast(location)
        if weather_data:
            response = format_weather_forecast_response(weather_data)
            update.message.reply_text(response)
        else:
            update.message.reply_text("Failed to fetch weather forecast. Please try again.")
    else:
        update.message.reply_text("Location not provided. Please send your city name first using the /start command.")

# Handler for city name updates
def city_handler(update: Update, context: CallbackContext) -> None:
    city = update.message.text
    context.user_data['location'] = city

    weather_data = get_weather(city)
    if weather_data:
        response = format_weather_response(weather_data)
        update.message.reply_text(response)
        update.message.reply_text("To get the weather forecast for the next 5 days, use the /forecast command.")
    else:
        update.message.reply_text("Failed to fetch weather data. Please try again.")

# Retrieve weather data from the OpenWeatherMap API based on the city
def get_weather(city: str) -> dict:
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving weather data: {e}")
        return None

# Retrieve weather forecast data from the OpenWeatherMap API based on the city
def get_weather_forecast(city: str) -> dict:
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving weather forecast: {e}")
        return None

# Format the weather data into a user-friendly response
def format_weather_response(weather_data: dict) -> str:
    weather = weather_data['weather'][0]['description']
    icon_code = weather_data['weather'][0]['icon']
    temperature_celsius = weather_data['main']['temp']
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
    temperature_kelvin = weather_data['main']['temp'] + 273.15
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']

    response = f"Current weather in {weather_data['name']}:\n\n"
    response += f"Description: {weather_icons.get(icon_code, 'Unknown')} {weather}\n"
    response += f"Temperature (Celsius): {temperature_celsius:.2f}°C\n"
    response += f"Temperature (Fahrenheit): {temperature_fahrenheit:.2f}°F\n"
    response += f"Temperature (Kelvin): {temperature_kelvin:.2f} K\n"
    response += f"Humidity: {humidity}%\n"
    response += f"Wind Speed: {wind_speed} m/s"

    return response

# Format the weather forecast data into a user-friendly response
def format_weather_forecast_response(weather_data: dict) -> str:
    forecast_list = weather_data['list']
    response = f"Weather forecast for the next 5 days in {weather_data['city']['name']}:\n\n"

    for forecast in forecast_list[:5]:
        date = forecast['dt_txt'].split()[0]
        time = forecast['dt_txt'].split()[1]
        icon_code = forecast['weather'][0]['icon']
        temperature_celsius = forecast['main']['temp']
        temperature_fahrenheit = (temperature_celsius * 9/5) + 32
        temperature_kelvin = forecast['main']['temp'] + 273.15
        weather = forecast['weather'][0]['description']

        response += f"Date: {date}\n"
        response += f"Time: {time}\n"
        response += f"Description: {weather_icons.get(icon_code, 'Unknown')} {weather}\n"
        response += f"Temperature (Celsius): {temperature_celsius:.2f}°C\n"
        response += f"Temperature (Fahrenheit): {temperature_fahrenheit:.2f}°F\n"
        response += f"Temperature (Kelvin): {temperature_kelvin:.2f} K\n\n"

    return response

# Error handler
def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    # Create the Updater and pass in your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("forecast", forecast_command))

    # Register message handler for city name updates
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, city_handler))

    # Register error handler
    dispatcher.add_error_handler(error_handler)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process is stopped
    updater.idle()

if __name__ == '__main__':
    main()
