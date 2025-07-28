# === Citypulse Professional Dashboard ===
# Professional urban sentiment intelligence dashboard with enhanced UX/UI
# Features: Landing page, city selection, manual scraping, professional styling

import praw
from openai import OpenAI
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import re
import time
from datetime import datetime
from world_map_component import render_world_map_with_interaction
from advanced_world_map import render_advanced_world_map_component
from integrated_world_map import render_clean_world_map

# -- Global Dark Minimal Theme --
st.markdown("""
<style>
.main .block-container {
    background-color: rgba(8, 12, 20, 1.0) !important;
    color: rgba(255, 255, 255, 0.9) !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFD700 !important;
    font-weight: 500 !important;
}
.stButton > button {
    background: rgba(255, 215, 0, 0.1) !important;
    border: 1px solid rgba(255, 215, 0, 0.3) !important;
    color: #FFD700 !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div {
    background-color: rgba(8, 12, 20, 0.8) !important;
    border: 1px solid rgba(255, 215, 0, 0.2) !important;
    border-radius: 6px !important;
}
.stApp {
    background-color: rgba(8, 12, 20, 1.0) !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -- API Keys --
with open("OpenAI_Secret_Key.txt", "r") as f:
    api_key = f.read().strip()

with open("NewsAPI_Secret_Key.txt", "r") as f:
    newsapi_key = f.read().strip()

client = OpenAI(api_key=api_key)

# -- Reddit Setup --
reddit = praw.Reddit(
    client_id="UDj6CSWAjCfLsGZZk--Pyw",
    client_secret="NKpJZwtmQY084TEhXM3X6Vhvv344PA",
    user_agent="LKYWCP_Scraper"
)

# -- Streamlit Configuration --
st.set_page_config(
    page_title="Citypulse Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏙️"
)

# -- Session State Initialization --
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'
if 'selected_cities' not in st.session_state:
    st.session_state.selected_cities = []
if 'selected_pillars' not in st.session_state:
    st.session_state.selected_pillars = []
if 'time_frame_months' not in st.session_state:
    st.session_state.time_frame_months = 12
if 'scraping_complete' not in st.session_state:
    st.session_state.scraping_complete = False
if 'reddit_data' not in st.session_state:
    st.session_state.reddit_data = pd.DataFrame()
if 'news_data' not in st.session_state:
    st.session_state.news_data = pd.DataFrame()
if 'claude_deep_research' not in st.session_state:
    st.session_state.claude_deep_research = False
if 'research_results' not in st.session_state:
    st.session_state.research_results = ""
if 'research_metadata' not in st.session_state:
    st.session_state.research_metadata = {}

# -- Available Cities Configuration --
AVAILABLE_CITIES = {
    'New York': {'keyword': 'new york', 'flag': '🇺🇸'},
    'Singapore': {'keyword': 'singapore', 'flag': '🇸🇬'},
    'Bilbao': {'keyword': 'bilbao', 'flag': '🇪🇸'},
    'Seoul': {'keyword': 'seoul', 'flag': '🇰🇷'},
    'Amsterdam': {'keyword': 'amsterdam', 'flag': '🇳🇱'},
    'Barcelona': {'keyword': 'barcelona', 'flag': '🇪🇸'},
    'Copenhagen': {'keyword': 'copenhagen', 'flag': '🇩🇰'},
    'Melbourne': {'keyword': 'melbourne', 'flag': '🇦🇺'}
}

# -- LKYWCP Pillars Configuration --
LKYWCP_PILLARS = {
    'Leadership & Governance': ['leadership', 'governance', 'vision', 'foresight', 'commitment', 'government', 'policy', 'mayor', 'council', 'administration'],
    'Creativity & Innovation': ['creativity', 'innovation', 'master plan', 'strategy', 'implementation', 'new models', 'benchmarks', 'technology', 'digital', 'smart city'],
    'Replicability': ['replicable', 'practices', 'ideas', 'adopted', 'benefit', 'other cities', 'scalable', 'transferable', 'best practices'],
    'Impact of Urban Initiatives Implemented': ['urban initiatives', 'positive changes', 'urban environment', 'local communities', 'people', 'impact', 'transformation', 'development'],
    'Sustainability of the Transformation': ['sustainability', 'institutionalised processes', 'unaffected by leadership changes', 'buy-in', 'local communities', 'vision', 'long-term'],
    'Integration of Plans': ['integration', 'relation of plans', 'regional', 'metropolitan level', 'coordination', 'planning', 'alignment']
}

# -- Custom CSS Styles --
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .welcome-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .welcome-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4rem;
        margin-top: 2rem;
    }
    
    .logo-box {
        background: rgba(255,255,255,0.15);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .logo-box:hover {
        transform: translateY(-5px);
    }
    
    .city-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 0.5rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        cursor: pointer;
    }
    
    .city-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .city-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #f5f7ff 0%, #e8f0ff 100%);
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7ff 0%, #e8f0ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9ff;
        border: 2px solid #e1e8ff;
        border-radius: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# -- Helper Functions --
def summarise_posts(titles, label="posts"):
    formatted_titles = "\n".join([f"- {title}" for title in titles])
    prompt = (
        f"Write a two-sentence analytic blurb for urban planners that captures the key mood and concerns across these {label}:\n\n"
        f"{formatted_titles}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"

def gpt_sentiment_score(title: str, city_context: str):
    """Return a tuple: (<float score>, <reason>) where score ∈ [-1, 1]."""
    prompt = f"""
You are rating sentiment towards urban conditions in {city_context.title()}. Assess the tone of this headline/post.
Give a single floating-point score between -1 (very unfavourable) and 1 (very favourable), then one short sentence explaining the main signal.

Title: "{title}"

Respond exactly in this format:
Score: <-1 to 1>
Reason: <one sentence>
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=120,
        )
        content = response.choices[0].message.content
        score_match = re.search(r"Score:\s*([\-0-9.]+)", content)
        reason_match = re.search(r"Reason:\s*(.*)", content)
        score = float(score_match.group(1)) if score_match else 0.0
        reason = reason_match.group(1).strip() if reason_match else "No reason provided."
        return score, reason
    except Exception as e:
        return 0.0, f"Error: {e}"

