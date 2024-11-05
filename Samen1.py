import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import folium
import branca.colormap as cm
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from folium.plugins import HeatMap

st.set_page_config(page_title='Eindpresentatie visualisatie ', page_icon='✈️')

# Sidebar met verbeterde menu-opties
with st.sidebar: 
    selected = option_menu(
        menu_title="Menu", 
        options=["Intro", "Vluchten", "Luchthavens"], 
        icons=["play", "airplane", "bezier"], 
        menu_icon="list"
    )
#---------------------------------------------------------------------------
# Functie voor laden van vluchten data
@st.cache_data
def load_vluchten_data():
    vluchten_data = {
        f'vlucht {i}': pd.read_excel(f'cleaned_30Flight {i}.xlsx') 
        for i in range(1, 8)
    }
    return vluchten_data

# Functie voor het tekenen van de kaart
def draw_flight_map(df):
    mid_lat, mid_lon = df['[3d Latitude]'].mean(), df['[3d Longitude]'].mean()
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=5, tiles='CartoDB positron')
    colormap = cm.LinearColormap(
        colors=['yellow', 'green', 'turquoise', 'blue', 'purple'], 
        index=[0, 10000, 20000, 30000, 40000],
        vmin=df['[3d Altitude Ft]'].min(), 
        vmax=df['[3d Altitude Ft]'].max(),
        caption='Hoogte in ft.'
    )

    coordinates = list(zip(df['[3d Latitude]'], df['[3d Longitude]'], df['[3d Altitude Ft]']))
    for i in range(1, len(coordinates)):
        start, end = coordinates[i-1], coordinates[i]
        color = colormap(start[2])
        folium.PolyLine(
            locations=[[start[0], start[1]], [end[0], end[1]]],
            color=color, weight=2.5, opacity=1,
            tooltip=f"Time: {df['Time (secs)'].iloc[i]} sec, Altitude: {df['[3d Altitude Ft]'].iloc[i]} ft, Speed: {df['TRUE AIRSPEED (derived)'].iloc[i]}"
        ).add_to(m)

    folium.Marker(location=[df['[3d Latitude]'].iloc[0], df['[3d Longitude]'].iloc[0]],
                  popup="AMSTERDAM (AMS)", tooltip="AMSTERDAM (AMS)").add_to(m)
    folium.Marker(location=[df['[3d Latitude]'].iloc[-1], df['[3d Longitude]'].iloc[-1]],
                  popup="BARCELONA (BCN)", tooltip="BARCELONA (BCN)").add_to(m)
    colormap.add_to(m)
    return m

# --------------------------------------------------------------------------

# INTRO pagina
if selected == 'Intro':
    st.title("Eindpresnetatie visualisatie")

    # Korte uitleg
    st.write("""
        Eindpresentaie, laten zien van de vooruitgang in onze visualisatie kunsten. Wij hebben gekkozen voor het verbetren van case 3 de vluchten data. 
    """)
    st.write("Sophia Olijhoek en Martijn de Jong")
    # Bronnen
    st.write("### Gebruikte Bronnen:")
    st.write("""
        - [Youtube filmpje](https://www.youtube.com/watch?v=hEPoto5xp3k)
        - [Streamlit documentatie](https://docs.streamlit.io/)
    """)
    st.image('intro.png', caption='Data science', use_column_width=True)
# --------------------------------------------------------------------------

# VLUCHTEN pagina
elif selected == "Vluchten": 
    st.title("7 Vluchten (AMS - BCN)") 

    vluchten_data = load_vluchten_data()
    selected_vlucht = st.selectbox("Selecteer een vlucht", options=['ALL'] + [f'vlucht {i}' for i in range(1, 8)])

    if selected_vlucht == 'ALL':
        df1 = pd.concat([df.assign(vlucht=vlucht) for vlucht, df in vluchten_data.items()], ignore_index=True)
    else:
        df1 = vluchten_data[selected_vlucht]
        df1['vlucht'] = selected_vlucht

    # Streamlit kaart weergave met uitleg
    if selected_vlucht != 'ALL':
        st.write("Hieronder zie je de kaart voor de geselecteerde vlucht.")
        map_ = draw_flight_map(df1)
        st_folium(map_, width=700, height=600)
    
    # Grafiek Hoogte vs Tijd met verbeterde kleuren en layout
    df1['Time (hours)'] = df1['Time (secs)'] / 3600
    kleuren_map = {f'vlucht {i}': color for i, color in enumerate(px.colors.qualitative.Plotly, 1)}
    fig = px.line(
        df1, x='Time (hours)', y='[3d Altitude Ft]', title='Hoogte vs Tijd',
        labels={"Time (hours)": "Tijd (uren)", "[3d Altitude Ft]": "Hoogte (ft)"}, color='vlucht', color_discrete_map=kleuren_map
    )
    st.plotly_chart(fig)
