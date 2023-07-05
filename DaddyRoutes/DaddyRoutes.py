""" SANTIAGO VALLE VILLAMAYOR - AutoSalesmanRoute """
#DATA: NAME AND ADDRESS OF SELLER/ORIGIN  - NAME AND ADDRESS OF THE CUSTOMERS/GOALS
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

print("IMPORTANT: THE EXCEL TABLE MUST HAVE THE FOLLOWING COLUMNS WITH THE SAME NUMBER OF ROWS AS CUSTOMERS THERE ARE")
print('\t-SELLER NAME\n\t-SELLER LOCATION\n\t-NAME\n\t-LOCATION\n\t-STATUS\n\t-LATITUDE\n\t-LONGITUDE')
print('NOTE 1: The first two columns are for entering the seller\'s data in the first row, the rest is for the consumers\' data')
print('NOTE 2: The columns LATITUDE and LONGITUDE must be empty. It will be calculated from location')
print('NOTE 3: The column STATUS also must be empty. It will be written with 1 when coordinates are calculated')

print("\nType the directory with the excel table (IMPORTANT: Put / at the end)")
print('Example: D:\\User\\Desktop\\')
directory = input()
directory = directory.replace("\\", "/") #Replace the \ symbol to / which i use in code
print()

print("Type the name of excel file without extension (IMPORTANT: File must be Excel extension like xlsx)")
excelname = input()
print()

# Read excel
df = pd.read_excel(directory+excelname+'.xlsx')
#display(df)

# Get origin
nombreorigen = df['SELLER NAME'].values
ubiorigen = df['SELLER LOCATION'].values
origen = gc.arcgis(ubiorigen[0]).latlng


# Getting the coordinates of locations that don't have coordinates yet
lats = df['LATITUDE'].values
lons = df['LONGITUDE'].values
status = df['STATUS'].values

for i,row in df.iterrows():
    lat,lon = None, None
    if row['STATUS'] != 1:
        g = gc.arcgis(row['LOCATION'])
        lat, lon = g.latlng
        lats[i] = lat
        lons[i] = lon
        status[i] = 1
        

# Overwrite the excel with the new data
df.to_excel(directory+excelname+'.xlsx')

# Address mapping (iconos --https://getbootstrap.com/docs/3.3/components/    colors--'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray') 
m = folium.Map(location = origen)

# Plot origin
iconoog = 'glyphicon glyphicon-home'
icono1 = folium.Icon(color='lightred', icon=iconoog)
folium.Marker(
    location=[origen[0],origen[1]],
    popup=ubiorigen[0],
    tooltip=nombreorigen[0],
    icon=icono1).add_to(m)


# Calculate address
""" Optencion de la mejor ruta por fuerza bruta
#numero de rutas posibles a traves del factorial del numero de clientes
print('Numero de rutas posbiles:',math.factorial(len(lats)))

#funcion para calcular la duracion entre puntos de la ruta
def duracion(origen, destino):
    for i, row in df.iterrows():
        if row['LATITUDE']==origen:
            origenlon = row['LONGITUDE']
        if row['LATITUDE']==destino:
            destinolon = row['LONGITUDE']
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
        if row['LATITUDE']==ruta[0]:
            loninicial = row['LONGITUDE']
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
            if row['LATITUDE']==ruta[i]:
                rutalon = row['LONGITUDE']
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
            if row['LATITUDE']==ruta[i]:
                rutalon = row['LONGITUDE']
        coords = ((round(newog[1], 6),round(newog[0], 6)),(round(rutalon, 6),round(ruta[i], 6)))
        route = client.directions(coords, profile='driving-car', format='geojson')
        waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))
        folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color='red').add_to(m)   
        #Ultimo destino es nuevo origen   
        newog = []
        newog.append(ruta[i])
        newog.append(rutalon)
"""


# Obtaining the pseudo best route by iterations based on the origin-next_destination distance
# Calculate the distance from the origin to each point
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

#Getting the sorted path in the list "ordenlat/ordenlon"
# Obtaining the smallest value of duration and removing that point to iterate again without it, being this point the new origin
while len(lat)>0:
    mindur = dur[0]
    minlat = lat[0]
    minlon = lon[0]

    for i in range(len(dur)):       
            if dur[i] < mindur:
                mindur = dur[i]
                minlat = lat[i]
                minlon = lon[i]

    # Plot the map
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

    # Saving the duration of the journey
    rutadur.append(route['features'][0]['properties']['segments'][0]['duration'])          
    rutadis.append(route['features'][0]['properties']['segments'][0]['distance'])

    # Origin being the last destination        
    newog = []
    newog.append(minlat)
    newog.append(minlon)
    # Appending the destination in the list of the ordered route
    ordenlat.append(minlat)
    ordenlon.append(minlon)
    # Remove from the complete list of coordinates the destination already used
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

# Typing on console the ordered list of clients with their name and location
icono = 'glyphicon glyphicon-user'

print("LIST OF CUSTOMERS ORDERED ACCORDING TO THE ROUTE:")
for k in range(len(ordenlat)):
    for i, row in df.iterrows():
        if row['LATITUDE']==ordenlat[k]:
            if(k == 0):
                print('Customer', k+1, '\n\t Name:', row['NAME'], ' Location:', row['LOCATION'], '\n\t Duration:', round(rutadur[k],2), 'minutos',' Distance:', round((disacumula[k]/1000),2),'Km', '\n\t Distance from the starting point:', round((rutadis[k]/1000),2),'Km')
            else:
                print('Customer', k+1, '\n\t Name:', row['NAME'], ' Location:', row['LOCATION'], '\n\t Duration:', round(rutadur[k],2), 'minutos', ' Distance:', round((disacumula[k]/1000),2),'Km', '\n\t Distance from the starting point:', round((rutadis[k]/1000),2),'Km')
            
            icono2 = folium.Icon(color='lightblue', icon=icono)
            folium.Marker(
            location=[row['LATITUDE'],row['LONGITUDE']],
            popup=row['LOCATION']+' Duration:'+str(round(rutadur[k],2))+ 'min' + ' Distance:'+str(round((disacumula[k]/1000),2))+'Km',
            tooltip=row['NAME'],
            icon=icono2).add_to(m)

print('\n Total duracion:',  round((durtotal/60),2), 'min', ' Total distance:',  round((distotal/1000),2),'Km')

# Show the map with html and open it
m.save("map.html")
webbrowser.open("map.html")   
    