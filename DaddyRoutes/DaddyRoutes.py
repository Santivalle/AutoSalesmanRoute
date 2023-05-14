# SANTIAGO VALLE VILLAMAYOR - MAPEADO DE LA RUTA EN FUNCION DE LA DISTANCIA ENTRE OBJETIVOS-ORIGEN CON LOS DATOS EXCEL
#DATOS: NOMBRE Y DIRECCION DEL VENDEDOR/ORIGEN  - NOMBRE Y DIRECCION DE LOS CLIENTES/OBJETIVOS
#from pydoc import plainpager
import openrouteservice as ors
from geopy.geocoders import Nominatim
import pandas as pd
import folium
from folium import features
from ipyleaflet import (Map,DrawControl)
#import numpy as np
import geocoder as gc
#from geopy import distance
from IPython.display import HTML, display
import operator
from functools import reduce
import webbrowser

API_KEY = '5b3ce3597851110001cf6248f86bbcc9adbd4557bc439f638fda8f45'
client = ors.Client(key=API_KEY)

#leo el excel y lo muestro
df = pd.read_excel('DatosRuta.xlsx')
display(df)

#origen seleccionable
nombreorigen = df['NOMBRE VENDEDOR'].values
ubiorigen = df['UBICACION VENDEDOR'].values
origen = gc.arcgis(ubiorigen[0]).latlng


#obtengo las coordenadas de las ubicaciones que no tengan coordenadas ya
lats = df['LATITUD'].values
lons = df['LONGITUD'].values
status = df['STATUS'].values

for i,row in df.iterrows():
    lat,lon = None, None
    if row['STATUS'] != 1:
        g = gc.arcgis(row['UBICACION'])
        lat, lon = g.latlng
        lats[i] = lat
        lons[i] = lon
        status[i] = 1
        

#sobreescribo el excel con los nuevos datos
#df.to_excel('DatosRuta.xlsx')

#Mapeado de las direcciones (iconos --https://getbootstrap.com/docs/3.3/components/    colores--'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray') 
m = folium.Map(location = origen)

#Represento origen
iconoog = 'glyphicon glyphicon-play'
icono1 = folium.Icon(color='lightred', icon=iconoog)
folium.Marker(
    location=[origen[0],origen[1]],
    popup=ubiorigen[0],
    tooltip=nombreorigen[0],
    icon=icono1).add_to(m)

#Represento clientes
icono = 'glyphicon glyphicon-user'

for i, row in df.iterrows():
    if row['STATUS']==1:
        icono2 = folium.Icon(color='lightblue', icon=icono)
        folium.Marker(
            location=[row['LATITUD'],row['LONGITUD']],
            popup=row['UBICACION'],
            tooltip=row['NOMBRE'],
            icon=icono2).add_to(m)

#Calculo de las direcciones
#calculo del origen a cada punto su distancia
dur = []
lon = []
lat = []
ordenlat = []
ordenlon = []

for i in range(len(lats)):       
        coords = ((round(origen[1], 6),round(origen[0], 6)),(round(lons[i], 6),round(lats[i], 6)))
        lon.append(lons[i])
        lat.append(lats[i])
        #Profiles route --https://giscience.github.io/openrouteservice-r/reference/ors_profile.html
        route = client.directions(coords, profile='driving-car', format='geojson')
        dur.append(route['features'][0]['properties']['segments'][0]['duration'])

j = 0

#Obtencion de la ruta ordenada en la lista ordenlat / ordenlon
#obteniendo el menor valor de duracion y elimino ese punto para volver a iterar sin el, siendo este punto el nuevo origen
while len(lat)>0:
    mindur = dur[0]
    minlat = lat[0]
    minlon = lon[0]

    for i in range(len(dur)):       
            if dur[i] < mindur:
                mindur = dur[i]
                minlat = lat[i]
                minlon = lon[i]

    #dibujo en el mapa
    if j == 0:
        coords = ((round(origen[1], 6),round(origen[0], 6)),(round(minlon, 6),round(minlat, 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)
    else:
        coords = ((round(newog[1], 6),round(newog[0], 6)),(round(minlon, 6),round(minlat, 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)   
               
    #origen siendo el ultimo destino            
    newog = []
    newog.append(minlat)
    newog.append(minlon)
    #metemos en la lista de la ruta ordenada el destino
    ordenlat.append(minlat)
    ordenlon.append(minlon)
    #eliminamos de la lista completa de coordenadas el destino ya utilizado
    lat.remove(minlat)
    lon.remove(minlon)

    dur = []

    if len(lat)>1:
        for i in range(len(lat)):       
            coords = ((round(newog[1], 6),round(newog[0], 6)),(round(lon[i], 6),round(lat[i], 6)))
            #Profiles route --https://giscience.github.io/openrouteservice-r/reference/ors_profile.html
            route = client.directions(coords, profile='driving-car', format='geojson')
            dur.append(route['features'][0]['properties']['segments'][0]['duration'])
    else:
        coords = ((round(newog[1], 6),round(newog[0], 6)),(round(lon[0], 6),round(lat[0], 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)
        ordenlat.append(lat[0])
        ordenlon.append(lon[0])
        lat.remove(lat[0])
        lon.remove(lon[0])
    
    j = j+1

""" Obtener direccion a partir de las coordenadas
for i in range(len(ordenlat)):
    geolocator = Nominatim(user_agent="coordinateconverter")
    coords = str(ordenlat[i]) + "," + str(ordenlon[i])
    ubicacion = geolocator.reverse(coords)
    print(ubicacion.address)
"""

#Guardo el mapa en una web y lo abro
m.save("map.html")
webbrowser.open("map.html")   
    