import streamlit as st
import requests
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

API_URL = "https://budget-travel-ai-api.onrender.com/api/search"
GEOCODE_URL = "https://budget-travel-ai-api.onrender.com/api/geocode"

st.set_page_config(page_title="Budget Travel AI", page_icon="🧳", layout="wide")

st.title("🧳 Budget Travel AI")
st.caption("Find budget-friendly places near you using Google Places API")

# --- Location selection (outside the form, since it needs live interaction) ---
st.subheader("📍 Where are you searching?")
location_mode = st.radio(
    "Choose location method:",
    ["Use my current location", "Type a place name"],
    horizontal=True,
)

lat, lng = None, None

if location_mode == "Use my current location":
    loc = streamlit_geolocation()
    if loc and loc.get("latitude"):
        lat, lng = loc["latitude"], loc["longitude"]
        st.success(f"Detected: {lat:.4f}, {lng:.4f}")
    else:
        st.info("Click the location icon above and allow permission.")
else:
    place_name = st.text_input("Enter a place name", placeholder="e.g. Kolkata, Howrah Bridge")
    if place_name:
        try:
            geo_resp = requests.get(GEOCODE_URL, params={"place": place_name}, timeout=10)
            geo_resp.raise_for_status()
            matches = geo_resp.json().get("matches", [])
            if matches:
                options = [m["formatted_address"] for m in matches]
                choice = st.selectbox("Did you mean:", options)
                selected = next(m for m in matches if m["formatted_address"] == choice)
                lat, lng = selected["lat"], selected["lng"]
            else:
                st.warning("No matching places found.")
        except requests.exceptions.RequestException as e:
            st.error(f"Couldn't reach the geocoding service: {e}")

st.divider()

# --- Search form ---
with st.form("search_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input("What are you looking for?", placeholder="e.g. budget restaurants, cheap hotels")
    with col2:
        max_budget_level = st.selectbox(
            "Max budget level",
            options=[0, 1, 2, 3, 4],
            index=1,
            format_func=lambda x: {
                0: "Free only",
                1: "Inexpensive",
                2: "Moderate",
                3: "Expensive",
                4: "Very expensive",
            }[x],
        )

    radius = st.slider("Search radius (meters)", 500, 20000, 5000, step=500)

    submitted = st.form_submit_button("🔍 Search")

# --- Handle search ---
if submitted:
    if not query:
        st.warning("Please enter a search query.")
    elif lat is None or lng is None:
        st.warning("Please set a location first (detect your location or type a place name above).")
    else:
        with st.spinner("Searching for budget-friendly places..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "query": query,
                        "lat": lat,
                        "lng": lng,
                        "radius": radius,
                        "max_budget_level": max_budget_level,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])

                st.success(f"Found {len(results)} budget-friendly places")

                if results:
                    map_data = pd.DataFrame([
                        {
                            "lat": p["location"]["latitude"],
                            "lon": p["location"]["longitude"],
                        }
                        for p in results
                        if "location" in p
                    ])
                    if not map_data.empty:
                        st.map(map_data, size=20)

                    for p in results:
                        name = p.get("displayName", {}).get("text", "Unknown")
                        address = p.get("formattedAddress", "No address available")
                        rating = p.get("rating", "N/A")
                        price = p.get("priceLevel", "N/A").replace("PRICE_LEVEL_", "").title()

                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.subheader(name)
                                st.write(address)
                            with c2:
                                st.metric("Rating", rating)
                                st.write(f"💰 {price}")
                else:
                    st.info("No places found matching your budget. Try increasing the budget level or radius.")

            except requests.exceptions.RequestException as e:
                st.error(f"Couldn't reach the backend API: {e}")
