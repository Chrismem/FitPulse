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
        background: linear-gradient(135deg, #2A2A26 0%, #7C9473 100%);
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
        margin-top: 8px;
        margin-bottom: 16px;
    }

    /* --- RESULT CARDS --- */
    .fitpulse-card {
        background-color: #F4F2EC;
        border: 1px solid #7C9473;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #1B1B1B;
    }

    /* --- CLICKABLE FEATURE CARDS: the button itself IS the card --- */
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
        box-shadow: none !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-top-color 0.15s ease;
    }
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
    .st-key-habit_tracking_card button:active,
    .st-key-community_card button:active,
    .st-key-gym_finder_card button:active,
    .st-key-friends_list_card button:active,
    .st-key-goal_calendar_card button:active,
    .st-key-gym_sessions_card button:active {
        transform: translateY(-1px);
    }
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
    .st-key-habit_tracking_card button p:first-of-type,
    .st-key-community_card button p:first-of-type,
    .st-key-gym_finder_card button p:first-of-type,
    .st-key-friends_list_card button p:first-of-type,
    .st-key-goal_calendar_card button p:first-of-type,
    .st-key-gym_sessions_card button p:first-of-type {
        font-size: 34px;
        margin-top: 0;
    }
    .st-key-habit_tracking_card button p strong,
    .st-key-community_card button p strong,
    .st-key-gym_finder_card button p strong,
    .st-key-friends_list_card button p strong,
    .st-key-goal_calendar_card button p strong,
    .st-key-gym_sessions_card button p strong {
        color: #2A2A26;
        font-size: 17px;
    }

    /* --- GOAL CALENDAR --- */
    .fitpulse-cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        margin-bottom: 10px;
    }
    .fitpulse-cal-daylabel {
        text-align: center;
        font-size: 12px;
        font-weight: 700;
        color: #767268;
        text-transform: uppercase;
        padding-bottom: 2px;
    }
    .fitpulse-cal-cell {
        border: 1px solid #E4E1D8;
        border-radius: 8px;
        min-height: 62px;
        padding: 6px;
        background-color: #FFFFFF;
        font-size: 12px;
    }
    .fitpulse-cal-cell.empty {
        border: none;
        background: transparent;
    }
    .fitpulse-cal-cell.workout-day {
        background-color: #EAF1E7;
        border-color: #7C9473;
    }
    .fitpulse-cal-cell.goal-day {
        border-color: #C79A3B;
        box-shadow: inset 0 0 0 1px #C79A3B;
    }
    .fitpulse-cal-cell.today {
        border-width: 2px;
        border-color: #2A2A26;
    }
    .fitpulse-cal-daynum {
        font-weight: 700;
        color: #2A2A26;
    }
    .fitpulse-cal-tag {
        display: block;
        margin-top: 3px;
        font-size: 10.5px;
        line-height: 1.3;
    }
    .fitpulse-goal-card {
        background-color: #F4F2EC;
        border: 1px solid #E0DCCF;
        border-left: 4px solid #C79A3B;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .fitpulse-goal-card.completed {
        border-left-color: #7C9473;
        opacity: 0.75;
    }

    /* --- TOP NAVIGATION BAR --- */
    .st-key-top_navbar {
        background-color: #F4F2EC;
        border: 1px solid #E4E1D8;
        border-radius: 999px;
        padding: 5px 8px;
        display: flex;
        align-items: center;
    }
    .st-key-top_navbar button {
        background-color: transparent !important;
        border: none !important;
        color: #4A4A42 !important;
        font-weight: 600 !important;
        font-size: 12.5px !important;
        padding: 7px 4px !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        white-space: nowrap;
    }
    .st-key-top_navbar button:hover {
        background-color: #E7E3D6 !important;
        color: #2A2A26 !important;
    }
    .st-key-top_navbar button[kind="primary"] {
        background-color: #7C9473 !important;
        color: #FFFFFF !important;
    }
    .st-key-top_navbar button[kind="primary"]:hover {
        background-color: #66805C !important;
    }

    /* --- COMMUNITY CHAT --- */
    .fitpulse-friend-name {
        font-weight: 700;
        color: #2A2A26;
    }

    /* --- FRIENDS LIST --- */
    .fitpulse-friend-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #7C9473;
        border-radius: 12px;
        padding: 18px 16px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }
    .fitpulse-friend-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .fitpulse-friend-info {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
    }
    .fitpulse-friend-avatar {
        font-size: 32px;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #F4F2EC;
        border-radius: 50%;
    }
    .fitpulse-friend-name-text {
        font-weight: 600;
        color: #2A2A26;
        font-size: 16px;
    }

    /* --- EMPTY STATE --- */
    .fitpulse-empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #8A8A80;
    }
    .fitpulse-empty-state-icon {
        font-size: 48px;
        margin-bottom: 12px;
    }

    /* --- USER PROFILE CARD --- */
    .fitpulse-profile-card {
        background: linear-gradient(135deg, #F4F2EC 0%, #FFFFFF 100%);
        border: 1px solid #E0E0E0;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .fitpulse-profile-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 24px;
    }
    .fitpulse-profile-avatar-large {
        font-size: 64px;
        width: 96px;
        height: 96px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #FFFFFF;
        border: 2px solid #7C9473;
        border-radius: 50%;
    }
    .fitpulse-profile-name-section h2 {
        margin: 0 0 4px 0;
        color: #2A2A26;
        font-size: 28px;
    }
    .fitpulse-profile-name-section p {
        margin: 4px 0;
        color: #8A8A80;
        font-size: 15px;
    }
    .fitpulse-profile-attributes {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    .fitpulse-profile-attr-item {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .fitpulse-profile-attr-label {
        font-size: 12px;
        font-weight: 700;
        color: #8A8A80;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .fitpulse-profile-attr-value {
        font-size: 16px;
        font-weight: 600;
        color: #2A2A26;
    }

    /* --- EDIT PROFILE FORM --- */
    .fitpulse-edit-section {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* --- HABIT TRACKER: streak badge --- */
    .fitpulse-streak-badge {
        display: inline-block;
        background-color: #2A2A26;
        color: white;
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 14px;
        font-weight: 700;
        margin-left: 8px;
    }

    /* --- BOTTOM CTA BANNER --- */
    .fitpulse-cta-banner {
        background:
            linear-gradient(135deg, rgba(28,28,26,0.82), rgba(85,112,76,0.72)),
            url("https://images.unsplash.com/photo-1590333748338-d629e4564ad9?w=1400&q=70&auto=format&fit=crop")
            center / cover no-repeat;
        border-radius: 14px;
        padding: 40px 32px;
        text-align: center;
        color: white;
        margin-top: 24px;
        margin-bottom: 12px;
    }
    .fitpulse-cta-banner h3 {
        font-size: 26px;
        margin: 0 0 8px 0;
    }

    /* --- COMMUNITY PHOTO GALLERY --- */
    .fitpulse-photo-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: 20px 0 8px 0;
    }
    .fitpulse-photo-card {
        position: relative;
        border-radius: 14px;
        overflow: hidden;
        height: 190px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.10);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .fitpulse-photo-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.18);
    }
    .fitpulse-photo-card img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        filter: saturate(0.9) contrast(1.02);
    }
    .fitpulse-photo-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to top,
            rgba(42, 42, 38, 0.75) 0%,
            rgba(42, 42, 38, 0.05) 55%,
            rgba(124, 148, 115, 0.18) 100%
        );
    }
    .fitpulse-photo-caption {
        position: absolute;
        left: 14px;
        bottom: 10px;
        z-index: 2;
        color: white;
        font-weight: 700;
        font-size: 14.5px;
        letter-spacing: 0.3px;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
    }

    @media (max-width: 700px) {
        .fitpulse-photo-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .fitpulse-photo-card {
            height: 150px;
        }
    }

    /* ================================================================
       GYM FINDER PAGE — locator experience
       ================================================================ */
    .fitpulse-locator-hero {
        background: linear-gradient(120deg, #1C1C1A 0%, #2A2A26 55%, #7C9473 100%);
        border-radius: 20px;
        padding: 40px 36px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .fitpulse-locator-hero::after {
        content: "📍";
        position: absolute;
        right: -10px;
        bottom: -30px;
        font-size: 150px;
        opacity: 0.12;
        transform: rotate(-12deg);
    }
    .fitpulse-locator-hero h1 {
        font-size: 36px;
        font-weight: 900;
        margin: 0 0 6px 0;
    }
    .fitpulse-locator-hero p {
        font-size: 16px;
        opacity: 0.92;
        margin: 0;
        max-width: 640px;
    }

    .fitpulse-locator-toolbar {
        background: rgba(85, 112, 76, 0.06);
        border: 1px solid rgba(85, 112, 76, 0.18);
        border-radius: 16px;
        padding: 20px 22px 6px 22px;
        margin-bottom: 20px;
    }

    .fitpulse-gym-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
        border: 1px solid #EAEAEA;
        border-top: none;
        position: relative;
        box-shadow: 0 2px 10px rgba(15, 32, 39, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .fitpulse-gym-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 5px;
        border-radius: 16px 16px 0 0;
        background: linear-gradient(90deg, #2A2A26, #7C9473);
    }
    .fitpulse-gym-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 28px rgba(15, 32, 39, 0.14);
    }
    .fitpulse-gym-card .gym-top-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
    }
    .fitpulse-gym-card h4 {
        margin: 0;
        color: #1C1C1A;
        font-size: 18px;
    }
    .fitpulse-gym-card .gym-address {
        color: #666;
        font-size: 13.5px;
        margin: 4px 0 10px 0;
    }
    .fitpulse-distance-badge {
        display: inline-block;
        background: linear-gradient(90deg, #2A2A26, #7C9473);
        color: white;
        font-size: 12.5px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }
    .fitpulse-rating-stars {
        color: #F5A623;
        font-size: 14px;
        letter-spacing: 1px;
    }
    .fitpulse-rating-number {
        color: #444;
        font-size: 13px;
        margin-left: 4px;
    }
    .fitpulse-pill-row {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .fitpulse-pill {
        background-color: #F4F2EC;
        color: #2A2A26;
        border: 1px solid rgba(85, 112, 76, 0.25);
        border-radius: 999px;
        padding: 3px 11px;
        font-size: 12px;
        font-weight: 600;
    }
    .fitpulse-closest-tag {
        position: absolute;
        top: -10px;
        right: 16px;
        background: #2A2A26;
        color: white;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 999px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }

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
# ------------------------------------------------------------------
FITNESS_CENTERS = [
    {"name": "Crunch Fitness - North Bergen", "address": "2819 John F Kennedy Blvd, North Bergen, NJ 07047",
     "lat": 40.8162, "lon": -74.0207, "rating": 4.5, "amenities": ["24/7 Access", "Group Classes", "Free Weights"]},
    {"name": "New York Sports Club - Hoboken", "address": "210 14th St, Hoboken, NJ 07030",
     "lat": 40.7357, "lon": -74.0324, "rating": 4.6, "amenities": ["Personal Training", "Sauna", "Group Classes"]},
    {"name": "Fitness Factory - Hoboken", "address": "130 Washington St, Hoboken, NJ 07030",
     "lat": 40.7361, "lon": -74.0316, "rating": 4.7, "amenities": ["Free Weights", "Cardio", "Strength Training"]},
    {"name": "Fitness Factory - Jersey City", "address": "525 Washington Boulevard, Jersey City, NJ 07310",
     "lat": 40.7180, "lon": -74.0450, "rating": 4.4, "amenities": ["24/7 Access", "Group Classes", "Personal Training"]},
    {"name": "Planet Fitness - Union", "address": "2445 Springfield Ave, Union, NJ 07088",
     "lat": 40.6700, "lon": -74.2757, "rating": 4.3, "amenities": ["Massage Chairs", "Hydro Massage", "Free Weights"]},
    {"name": "Planet Fitness - Newark", "address": "520 Broad St, Newark, NJ 07102",
     "lat": 40.7357, "lon": -74.1724, "rating": 4.2, "amenities": ["Free Fitness Training", "Cardio", "Strength Equipment"]},
    {"name": "YMCA of Newark - Central Branch", "address": "600 Broad St, Newark, NJ 07102",
     "lat": 40.7365, "lon": -74.1730, "rating": 4.4, "amenities": ["Pool", "Youth Programs", "Basketball Court"]},
    {"name": "Chelsea Piers Fitness", "address": "Pier 60, Chelsea Piers, New York, NY 10011",
     "lat": 40.7467, "lon": -74.0103, "rating": 4.8, "amenities": ["Rock Climbing", "Pool", "Cold Plunge", "Sauna"]},
]

SAMPLE_LOCATIONS = {
    "Union City, NJ": (40.7795, -74.0237),
    "Jersey City, NJ": (40.7190, -74.0450),
    "Hoboken, NJ": (40.7357, -74.0324),
    "Newark, NJ": (40.7357, -74.1724),
    "New York, NY": (40.7467, -74.0103),
}

# ------------------------------------------------------------------
# WORKOUT PLANS DATA (15 Muscle Groups)
# ------------------------------------------------------------------
WORKOUT_PLANS = {
    "Chest": {
        "icon": "🏋️‍♂️",
        "description": "Build upper body pushing power and pectoral muscle size.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Bench Press", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Lower bar to mid-chest, pause 1 second, drive up explosively.", "progression": "Increase weight by 5-10 lbs each week."},
            {"type": "Secondary Exercise", "name": "Incline Dumbbell Press", "details": "3 sets x 8-10 reps | Rest: 90-120 secs", "form": "Set bench to 30-45 degrees, lower dumbbells to shoulders, press up.", "progression": "Increase dumbbell weight or add 1-2 reps."},
            {"type": "Isolation Exercise 1", "name": "Barbell or Machine Chest Flyes", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Keep slight bend in elbows, bring hands together at chest level.", "progression": "Increase weight or control the eccentric phase."},
            {"type": "Isolation Exercise 2", "name": "Cable Crossovers", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Stand in middle, bring cables across body, squeeze at center.", "progression": "Increase cable weight or increase rep range."},
            {"type": "Finisher", "name": "Push-ups", "details": "3 sets x 15-20 reps | Rest: 45-60 secs", "form": "Keep core tight, lower chest to 1 inch from ground.", "progression": "Add weight vest or decrease rest periods."}
        ]
    },
    "Back": {
        "icon": "🏋️‍♀️",
        "description": "Develop a strong, wide back and improve posture.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Bent-Over Barbell Row", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Hinge at hips, pull bar to lower chest, squeeze shoulder blades.", "progression": "Increase weight by 5-10 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Weighted Pull-ups / Lat Pulldown", "details": "3 sets x 6-10 reps | Rest: 2-3 mins", "form": "Full range of motion, chest to bar if possible.", "progression": "Add weight with belt or achieve more reps."},
            {"type": "Upper Back Isolation", "name": "Face Pulls", "details": "3 sets x 12-15 reps | Rest: 60-90 secs", "form": "Pull rope towards face, flare elbows out, squeeze rear delts.", "progression": "Increase weight or reps."},
            {"type": "Lat Isolation", "name": "Machine Lat Pulldown", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Pull bar to upper chest, control the weight up slowly.", "progression": "Increase weight or add reps."},
            {"type": "Lower Back", "name": "Hyperextensions", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Hinge at hips, extend back to neutral position.", "progression": "Add weight plate or increase reps."},
            {"type": "Finisher", "name": "Inverted Rows", "details": "3 sets x 12-15 reps | Rest: 45-60 secs", "form": "Hang under bar, pull chest to bar, keep body rigid.", "progression": "Lower bar height to increase difficulty."}
        ]
    },
    "Shoulders": {
        "icon": "🛡️",
        "description": "Carve 3D deltoids and build overhead power.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Standing Overhead Press (Barbell)", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Press from shoulders to full lockout, maintain core tension.", "progression": "Increase weight by 2.5-5 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Machine Shoulder Press", "details": "3 sets x 8-10 reps | Rest: 90-120 secs", "form": "Press handles forward and up, controlled descent.", "progression": "Increase weight or reps."},
            {"type": "Lateral Delt Focus", "name": "Standing Lateral Raises", "details": "3 sets x 12-15 reps | Rest: 60-90 secs", "form": "Slight bend in elbows, raise to shoulder height, squeeze at top.", "progression": "Increase dumbbell weight or decrease rest."},
            {"type": "Rear Delt Focus", "name": "Reverse Pec Deck Machine", "details": "3 sets x 12-15 reps | Rest: 60-90 secs", "form": "Sit upright, pull handles back, squeeze shoulder blades.", "progression": "Increase weight or reps."},
            {"type": "Rotator Cuff & Health", "name": "Dumbbell Lateral Raises (Light)", "details": "3 sets x 15-20 reps | Rest: 45-60 secs", "form": "Controlled movement, light weight, focus on shoulder health.", "progression": "Slightly increase weight while maintaining form."},
            {"type": "Finisher", "name": "Upright Rows", "details": "3 sets x 10-12 reps | Rest: 60 secs", "form": "Pull elbows up, raise bar to chin height.", "progression": "Increase weight or reps."}
        ]
    },
    "Biceps": {
        "icon": "💪",
        "description": "Isolate and grow biceps peak and overall arm thickness.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Curls", "details": "4 sets x 6-8 reps | Rest: 90-120 secs", "form": "Keep elbows at sides, full range of motion, no swinging.", "progression": "Increase weight by 2.5-5 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Incline Dumbbell Curls", "details": "3 sets x 8-10 reps | Rest: 90 secs", "form": "Sit on incline bench, curl dumbbells up, avoid body momentum.", "progression": "Increase dumbbell weight or add reps."},
            {"type": "Isolation 1", "name": "Machine Bicep Curl", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Full range of motion, squeeze at top, controlled descent.", "progression": "Increase weight or reps."},
            {"type": "Isolation 2", "name": "Preacher Curls", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Upper arms flat on pad, curl bar to shoulders.", "progression": "Increase weight or decrease rest."},
            {"type": "Drop Set Exercise", "name": "Cable Curls", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Keep cable at chest height, curl handle up.", "progression": "Increase cable weight or add drops."},
            {"type": "Finisher", "name": "Bodyweight Chin-ups", "details": "3 sets x Max Reps | Rest: 60-90 secs", "form": "Palms facing you, full range of motion, explosive pull.", "progression": "Add more reps or weight with belt."}
        ]
    },
    "Triceps": {
        "icon": "⚡",
        "description": "Maximize arm size with lockout power and horseshoe triceps.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Close-Grip Bench Press", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Hands 6-8 inches apart, lower to chest, press explosively.", "progression": "Increase weight by 5-10 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Tricep Dips", "details": "3 sets x 8-10 reps | Rest: 2 mins", "form": "Lower body until elbows are ~90 degrees, drive back up.", "progression": "Add weight with dipping belt or increase reps."},
            {"type": "Isolation 1", "name": "Tricep Rope Pushdowns", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Keep elbows pinned, push rope down, spread handles at bottom.", "progression": "Increase cable weight."},
            {"type": "Isolation 2", "name": "Skull Crushers (EZ-Bar)", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Lie on bench, lower bar to forehead, extend elbows back up.", "progression": "Increase weight or reps."},
            {"type": "Overhead Extension", "name": "Overhead Cable Tricep Extension", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Extend arms forward/overhead, squeeze triceps at lockout.", "progression": "Increase weight."},
            {"type": "Finisher", "name": "Diamond Push-ups", "details": "3 sets x 15-20 reps | Rest: 45-60 secs", "form": "Hands close together forming diamond shape under chest.", "progression": "Decrease rest time between sets."}
        ]
    },
    "Quadriceps": {
        "icon": "🦵",
        "description": "Build strong, explosive legs and leg quad sweep.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Back Squat", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Squat below parallel, keep chest up, drive through heels.", "progression": "Increase weight by 5-10 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Leg Press Machine", "details": "3 sets x 8-10 reps | Rest: 2 mins", "form": "Feet hip-width apart, lower sled deep without lifting lower back.", "progression": "Add weight plates."},
            {"type": "Quad Isolation 1", "name": "Leg Extensions Machine", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Extend legs straight out, hold contraction at top for 1 second.", "progression": "Increase machine weight."},
            {"type": "Unilateral Exercise", "name": "Bulgarian Split Squats", "details": "3 sets x 10-12 reps per leg | Rest: 90 secs", "form": "One foot elevated behind, lower back knee toward floor.", "progression": "Hold heavier dumbbells."},
            {"type": "Finisher", "name": "Walking Bodyweight Lunges", "details": "3 sets x 20 reps total | Rest: 45-60 secs", "form": "Step forward, drop hips straight down, maintain balance.", "progression": "Add weight or do jumping lunges."}
        ]
    },
    "Hamstrings": {
        "icon": "🏃‍♂️",
        "description": "Target the posterior chain for athletic speed and knee stability.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Romanian Deadlift (RDL)", "details": "4 sets x 6-8 reps | Rest: 2-3 mins", "form": "Hinge hips back, lower bar along shins until hamstring stretch.", "progression": "Increase weight by 5-10 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Lying Leg Curls Machine", "details": "3 sets x 8-10 reps | Rest: 90 secs", "form": "Curl pad toward glutes, squeeze hamstrings, lower slowly.", "progression": "Increase weight or reps."},
            {"type": "Isolation", "name": "Seated Leg Curl Machine", "details": "3 sets x 10-12 reps | Rest: 60-90 secs", "form": "Keep thighs locked down, flex knees fully.", "progression": "Increase weight."},
            {"type": "Glute/Ham Focus", "name": "Glute-Ham Raise or Nordic Curls", "details": "3 sets x 8-10 reps | Rest: 90 secs", "form": "Lower torso under control using hamstrings to resist gravity.", "progression": "Increase reps or reduce assistance."},
            {"type": "Finisher", "name": "Kettlebell Swings", "details": "3 sets x 15-20 reps | Rest: 60 secs", "form": "Explosive hip hinge, drive hips forward to swing bell to eye level.", "progression": "Increase kettlebell weight."}
        ]
    },
    "Glutes": {
        "icon": "🍑",
        "description": "Develop glute strength and hip extension power.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Hip Thrusts", "details": "4 sets x 8-10 reps | Rest: 2 mins", "form": "Upper back against bench, drive hips up, squeeze glutes at top.", "progression": "Increase weight weekly."},
            {"type": "Secondary Exercise", "name": "Cable Pull-Throughs", "details": "3 sets x 10-12 reps | Rest: 90 secs", "form": "Stand facing away from cable, hinge at hips, drive glutes forward.", "progression": "Increase cable weight."},
            {"type": "Isolation", "name": "Glute Kickback Machine / Cable", "details": "3 sets x 12-15 reps per leg | Rest: 60 secs", "form": "Kick leg backward using glutes, keep spine neutral.", "progression": "Increase weight."},
            {"type": "Finisher", "name": "Frog Pumps", "details": "3 sets x 20-30 reps | Rest: 45 secs", "form": "Soles of feet together, lift hips up rapidly squeezing glutes.", "progression": "Add dumbbell on hips."}
        ]
    },
    "Calves": {
        "icon": "👟",
        "description": "Strengthen calves for jump power and lower leg definition.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Standing Calf Raises", "details": "4 sets x 10-12 reps | Rest: 60-90 secs", "form": "Full stretch at bottom, press up onto toes, hold 1s at top.", "progression": "Increase weight plate / machine weight."},
            {"type": "Secondary Exercise", "name": "Seated Calf Raise Machine", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Focus on soleus muscle, smooth rhythm throughout movement.", "progression": "Increase weight."},
            {"type": "Finisher", "name": "Single-Leg Bodyweight Calf Raise", "details": "3 sets x 20 reps per leg | Rest: 45 secs", "form": "Stand on edge of step, complete full range of motion.", "progression": "Hold dumbbell on same side."}
        ]
    },
    "Abs": {
        "icon": "🔥",
        "description": "Strengthen core stability and sculpt abdominal muscles.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Hanging Leg / Knee Raises", "details": "4 sets x 10-12 reps | Rest: 60 secs", "form": "Hang from bar, raise knees or toes to bar without swinging.", "progression": "Keep legs straight or add ankle weights."},
            {"type": "Secondary Exercise", "name": "Ab Wheel Rollouts", "details": "3 sets x 8-10 reps | Rest: 60 secs", "form": "Kneel down, roll wheel forward maintaining flat lower back.", "progression": "Roll out farther or perform standing."},
            {"type": "Machine Focus", "name": "Cable Crunches", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Kneel beneath rope attachment, crunch ribcage down toward hips.", "progression": "Increase cable resistance."},
            {"type": "Finisher", "name": "Plank Hold", "details": "3 sets x 45-60 seconds | Rest: 45 secs", "form": "Elbows under shoulders, keep body in flat straight line.", "progression": "Increase hold duration."}
        ]
    },
    "Obliques": {
        "icon": "🔄",
        "description": "Build rotational power and lateral core stability.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Cable Woodchoppers", "details": "3 sets x 12-15 reps per side | Rest: 60 secs", "form": "Rotate torso from high-to-low or low-to-high, pivot back foot.", "progression": "Increase cable weight."},
            {"type": "Secondary Exercise", "name": "Russian Twists with Weight", "details": "3 sets x 15-20 reps total | Rest: 60 secs", "form": "Sit on floor, lean back slightly, rotate weight side to side.", "progression": "Increase weight plate size."},
            {"type": "Finisher", "name": "Side Plank Hip Dips", "details": "3 sets x 12-15 reps per side | Rest: 45 secs", "form": "Hold side plank, lower hip toward floor, drive back up.", "progression": "Increase reps or hold plank longer."}
        ]
    },
    "Forearms": {
        "icon": "✊",
        "description": "Improve grip strength and forearm muscularity.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Wrist Curls", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Forearms resting on bench, curl bar up with wrists.", "progression": "Increase barbell weight."},
            {"type": "Secondary Exercise", "name": "Reverse Barbell Curls", "details": "3 sets x 10-12 reps | Rest: 60 secs", "form": "Overhand grip on barbell, curl up toward shoulders.", "progression": "Increase weight."},
            {"type": "Finisher", "name": "Farmer's Carries", "details": "3 sets x 45-60 seconds hold | Rest: 60 secs", "form": "Hold heavy dumbbells at sides, walk tall with tight grip.", "progression": "Increase dumbbell weight."}
        ]
    },
    "Lower Back": {
        "icon": "🪵",
        "description": "Fortify spine stability and spinal erectors.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Deadlift", "details": "3 sets x 5 reps | Rest: 2-3 mins", "form": "Flat back, drive feet into floor, stand tall squeezing glutes.", "progression": "Increase weight by 5-10 lbs weekly."},
            {"type": "Secondary Exercise", "name": "Good Mornings", "details": "3 sets x 8-10 reps | Rest: 90 secs", "form": "Barbell on upper back, hinge at hips while keeping back straight.", "progression": "Increase light barbell weight."},
            {"type": "Finisher", "name": "Superman Holds", "details": "3 sets x 12-15 reps | Rest: 45 secs", "form": "Lie face down, lift chest and thighs off floor simultaneously.", "progression": "Hold top position for 3 seconds each."}
        ]
    },
    "Upper Back / Traps": {
        "icon": "🦅",
        "description": "Build thick neck, trap, and rear-shoulder muscles.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Barbell Shrugs", "details": "4 sets x 10-12 reps | Rest: 90 secs", "form": "Shrug shoulders straight up toward ears, pause at top.", "progression": "Increase barbell weight."},
            {"type": "Secondary Exercise", "name": "Dumbbell Shrugs", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Hold dumbbells at sides, shrug up and squeeze traps.", "progression": "Increase dumbbell weight."},
            {"type": "Finisher", "name": "Rack Pulls", "details": "3 sets x 8-10 reps | Rest: 2 mins", "form": "Set bar above knee height, pull weight up locking shoulders back.", "progression": "Increase weight."}
        ]
    },
    "Hip Abductors / Adductors": {
        "icon": "↕️",
        "description": "Strengthen inner & outer hips for athletic stability.",
        "exercises": [
            {"type": "Primary Exercise", "name": "Seated Hip Abductor Machine", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Push legs outward against pad, squeeze outer glutes.", "progression": "Increase machine stack weight."},
            {"type": "Secondary Exercise", "name": "Seated Hip Adductor Machine", "details": "3 sets x 12-15 reps | Rest: 60 secs", "form": "Squeeze legs together targeting inner thighs.", "progression": "Increase machine weight."},
            {"type": "Finisher", "name": "Side Plank Hip Abduction", "details": "3 sets x 12-15 reps per side | Rest: 45 secs", "form": "Side plank position, raise top leg up and down smoothly.", "progression": "Increase hold time or reps."}
        ]
    }
}