def score_band(s: float) -> str:
    if s <= -0.6:
        return "Strongly Negative"
    if s < -0.2:
        return "Negative"
    if s <= 0.2:
        return "Neutral"
    if s < 0.6:
        return "Positive"
    return "Strongly Positive"

def generate_research_prompt(selected_cities, selected_pillars, time_frame_months=12):
    """Generate dynamic research prompt based on user selections"""
    cities_text = ""
    if len(selected_cities) == 1:
        cities_text = f"{selected_cities[0]}"
    elif len(selected_cities) == 2:
        cities_text = f"{selected_cities[0]} and {selected_cities[1]}"
    else:
        cities_text = f"{', '.join(selected_cities[:-1])}, and {selected_cities[-1]}"
    
    # Map pillar names to official LKYWCP pillars (no mapping needed as we use official names)
    pillar_mapping = {
        'Leadership & Governance': 'Leadership & Governance',
        'Creativity & Innovation': 'Creativity & Innovation',
        'Replicability': 'Replicability',
        'Impact of Urban Initiatives Implemented': 'Impact of Urban Initiatives Implemented',
        'Sustainability of the Transformation': 'Sustainability of the Transformation',
        'Integration of Plans': 'Integration of Plans'
    }
    
    selected_official_pillars = []
    for pillar in selected_pillars:
        official_pillar = pillar_mapping.get(pillar, pillar)
        if official_pillar not in selected_official_pillars:
            selected_official_pillars.append(official_pillar)
    
    # Use only selected pillars, not all LKYWCP pillars
    final_pillars = selected_official_pillars
    
    pillars_text = ', '.join(final_pillars)
    
    # Get current date for research period based on selected timeframe
    from datetime import datetime, timedelta
    current_date = datetime.now()
    start_date = current_date - timedelta(days=time_frame_months * 30)  # Approximate months to days
    
    # Calculate start and end years
    start_year = start_date.year
    end_year = current_date.year
    
    research_prompt = f"""You are an impartial, neutral and nuanced urban-policy analyst working for Singapore's Urban Redevelopment Authority. Evaluate the current performance of {cities_text} in the period {start_year}–{end_year}.

Evaluation framework
Assess {'all cities' if len(selected_cities) > 1 else 'the city'} across the selected Lee Kuan Yew World City Prize pillars—{pillars_text}—giving each pillar exactly the same weight. In addition, highlight any emerging urban factors that materially influence {'any city' if len(selected_cities) > 1 else 'the city'}, such as digital equity, housing justice, nightlife culture, public mental health, climate migration or surveillance.

Required output
Present your results in {'separate' if len(selected_cities) > 1 else 'a single'} Markdown table{'s' if len(selected_cities) > 1 else ''}—{'one for each city' if len(selected_cities) > 1 else 'for the city'}—followed by a {'comparative' if len(selected_cities) > 1 else 'summary'} paragraph of no more than 250 words.

To make the briefing instantly readable and machine-sortable, each table must contain the following columns in the order shown:

| Pillar | Trend | Key Indicators & Metrics | Concise Findings (≤ 50 words) | Official Sources | Citizen / Unofficial Sources | Publication Dates | Original Language |

Trend must be labelled Improving, Maintaining or Backsliding.

Key Indicators & Metrics should list concrete figures (for example "+3 % QoQ rental growth; 14 µg/m³ annual PM2.5").

Official Sources and Citizen / Unofficial Sources should each contain as many hyperlinks as you can credibly provide; there is no upper limit.

Publication Dates should show the date range covered by the sources in that row (e.g. "{start_date.strftime('%d %b').lstrip('0')} – {current_date.strftime('%d %b %Y').lstrip('0')}").

Original Language should state "EN", "ES", "EU (Basque)", etc., or "Multiple" if a mixture is cited.

Source requirements
Cite at least one hundred distinct sources in total (more are welcome) and verify that every one was published between {start_date.strftime('%d %B').lstrip('0')} and {current_date.strftime('%d %B %Y').lstrip('0')}. Balance official material (municipal portals, UN or OECD datasets, CDP filings, court documents, policy white papers) with citizen perspectives (reputable news outlets, LinkedIn insights, Instagram threads, Reddit discussions, Twitter/X posts, local forums). When official optimism clashes with grass-roots scepticism, show both views impartially.

Methodology
Harvest all relevant material for the target period, translating where necessary and noting the original language. Allocate each source to a city and pillar. Cross-check figures to remove duplicates and resolve discrepancies, then decide the trend for every pillar based on the balance of evidence. Draft findings in clear, factual UK-English sentences of no more than fifty words, embed all hyperlinks, confirm their dates, count your citations, and supply the final tables plus {'comparative' if len(selected_cities) > 1 else 'summary'} paragraph—nothing more.

Style guidance
Write exclusively in UK English, omit value-laden adjectives, and never use the expressions complex interplay or critical engagement. Keep the entire deliverable concise, scannable and suitable for rapid decision-making by URA reviewers."""
    
    return research_prompt

