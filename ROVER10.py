import os
import base64
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
rover = "perseverance"

st.write(f"API_KEY loaded: {API_KEY is not None}")

cameras = [
    "FRONT_HAZCAM_LEFT",
    "FRONT_HAZCAM_RIGHT",
    "REAR_HAZCAM_LEFT",
    "REAR_HAZCAM_RIGHT",
    "NAVCAM_LEFT",
    "NAVCAM_RIGHT",
    "EDL_RUCAM",
    "EDL_DDCAM",
    "EDL_PUCAM1",
    "EDL_PUCAM2",
    "MCZ_LEFT",
    "MCZ_RIGHT",
    "SHERLOC_WATSON",
    "SKYCAM",
    "SUPERCAM_RMI",
]

# Streamlit UI
with open("mars1.jpg", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}

    .css-18e3th9, .css-1d391kg, .block-container {{
        background-color: rgba(0, 0, 0, 0) !important;
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
            <div style="display: flex; align-items: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg" width="60" style="margin-right: 15px;">
                    <h3 style="margin: 0;">
                        <span style='color:white; text-shadow: 2px 2px 4px black; '>NASA's Mars Rover</span>
                    </h3>
            </div>
            <h5 style="font-weight: normal; color: white; font-size: 14px;">
                    Images and data © NASA/JPL-Caltech.
            </h5>
            """, unsafe_allow_html=True)

st.write("Developer: Zay Bhone") 
start_date = st.date_input("Start date-YY/MM/DD")
end_date = st.date_input("End date-YY/MM/DD")
selected_cameras = st.multiselect("Select cameras", cameras)

if st.button("Search Images"):
    total_images = 0
    current_date = start_date
    while current_date <= end_date:
        earth_date = current_date.strftime("%Y-%m-%d")
        st.subheader(f"📅 {earth_date}")
        for camera in selected_cameras:
            url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos"
            params = {
                "earth_date": earth_date,
                "camera": camera,
                "api_key": API_KEY
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status() 
                data = response.json()

                if data.get("photos"):
                    photo = data["photos"][0]
                    img_url = photo["img_src"]

                    try:
                        img_response = requests.get(img_url, timeout=10)
                        img_response.raise_for_status()
                        img = Image.open(BytesIO(img_response.content))
                        st.image(img, caption=f"{camera} - {earth_date}", use_column_width=True)
                        total_images += 1
                    except requests.exceptions.RequestException as e:
                        st.error(f"⚠️ Failed to load image for {camera} on {earth_date}. Error: {e}")

                else:
                    st.info(f"[{camera}] No image found for {earth_date}")

            except requests.exceptions.HTTPError as http_err:
                st.error(f"❌ HTTP error for {camera} on {earth_date}: {http_err}")
            except requests.exceptions.RequestException as req_err:
                st.error(f"❌ Network error for {camera} on {earth_date}: {req_err}")
            except Exception as ex:
                st.error(f"❌ Unexpected error for {camera} on {earth_date}: {ex}")
        
        current_date += timedelta(days=1)

    st.success(f"Total images shown: {total_images}")