#-----------------------------------------------------------------------------------------------    
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


# Zorg ervoor dat je DataFrame 'df' gedefinieerd is en klaar is voor gebruik


# Zorg ervoor dat je DataFrame 'df' gedefinieerd is en dat het kolommen 'geplande_vertrek' en 'werkelijke_vertrek' bevat

# Voorbeeld van DataFrame opbouw
# df = pd.DataFrame({
#     'City': ['Amsterdam', 'Amsterdam', 'Rotterdam', 'Rotterdam'],
#     'status': ['Te laat', 'Op tijd', 'Te vroeg', 'Te laat'],
#     'geplande_vertrek': [pd.Timestamp('2024-11-06 10:00'), pd.Timestamp('2024-11-06 10:00'), pd.Timestamp('2024-11-06 11:00'), pd.Timestamp('2024-11-06 11:00')],
#     'werkelijke_vertrek': [pd.Timestamp('2024-11-06 10:05'), pd.Timestamp('2024-11-06 10:00'), pd.Timestamp('2024-11-06 10:55'), pd.Timestamp('2024-11-06 11:10')],
# })

# Bereken de vertraging in minuten
    df['vertraging_minuten'] = (df['verschil_minuten'])

# Bepaal de status op basis van de vertraging
    df['status'] = pd.cut(df['vertraging_minuten'],
                      bins=[-float('inf'), 0, 1, float('inf')],
                      labels=['Op tijd', 'Te laat', 'Te vroeg'])

    st.subheader("Luchthavens zijn optijd?")

# Groeperen per luchthaven en status
    grouped = df.groupby(['City', 'status']).size().unstack(fill_value=0)

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

# Voeg een checkbox toe voor de extra functionaliteiten
    show_extra_features = st.checkbox("Toon extra details")

    if show_extra_features:
    # Voeg percentages toe als tekst op de balken
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='inside', insidetextanchor='middle')

    # Voeg een slider toe om het drempelpercentage voor op tijd aan te passen
        tijd_drempel = st.slider("Stel het aantal minuten in voor een vlucht om als op tijd te worden beschouwd:", 0, 60, 5)

    # Bepaal de nieuwe status op basis van de geselecteerde tijdsgrens
        df['status'] = pd.cut(df['vertraging_minuten'],
                              bins=[-float('inf'), 0, tijd_drempel, float('inf')],
                              labels=['Op tijd', 'Te laat', 'Te vroeg'])

    # Groeperen per luchthaven en status
        grouped = df.groupby(['City', 'status']).size().unstack(fill_value=0)

    # Berekenen van het percentage per luchthaven
        grouped_percentage = grouped.div(grouped.sum(axis=1), axis=0) * 100

    # Voor plotly moeten we het DataFrame omzetten naar een lang formaat
        grouped_percentage_reset = grouped_percentage.reset_index().melt(id_vars='City', value_vars=['Te laat', 'Op tijd', 'Te vroeg'],
                                                                         var_name='status', value_name='percentage')

    # Maak een nieuwe gestapelde bar plot met de aangepaste drempel
        fig_drempel = px.bar(grouped_percentage_reset, x='City', y='percentage', color='status',
                             title=f'Percentage vluchten die te laat, op tijd of te vroeg zijn per luchthaven (drempel: {tijd_drempel} minuten)',
                             labels={'percentage': 'Percentage (%)', 'City': 'ICAO'},
                             color_discrete_map={'Te laat': 'red', 'Op tijd': 'green', 'Te vroeg': 'blue'})

    # Pas de lay-out aan van de nieuwe grafiek
        fig_drempel.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    # Toon de aangepaste grafiek in Streamlit
        st.plotly_chart(fig_drempel)


