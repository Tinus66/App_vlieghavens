import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# sidebar
with st.sidebar: 
  selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"], icons=["play", "airplane", "bezier"], menu_icon="list")

# --------------------------------------------------------------------------

# Intro pagina
if selected == 'Intro':
    st.title("Case 3 Vluchten - Groep 3")

    # Korte uitleg
    st.write("""
        Tekst
    """)
  
    # Bronnen
    st.write("### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
    """)

# --------------------------------------------------------------------------

# Vluchten pagina
if selected == "Vluchten": 
  st.title("7 Vluchten (AMS - BCN)") 

  # Laad de 7 Excel-bestanden in een dictionary
  vluchten_data = {
      'vlucht 1': pd.read_excel('30Flight 1.xlsx'),
      'vlucht 2': pd.read_excel('cleaned_30Flight 2.xlsx'),
      'vlucht 3': pd.read_excel('cleaned_30Flight 3.xlsx'),
      'vlucht 4': pd.read_excel('cleaned_30Flight 4.xlsx'),
      'vlucht 5': pd.read_excel('30Flight 5.xlsx'),
      'vlucht 6': pd.read_excel('cleaned_30Flight 6.xlsx'),
      'vlucht 7': pd.read_excel('30Flight 7.xlsx')
  }

  # Dropdownmenu in Streamlit om de vlucht te selecteren
  selected_vlucht = st.selectbox("Selecteer een vlucht", options=[f'vlucht {i}' for i in range(1, 8)])

  # Haal de geselecteerde dataframe op
  df1 = vluchten_data[selected_vlucht]

  # Maak een lijst van coördinaten (Latitude, Longitude) en de hoogte
  coordinates = list(zip(df1['[3d Latitude]'], df1['[3d Longitude]'], df1['[3d Altitude Ft]']))

  # Bereken het gemiddelde van de latitude en longitude om het midden van de vlucht te vinden
  mid_lat = df1['[3d Latitude]'].mean()
  mid_lon = df1['[3d Longitude]'].mean()

  # Creëer een Folium-kaart gecentreerd op het midden van de vlucht
  m = folium.Map(location=[mid_lat, mid_lon], zoom_start=5, tiles='CartoDB positron')

  # Creëer een colormap op basis van hoogte (gebaseerd op de gevraagde kleuren)
  colormap = cm.LinearColormap(colors=['yellow', 'green', 'turquoise', 'blue', 'purple'], 
                               index=[0, 10000, 20000, 30000, 40000],
                               vmin=df1['[3d Altitude Ft]'].min(), 
                               vmax=df1['[3d Altitude Ft]'].max(),
                               caption='Hoogte in ft.')

  # Voeg de lijn toe, waarbij de kleur afhangt van de hoogte
  for i in range(1, len(coordinates)):
      start = coordinates[i-1]
      end = coordinates[i]
    
      # Kleur gebaseerd op de hoogte
      color = colormap(start[2])  # De derde waarde in 'coordinates' is de hoogte
    
      # Voeg polyline toe van het vorige naar het volgende punt met een tooltip voor extra informatie
      folium.PolyLine(
          locations=[[start[0], start[1]], [end[0], end[1]]],
          color=color, 
          weight=2.5, 
          opacity=1,
          tooltip=f"Time: {df1['Time (secs)'].iloc[i]} sec, Altitude: {df1['[3d Altitude Ft]'].iloc[i]} ft, Speed: {df1['TRUE AIRSPEED (derived)'].iloc[i]}"
      ).add_to(m)

  # Voeg een marker toe voor het vertrek vliegveld (AMS - Amsterdam)
  folium.Marker(
      location=[df1['[3d Latitude]'].iloc[0], df1['[3d Longitude]'].iloc[0]],
      popup="AMSTERDAM (AMS)",
      tooltip="AMSTERDAM (AMS)"
  ).add_to(m)

  # Voeg een marker toe voor het aankomst vliegveld (BCN - Barcelona)
  folium.Marker(
      location=[df1['[3d Latitude]'].iloc[-1], df1['[3d Longitude]'].iloc[-1]],
      popup="BARCELONA (BCN)",
      tooltip="BARCELONA (BCN)"
  ).add_to(m)

  # Toon de colormap als legenda op de kaart
  colormap.add_to(m)

  # Weergave van de kaart in Streamlit
  st_folium(m, width=700, height=600)

  # --------------------------------------

  # Voeg 'ALL' toe aan de opties voor het dropdownmenu
  selected_vlucht = st.selectbox("Selecteer een vlucht", options=['ALL'] + [f'vlucht {i}' for i in range(1, 8)])

  # Als 'ALL' is geselecteerd, combineer de data van alle vluchten en voeg een kolom toe om de vlucht te labelen
  if selected_vlucht == 'ALL':
      df_all = pd.concat([df.assign(vlucht=vlucht) for vlucht, df in vluchten_data.items()], ignore_index=True)
      df1 = df_all
  else:
      df1 = vluchten_data[selected_vlucht]
      df1['vlucht'] = selected_vlucht  # Voeg een kolom toe om de vlucht te labelen

  # Tijd omzetten van seconden naar uren
  df1['Time (hours)'] = df1['Time (secs)'] / 3600

  # Specifieke kleuren toewijzen aan elke vlucht
  kleuren_map = {
      'vlucht 1': 'red',
      'vlucht 2': 'green',
      'vlucht 3': 'blue',
      'vlucht 4': 'orange',
      'vlucht 5': 'purple',
      'vlucht 6': 'brown',
      'vlucht 7': 'pink'
  }

  # Maak de lijnplot met verschillende kleuren per vlucht
  fig = px.line(df1, x='Time (hours)', y='[3d Altitude Ft]', 
                title='Hoogte vs Tijd',  
                labels={"Time (hours)": "Tijd (uren)", "[3d Altitude Ft]": "Hoogte (ft)"},
                color='vlucht',  
                color_discrete_map=kleuren_map  
               )

  # Toon de grafiek in Streamlit
  st.plotly_chart(fig)

# --------------------------------------------------------------------------
# Vluchten pagina
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap

# Vluchten pagina
if selected == 'Luchthavens':
    st.title("Luchthavens")
    st.subheader("Top 20 luchthavens")

    # Lees de datasets in
    df = pd.read_csv("DatasetLuchthaven_murged2.csv")
    luchthaven_frequentie = pd.read_csv("luchthaven_frequentie.csv")

    # Maak een bar plot van de 20 meest voorkomende luchthavens met Plotly
    fig = px.bar(
        luchthaven_frequentie,
        x='luchthaven',
        y='aantal_vluchten',
        title='Top 20 Meest Voorkomende Luchthavens',
        labels={'luchthaven': 'luchthaven', 'aantal_vluchten': 'Aantal Vluchten'},
        color_discrete_sequence=['blue']  # Maak alle bars blauw
    )

    # Pas de layout aan voor betere weergave
    fig.update_layout(
        xaxis_title='Luchthaven',
        yaxis_title='Aantal Vluchten',
        xaxis_tickangle=-45,
    )

    # Toon de grafiek
    st.plotly_chart(fig)

    st.subheader("Luchthavens zijn optijd?")

    # Groeperen per luchthaven en status
    grouped = df.groupby(['City', 'status'])['vluchten'].sum().unstack(fill_value=0)

    # Berekenen van het percentage per luchthaven
    grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Voor plotly moeten we het DataFrame omzetten naar een lang formaat
    grouped_percentage_reset = grouped_percentage.reset_index().melt(id_vars='City', value_vars=['Te laat', 'Op tijd', 'Te vroeg'],
                                                                     var_name='status', value_name='percentage')

    # Maak een gestapelde bar plot met plotly express
    fig = px.bar(grouped_percentage_reset, x='City', y='percentage', color='status',
                 title='Percentage vluchten die te laat, op tijd of te vroeg zijn per luchthaven',
                 labels={'percentage': 'Percentage (%)', 'City': 'ICAO'},
                 color_discrete_map={'Te laat': 'red', 'Op tijd': 'green', 'Te vroeg': 'blue'})

    # Pas de lay-out van de grafiek aan
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    # Toon de plot in Streamlit
    st.plotly_chart(fig)
