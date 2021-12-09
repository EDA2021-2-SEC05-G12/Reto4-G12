"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import controller
from DISClib.ADT import list as lt
assert cf

try:
    from tabulate import tabulate
except ModuleNotFoundError:
    print('ADVERTENCIA: No se encontró el módulo tabulate para graficar tablas.')
    #pip install tabulate
    tabulate = None

try:
    import folium
except ModuleNotFoundError:
    print('ADVERTENCIA: No se encontró el módulo folium para visualizar.')
    #Puedes instalar folium con el comando "pip install folium".
    folium = None


sys.setrecursionlimit(2 ** 20)

"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

airports_filename = 'airports-utf8-large.csv'
routes_filename = 'routes-utf8-large.csv'
worldcities_filename = 'worldcities-utf8.csv'

catalog = None


def printMenu():
    print()
    print("Bienvenido")
    print("1 - Cargar información en el catálogo")
    print("2 - Encontrar puntos de interconexión aérea")
    print("3 - Encontrar clústeres de tráfico aéreo")
    print("4 - Encontrar la ruta más corta entre ciudades")
    print("5 - Utilizar las millas de viajero")
    print("6 - Cuantificar el efecto de un aeropuerto cerrado")
    print()


def print_table(tabular_data, headers=()):
    if tabulate is None:
        header_str = '| ' + ' | '.join([str(x) for x in headers]) + ' |'
        if headers != ():
            print('-' * len(header_str))
            print(header_str)
            print('=' * len(header_str))
        for row in tabular_data:
            row_str = '| ' + ' | '.join([str(x) for x in row]) + ' |'
            print(row_str)
            print('-' * len(row_str))
        if headers != ():
            print('=' * len(header_str))
    else:
        table = tabulate(
            tabular_data=tabular_data,
            headers=headers,
            tablefmt='grid',
        )
        print(table)


def createNewVisualizationData(zoom=1):
    return {
        'zoom': zoom,
        'markers': [],
        'routes': [],
        'location': [0, 0],
    }


def addAirport(data, airport_info, lat, lng):
    marker = {
        'color': 'red',
        'icon': 'plane',
        'tooltip': 'Airport',
        'popup': airport_info,
        'location': [lat, lng],
    }
    data['markers'].append(marker)
    return data


def addCity(data, city_info, lat, lng): #pasar al model, model.addCity cambiar
    marker = {
        'color': 'green',
        'icon': 'info-sign',
        'tooltip': 'City',
        'popup': city_info,
        'location': [lat, lng],
    }
    data['markers'].append(marker)
    return data


def addRoutes(data, locations):
    data['routes'].append([
        (float(location[0]), float(location[1]))
        for location in locations
    ])
    return data


def setLocation(data, lat, lng):
    data['location'] = [lat, lng]
    return data


def visualize(data, filename):
    if folium is None:
        return
    m = folium.Map(location=data['location'], zoom_start=data['zoom'], tiles="Stamen Terrain")
    for marker in data['markers']:
        folium.Marker(
            location=marker['location'],
            popup=marker['popup'],
            tooltip=marker['tooltip'],
            icon=folium.Icon(color=marker['color'], icon=marker['icon']),
        ).add_to(m)
    for points in data['routes']:
        folium.PolyLine(points, color='cyan').add_to(m)
    m.save(filename)
    print()
    print_table([[f'Mapa guardado en "{filename}"']])