# ------------------------------------------------------------------
# SECTION 4: DISTANCE CALCULATION (Haversine Formula)
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
    user_data = all_data.get(username, {"habits": {}, "goals": []})
    user_data.setdefault("habits", {})
    user_data.setdefault("goals", [])
    return user_data

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
# SECTION 5A: WORKOUT GOAL CALENDAR HELPERS
# ------------------------------------------------------------------
def get_completed_workout_days(user_data):
    """Return the set of every date (YYYY-MM-DD) with at least one logged workout across all habits."""
    days = set()
    for habit in user_data["habits"].values():
        for entry in habit["logs"]:
            days.add(entry["date"])
    return days

def count_completed_workouts(user_data):
    """Total number of workout logs (completed workouts) across all habits."""
    return sum(len(habit["logs"]) for habit in user_data["habits"].values())

def add_goal(user_data, title, target_date_str, habit_name="", target_value=None):
    """Create a new workout goal and add it to the user's goal list."""
    goal = {
        "id": f"g_{int(datetime.now().timestamp() * 1000)}",
        "title": title,
        "habit_name": habit_name,
        "target_date": target_date_str,
        "target_value": target_value,
        "completed": False,
        "created_at": date.today().strftime("%Y-%m-%d"),
    }
    user_data["goals"].append(goal)
    return goal

