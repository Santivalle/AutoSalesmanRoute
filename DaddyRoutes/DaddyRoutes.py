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
from itertools import permutations
import math

API_KEY = '5b3ce3597851110001cf6248f86bbcc9adbd4557bc439f638fda8f45'
client = ors.Client(key=API_KEY)

#Leo el excel
df = pd.read_excel('C:/DatosRuta.xlsx')
#display(df)

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
df.to_excel('D:/User/Desktop/Python Projects/DaddyRoutes/DaddyRoutes/DatosRuta.xlsx')

#Mapeado de las direcciones (iconos --https://getbootstrap.com/docs/3.3/components/    colores--'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray') 
m = folium.Map(location = origen)

#Represento origen
iconoog = 'glyphicon glyphicon-home'
icono1 = folium.Icon(color='lightred', icon=iconoog)
folium.Marker(
    location=[origen[0],origen[1]],
    popup=ubiorigen[0],
    tooltip=nombreorigen[0],
    icon=icono1).add_to(m)



#Calculo de las direcciones
""" Optencion de la mejor ruta por fuerza bruta
#numero de rutas posibles a traves del factorial del numero de clientes
print('Numero de rutas posbiles:',math.factorial(len(lats)))

#funcion para calcular la duracion entre puntos de la ruta
def duracion(origen, destino):
    for i, row in df.iterrows():
        if row['LATITUD']==origen:
            origenlon = row['LONGITUD']
        if row['LATITUD']==destino:
            destinolon = row['LONGITUD']
    coords = ((round(origenlon, 6),round(origen, 6)),(round(destinolon, 6),round(destino, 6)))
    route = client.directions(coords, profile='driving-car', format='geojson')
    dur = route['features'][0]['properties']['segments'][0]['duration']
    return dur

def calcular_duracion_ruta(ruta):
    duracion_total = 0
    #calculo duracion ruta
    for i in range(len(ruta)-1):
        duracion_total += duracion(ruta[i], ruta[i+1])
    #calculo duracion inicial
    for i, row in df.iterrows():
        if row['LATITUD']==ruta[0]:
            loninicial = row['LONGITUD']
    coords = ((round(origen[1], 6),round(origen[0], 6)),(round(loninicial, 6),round(ruta[0], 6)))
    route = client.directions(coords, profile='driving-car', format='geojson')
    duracion_inicial = route['features'][0]['properties']['segments'][0]['duration']
    #duracion total ruta
    duracion_total = duracion_total+duracion_inicial
    return duracion_total

rutas_posibles = permutations(lats)

#recorro todas las posibles rutas y calculo su duracion
duracionrutas = []
for ruta in rutas_posibles:
    duracionrutas.append(calcular_duracion_ruta(ruta))

mindur = duracionrutas[0]
indruta = 0
for i in range(len(duracionrutas)):
    if duracionrutas[i] < mindur:
        mindur = duracionrutas[i]
        indruta = i #guardo el indice con la ruta optima y su duracion

for i in range(len(rutas_posibles[i])):
    if i == 0: #Origen - primer destino
        for i, row in df.iterrows():
            if row['LATITUD']==ruta[i]:
                rutalon = row['LONGITUD']
        coords = ((round(origen[1], 6),round(origen[0], 6)),(round(rutalon, 6),round(ruta[i], 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)   
        #Ultimo destino es nuevo origen  
        newog = [] 
        newog.append(ruta[i])
        newog.append(rutalon)
    else: #Resto de la ruta
        for i, row in df.iterrows():
            if row['LATITUD']==ruta[i]:
                rutalon = row['LONGITUD']
        coords = ((round(newog[1], 6),round(newog[0], 6)),(round(rutalon, 6),round(ruta[i], 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)   
        #Ultimo destino es nuevo origen   
        newog = []
        newog.append(ruta[i])
        newog.append(rutalon)
"""


# Optencion de la pseudomejor ruta por iteraciones en base a la distancia origen-siguiente destino
#calculo del origen a cada punto su distancia
dur = []
lon = []
lat = []
ordenlat = []
ordenlon = []
rutadur = []
rutadis = []

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

    #Guardo la duracion del trayecto
    rutadur.append(route['features'][0]['properties']['segments'][0]['duration'])          
    rutadis.append(route['features'][0]['properties']['segments'][0]['distance'])

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
        rutadur.append(route['features'][0]['properties']['segments'][0]['duration']) 
        rutadis.append(route['features'][0]['properties']['segments'][0]['distance'])
    
    j = j+1

acumulacion = 0
acumulacion2 = 0
durtotal = 0
distotal = 0
disacumula = []

for i in range(len(rutadis)):
    disacumula.append(rutadis[i])

for i in range(len(rutadur)):

    distotal = rutadis[i]+distotal
    durtotal = rutadur[i]+durtotal

    rutadur[i] = acumulacion+(rutadur[i]/60)
    acumulacion = rutadur[i]

    disacumula[i] = acumulacion2+disacumula[i]
    acumulacion2 = disacumula[i]

#Escribo por consola la lista ordenada de los clientes con su nombre y ubicacion
icono = 'glyphicon glyphicon-user'

print("LISTADO DE CLIENTES ORDENADOS SEGUN LA RUTA:")
for k in range(len(ordenlat)):
    for i, row in df.iterrows():
        if row['LATITUD']==ordenlat[k]:
            if(k == 0):
                print('Cliente', k+1, '\n\t Nombre:', row['NOMBRE'], ' Ubicacion:', row['UBICACION'], '\n\t Tiempo:', round(rutadur[k],2), 'minutos',' Distancia:', round((disacumula[k]/1000),2),'Km', '\n\t Distancia desde el punto de salida:', round((rutadis[k]/1000),2),'Km')
            else:
                print('Cliente', k+1, '\n\t Nombre:', row['NOMBRE'], ' Ubicacion:', row['UBICACION'], '\n\t Tiempo:', round(rutadur[k],2), 'minutos', ' Distancia:', round((disacumula[k]/1000),2),'Km', '\n\t Distancia desde anterior cliente:', round((rutadis[k]/1000),2),'Km')
            
            icono2 = folium.Icon(color='lightblue', icon=icono)
            folium.Marker(
            location=[row['LATITUD'],row['LONGITUD']],
            popup=row['UBICACION']+' Tiempo:'+str(round(rutadur[k],2))+ 'min' + ' Distancia:'+str(round((disacumula[k]/1000),2))+'Km',
            tooltip=row['NOMBRE'],
            icon=icono2).add_to(m)

print('\n Duracion total:',  round((durtotal/60),2), 'min', ' Distancia total:',  round((distotal/1000),2),'Km')
""" Obtener direccion a partir de las coordenadas
for i in range(len(ordenlat)):
    geolocator = Nominatim(user_agent="coordinateconverter")
    coords = str(ordenlat[i]) + "," + str(ordenlon[i])
    ubicacion = geolocator.reverse(coords)
    print(ubicacion.address)
"""
"""
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
"""

#Guardo el mapa en una web y lo abro
m.save("map.html")
webbrowser.open("map.html")   
    