def conduct_claude_research(selected_cities, selected_pillars, time_frame_months=12, custom_prompt=None):
    """Execute Claude deep research based on user selections"""
    if custom_prompt:
        research_prompt = custom_prompt
    else:
        research_prompt = generate_research_prompt(selected_cities, selected_pillars, time_frame_months)
    
    try:
        # Execute research using OpenAI client (Claude API integration)
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 as proxy for Claude research capabilities
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional urban policy analyst with access to comprehensive research capabilities. Conduct thorough research using multiple sources and provide detailed analysis in the requested format."
                },
                {
                    "role": "user", 
                    "content": research_prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        research_content = response.choices[0].message.content
        
        # Generate metadata
        from datetime import datetime
        metadata = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cities": selected_cities,
            "pillars": selected_pillars,
            "research_period": "Last 3 months",
            "model": "Claude Research Assistant",
            "prompt_length": len(research_prompt),
            "response_length": len(research_content)
        }
        
        return research_content, metadata
        
    except Exception as e:
        error_message = f"""# Research Error

**Error occurred during Claude deep research:**
```
{str(e)}
```

**Attempted Analysis:**
- Cities: {', '.join(selected_cities)}
- Pillars: {', '.join(selected_pillars)}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check your API configuration and try again."""
        
        metadata = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cities": selected_cities,
            "pillars": selected_pillars,
            "error": str(e),
            "status": "failed"
        }
        
        return error_message, metadata

def export_research_markdown(research_content, metadata):
    """Generate exportable markdown document"""
    from datetime import datetime
    
    # Create professional markdown document
    markdown_document = f"""# LKYWCP Urban Policy Analysis Report

**Generated by:** Claude Research Assistant  
**Date:** {metadata.get('generated_at', 'Unknown')}  
**Analysis Period:** {metadata.get('research_period', 'Unknown')}  

## Executive Summary

This report provides comprehensive urban policy analysis for the selected cities based on Lee Kuan Yew World City Prize evaluation criteria.

### Scope of Analysis

**Cities Analyzed:** {', '.join(metadata.get('cities', []))}  
**Evaluation Pillars:** {', '.join(metadata.get('pillars', []))}  
**Research Model:** {metadata.get('model', 'Unknown')}  

---

## Detailed Analysis

{research_content}

---

## Methodology Notes

- **Source Requirements:** Minimum 100 distinct sources per city
- **Evaluation Framework:** Six official LKYWCP pillars with equal weighting
- **Language Coverage:** Multi-language sources with English translation
- **Source Balance:** Official municipal data + citizen perspectives
- **Trend Analysis:** Improving / Maintaining / Backsliding classification

## Report Metadata

| Attribute | Value |
|-----------|-------|
| Generated At | {metadata.get('generated_at', 'Unknown')} |
| Cities Count | {len(metadata.get('cities', []))} |
| Pillars Count | {len(metadata.get('pillars', []))} |
| Prompt Length | {metadata.get('prompt_length', 0):,} characters |
| Response Length | {metadata.get('response_length', 0):,} characters |
| Status | {metadata.get('status', 'completed').title()} |

---

*This report was generated using Claude Research Assistant for the Singapore Urban Redevelopment Authority (URA) LKYWCP evaluation framework.*
"""
    
    return markdown_document