def set_goal_completed(user_data, goal_id, completed):
    """Mark a goal as completed (or not) by id."""
    for goal in user_data["goals"]:
        if goal["id"] == goal_id:
            goal["completed"] = completed
            break

def delete_goal(user_data, goal_id):
    """Remove a goal by id."""
    user_data["goals"] = [g for g in user_data["goals"] if g["id"] != goal_id]

def goals_on_date(goals, date_str):
    """Return every goal whose target_date matches the given date string."""
    return [g for g in goals if g["target_date"] == date_str]

# ------------------------------------------------------------------
# SECTION 5B: USER PROFILE DATA HELPERS
# ------------------------------------------------------------------
PROFILE_FILE = "profile_data.json"

def load_all_profiles():
    """Read the whole profile_data.json file into a Python dict."""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_all_profiles(all_profiles):
    """Write the whole profile data dict back to profile_data.json."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(all_profiles, f, indent=2)

def get_user_profile(username):
    """Get the profile data for one user, or return defaults if not found."""
    all_profiles = load_all_profiles()
    if username in all_profiles:
        return all_profiles[username]
    return {
        "full_name": username,
        "email": "",
        "fitness_level": "Beginner",
        "favorite_workout": "General Fitness",
        "avatar_emoji": "🏋️",
        "bio": "FitPulse Member",
        "created_at": date.today().strftime("%Y-%m-%d"),
    }

def save_user_profile(username, profile_data):
    """Save one user's profile data back into the shared file."""
    all_profiles = load_all_profiles()
    all_profiles[username] = profile_data
    save_all_profiles(all_profiles)