# Gemiddelde vertraging per luchthaven en jaar berekenen
    gemiddelde_vertraging = df.groupby(['City', 'Jaartal'])['verschil_minuten'].mean().reset_index()

# Aantal vluchten per luchthaven en jaar tellen
    aantal_vluchten = df.groupby(['City', 'Jaartal']).size().reset_index(name='aantal_vluchten')

# De resultaten samenvoegen
    if not gemiddelde_vertraging.empty and not aantal_vluchten.empty:
        gemiddelde_vertraging = gemiddelde_vertraging.merge(aantal_vluchten, on=['City', 'Jaartal'])

# Split de data op basis van jaartal
    df_2019 = gemiddelde_vertraging[gemiddelde_vertraging['Jaartal'] == 2019]
    df_2020 = gemiddelde_vertraging[gemiddelde_vertraging['Jaartal'] == 2020]

# Bepaal de maximale en minimale waarde voor de y-as
    max_vertraging = max(gemiddelde_vertraging['verschil_minuten'].max(), 0)
    min_vertraging = min(gemiddelde_vertraging['verschil_minuten'].min(), 0)

# Dropdown menu voor het jaar
    jaartal = st.selectbox("Kies een jaar:", [2019, 2020])

# Conditie voor het maken van de grafiek op basis van het gekozen jaar
    if jaartal == 2019:
        # Bar plot voor 2019
        fig_jaartal = px.bar(
            df_2019,
            x='City',
            y='verschil_minuten',
            title='Gemiddelde vertraging van vluchten per luchthaven in 2019 (in minuten)',
            labels={'City': 'ICAO', 'verschil_minuten': 'Gemiddelde vertraging (minuten)'},
            color='verschil_minuten',
            text='aantal_vluchten',  # Aantal vluchten als tekstlabel
            color_continuous_scale=px.colors.sequential.Viridis
        )

    # Y-as instellen voor 2019
        fig_jaartal.update_yaxes(range=[min_vertraging, max_vertraging])
        st.plotly_chart(fig_jaartal)

    elif jaartal == 2020:
    # Bar plot voor 2020
        fig_jaartal = px.bar(
            df_2020,
            x='City',
            y='verschil_minuten',
            title='Gemiddelde vertraging van vluchten per luchthaven in 2020 (in minuten)',
            labels={'City': 'Luchthaven', 'verschil_minuten': 'Gemiddelde vertraging (minuten)'},
            color='verschil_minuten',
            text='aantal_vluchten',  # Aantal vluchten als tekstlabel
            color_continuous_scale=px.colors.sequential.Viridis
        )

    # Y-as instellen voor 2020
        fig_jaartal.update_yaxes(range=[min_vertraging, max_vertraging])
        st.plotly_chart(fig_jaartal)

# Subheader voor drukte op luchthavens
    st.subheader("Drukte op luchthavens in de tijd")
# Bereken het aantal vliegtuigen op elke luchthaven op een bepaald moment
    def calculate_aircraft_on_airport(selected_time):
    # Zorg ervoor dat de STD-kolom correct is geformatteerd als datetime
      df['STD'] = pd.to_datetime(df['STD'], errors='coerce')
    
    # Zorg ervoor dat selected_time een pd.Timestamp is
      if not isinstance(selected_time, pd.Timestamp):
          selected_time = pd.to_datetime(selected_time)
    
    # Filter de dataframe op basis van landingen en vertrektijden
      landed = df[(df['LSV'] == 'L') & (df['STD'].notna()) & (df['STD'] <= selected_time)]
      departed = df[(df['LSV'] == 'S') & (df['STD'].notna()) & (df['STD'] <= selected_time)]
    
    # Tel het aantal vliegtuigen per luchthaven
      landed_count = landed.groupby('City')['TAR'].nunique().reset_index(name='Aantal_vliegtuigen')
      departed_count = departed.groupby('City')['TAR'].nunique().reset_index(name='Aantal_vertrokken')

    # Bereken het aantal vliegtuigen dat nog op de luchthaven is
      airport_traffic = pd.merge(landed_count, departed_count, on='City', how='left').fillna(0)
      airport_traffic['Aantal_vliegtuigen'] = airport_traffic['Aantal_vliegtuigen'] - airport_traffic['Aantal_vertrokken']

      return airport_traffic



