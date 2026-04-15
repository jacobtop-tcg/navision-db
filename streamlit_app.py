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
    page_title="Navision Global Database v2",
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
    .verified-badge {
        background: linear-gradient(135deg, #00ff88, #00cc6a);
        color: #000;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
    }
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

@st.cache_data(ttl=60)  # Cache i 1 minut (hurtigere refresh)
def load_data(use_verified=True, version="v2-2026-04-15"):
    """Hent data fra CSV export (konsolideret database)"""
    import traceback
    import io
    
    # Hent fra GitHub (virker både lokalt og på Streamlit Cloud)
    try:
        # KONSOLIDERET DATABASE - Alle verificerede virksomheder
        if use_verified:
            # NY: all-verified.csv - 38.718 verificerede NAV-kunder
            companies_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/exports/all-verified.csv"
            summary_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/exports/summary.json"
            data_type = "KONSOLIDERET (2026-04-15)"
        else:
            # Fallback til gamle data
            companies_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/web-export/companies.csv"
            summary_url = "https://raw.githubusercontent.com/jacobtop-tcg/navision-db/master/web-export/summary.json"
            data_type = "ALLE (UKONSOLIDERET)"
        
        # Hent data med headers for at undgå rate limiting
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; NavisionBot/1.0)'}
        
        # PRØV JSON FØRST (hurtigere at parse)
        try:
            json_url = companies_url.replace('.csv', '.json')
            json_response = requests.get(json_url, headers=headers, timeout=30)
            json_response.raise_for_status()
            companies = json_response.json()
            df = pd.DataFrame(companies)
        except:
            # Fallback til CSV
            companies_response = requests.get(companies_url, headers=headers, timeout=30)
            companies_response.raise_for_status()
            df = pd.read_csv(io.StringIO(companies_response.text))
        
        # Hent summary metadata
        try:
            summary_response = requests.get(summary_url, headers=headers, timeout=30)
            summary_response.raise_for_status()
            metadata = summary_response.json()
        except:
            metadata = {'total_verified': len(df), 'exported_at': '2026-04-15'}
        
        # NORMALISER KOLONNENAVNE (vigtigt!)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Omdøb til standard navne
        df = df.rename(columns={
            'company_name': 'name',
            'company': 'name',
            'confidence_score': 'confidence',
            'confidence': 'confidence',
            'evidence_text': 'evidence',
            'evidence': 'evidence'
        })
        
        # Sikr at 'country' eksisterer
        if 'country' not in df.columns:
            if 'Country' in df.columns:
                df = df.rename(columns={'Country': 'country'})
            else:
                df['country'] = 'XX'  # Fallback
        
        return df, metadata, data_type
    except Exception as e:
        st.error(f"❌ Fejl: {type(e).__name__}")
        st.error(f"Detaljer: {str(e)}")
        st.code(traceback.format_exc())
        st.info("💡 **Fix:** Tjek at web-export/all-verified.csv findes på GitHub")
        return None, None, None

def load_compiled_knowledge():
    """Indlæs compiled knowledge fra weekly reports"""
    compiled_dir = Path(__file__).parent / 'compiled'
    weekly_dir = compiled_dir / 'weekly'
    
    knowledge_data = {
        'overview': None,
        'weekly_reports': []
    }
    
    # Indlæs overview.md
    overview_file = compiled_dir / 'overview.md'
    if overview_file.exists():
        with open(overview_file, 'r', encoding='utf-8') as f:
            knowledge_data['overview'] = f.read()
    
    # Indlæs weekly reports
    if weekly_dir.exists():
        for report_file in sorted(weekly_dir.glob('*.md'), reverse=True):
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract week number from filename
                week_num = report_file.stem
                knowledge_data['weekly_reports'].append({
                    'week': week_num,
                    'content': content,
                    'file': report_file.name
                })
    
    return knowledge_data

