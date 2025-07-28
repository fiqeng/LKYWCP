"""
Integrated Singapore-Centered World Map with Radial Gradient Animations
Clean, seamless integration into LKYWCP Dashboard
Auto-playing radial gradients emanating from cities
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
import time

@st.cache_data
def create_radial_animation_data():
    """Create data for radial gradient animations from city centers"""
    
    # City coordinates with LKYWCP information
    cities = {
        'Singapore': {
            'lat': 1.3521, 'lng': 103.8198, 'flag': '🇸🇬',
            'info': 'Host City', 'priority': 'high'
        },
        'New York': {
            'lat': 40.7128, 'lng': -74.0060, 'flag': '🇺🇸',
            'info': '2012 Winner', 'priority': 'high'
        },
        'Bilbao': {
            'lat': 43.2627, 'lng': -2.9253, 'flag': '🇪🇸',
            'info': '2010 Winner', 'priority': 'high'
        },
        'Seoul': {
            'lat': 37.5665, 'lng': 126.9780, 'flag': '🇰🇷',
            'info': '2018 Winner', 'priority': 'high'
        },
        'Amsterdam': {
            'lat': 52.3676, 'lng': 4.9041, 'flag': '🇳🇱',
            'info': 'Special Mention', 'priority': 'medium'
        },
        'Barcelona': {
            'lat': 41.3851, 'lng': 2.1734, 'flag': '🇪🇸',
            'info': 'Special Mention', 'priority': 'medium'
        },
        'Copenhagen': {
            'lat': 55.6761, 'lng': 12.5683, 'flag': '🇩🇰',
            'info': 'Special Mention', 'priority': 'medium'
        },
        'Melbourne': {
            'lat': -37.8136, 'lng': 144.9631, 'flag': '🇦🇺',
            'info': 'Special Mention', 'priority': 'medium'
        }
    }
    
    return cities

def create_radial_gradient_frames(cities_data, n_frames=60):
    """Create animation frames with radial gradients emanating from cities"""
    
    # Get selected cities from session state
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        if not isinstance(selected_cities, list):
            selected_cities = []
    except Exception:
        selected_cities = []
    
    frames = []
    
    for frame_i in range(n_frames):
        frame_data = []
        
        # Create radial gradient effect for each city
        for city_name, city_data in cities_data.items():
            is_selected = city_name in selected_cities
            
            # Skip if not selected (for cleaner display)
            if not is_selected and len(selected_cities) > 0:
                continue
            
            # Create multiple concentric circles for gradient effect
            wave_progress = frame_i / n_frames
            
            # Create 3 expanding circles with decreasing opacity
            for circle_idx in range(3):
                base_radius = 2 + circle_idx * 3  # Base radius for each circle
                wave_offset = circle_idx * 0.3  # Phase offset for each circle
                
                # Calculate current radius based on wave progress
                current_progress = (wave_progress + wave_offset) % 1.0
                radius = base_radius * (1 + current_progress * 4)  # Expand radius
                opacity = (1 - current_progress) * 0.6  # Fade out as it expands
                
                if opacity > 0.05:  # Only show if visible enough
                    frame_data.append(go.Scattergeo(
                        lon=[city_data['lng']],
                        lat=[city_data['lat']],
                        mode='markers',
                        marker=dict(
                            size=radius,
                            color='rgba(255, 215, 0, 0)',  # Transparent center
                            line=dict(
                                width=2,
                                color=f'rgba(255, 215, 0, {opacity})'
                            ),
                            symbol='circle'
                        ),
                        hovertemplate=f"<b>{city_data['flag']} {city_name}</b><br>" +
                                     f"{city_data['info']}<br>" +
                                     f"<extra></extra>",
                        showlegend=False,
                        name=f"{city_name}_gradient_{circle_idx}"
                    ))
            
            # Add center point
            frame_data.append(go.Scattergeo(
                lon=[city_data['lng']],
                lat=[city_data['lat']],
                mode='markers',
                marker=dict(
                    size=8,
                    color='rgba(255, 215, 0, 0.9)',
                    line=dict(width=1, color='rgba(255, 215, 0, 0.5)'),
                    symbol='circle'
                ),
                hovertemplate=f"<b>{city_data['flag']} {city_name}</b><br>" +
                             f"{city_data['info']}<br>" +
                             f"<extra></extra>",
                showlegend=False,
                name=f"{city_name}_center"
            ))
        
        frames.append(go.Frame(data=frame_data, name=str(frame_i)))
    
    return frames

def render_integrated_world_map():
    """Render integrated world map with auto-playing radial animations"""
    
    cities_data = create_radial_animation_data()
    
    # Create animation frames
    frames = create_radial_gradient_frames(cities_data, n_frames=60)
    
    # Create initial frame (first frame data)
    initial_data = frames[0].data if frames else []
    
    # Create figure
    fig = go.Figure(data=initial_data, frames=frames)
    
    # Configure Singapore-centered projection with clean styling  
    fig.update_geos(
        projection_type="natural earth",
        center=dict(lat=1.3521, lon=103.8198),  # Center on Singapore
        projection_rotation=dict(lon=103.8198),  # Rotate to center Singapore
        showland=True,
        landcolor='rgba(40, 45, 55, 0.3)',  # Very subtle landforms
        showocean=True,
        oceancolor='rgba(8, 12, 20, 1.0)',  # Deep dark ocean
        showlakes=True,
        lakecolor='rgba(8, 12, 20, 0.8)',
        showcountries=False,  # Remove country outlines
        showcoastlines=True,
        coastlinecolor='rgba(80, 90, 105, 0.2)',  # Very subtle coastlines only
        coastlinewidth=0.5,
        showframe=False,
        bgcolor='rgba(8, 12, 20, 1.0)'
    )
    
    # Clean layout with no controls
    fig.update_layout(
        title='',  # No title for clean integration
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        paper_bgcolor='rgba(8, 12, 20, 1.0)',
        plot_bgcolor='rgba(8, 12, 20, 1.0)',
        font=dict(color='rgba(255, 255, 255, 0.9)'),  # White text
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),  # No margins
        showlegend=False,
        # Remove all controls and toolbars
        updatemenus=[],
        annotations=[]
    )
    
    # Configure auto-play animation
    fig.layout.updatemenus = []  # Remove play/pause buttons
    
    return fig

def render_integrated_map_component():
    """Main component for seamless UI integration"""
    
    # Get selected cities count for display
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        selected_count = len(selected_cities) if isinstance(selected_cities, list) else 0
    except Exception:
        selected_count = 0
    
    # Clean integration CSS
    st.markdown("""
    <style>
    /* Hide all Plotly controls for clean integration */
    .js-plotly-plot .plotly .modebar {
        display: none !important;
    }
    
    .js-plotly-plot .plotly .plotly-graph-div {
        background: rgba(8, 12, 20, 1.0) !important;
        border: none !important;
    }
    
    /* Seamless map integration */
    .integrated-map-container {
        background: rgba(8, 12, 20, 1.0);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(80, 90, 105, 0.1);
        margin: 0;
        padding: 0;
    }
    
    /* Auto-hide scrollbars in map */
    .integrated-map-container::-webkit-scrollbar {
        display: none;
    }
    
    /* Remove any Plotly branding */
    .plotly-notifier {
        display: none !important;
    }
    
    /* Ensure white text throughout */
    .plotly text {
        fill: rgba(255, 255, 255, 0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the figure
    fig = render_integrated_world_map()
    
    # Display with auto-animation
    with st.container():
        st.markdown('<div class="integrated-map-container">', unsafe_allow_html=True)
        
        # Display the map with auto-animation
        map_container = st.plotly_chart(
            fig, 
            use_container_width=True, 
            key="integrated_world_map",
            config={
                'displayModeBar': False,  # Hide toolbar
                'staticPlot': False,  # Allow interaction
                'doubleClick': 'reset',  # Allow reset on double-click
                'showTips': False,  # Hide tips
                'displaylogo': False,  # Hide Plotly logo
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
            }
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-start animation with JavaScript
    st.markdown(f"""
    <script>
    // Auto-start radial gradient animation
    setTimeout(function() {{
        var plotlyDiv = document.querySelector('[data-testid="stPlotlyChart"] .js-plotly-plot');
        if (plotlyDiv && plotlyDiv.data && plotlyDiv.layout) {{
            // Start continuous animation loop
            function startRadialAnimation() {{
                Plotly.animate(plotlyDiv, null, {{
                    frame: {{duration: 100, redraw: true}},
                    transition: {{duration: 50}},
                    mode: 'immediate'
                }}).then(function() {{
                    // Loop the animation continuously
                    setTimeout(startRadialAnimation, 50);
                }});
            }}
            startRadialAnimation();
        }}
    }}, 1000);
    </script>
    """, unsafe_allow_html=True)

def render_clean_world_map():
    """Entry point for clean integrated world map"""
    render_integrated_map_component()