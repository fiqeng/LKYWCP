"""
Interactive World Map Component with Pulsating City Markers
Professional UIUX component for LKYWCP Dashboard with accurate world map
Singapore-centered projection with crisp white linework and gold accents
Using real geographic data from Natural Earth for accuracy
"""

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import json
from io import StringIO

@st.cache_data
def load_world_boundaries():
    """Load world boundaries from Natural Earth data with caching"""
    try:
        # Use Natural Earth's simplified world boundaries (50m resolution for performance)
        url = "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson"
        
        # Fallback: if that fails, use a simpler approach
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                world_data = gpd.read_file(StringIO(response.text))
                return world_data
        except:
            pass
            
        # Fallback: use built-in world data
        try:
            world_data = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            return world_data
        except:
            return None
            
    except Exception as e:
        st.error(f"Error loading world boundaries: {e}")
        return None

def render_world_map_with_interaction():
    """Enhanced Singapore-centered world map with real geographic data and gold LKYWCP styling"""
    
    # Get selected cities from session state with error handling
    try:
        selected_cities = st.session_state.get('selected_cities', [])
        if not isinstance(selected_cities, list):
            selected_cities = []
    except Exception:
        selected_cities = []
    
    # Real city coordinates with LKYWCP prize information
    cities = {
        'Singapore': {
            'lat': 1.3521, 'lng': 103.8198, 'flag': '🇸🇬',
            'prize_info': 'Host City - Prize Organizer'
        },
        'New York': {
            'lat': 40.7128, 'lng': -74.0060, 'flag': '🇺🇸',
            'prize_info': '2012 Laureate Winner'
        },
        'Bilbao': {
            'lat': 43.2627, 'lng': -2.9253, 'flag': '🇪🇸',
            'prize_info': '2010 Laureate Winner'
        },
        'Seoul': {
            'lat': 37.5665, 'lng': 126.9780, 'flag': '🇰🇷',
            'prize_info': '2018 Laureate Winner'
        },
        'Amsterdam': {
            'lat': 52.3676, 'lng': 4.9041, 'flag': '🇳🇱',
            'prize_info': 'Special Mention'
        },
        'Barcelona': {
            'lat': 41.3851, 'lng': 2.1734, 'flag': '🇪🇸',
            'prize_info': 'Special Mention'
        },
        'Copenhagen': {
            'lat': 55.6761, 'lng': 12.5683, 'flag': '🇩🇰',
            'prize_info': 'Special Mention (2010)'
        },
        'Melbourne': {
            'lat': -37.8136, 'lng': 144.9631, 'flag': '🇦🇺',
            'prize_info': 'Special Mention (2010)'
        }
    }
    
    # Create a Folium map centered on Singapore
    # Using a projection that works well for Singapore-centered view
    singapore_lat, singapore_lng = cities['Singapore']['lat'], cities['Singapore']['lng']
    
    # Create the map with custom styling - Singapore-centered projection
    # Using bounds that center around Singapore's longitude (103.8°E)
    m = folium.Map(
        location=[singapore_lat, singapore_lng],
        zoom_start=2,  # Lower zoom for better global view
        tiles=None,  # We'll add custom tiles
        max_bounds=True,
        world_copy_jump=False,
        no_wrap=False,  # Allow wrapping to center on Singapore
        prefer_canvas=True,
        min_zoom=1,
        max_zoom=10
    )
    
    # Set custom bounds centered on Singapore longitude
    # This creates a view where Singapore is truly at the center
    west_bound = singapore_lng - 180  # 180 degrees west of Singapore
    east_bound = singapore_lng + 180  # 180 degrees east of Singapore
    north_bound = 85
    south_bound = -85
    
    m.fit_bounds([[south_bound, west_bound], [north_bound, east_bound]])
    
    # Add custom dark ocean tiles that match LKYWCP branding
    # Using a tile server that handles custom projections better
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Dark Ocean',
        control=False,
        overlay=False,
        no_wrap=False  # Allow wrapping for Singapore centering
    ).add_to(m)
    
    # Alternative: Add a simple dark base layer
    folium.TileLayer(
        tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
        attr='Stadia Maps',
        name='Dark Base',
        control=False,
        overlay=False,
        no_wrap=False
    ).add_to(m)
    
    # Add country boundaries with crisp white outlines
    world_data = load_world_boundaries()
    
    if world_data is not None:
        # Style for country boundaries - crisp white outlines on dark background
        country_style = {
            'fillColor': 'transparent',
            'color': 'rgba(255, 255, 255, 0.9)',
            'weight': 1.5,
            'fillOpacity': 0,
            'opacity': 0.9
        }
        
        # Add countries to map
        folium.GeoJson(
            world_data,
            style_function=lambda x: country_style,
            tooltip=folium.Tooltip('Country boundaries'),
            popup=False
        ).add_to(m)
    
    # Add enhanced pulsating gold animations for all cities with prize information tooltips
    for city_name, city_data in cities.items():
        is_selected = city_name in selected_cities
        
        # Create rich tooltip with prize information
        tooltip_text = f"{city_data['flag']} {city_name}<br/><b>{city_data['prize_info']}</b>"
        popup_text = f"{city_data['flag']} <b>{city_name}</b><br/>{city_data['prize_info']}"
        
        # All cities get gold pulsating markers with enhanced animations
        if is_selected:
            # Selected cities get larger gold markers with stronger pulse
            marker_id = f"marker-{city_name.lower().replace(' ', '-')}"
            folium.CircleMarker(
                location=[city_data['lat'], city_data['lng']],
                radius=20,
                popup=folium.Popup(popup_text, parse_html=True),
                tooltip=folium.Tooltip(tooltip_text, parse_html=True),
                color='#FFD700',
                weight=5,
                fillColor='rgba(255, 215, 0, 0.5)',
                fillOpacity=0.5,
                opacity=1.0,
                className=f'pulsating-marker-large {marker_id}'
            ).add_to(m)
            
        else:
            # Unselected cities get smaller gold markers with gentle pulse
            marker_id = f"marker-{city_name.lower().replace(' ', '-')}"
            folium.CircleMarker(
                location=[city_data['lat'], city_data['lng']],
                radius=14,
                popup=folium.Popup(popup_text, parse_html=True),
                tooltip=folium.Tooltip(tooltip_text, parse_html=True),
                color='#FFD700',
                weight=3,
                fillColor='rgba(255, 215, 0, 0.4)',
                fillOpacity=0.4,
                opacity=0.9,
                className=f'pulsating-marker-small {marker_id}'
            ).add_to(m)
    
    # Add special highlight for Singapore (center of analysis)
    folium.CircleMarker(
        location=[singapore_lat, singapore_lng],
        radius=25,
        popup="🇸🇬 Singapore - Analysis Center",
        color='rgba(255, 215, 0, 0.5)',
        weight=2,
        fillColor='transparent',
        fillOpacity=0,
        opacity=0.6,
        dashArray='10, 10'
    ).add_to(m)
    
    # Custom CSS for LKYWCP branding with gold pulsating animations
    st.markdown("""
    <style>
    .lkywcp-map-header {
        text-align: center;
        margin-bottom: 15px;
        padding: 15px;
        background: linear-gradient(135deg, #0a1525 0%, #162033 50%, #0c1b2e 100%);
        border-radius: 12px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .lkywcp-map-header h3 {
        margin: 0 0 5px 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: #FFD700;
        text-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    
    .lkywcp-map-header p {
        margin: 0;
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
    }
    
    .folium-map {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 16px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    /* Enhanced Gold pulsating animation keyframes */
    @keyframes pulse-gold-strong {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.8),
                        0 0 0 0 rgba(255, 215, 0, 0.6);
            opacity: 1;
        }
        25% {
            transform: scale(1.05);
            box-shadow: 0 0 0 5px rgba(255, 215, 0, 0.6),
                        0 0 0 10px rgba(255, 215, 0, 0.3);
            opacity: 0.9;
        }
        50% {
            transform: scale(1.1);
            box-shadow: 0 0 0 10px rgba(255, 215, 0, 0.4),
                        0 0 0 15px rgba(255, 215, 0, 0.2);
            opacity: 0.8;
        }
        75% {
            transform: scale(1.05);
            box-shadow: 0 0 0 15px rgba(255, 215, 0, 0.2),
                        0 0 0 20px rgba(255, 215, 0, 0.1);
            opacity: 0.9;
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 20px rgba(255, 215, 0, 0),
                        0 0 0 25px rgba(255, 215, 0, 0);
            opacity: 1;
        }
    }
    
    @keyframes pulse-gold-gentle {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7);
            opacity: 0.9;
        }
        50% {
            transform: scale(1.08);
            box-shadow: 0 0 0 8px rgba(255, 215, 0, 0.3),
                        0 0 0 12px rgba(255, 215, 0, 0.15);
            opacity: 0.7;
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 15px rgba(255, 215, 0, 0);
            opacity: 0.9;
        }
    }
    
    /* Apply enhanced pulsating animation to city markers */
    .pulsating-marker-large {
        animation: pulse-gold-strong 1.8s ease-in-out infinite;
        border-radius: 50% !important;
        transition: all 0.3s ease;
    }
    
    .pulsating-marker-small {
        animation: pulse-gold-gentle 2.2s ease-in-out infinite;
        border-radius: 50% !important;
        transition: all 0.3s ease;
    }
    
    /* Special enhanced pulse for Singapore */
    .marker-singapore {
        animation: pulse-gold-strong 1.5s ease-in-out infinite !important;
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
    }
    
    /* Style for leaflet tooltips to match LKYWCP theme */
    .leaflet-tooltip {
        background-color: rgba(10, 21, 37, 0.95) !important;
        border: 1px solid #FFD700 !important;
        border-radius: 8px !important;
        color: #FFD700 !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    
    .leaflet-popup-content-wrapper {
        background-color: rgba(10, 21, 37, 0.95) !important;
        border: 1px solid #FFD700 !important;
        border-radius: 8px !important;
        color: #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header for the map
    st.markdown(f"""
    <div class="lkywcp-map-header">
        <h3>🌍 Our Global Network</h3>
        <p>Selected Cities: {len(selected_cities)} of 8 | Real Geographic Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add JavaScript to enhance the Singapore-centered view
    singapore_center_js = f"""
    <script>
    setTimeout(function() {{
        // Find the map and center it properly on Singapore
        var maps = document.querySelectorAll('.folium-map');
        if (maps.length > 0) {{
            var mapContainer = maps[0];
            var leafletMap = window[mapContainer.id + '_map'];
            if (leafletMap) {{
                // Force center on Singapore with custom bounds
                leafletMap.setView([{singapore_lat}, {singapore_lng}], 2);
                leafletMap.setMaxBounds([[-85, {singapore_lng - 180}], [85, {singapore_lng + 180}]]);
            }}
        }}
    }}, 1000);
    </script>
    """
    
    # Apply the centering script
    st.markdown(singapore_center_js, unsafe_allow_html=True)
    
    # Render the interactive map
    try:
        map_data = st_folium(
            m,
            width=None,
            height=520,  # Slightly taller for better view
            returned_objects=["last_object_clicked"],
            key="world_map",
            center=[singapore_lat, singapore_lng],  # Force center on Singapore
            zoom=2
        )
        
        # Handle map interactions (optional)
        if map_data['last_object_clicked']:
            clicked_data = map_data['last_object_clicked']
            if 'popup' in clicked_data:
                st.info(f"Clicked: {clicked_data['popup']}")
                
    except Exception as e:
        st.error(f"Error rendering interactive map: {str(e)}")
        # Fallback to simple display
        st.info("Loading fallback map display...")
        render_fallback_map(selected_cities, cities)

def render_fallback_map(selected_cities, cities):
    """Fallback SVG map if Folium fails"""
    
    # Simple SVG fallback with better geographic accuracy
    svg_content = f"""
    <div style="background: linear-gradient(135deg, #0a1525 0%, #162033 50%, #0c1b2e 100%); 
                border-radius: 12px; padding: 20px; margin: 10px 0;">
        <div style="text-align: center; margin-bottom: 15px;">
            <h4 style="color: #FFD700; margin: 0;">🌍 Geographic Network Map</h4>
            <p style="color: rgba(255,255,255,0.8); margin: 5px 0; font-size: 0.9rem;">
                Selected Cities: {len(selected_cities)} of 8
            </p>
        </div>
        
        <svg viewBox="-180 -90 360 180" width="100%" height="400" 
             style="background: #0a1525; border-radius: 8px;">
            
            <!-- World outline (simplified but accurate) -->
            <g stroke="rgba(255,255,255,0.6)" stroke-width="0.5" fill="none">
                <!-- Continental outlines -->
                <path d="M-160 60 L-120 65 L-80 55 L-60 45 L-40 35 M-140 -10 L-110 -5 L-80 -15 L-60 -25"/>
                <path d="M-10 65 L20 60 L50 55 L70 45 M0 35 L30 40 L60 35"/>
                <path d="M80 -40 L120 -35 L150 -30 L160 -20"/>
                <circle cx="0" cy="0" r="2" fill="rgba(255,255,255,0.3)"/>
            </g>
            
            <!-- City markers -->
    """
    
    for city_name, city_data in cities.items():
        is_selected = city_name in selected_cities
        x, y = city_data['lng'], -city_data['lat']  # SVG coordinate system
        
        if is_selected:
            svg_content += f"""
                <g>
                    <circle cx="{x}" cy="{y}" r="3" fill="#FFD700" opacity="0.8"/>
                    <circle cx="{x}" cy="{y}" r="6" fill="none" stroke="#FFD700" stroke-width="1" opacity="0.6"/>
                    <text x="{x}" y="{y-8}" text-anchor="middle" fill="#FFD700" font-size="3" font-weight="bold">
                        {city_data['flag']} {city_name}
                    </text>
                </g>
            """
        else:
            svg_content += f"""
                <g>
                    <circle cx="{x}" cy="{y}" r="2" fill="rgba(255,255,255,0.7)"/>
                    <text x="{x}" y="{y-6}" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-size="2.5">
                        {city_data['flag']} {city_name}
                    </text>
                </g>
            """
    
    svg_content += """
            <!-- Singapore center highlight -->
            <circle cx="103.8198" cy="-1.3521" r="8" fill="none" stroke="rgba(255,215,0,0.4)" 
                    stroke-width="1" stroke-dasharray="2,2" opacity="0.8"/>
        </svg>
    </div>
    """
    
    st.markdown(svg_content, unsafe_allow_html=True)

def render_world_map():
    """Basic version for simple display"""
    render_world_map_with_interaction()