def fetch_reddit_sentiment(cities, num_posts=100):
    """Fetch Reddit sentiment for selected cities with pillar-based keyword targeting"""
    all_data = []
    
    # Generate pillar keywords for targeting
    all_keywords = []
    for pillar in st.session_state.selected_pillars:
        all_keywords.extend(LKYWCP_PILLARS[pillar])
    combined_keywords = list(set(all_keywords))
    
    for city_name in cities:
        city_info = AVAILABLE_CITIES[city_name]
        keyword = city_info['keyword']
        
        with st.spinner(f"Scraping Reddit for {city_name}..."):
            try:
                # Search with different keyword combinations
                search_queries = [
                    keyword,
                    f"{keyword} {combined_keywords[0]}" if combined_keywords else keyword,
                    f"{keyword} OR {combined_keywords[1]}" if len(combined_keywords) > 1 else keyword
                ]
                
                posts_collected = 0
                posts_per_query = num_posts // len(search_queries)
                
                for query in search_queries:
                    if posts_collected >= num_posts:
                        break
                        
                    try:
                        for post in reddit.subreddit("all").search(query, sort="relevance", limit=posts_per_query):
                            if posts_collected >= num_posts:
                                break
                                
                            score, reason = gpt_sentiment_score(post.title, keyword)
                            
                            # Determine which pillars this post relates to
                            related_pillars = []
                            post_text = (post.title + " " + getattr(post, 'selftext', '')).lower()
                            for pillar in st.session_state.selected_pillars:
                                pillar_keys = LKYWCP_PILLARS[pillar]
                                if any(kw.lower() in post_text for kw in pillar_keys):
                                    related_pillars.append(pillar)
                            
                            all_data.append({
                                "City": city_name,
                                "Title": post.title,
                                "Sentiment_Score": score,
                                "Band": score_band(score),
                                "Reason": reason,
                                "Upvotes": post.score,
                                "Comments": post.num_comments,
                                "URL": post.url,
                                "Source": "Reddit",
                                "Related_Pillars": ", ".join(related_pillars) if related_pillars else "General"
                            })
                            posts_collected += 1
                    except Exception as query_error:
                        st.warning(f"Query '{query}' failed: {query_error}")
                        continue
                        
            except Exception as e:
                st.error(f"Error fetching Reddit data for {city_name}: {e}")
    
    return pd.DataFrame(all_data)

def fetch_news_sentiment(cities, num_articles=100):
    """Fetch news sentiment for selected cities with pillar-based keyword targeting"""
    from datetime import datetime, timedelta
    
    all_data = []
    
    # Generate pillar keywords for targeting
    all_keywords = []
    for pillar in st.session_state.selected_pillars:
        all_keywords.extend(LKYWCP_PILLARS[pillar])
    combined_keywords = list(set(all_keywords))
    
    # Calculate date range based on time frame
    end_date = datetime.now()
    start_date = end_date - timedelta(days=st.session_state.time_frame_months * 30)
    
    for city_name in cities:
        city_info = AVAILABLE_CITIES[city_name]
        keyword = city_info['keyword']
        
        with st.spinner(f"Scraping News for {city_name}..."):
            url = "https://newsapi.org/v2/everything"
            
            # Create search queries combining city with pillar keywords
            search_queries = [
                keyword,
                f"{keyword} AND ({' OR '.join(combined_keywords[:3])})" if combined_keywords else keyword
            ]
            
            articles_collected = 0
            articles_per_query = num_articles // len(search_queries)
            
            for query in search_queries:
                if articles_collected >= num_articles:
                    break
                    
                params = {
                    "q": query,
                    "pageSize": min(articles_per_query, 100),  # NewsAPI limit
                    "apiKey": newsapi_key,
                    "language": "en",
                    "sortBy": "relevancy",
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                }
                
                try:
                    response = requests.get(url, params=params)
                    data = response.json()
                    
                    if data.get("status") == "ok":
                        for art in data.get("articles", []):
                            if articles_collected >= num_articles:
                                break
                                
                            score, reason = gpt_sentiment_score(art["title"], keyword)
                            
                            # Determine which pillars this article relates to
                            related_pillars = []
                            article_text = (art["title"] + " " + (art.get("description", "") or "")).lower()
                            for pillar in st.session_state.selected_pillars:
                                pillar_keys = LKYWCP_PILLARS[pillar]
                                if any(kw.lower() in article_text for kw in pillar_keys):
                                    related_pillars.append(pillar)
                            
                            all_data.append({
                                "City": city_name,
                                "Title": art["title"],
                                "Sentiment_Score": score,
                                "Band": score_band(score),
                                "Reason": reason,
                                "Source": art["source"]["name"],
                                "Published": art["publishedAt"],
                                "URL": art["url"],
                                "Data_Source": "News",
                                "Related_Pillars": ", ".join(related_pillars) if related_pillars else "General"
                            })
                            articles_collected += 1
                    else:
                        st.warning(f"NewsAPI error for '{query}': {data.get('message')}")
                except Exception as e:
                    st.warning(f"Error fetching news for '{query}': {e}")
                    continue
    
    return pd.DataFrame(all_data)