def show_knowledge_tab():
    """Vis Knowledge System fane"""
    st.markdown('<p class="main-header">📚 Navision Knowledge System</p>', unsafe_allow_html=True)
    st.markdown("### Compiled knowledge & weekly insights")
    st.markdown("---")
    
    knowledge = load_compiled_knowledge()
    
    # Tabs for Overview og Weekly Reports
    tab_overview, tab_weekly = st.tabs(["📊 Overview", "📅 Weekly Reports"])
    
    with tab_overview:
        if knowledge['overview']:
            st.markdown(knowledge['overview'])
        else:
            st.info("📝 Ingen overview.md fundet. Kørs `weekly-compile.sh` for at generere.")
        
        # Vis raw decisions preview
        st.markdown("### 🔍 Seneste CDQO Decisions")
        decisions_dir = Path(__file__).parent / 'raw' / 'decisions'
        if decisions_dir.exists():
            latest_decisions = sorted(decisions_dir.glob('*.jsonl'), reverse=True)[:1]
            if latest_decisions:
                try:
                    with open(latest_decisions[0], 'r', encoding='utf-8') as f:
                        decisions = [json.loads(line) for line in f if line.strip()]
                    
                    # Aggregér statistikker
                    total = len(decisions)
                    keep = sum(1 for d in decisions if d.get('decision') == 'KEEP')
                    remove = sum(1 for d in decisions if d.get('decision') == 'REMOVE')
                    upgrades = sum(1 for d in decisions if d.get('lead_type') == 'upgrade')
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Decisions", f"{total:,}")
                    col2.metric("Kept (NAV)", f"{keep:,}", delta=f"{keep/total*100:.1f}%" if total > 0 else "0%")
                    col3.metric("Removed", f"{remove:,}", delta=f"-{remove/total*100:.1f}%" if total > 0 else "0%")
                    col4.metric("Upgrade Leads ⭐", f"{upgrades:,}")
                    
                    # Lead type fordeling
                    st.subheader("🎯 Lead Type Fordeling")
                    lead_types = {}
                    for d in decisions:
                        lt = d.get('lead_type', 'unknown')
                        lead_types[lt] = lead_types.get(lt, 0) + 1
                    
                    fig = px.pie(
                        values=list(lead_types.values()),
                        names=list(lead_types.keys()),
                        title="CDQO Lead Types"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 🔥 NYE ANALYTICS
                    
                    # 1. Confidence Distribution
                    st.subheader("📊 Confidence Distribution")
                    confidences = [d.get('confidence', 0) for d in decisions if d.get('confidence')]
                    if confidences:
                        conf_hist = px.histogram(
                            x=confidences,
                            nbins=20,
                            labels={'x': 'Confidence Score', 'y': 'Antal'},
                            title='Confidence Score Fordeling',
                            color_discrete_sequence=['#00d4ff']
                        )
                        conf_hist.update_layout(showlegend=False)
                        st.plotly_chart(conf_hist, use_container_width=True)
                        
                        # Confidence stats
                        col_conf1, col_conf2, col_conf3 = st.columns(3)
                        col_conf1.metric("Avg Confidence", f"{sum(confidences)/len(confidences)*100:.1f}%")
                        col_conf2.metric("Min Confidence", f"{min(confidences)*100:.1f}%")
                        col_conf3.metric("Max Confidence", f"{max(confidences)*100:.1f}%")
                    
                    # 2. Daily Decision Trend
                    st.subheader("📈 Daily Decision Trend")
                    daily_stats = {}
                    for d in decisions:
                        date = d.get('timestamp', '')[:10]  # YYYY-MM-DD
                        if date not in daily_stats:
                            daily_stats[date] = {'total': 0, 'keep': 0, 'remove': 0, 'upgrade': 0}
                        daily_stats[date]['total'] += 1
                        if d.get('decision') == 'KEEP':
                            daily_stats[date]['keep'] += 1
                        elif d.get('decision') == 'REMOVE':
                            daily_stats[date]['remove'] += 1
                        if d.get('lead_type') == 'upgrade':
                            daily_stats[date]['upgrade'] += 1
                    
                    if daily_stats:
                        sorted_dates = sorted(daily_stats.keys())
                        trend_df = pd.DataFrame([
                            {
                                'date': date,
                                'total': daily_stats[date]['total'],
                                'keep': daily_stats[date]['keep'],
                                'remove': daily_stats[date]['remove'],
                                'upgrade': daily_stats[date]['upgrade']
                            }
                            for date in sorted_dates
                        ])
                        
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=trend_df['date'],
                            y=trend_df['total'],
                            mode='lines+markers',
                            name='Total',
                            line=dict(color='#00d4ff', width=3)
                        ))
                        fig_trend.add_trace(go.Scatter(
                            x=trend_df['date'],
                            y=trend_df['keep'],
                            mode='lines+markers',
                            name='Kept (NAV)',
                            line=dict(color='#00ff88', width=2)
                        ))
                        fig_trend.add_trace(go.Scatter(
                            x=trend_df['date'],
                            y=trend_df['remove'],
                            mode='lines+markers',
                            name='Removed',
                            line=dict(color='#ff4444', width=2, dash='dash')
                        ))
                        fig_trend.update_layout(
                            title='Daily Decisions',
                            xaxis_title='Dato',
                            yaxis_title='Antal',
                            hovermode='x unified',
                            showlegend=True,
                            height=400
                        )
                        st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # 3. Top Removed Companies
                    removed_decisions = [d for d in decisions if d.get('decision') == 'REMOVE']
                    if removed_decisions:
                        st.subheader("❌ Top Removed Companies")
                        removed_by_reason = {}
                        for d in removed_decisions:
                            reason = d.get('lead_type', 'unknown').upper()
                            if reason not in removed_by_reason:
                                removed_by_reason[reason] = []
                            removed_by_reason[reason].append(d)
                        
                        for reason, companies in sorted(removed_by_reason.items(), key=lambda x: -len(x[1])):
                            with st.expander(f"{reason} ({len(companies)} virksomheder)"):
                                for c in companies[:10]:  # Vis første 10
                                    st.write(f"- **{c.get('company_name', 'Unknown')}** ({c.get('country', 'XX')})")
                                    if c.get('evidence_text'):
                                        st.caption(f"Evidence: {c['evidence_text'][:100]}...")
                                if len(companies) > 10:
                                    st.write(f"... og {len(companies) - 10} flere")
                    
                    # 4. Source Quality Comparison
                    st.subheader("📊 Source Quality Comparison")
                    source_stats = {}
                    for d in decisions:
                        source = d.get('source_url', 'unknown')
                        if source:
                            # Ekstraher domain
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(source).netloc.replace('www.', '')
                            except:
                                domain = source
                            
                            if domain not in source_stats:
                                source_stats[domain] = {'total': 0, 'keep': 0, 'avg_conf': 0, 'conf_sum': 0}
                            source_stats[domain]['total'] += 1
                            if d.get('decision') == 'KEEP':
                                source_stats[domain]['keep'] += 1
                            conf = d.get('confidence', 0)
                            source_stats[domain]['conf_sum'] += conf
                    
                    # Beregn averages og sorter
                    source_data = []
                    for domain, stats in source_stats.items():
                        if stats['total'] >= 5:  # Kun kilder med mindst 5 decisions
                            stats['keep_rate'] = stats['keep'] / stats['total'] * 100
                            stats['avg_conf'] = stats['conf_sum'] / stats['total']
                            source_data.append({
                                'source': domain,
                                'total': stats['total'],
                                'keep_rate': stats['keep_rate'],
                                'avg_conf': stats['avg_conf'] * 100
                            })
                    
                    if source_data:
                        source_df = pd.DataFrame(source_data).sort_values('total', ascending=False).head(15)
                        
                        col_src1, col_src2 = st.columns(2)
                        with col_src1:
                            fig_src_keep = px.bar(
                                source_df,
                                x='source',
                                y='keep_rate',
                                title='Keep Rate by Source (%)',
                                labels={'source': 'Kilde', 'keep_rate': 'Keep Rate %'},
                                color='keep_rate',
                                color_continuous_scale='RdYlGn'
                            )
                            fig_src_keep.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
                            st.plotly_chart(fig_src_keep, use_container_width=True)
                        
                        with col_src2:
                            fig_src_conf = px.bar(
                                source_df,
                                x='source',
                                y='avg_conf',
                                title='Avg Confidence by Source (%)',
                                labels={'source': 'Kilde', 'avg_conf': 'Avg Confidence %'},
                                color='avg_conf',
                                color_continuous_scale='Blues'
                            )
                            fig_src_conf.update_layout(showlegend=False, xaxis_tickangle=-45, height=400)
                            st.plotly_chart(fig_src_conf, use_container_width=True)
                        
                        # Source data table
                        st.subheader("📋 Source Data (Top 15)")
                        st.dataframe(
                            source_df.round(1),
                            use_container_width=True,
                            height=300
                        )
                    
                except Exception as e:
                    st.error(f"Kunne ikke indlæse decisions: {e}")
                    st.exception(e)
    
    with tab_weekly:
        if knowledge['weekly_reports']:
            # Vælg uge
            report_options = {r['week']: r for r in knowledge['weekly_reports']}
            selected_week = st.selectbox(
                "Vælg uge:",
                options=list(report_options.keys()),
                format_func=lambda x: f"{x}"
            )
            
            if selected_week and selected_week in report_options:
                report = report_options[selected_week]
                st.markdown(report['content'])
        else:
            st.info("📝 Ingen weekly reports endnu. Køres hver søndag automatisk.")
            st.markdown("""
            **Næste kørsel:** Søndag kl. 09:00 UTC
            
            **Manuel kørsel:**
            ```bash
            cd navision-db && bash scripts/weekly-compile.sh
            ```
            """)

