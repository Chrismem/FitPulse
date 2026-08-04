"""
FitPulse - STEM Fitness & Gym Companion
-----------------------------------------
A Streamlit app that helps people find fitness centers
near them within a chosen radius, track daily fitness habits,
manage goals on a calendar, and connect with friends.
"""

import calendar
import math
import json
import os
from datetime import date, datetime, time as time_cls, timedelta

import pandas as pd
import streamlit as st
import extra_streamlit_components as stx

# ------------------------------------------------------------------
# SECTION 1: PAGE SETUP
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FitPulse",
    page_icon="💪",
    layout="wide",
)

# ------------------------------------------------------------------
# SECTION 2: BRAND STYLE (FitPulse Theme: Dark Charcoal, Forest Green)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* --- FITPULSE BRAND HERO BANNER --- */
    .fitpulse-hero {
        background: linear-gradient(135deg, #1C1C1A 0%, #2A2A26 50%, #7C9473 100%);
        border-radius: 20px;
        padding: 50px 40px;
        text-align: center;
        color: white;
        margin-bottom: 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .fitpulse-hero h1 {
        font-size: 56px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .fitpulse-hero p {
        font-size: 20px;
        margin-top: 14px;
        opacity: 0.92;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
    }
    .fitpulse-hero-badge {
        display: inline-block;
        background-color: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 999px;
        padding: 6px 20px;
        font-size: 13px;
        font-weight: 800;
        margin-bottom: 16px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* --- HOME METRICS STAT CARDS --- */
    .fitpulse-stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-top: 4px solid #7C9473;
        border-radius: 14px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .fitpulse-stat-card .val {
        font-size: 32px;
        font-weight: 800;
        color: #2A2A26;
        margin: 4px 0;
    }
    .fitpulse-stat-card .lbl {
        font-size: 13px;
        font-weight: 700;
        color: #767268;
        text-transform: uppercase;
    }

    /* --- FEATURE CARDS (grid) --- */
    .fitpulse-feature-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-top: 4px solid #7C9473;
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
        color: #2A2A26;
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
        color: #2A2A26;
        background-color: #F4F2EC;
        border-left: 5px solid #7C9473;
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 22px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 18px;
    }

    /* --- CARD BUTTON INTERACTION --- */
    .st-key-home_card button,
    .st-key-habit_tracking_card button,
    .st-key-community_card button,
    .st-key-gym_finder_card button,
    .st-key-friends_list_card button,
    .st-key-goal_calendar_card button,
    .st-key-gym_sessions_card button {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-top: 4px solid #7C9473 !important;
        border-radius: 14px !important;
        padding: 22px 18px !important;
        width: 100%;
        min-height: 175px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-top-color 0.15s ease;
    }
    .st-key-home_card button:hover,
    .st-key-habit_tracking_card button:hover,
    .st-key-community_card button:hover,
    .st-key-gym_finder_card button:hover,
    .st-key-friends_list_card button:hover,
    .st-key-goal_calendar_card button:hover,
    .st-key-gym_sessions_card button:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 22px rgba(0,0,0,0.14) !important;
        border-top-color: #2A2A26 !important;
    }

    .st-key-home_card button p,
    .st-key-habit_tracking_card button p,
    .st-key-community_card button p,
    .st-key-gym_finder_card button p,
    .st-key-friends_list_card button p,
    .st-key-goal_calendar_card button p,
    .st-key-gym_sessions_card button p {
        margin: 6px 0 0 0;
        color: #444;
        font-size: 14px;
        white-space: pre-line;
    }
    .st-key-home_card button p:first-of-type,
    .st-key-habit_tracking_card button p:first-of-type,
    .st-key-community_card button p:first-of-type,
    .st-key-gym_finder_card button p:first-of-type,
    .st-key-friends_list_card button p:first-of-type,
    .st-key-goal_calendar_card button p:first-of-type,
    .st-key-gym_sessions_card button p:first-of-type {
        font-size: 34px;
        margin-top: 0;
    }
    .st-key-home_card button p strong,
    .st-key-habit_tracking_card button p strong,
    .st-key-community_card button p strong,
    .st-key-gym_finder_card button p strong,
    .st-key-friends_list_card button p strong,
    .st-key-goal_calendar_card button p strong,
    .st-key-gym_sessions_card button p strong {
        color: #2A2A26;
        font-size: 17px;
    }

    /* --- CTA BANNER --- */
    .fitpulse-cta-banner {
        background:
            linear-gradient(135deg, rgba(28,28,26,0.85), rgba(85,112,76,0.78)),
            url("https://images.unsplash.com/photo-1590333748338-d629e4564ad9?w=1400&q=70&auto=format&fit=crop")
            center / cover no-repeat;
        border-radius: 16px;
        padding: 42px 32px;
        text-align: center;
        color: white;
        margin-top: 28px;
        margin-bottom: 12px;
    }
    .fitpulse-cta-banner h3 {
        font-size: 28px;
        margin: 0 0 8px 0;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# SECTION 3: SESSION STATE INIT
# ------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "username" not in st.session_state:
    st.session_state.username = "Alex"

# ------------------------------------------------------------------
# SECTION 4: NAVIGATION HEADER
# ------------------------------------------------------------------
def render_header():
    nav_cols = st.columns([1.2, 5, 2.5])
    
    with nav_cols[0]:
        st.markdown("<h2 style='margin:0; color:#2A2A26; font-weight:900;'>⚡ FITPULSE</h2>", unsafe_allow_html=True)

    with nav_cols[1]:
        pages = {
            "home": "🏠 Home",
            "gym_sessions": "🏋️ Workout Plans",
            "gym_finder": "📍 Find Gyms",
            "habits": "📊 Habit Tracker",
            "goal_calendar": "📅 Calendar",
            "community": "💬 Community",
            "friends_list": "👥 Friends",
            "profile": "👤 Profile",
        }
        
        selected = stx.tab_bar(
            data=[
                stx.TabBarItemData(id=pid, title=label, description="")
                for pid, label in pages.items()
            ],
            default=st.session_state.page,
            key="main_nav_tabs",
        )
        if selected and selected != st.session_state.page:
            st.session_state.page = selected
            st.rerun()

    with nav_cols[2]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.session_state.username = st.text_input("Active User:", value=st.session_state.username, key="active_user_top_input")
        with c2:
            st.write("")
            st.write("")
            if st.button("Logout", key="btn_logout_top"):
                st.session_state.username = "Guest"
                st.rerun()

# ------------------------------------------------------------------
# SECTION 5: RENDER HOME PAGE
# ------------------------------------------------------------------
def render_home_page():
    # Hero Section
    st.markdown(
        """
        <div class="fitpulse-hero">
            <span class="fitpulse-hero-badge">WELCOME TO FITPULSE</span>
            <h1>ELEVATE YOUR FITNESS JOURNEY</h1>
            <p>Your all-in-one companion for targeted 15-muscle workout plans, local gym navigation, daily tracking analytics, and community goal setting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick Jump Features Grid
    st.markdown("<div class='fitpulse-section-header'>🚀 EXPLORE FITPULSE FEATURES</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='st-key-gym_sessions_card'>", unsafe_allow_html=True)
        if st.button("🏋️\n\n**15-Muscle Workouts**\nTargeted plans & full exercise breakdowns", key="home_card_sessions"):
            st.session_state.page = "gym_sessions"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='st-key-gym_finder_card'>", unsafe_allow_html=True)
        if st.button("📍\n\n**Gym Locator**\nFind top rated fitness centers nearby", key="home_card_finder"):
            st.session_state.page = "gym_finder"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='st-key-habit_tracking_card'>", unsafe_allow_html=True)
        if st.button("📊\n\n**Habit Analytics**\nLog workouts, track speeds & streaks", key="home_card_habits"):
            st.session_state.page = "habits"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("<div class='st-key-goal_calendar_card'>", unsafe_allow_html=True)
        if st.button("📅\n\n**Goal Calendar**\nSchedule milestones & track achievements", key="home_card_calendar"):
            st.session_state.page = "goal_calendar"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col5:
        st.markdown("<div class='st-key-community_card'>", unsafe_allow_html=True)
        if st.button("💬\n\n**FitPulse Community**\nConnect, share workouts, and chat", key="home_card_community"):
            st.session_state.page = "community"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col6:
        st.markdown("<div class='st-key-friends_list_card'>", unsafe_allow_html=True)
        if st.button("👥\n\n**Friends & Network**\nBuild your training network", key="home_card_friends"):
            st.session_state.page = "friends_list"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SECTION 6: MAIN ENTRY ROUTER
# ------------------------------------------------------------------
render_header()

if st.session_state.page == "home":
    render_home_page()
elif st.session_state.page == "gym_sessions":
    st.title("🏋️ Workout Sessions & Muscle Plans")
    st.info("Select a muscle group to view detailed exercise breakdowns.")
elif st.session_state.page == "gym_finder":
    st.title("📍 Local Gym Locator")
    st.info("Find gyms near you within your custom radius.")
elif st.session_state.page == "habits":
    st.title("📊 Habit Tracker & Analytics")
    st.info("Log your daily exercises and view your stats.")
elif st.session_state.page == "goal_calendar":
    st.title("📅 Goal Calendar")
    st.info("View your scheduled workouts and milestones.")
elif st.session_state.page == "community":
    st.title("💬 Community Feed")
    st.info("Chat with fellow FitPulse members.")
elif st.session_state.page == "friends_list":
    st.title("👥 Friends List")
    st.info("Manage your workout buddies.")
elif st.session_state.page == "profile":
    st.title("👤 User Profile")
    st.info(f"Viewing profile for user: {st.session_state.username}")

# CTA Footer Banner
st.markdown(
    """
    <div class="fitpulse-cta-banner">
        <h3>READY TO PUSH YOUR LIMITS WITH FITPULSE?</h3>
        <p>Stay consistent, log your sessions, and reach your peak performance today.</p>
    </div>
    """,
    unsafe_allow_html=True,
)