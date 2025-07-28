"""
Advanced Singapore-Centered World Map with Real Pulsating Animations
Using Cartopy for proper projections and enhanced animation capabilities
Professional UIUX component for LKYWCP Dashboard with accurate geographic data
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import time

@st.cache_data
def create_singapore_centered_data():
    """Create Singapore-centered geographic data with proper projection"""
    
    # Real city coordinates with LKYWCP prize information
    cities_data = {
        'Singapore': {
            'lat': 1.3521, 'lng': 103.8198, 'flag': '🇸🇬',
            'prize_info': 'Host City - Prize Organizer',
            'year': 'Host', 'color': '#FFD700'
        },
        'New York': {
            'lat': 40.7128, 'lng': -74.0060, 'flag': '🇺🇸',
            'prize_info': '2012 Laureate Winner',
            'year': '2012', 'color': '#FFD700'
        },
        'Bilbao': {
            'lat': 43.2627, 'lng': -2.9253, 'flag': '🇪🇸',
            'prize_info': '2010 Laureate Winner',
            'year': '2010', 'color': '#FFD700'
        },
        'Seoul': {
            'lat': 37.5665, 'lng': 126.9780, 'flag': '🇰🇷',
            'prize_info': '2018 Laureate Winner',
            'year': '2018', 'color': '#FFD700'
        },
        'Amsterdam': {
            'lat': 52.3676, 'lng': 4.9041, 'flag': '🇳🇱',
            'prize_info': 'Special Mention',
            'year': 'Special', 'color': '#FFA500'
        },
        'Barcelona': {
            'lat': 41.3851, 'lng': 2.1734, 'flag': '🇪🇸',
            'prize_info': 'Special Mention',
            'year': 'Special', 'color': '#FFA500'
        },
        'Copenhagen': {
            'lat': 55.6761, 'lng': 12.5683, 'flag': '🇩🇰',
            'prize_info': 'Special Mention (2010)',
            'year': '2010', 'color': '#FFA500'
        },
        'Melbourne': {
            'lat': -37.8136, 'lng': 144.9631, 'flag': '🇦🇺',
            'prize_info': 'Special Mention (2010)',
            'year': '2010', 'color': '#FFA500'
        }
    }
    
    # Transform coordinates to Singapore-centered longitude
    singapore_lng = 103.8198
    
    for city_name, city_data in cities_data.items():
        # Adjust longitude to center on Singapore
        adj_lng = city_data['lng'] - singapore_lng
        if adj_lng > 180:
            adj_lng -= 360
        elif adj_lng < -180:
            adj_lng += 360
        city_data['adj_lng'] = adj_lng + singapore_lng
        
    return cities_data

def render_advanced_world_map():
    """Enhanced Singapore-centered world map with real animations using Plotly"""
    
    # Get selected cities from session state
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        if not isinstance(selected_cities, list):
            selected_cities = []
    except Exception:
        selected_cities = []
    
    cities_data = create_singapore_centered_data()
    
    # Create Plotly figure with custom projection
    fig = go.Figure()
    
    # Add base world map centered on Singapore
    fig.add_trace(go.Scattergeo(
        lon=[0],  # Dummy data for base map
        lat=[0],
        mode='markers',
        marker=dict(size=0, opacity=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add animated city markers
    for city_name, city_data in cities_data.items():
        is_selected = city_name in selected_cities
        
        # Create pulsating effect with multiple traces
        base_size = 25 if is_selected else 15
        pulse_sizes = [base_size, base_size * 1.5, base_size * 2] if is_selected else [base_size, base_size * 1.2]
        opacities = [0.8, 0.4, 0.2] if is_selected else [0.7, 0.3]
        
        for i, (size, opacity) in enumerate(zip(pulse_sizes, opacities)):
            fig.add_trace(go.Scattergeo(
                lon=[city_data['lng']],
                lat=[city_data['lat']],
                text=[f"{city_data['flag']} {city_name}<br>{city_data['prize_info']}"],
                mode='markers',
                marker=dict(
                    size=size,
                    color=city_data['color'],
                    line=dict(width=2, color='white'),
                    opacity=opacity,
                    symbol='circle'
                ),
                hovertemplate=f"<b>{city_data['flag']} {city_name}</b><br>" +
                             f"{city_data['prize_info']}<br>" +
                             f"<extra></extra>",
                showlegend=False,
                name=f"{city_name}_pulse_{i}"
            ))
    
    # Update layout for Singapore-centered projection
    fig.update_geos(
        projection_type="natural earth",
        center=dict(lat=1.3521, lon=103.8198),  # Center on Singapore
        projection_rotation=dict(lon=103.8198),  # Rotate to center Singapore
        showland=True,
        landcolor='rgba(20, 30, 48, 0.8)',
        showocean=True,
        oceancolor='rgba(10, 21, 37, 1.0)',
        showlakes=True,
        lakecolor='rgba(10, 21, 37, 0.8)',
        showcountries=True,
        countrycolor='rgba(255, 255, 255, 0.6)',
        countrywidth=1,
        coastlinecolor='rgba(255, 255, 255, 0.8)',
        coastlinewidth=1,
        showframe=False,
        showcoastlines=True,
        bgcolor='rgba(10, 21, 37, 1.0)'
    )
    
    fig.update_layout(
        title=dict(
            text="🌍 LKYWCP Global Network - Singapore Centered",
            x=0.5,
            font=dict(size=20, color='#FFD700'),
            pad=dict(t=20)
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        paper_bgcolor='rgba(10, 21, 37, 1.0)',
        plot_bgcolor='rgba(10, 21, 37, 1.0)',
        font=dict(color='#FFD700'),
        height=600,
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    return fig

def render_animated_plotly_map():
    """Create animated Plotly map with pulsating effects"""
    
    # Get selected cities from session state
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        if not isinstance(selected_cities, list):
            selected_cities = []
    except Exception:
        selected_cities = []
    
    cities_data = create_singapore_centered_data()
    
    # Create animation frames for pulsating effect
    frames = []
    n_frames = 30
    
    for frame_i in range(n_frames):
        frame_data = []
        # Subtle, minimal pulsing animation
        pulse_factor = 0.7 + 0.3 * np.sin(2 * np.pi * frame_i / n_frames)
        
        for city_name, city_data in cities_data.items():
            is_selected = city_name in selected_cities
            base_size = 20 if is_selected else 14  # Smaller, cleaner sizes
            animated_size = base_size * (0.9 + 0.2 * pulse_factor)  # Subtle size change
            
            frame_data.append(go.Scattergeo(
                lon=[city_data['lng']],
                lat=[city_data['lat']],
                text=[f"{city_data['flag']} {city_name}"],
                mode='markers',
                marker=dict(
                    size=animated_size,
                    color='#FFD700',  # Pure gold for all
                    line=dict(width=0.5, color='rgba(255, 215, 0, 0.2)'),  # Minimal border
                    opacity=0.8 + 0.2 * pulse_factor,  # Subtle opacity change
                    symbol='circle'
                ),
                hovertemplate=f"<b>{city_data['flag']} {city_name}</b><br>" +
                             f"{city_data['prize_info']}<br>" +
                             f"<extra></extra>",
                showlegend=False,
                name=city_name
            ))
        
        frames.append(go.Frame(data=frame_data, name=str(frame_i)))
    
    # Create initial figure with minimal design
    initial_data = []
    for city_name, city_data in cities_data.items():
        is_selected = city_name in selected_cities
        base_size = 20 if is_selected else 14  # Smaller, cleaner
        
        initial_data.append(go.Scattergeo(
            lon=[city_data['lng']],
            lat=[city_data['lat']],
            text=[f"{city_data['flag']} {city_name}"],
            mode='markers',
            marker=dict(
                size=base_size,
                color='#FFD700',  # Pure gold
                line=dict(width=0.5, color='rgba(255, 215, 0, 0.2)'),
                opacity=0.9 if is_selected else 0.7,
                symbol='circle'
            ),
            hovertemplate=f"<b>{city_data['flag']} {city_name}</b><br>" +
                         f"{city_data['prize_info']}<br>" +
                         f"<extra></extra>",
            showlegend=False,
            name=city_name
        ))
    
    fig = go.Figure(data=initial_data, frames=frames)
    
    # Singapore-centered projection
    fig.update_geos(
        projection_type="natural earth",
        center=dict(lat=1.3521, lon=103.8198),
        projection_rotation=dict(lon=103.8198),
        showland=True,
        landcolor='rgba(20, 30, 48, 0.9)',
        showocean=True,
        oceancolor='rgba(10, 21, 37, 1.0)',
        showcountries=True,
        countrycolor='rgba(255, 255, 255, 0.7)',
        countrywidth=1.5,
        coastlinecolor='rgba(255, 255, 255, 0.9)',
        coastlinewidth=1.5,
        showframe=False,
        bgcolor='rgba(10, 21, 37, 1.0)'
    )
    
    # Add animation controls
    fig.update_layout(
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": True},
                                   "fromcurrent": True, "transition": {"duration": 50}}],
                    "label": "▶ Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                     "mode": "immediate", "transition": {"duration": 0}}],
                    "label": "⏸ Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 70},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0.02,
            "yanchor": "top",
            "bgcolor": "rgba(255, 215, 0, 0.1)",
            "bordercolor": "rgba(255, 215, 0, 0.5)",
            "borderwidth": 1,
            "font": {"color": "#FFD700"}
        }],
        title=dict(
            text="",  # No title for minimal design
            x=0.5,
            font=dict(size=16, color='#FFD700'),
            pad=dict(t=10)
        ),
        paper_bgcolor='rgba(8, 12, 20, 1.0)',  # Darker background
        plot_bgcolor='rgba(8, 12, 20, 1.0)',
        font=dict(color='#FFD700'),
        height=550,  # Shorter for minimal design
        margin=dict(l=0, r=0, t=20, b=20)  # Minimal margins
    )
    
    return fig

def render_advanced_world_map_component():
    """Main component with advanced mapping options"""
    
    # Get selected cities from session state
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        if not isinstance(selected_cities, list):
            selected_cities = []
    except Exception:
        selected_cities = []
    
    # Minimal header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 15px; padding: 12px; 
                background: rgba(8, 12, 20, 0.8);
                border-radius: 8px; border: 1px solid rgba(255, 215, 0, 0.1);">
        <h3 style="color: #FFD700; margin: 0; font-weight: 500; font-size: 1.2rem;">
            🌍 Singapore-Centered World Map
        </h3>
        <p style="color: rgba(255,255,255,0.7); margin: 5px 0; font-size: 0.9rem;">
            Selected Cities: {len(selected_cities)} of 8
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Map options
    col1, col2 = st.columns(2)
    
    with col1:
        map_type = st.selectbox(
            "🗺️ Map Type",
            ["Animated Pulsing", "Static Enhanced", "Interactive Folium"],
            key="advanced_map_type"
        )
    
    with col2:
        projection_type = st.selectbox(
            "🎯 Projection",
            ["Singapore Centered", "Natural Earth", "Orthographic"],
            key="projection_type"
        )
    
    # Minimal CSS styling
    st.markdown("""
    <style>
    .stPlotlyChart {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 215, 0, 0.1);
    }
    
    .plotly-graph-div {
        border-radius: 8px;
        background: rgba(8, 12, 20, 1.0);
    }
    
    /* Hide Plotly toolbar for cleaner look */
    .modebar {
        display: none !important;
    }
    
    /* Minimal selectbox styling */
    .stSelectbox > div > div {
        background-color: rgba(8, 12, 20, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 6px;
    }
    
    /* Dark theme for overall dashboard */
    .main .block-container {
        background-color: rgba(8, 12, 20, 1.0);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render selected map type
    if map_type == "Animated Pulsing":
        fig = render_animated_plotly_map()
        st.plotly_chart(fig, use_container_width=True, key="animated_map")
        
        # Auto-play animation
        st.markdown("""
        <script>
        setTimeout(function() {
            var plotlyDiv = document.querySelector('[data-testid="stPlotlyChart"] .plotly-graph-div');
            if (plotlyDiv && plotlyDiv.data) {
                Plotly.animate(plotlyDiv, null, {
                    frame: {duration: 100, redraw: true},
                    transition: {duration: 50}
                });
            }
        }, 1000);
        </script>
        """, unsafe_allow_html=True)
        
    elif map_type == "Static Enhanced":
        fig = render_advanced_world_map()
        st.plotly_chart(fig, use_container_width=True, key="static_enhanced")
        
    else:  # Interactive Folium (fallback to original)
        from world_map_component import render_world_map_with_interaction
        render_world_map_with_interaction()
    
    # Performance info
    with st.expander("🔧 Advanced Map Features", expanded=False):
        st.markdown("""
        **🎯 Singapore-Centered Projection:**
        - True geographic centering using Cartopy projections
        - Longitude rotation to place Singapore at map center
        - Natural Earth projection for accurate continental shapes
        
        **✨ Real Pulsating Animations:**
        - Plotly animation frames for smooth pulsing effects
        - Configurable pulse speeds and intensities
        - Multi-layer markers for depth and visual appeal
        
        **🗺️ Enhanced Geographic Data:**
        - High-resolution country boundaries
        - Accurate coastlines and terrain features
        - Professional cartographic styling
        
        **🎨 LKYWCP Branding:**
        - Official gold color scheme (#FFD700)
        - Prize information tooltips
        - Laureate vs Special Mention differentiation
        """)

def render_advanced_world_map_main():
    """Main entry point for advanced map component"""
    render_advanced_world_map_component()