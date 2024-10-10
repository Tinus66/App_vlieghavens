import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap
import plotly.graph_objects as go

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# Sidebar met menu-opties
with st.sidebar: 
    selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], icons=["play", "airplane", "bezier"], menu_icon="list")

# --------------------------------------------------------------------------

# Intro pagina
if selected == 'Intro':
    st.title("Case 3 Vluchten - Groep 3")
    st.write("Tekst over de case...")
    st.write("### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
    """)

# --------------------------------------------------------------------------

# Vluchten pagina
if selected == "Vluchten": 
    st.title("7 Vluchten (AMS - BCN)") 

    @st.cache_data
    def load_vlucht_data():
        return {
            'vlucht 1': pd.read_excel('30Flight 1.xlsx'),
            'vlucht 2': pd.read_excel('cleaned_30Flight 2.xlsx'),
            'vlucht 3': pd.read_excel('cleaned_30Flight 3.xlsx'),
            'vlucht 4': pd.read_excel('cleaned_30Flight 4.xlsx'),
            'vlucht 5': pd.read_excel('30Flight 5.xlsx'),
            'vlucht 6': pd.read_excel('cleaned_30Flight 6.xlsx'),
            'vlucht 7': pd.read_excel('30Flight 7.xlsx')
        }

    vluchten_data = load_vlucht_data()

    selected_vlucht = st.selectbox("Selecteer een vlucht", options=[f'vlucht {i}' for i in range(1, 8)])
    df1 = vluchten_data[selected_vlucht]

    # Coördinaten lijst opstellen
    coordinates = list(zip(df1['[3d Latitude]'], df1['[3d Longitude]'], df1['[3d Altitude Ft]']))

    # Bereken het gemiddelde voor centrering van de kaart
    mid_lat = df1['[3d Latitude]'].mean()
    mid_lon = df1['[3d Longitude]'].mean()

    # Folium-kaart aanmaken
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=5, tiles='CartoDB positron')

    colormap = cm.LinearColormap(colors=['yellow', 'green', 'turquoise', 'blue', 'purple'], 
                                 index=[0, 10000, 20000, 30000, 40000],
                                 vmin=df1['[3d Altitude Ft]'].min(), 
                                 vmax=df1['[3d Altitude Ft]'].max(),
                                 caption='Hoogte in ft.')

    # Voeg lijnen toe aan de kaart
    for i in range(1, len(coordinates)):
        start = coordinates[i-1]
        end = coordinates[i]
        color = colormap(start[2])
    
        folium.PolyLine(
            locations=[[start[0], start[1]], [end[0], end[1]]],
            color=color, 
            weight=2.5, 
            opacity=1,
            tooltip=f"Time: {df1['Time (secs)'].iloc[i]} sec, Altitude: {df1['[3d Altitude Ft]'].iloc[i]} ft, Speed: {df1['TRUE AIRSPEED (derived)'].iloc[i]}"
        ).add_to(m)

    folium.Marker(
        location=[df1['[3d Latitude]'].iloc[0], df1['[3d Longitude]'].iloc[0]],
        popup="AMSTERDAM (AMS)",
        tooltip="AMSTERDAM (AMS)"
    ).add_to(m)

    folium.Marker(
        location=[df1['[3d Latitude]'].iloc[-1], df1['[3d Longitude]'].iloc[-1]],
        popup="BARCELONA (BCN)",
        tooltip="BARCELONA (BCN)"
    ).add_to(m)

    colormap.add_to(m)

    st_folium(m, width=700, height=600)

    # Hoogte vs tijd grafiek
    df1['Time (hours)'] = df1['Time (secs)'] / 3600
    kleuren_map = {'vlucht 1': 'red', 'vlucht 2': 'green', 'vlucht 3': 'blue', 'vlucht 4': 'orange', 'vlucht 5': 'purple', 'vlucht 6': 'brown', 'vlucht 7': 'pink'}

    fig = px.line(df1, x='Time (hours)', y='[3d Altitude Ft]', 
                  title='Hoogte vs Tijd',  
                  labels={"Time (hours)": "Tijd (uren)", "[3d Altitude Ft]": "Hoogte (ft)"},
                  color='vlucht',  
                  color_discrete_map=kleuren_map  
                 )
    st.plotly_chart(fig)

# --------------------------------------------------------------------------

if selected == 'Luchthavens':
    st.title("Luchthavens")
    st.subheader("Top 20 luchthavens")

    @st.cache_data
    def load_luchthaven_data():
        df = pd.read_csv("DatasetLuchthaven_murged2.csv")
        luchthaven_frequentie = pd.read_csv("luchthaven_frequentie.csv")
        return df, luchthaven_frequentie

    df, luchthaven_frequentie = load_luchthaven_data()

    fig = px.bar(luchthaven_frequentie, x='luchthaven', y='aantal_vluchten',
                 title='Top 20 Meest Voorkomende Luchthavens', color_discrete_sequence=['blue'])
    fig.update_layout(xaxis_title='Luchthaven', yaxis_title='Aantal Vluchten', xaxis_tickangle=-45)
    st.plotly_chart(fig)

    st.subheader("Luchthavens op tijd?")
    grouped = df.groupby(['City', 'status']).size().unstack(fill_value=0)
    grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100
    grouped_percentage_reset = grouped_percentage.reset_index().melt(id_vars='City', value_vars=['Te laat', 'Op tijd', 'Te vroeg'],
                                                                     var_name='status', value_name='percentage')

    fig = px.bar(grouped_percentage_reset, x='City', y='percentage', color='status',
                 title='Percentage vluchten per status per luchthaven',
                 labels={'percentage': 'Percentage (%)', 'City': 'ICAO'},
                 color_discrete_map={'Te laat': 'red', 'Op tijd': 'green', 'Te vroeg': 'blue'})
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig)