def showReport(report):
    header = ['IATA', 'Name', 'City', 'Country', 'Latitude', 'Longitude']
    print('Hay', report['countCities'], 'ciudad(es).')
    print('Airports-Routes DiGraph')
    print('Nodes:', report['digraph']['nodes'], 'loaded airports')
    print('Edges:', report['digraph']['edges'], 'loaded routes')
    print('First & Last Airport loaded in the DiGraph')
    # Show  the table
    digraph_first = report['digraph']['first']
    digraph_last = report['digraph']['last']
    print_table(
        tabular_data=[
            [digraph_first[key] for key in header],
            [digraph_last[key] for key in header],
        ],
        headers=header,
    )
    print()

    print('Airports-Routes Graph')
    print('Nodes:', report['graph']['nodes'], 'loaded airports')
    print('Edges:', report['graph']['edges'], 'loaded routes')
    print('First & Last Airport loaded in the Graph')
    graph_first = report['graph']['first']
    graph_last = report['graph']['last']
    print_table(
        tabular_data=[
            [graph_first[key] for key in header],
            [graph_last[key] for key in header],
        ],
        headers=header,
    )
    print()

    first_city = report['cities']['first']
    last_city = report['cities']['last']

    print('Primera ciudad agregada:')
    print(
        'Nombre:', first_city['city'],
        'de', first_city['country'],
    )
    print(
        'Población de:', first_city['population'],
        ', coordenadas:',
        'latitud', first_city['lat'],
        'longitud', first_city['lng'],
    )
    print()

    print('Última ciudad agregada:')
    print(
        'Nombre:', last_city['city'],
        'de', last_city['country'],
    )
    print(
        'Población de:', last_city['population'],
        ', coordenadas:',
        'latitud', last_city['lat'],
        'longitud', last_city['lng'],
    )
    print()
    # Visualize
    visualization_data = createNewVisualizationData(zoom=3)
    visualization_data = setLocation(
        visualization_data,
        digraph_first['Latitude'],
        digraph_first['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"DiGraph:primera ({digraph_first['IATA']}) {digraph_first['Name']} de {digraph_first['City']} - {digraph_first['Country']}",
        digraph_first['Latitude'],
        digraph_first['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"DiGraph:última ({digraph_last['IATA']}) {digraph_last['Name']} de {digraph_last['City']} - {digraph_last['Country']}",
        digraph_last['Latitude'],
        digraph_last['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"Graph:primera ({graph_first['IATA']}) {graph_first['Name']} de {graph_first['City']} - {graph_first['Country']}",
        graph_first['Latitude'],
        graph_first['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"Graph:última ({graph_last['IATA']}) {graph_last['Name']} de {graph_last['City']} - {graph_last['Country']}",
        graph_last['Latitude'],
        graph_last['Longitude'],
    )
    visualization_data = addCity(
        visualization_data,
        f"Primera ciudad {first_city['city']} - {first_city['country']}",
        first_city['lat'],
        first_city['lng'],
    )
    visualization_data = addCity(
        visualization_data,
        f"Última ciudad {last_city['city']} - {last_city['country']}",
        last_city['lat'],
        last_city['lng'],
    )
    visualize(visualization_data, 'carga-de-datos.html')


def selectOneCityFromVarious(cities):
    count_cities = lt.size(cities)
    if count_cities == 0:
        return
    if count_cities == 1:
        return lt.getElement(cities, 0)
    print('Hay', count_cities, 'ciudad(es)')
    print('Hay varias ciudades con ese nombre, elegir:')
    for i, city in enumerate(lt.iterator(cities)):
        print(f'#{i+1}\t',
                city['city_ascii'], '-', city['country'],
                '(', city['lat'], ',', city['lng'], ')',
                )
    inputs = input('Índice: ')
    index = int(inputs)
    city = lt.getElement(cities, index)
    print(
        'Ciudad:', city['city_ascii'],
        'de', city['country'],
        f"({city['lat']}, {city['lng']})"
    )
    return city


def findInterconnectionPoints(catalog):
    iata_data_list, count = controller.getConnectedAirports(catalog, amount=5)
    print("Connected airports inside network:", count)
    print("TOP 5 most connected airports...")
    airport_info_list = controller.getMoreInformationOfAirports(catalog, iata_data_list)
    header = ['Name', 'City', 'Country', 'IATA', 'connections', 'inbound', 'outbound']
    # Imprime la tabla
    tabular_data = []
    for info in lt.iterator(airport_info_list):
        row = [info[key] for key in header]
        tabular_data.append(row)
    # La pone en al tabla
    print_table(
        tabular_data=tabular_data,
        headers=header,
    )
    # Visualize
    visualization_data = createNewVisualizationData(zoom=4)
    location = None
    for info in lt.iterator(airport_info_list):
        visualization_data = addAirport(
            visualization_data,
            f"[{info['connections']} conexiones] ({info['IATA']}) {info['Name']} de {info['City']} - {info['Country']}",
            info['Latitude'],
            info['Longitude'],
        )
        if location is None:
            location = [info['Latitude'], info['Longitude']]
    visualization_data = setLocation(
        visualization_data,
        *location,
    )
    visualize(visualization_data, 'puntos-de-interconexión-aérea.html')


def findClusters(catalog):
    print('Buscando clústers...')
    amount = controller.amountOfCluster(catalog)
    print("Clusters:", amount)
    v1 = input("Escriba un aeropuerto (IATA): ")
    v2 = input("Escriba otro aeropuerto (IATA): ")
    print('Procesando...')
    is_connected = controller.checkIfTheVerticesAreConnected(catalog, v1, v2)
    print(
        f"Los aeropuertos {v1} y {v2} están",
        "conectados" if is_connected else "no conectados",
    )
    # Visualize
    airport_1 = controller.getAirportByIATA(catalog, v1)
    airport_2 = controller.getAirportByIATA(catalog, v2)
    visualization_data = createNewVisualizationData(zoom=4)
    visualization_data = setLocation(
        visualization_data,
        airport_1['Latitude'],
        airport_1['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"({airport_1['IATA']}) {airport_1['Name']} de {airport_1['City']} - {airport_1['Country']}",
        airport_1['Latitude'],
        airport_1['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"({airport_2['IATA']}) {airport_2['Name']} de {airport_2['City']} - {airport_2['Country']}",
        airport_2['Latitude'],
        airport_2['Longitude'],
    )
    if is_connected:
        visualization_data = addRoutes(
            visualization_data,
            [
                [airport_1['Latitude'], airport_1['Longitude']],
                [airport_2['Latitude'], airport_2['Longitude']],
            ],
        )
    visualize(visualization_data, 'clústeres-de-tráfico-aéreo.html')


def findTheNearestWayBetweenCities(catalog):
    # Preguntar una ciudad
    origin_city_str = input("Escribe el nombre de la ciudad de origen: ")
    # Si hay varias, pedir ayuda para elegir la correcta
    origin_cities = controller.findCitiesByName(catalog, origin_city_str)
    origin_city = selectOneCityFromVarious(origin_cities)
    if origin_city is None:
        print(f'Ninguna ciudad encontrada para "{origin_city_str}"')
        return

    # Preguntar la otra ciudad
    target_city_str = input("Escribe el nombre de la ciudad de destino: ")
    # Lo mismo que #2 pero con esta
    target_cities = controller.findCitiesByName(catalog, target_city_str)
    target_city = selectOneCityFromVarious(target_cities)
    if target_city is None:
        print(f'Ninguna ciudad encontrada para "{target_city_str}"')
        return

    # Buscar el aeropuerto más cercano de la primera ciudad
    origin_airport = controller.searchNearestAirport(catalog, origin_city)
    if origin_airport is None:
        print(f'No se encontró aeropuerto cercano a {origin_city_str}')
        return
    # Buscar el aeropuerto más cercano de la otra ciudad
    target_airport = controller.searchNearestAirport(catalog, target_city)
    if target_airport is None:
        print(f'No se encontró aeropuerto cercano a {target_city_str}')
        return
    # Calcular la distancia normal
    flights = controller.getFlightsToPoints(catalog, origin_airport, target_airport)
    if flights is None:
        print('No se pueden obtener un camino desde', origin_city_str, 'a', target_city_str)
        return
    flight_list = controller.convertStackToList(flights)
    # Calcular la distancia de vuelo por tramos
    controller.showDistances(catalog, origin_city, target_city, origin_airport, target_airport, flight_list)
    # Visualize
    visualization_data = createNewVisualizationData(zoom=4)
    points = []
    visualization_data = setLocation(
        visualization_data,
        origin_city['lat'],
        origin_city['lng'],
    )
    visualization_data = addCity(
        visualization_data,
        f"Origen, {origin_city['city']} - {origin_city['country']}",
        origin_city['lat'],
        origin_city['lng'],
    )
    points.append([origin_airport['Latitude'], origin_airport['Longitude'],])
    visualization_data = addCity(
        visualization_data,
        f"Destino, {target_city['city']} - {target_city['country']}",
        target_city['lat'],
        target_city['lng'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"Salida ({origin_airport['IATA']}) {origin_airport['Name']}",
        origin_airport['Latitude'],
        origin_airport['Longitude'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"Llegada ({target_airport['IATA']}) {target_airport['Name']}",
        target_airport['Latitude'],
        target_airport['Longitude'],
    )
    # Add other airports and their routes
    for flight in lt.iterator(flight_list):
        iata = flight['vertexB']
        airport = controller.getAirportByIATA(catalog, iata)
        points.append([airport['Latitude'], airport['Longitude']])
        visualization_data = addAirport(
            visualization_data,
            f"De paso por: ({airport['IATA']}) {airport['Name']}",
            airport['Latitude'],
            airport['Longitude'],
        )
    visualization_data = addRoutes(visualization_data, points)
    visualize(visualization_data, 'ruta-más-corta-entre-ciudades.html')


def useTravelerMiles(catalog):
    # Preguntar una ciudad
    origin_city_str = input("Escribe el nombre de la ciudad de origen: ")
    # Si hay varias, pedir ayuda para elegir la correcta
    origin_cities = controller.findCitiesByName(catalog, origin_city_str)
    origin_city = selectOneCityFromVarious(origin_cities)
    if origin_city is None:
        print(f'Ninguna ciudad encontrada para "{origin_city_str}"')
        return

    miles_str = input("Cantidad de millas disponible: ")
    miles = float(miles_str)

    result = controller.findRoundTrip(catalog, origin_city)
    if result is None:
        print('No hay aeropuertos cercanos')
        return
    elif result[1] is None:
        print('No se encontraron rutas de ida y vuelta')
        return
    city_airport, airports = result
    distance = 0.0
    print('Recorrerás', lt.size(airports), 'aeropuertos.')
    print('El viaje comienza en el aeropuerto', city_airport['Name'])
    last_coords = city_airport['Longitude'], city_airport['Latitude']
    for airport in lt.iterator(airports):
        print('Parada en aeropuerto', airport['Name'])
        print('\t', 'se recomineda visitar la ciudad de', airport['City'], '-', airport['Country'])
        distance += controller.calcDistanceBetween(
            last_coords[0],
            last_coords[1],
            airport['Longitude'],
            airport['Latitude'],
        )
        # Actualiza la lista de últimos
        last_coords = airport['Longitude'], airport['Latitude']
    print()
    print('Distancia total de', distance, 'km')
    req_miles = controller.convertKmToMiles(distance)
    diff = miles - req_miles
    if diff < 0:
        print('Te faltan', abs(diff), 'millas.')
    elif diff > 0:
        print('Te sobraron', abs(diff), 'millas.')
    else:
        print('Se han gastado todas las millas.')
    # Visualize
    visualization_data = createNewVisualizationData(zoom=6)
    points = []
    visualization_data = setLocation(
        visualization_data,
        origin_city['lat'],
        origin_city['lng'],
    )
    visualization_data = addCity(
        visualization_data,
        f"Origen, {origin_city['city']} - {origin_city['country']}",
        origin_city['lat'],
        origin_city['lng'],
    )
    visualization_data = addAirport(
        visualization_data,
        f"Salida ({city_airport['IATA']}) {city_airport['Name']}",
        city_airport['Latitude'],
        city_airport['Longitude'],
    )
    for airport in lt.iterator(airports):
        visualization_data = addAirport(
            visualization_data,
            f"Escala ({airport['IATA']}) {airport['Name']}",
            airport['Latitude'],
            airport['Longitude'],
        )
        points.append([airport['Latitude'], airport['Longitude']])
    visualization_data = addRoutes(visualization_data, points)
    visualize(visualization_data, 'las-millas-de-viajero.html')


def evalIfAirportStopWorking(catalog):
    iata = input('Código IATA del aeropuerto fuera de funcionamiento: ')
    airport, airport_affedted_data_list = controller.getAirportsAffectedForIATA(catalog, iata)
    print('Si el aeropuerto',
          airport['Name'],
          'de la ciudad de',
          airport['City'],
          'queda fuera de servicios, los siguientes aeropuertos pueden verse afectados:',
         )
    print(lt.size(airport_affedted_data_list), 'aeropuertos afectados')
    # Print data
    header = ['Vuelo', 'Nombre', 'Ciudad', 'IATA']
    tabular_data = []
    for airport_data in lt.iterator(airport_affedted_data_list):
        type = airport_data['type']
        tabular_data.append([
            'Entrada' if type == 'from' else 'Salida' if type == 'to' else 'Desconocido',
            airport_data['airport']['Name'],
            airport_data['airport']['City'],
            airport_data['airport']['IATA'],
        ])
    print_table(
        tabular_data=tabular_data,
        headers=header,
    )
    # Visualize
    visualization_data = createNewVisualizationData(zoom=4)
    point_origin = [airport['Latitude'], airport['Longitude']]
    visualization_data = setLocation(
        visualization_data,
        *point_origin,
    )
    visualization_data = addAirport(
        visualization_data,
        f"Fuera de servicio: ({airport['IATA']}) {airport['Name']}",
        airport['Latitude'],
        airport['Longitude'],
    )
    for airport_data in lt.iterator(airport_affedted_data_list):
        visualization_data = addAirport(
            visualization_data,
            f"Afectado: ({airport_data['airport']['IATA']}) {airport_data['airport']['Name']}",
            airport_data['airport']['Latitude'],
            airport_data['airport']['Longitude'],
        )
        visualization_data = addRoutes(
            visualization_data,
            [
                point_origin,
                [airport_data['airport']['Latitude'], airport_data['airport']['Longitude']],
            ]
        )
    visualize(visualization_data, 'efecto-de-un-aeropuerto-cerrado.html')


"""
Menu principal
"""
while True:
    printMenu()
    try:
        inputs = input('Seleccione una opción para continuar: ')
        index = int(inputs[0])
        print()
    except IndexError:
        continue
    except ValueError:
        print('Valor desconocido.')
        continue
    except KeyboardInterrupt:
        print()
        print('Hasta luego.')
        break

    if not inputs:
        continue

    if index != 1 and catalog is None:
        print('Primero cargue la información de los archivo.')
        continue

    if index == 1:
        print("Cargando información de los archivos ....")
        catalog = controller.init()
        catalog, report = controller.load(
            catalog,
            airports_filename,
            routes_filename,
            worldcities_filename,
        )
        showReport(report)

    elif index == 2:
        findInterconnectionPoints(catalog)

    elif index == 3:
        findClusters(catalog)

    elif index == 4:
        findTheNearestWayBetweenCities(catalog)

    elif index == 5:
        useTravelerMiles(catalog)

    elif index == 6:
        evalIfAirportStopWorking(catalog)

    else:
        sys.exit(0)
sys.exit(0)
