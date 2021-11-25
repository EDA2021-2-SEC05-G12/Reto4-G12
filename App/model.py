"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
assert cf
from DISClib.ADT.graph import gr

"""

"""

# Construccion de modelos
def newCatalog():

    catalog = {
               'graph':None,
               'airports_map':None,
               'cities':None
               }
    
    catalog['graph'] = gr.newGraph(datastructure='ADJ_LIST', #aeropuertos/ km
                                         directed = False,
                                         size= 15000,
                                         comparefunction=compareJointId)

    catalog["aux_graph"]=gr.newGraph(datastructure='ADJ_LIST',
                                         directed = False,
                                         size= 15000,
                                         comparefunction=compareJointId)

    
    catalog['airports'] = gr.newGraph(datastructure='ADJ_LIST',  #VERTICES AEROPUERTOS
                                         directed = False,
                                         size= 15000,
                                         comparefunction=compareJointId)

    
    catalog["airport_by_name"]=mp.newMap(numelements=1300,maptype='PROBING') #aeropuerto y su iata


    catalog['airports_map'] = mp.newMap(numelements=1500,
                                          maptype='PROBING')
    
    catalog['same_airport_map']=mp.newMap(numelements=1500,maptype='PROBING')
    

    catalog['cities'] = mp.newMap(numelements=250,
                                          maptype='PROBING')
    
    catalog['airport_by_city_map'] = mp.newMap(numelements=15000,
                                          maptype='PROBING')

    catalog["cities_name"]=lt.newList("ARRAY_LIST")

    catalog["airports_name"]=lt.newList("ARRAY_LIST")

    catalog['route_map'] = mp.newMap(numelements=2500,
                                          maptype='PROBING')
    
    catalog['airlane_map'] = mp.newMap(numelements=5000,
                                          maptype='PROBING')
    return catalog


# Funciones para agregar informacion al catalogo
def addAirports(catalog, airport):
    """
    
    """

    name=airport["Name"].split(",")
    city_name=name[0].lower()
    city = name[-1].title()
    airport['City'] = city

    mp.put(catalog["airport_by_name"],city_name,airport["IATA"])
    mp.put(catalog['airports_map'],airport['IATA'],airport)
    lt.addLast(catalog["airports_name"],airport["IATA"])

    city = airport['name'].split(',')
    city = city[-1].lower().strip()
    exists = mp.get(catalog['airport_by_city_map'],city)

    if exists is None: 
        airports_list=lt.newList(datastructure="ARRAY_LIST")
        lt.addLast(airports_list,airport['IATA'])
    else:
        airports_list=me.getValue(exists)
        if not lt.isPresent(airports_list,airport['IATA']):
            lt.addLast(airports_list,airport['IATA'])

    mp.put(catalog["airport_by_city_map"],city,airports_list)



#añada rutas
#agregar conex
#agregar ciudades

# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento
