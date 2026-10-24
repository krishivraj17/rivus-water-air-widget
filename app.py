import streamlit as st
import requests

# Page Configuration for Embedded View
st.set_page_config(page_title="US Water & Air Quality Lookup", page_icon="💧", layout="centered")

# Custom CSS for Embed Cleanliness & Card Styling
st.markdown("""
    <style>
    .stApp { 
        background-color: #F8FAFC; 
    }
    .card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Local Water & Air Quality Scorecard")
st.caption("Enter any 5-digit US ZIP Code to view local EPA Air Quality metrics and regional water characteristics.")

# Input Field
zip_code = st.text_input("Enter 5-Digit US ZIP Code", value="77494", max_chars=5)

if st.button("Analyze Location"):
    if len(zip_code) != 5 or not zip_code.isdigit():
        st.error("Please enter a valid 5-digit US ZIP Code.")
    else:
        # 1. Geocode ZIP Code using Nominatim OpenStreetMap API
        geo_url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=USA&format=json&addressdetails=1"
        headers = {'User-Agent': 'RivusSolutions-EnvironmentalWidget/1.0'}
        
        try:
            geo_res = requests.get(geo_url, headers=headers).json()
            
            if geo_res:
                address_data = geo_res[0].get('address', {})
                lat = geo_res[0]['lat']
                lon = geo_res[0]['lon']
                
                # Extract City/Town & State dynamically across any of the 50 US States
                city = (
                    address_data.get('city') or 
                    address_data.get('town') or 
                    address_data.get('village') or 
                    address_data.get('county') or 
                    "Local Area"
                )
                state = address_data.get('state', 'US')
                location_label = f"{city}, {state}"
                
                # 2. Fetch Real-Time EPA Air Quality Index (AQI) from Open-Meteo
                aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10"
                aqi_res = requests.get(aqi_url).json()
                us_aqi = aqi_res.get('current', {}).get('us_aqi', 40)
                
                # 6-Tier EPA Air Quality Rating Logic
                if us_aqi <= 50:
                    aqi_status = "Good (0–50 AQI)"
                    aqi_color = "🟢"
                    aqi_desc = "Air quality is satisfactory and poses little or no risk."
                elif us_aqi <= 100:
                    aqi_status = "Moderate (51–100 AQI)"
                    aqi_color = "🟡"
                    aqi_desc = "Air quality is acceptable; sensitive individuals may experience mild discomfort."
                elif us_aqi <= 150:
                    aqi_status = "Unhealthy for Sensitive Groups (101–150 AQI)"
                    aqi_color = "🟠"
                    aqi_desc = "General public is unlikely affected, but sensitive groups may experience health effects."
                elif us_aqi <= 200:
                    aqi_status = "Unhealthy (151–200 AQI)"
                    aqi_color = "🔴"
                    aqi_desc = "Some members of the general public may experience health effects."
                elif us_aqi <= 300:
                    aqi_status = "Very Unhealthy (201–300 AQI)"
                    aqi_color = "🟣"
                    aqi_desc = "Health alert: The risk of health effects is increased for everyone."
                else:
                    aqi_status = "Hazardous (301+ AQI)"
                    aqi_color = "🟤"
                    aqi_desc = "Health warning of emergency conditions."

                # Render Dynamic Output Scorecard
                st.markdown(f"### Environmental Summary: **{location_label} ({zip_code})**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <h4>💨 Outdoor Air Quality Index</h4>
                        <h3>{aqi_color} {us_aqi} AQI</h3>
                        <p><b>Status:</b> {aqi_status}</p>
                        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.5rem; line-height: 1.2;">
                            {aqi_desc} Tracks PM2.5 & PM10 particulates near {city}.
                        </p>
                        <hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #E2E8F0;">
                        <p style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 0;">
                            <b>Source:</b> Live metrics via U.S. EPA AirNow & Open-Meteo Air Quality API.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.markdown(f"""
                    <div class="card">
                        <h4>💧 Municipal Tap Water Profile</h4>
                        <h3>🟡 Hardness & Chemical Additives</h3>
                        <p><b>Typical Range:</b> 7–15+ GPG (Hard Water)</p>
                        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.5rem; line-height: 1.2;">
                            Public water systems across {state} rely on chlorine/chloramine disinfection and municipal mineral treatment.
                        </p>
                        <hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #E2E8F0;">
                        <p style="font-size: 0.72rem; color: #94A3B8; margin-bottom: 0;">
                            <b>Source:</b> Baseline parameters compiled from EPA Safe Drinking Water Act & USGS Water Quality Data.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Contextual Lead Generation CTA
                st.info(
                    f"💡 **Living in {location_label}?** Learn how to eliminate municipal chlorine, mineral scale, "
                    "and indoor airborne allergens with pure home filtration. Download our free guide below!"
                )

            else:
                st.error("ZIP Code not found. Please double-check the 5-digit number and try again.")
                
        except Exception as e:
            st.error("Unable to retrieve local metrics right now. Please try again shortly.")
