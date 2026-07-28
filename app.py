"""
FitPulse - Sprint 3
--------------------
A simple Streamlit app that helps people find fitness centers
near them within a chosen radius (default 10 miles), track daily
fitness habits, and connect with friends on the app.

This is a beginner-friendly, high-school STEM project file.
No secret API keys or external geocoding services are used.
Instead, we use a small built-in list of sample cities and
sample fitness centers so the app works right away, anywhere.

LAYOUT NOTE: this version uses a "gym website" style layout —
a big bold hero banner up top, a row of feature cards, then the
search tool, inspired by real gym landing pages (big headline,
strong colors, card-based feature grid).

HABIT TRACKING & COMMUNITY:
Clicking the "Habit Tracking" or "Communities" feature card
switches the app into that view. This is NOT a new browser tab or
a page reload — it's done with Streamlit's `st.session_state`,
which lets us remember which "view" we're on and redraw the page
accordingly. Think of it like flipping to a different tab inside
the same app window, rather than opening a whole new website.

Habit data is saved to habit_data.json, and friends/chat data is
saved to community_data.json, both next to this script, keyed by
the user's name. That means progress is remembered even if you
close and reopen the app (as long as it's running on the same
machine/server).
"""

import math
import json
import os
from datetime import date, datetime, time as time_cls, timedelta