def update_user_profile(username, **kwargs):
    """Update specific fields in a user's profile."""
    profile = get_user_profile(username)
    profile.update(kwargs)
    save_user_profile(username, profile)

FITNESS_LEVELS = ["Beginner", "Intermediate", "Advanced"]
WORKOUT_TYPES = [
    "Running", "Weightlifting", "Yoga", "Cycling", "Swimming",
    "CrossFit", "Pilates", "HIIT", "General Fitness",
]
AVATAR_EMOJIS = ["🏋️", "🏃", "🚴", "🏊", "🧘", "💪", "⛹️", "🤸", "🏃‍♀️"]

# ------------------------------------------------------------------
# SECTION 5C: COMMUNITY DATA HELPERS (friends + chat)
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
    """Return every name that has ever used FitPulse."""
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

def remove_friend(name, friend_name):
    """Remove a friendship between two people (mutual, both directions)."""
    data = load_community_data()
    if name in data["friends"] and friend_name in data["friends"][name]:
        data["friends"][name].remove(friend_name)
    if friend_name in data["friends"] and name in data["friends"][friend_name]:
        data["friends"][friend_name].remove(friend_name)
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
    if not text.strip():
        return
    data = load_community_data()
    key = chat_key(sender, recipient)
    data["messages"].setdefault(key, [])
    data["messages"][key].append({
        "sender": sender,
        "text": text.strip(),
        "time": datetime.now().strftime("%I:%M %p"),
    })
    save_community_data(data)

