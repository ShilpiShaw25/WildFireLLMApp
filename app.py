import streamlit as st
import requests
import json

from config import COUNTRY_CODES, WEATHER_API_KEY
from rag import generate_answer

IMAGE_ADDRESS = "https://blog.nhstateparks.org/wp-content/uploads/2023/09/canada-wildfire-rt-lv-230605_1686011446619_hpMain_16x9_1600.jpeg"
CONTEXT_TEMPLATE = """
Weather condition of the city {city} is {weather_condition}.
Tempertaure is {temp}. Temperature feels link {temp_feel}. Minimum temperature is {temp_min} while maximum temperature is {temp_max}. All the temperatures are in Kelvin.
Humidity is {humidity}%.
Pressure is {pressure} hPa.
Atmospheric pressure on the sea level {sea_level} hPa.
Atmospheric pressure on the ground level {ground_level} hPa.
Visibility in meters {visibility}.
Wind speed is {wind_speed} in meter/sec and direction is {wind_deg} in degrees.
Based on this weather data, is there a wildfire risk in this area?
"""


def create_url(country_code: str, city: str) -> str:
    return f'http://api.openweathermap.org/data/2.5/weather?q={city}, {country_code} usa&APPID={WEATHER_API_KEY}'



def get_weather_data(url: str):
    r = requests.get(url)
    response = getattr(r,'_content').decode("utf-8")
    response = json.loads(response)
    weather_data = response.get("weather", None)
    try:
        main_data = response["main"]
        wind_data = response["wind"]
        cloud_data = response["clouds"]
        # create a dictionary of data
        weather_dict = {}
        if weather_data:
            weather_dict["weather_condition"] = weather_data[0]["main"]
        else:
            weather_dict["weather_condition"] = "not available"
        weather_dict["temp"] = response["main"]["temp"]
        weather_dict["temp_feel"] = response["main"]["feels_like"]
        weather_dict["temp_min"] = response["main"]["temp_min"]
        weather_dict["temp_max"] = response["main"]["temp_max"]
        weather_dict["pressure"] = response["main"]["pressure"]
        weather_dict["humidity"] = response["main"]["humidity"]
        weather_dict["sea_level"] = response["main"]["sea_level"]
        weather_dict["ground_level"] = response["main"]["grnd_level"]
        weather_dict["visibility"] = response["visibility"]
        weather_dict["wind_speed"] = response["wind"]["speed"]
        weather_dict["wind_deg"] = response["wind"]["deg"]
    except Exception as error:
        weather_dict = None
        main_data = None
        wind_data = None
        cloud_data = None

    return main_data, wind_data, cloud_data, weather_data, weather_dict

# set a title
st.title("Wild Fire Prediction")

# set the image
st.image(IMAGE_ADDRESS, caption = "Wildfire")

# user needs to select type a city and select a country
st.subheader("What is the country you are living in?")

# get the country
country = st.selectbox(
    "Select Your Country",
    list(COUNTRY_CODES.keys()),
    index = None

)

if country:
    # set the text input
    city_name = st.text_input("City Name", value = None)

    if city_name:
        weather_url = create_url(COUNTRY_CODES[country], city_name)
        # get weather data
        main_data, wind_data, cloud_data, weather_data, dict_weather_data = get_weather_data(weather_url)
        if not dict_weather_data:
            st.error("Check the City Name: Cannot fetch weather data", icon = "🛑")
            st.stop()
        st.write(dict_weather_data)
        dict_weather_data["city"] = city_name
        with st.sidebar:
            if weather_data:
                st.subheader("Weather Condition")
                st.write(weather_data[0])
            st.subheader("Temperature Statistics")
            st.write(main_data)
            st.subheader("Wind and Cloud Data")
            st.write(wind_data)
            st.write(cloud_data)

        # create the query
        query = CONTEXT_TEMPLATE.format(**dict_weather_data)
        # get the answer
        with st.spinner('Getting Predictions'):
            answer = generate_answer(query, country)
            st.toast("Prediction Completed!", icon = "✅")
        st.subheader("Predictions")
        st.write(answer)