# Streamlit interface
    st.title("Vliegtuigen op luchthavens")
    st.write("Selecteer een datum om het aantal vliegtuigen per luchthaven te zien.")
    st.write("")  
    st.write("")  
# Datumkeuze
    selected_date = st.date_input("Kies een datum:", value=pd.to_datetime('2019-07-15'))

# Bereken het aantal vliegtuigen voor de geselecteerde datum
    airport_traffic = calculate_aircraft_on_airport(selected_date)
    st.write("")  
# Bar plot weergeven
    fig = px.bar(
        airport_traffic,
        x='City',
        y='Aantal_vliegtuigen',
        title=f"Aantal vliegtuigen per luchthaven op {selected_date}",
        labels={'City': 'Luchthaven', 'Aantal_vliegtuigen': 'Aantal Vliegtuigen'},
        color='Aantal_vliegtuigen',
        color_continuous_scale=px.colors.sequential.Viridis
    )

    st.plotly_chart(fig)
    st.write("")  
    st.write("")  
# Interactieve grafiek met een slider
    def create_aircraft_slider_plot():
        start_date = pd.to_datetime('2019-01-01')
        end_date = pd.to_datetime('2020-12-31')
        days = pd.date_range(start=start_date, end=end_date, freq='D')

        frames = []

        for day in days:
          filtered_data = calculate_aircraft_on_airport(day)
          fig = px.bar(filtered_data, x='City', y='Aantal_vliegtuigen', title=f"Aantal vliegtuigen per luchthaven op {day.date()}")
          frames.append(go.Frame(data=fig.data, name=str(day.date())))

    # Initiële figuur
        initial_fig = calculate_aircraft_on_airport(days[0])
        fig = px.bar(initial_fig, x='City', y='Aantal_vliegtuigen', title=f"Aantal vliegtuigen per luchthaven op {days[0].date()}")

        fig = go.Figure(
            data=fig.data,
            layout=go.Layout(
                sliders=[{
                    'steps': [{
                        'args': [[str(day.date())], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                        'label': str(day.date()),
                        'method': 'animate'
                    } for day in days],
                    'currentvalue': {'prefix': 'Datum: '},
                    'pad': {'b': 10},
                }]
            ),
            frames=frames
        )

        st.plotly_chart(fig)

# Aanroepen van de slider grafiek
    if st.checkbox("Toon interactieve grafiek met slider"):
        create_aircraft_slider_plot()

#--------------------------------------------------------------------------------------
# Filterfunctie voor jaar
    def filter_data_by_year(df, year):
        return df[df['Jaartal'] == year]

# Streamlit app
    def main():
        st.title("Aantal vluchten per luchthaven in 2019 en 2020")

    # Data inladen
        df = load_data()

    # Dropdown voor het selecteren van luchthaven
        available_airports = df['City'].unique().tolist()
        selected_airport = st.selectbox("Selecteer een luchthaven", available_airports)

    # Radiobutton voor het selecteren van jaar
        selected_year = st.radio("Kies een jaar:", [2019, 2020])

    # Filter de gegevens op basis van de gekozen luchthaven en jaar
        filtered_data = df[(df['City'] == selected_airport) & (df['Jaartal'] == selected_year)]

    # Controleer of er data beschikbaar is na de filtering
        if filtered_data.empty:
            st.write(f"Geen data beschikbaar voor {selected_airport} in {selected_year}")
            return

    # Groepeer op maand en tel het aantal unieke vluchten (TAR) per maand
        flights_per_month = filtered_data.groupby(filtered_data['STD'].dt.month)['TAR'].nunique().reset_index()
        flights_per_month.columns = ['Maand', 'Aantal_vluchten']

    # Lijndiagram maken met Plotly Express
        fig = px.line(flights_per_month, 
                      x='Maand', 
                      y='Aantal_vluchten', 
                      title=f"Aantal vluchten per maand in {selected_year} voor luchthaven {selected_airport}",
                      labels={'Maand': 'Maand', 'Aantal_vluchten': 'Aantal vluchten'})
  
    # Toon het lijndiagram
        st.plotly_chart(fig)

#--------------------------------------------------------------------------------------
    st.subheader("Hittekaart Europa")
# Zorg ervoor dat de coördinaten numeriek zijn
    df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
    df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)