# ------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "gym_finder"
if "username" not in st.session_state:
    st.session_state.username = "Alex"
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "selected_muscle" not in st.session_state:
    st.session_state.selected_muscle = None

register_user(st.session_state.username)

# ------------------------------------------------------------------
# SECTION 6: NAVIGATION / HEADER
# ------------------------------------------------------------------
def render_header():
    """Renders top header, nav bar, and user switcher."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### ⚡ **FitPulse** Fitness Portal")
    
    with col2:
        username = st.text_input("User Account:", value=st.session_state.username, key="user_account_input")
        if username != st.session_state.username:
            st.session_state.username = username
            register_user(username)
            st.rerun()

    # Nav Bar Tabs
    nav_cols = st.columns(7)
    pages = [
        ("gym_finder", "📍 Gym Finder"),
        ("gym_sessions", "🏋️ Workout Plans"),
        ("habits", "🏃 Habit Tracker"),
        ("goal_calendar", "📅 Goal Calendar"),
        ("community", "💬 Chat / Community"),
        ("friends_list", "👥 Friends List"),
        ("profile", "👤 Profile"),
    ]
    
    for idx, (p_id, label) in enumerate(pages):
        btn_type = "primary" if st.session_state.page == p_id else "secondary"
        if nav_cols[idx].button(label, key=f"nav_btn_{p_id}", type=btn_type, use_container_width=True):
            st.session_state.page = p_id
            if p_id != "gym_sessions":
                st.session_state.selected_muscle = None
            st.rerun()

# ------------------------------------------------------------------
# SECTION 7: RENDER PAGES
# ------------------------------------------------------------------

def render_gym_finder():
    """Renders modern Gym Finder screen."""
    st.markdown(
        """
        <div class="fitpulse-locator-hero">
            <h1>📍 FIND NEARBY GYMS & FITNESS CENTERS</h1>
            <p>Locate the top fitness facilities around your area with real-time distance calculations and amenity lists.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_city = st.selectbox("Select Your City/Location:", list(SAMPLE_LOCATIONS.keys()))
    with col2:
        max_radius = st.slider("Search Radius (Miles):", 1, 25, 10)
    with col3:
        sort_by = st.selectbox("Sort By:", ["Distance (Closest)", "Rating (Highest)"])

    user_lat, user_lon = SAMPLE_LOCATIONS[selected_city]
    
    results = []
    for gym in FITNESS_CENTERS:
        dist = distance_in_miles(user_lat, user_lon, gym["lat"], gym["lon"])
        if dist <= max_radius:
            results.append({**gym, "distance": dist})

    if sort_by == "Distance (Closest)":
        results.sort(key=lambda x: x["distance"])
    else:
        results.sort(key=lambda x: x["rating"], reverse=True)

    st.markdown(f"#### Showing {len(results)} Gyms near {selected_city}")

    for idx, gym in enumerate(results):
        is_closest = (idx == 0 and sort_by == "Distance (Closest)")
        closest_badge = '<div class="fitpulse-closest-tag">Closest Choice</div>' if is_closest else ''
        
        pills_html = "".join([f'<span class="fitpulse-pill">{a}</span>' for a in gym["amenities"]])
        
        st.markdown(
            f"""
            <div class="fitpulse-gym-card">
                {closest_badge}
                <div class="gym-top-row">
                    <div>
                        <h4>{gym['name']}</h4>
                        <div class="gym-address">{gym['address']}</div>
                    </div>
                    <span class="fitpulse-distance-badge">{gym['distance']:.1f} Miles</span>
                </div>
                <div>
                    <span class="fitpulse-rating-stars">★ {gym['rating']}</span>
                    <span class="fitpulse-rating-number">/ 5.0</span>
                </div>
                <div class="fitpulse-pill-row">
                    {pills_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_gym_sessions():
    """Renders the Gym Sessions workout selection screen and muscle detail page."""
    
    if st.session_state.get("selected_muscle") and st.session_state.selected_muscle in WORKOUT_PLANS:
        muscle_key = st.session_state.selected_muscle
        data = WORKOUT_PLANS[muscle_key]
        
        if st.button("⬅ Back to All Muscle Groups", key="back_to_muscles"):
            st.session_state.selected_muscle = None
            st.rerun()
            
        st.markdown(
            f"""
            <div class="fitpulse-hero" style="background: linear-gradient(135deg, #1C1C1A 0%, #3A4D39 100%);">
                <h1 style="font-size: 42px; color: #E8F5E9;">{data['icon']} {muscle_key.upper()} WORKOUT PLAN</h1>
                <p style="font-size: 18px; color: #C8E6C9;">{data['description']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="fitpulse-section-header">📋 Exercises, Reps & Form Guidelines</div>', unsafe_allow_html=True)
        
        for idx, ex in enumerate(data["exercises"], 1):
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #7C9473; border-radius: 12px; padding: 20px; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                    <span style="display: inline-block; background-color: #EAF1E7; color: #2A2A26; font-weight: bold; padding: 4px 10px; border-radius: 6px; font-size: 13px; margin-bottom: 8px;">{ex['type'].upper()}</span>
                    <h3 style="margin-top: 0; color: #2A2A26; font-size: 20px;">{idx}. {ex['name']}</h3>
                    <p style="margin: 4px 0;"><strong>📊 Details:</strong> {ex['details']}</p>
                    <p style="margin: 4px 0;"><strong>💡 Form:</strong> {ex['form']}</p>
                    <p style="margin: 4px 0;"><strong>📈 Progression:</strong> {ex['progression']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    else:
        st.markdown(
            """
            <div class="fitpulse-hero" style="background: linear-gradient(135deg, #1C1C1A 0%, #3A4D39 100%); padding: 36px 28px;">
                <h1 style="font-size: 40px; color: #E8F5E9;">🔥 WHAT DO YOU WANT TO WORK OUT TODAY? 🔥</h1>
                <p style="font-size: 18px; color: #C8E6C9;">Pick a muscle group below to unlock full exercise plans and rep guides!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        muscle_names = list(WORKOUT_PLANS.keys())
        cols = st.columns(3)
        for i, m_name in enumerate(muscle_names):
            col = cols[i % 3]
            m_data = WORKOUT_PLANS[m_name]
            with col:
                btn_label = f"{m_data['icon']} {m_name}\n\n{m_data['description']}"
                if st.button(btn_label, key=f"muscle_btn_{m_name}", use_container_width=True):
                    st.session_state.selected_muscle = m_name
                    st.rerun()

def render_habit_tracker():
    """Renders Habit Tracker view."""
    user = st.session_state.username
    user_data = get_user_data(user)
    habits = user_data["habits"]

    st.markdown(
        f"""
        <div class="fitpulse-hero">
            <h1>🏃 HABIT TRACKER</h1>
            <p>Welcome back, <strong>{user}</strong>! Log your routines and keep your streaks active.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="fitpulse-section-header">➕ Add New Habit</div>', unsafe_allow_html=True)
        with st.form("new_habit_form"):
            h_name = st.text_input("Habit Name:")
            h_dist = st.number_input("Target Distance (Miles):", min_value=0.1, value=1.0, step=0.5)
            h_freq = st.selectbox("Frequency:", ["Daily", "Weekly", "Custom"])
            submit = st.form_submit_button("Save Habit")
            
            if submit and h_name:
                habits[h_name] = {
                    "goal_distance": h_dist,
                    "frequency": h_freq,
                    "logs": []
                }
                save_user_data(user, user_data)
                st.success(f"Habit '{h_name}' created!")
                st.rerun()

    with col2:
        st.markdown('<div class="fitpulse-section-header">📊 Your Active Habits</div>', unsafe_allow_html=True)
        if not habits:
            st.info("No habits logged yet. Create one using the form on the left!")
            return

        for name, h_info in habits.items():
            logs = h_info["logs"]
            streak = compute_streak(logs)
            stats = compute_habit_stats(logs)
            
            with st.expander(f"📌 {name} (Streak: {streak} Days 🔥)", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Workouts", stats["total_runs"])
                c2.metric("Total Distance", f"{stats['total_distance']} mi")
                c3.metric("Avg Speed", f"{stats['avg_speed']} mph")
                
                if not logged_today(logs):
                    st.markdown("##### Log Today's Session:")
                    with st.form(f"log_form_{name}"):
                        lc1, lc2 = st.columns(2)
                        l_dist = lc1.number_input("Distance (mi):", value=float(h_info["goal_distance"]), key=f"d_{name}")
                        l_dur = lc2.number_input("Duration (mins):", value=10.0, key=f"dur_{name}")
                        if st.form_submit_button("Record Session"):
                            speed = (l_dist / (l_dur / 60.0)) if l_dur > 0 else 0.0
                            logs.append({
                                "date": date.today().strftime("%Y-%m-%d"),
                                "distance": l_dist,
                                "duration_min": l_dur,
                                "speed_mph": round(speed, 2)
                            })
                            save_user_data(user, user_data)
                            st.success("Session logged!")
                            st.rerun()
                else:
                    st.success("✅ Logged for today!")

def render_goal_calendar():
    """Renders Goal Calendar view."""
    user = st.session_state.username
    user_data = get_user_data(user)
    
    st.markdown(
        """
        <div class="fitpulse-hero">
            <h1>📅 WORKOUT GOAL CALENDAR</h1>
            <p>Set targets and monitor workout completion across the month.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="fitpulse-section-header">🎯 Set Target Goal</div>', unsafe_allow_html=True)
        g_title = st.text_input("Goal Title:")
        g_date = st.date_input("Target Date:", value=date.today())
        if st.button("Add Goal to Calendar"):
            if g_title:
                add_goal(user_data, g_title, g_date.strftime("%Y-%m-%d"))
                save_user_data(user, user_data)
                st.success("Goal added!")
                st.rerun()

    with c2:
        st.markdown('<div class="fitpulse-section-header">🗓 Calendar Overview</div>', unsafe_allow_html=True)
        completed_days = get_completed_workout_days(user_data)
        
        today = date.today()
        cal = calendar.Calendar()
        month_days = cal.monthdatescalendar(today.year, today.month)
        
        st.write(f"### {today.strftime('%B %Y')}")
        
        for week in month_days:
            cols = st.columns(7)
            for i, d in enumerate(week):
                d_str = d.strftime("%Y-%m-%d")
                is_workout = d_str in completed_days
                day_goals = goals_on_date(user_data["goals"], d_str)
                
                bg = "#EAF1E7" if is_workout else "#FFFFFF"
                border = "#7C9473" if is_workout else "#E0E0E0"
                
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style="background:{bg}; border:1px solid {border}; border-radius:8px; padding:6px; min-height:60px;">
                            <strong>{d.day}</strong>
                            {'<br>✅ Worked Out' if is_workout else ''}
                            {'<br>🎯 ' + str(len(day_goals)) + ' Goal(s)' if day_goals else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

def render_community():
    """Renders Community Chat view."""
    user = st.session_state.username
    friends = get_friends(user)

    st.markdown(
        """
        <div class="fitpulse-hero">
            <h1>💬 COMMUNITY CHAT</h1>
            <p>Connect and chat directly with your fitness friends.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not friends:
        st.warning("You haven't added any friends yet. Visit the Friends List tab to add people!")
        return

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="fitpulse-section-header">👥 Select Friend</div>', unsafe_allow_html=True)
        active = st.radio("Friends:", friends, key="chat_friend_radio")
        st.session_state.active_chat = active

    with c2:
        if st.session_state.active_chat:
            recipient = st.session_state.active_chat
            st.markdown(f'<div class="fitpulse-section-header">Chat with {recipient}</div>', unsafe_allow_html=True)
            
            messages = get_messages(user, recipient)
            chat_container = st.container()
            
            with chat_container:
                for msg in messages:
                    is_me = msg["sender"] == user
                    align = "right" if is_me else "left"
                    bg = "#EAF1E7" if is_me else "#F4F2EC"
                    st.markdown(
                        f"""
                        <div style="text-align: {align}; margin-bottom: 8px;">
                            <div style="display: inline-block; background: {bg}; padding: 8px 14px; border-radius: 12px; max-width: 70%;">
                                <strong>{msg['sender']}</strong> <small>({msg['time']})</small><br>
                                {msg['text']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            with st.form("send_msg_form", clear_on_submit=True):
                txt = st.text_input("Type message:")
                if st.form_submit_button("Send") and txt:
                    send_message(user, recipient, txt)
                    st.rerun()

def render_friends_list():
    """Renders Friends List management view."""
    user = st.session_state.username
    all_users = get_all_users()
    friends = get_friends(user)

    st.markdown(
        """
        <div class="fitpulse-hero">
            <h1>👥 FRIENDS & NETWORK</h1>
            <p>Find new fitness partners and manage your existing network.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="fitpulse-section-header">🔍 Discover People</div>', unsafe_allow_html=True)
        others = [u for u in all_users if u != user and u not in friends]
        if not others:
            st.info("No new users to discover.")
        for ot in others:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"👤 **{ot}**")
            if col_b.button("Add Friend", key=f"add_{ot}"):
                add_friend(user, ot)
                st.success(f"Added {ot}!")
                st.rerun()

    with c2:
        st.markdown('<div class="fitpulse-section-header">💚 Your Friends</div>', unsafe_allow_html=True)
        if not friends:
            st.info("No friends added yet.")
        for fr in friends:
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"🤝 **{fr}**")
            if col_b.button("Remove", key=f"rem_{fr}"):
                remove_friend(user, fr)
                st.rerun()

def render_profile():
    """Renders User Profile view."""
    user = st.session_state.username
    prof = get_user_profile(user)

    st.markdown(
        """
        <div class="fitpulse-hero">
            <h1>👤 USER PROFILE</h1>
            <p>Manage your account info and fitness preferences.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="fitpulse-profile-card">
            <div class="fitpulse-profile-header">
                <div class="fitpulse-profile-avatar-large">{prof.get('avatar_emoji', '🏋️')}</div>
                <div class="fitpulse-profile-name-section">
                    <h2>{prof.get('full_name', user)}</h2>
                    <p>@{user} • Member since {prof.get('created_at', '2026')}</p>
                    <p><em>"{prof.get('bio', 'Staying active!')}"</em></p>
                </div>
            </div>
            <div class="fitpulse-profile-attributes">
                <div class="fitpulse-profile-attr-item">
                    <div class="fitpulse-profile-attr-label">Fitness Level</div>
                    <div class="fitpulse-profile-attr-value">{prof.get('fitness_level', 'Beginner')}</div>
                </div>
                <div class="fitpulse-profile-attr-item">
                    <div class="fitpulse-profile-attr-label">Favorite Focus</div>
                    <div class="fitpulse-profile-attr-value">{prof.get('favorite_workout', 'General')}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("✏️ Edit Profile Info"):
        with st.form("edit_profile_form"):
            fn = st.text_input("Full Name:", value=prof.get("full_name", user))
            bio = st.text_area("Bio:", value=prof.get("bio", ""))
            lvl = st.selectbox("Fitness Level:", FITNESS_LEVELS, index=FITNESS_LEVELS.index(prof.get("fitness_level", "Beginner")))
            fav = st.selectbox("Favorite Workout:", WORKOUT_TYPES, index=WORKOUT_TYPES.index(prof.get("favorite_workout", "General Fitness")))
            emoji = st.selectbox("Avatar Emoji:", AVATAR_EMOJIS, index=AVATAR_EMOJIS.index(prof.get("avatar_emoji", "🏋️")))
            
            if st.form_submit_button("Save Profile"):
                update_user_profile(user, full_name=fn, bio=bio, fitness_level=lvl, favorite_workout=fav, avatar_emoji=emoji)
                st.success("Profile updated!")
                st.rerun()

# ------------------------------------------------------------------
# SECTION 8: APP ENTRY POINT / ROUTER
# ------------------------------------------------------------------
render_header()

if st.session_state.page == "gym_finder":
    render_gym_finder()
elif st.session_state.page == "gym_sessions":
    render_gym_sessions()
elif st.session_state.page == "habits":
    render_habit_tracker()
elif st.session_state.page == "goal_calendar":
    render_goal_calendar()
elif st.session_state.page == "community":
    render_community()
elif st.session_state.page == "friends_list":
    render_friends_list()
elif st.session_state.page == "profile":
    render_profile()

st.markdown(
    """
    <div class="fitpulse-cta-banner">
        <h3>READY TO PUSH YOUR LIMITS?</h3>
        <p>Track your daily habits, explore gyms near you, and crush your fitness targets every single day.</p>
    </div>
    """,
    unsafe_allow_html=True