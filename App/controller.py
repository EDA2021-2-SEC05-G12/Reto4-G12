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
 """

import config as cf
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del base de datos
def init():
    return model.newAnalizer()


# Funciones para la carga de datos
def load(analyzer, airports_filename, routes_filename, worldcities_filename):
    # Carga aeropuertos
    print('Cargando aeropuertos', end='... ', flush=True)
    airports_path = cf.data_dir + airports_filename
    airports = csv.DictReader(open(airports_path, encoding='utf-8'), delimiter=',')
    for data in airports:
        model.loadAirports(analyzer, data)
    print('Cargado.')
    # Carga rutas
    print('Cargando rutas', end='...', flush=True)
    routes_path = cf.data_dir + routes_filename
    routes = csv.DictReader(open(routes_path, encoding='utf-8'), delimiter=',')
    model.loadRoutes(analyzer, routes)
    print('Cargado.')
    # Carga ciudades
    print('Cargando ciudades del mundo', end='...', flush=True)
    worldcities_path = cf.data_dir + worldcities_filename
    worldcities = csv.DictReader(open(worldcities_path, encoding='utf-8'), delimiter=',')
    for data in worldcities:
        model.loadCities(analyzer, data)
    print('Cargado.')
    report = {}
    # Muestra información sobre los datos cargados
    report['countCities'] = model.countAllCities(analyzer)

    report['digraph'] = {}
    report['digraph']['nodes'] = model.getNodeDiGraphAmount(analyzer)
    report['digraph']['edges'] = model.getEdgeDigraphAmount(analyzer)
    report['digraph']['first'] = model.getFirstAirportLoaded(analyzer, is_digraph=True)
    report['digraph']['last'] = model.getLastAirportLoaded(analyzer, is_digraph=True)

    report['graph'] = {}
    report['graph']['nodes'] = model.getNodeGraphAmount(analyzer)
    report['graph']['edges'] = model.getEdgeGraphAmount(analyzer)
    report['graph']['first'] = model.getFirstAirportLoaded(analyzer, is_digraph=False)
    report['graph']['last'] = model.getLastAirportLoaded(analyzer, is_digraph=False)

    report['cities'] = {}
    report['cities']['first'] = model.getFirstCityAdded(analyzer)
    report['cities']['last'] = model.getLastCityAdded(analyzer)

    return analyzer, report


# Funciones de ordenamiento


# Funciones de consulta sobre el catálogo
def getConnectedAirports(analyzer, amount):
    """
    Retorna una tupla que contiene una lista del top 5 con los
    aeropuertos más conectados en formato código IATA. Y la cantidad
    total de interconexiones.
    """
    return model.getConnectedAirports(analyzer, amount)


def getMoreInformationOfAirports(analyzer, iata_list):
    """
    Retorna una lista de aeropuertos para la lista de códigos IATA dados.
    """
    # Obtiene la información
    info_list = model.getMoreInformationOfAirports(analyzer, iata_list)
    return info_list


def amountOfCluster(analyzer):
    return model.amountOfCluster(analyzer)


def checkIfTheVerticesAreConnected(analyzer, v1, v2):
    return model.checkIfTheVerticesAreConnected(analyzer, v1, v2)


def findCitiesByName(analyzer, city_str):
    """
    Retorna una lista de todas las ciudades que tiene el
    mismo nombre que el nombre proporcionado.
    """
    cities = model.findCities(analyzer, city_str)
    return cities


def searchNearestAirport(analyzer, origin_city):
    """
    Retorna el aeropuerto más cercano a una ciudad dada.
    """
    airports, length = model.getAllAirportsFor(analyzer, origin_city)
    if length == 0:
        print("No se encontró aeropuerto para", origin_city['city'])
        return None
    nearest = model.getNearestAirportTo(airports, origin_city['lat'], origin_city['lng'])
    return nearest


def getFlightsToPoints(analyzer, origin, target):
    """Retorna una pila de vuelos"""
    steps = model.getStepsToGo(analyzer, origin['IATA'], target['IATA'])
    return steps


def showDistances(analyzer, origin_city, target_city, origin_airport, target_airport, flight_list):
    print("Ruta de vuelo.")
    print("Aeropuerto de origin:", origin_airport['Name'])
    print("Aeropuerto de destino:", target_airport['Name'])
    flight_distance = model.showInformationAboutFlights(analyzer, flight_list)
    distance_from_origin = model.haversine(
        origin_city['lng'],
        origin_city['lat'],
        origin_airport['Longitude'],
        origin_airport['Latitude'],
    )
    distance_to_target = model.haversine(
        target_city['lng'],
        target_city['lat'],
        target_airport['Longitude'],
        target_airport['Latitude'],
    )
    print()
    print('Distancia de', origin_city['city'], 'al aeropuerto:', distance_from_origin, 'km')
    print('Distancia de', target_city['city'], 'al aeropuerto:', distance_to_target, 'km')
    print('Distancia en vuelo:', flight_distance, 'km')
    print('Distancia total:', distance_from_origin + distance_to_target + flight_distance, 'km')


def findRoundTrip(analyzer, city):
    """
    Encuentras rutas de ida y vuelta de una ciudad de origen.
    """
    city_airport = searchNearestAirport(analyzer, city)
    if city_airport is None:
        return
    airports = model.findNodeCycles(analyzer, city_airport)
    return city_airport, airports


def calcDistanceBetween(lon1, lat1, lon2, lat2):
    return model.haversine(lon1, lat1, lon2, lat2)


def convertKmToMiles(km):
    return km / 1.60


def getAirportByIATA(analyzer, iata):
    """Dado el código IATA, retorna el aeropuerto."""
    return model.findAirportByIATA(analyzer, iata)


def getAirportsAffectedForIATA(analyzer, iata):
    """
    Dado el código IATA de un aeropuerto fuera de servicio,
    busca todos los aeropuertos que tienen ruta a/desde él.

    Retorna una tupla del aeropuerto consultado y una lista de
    los aeropuertos afectados.
    """
    airport = model.findAirportByIATA(analyzer, iata)
    airport_affedted_data_list = model.getAirportsAffectedForIATA(analyzer, iata)
    return airport, airport_affedted_data_list

def convertStackToList(stack):
    return model.convertStackToList(stack)