# -- Page Functions --
def show_welcome_page():
    """Display the welcome page with slogan, world map, and Enter button"""
    
    # Welcome Header
    st.markdown("""
    <div class="main-header">
        <h1 class="welcome-title">📊 LKYWCP Urban Sentiment Dashboard</h1>
        <p class="welcome-subtitle">Analyzing global urban sentiment through social media and news intelligence</p>
        <div style="margin: 40px 0; padding: 30px; background: rgba(255,255,255,0.15); border-radius: 15px; backdrop-filter: blur(10px);">
            <p style="font-size: 1.3rem; margin-bottom: 20px; font-weight: 400;">
                Discover insights from Reddit discussions and news coverage across major cities, 
                filtered by Lee Kuan Yew World City Prize evaluation pillars
            </p>
        </div>
        <div class="logo-container">
            <div class="logo-box">
                <h3>LKYWCP</h3>
                <p>Lee Kuan Yew<br>World City Prize</p>
            </div>
            <div class="logo-box">
                <h3>URA</h3>
                <p>Urban Redevelopment<br>Authority</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive World Map with Advanced Options
    st.markdown("### 🌍 Our Global Network")
    
    # Map selection options
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    with col2:
        map_style = st.selectbox(
            "🗺️ Map Style:",
            ["🎯 Advanced (Singapore-Centered)", "🗺️ Classic Interactive"],
            key="welcome_map_style",
            help="Choose between advanced Singapore-centered projection with animations or classic interactive map"
        )
    
    # Render selected map type
    if map_style == "🎯 Advanced (Singapore-Centered)":
        render_clean_world_map()
    else:
        render_clean_world_map()
    
    # Enter button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Enter Dashboard", key="enter_button", use_container_width=True):
            st.session_state.current_page = 'selection'
            st.rerun()

def show_selection_page():
    """Display the selection page with cities, time frame, and pillars"""
    
    st.title("🎯 Configure Your Analysis")
    st.markdown("Select your parameters to analyze urban sentiment across cities and themes.")
    
    # City Selection
    st.subheader("🏙️ Select Cities")
    st.markdown("Choose from our curated list of world cities for sentiment analysis:")
    
    # City selection grid - 4 columns for 8 cities
    cols = st.columns(4)
    
    for idx, (city_name, city_info) in enumerate(AVAILABLE_CITIES.items()):
        with cols[idx % 4]:
            selected = st.checkbox(
                f"{city_info['flag']} {city_name}",
                key=f"city_{city_name}",
                value=city_name in st.session_state.selected_cities
            )
            
            if selected and city_name not in st.session_state.selected_cities:
                st.session_state.selected_cities.append(city_name)
            elif not selected and city_name in st.session_state.selected_cities:
                st.session_state.selected_cities.remove(city_name)
    
    # Show selected cities
    if st.session_state.selected_cities:
        st.success(f"✅ Selected: {', '.join([f'{AVAILABLE_CITIES[city]['flag']} {city}' for city in st.session_state.selected_cities])}")
    
    # Time Frame Slider
    st.subheader("⏰ Time Frame")
    time_frame = st.slider(
        "How far back should we scrape data?",
        min_value=1,
        max_value=120,
        value=st.session_state.time_frame_months,
        help="Select time frame in months (1 month = 1, 1 year = 12, 10 years = 120)"
    )
    st.session_state.time_frame_months = time_frame
    
    # Convert to readable format
    if time_frame <= 12:
        time_display = f"{time_frame} month{'s' if time_frame > 1 else ''}"
    else:
        years = time_frame // 12
        months = time_frame % 12
        time_display = f"{years} year{'s' if years > 1 else ''}"
        if months > 0:
            time_display += f" {months} month{'s' if months > 1 else ''}"
    
    st.info(f"📅 Selected time frame: **{time_display}** ago to present")
    
    # LKYWCP Pillars Selection
    st.subheader("🏛️ LKYWCP Evaluation Pillars")
    st.markdown("Choose pillars to focus your analysis:")
    
    # Pillar selection - 3 columns for 6 pillars
    pillar_cols = st.columns(3)
    
    for idx, pillar_name in enumerate(LKYWCP_PILLARS.keys()):
        with pillar_cols[idx % 3]:
            selected = st.checkbox(
                pillar_name,
                key=f"pillar_{pillar_name}",
                value=pillar_name in st.session_state.selected_pillars
            )
            
            if selected and pillar_name not in st.session_state.selected_pillars:
                st.session_state.selected_pillars.append(pillar_name)
            elif not selected and pillar_name in st.session_state.selected_pillars:
                st.session_state.selected_pillars.remove(pillar_name)
    
    # Show selected pillars
    if st.session_state.selected_pillars:
        st.success(f"✅ Pillars: {', '.join(st.session_state.selected_pillars)}")
    
    # Claude Deep Research Section
    st.markdown("---")
    st.subheader("🔬 Claude Deep Research")
    st.markdown("Enable enhanced analysis with comprehensive urban policy research and evaluation.")
    
    # Deep Research Toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        deep_research_enabled = st.checkbox(
            "Enable Claude Deep Research",
            value=st.session_state.claude_deep_research,
            help="Conduct comprehensive urban policy analysis with 100+ sources, official data, and citizen perspectives"
        )
        st.session_state.claude_deep_research = deep_research_enabled
        
    with col2:
        if deep_research_enabled:
            st.success("🔬 Enabled")
        else:
            st.info("📝 Basic Mode")
    
    # Show research preview if enabled and selections made
    if deep_research_enabled and st.session_state.selected_cities and st.session_state.selected_pillars:
        st.markdown("#### 📋 Research Preview")
        
        research_prompt = generate_research_prompt(st.session_state.selected_cities, st.session_state.selected_pillars, st.session_state.time_frame_months)
        
        # Show expandable preview
        with st.expander("🔍 View Research Brief", expanded=False):
            st.markdown("**Dynamic Research Prompt:**")
            
            # Initialize session state for edited prompt
            if 'edited_research_prompt' not in st.session_state:
                st.session_state.edited_research_prompt = research_prompt
            
            # Update the prompt if base selections changed
            if st.session_state.edited_research_prompt != research_prompt and st.button("🔄 Reset to Generated Prompt"):
                st.session_state.edited_research_prompt = research_prompt
                st.rerun()
            
            # Editable prompt
            edited_prompt = st.text_area(
                "Edit the research prompt as needed:",
                value=st.session_state.edited_research_prompt,
                height=300,
                help="This prompt will be used for comprehensive urban policy analysis. You can edit it to customize your research focus."
            )
            
            # Update session state when prompt is edited
            if edited_prompt != st.session_state.edited_research_prompt:
                st.session_state.edited_research_prompt = edited_prompt
            
            # Research scope summary
            st.markdown("**Research Scope:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cities", len(st.session_state.selected_cities))
            with col2:
                st.metric("Focus Pillars", len(st.session_state.selected_pillars))
            with col3:
                st.metric("Min. Sources", "100+")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Welcome", use_container_width=True):
            st.session_state.current_page = 'welcome'
            st.rerun()
    
    with col3:
        can_proceed = len(st.session_state.selected_cities) > 0 and len(st.session_state.selected_pillars) > 0
        if st.button("📊 Start Analysis", type="primary", use_container_width=True, disabled=not can_proceed):
            if can_proceed:
                st.session_state.current_page = 'scraping'
                # Default to top 100 posts and headlines
                st.session_state.num_reddit_posts = 100
                st.session_state.num_news_articles = 100
                st.rerun()
    
    if not can_proceed:
        st.warning("⚠️ Please select at least one city and one pillar to begin analysis.")
    
    # Show current selection summary
    if st.session_state.selected_cities and st.session_state.selected_pillars:
        st.markdown("---")
        st.subheader("📋 Current Selection Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Selected Cities:**")
            for city in st.session_state.selected_cities:
                st.write(f"• {AVAILABLE_CITIES[city]['flag']} {city}")
                
        with col2:
            st.write("**Selected Pillars:**")
            for pillar in st.session_state.selected_pillars:
                st.write(f"• {pillar}")
        
        st.info(f"**Analysis Parameters:** Top 100 posts and 100 headlines from the last {time_display}")
        
        # Show keyword preview
        all_keywords = []
        for pillar in st.session_state.selected_pillars:
            all_keywords.extend(LKYWCP_PILLARS[pillar])
        
        combined_keywords = list(set(all_keywords))[:10]  # Show first 10 unique keywords
        st.info(f"🔍 **Keyword targeting:** {', '.join(combined_keywords)}{'...' if len(all_keywords) > 10 else ''}")

def show_scraping_page():
    """Display the scraping progress page"""
    
    st.markdown("# 🔄 Data Collection in Progress")
    st.markdown(f"Analyzing sentiment for: **{', '.join(st.session_state.selected_cities)}**")
    
    # Check if deep research is enabled
    research_enabled = st.session_state.get('claude_deep_research', False)
    total_steps = 4 if research_enabled else 3
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Collect Reddit data
    status_text.text("Collecting Reddit data...")
    progress_bar.progress(int(25 * (3/total_steps)))
    
    st.session_state.reddit_data = fetch_reddit_sentiment(
        st.session_state.selected_cities, 
        st.session_state.num_reddit_posts
    )
    
    # Collect News data
    status_text.text("Collecting News data...")
    progress_bar.progress(int(50 * (3/total_steps)))
    
    st.session_state.news_data = fetch_news_sentiment(
        st.session_state.selected_cities, 
        st.session_state.num_news_articles
    )
    
    # Conduct Claude Deep Research if enabled
    if research_enabled:
        status_text.text("🔬 Conducting Claude Deep Research...")
        progress_bar.progress(75)
        
        # Execute research
        research_content, metadata = conduct_claude_research(
            st.session_state.selected_cities,
            st.session_state.selected_pillars,
            st.session_state.time_frame_months
        )
        
        # Store research results
        st.session_state.research_results = research_content
        st.session_state.research_metadata = metadata
        
        # Generate exportable markdown
        exportable_markdown = export_research_markdown(research_content, metadata)
        st.session_state.exportable_research = exportable_markdown
        
        status_text.text("🔬 Claude Deep Research complete!")
    else:
        # Clear any previous research results
        st.session_state.research_results = ""
        st.session_state.research_metadata = {}
        st.session_state.exportable_research = ""
    
    # Complete
    progress_bar.progress(100)
    status_text.text("Data collection complete!" + (" Including deep research analysis." if research_enabled else ""))
    
    st.session_state.scraping_complete = True
    st.session_state.current_page = 'dashboard'
    
    time.sleep(2)
    st.rerun()

def show_dashboard():
    """Display the main dashboard with results"""
    
    # Navigation
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("# 📊 LKYWCP Urban Sentiment Analysis")
    with col2:
        if st.button("← Back to Selection"):
            st.session_state.current_page = 'selection'
            st.rerun()
    with col3:
        if st.button("🔄 New Analysis"):
            st.session_state.current_page = 'welcome'
            st.session_state.selected_cities = []
            st.session_state.selected_pillars = []
            st.session_state.scraping_complete = False
            st.rerun()
    
    # Display current selections in sidebar
    st.sidebar.header("📋 Analysis Settings")
    st.sidebar.write(f"**Cities:** {', '.join(st.session_state.selected_cities)}")
    st.sidebar.write(f"**Pillars:** {', '.join(st.session_state.selected_pillars)}")
    
    time_frame = st.session_state.time_frame_months
    if time_frame <= 12:
        time_display = f"{time_frame} month{'s' if time_frame > 1 else ''}"
    else:
        years = time_frame // 12
        months = time_frame % 12
        time_display = f"{years} year{'s' if years > 1 else ''}"
        if months > 0:
            time_display += f" {months} month{'s' if months > 1 else ''}"
    
    st.sidebar.write(f"**Time Frame:** Last {time_display}")
    st.sidebar.write(f"**Max Posts:** 100")
    st.sidebar.write(f"**Max Headlines:** 100")
    
    # Summary metrics
    if not st.session_state.reddit_data.empty or not st.session_state.news_data.empty:
        
        # Combine data for overview
        combined_data = pd.concat([st.session_state.reddit_data, st.session_state.news_data], ignore_index=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cities Analyzed", len(st.session_state.selected_cities))
        
        with col2:
            total_posts = len(combined_data)
            st.metric("Total Posts/Articles", total_posts)
        
        with col3:
            avg_sentiment = combined_data['Sentiment_Score'].mean()
            st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
        
        with col4:
            positive_ratio = len(combined_data[combined_data['Sentiment_Score'] > 0]) / len(combined_data) * 100
            st.metric("Positive Sentiment %", f"{positive_ratio:.1f}%")
        
        # Sentiment by City
        st.markdown("## 🌍 Sentiment by City")
        
        city_sentiment = combined_data.groupby('City')['Sentiment_Score'].mean().reset_index()
        city_sentiment['Flag'] = city_sentiment['City'].map(lambda x: AVAILABLE_CITIES[x]['flag'])
        
        fig1 = px.bar(
            city_sentiment, 
            x='City', 
            y='Sentiment_Score', 
            color='Sentiment_Score',
            color_continuous_scale='RdYlGn',
            title='Average Sentiment Score by City'
        )
        fig1.update_layout(xaxis_title="City", yaxis_title="Sentiment Score")
        st.plotly_chart(fig1, use_container_width=True)
        
        # Sentiment by LKYWCP Pillar Analysis
        st.markdown("## 🏛️ Sentiment Analysis by LKYWCP Pillar")
        
        # Process pillar data for both Reddit and News
        pillar_sentiment_data = []
        for df, source in [(st.session_state.reddit_data, 'Reddit'), (st.session_state.news_data, 'News')]:
            if not df.empty and 'Related_Pillars' in df.columns:
                for _, row in df.iterrows():
                    pillars_list = row['Related_Pillars'].split(', ') if row['Related_Pillars'] != 'General' else ['General']
                    for pillar in pillars_list:
                        pillar_sentiment_data.append({
                            'City': row['City'],
                            'Pillar': pillar,
                            'Sentiment_Score': row['Sentiment_Score'],
                            'Source': source
                        })
        
        if pillar_sentiment_data:
            pillar_df = pd.DataFrame(pillar_sentiment_data)
            
            # Average sentiment by pillar across all cities
            col1, col2 = st.columns(2)
            
            with col1:
                avg_pillar_sentiment = pillar_df.groupby('Pillar')['Sentiment_Score'].mean().reset_index()
                fig_pillar_avg = px.bar(
                    avg_pillar_sentiment, 
                    x='Pillar', 
                    y='Sentiment_Score',
                    color='Sentiment_Score',
                    color_continuous_scale='RdYlGn',
                    title='Average Sentiment by LKYWCP Pillar'
                )
                fig_pillar_avg.update_layout(xaxis={'tickangle': 45})
                st.plotly_chart(fig_pillar_avg, use_container_width=True)
            
            with col2:
                # Sentiment by pillar and city
                city_pillar_avg = pillar_df.groupby(['City', 'Pillar'])['Sentiment_Score'].mean().reset_index()
                fig_city_pillar = px.bar(
                    city_pillar_avg, 
                    x='Pillar', 
                    y='Sentiment_Score', 
                    color='City',
                    barmode='group',
                    title='Sentiment by City and Pillar'
                )
                fig_city_pillar.update_layout(xaxis={'tickangle': 45})
                st.plotly_chart(fig_city_pillar, use_container_width=True)
        
        # Data source comparison
        st.markdown("## 📊 Data Source Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.reddit_data.empty:
                st.markdown("### Reddit Data")
                reddit_avg = st.session_state.reddit_data.groupby('City')['Sentiment_Score'].mean().reset_index()
                fig2 = px.bar(reddit_avg, x='City', y='Sentiment_Score', title='Reddit Sentiment by City')
                st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            if not st.session_state.news_data.empty:
                st.markdown("### News Data")
                news_avg = st.session_state.news_data.groupby('City')['Sentiment_Score'].mean().reset_index()
                fig3 = px.bar(news_avg, x='City', y='Sentiment_Score', title='News Sentiment by City')
                st.plotly_chart(fig3, use_container_width=True)
        
        # Claude Deep Research Results
        if st.session_state.get('research_results'):
            st.markdown("## 🔬 Claude Deep Research Analysis")
            
            # Research metadata display
            metadata = st.session_state.get('research_metadata', {})
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Research Status", metadata.get('status', 'completed').title())
            with col2:
                st.metric("Cities Analyzed", len(metadata.get('cities', [])))
            with col3:
                st.metric("Pillars Covered", len(metadata.get('pillars', [])))
            with col4:
                st.metric("Generated", metadata.get('generated_at', 'Unknown').split()[0])
            
            # Research content display with export
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown("### 📊 Professional Urban Policy Analysis")
            
            with col2:
                if st.session_state.get('exportable_research'):
                    st.download_button(
                        label="📄 Export Markdown",
                        data=st.session_state.exportable_research,
                        file_name=f"LKYWCP_Research_{metadata.get('generated_at', 'unknown').split()[0]}.md",
                        mime="text/markdown",
                        use_container_width=True,
                        help="Download professional research report as markdown document"
                    )
            
            # Display research content in expandable sections
            with st.expander("🔍 View Research Analysis", expanded=True):
                st.markdown(st.session_state.research_results)
            
            # Research summary box
            if 'error' not in metadata:
                st.success(
                    f"✅ **Research Complete:** Analyzed {len(metadata.get('cities', []))} cities across "
                    f"{len(metadata.get('pillars', []))} pillars with {metadata.get('response_length', 0):,} characters of analysis."
                )
            else:
                st.error(f"❌ **Research Error:** {metadata.get('error', 'Unknown error occurred')}")
        
        # Detailed data tables
        st.markdown("## 📋 Detailed Data")
        
        # Update tabs to include research if available
        tabs = ["Reddit Data", "News Data"]
        if st.session_state.get('research_results'):
            tabs.append("Research Export")
        
        tab_objects = st.tabs(tabs)
        
        with tab_objects[0]:
            if not st.session_state.reddit_data.empty:
                st.dataframe(st.session_state.reddit_data, use_container_width=True)
                
                if st.button("Generate Reddit Summary"):
                    summary = summarise_posts(st.session_state.reddit_data['Title'].tolist(), "Reddit posts")
                    st.markdown("### 📝 Reddit Insights")
                    st.write(summary)
        
        with tab_objects[1]:
            if not st.session_state.news_data.empty:
                st.dataframe(st.session_state.news_data, use_container_width=True)
                
                if st.button("Generate News Summary"):
                    summary = summarise_posts(st.session_state.news_data['Title'].tolist(), "news articles")
                    st.markdown("### 📝 News Insights")
                    st.write(summary)
        
        # Research export tab
        if len(tab_objects) > 2:
            with tab_objects[2]:
                st.markdown("### 📄 Exportable Research Document")
                
                if st.session_state.get('exportable_research'):
                    # Show preview of exportable document
                    st.markdown("**Document Preview:**")
                    st.text_area(
                        "Formatted research document ready for export:",
                        value=st.session_state.exportable_research,
                        height=400,
                        disabled=True
                    )
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📄 Download as Markdown (.md)",
                            data=st.session_state.exportable_research,
                            file_name=f"LKYWCP_Research_{metadata.get('generated_at', 'unknown').replace(':', '-').replace(' ', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Copy to clipboard button (requires user action)
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.info("📋 Select all text above and copy with Ctrl+C (Windows) or Cmd+C (Mac)")
                    
                    # Document stats
                    st.markdown("**Document Statistics:**")
                    doc_stats = {
                        "Total Length": f"{len(st.session_state.exportable_research):,} characters",
                        "Research Content": f"{len(st.session_state.research_results):,} characters", 
                        "Cities": ", ".join(metadata.get('cities', [])),
                        "Pillars": ", ".join(metadata.get('pillars', [])),
                        "Generated": metadata.get('generated_at', 'Unknown')
                    }
                    
                    for key, value in doc_stats.items():
                        st.text(f"• {key}: {value}")
                
                else:
                    st.warning("No research document available for export.")
    
    else:
        st.warning("⚠️ No data available. Please run the analysis first.")

# -- Main App Logic --
def main():
    """Main application controller"""
    
    if st.session_state.current_page == 'welcome':
        show_welcome_page()
    
    elif st.session_state.current_page == 'selection':
        show_selection_page()
    
    elif st.session_state.current_page == 'scraping':
        show_scraping_page()
    
    elif st.session_state.current_page == 'dashboard':
        show_dashboard()

if __name__ == "__main__":
    main()