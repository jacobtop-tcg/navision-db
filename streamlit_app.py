#!/usr/bin/env python3
"""
Navision Global Database - Live Dashboard
Streamlit app til at browse, søge og filtrere Navision virksomheder
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
import requests

# Side config
st.set_page_config(
    page_title="Navision Global Database",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .stat-card {
        background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,153,255,0.05));
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0,212,255,0.2);
        text-align: center;
    }
    .stat-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #00d4ff;
    }
    .stat-label {
        color: #888;
        font-size: 0.9em;
        margin-top: 5px;
    }
    .quality-high { color: #00ff88; }
    .quality-med { color: #ffaa00; }
    .quality-low { color: #ff4444; }
</style>
""", unsafe_allow_html=True)

# Flag emoji mapping
FLAG_EMOJIS = {
    'DK': '🇩🇰', 'SE': '🇸🇪', 'NO': '🇳🇴', 'DE': '🇩🇪', 'US': '🇺🇸',
    'NL': '🇳🇱', 'UK': '🇬🇧', 'FR': '🇫🇷', 'BE': '🇧🇪', 'PL': '🇵🇱',
    'ES': '🇪🇸', 'IT': '🇮🇹', 'FI': '🇫🇮', 'GB': '🇬🇧', 'IN': '🇮🇳',
    'CA': '🇨🇦', 'AU': '🇦🇺', 'JP': '🇯🇵', 'BR': '🇧🇷', 'XX': '🌍'
}

def get_flag(country_code):
    return FLAG_EMOJIS.get(country_code.upper(), '🌍')

@st.cache_data(ttl=300)  # Cache i 5 minutter
def load_data():
    """Hent data fra JSON export"""
    # Hent fra GitHub (virker både lokalt og på Streamlit Cloud)
    try:
        companies_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/web-export/companies.json"
        meta_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/web-export/metadata.json"
        
        companies = requests.get(companies_url, timeout=30).json()
        metadata = requests.get(meta_url, timeout=30).json()
        return pd.DataFrame(companies), metadata
    except Exception as e:
        st.error(f"Fejl ved indlæsning af data: {e}")
        return None, None

def main():
    # Header
    st.markdown('<p class="main-header">🌍 Navision Global Database</p>', unsafe_allow_html=True)
    st.markdown("### Live oversigt over virksomheder der bruger Microsoft Dynamics NAV/Navision")
    st.markdown("---")
    
    # Hent data
    df, metadata = load_data()
    
    if df is None:
        st.error("Kunne ikke indlæse data. Sørg for at export scriptet er kørt.")
        st.stop()
    
    # Auto-refresh knap
    if st.button('🔄 Opdater data'):
        st.cache_data.clear()
        st.rerun()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{metadata['total_companies']:,}</div>
            <div class="stat-label">Virksomheder</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_quality = len(df[df['confidence'] >= 4])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number quality-high">{high_quality:,}</div>
            <div class="stat-label">Høj Kvalitet (4-5★)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        countries = df['country'].nunique()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{countries}</div>
            <div class="stat-label">Lande</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(df['source'].unique())}</div>
            <div class="stat-label">Kilder</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar filtre
    st.sidebar.header("🔍 Filtre")
    
    # Land filter
    all_countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Vælg lande",
        all_countries,
        default=all_countries[:10],  # Default top 10
        format_func=lambda x: f"{get_flag(x)} {x}"
    )
    
    # Confidence filter
    confidence_filter = st.sidebar.slider(
        "Minimum kvalitet (stjerner)",
        min_value=1,
        max_value=5,
        value=3
    )
    
    # Kilde filter
    all_sources = sorted(df['source'].unique())
    selected_sources = st.sidebar.multiselect(
        "Vælg kilder",
        all_sources,
        default=all_sources
    )
    
    # Søgning
    search_query = st.sidebar.text_input("🔎 Søg i virksomheder", "")
    
    # Anvend filtre
    filtered_df = df.copy()
    
    if selected_countries:
        filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
    
    filtered_df = filtered_df[filtered_df['confidence'] >= confidence_filter]
    
    if selected_sources:
        filtered_df = filtered_df[filtered_df['source'].isin(selected_sources)]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_query, case=False, na=False) |
            filtered_df['industry'].str.contains(search_query, case=False, na=False) |
            filtered_df['evidence'].str.contains(search_query, case=False, na=False)
        ]
    
    # Vis filtre resultat
    st.sidebar.markdown(f"**Resultater:** {len(filtered_df):,} virksomheder")
    
    # Download knap
    csv = filtered_df.to_csv(index=False, encoding='utf-8')
    st.sidebar.download_button(
        label="📥 Download som CSV",
        data=csv,
        file_name=f"navision_companies_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
    
    # Main content - to kolonner
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📋 Virksomhedsliste")
        
        # Vis tabel med pagination
        st.dataframe(
            filtered_df[['name', 'country', 'industry', 'confidence', 'source', 'evidence']],
            use_container_width=True,
            height=600,
            column_config={
                "name": "Virksomhed",
                "country": st.column_config.TextColumn("Land", help="Landekode"),
                "industry": "Branche",
                "confidence": st.column_config.NumberColumn("Kvalitet", help="1-5 stjerner"),
                "source": "Kilde",
                "evidence": st.column_config.TextColumn("Bevis", width="medium")
            }
        )
    
    with col_right:
        # Top lande chart
        st.subheader("🌍 Top Lande")
        country_counts = filtered_df['country'].value_counts().head(10)
        
        country_labels = [f"{get_flag(c)} {c}: {count:,}" for c, count in country_counts.items()]
        
        fig = go.Figure(go.Pie(
            labels=country_labels,
            values=country_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Blues)
        ))
        fig.update_layout(height=400, showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # Kilde fordeling
        st.subheader("📊 Kilder")
        source_counts = filtered_df['source'].value_counts().head(8)
        
        fig2 = px.bar(
            y=source_counts.index,
            x=source_counts.values,
            orientation='h',
            color=source_counts.values,
            color_continuous_scale='Blues'
        )
        fig2.update_layout(height=300, showlegend=False, margin=dict(t=20, b=40, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)
    
    # Kvalitetsfordeling
    st.markdown("---")
    st.subheader("⭐ Kvalitetsfordeling")
    
    conf_counts = filtered_df['confidence'].value_counts().sort_index()
    conf_labels = [f"{'⭐' * int(c)} ({count:,})" for c, count in conf_counts.items()]
    
    fig3 = px.bar(
        x=[str(c) for c in conf_counts.index],
        y=conf_counts.values,
        labels={'x': 'Stjerner', 'y': 'Antal virksomheder'},
        color=conf_counts.values,
        color_continuous_scale='RdYlGn'
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666;">
        <p>🔄 Data opdateres automatisk hvert 5. minut</p>
        <p>Sidst opdateret: {metadata.get('last_updated', 'Ukendt')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
