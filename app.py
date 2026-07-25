"""
FitPulse - Sprint 1
--------------------
A simple Streamlit app that helps people find fitness centers
near them within a chosen radius (default 10 miles).

This is a beginner-friendly, high-school STEM project file.
No secret API keys or external geocoding services are used.
Instead, we use a small built-in list of sample cities and
sample fitness centers so the app works right away, anywhere.

LAYOUT NOTE: this version uses a "gym website" style layout —
a big bold hero banner up top, a row of feature cards, then the
search tool, inspired by real gym landing pages (big headline,
strong colors, card-based feature grid).
"""

import math
import streamlit as st

# ------------------------------------------------------------------
# SECTION 1: PAGE SETUP
# "wide" layout gives us room for a full-width hero banner and a
# multi-column feature grid, like a real gym website homepage.
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FitPulse",
    page_icon="💪",
    layout="wide",
)

# ------------------------------------------------------------------
# SECTION 2: BRAND STYLE (Blue, Green, White)
# This CSS block builds the "gym website" look:
#   - a bold gradient hero banner with a big headline
#   - rounded feature cards with a hover lift effect
#   - a colorful bottom call-to-action banner
# It's all optional styling — the app still works without it.
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Hide default Streamlit top padding so the hero banner
       can sit right at the top of the page, like a real site. */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* --- HERO BANNER --- */
    .fitpulse-hero {
        background: linear-gradient(135deg, #1565C0 0%, #2E7D32 100%);
        border-radius: 18px;
        padding: 48px 40px;
        text-align: center;
        color: white;
        margin-bottom: 32px;
    }
    .fitpulse-hero h1 {
        font-size: 52px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1px;
    }
    .fitpulse-hero p {
        font-size: 19px;
        margin-top: 14px;
        opacity: 0.95;
    }
    .fitpulse-hero-badge {
        display: inline-block;
        background-color: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 999px;
        padding: 6px 18px;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 16px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* --- FEATURE CARDS (grid) --- */
    .fitpulse-feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-top: 4px solid #2E7D32;
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        height: 100%;
        transition: transform 0.15s ease;
    }
    .fitpulse-feature-card .icon {
        font-size: 34px;
        margin-bottom: 8px;
    }
    .fitpulse-feature-card h4 {
        color: #1565C0;
        margin: 6px 0;
        font-size: 17px;
    }
    .fitpulse-feature-card p {
        color: #444;
        font-size: 14px;
        margin: 0;
    }

    /* --- SECTION HEADERS --- */
    .fitpulse-section-header {
        color: #1565C0;
        background-color: #E8F1FC;
        border-left: 5px solid #2E7D32;
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 22px;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 16px;
    }

    /* --- RESULT CARDS --- */
    .fitpulse-card {
        background-color: #F1F8F5;
        border: 1px solid #2E7D32;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #1B1B1B;
    }

    /* --- BOTTOM CTA BANNER --- */
    .fitpulse-cta-banner {
        background-color: #0D3B14;
        border-radius: 14px;
        padding: 32px;
        text-align: center;
        color: white;
        margin-top: 24px;
        margin-bottom: 12px;
    }
    .fitpulse-cta-banner h3 {
        font-size: 26px;
        margin: 0 0 8px 0;
    }

    /* --- Mobile responsiveness ---
       On narrow screens (phones), shrink the hero text and
       tighten padding so nothing feels cramped or overflows. */
    @media (max-width: 600px) {
        .fitpulse-hero {
            padding: 30px 18px;
        }
        .fitpulse-hero h1 {
            font-size: 32px;
        }
        .fitpulse-hero p {
            font-size: 15px;
        }
        .fitpulse-section-header {
            font-size: 18px;
            padding: 8px 12px;
        }
        .fitpulse-card {
            padding: 10px 14px;
        }
        .fitpulse-cta-banner h3 {
            font-size: 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# SECTION 3: SAMPLE DATA
# In a real product, this list would come from a database or a
# maps API. For our Sprint 1 demo, we use sample fitness centers
# with made-up coordinates so the distance math actually works.
# ------------------------------------------------------------------
FITNESS_CENTERS = [
    {"name": "Green Street Gym", "address": "12 Green St", "lat": 40.7128, "lon": -74.0060},
    {"name": "Pulse Fitness Center", "address": "88 Pulse Ave", "lat": 40.7357, "lon": -74.1724},
    {"name": "Riverside Athletic Club", "address": "5 Riverside Dr", "lat": 40.8000, "lon": -73.9500},
    {"name": "Uptown CrossFit Box", "address": "200 Uptown Blvd", "lat": 40.8448, "lon": -73.8648},
    {"name": "Downtown YMCA", "address": "1 Civic Center Plaza", "lat": 40.7000, "lon": -74.0100},
    {"name": "Harbor Health Club", "address": "45 Harbor Way", "lat": 40.6500, "lon": -74.0200},
    {"name": "Summit Strength & Cardio", "address": "310 Summit Rd", "lat": 40.9000, "lon": -74.1000},
]

# A small list of sample "user location" choices, each with
# coordinates. This stands in for a real address search box.
SAMPLE_LOCATIONS = {
    "Union City, NJ": (40.7795, -74.0237),
    "Jersey City, NJ": (40.7178, -74.0431),
    "Hoboken, NJ": (40.7440, -74.0324),
    "Newark, NJ": (40.7357, -74.1724),
    "New York, NY": (40.7128, -74.0060),
}


# ------------------------------------------------------------------
# SECTION 4: DISTANCE CALCULATION (Haversine Formula)
# This function calculates the distance in miles between two
# points on Earth using their latitude and longitude.
# We use this instead of a paid maps API.
# ------------------------------------------------------------------
def distance_in_miles(lat1, lon1, lat2, lon2):
    """Return the distance in miles between two lat/lon points."""
    radius_of_earth_miles = 3958.8

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius_of_earth_miles * c


# ------------------------------------------------------------------
# SECTION 5: HERO BANNER
# This is the big, bold "gym website" style header — a full-width
# gradient banner with a headline and short pitch, similar to the
# hero section on real gym homepages.
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="fitpulse-hero">
        <div class="fitpulse-hero-badge">Free &nbsp;•&nbsp; No Membership Required</div>
        <h1>💪 FITPULSE</h1>
        <p>Stay active. Build healthy habits. Connect with your community.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Welcome to **FitPulse**! 🎉 We help you find fitness centers near you, "
    "so staying active is easier and more affordable. Let's find a gym close to you!"
)

# ------------------------------------------------------------------
# SECTION 6: FEATURE CARD GRID
# A row of highlight cards, similar to the "Why Choose Us" feature
# grid seen on real gym websites.
# ------------------------------------------------------------------
feature_cols = st.columns(4)

features = [
    ("📍", "Gym Finder", "Locate fitness centers within your chosen radius."),
    ("👥", "Group Workouts", "Join group sessions and train with others."),
    ("🌐", "Communities", "Connect with people who share your goals."),
    ("✅", "Habit Tracking", "Build and track healthy daily habits."),
]

for col, (icon, title, text) in zip(feature_cols, features):
    with col:
        st.markdown(
            f"""
            <div class="fitpulse-feature-card">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")  # small spacer
st.divider()

# ------------------------------------------------------------------
# SECTION 7: LOCATION INPUT + SEARCH
# ------------------------------------------------------------------
st.markdown(
    '<div class="fitpulse-section-header">📍 Find a Fitness Center Near You</div>',
    unsafe_allow_html=True,
)

search_col1, search_col2 = st.columns(2)

with search_col1:
    location_choice = st.selectbox(
        "Choose your location:",
        options=list(SAMPLE_LOCATIONS.keys()),
        help="In a future version, you'll be able to type any address.",
    )

with search_col2:
    radius_miles = st.slider(
        "Search radius (miles):",
        min_value=1,
        max_value=25,
        value=10,
        help="FitPulse's Sprint 1 goal is a 10-mile search radius.",
    )

search_clicked = st.button("🔎 Find Nearby Gyms", use_container_width=True)

# ------------------------------------------------------------------
# SECTION 8: SEARCH RESULTS
# ------------------------------------------------------------------
if search_clicked:
    user_lat, user_lon = SAMPLE_LOCATIONS[location_choice]

    # Calculate distance to every gym in our sample list
    nearby_gyms = []
    for gym in FITNESS_CENTERS:
        dist = distance_in_miles(user_lat, user_lon, gym["lat"], gym["lon"])
        if dist <= radius_miles:
            nearby_gyms.append((gym, dist))

    # Sort so the closest gym shows up first
    nearby_gyms.sort(key=lambda pair: pair[1])

    if nearby_gyms:
        st.success(f"✅ Found {len(nearby_gyms)} fitness center(s) near {location_choice}!")
        result_cols = st.columns(2)
        for index, (gym, dist) in enumerate(nearby_gyms):
            with result_cols[index % 2]:
                st.markdown(
                    f"""
                    <div class="fitpulse-card">
                    <b>🏋️ {gym['name']}</b><br>
                    📍 {gym['address']}<br>
                    📏 {dist:.1f} miles away
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.error(
            "❌ No fitness centers found in that radius. "
            "Try increasing your search radius or choosing a different location."
        )

st.divider()

# ------------------------------------------------------------------
# SECTION 9: FUTURE FEATURES
# ------------------------------------------------------------------
st.markdown(
    '<div class="fitpulse-section-header">🚀 Coming Soon to FitPulse</div>',
    unsafe_allow_html=True,
)
st.write(
    """
- 🤝 **Workout Sharing** — share your progress with friends
- 👥 **Group Workouts** — join a workout session with others
- 🌐 **Fitness Communities** — connect with people who share your goals
- 😴 **Sleep Tracking** — monitor your rest and recovery
- ✅ **Healthy Habit Tracking** — build and track daily habits
"""
)

# ------------------------------------------------------------------
# SECTION 10: BOTTOM CALL-TO-ACTION BANNER
# A bold closing banner, similar to the "Ready to make a change?"
# sections seen on real gym websites.
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="fitpulse-cta-banner">
        <h3>Ready to make a change? 🚀</h3>
        <p>FitPulse is free to use — start by finding a gym near you above.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("FitPulse — Sprint 1 Demo | Built with Python + Streamlit")