# Voeg een nieuwe kolom toe voor de tijdstippen van de gebeurtenissen
    df['STD'] = pd.to_datetime(df['STD'])  # Zorg dat STD als datetime is

# Bereken het aantal vliegtuigen op elke luchthaven op een bepaald moment
    def calculate_aircraft_on_airport(selected_time):
    # Filter de data voor alle vluchten die al geland zijn, maar nog niet vertrokken op het gekozen tijdstip
        landed = df[(df['LSV'] == 'L') & (df['STD'] <= selected_time)]
        departed = df[(df['LSV'] == 'S') & (df['STD'] <= selected_time)]
    
    # Groepeer de vluchten per luchthaven en tel het aantal vliegtuigen dat er nog is
        landed_count = landed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vliegtuigen')
        departed_count = departed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vertrokken')

    # Voeg de twee datasets samen en bereken het aantal vliegtuigen dat nog aanwezig is
        airport_traffic = pd.merge(landed_count, departed_count, on='luchthaven', how='left').fillna(0)
        airport_traffic['Aantal_vliegtuigen'] = airport_traffic['Aantal_vliegtuigen'] - airport_traffic['Aantal_vertrokken']

    # Voeg de coördinaten van de luchthavens toe
        airports = df[['luchthaven', 'Latitude', 'Longitude']].drop_duplicates()
        airport_traffic = airport_traffic.merge(airports, on='luchthaven')

        return airport_traffic

# Maak een functie om de kaart te genereren, inclusief een heatmap
    def create_aircraft_traffic_map(selected_time):
    # Bereken het aantal vliegtuigen op de luchthavens op de geselecteerde tijd
        airport_traffic = calculate_aircraft_on_airport(selected_time)

    # Maak de kaart met een centraal punt in Europa
        traffic_map = folium.Map(location=[50, 10], zoom_start=4)

    # Voeg markers toe aan de kaart voor elke luchthaven
        for idx, row in airport_traffic.iterrows():
        # Bepaal de grootte van de marker op basis van het aantal vliegtuigen
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=row['Aantal_vliegtuigen'] / 10,  # Maak de marker afhankelijk van het aantal vliegtuigen
                color='red',  # Rode markers voor het aantal vliegtuigen op de luchthaven
                fill=True,
                fill_opacity=0.6,
                tooltip=f"Luchthaven: {row['luchthaven']}, Aantal vliegtuigen: {row['Aantal_vliegtuigen']}"
            ).add_to(traffic_map)

    # Voeg heatmap toe gebaseerd op het aantal vliegtuigen op elke luchthaven
        heat_data = [[row['Latitude'], row['Longitude'], row['Aantal_vliegtuigen']] for idx, row in airport_traffic.iterrows()]
        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(traffic_map)

        return traffic_map

# Streamlit-app
    def main():
        st.title("Interactieve Luchtvaartkaart")

    # Datumselector
        start_date = pd.to_datetime('2019-01-01')
        end_date = pd.to_datetime('2020-12-31')
        selected_day = st.date_input("Selecteer een datum", value=start_date)

    # Controleer of de geselecteerde datum binnen het bereik ligt
        if start_date <= pd.Timestamp(selected_day) <= end_date:
        # Genereer de kaart voor de geselecteerde datum en tijd
            selected_date_time = pd.Timestamp(selected_day)
            traffic_map = create_aircraft_traffic_map(selected_date_time)
        
        # Toon de kaart met st_folium
            st.subheader(f"Luchtvaartverkeer op {selected_day}")
            st_folium(traffic_map)  # Gebruik st_folium in plaats van folium_static
        else:
            st.warning("Selecteer een datum tussen 2019-01-01 en 2020-12-31.")

# Roep de main functie aan om de Streamlit-app te starten
    if __name__ == "__main__":
        main()
