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

    /* --- CLICKABLE FEATURE CARDS: the button itself IS the card ---
       Instead of overlaying an invisible button on top of decorative
       HTML (which was unreliable to click), we style the real
       st.button directly so it looks exactly like the other feature
       cards. Since there's only one real element here, clicking
       anywhere on it always works. Both Habit Tracking and
       Communities use this same pattern. */
    .st-key-habit_tracking_card button,
    .st-key-community_card button,
    .st-key-gym_finder_card button,
    .st-key-friends_list_card button,
    .st-key-goal_calendar_card button {
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
    .st-key-goal_calendar_card button:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 22px rgba(0,0,0,0.14) !important;
        border-top-color: #2A2A26 !important;
    }
    .st-key-habit_tracking_card button:active,
    .st-key-community_card button:active,
    .st-key-gym_finder_card button:active,
    .st-key-friends_list_card button:active,
    .st-key-goal_calendar_card button:active {
        transform: translateY(-1px);
    }
    .st-key-habit_tracking_card button p,
    .st-key-community_card button p,
    .st-key-gym_finder_card button p,
    .st-key-friends_list_card button p,
    .st-key-goal_calendar_card button p {
        margin: 6px 0 0 0;
        color: #444;
        font-size: 14px;
        white-space: pre-line;
    }
    .st-key-habit_tracking_card button p:first-of-type,
    .st-key-community_card button p:first-of-type,
    .st-key-gym_finder_card button p:first-of-type,
    .st-key-friends_list_card button p:first-of-type,
    .st-key-goal_calendar_card button p:first-of-type {
        font-size: 34px;
        margin-top: 0;
    }
    .st-key-habit_tracking_card button p strong,
    .st-key-community_card button p strong,
    .st-key-gym_finder_card button p strong,
    .st-key-friends_list_card button p strong,
    .st-key-goal_calendar_card button p strong {
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

    /* --- TOP NAVIGATION BAR (feature quick-links, top-left of header) --- */
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

    /* --- COMMUNITY: chat bubbles reuse the same result-card style --- */
    .fitpulse-friend-name {
        font-weight: 700;
        color: #2A2A26;
    }

    /* --- FRIENDS LIST: friend card styling --- */
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

    /* --- BOTTOM CTA BANNER: now a real photo instead of a flat color,
       so the bottom of the page has some life to it. The gradient
       overlay keeps the white text readable over any photo. --- */
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

    /* --- COMMUNITY PHOTO GALLERY ---
       A few real, free-to-use photos of people working out (Unsplash,
       free license) so the site feels less like an empty template and
       more like an actual community of people staying active. Each
       photo gets a subtle earthy-green duotone wash (via the ::after
       overlay) so they all feel like they belong to the same neutral
       palette instead of clashing with it, plus a soft caption. */
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

    /* Stack the photo grid to 2 columns on narrower screens */
    @media (max-width: 700px) {
        .fitpulse-photo-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .fitpulse-photo-card {
            height: 150px;
        }
    }

    /* ================================================================
       GYM FINDER PAGE — modernized, standalone locator experience.
       A punchier gradient hero, a "glass" toolbar for the search
       controls, and animated result cards with star ratings and
       amenity pills (instead of plain text lines).
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

    /* Glassy toolbar wrapping the location/radius/sort controls */
    .fitpulse-locator-toolbar {
        background: rgba(85, 112, 76, 0.06);
        border: 1px solid rgba(85, 112, 76, 0.18);
        border-radius: 16px;
        padding: 20px 22px 6px 22px;
        margin-bottom: 20px;
    }

    /* Modern result cards: soft shadow, gradient top accent, lift on hover */
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
# Real fitness centers from the NJ/NY area with accurate addresses
# and coordinates. These are actual gyms you can find and visit!
# ------------------------------------------------------------------
FITNESS_CENTERS = [
    # Union City / North Bergen Area
    {"name": "Crunch Fitness - North Bergen", "address": "2819 John F Kennedy Blvd, North Bergen, NJ 07047",
     "lat": 40.8162, "lon": -74.0207, "rating": 4.5, "amenities": ["24/7 Access", "Group Classes", "Free Weights"]},
    
    # Hoboken Area
    {"name": "New York Sports Club - Hoboken", "address": "210 14th St, Hoboken, NJ 07030",
     "lat": 40.7357, "lon": -74.0324, "rating": 4.6, "amenities": ["Personal Training", "Sauna", "Group Classes"]},
    {"name": "Fitness Factory - Hoboken", "address": "130 Washington St, Hoboken, NJ 07030",
     "lat": 40.7361, "lon": -74.0316, "rating": 4.7, "amenities": ["Free Weights", "Cardio", "Strength Training"]},
    
    # Jersey City Area
    {"name": "Fitness Factory - Jersey City", "address": "525 Washington Boulevard, Jersey City, NJ 07310",
     "lat": 40.7180, "lon": -74.0450, "rating": 4.4, "amenities": ["24/7 Access", "Group Classes", "Personal Training"]},
    
    # Union / North Newark Area
    {"name": "Planet Fitness - Union", "address": "2445 Springfield Ave, Union, NJ 07088",
     "lat": 40.6700, "lon": -74.2757, "rating": 4.3, "amenities": ["Massage Chairs", "Hydro Massage", "Free Weights"]},
    
    # Newark Area
    {"name": "Planet Fitness - Newark", "address": "520 Broad St, Newark, NJ 07102",
     "lat": 40.7357, "lon": -74.1724, "rating": 4.2, "amenities": ["Free Fitness Training", "Cardio", "Strength Equipment"]},
    {"name": "YMCA of Newark - Central Branch", "address": "600 Broad St, Newark, NJ 07102",
     "lat": 40.7365, "lon": -74.1730, "rating": 4.4, "amenities": ["Pool", "Youth Programs", "Basketball Court"]},
    
    # Manhattan Area
    {"name": "Chelsea Piers Fitness", "address": "Pier 60, Chelsea Piers, New York, NY 10011",
     "lat": 40.7467, "lon": -74.0103, "rating": 4.8, "amenities": ["Rock Climbing", "Pool", "Cold Plunge", "Sauna"]},
]

# Real sample locations in the NJ/NY area with accurate coordinates
SAMPLE_LOCATIONS = {
    "Union City, NJ": (40.7795, -74.0237),
    "Jersey City, NJ": (40.7190, -74.0450),
    "Hoboken, NJ": (40.7357, -74.0324),
    "Newark, NJ": (40.7357, -74.1724),
    "New York, NY": (40.7467, -74.0103),
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
# Goals are separate from habits: a habit is a recurring routine you
# log day to day, while a goal is a specific target ("Run 5 miles by
# Aug 15") tied to a date on the calendar. Goals live alongside habits
# in the same per-user record in habit_data.json, under the "goals"
# key, so everything for a user stays in one file.
#
# Goal shape:
#   {"id": "g_1690000000000", "title": "Run 5 miles", "habit_name":
#    "Daily 1-Mile Run" (or "" if not linked), "target_date":
#    "2026-08-15", "target_value": 5.0, "completed": False,
#    "created_at": "2026-08-01"}
# ------------------------------------------------------------------
def get_completed_workout_days(user_data):
    """Return the set of every date (YYYY-MM-DD) with at least one
    logged workout across all of a user's habits — i.e. every day a
    workout was actually completed, used to mark the calendar."""
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
# Store user profile information (username, fitness level, 
# favorite workout, avatar emoji, bio) in a separate JSON file.
# This allows personalization while keeping habit data separate.
#
# Data shape:
# {
#   "Alex": {
#     "full_name": "Alexander Johnson",
#     "email": "alex@example.com",
#     "fitness_level": "intermediate",
#     "favorite_workout": "running",
#     "avatar_emoji": "🏃",
#     "bio": "Love morning runs!",
#     "created_at": "2026-07-28"
#   }
# }
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
    # Return default profile if user doesn't have one yet
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


# Define fitness level and workout type options
FITNESS_LEVELS = ["Beginner", "Intermediate", "Advanced"]
WORKOUT_TYPES = [
    "Running",
    "Weightlifting",
    "Yoga",
    "Cycling",
    "Swimming",
    "CrossFit",
    "Pilates",
    "HIIT",
    "General Fitness",
]
AVATAR_EMOJIS = ["🏋️", "🏃", "🚴", "🏊", "🧘", "💪", "⛹️", "🤸", "🏃‍♀️"]


# ------------------------------------------------------------------
# SECTION 5C: COMMUNITY DATA HELPERS (friends + chat)
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


def remove_friend(name, friend_name):
    """Remove a friendship between two people (mutual, both directions)."""
    data = load_community_data()
    if name in data["friends"] and friend_name in data["friends"][name]:
        data["friends"][name].remove(friend_name)
    if friend_name in data["friends"] and name in data["friends"][friend_name]:
        data["friends"][friend_name].remove(name)
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
# SECTION 6: SESSION STATE (controls which "view" we're on) +
# LOGIN PERSISTENCE (controls whether you stay logged in)
#
# st.session_state only lives in memory for as long as your browser
# tab's connection to the app stays open — a page refresh throws it
# away and you'd be back to "Guest". To fix that, we ALSO save the
# logged-in username in a browser cookie. Cookies are little pieces
# of data the browser stores on your device and hands back to the
# app on every visit, so:
#   - Sign up / log in  -> we save a cookie on this device.
#   - Refresh the page  -> the cookie is still there, so we log you
#                           right back in automatically.
#   - Click "Log Out"   -> we delete the cookie, so you go back to
#                           being a Guest until you log in again.
# ------------------------------------------------------------------
LOGIN_COOKIE_NAME = "fitpulse_username"


def get_cookie_manager():
    """One CookieManager per script run, talking to the browser's cookies."""
    return stx.CookieManager(key="fitpulse_cookie_manager")


cookie_manager = get_cookie_manager()
# get_all() reads every cookie the browser has for this app. On the very
# first run in a brand-new tab this can briefly come back empty while the
# browser and the app finish their handshake — that's normal and Streamlit
# will automatically rerun once the real cookies arrive.
saved_cookies = cookie_manager.get_all(key="fitpulse_cookie_get_all") or {}

if "page" not in st.session_state:
    st.session_state.page = "home"

if "username" not in st.session_state:
    saved_username = (saved_cookies.get(LOGIN_COOKIE_NAME) or "").strip()
    st.session_state.username = saved_username or "Guest"


def login_user(name):
    """Log a user in for real: remember them in this tab's session AND
    write a cookie to this device so a page refresh (or closing and
    reopening the browser) keeps them logged in automatically."""
    name = name.strip() or "Guest"
    st.session_state.username = name
    cookie_manager.set(
        LOGIN_COOKIE_NAME,
        name,
        expires_at=datetime.now() + timedelta(days=365),
        key="fitpulse_cookie_set",
    )


def logout_user():
    """The ONLY way a user gets signed out: clears this tab's session
    AND deletes the saved cookie, so they won't be auto logged back in
    on the next refresh."""
    st.session_state.username = "Guest"
    st.session_state.page = "home"
    if LOGIN_COOKIE_NAME in saved_cookies:
        cookie_manager.delete(LOGIN_COOKIE_NAME, key="fitpulse_cookie_delete")


# ------------------------------------------------------------------
# Make sure this person shows up for others in "Discover People".
# ------------------------------------------------------------------
def init_username():
    global username
    username = st.session_state.username.strip() or "Guest"
    register_user(username)

init_username()

# ------------------------------------------------------------------
# SECTION 7: TOP-RIGHT HEADER (user profile + navigation)
# ------------------------------------------------------------------
username = st.session_state.username.strip() or "Guest"
user_profile = get_user_profile(username)
avatar_emoji = user_profile.get("avatar_emoji", "🏋️")

# Feature quick-links shown in the top navigation bar, in the same
# order as the feature cards on the home page, so the bar and the
# cards always point to the same set of pages.
NAV_ITEMS = [
    ("🏠", "Home", "home"),
    ("📍", "Gyms", "gym_finder"),
    ("🌐", "Community", "community"),
    ("✅", "Habits", "habits"),
    ("👥", "Friends", "friends_list"),
    ("🗓️", "Goals", "goal_calendar"),
]

header_col1, header_col2, header_col3 = st.columns([2.5, 0.5, 1.5])

with header_col1:
    with st.container(key="top_navbar"):
        nav_cols = st.columns(len(NAV_ITEMS))
        for nav_col, (nav_icon, nav_label, nav_page) in zip(nav_cols, NAV_ITEMS):
            with nav_col:
                is_active_page = st.session_state.page == nav_page
                if st.button(
                    f"{nav_icon} {nav_label}",
                    key=f"nav_{nav_page}",
                    use_container_width=True,
                    type="primary" if is_active_page else "secondary",
                ):
                    st.session_state.page = nav_page
                    st.rerun()

with header_col3:
    st.markdown(
        """
        <style>
        /* Small, square icon-only button for Log Out, sized to sit
           neatly next to the other header buttons. */
        .st-key-header_logout_btn button {
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="text-align: right; font-weight: 700; color: #2A2A26; margin-bottom: 8px;">{avatar_emoji} {username}</div>',
        unsafe_allow_html=True,
    )

    is_logged_in = username != "Guest"
    header_cols = st.columns(3 if is_logged_in else 2)
    col_profile = header_cols[0]
    col_back = header_cols[1]
    col_logout = header_cols[2] if is_logged_in else None

    with col_profile:
        if st.button("👤 Profile", use_container_width=True, key="header_profile_btn"):
            st.session_state.page = "profile"
            st.rerun()

    with col_back:
        if st.session_state.page in ("habits", "community", "gym_finder", "friends_list", "goal_calendar", "profile", "signup", "login"):
            if st.button("🏠 Home", use_container_width=True, key="back_to_home_header"):
                st.session_state.page = "home"
                st.rerun()

    # The ONLY way to sign out — clears the session AND deletes the
    # login cookie so you won't be auto logged back in on refresh.
    if col_logout is not None:
        with col_logout:
            if st.button("🚪", use_container_width=True, key="header_logout_btn", help="Log out"):
                logout_user()
                st.rerun()

st.divider()

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
        "so staying active is easier and more affordable. Tap **Gym Finder** below to "
        "open the locator."
    )

    # --- Feature card grid (5 cards: 3 in first row, 2 in second) ---
    feature_cols = st.columns(3)

    features = [
        ("📍", "Gym Finder", "Open the locator to search fitness centers near you."),
        ("🌐", "Communities", "Add friends and chat with people on FitPulse."),
        ("✅", "Habit Tracking", "Build and track healthy daily habits."),
    ]

    # Cards that actually navigate somewhere: title -> (container key,
    # button key, page to switch to). Each is rendered as ONE real
    # st.button styled (via CSS in SECTION 2) to look like a feature
    # card, instead of decorative HTML with an invisible button on top
    # — that overlay approach was unreliable to click. With a single
    # real button, clicking anywhere on the card always works. All
    # cards (Gym Finder, Communities, Habit Tracking, Friends List,
    # Goal Calendar) use this same pattern now, so each opens only
    # when its card is actually clicked — there's no duplicate content.
    CLICKABLE_CARDS = {
        "Gym Finder": ("gym_finder_card", "gym_finder_card_click", "gym_finder"),
        "Communities": ("community_card", "community_card_click", "community"),
        "Habit Tracking": ("habit_tracking_card", "habit_card_click", "habits"),
        "Friends List": ("friends_list_card", "friends_list_card_click", "friends_list"),
        "Goal Calendar": ("goal_calendar_card", "goal_calendar_card_click", "goal_calendar"),
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

    # --- Friends List + Goal Calendar cards (second row) ---
    second_row_cols = st.columns(2)
    with second_row_cols[0]:
        with st.container(key="friends_list_card"):
            friends_card_clicked = st.button(
                "👥\n\n**Friends List**\n\nView and manage all your FitPulse friends.",
                key="friends_list_card_click",
                use_container_width=True,
            )
            if friends_card_clicked:
                st.session_state.page = "friends_list"
                st.rerun()
    with second_row_cols[1]:
        with st.container(key="goal_calendar_card"):
            goal_calendar_clicked = st.button(
                "🗓️\n\n**Goal Calendar**\n\nSet workout goals and track completed workouts.",
                key="goal_calendar_card_click",
                use_container_width=True,
            )
            if goal_calendar_clicked:
                st.session_state.page = "goal_calendar"
                st.rerun()

    st.write("")  # small spacer
    st.divider()

    # --- Photo gallery: real people, working out, staying active ---
    # A handful of free-to-use (Unsplash License) photos so the page
    # feels lived-in instead of just icons and text — a little glimpse
    # of the kind of community FitPulse is for.
    st.markdown(
        '<div class="fitpulse-section-header">📸 Our Community in Motion</div>',
        unsafe_allow_html=True,
    )
    gallery_photos = [
        (
            "https://images.unsplash.com/photo-1547226238-e53e98a8e59d?w=700&q=70&auto=format&fit=crop",
            "Gym Sessions",
        ),
        (
            "https://images.unsplash.com/photo-1518644961665-ed172691aaa1?w=700&q=70&auto=format&fit=crop",
            "Wellness & Stretching",
        ),
        (
            "https://images.unsplash.com/photo-1577221084712-45b0445d2b00?w=700&q=70&auto=format&fit=crop",
            "Strength Training",
        ),
        (
            "https://images.unsplash.com/photo-1590333748338-d629e4564ad9?w=700&q=70&auto=format&fit=crop",
            "Cardio & Running",
        ),
    ]
    gallery_html = '<div class="fitpulse-photo-grid">' + "".join(
        f'<div class="fitpulse-photo-card"><img src="{url}" alt="{caption}">'
        f'<div class="fitpulse-photo-caption">{caption}</div></div>'
        for url, caption in gallery_photos
    ) + "</div>"
    st.markdown(gallery_html, unsafe_allow_html=True)

    # --- Bottom CTA banner ---
    st.markdown(
        """
        <div class="fitpulse-cta-banner">
            <h3>Ready to make a change? 🚀</h3>
            <p>FitPulse is free to use — tap the Gym Finder card to find one near you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("FitPulse — Sprint 2 Demo | Built with Python + Streamlit")


# ------------------------------------------------------------------
# SECTION 8A: GYM FINDER PAGE
# This is the page users land on after clicking the Gym Finder card
# on the home page — it's the ONLY place the locator tool lives now
# (previously there was a second copy of it sitting directly on the
# home page, which was redundant since the card already led here).
#
# It reuses the same FITNESS_CENTERS sample data and haversine
# distance math as before, but the results are presented in a more
# modern, "app-like" style: a gradient hero banner, a glassy toolbar
# for the search controls, sortable results, and card-style results
# with star ratings, amenity pills, and a "Closest" tag.
# ------------------------------------------------------------------
def render_gym_finder():
    if st.button("🏠 Back to Home", key="back_home_gym_finder"):
        st.session_state.page = "home"
        st.rerun()

    # --- Hero banner (gym-finder themed) ---
    st.markdown(
        """
        <div class="fitpulse-locator-hero">
            <h1>📍 Gym Finder</h1>
            <p>Search fitness centers near you, compare ratings and amenities,
            and sort results the way that matters most to you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Location search options ---
    st.markdown("**Choose your search location:**")
    
    search_method = st.radio(
        "Search by:",
        options=["Select from cities", "Type custom location"],
        horizontal=True,
        key="gym_search_method"
    )
    
    user_lat = None
    user_lon = None
    location_name = ""
    
    if search_method == "Select from cities":
        location_choice = st.selectbox(
            "📍 Select a city",
            options=list(SAMPLE_LOCATIONS.keys()),
            key="gym_location",
            help="Choose from available cities in NJ/NY area"
        )
        user_lat, user_lon = SAMPLE_LOCATIONS[location_choice]
        location_name = location_choice
    else:
        # Custom location search (accepts city names from SAMPLE_LOCATIONS)
        custom_location = st.text_input(
            "📍 Type a city name",
            placeholder="e.g., Union City, NJ or Hoboken, NJ",
            key="gym_custom_location"
        )
        
        if custom_location.strip():
            # Check if typed location matches any in our list
            matching_locations = [city for city in SAMPLE_LOCATIONS.keys() 
                                 if custom_location.strip().lower() in city.lower()]
            
            if matching_locations:
                user_lat, user_lon = SAMPLE_LOCATIONS[matching_locations[0]]
                location_name = matching_locations[0]
            else:
                st.warning(f"Location '{custom_location}' not found. Try: {', '.join(list(SAMPLE_LOCATIONS.keys())[:3])}")
    
    st.divider()
    
    # --- Glassy toolbar: radius and sort ---
    with st.container():
        st.markdown('<div class="fitpulse-locator-toolbar">', unsafe_allow_html=True)
        tool_col1, tool_col2 = st.columns([1, 1])
        with tool_col1:
            radius_miles = st.slider(
                "📏 Search radius (mi)",
                min_value=1,
                max_value=25,
                value=10,
                key="gym_radius",
            )
        with tool_col2:
            sort_choice = st.selectbox(
                "↕️ Sort by",
                options=["Distance", "Rating", "Name"],
                key="gym_sort",
            )

        search_clicked = st.button(
            "🔎 Find Nearby Gyms", use_container_width=True, type="primary", key="search_gyms"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Auto-search: trigger search if button clicked ---
    should_search = search_clicked and user_lat is not None and user_lon is not None

    # --- Search results ---
    if should_search:
        st.caption(f"📍 Searching from {location_name}: ({user_lat:.4f}, {user_lon:.4f})")

        nearby_gyms = []
        for gym in FITNESS_CENTERS:
            dist = distance_in_miles(user_lat, user_lon, gym["lat"], gym["lon"])
            if dist <= radius_miles:
                nearby_gyms.append((gym, dist))

        if sort_choice == "Distance":
            nearby_gyms.sort(key=lambda pair: pair[1])
        elif sort_choice == "Rating":
            nearby_gyms.sort(key=lambda pair: pair[0]["rating"], reverse=True)
        else:  # Name
            nearby_gyms.sort(key=lambda pair: pair[0]["name"])

        if nearby_gyms:
            st.success(f"✅ Found {len(nearby_gyms)} fitness center(s) near you!")

            closest_name = min(nearby_gyms, key=lambda pair: pair[1])[0]["name"]
            result_cols = st.columns(2)
            for index, (gym, dist) in enumerate(nearby_gyms):
                full_stars = int(round(gym["rating"]))
                stars = "★" * full_stars + "☆" * (5 - full_stars)
                pills_html = "".join(
                    f'<span class="fitpulse-pill">{tag}</span>' for tag in gym["amenities"]
                )
                closest_tag_html = (
                    '<div class="fitpulse-closest-tag">Closest</div>'
                    if gym["name"] == closest_name
                    else ""
                )

                # Built as ONE flat string with no leading whitespace on any
                # line. Streamlit's markdown renderer treats heavily-indented
                # lines (like the multi-line, deeply-nested version this
                # used to be) as a preformatted code block instead of parsing
                # them as HTML — which is why every card after the first one
                # was showing up as raw "<div class=...>" text instead of a
                # styled card. A flat string has no indentation to trip on.
                card_html = (
                    '<div class="fitpulse-gym-card">'
                    f'{closest_tag_html}'
                    '<div class="gym-top-row"><div>'
                    f'<h4>🏋️ {gym["name"]}</h4>'
                    f'<div class="gym-address">📍 {gym["address"]}</div>'
                    "</div>"
                    f'<span class="fitpulse-distance-badge">{dist:.1f} mi</span>'
                    "</div>"
                    f'<span class="fitpulse-rating-stars">{stars}</span>'
                    f'<span class="fitpulse-rating-number">{gym["rating"]}/5</span>'
                    f'<div class="fitpulse-pill-row">{pills_html}</div>'
                    "</div>"
                )

                with result_cols[index % 2]:
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.error(
                "❌ No fitness centers found in that radius. "
                "Try increasing your search radius or choosing a different location."
            )
    else:
        st.info("Set your location and radius above, then click **Find Nearby Gyms**.")


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
    
    # --- GUEST USER POPUP CHECK ---
    # If the user is a "Guest", show a card asking them to sign up or log in
    # before they can access the community messaging features.
    #
    # NOTE: the old version of this used a position:fixed full-screen
    # overlay for the "modal" look. That overlay floated on top of
    # everything else on the page, including the real Sign Up / Log In
    # buttons underneath it — so the buttons were basically unclickable.
    # This version keeps the same "popup card" idea, but builds it as a
    # normal in-page card (using the same real-button-styled-as-a-card
    # trick used elsewhere in this file), so the two buttons are always
    # visible and always clickable.
    if username == "Guest":
        st.markdown(
            """
            <style>
            .st-key-guest_gate_card {
                background-color: #F7F5EF;
                border: 1px solid #D9D4C7;
                border-radius: 16px;
                padding: 40px 40px 28px 40px;
                text-align: center;
                box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
            }
            .guest-gate-icon {
                font-size: 48px;
                margin-bottom: 10px;
            }
            .guest-gate-title {
                color: #2E2E2A;
                font-size: 26px;
                font-weight: 700;
                margin: 0 0 12px 0;
            }
            .guest-gate-text {
                color: #5A5A52;
                font-size: 15.5px;
                line-height: 1.6;
                margin: 0 auto 8px auto;
                max-width: 420px;
            }

            /* Sign Up button: earthy, muted green */
            .st-key-guest_signup_btn button {
                background-color: #7C9473 !important;
                border: 1px solid #7C9473 !important;
                color: white !important;
                font-weight: 700 !important;
            }
            .st-key-guest_signup_btn button:hover {
                background-color: #66805C !important;
                border-color: #66805C !important;
            }

            /* Log In button: earthy, warm gray */
            .st-key-guest_login_btn button {
                background-color: #8C887E !important;
                border: 1px solid #8C887E !important;
                color: white !important;
                font-weight: 700 !important;
            }
            .st-key-guest_login_btn button:hover {
                background-color: #75716A !important;
                border-color: #75716A !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        gate_col1, gate_col2, gate_col3 = st.columns([1, 2, 1])
        with gate_col2:
            with st.container(key="guest_gate_card"):
                st.markdown(
                    """
                    <div class="guest-gate-icon">👤</div>
                    <div class="guest-gate-title">Sign in to Chat</div>
                    <p class="guest-gate-text">
                        To communicate with other FitPulse members and speak
                        under your name, you'll need to create an account or
                        log in.
                    </p>
                    """,
                    unsafe_allow_html=True,
                )

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️ Sign Up", use_container_width=True, key="guest_signup_btn"):
                        st.session_state.page = "signup"
                        st.rerun()
                with btn_col2:
                    if st.button("🔑 Log In", use_container_width=True, key="guest_login_btn"):
                        st.session_state.page = "login"
                        st.rerun()

                st.markdown(
                    '<p style="margin-top: 20px; font-size: 13px; color: #8A8A80;">'
                    "<em>You can continue browsing as a guest, but messaging is limited.</em>"
                    "</p>",
                    unsafe_allow_html=True,
                )

        # Stop rendering the rest of the community features
        return

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
        
        # City-based location filtering using city physical centers
        city_filter_col1, city_filter_col2 = st.columns([2, 1])
        with city_filter_col1:
            selected_city = st.selectbox(
                "🗺️ Filter by city (location-based)",
                options=["All Cities"] + list(SAMPLE_LOCATIONS.keys()),
                key="discover_city_filter",
                help="Shows people searching from each city's physical center"
            )
        
        search_query = st.text_input(
            "Search by name", placeholder="Type a name to search...", key="discover_search"
        )
        
        # Display the selected city's physical center location
        if selected_city != "All Cities":
            city_lat, city_lon = SAMPLE_LOCATIONS[selected_city]
            st.caption(f"📍 Searching from {selected_city} center: ({city_lat:.4f}, {city_lon:.4f})")

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
                person_profile = get_user_profile(person)
                person_avatar = person_profile.get("avatar_emoji", "🏋️")
                person_fitness = person_profile.get("favorite_workout", "General Fitness")
                
                person_col, action_col = st.columns([3, 1])
                with person_col:
                    st.markdown(f"{person_avatar} **{person}** • {person_fitness}")
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
# SECTION 8B: FRIENDS LIST PAGE
# A dedicated page to view and manage all friends with search,
# cards, and remove functionality.
# ------------------------------------------------------------------
def render_friends_list():
    st.markdown(
        '<div class="fitpulse-section-header">👥 My Friends</div>',
        unsafe_allow_html=True,
    )
    st.write(f"Manage your FitPulse friends, **{username}**.")

    if st.button("🏠 Back to Home", key="back_home_friends"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # --- GUEST USER CHECK ---
    if username == "Guest":
        st.info(
            "👤 **Sign in to see your friends.** "
            "Create an account or log in to view and manage your friend list."
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Sign Up", use_container_width=True, key="guest_signup_friends"):
                st.session_state.page = "signup"
                st.rerun()
        with col2:
            if st.button("🔑 Log In", use_container_width=True, key="guest_login_friends"):
                st.session_state.page = "login"
                st.rerun()
        return

    friends = get_friends(username)

    # --- SEARCH BAR ---
    search_query = st.text_input(
        "🔍 Search friends by name",
        placeholder="Type a name...",
        key="friends_search",
    )

    # Filter friends based on search
    if search_query.strip():
        filtered_friends = [
            f for f in friends
            if search_query.strip().lower() in f.lower()
        ]
    else:
        filtered_friends = friends

    # --- EMPTY STATE ---
    if not friends:
        st.markdown(
            """
            <div class="fitpulse-empty-state">
                <div class="fitpulse-empty-state-icon">👥</div>
                <h3 style="color: #2A2A26; margin: 8px 0;">No Friends Yet</h3>
                <p>You haven't added any friends yet. Head to the <strong>Communities</strong> 
                section to discover and add friends!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🌐 Go to Communities", use_container_width=True, key="go_to_community_from_friends"):
            st.session_state.page = "community"
            st.rerun()
        return

    # --- SEARCH NO RESULTS ---
    if search_query.strip() and not filtered_friends:
        st.info(f"No friends found matching '{search_query}'. Try a different search.")
        return

    # --- FRIENDS CARDS ---
    st.markdown(f"**{len(filtered_friends)} Friend{'s' if len(filtered_friends) != 1 else ''}**")
    
    for friend in filtered_friends:
        friend_profile = get_user_profile(friend)
        friend_avatar = friend_profile.get("avatar_emoji", "🏋️")
        friend_fitness = friend_profile.get("fitness_level", "Beginner")
        
        col_avatar, col_info, col_action = st.columns([0.5, 2.5, 1])

        with col_avatar:
            st.markdown(
                f"""
                <div class="fitpulse-friend-avatar" style="text-align: center;">
                    {friend_avatar}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_info:
            st.markdown(
                f"""
                <div class="fitpulse-friend-name-text">{friend}</div>
                <div style="font-size: 13px; color: #8A8A80;">📊 {friend_fitness} • FitPulse Member</div>
                """,
                unsafe_allow_html=True,
            )

        with col_action:
            if st.button(
                "❌ Remove",
                key=f"remove_friend_{friend}",
                use_container_width=True,
                help=f"Remove {friend} from your friends list",
            ):
                remove_friend(username, friend)
                st.success(f"Removed {friend} from your friends list.")
                st.rerun()

    st.divider()
    
    # Navigation back to Communities
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Go to Communities", use_container_width=True, key="back_to_community"):
            st.session_state.page = "community"
            st.rerun()
    with col2:
        if st.button("👤 View Profile", use_container_width=True, key="view_profile_friends"):
            st.info(f"**{username}'s Profile**\n\nFriends: {len(friends)}\n\nYour FitPulse account is all set!")


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
# SECTION 9AA: WORKOUT GOAL CALENDAR PAGE
# A dedicated page where users set workout goals tied to a specific
# date, see them laid out on a real month calendar alongside the
# days they actually completed a workout (any logged habit), and
# mark goals complete as they hit them.
# ------------------------------------------------------------------
def render_goal_calendar():
    st.markdown(
        '<div class="fitpulse-section-header">🗓️ Workout Goal Calendar</div>',
        unsafe_allow_html=True,
    )
    st.write(f"Set workout goals and track your completed workouts, **{username}**.")

    if st.button("🏠 Back to Home", key="back_home_goal_calendar"):
        st.session_state.page = "home"
        st.rerun()

    user_data = get_user_data(username)
    habits = user_data["habits"]
    goals = user_data["goals"]
    workout_days = get_completed_workout_days(user_data)
    total_completed = count_completed_workouts(user_data)
    completed_goals = sum(1 for g in goals if g["completed"])

    st.divider()

    # --- Quick stats ---
    stat_cols = st.columns(3)
    stat_cols[0].metric("✅ Completed workouts", total_completed)
    stat_cols[1].metric("🎯 Goals set", len(goals))
    stat_cols[2].metric("🏆 Goals completed", f"{completed_goals}/{len(goals)}" if goals else "0/0")

    st.write("")

    # --- Add a new goal ---
    with st.expander("➕ Add a Workout Goal", expanded=(len(goals) == 0)):
        with st.form("add_goal_form", clear_on_submit=True):
            goal_title = st.text_input(
                "Goal", placeholder="e.g., Run 5 miles without stopping"
            )
            goal_col1, goal_col2, goal_col3 = st.columns(3)
            with goal_col1:
                goal_date = st.date_input(
                    "Target date", value=date.today() + timedelta(days=7)
                )
            with goal_col2:
                linked_habit = st.selectbox(
                    "Link to a habit (optional)",
                    ["None"] + list(habits.keys()),
                )
            with goal_col3:
                target_value = st.number_input(
                    "Target distance (mi, optional)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                )

            goal_submitted = st.form_submit_button("Add Goal to Calendar")
            if goal_submitted:
                clean_title = goal_title.strip()
                if not clean_title:
                    st.warning("Please describe your goal.")
                else:
                    add_goal(
                        user_data,
                        title=clean_title,
                        target_date_str=goal_date.strftime("%Y-%m-%d"),
                        habit_name="" if linked_habit == "None" else linked_habit,
                        target_value=target_value if target_value > 0 else None,
                    )
                    save_user_data(username, user_data)
                    st.success(f"Goal '{clean_title}' added to your calendar!")
                    st.rerun()

    st.divider()

    # --- Month navigation ---
    if "goal_calendar_month" not in st.session_state:
        today = date.today()
        st.session_state.goal_calendar_month = date(today.year, today.month, 1)

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("◀ Previous", key="cal_prev_month", use_container_width=True):
            first_of_month = st.session_state.goal_calendar_month
            prev_last_day = first_of_month - timedelta(days=1)
            st.session_state.goal_calendar_month = date(
                prev_last_day.year, prev_last_day.month, 1
            )
            st.rerun()
    with nav_col2:
        st.markdown(
            f"<h3 style='text-align:center;'>{st.session_state.goal_calendar_month.strftime('%B %Y')}</h3>",
            unsafe_allow_html=True,
        )
    with nav_col3:
        if st.button("Next ▶", key="cal_next_month", use_container_width=True):
            first_of_month = st.session_state.goal_calendar_month
            days_in_month = calendar.monthrange(first_of_month.year, first_of_month.month)[1]
            next_first_day = first_of_month + timedelta(days=days_in_month)
            st.session_state.goal_calendar_month = date(
                next_first_day.year, next_first_day.month, 1
            )
            st.rerun()

    # --- Build the calendar grid (Mon-Sun) ---
    cal_month = st.session_state.goal_calendar_month
    month_weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(
        cal_month.year, cal_month.month
    )
    today_str = date.today().strftime("%Y-%m-%d")

    day_labels = "".join(
        f'<div class="fitpulse-cal-daylabel">{d}</div>'
        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    cell_html = ""
    for week in month_weeks:
        for day_obj in week:
            if day_obj.month != cal_month.month:
                cell_html += '<div class="fitpulse-cal-cell empty"></div>'
                continue
            day_str = day_obj.strftime("%Y-%m-%d")
            day_goals = goals_on_date(goals, day_str)
            classes = ["fitpulse-cal-cell"]
            if day_str in workout_days:
                classes.append("workout-day")
            if day_goals:
                classes.append("goal-day")
            if day_str == today_str:
                classes.append("today")

            tags = ""
            if day_str in workout_days:
                tags += '<span class="fitpulse-cal-tag">✅ Workout</span>'
            for g in day_goals:
                mark = "☑️" if g["completed"] else "🎯"
                short_title = g["title"] if len(g["title"]) <= 16 else g["title"][:14] + "…"
                tags += f'<span class="fitpulse-cal-tag">{mark} {short_title}</span>'

            cell_html += (
                f'<div class="{" ".join(classes)}">'
                f'<div class="fitpulse-cal-daynum">{day_obj.day}</div>'
                f'{tags}</div>'
            )

    st.markdown(
        f'<div class="fitpulse-cal-grid">{day_labels}{cell_html}</div>',
        unsafe_allow_html=True,
    )
    st.caption("🟢 Green = a completed workout was logged that day &nbsp;•&nbsp; 🟡 Gold outline = a goal is due that day")

    st.divider()

    # --- Goals list: mark complete, or delete ---
    st.markdown("### 🎯 Your Goals")
    if not goals:
        st.info("You haven't set any workout goals yet — add one above to see it on the calendar.")
    else:
        for goal in sorted(goals, key=lambda g: g["target_date"]):
            card_class = "fitpulse-goal-card completed" if goal["completed"] else "fitpulse-goal-card"
            details = f"🗓️ {goal['target_date']}"
            if goal["habit_name"]:
                details += f" &nbsp;•&nbsp; linked to **{goal['habit_name']}**"
            if goal["target_value"]:
                details += f" &nbsp;•&nbsp; target **{goal['target_value']} mi**"

            g_col1, g_col2, g_col3 = st.columns([4, 1, 1])
            with g_col1:
                st.markdown(
                    f'<div class="{card_class}">'
                    f'<strong>{"✅ " if goal["completed"] else ""}{goal["title"]}</strong><br>'
                    f'<span style="color:#5A5A52; font-size:13px;">{details}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with g_col2:
                toggle_label = "↩️ Undo" if goal["completed"] else "✅ Complete"
                if st.button(toggle_label, key=f"toggle_goal_{goal['id']}", use_container_width=True):
                    set_goal_completed(user_data, goal["id"], not goal["completed"])
                    save_user_data(username, user_data)
                    st.rerun()
            with g_col3:
                if st.button("🗑️ Delete", key=f"delete_goal_{goal['id']}", use_container_width=True):
                    delete_goal(user_data, goal["id"])
                    save_user_data(username, user_data)
                    st.rerun()


# ------------------------------------------------------------------
# SECTION 9A: SHARED AUTH PAGE STYLE (Sign Up + Log In)
# Both pages use the same "split card" look from the reference design:
# a plain white form panel on one side, and a colored info panel with
# a "Welcome" message on the other. Instead of orange, this version
# uses a neutral, earthy green so it fits FitPulse's outdoorsy/fitness
# feel without shouting for attention. Each panel is a real
# st.container(key=...), styled via the same "real element, styled
# with CSS" trick used for the feature cards earlier in this file.
# ------------------------------------------------------------------
def render_auth_style():
    st.markdown(
        """
        <style>
        /* Remove the gap between the two columns and wrap them in one
           rounded, shadowed card so the two halves look like a single
           connected panel instead of two separate boxes. */
        .st-key-auth_card_outer [data-testid="stHorizontalBlock"] {
            gap: 0rem !important;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.10);
            border: 1px solid #D9D4C7;
        }
        .st-key-auth_form_panel {
            background-color: #FFFFFF;
            padding: 44px 40px;
            min-height: 480px;
        }
        .st-key-auth_info_panel {
            background: linear-gradient(150deg, #93AC86 0%, #55704C 100%);
            padding: 44px 40px;
            min-height: 480px;
            display: flex;
            align-items: center;
        }
        .auth-info-inner h2 {
            color: white;
            font-size: 30px;
            font-weight: 800;
            margin: 0 0 14px 0;
        }
        .auth-info-inner p {
            color: white;
            font-size: 15px;
            line-height: 1.7;
            opacity: 0.95;
            margin: 0;
        }
        .auth-form-title {
            font-size: 26px;
            font-weight: 800;
            color: #2E2E2A;
            margin: 0 0 22px 0;
        }

        /* Sign Up submit button: earthy, muted green */
        .st-key-signup_submit_btn button {
            background-color: #7C9473 !important;
            border-color: #7C9473 !important;
            color: white !important;
            font-weight: 700 !important;
        }
        .st-key-signup_submit_btn button:hover {
            background-color: #66805C !important;
            border-color: #66805C !important;
        }

        /* Log In submit button: earthy, warm gray */
        .st-key-login_submit_btn button {
            background-color: #8C887E !important;
            border-color: #8C887E !important;
            color: white !important;
            font-weight: 700 !important;
        }
        .st-key-login_submit_btn button:hover {
            background-color: #75716A !important;
            border-color: #75716A !important;
        }

        /* The small "switch to the other page" buttons underneath
           each form, styled to look like plain text links. */
        .st-key-goto_login_btn button,
        .st-key-goto_signup_btn button {
            background: none !important;
            border: none !important;
            color: #55704C !important;
            font-weight: 700 !important;
            text-decoration: underline;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# SECTION 9B: SIGNUP PAGE
# This page appears when a guest user clicks "Sign Up" from the
# community popup. They enter their name, email, phone number, and
# a password.
# ------------------------------------------------------------------
def render_signup():
    st.markdown(
        '<div class="fitpulse-section-header">📝 Create Your Account</div>',
        unsafe_allow_html=True,
    )

    if st.button("🏠 Back to Home", key="back_home_signup"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    render_auth_style()

    outer_left, outer_mid, outer_right = st.columns([1, 5, 1])
    with outer_mid:
        with st.container(key="auth_card_outer"):
            form_col, info_col = st.columns([3, 2])

            with form_col:
                with st.container(key="auth_form_panel"):
                    st.markdown(
                        '<div class="auth-form-title">Sign Up</div>',
                        unsafe_allow_html=True,
                    )

                    with st.form("signup_form", clear_on_submit=True):
                        full_name = st.text_input("Name", placeholder="e.g., John Doe")
                        email = st.text_input("E-mail", placeholder="e.g., john@example.com")
                        phone = st.text_input("Phone Number", placeholder="e.g., (555) 123-4567")
                        
                        # Profile attributes
                        st.markdown("<hr>", unsafe_allow_html=True)
                        st.caption("**Complete your fitness profile** (you can update this later)")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            fitness_level = st.selectbox(
                                "Fitness Level",
                                FITNESS_LEVELS,
                                key="signup_fitness",
                            )
                        with col2:
                            favorite_workout = st.selectbox(
                                "Favorite Workout",
                                WORKOUT_TYPES,
                                key="signup_workout",
                            )
                        
                        avatar_emoji = st.selectbox(
                            "Choose Your Avatar",
                            AVATAR_EMOJIS,
                            key="signup_avatar",
                        )
                        
                        bio = st.text_area(
                            "Bio (optional)",
                            placeholder="Tell us about your fitness goals!",
                            max_chars=150,
                            height=60,
                            key="signup_bio",
                        )
                        
                        st.markdown("<hr>", unsafe_allow_html=True)
                        password = st.text_input("Password", type="password")
                        confirm_password = st.text_input("Confirm Password", type="password")

                        submitted = st.form_submit_button(
                            "Create Account",
                            use_container_width=True,
                            key="signup_submit_btn",
                        )

                        if submitted:
                            if not full_name.strip():
                                st.error("❌ Please enter your name.")
                            elif not email.strip() or "@" not in email:
                                st.error("❌ Please enter a valid email address.")
                            elif not password:
                                st.error("❌ Please choose a password.")
                            elif password != confirm_password:
                                st.error("❌ Passwords don't match.")
                            else:
                                # Create account and save profile
                                username = full_name.strip()
                                profile_data = {
                                    "full_name": full_name.strip(),
                                    "email": email.strip(),
                                    "fitness_level": fitness_level,
                                    "favorite_workout": favorite_workout,
                                    "avatar_emoji": avatar_emoji,
                                    "bio": bio.strip() or "FitPulse Member",
                                    "created_at": date.today().strftime("%Y-%m-%d"),
                                }
                                save_user_profile(username, profile_data)
                                
                                st.success("✅ Account created successfully!")
                                st.info(
                                    f"Welcome to FitPulse, **{full_name}**! 🎉\n\n"
                                    "*Redirecting you back to the app...*"
                                )
                                login_user(username)
                                st.session_state.page = "home"
                                import time
                                time.sleep(2)
                                st.rerun()

                    st.markdown(
                        '<p style="text-align:center; font-size:13.5px; color:#767268; '
                        'margin: 10px 0 4px 0;">Already have an account?</p>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Log In Instead", key="goto_login_btn", use_container_width=True):
                        st.session_state.page = "login"
                        st.rerun()

            with info_col:
                with st.container(key="auth_info_panel"):
                    st.markdown(
                        """
                        <div class="auth-info-inner">
                            <h2>Welcome!</h2>
                            <p>
                                Join FitPulse to track your fitness habits,
                                find gyms nearby, and connect with friends
                                who are working toward the same goals.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ------------------------------------------------------------------
# SECTION 9C: LOGIN PAGE
# This page appears when a guest user clicks "Log In" from the
# community popup, or from the "Log In Instead" link on the signup
# page. This is a beginner demo project with no real account
# database, so logging in simply takes you back to the app.
# ------------------------------------------------------------------
def render_login():
    st.markdown(
        '<div class="fitpulse-section-header">🔑 Log In</div>',
        unsafe_allow_html=True,
    )

    if st.button("🏠 Back to Home", key="back_home_login"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    render_auth_style()

    outer_left, outer_mid, outer_right = st.columns([1, 5, 1])
    with outer_mid:
        with st.container(key="auth_card_outer"):
            info_col, form_col = st.columns([2, 3])

            with info_col:
                with st.container(key="auth_info_panel"):
                    st.markdown(
                        """
                        <div class="auth-info-inner">
                            <h2>Welcome Back!</h2>
                            <p>
                                Log in to pick up where you left off — your
                                habits, gym searches, and friends are all
                                waiting for you.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with form_col:
                with st.container(key="auth_form_panel"):
                    st.markdown(
                        '<div class="auth-form-title">Log In</div>',
                        unsafe_allow_html=True,
                    )

                    with st.form("login_form", clear_on_submit=False):
                        phone_or_email = st.text_input(
                            "Phone Number or E-mail",
                            placeholder="e.g., (555) 123-4567 or john@example.com",
                        )
                        password = st.text_input("Password", type="password")

                        submitted = st.form_submit_button(
                            "Log In",
                            use_container_width=True,
                            key="login_submit_btn",
                        )

                        if submitted:
                            if not phone_or_email.strip():
                                st.error("❌ Please enter your phone number or email.")
                            elif not password:
                                st.error("❌ Please enter your password.")
                            else:
                                # Look up which saved account this email
                                # belongs to, so logging in actually signs
                                # you back into YOUR account (not just
                                # whichever guest name happened to be set).
                                entered = phone_or_email.strip().lower()
                                all_profiles = load_all_profiles()
                                matched_username = None
                                for existing_name, profile in all_profiles.items():
                                    if profile.get("email", "").strip().lower() == entered:
                                        matched_username = existing_name
                                        break

                                if matched_username is None:
                                    st.error(
                                        "❌ We couldn't find an account with that "
                                        "email. Check the spelling, or sign up "
                                        "below if you're new here."
                                    )
                                else:
                                    st.success("✅ Logged in! Redirecting you back to the app...")
                                    login_user(matched_username)
                                    st.session_state.page = "home"
                                    import time
                                    time.sleep(1)
                                    st.rerun()

                    st.markdown(
                        '<p style="text-align:center; font-size:13.5px; color:#767268; '
                        'margin: 10px 0 4px 0;">Don\'t have an account?</p>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Sign Up Instead", key="goto_signup_btn", use_container_width=True):
                        st.session_state.page = "signup"
                        st.rerun()


# ------------------------------------------------------------------
# SECTION 9D: PROFILE PAGE
# Display and edit user profile information including fitness level,
# favorite workout type, avatar, and bio.
# ------------------------------------------------------------------
def render_profile():
    st.markdown(
        '<div class="fitpulse-section-header">👤 My Profile</div>',
        unsafe_allow_html=True,
    )
    st.write(f"View and manage your FitPulse profile, **{username}**.")

    if st.button("🏠 Back to Home", key="back_home_profile"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # Load user profile
    profile = get_user_profile(username)

    # --- PROFILE VIEW MODE (DEFAULT) ---
    if "edit_profile_mode" not in st.session_state:
        st.session_state.edit_profile_mode = False

    if not st.session_state.edit_profile_mode:
        # Display profile card
        st.markdown(
            f"""
            <div class="fitpulse-profile-card">
                <div class="fitpulse-profile-header">
                    <div class="fitpulse-profile-avatar-large">{profile.get('avatar_emoji', '🏋️')}</div>
                    <div class="fitpulse-profile-name-section">
                        <h2>{profile.get('full_name', username)}</h2>
                        <p>📧 {profile.get('email', 'No email')}</p>
                        <p>💬 "{profile.get('bio', 'FitPulse Member')}"</p>
                        <p style="color: #7C9473; font-weight: 600;">Member since {profile.get('created_at', 'Recently')}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Profile attributes grid
        st.markdown("### 🎯 Fitness Profile")
        attr_col1, attr_col2, attr_col3 = st.columns(3)

        with attr_col1:
            st.markdown(
                f"""
                <div class="fitpulse-profile-attr-item">
                    <div class="fitpulse-profile-attr-label">Fitness Level</div>
                    <div class="fitpulse-profile-attr-value">{profile.get('fitness_level', 'Beginner')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with attr_col2:
            st.markdown(
                f"""
                <div class="fitpulse-profile-attr-item">
                    <div class="fitpulse-profile-attr-label">Favorite Workout</div>
                    <div class="fitpulse-profile-attr-value">{profile.get('favorite_workout', 'General Fitness')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with attr_col3:
            st.markdown(
                f"""
                <div class="fitpulse-profile-attr-item">
                    <div class="fitpulse-profile-attr-label">Avatar</div>
                    <div class="fitpulse-profile-attr-value">{profile.get('avatar_emoji', '🏋️')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Edit button
        if st.button("✏️ Edit Profile", use_container_width=True, key="edit_profile_btn"):
            st.session_state.edit_profile_mode = True
            st.rerun()

    else:
        # --- EDIT PROFILE MODE ---
        st.markdown("### ✏️ Edit Your Profile")

        with st.form("edit_profile_form"):
            new_full_name = st.text_input(
                "Full Name",
                value=profile.get("full_name", username),
                key="edit_full_name",
            )
            new_email = st.text_input(
                "Email",
                value=profile.get("email", ""),
                key="edit_email",
            )
            new_bio = st.text_area(
                "Bio",
                value=profile.get("bio", ""),
                max_chars=150,
                height=80,
                key="edit_bio",
            )

            col1, col2 = st.columns(2)
            with col1:
                new_fitness_level = st.selectbox(
                    "Fitness Level",
                    FITNESS_LEVELS,
                    index=FITNESS_LEVELS.index(profile.get("fitness_level", "Beginner")),
                    key="edit_fitness",
                )

            with col2:
                new_favorite_workout = st.selectbox(
                    "Favorite Workout",
                    WORKOUT_TYPES,
                    index=WORKOUT_TYPES.index(profile.get("favorite_workout", "General Fitness")),
                    key="edit_workout",
                )

            new_avatar_emoji = st.selectbox(
                "Avatar Emoji",
                AVATAR_EMOJIS,
                index=AVATAR_EMOJIS.index(profile.get("avatar_emoji", "🏋️")),
                key="edit_avatar",
            )

            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    # Update profile
                    profile["full_name"] = new_full_name.strip() or username
                    profile["email"] = new_email.strip()
                    profile["fitness_level"] = new_fitness_level
                    profile["favorite_workout"] = new_favorite_workout
                    profile["avatar_emoji"] = new_avatar_emoji
                    profile["bio"] = new_bio.strip() or "FitPulse Member"

                    save_user_profile(username, profile)
                    st.success("✅ Profile updated successfully!")
                    st.session_state.edit_profile_mode = False
                    import time
                    time.sleep(1)
                    st.rerun()

            with col_cancel:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_profile_mode = False
                    st.rerun()


# ------------------------------------------------------------------
# SECTION 10: ROUTER — draw whichever page we're on
# ------------------------------------------------------------------
if st.session_state.page == "habits":
    render_habit_tracker()
elif st.session_state.page == "community":
    render_community()
elif st.session_state.page == "friends_list":
    render_friends_list()
elif st.session_state.page == "goal_calendar":
    render_goal_calendar()
elif st.session_state.page == "gym_finder":
    render_gym_finder()
elif st.session_state.page == "profile":
    render_profile()
elif st.session_state.page == "signup":
    render_signup()
elif st.session_state.page == "login":
    render_login()
else:
    render_home()
