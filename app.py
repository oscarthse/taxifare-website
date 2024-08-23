import streamlit as st
import datetime
import requests
import folium
import openrouteservice
from streamlit_folium import st_folium

st.markdown('''
# Taxi Fare Calculator
## Please enter the following details
''')

# Inputs for the pickup and dropoff locations
pickup_lat = st.number_input(
    "Insert pickup latitude", value=40.7128, format="%.6f"
)
pickup_lon = st.number_input(
    "Insert pickup longitude", value=-74.0060, format="%.6f"
)
dropoff_lat = st.number_input(
    "Insert dropoff latitude", value=40.730610, format="%.6f"
)
dropoff_lon = st.number_input(
    "Insert dropoff longitude", value=-73.935242, format="%.6f"
)

# Inputs for date, time, and passenger count
date = st.date_input("Enter pickup date", datetime.date(2024, 8, 23))
time = st.time_input("Enter pickup time", datetime.time(14, 0))
passenger_count = st.slider(
    "Insert passenger count", min_value=1, max_value=10, step=1, value=1
)

# URL for the taxi fare prediction API
url = 'https://taxifare.lewagon.ai/predict'

# Parameters for the API request
params = {
    'pickup_datetime': f'{date} {time}',
    'pickup_longitude': pickup_lon,
    'pickup_latitude': pickup_lat,
    'dropoff_longitude': dropoff_lon,
    'dropoff_latitude': dropoff_lat,
    'passenger_count': passenger_count
}

# OpenRouteService API Key
API_KEY = '5b3ce3597851110001cf624855b77fc5114b4000a0d284319d1845f0'
client = openrouteservice.Client(key=API_KEY)

# Button to calculate the route and fare
if st.button("Calculate Fare"):
    try:
        # Coordinates should be in [longitude, latitude] format
        coords = [[pickup_lon, pickup_lat], [dropoff_lon, dropoff_lat]]

        # Get the route between the two points
        route = client.directions(coords)
        route_geometry = route['routes'][0]['geometry']
        decoded_route = openrouteservice.convert.decode_polyline(route_geometry)

        # Store the map in the session state to persist it across reruns
        m = folium.Map(location=[pickup_lat, pickup_lon], zoom_start=13)
        folium.PolyLine(locations=decoded_route['coordinates'], color='blue', weight=5).add_to(m)
        folium.Marker(location=[pickup_lat, pickup_lon], popup='Start').add_to(m)
        folium.Marker(location=[dropoff_lat, dropoff_lon], popup='End').add_to(m)

        # Save the map and fare result in session state
        st.session_state['map'] = m
        query = requests.get(url=url, params=params).json()
        st.session_state['fare'] = query['fare']

    except openrouteservice.exceptions.ApiError as e:
        st.error(f"OpenRouteService API Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Render the map if it's in session state
if 'map' in st.session_state:
    st_folium(st.session_state['map'], width=700, height=500)

# Display the fare if it's in session state
if 'fare' in st.session_state:
    st.write(f"Estimated Fare: ${st.session_state['fare']:.2f}")