import pandas as pd
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
#   - habit tracker cards/badges that match the same brand
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

    /* --- CLICKABLE FEATURE CARDS: the button itself IS the card ---
       Instead of overlaying an invisible button on top of decorative
       HTML (which was unreliable to click), we style the real
       st.button directly so it looks exactly like the other feature
       cards. Since there's only one real element here, clicking
       anywhere on it always works. Both Habit Tracking and
       Communities use this same pattern. */
    .st-key-habit_tracking_card button,
    .st-key-community_card button {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-top: 4px solid #2E7D32 !important;
        border-radius: 14px !important;
        padding: 22px 18px !important;
        width: 100%;
        min-height: 175px;
        box-shadow: none !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-top-color 0.15s ease;
    }
    .st-key-habit_tracking_card button:hover,
    .st-key-community_card button:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 22px rgba(0,0,0,0.14) !important;
        border-top-color: #1565C0 !important;
    }
    .st-key-habit_tracking_card button:active,
    .st-key-community_card button:active {
        transform: translateY(-1px);
    }
    .st-key-habit_tracking_card button p,
    .st-key-community_card button p {
        margin: 6px 0 0 0;
        color: #444;
        font-size: 14px;
        white-space: pre-line;
    }
    .st-key-habit_tracking_card button p:first-of-type,
    .st-key-community_card button p:first-of-type {
        font-size: 34px;
        margin-top: 0;
    }
    .st-key-habit_tracking_card button p strong,
    .st-key-community_card button p strong {
        color: #1565C0;
        font-size: 17px;
    }

    /* --- COMMUNITY: chat bubbles reuse the same result-card style --- */
    .fitpulse-friend-name {
        font-weight: 700;
        color: #1565C0;
    }

    /* --- HABIT TRACKER: streak badge --- */
    .fitpulse-streak-badge {
        display: inline-block;
        background-color: #1565C0;
        color: white;
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 14px;
        font-weight: 700;
        margin-left: 8px;
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
# SECTION 3: SAMPLE DATA (gym finder)
# In a real product, this list would come from a database or a
# maps API. For our demo, we use sample fitness centers with
# made-up coordinates so the distance math actually works.
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
# SECTION 5: HABIT TRACKER DATA HELPERS
# We store habit data in a small JSON file on disk, keyed by
# username, so progress is remembered between visits. This keeps
# things simple for a class project (no external database needed).
#
# Data shape:
# {
#   "Alex": {
#     "habits": {
#       "Daily 1-Mile Run": {
#         "goal_distance": 1.0,
#         "frequency": "Daily",
#         "reminder_time": "07:00",
#         "logs": [
#           {"date": "2026-07-27", "distance": 1.0,
#            "duration_min": 9.5, "speed_mph": 6.32},
#           ...
#         ]
#       }
#     }
#   }
# }
# ------------------------------------------------------------------
DATA_FILE = "habit_data.json"


def load_all_data():
    """Read the whole habit_data.json file into a Python dict."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_all_data(all_data):
    """Write the whole habit data dict back to habit_data.json."""
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)


def get_user_data(username):
    """Get (or create) the habit data for one user."""
    all_data = load_all_data()
    return all_data.get(username, {"habits": {}})


def save_user_data(username, user_data):
    """Save one user's habit data back into the shared file."""
    all_data = load_all_data()
    all_data[username] = user_data
    save_all_data(all_data)


def compute_streak(logs):
    """Count consecutive days (ending today) that have a log entry."""
    if not logs:
        return 0
    log_dates = {entry["date"] for entry in logs}
    streak = 0
    current_day = date.today()
    while current_day.strftime("%Y-%m-%d") in log_dates:
        streak += 1
        current_day -= timedelta(days=1)
    return streak


def compute_habit_stats(logs):
    """Return total runs, total distance, and average speed for a habit."""
    if not logs:
        return {"total_runs": 0, "total_distance": 0.0, "avg_speed": 0.0}
    total_runs = len(logs)
    total_distance = sum(entry["distance"] for entry in logs)
    avg_speed = sum(entry["speed_mph"] for entry in logs) / total_runs
    return {
        "total_runs": total_runs,
        "total_distance": round(total_distance, 2),
        "avg_speed": round(avg_speed, 2),
    }


def logged_today(logs):
    """Check whether there's already a log entry for today."""
    today_str = date.today().strftime("%Y-%m-%d")
    return any(entry["date"] == today_str for entry in logs)


# ------------------------------------------------------------------
# SECTION 5B: COMMUNITY DATA HELPERS (friends + chat)
# Just like habit data, community data (who's on the app, who's
# friends with who, and chat messages) is saved to a small JSON
# file on disk so it's remembered between visits.
#
# Data shape:
# {
#   "users": ["Alex", "Sam", ...],                 <- everyone who's opened the app
#   "friends": {"Alex": ["Sam"], "Sam": ["Alex"]},  <- friendships are mutual
#   "messages": {
#     "Alex::Sam": [                                <- key is names sorted + joined
#       {"sender": "Alex", "text": "hey!", "time": "2026-07-28 09:15"},
#       ...
#     ]
#   }
# }
# ------------------------------------------------------------------
COMMUNITY_FILE = "community_data.json"


def load_community_data():
    """Read the whole community_data.json file into a Python dict."""
    if os.path.exists(COMMUNITY_FILE):
        try:
            with open(COMMUNITY_FILE, "r") as f:
                data = json.load(f)
                data.setdefault("users", [])
                data.setdefault("friends", {})
                data.setdefault("messages", {})
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return {"users": [], "friends": {}, "messages": {}}


def save_community_data(data):
    """Write the whole community data dict back to community_data.json."""
    with open(COMMUNITY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def register_user(name):
    """Add a name to the discoverable users list, if it isn't already there."""
    data = load_community_data()
    if name and name not in data["users"]:
        data["users"].append(name)
        save_community_data(data)


def get_all_users():
    """Return every name that has ever used FitPulse (for Discover People)."""
    return load_community_data()["users"]


def get_friends(name):
    """Return a person's current friends list."""
    return load_community_data()["friends"].get(name, [])


def add_friend(name, friend_name):
    """Add a friendship between two people (mutual, both directions)."""
    data = load_community_data()
    data["friends"].setdefault(name, [])
    data["friends"].setdefault(friend_name, [])
    if friend_name not in data["friends"][name]:
        data["friends"][name].append(friend_name)
    if name not in data["friends"][friend_name]:
        data["friends"][friend_name].append(name)
    save_community_data(data)


def chat_key(name_a, name_b):
    """Build a stable, order-independent key for a pair of chatters."""
    return "::".join(sorted([name_a, name_b]))


def get_messages(name_a, name_b):
    """Return the chat history between two people, oldest first."""
    data = load_community_data()
    return data["messages"].get(chat_key(name_a, name_b), [])


def send_message(sender, recipient, text):
    """Append a new chat message between two people."""
    data = load_community_data()
    key = chat_key(sender, recipient)
    data["messages"].setdefault(key, [])
    data["messages"][key].append(
        {
            "sender": sender,
            "text": text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    save_community_data(data)


# ------------------------------------------------------------------
# SECTION 6: SESSION STATE (controls which "view" we're on)
# st.session_state persists across reruns of the same browser tab.
# We use it as a simple router: "home" or "habits". Switching this
# value + calling st.rerun() redraws the page in place — no new
# browser tab, no page reload, just a different view of the same app.
# ------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "username" not in st.session_state:
    st.session_state.username = "Guest"


# ------------------------------------------------------------------
# SECTION 7: SIDEBAR (user profile + navigation)
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    st.session_state.username = st.text_input(
        "Your name",
        value=st.session_state.username,
        help="Habits and progress are saved per name, so each person on this "
        "computer can track their own habits separately.",
    )
    st.caption("Tip: use the same name each time so your progress is saved.")

    if st.session_state.page in ("habits", "community"):
        st.markdown("---")
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

username = st.session_state.username.strip() or "Guest"
# Make sure this person shows up for others in "Discover People".
register_user(username)


# ------------------------------------------------------------------
# SECTION 8: HOME PAGE (hero, feature cards, gym finder)
# ------------------------------------------------------------------
def render_home():
    # --- Hero banner ---
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

    # --- Feature card grid ---
    feature_cols = st.columns(3)

    features = [
        ("📍", "Gym Finder", "Locate fitness centers within your chosen radius."),
        ("🌐", "Communities", "Add friends and chat with people on FitPulse."),
        ("✅", "Habit Tracking", "Build and track healthy daily habits."),
    ]

    # Cards that actually navigate somewhere: title -> (container key,
    # button key, page to switch to). Each is rendered as ONE real
    # st.button styled (via CSS in SECTION 2) to look like a feature
    # card, instead of decorative HTML with an invisible button on top
    # — that overlay approach was unreliable to click. With a single
    # real button, clicking anywhere on the card always works.
    CLICKABLE_CARDS = {
        "Communities": ("community_card", "community_card_click", "community"),
        "Habit Tracking": ("habit_tracking_card", "habit_card_click", "habits"),
    }

    for col, (icon, title, text) in zip(feature_cols, features):
        with col:
            if title in CLICKABLE_CARDS:
                container_key, button_key, target_page = CLICKABLE_CARDS[title]
                with st.container(key=container_key):
                    card_clicked = st.button(
                        f"{icon}\n\n**{title}**\n\n{text}",
                        key=button_key,
                        use_container_width=True,
                    )
                    if card_clicked:
                        st.session_state.page = target_page
                        st.rerun()
            else:
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

    # --- Location input + search ---
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

    # --- Search results ---
    if search_clicked:
        user_lat, user_lon = SAMPLE_LOCATIONS[location_choice]

        nearby_gyms = []
        for gym in FITNESS_CENTERS:
            dist = distance_in_miles(user_lat, user_lon, gym["lat"], gym["lon"])
            if dist <= radius_miles:
                nearby_gyms.append((gym, dist))

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

    # --- Future features ---
    st.markdown(
        '<div class="fitpulse-section-header">🚀 Coming Soon to FitPulse</div>',
        unsafe_allow_html=True,
    )
    st.write(
        """
    - 🤝 **Workout Sharing** — share your progress with friends
    - 😴 **Sleep Tracking** — monitor your rest and recovery
    """
    )

    # --- Bottom CTA banner ---
    st.markdown(
        """
        <div class="fitpulse-cta-banner">
            <h3>Ready to make a change? 🚀</h3>
            <p>FitPulse is free to use — start by finding a gym near you above.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("FitPulse — Sprint 2 Demo | Built with Python + Streamlit")


# ------------------------------------------------------------------
# SECTION 8B: COMMUNITY PAGE
# This is the page users land on after clicking the Communities card.
# It has two tabs:
#   1. "My Friends"      — pick a friend and chat with them
#   2. "Discover People"  — search everyone who's used FitPulse and
#                           add them as a friend
# Friends and chat messages are saved to community_data.json, so
# they're remembered between visits (as long as the app runs on the
# same machine/server).
# ------------------------------------------------------------------
def render_community():
    st.markdown(
        '<div class="fitpulse-section-header">🌐 Community</div>',
        unsafe_allow_html=True,
    )
    st.write(f"Connect with other FitPulse members, **{username}**.")

    if st.button("🏠 Back to Home", key="back_home_community"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    friends_tab, discover_tab = st.tabs(["👥 My Friends", "🔍 Discover People"])

    # --- TAB 1: My Friends (pick a friend, chat with them) ---
    with friends_tab:
        friends = get_friends(username)

        if not friends:
            st.info(
                "You haven't added any friends yet. Head over to **Discover People** "
                "to search for someone and add them."
            )
        else:
            if (
                "chat_partner" not in st.session_state
                or st.session_state.chat_partner not in friends
            ):
                st.session_state.chat_partner = friends[0]

            list_col, chat_col = st.columns([1, 2])

            with list_col:
                st.markdown("**Your friends**")
                for friend in friends:
                    is_active = friend == st.session_state.chat_partner
                    label = f"{'💬 ' if is_active else '👤 '}{friend}"
                    if st.button(
                        label,
                        key=f"select_friend_{friend}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                    ):
                        st.session_state.chat_partner = friend
                        st.rerun()

            with chat_col:
                partner = st.session_state.chat_partner
                st.markdown(f"**Chat with <span class='fitpulse-friend-name'>{partner}</span>**", unsafe_allow_html=True)

                messages = get_messages(username, partner)
                with st.container(height=320, border=True):
                    if not messages:
                        st.caption("No messages yet — say hi! 👋")
                    for msg in messages:
                        role = "user" if msg["sender"] == username else "assistant"
                        with st.chat_message(role):
                            st.write(msg["text"])
                            st.caption(msg["time"])

                new_message = st.chat_input(f"Message {partner}...")
                if new_message:
                    send_message(username, partner, new_message)
                    st.rerun()

    # --- TAB 2: Discover People (search + add friends) ---
    with discover_tab:
        st.markdown("**Find people on FitPulse**")
        search_query = st.text_input(
            "Search by name", placeholder="Type a name to search...", key="discover_search"
        )

        current_friends = get_friends(username)
        all_people = [name for name in get_all_users() if name != username]

        if search_query.strip():
            matches = [
                name for name in all_people
                if search_query.strip().lower() in name.lower()
            ]
        else:
            matches = all_people

        if not matches:
            st.info(
                "No one found yet. Try a different search, or have a friend open "
                "FitPulse and set their name so you can find them here."
            )
        else:
            for person in matches:
                person_col, action_col = st.columns([3, 1])
                with person_col:
                    st.markdown(f"🧑 **{person}**")
                with action_col:
                    if person in current_friends:
                        st.button(
                            "✅ Friends",
                            key=f"already_friend_{person}",
                            disabled=True,
                            use_container_width=True,
                        )
                    else:
                        if st.button(
                            "➕ Add",
                            key=f"add_friend_{person}",
                            use_container_width=True,
                        ):
                            add_friend(username, person)
                            st.success(f"You and {person} are now friends! 🎉")
                            st.rerun()


# ------------------------------------------------------------------
# SECTION 9: HABIT TRACKER PAGE
# This is the new page users land on after clicking the Habit
# Tracking card. It lets a user:
#   1. Create a habit (e.g. "Daily 1-Mile Run") with a goal + reminder
#   2. Log each day's run (distance + time), and see speed calculated
#   3. See progress: current streak, totals, and charts over time
# ------------------------------------------------------------------
def render_habit_tracker():
    st.markdown(
        '<div class="fitpulse-section-header">🏋️ Habit Tracker</div>',
        unsafe_allow_html=True,
    )
    st.write(f"Tracking healthy habits for **{username}**. Every log is saved automatically.")

    if st.button("🏠 Back to Home", key="back_home_top"):
        st.session_state.page = "home"
        st.rerun()

    user_data = get_user_data(username)
    habits = user_data["habits"]

    # --- Add a new habit ---
    with st.expander("➕ Add a New Habit", expanded=(len(habits) == 0)):
        with st.form("add_habit_form", clear_on_submit=True):
            habit_name = st.text_input(
                "Habit name", placeholder="e.g., Daily 1-Mile Run"
            )
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                goal_distance = st.number_input(
                    "Goal distance (miles)", min_value=0.0, value=1.0, step=0.1
                )
            with col_b:
                frequency = st.selectbox("Frequency", ["Daily", "Weekdays", "Weekly"])
            with col_c:
                reminder_time = st.time_input("Reminder time", value=time_cls(7, 0))

            submitted = st.form_submit_button("Create Habit")
            if submitted:
                clean_name = habit_name.strip()
                if not clean_name:
                    st.warning("Please enter a habit name.")
                elif clean_name in habits:
                    st.warning("You already have a habit with that name.")
                else:
                    habits[clean_name] = {
                        "goal_distance": goal_distance,
                        "frequency": frequency,
                        "reminder_time": reminder_time.strftime("%H:%M"),
                        "logs": [],
                    }
                    save_user_data(username, user_data)
                    st.success(f"Habit '{clean_name}' created! Scroll down to log your first entry.")
                    st.rerun()

    if not habits:
        st.info("You don't have any habits yet — add one above to get started, "
                 "for example **Daily 1-Mile Run**.")
        return

    st.divider()

    # --- Show every habit ---
    for habit_name, habit in habits.items():
        logs = habit["logs"]
        stats = compute_habit_stats(logs)
        streak = compute_streak(logs)
        already_logged = logged_today(logs)

        st.markdown(f"### 🏃 {habit_name}")
        st.markdown(
            f'Goal: **{habit["goal_distance"]} mi**, {habit["frequency"].lower()} '
            f'&nbsp; <span class="fitpulse-streak-badge">🔥 {streak}-day streak</span>',
            unsafe_allow_html=True,
        )

        # Reminder banner: only nag if today's entry is missing and
        # the reminder time has already passed.
        reminder_hour, reminder_minute = (int(x) for x in habit["reminder_time"].split(":"))
        reminder_dt = time_cls(reminder_hour, reminder_minute)
        if not already_logged and datetime.now().time() >= reminder_dt:
            st.warning(
                f"⏰ Reminder: you haven't logged **{habit_name}** yet today "
                f"(reminder set for {habit['reminder_time']})."
            )
        elif not already_logged:
            st.info(f"⏰ Today's reminder is set for {habit['reminder_time']}. No log yet today.")
        else:
            st.success("✅ Already logged today. Nice work!")

        # Quick stats
        stat_cols = st.columns(4)
        stat_cols[0].metric("Total runs", stats["total_runs"])
        stat_cols[1].metric("Total distance", f"{stats['total_distance']} mi")
        stat_cols[2].metric("Avg speed", f"{stats['avg_speed']} mph")
        stat_cols[3].metric("Current streak", f"{streak} days")

        # Log today's run
        with st.form(f"log_form_{habit_name}"):
            log_col1, log_col2 = st.columns(2)
            with log_col1:
                run_distance = st.number_input(
                    "Distance run today (miles)",
                    min_value=0.0,
                    value=float(habit["goal_distance"]),
                    step=0.1,
                    key=f"dist_{habit_name}",
                )
            with log_col2:
                run_duration = st.number_input(
                    "Time it took (minutes)",
                    min_value=0.1,
                    value=9.0,
                    step=0.5,
                    key=f"dur_{habit_name}",
                )
            log_submitted = st.form_submit_button("✅ Log Today's Run")
            if log_submitted:
                speed_mph = run_distance / (run_duration / 60)
                today_str = date.today().strftime("%Y-%m-%d")
                # Replace any existing entry for today so re-logging updates it
                logs[:] = [entry for entry in logs if entry["date"] != today_str]
                logs.append(
                    {
                        "date": today_str,
                        "distance": round(run_distance, 2),
                        "duration_min": round(run_duration, 2),
                        "speed_mph": round(speed_mph, 2),
                    }
                )
                save_user_data(username, user_data)
                st.success(
                    f"Logged {run_distance} mi in {run_duration} min "
                    f"({speed_mph:.1f} mph). Great job! 💪"
                )
                st.rerun()

        # Progress charts + history table
        if logs:
            df = pd.DataFrame(logs).sort_values("date")
            df_indexed = df.set_index("date")

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.caption("Distance per day (miles)")
                st.line_chart(df_indexed[["distance"]])
            with chart_col2:
                st.caption("Speed per day (mph)")
                st.line_chart(df_indexed[["speed_mph"]])

            with st.expander("📜 View full log history"):
                st.dataframe(
                    df.rename(
                        columns={
                            "date": "Date",
                            "distance": "Distance (mi)",
                            "duration_min": "Duration (min)",
                            "speed_mph": "Speed (mph)",
                        }
                    ).sort_values("Date", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                )

        if st.button(f"🗑️ Delete '{habit_name}'", key=f"delete_{habit_name}"):
            del habits[habit_name]
            save_user_data(username, user_data)
            st.rerun()

        st.divider()


# ------------------------------------------------------------------
# SECTION 10: ROUTER — draw whichever page we're on
# ------------------------------------------------------------------
if st.session_state.page == "habits":
    render_habit_tracker()
elif st.session_state.page == "community":
    render_community()
else:
    render_home()