def main():
    # Header
    st.markdown('<p class="main-header">🌍 Navision Global Database</p>', unsafe_allow_html=True)
    st.markdown("### Live oversigt over virksomheder der bruger Microsoft Dynamics NAV/Navision")
    st.markdown("---")
    
    # Tab selector
    tab_db, tab_knowledge = st.tabs(["🗄️ Database", "📚 Knowledge System"])
    
    with tab_db:
        # Data source selector
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💎 **VERIFIED:** 100% har konkret evidence + direkte kilde-link")
        with col2:
            use_verified = st.checkbox("✅ Kun VERIFIED data (anbefalet)", value=True)
        
        # Hent data
        df, metadata, data_type = load_data(use_verified=use_verified, version="v2-2026-04-15")
        
        if df is None:
            st.error("Kunne ikke indlæse data. Tjek internetforbindelsen.")
            st.stop()
        
        # Data source badge
        if use_verified:
            total = metadata.get('total_verified', len(df))
            st.markdown(f'<span class="verified-badge">🎯 VERIFIED DATA: {total:,} virksomheder</span>', unsafe_allow_html=True)
            st.caption("Alle har: konkret evidence/bevis + direkte link til kilde + høj kvalitet (CDQO verificeret)")
        else:
            total = metadata.get('total_companies', len(df))
            st.markdown(f"📊 ALLE DATA: {total:,} virksomheder")
        
        st.markdown("---")
        
        # Auto-refresh knap
        if st.button('🔄 Opdater data'):
            st.cache_data.clear()
            st.rerun()
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = metadata.get('total_verified', len(df))
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total:,}</div>
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
            default=all_countries,
            help="Filtrer efter land"
        )
        
        # Branche filter
        all_industries = sorted(df['industry'].dropna().unique())
        selected_industries = st.sidebar.multiselect(
            "Vælg brancher",
            all_industries,
            default=all_industries,
            help="Filtrer efter branche"
        )
        
        # Kilde filter
        all_sources = sorted(df['source'].unique())
        selected_sources = st.sidebar.multiselect(
            "Vælg kilder",
            all_sources,
            default=all_sources,
            help="Filtrer efter kilde"
        )
        
        # Stjerner filter
        min_stars = st.sidebar.slider("Min. stjerner", 1, 5, 1)
        
        # Søgning
        search_query = st.sidebar.text_input("🔍 Søg...", help="Søg i navn, branche eller evidence")
        
        # Appler filtre
        filtered_df = df.copy()
        
        if selected_countries:
            filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
        if selected_industries:
            filtered_df = filtered_df[filtered_df['industry'].isin(selected_industries)]
        if selected_sources:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_sources)]
        if min_stars > 1:
            filtered_df = filtered_df[filtered_df['confidence'] >= min_stars]
        
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
            
            # Tilføj links kolonner
            display_df = filtered_df.copy()
            
            # Vis tabel med pagination og links
            st.dataframe(
                display_df[['name', 'country', 'industry', 'confidence', 'source', 'website', 'source_url', 'evidence']],
                use_container_width=True,
                height=600,
                column_config={
                    "name": st.column_config.TextColumn("Virksomhed", width="medium"),
                    "country": st.column_config.TextColumn("Land", help="Landekode"),
                    "industry": st.column_config.TextColumn("Branche"),
                    "confidence": st.column_config.NumberColumn("Kvalitet", help="1-5 stjerner"),
                    "source": st.column_config.TextColumn("Kilde"),
                    "website": st.column_config.LinkColumn("Website"),
                    "source_url": st.column_config.LinkColumn("Kilde URL", width="small"),
                    "evidence": st.column_config.TextColumn("Bevis", width="large")
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
            <p>🔄 Data opdateres automatisk hver gang du pusher til GitHub</p>
            <p>Sidst opdateret: {metadata.get('last_updated', 'Ukendt')}</p>
            {f'<p>🎯 KVALITET: 100% har evidence + direkte kilde-link</p>' if use_verified else ''}
        </div>
        """, unsafe_allow_html=True)
    
    with tab_knowledge:
        show_knowledge_tab()

if __name__ == "__main__":
    main()
