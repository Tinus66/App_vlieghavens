import folium
from folium.plugins import HeatMap
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium  # Gebruik st_folium in plaats van folium_static

merged_df = pd.read_csv("C:\\Users\\marti\\Documents\\Data_science_minor\\Week 6\\case3_data\\case3\\DatasetLuchthaven_murged.csv")
# Zorg ervoor dat de coördinaten numeriek zijn
merged_df['Latitude'] = merged_df['Latitude'].astype(str).str.replace(',', '.').astype(float)
merged_df['Longitude'] = merged_df['Longitude'].astype(str).str.replace(',', '.').astype(float)

# Voeg een nieuwe kolom toe voor de tijdstippen van de gebeurtenissen
merged_df['STD'] = pd.to_datetime(merged_df['STD'])  # Zorg dat STD als datetime is

# Bereken het aantal vliegtuigen op elke luchthaven op een bepaald moment
def calculate_aircraft_on_airport(selected_time):
    # Filter de data voor alle vluchten die al geland zijn, maar nog niet vertrokken op het gekozen tijdstip
    landed = merged_df[(merged_df['LSV'] == 'L') & (merged_df['STD'] <= selected_time)]
    departed = merged_df[(merged_df['LSV'] == 'S') & (merged_df['STD'] <= selected_time)]
    
    # Groepeer de vluchten per luchthaven en tel het aantal vliegtuigen dat er nog is
    landed_count = landed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vliegtuigen')
    departed_count = departed.groupby('luchthaven')['TAR'].nunique().reset_index(name='Aantal_vertrokken')

    # Voeg de twee datasets samen en bereken het aantal vliegtuigen dat nog aanwezig is
    airport_traffic = pd.merge(landed_count, departed_count, on='luchthaven', how='left').fillna(0)
    airport_traffic['Aantal_vliegtuigen'] = airport_traffic['Aantal_vliegtuigen'] - airport_traffic['Aantal_vertrokken']

    # Voeg de coördinaten van de luchthavens toe
    airports = merged_df[['luchthaven', 'Latitude', 'Longitude']].drop_duplicates()
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
