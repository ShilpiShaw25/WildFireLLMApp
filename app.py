import streamlit as st
import requests
import json

from config import COUNTRY_CODES, WEATHER_API_KEY


def create_url(country_code: str, city: str) -> str:
    return f'http://api.openweathermap.org/data/2.5/weather?q={city}, {country_code} usa&APPID={WEATHER_API_KEY}'



def get_weather_data(url: str):
    r = requests.get(url)
    response = getattr(r,'_content').decode("utf-8")
    response = json.loads(response)
    print(response)
    return response["main"], response["wind"], response["clouds"]

# set a title
st.title("Wild Fire Prediction")

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
        main_data, wind_data, cloud_data = get_weather_data(weather_url)
        col1, col2= st.columns(2)
        with col1:
            st.subheader("Main Weather Data")
            st.write(main_data)
        with col2:
            st.subheader("Wind and Cloud Data")
            st.write(wind_data)
            st.write(cloud_data)