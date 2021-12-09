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


import sys
import time
import signal
import multiprocessing
import math
import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.ADT import graph as gr
from DISClib.ADT import stack
from DISClib.DataStructures import mapentry as me
from DISClib.DataStructures import edge as ed
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra
from DISClib.Algorithms.Graphs import cycles
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos
def newAnalizer():
    analyzer = {
        'airports': None,
        'cities': None,
        'digraph': None,
        'graph': None
    }
    analyzer['airports'] = mp.newMap()
    analyzer['cities'] = mp.newMap()
    analyzer['cities_list'] = lt.newList()
    analyzer['digraph'] = gr.newGraph(directed=True)
    analyzer['graph'] = gr.newGraph(directed=False)
    return analyzer


# Funciones para agregar informacion al catalogo
def loadAirports(analyzer, data):
    mp.put(analyzer['airports'], data['IATA'], data)
    # Agrega el vértice para los dos grafos
    gr.insertVertex(analyzer['digraph'], data['IATA'])
    gr.insertVertex(analyzer['graph'], data['IATA'])


def loadRoutes(analyzer, routes):
    for data in routes:
        gr.addEdge(analyzer['digraph'],
                   data['Departure'],
                   data['Destination'],
                   float(data['distance_km']))

    # Carga solamente los que van y vienen
    for edge in lt.iterator(gr.edges(analyzer['digraph'])):
        either = ed.either(edge)
        other = ed.other(edge, either)
        weight = ed.weight(edge)

        if not gr.getEdge(analyzer['digraph'], other, either):
            continue
        
        if not gr.getEdge(analyzer['digraph'], either, other):
            continue

        if not gr.getEdge(analyzer['graph'], either, other) and not gr.getEdge(analyzer['graph'], other, either):
            gr.addEdge(analyzer['graph'], either, other, weight)


def loadCities(analyzer, data):
    mp.put(analyzer['cities'], data['iso2'], data)
    lt.addFirst(analyzer['cities_list'], data)


def countAllCities(analyzer):
    return mp.size(analyzer['cities'])

# Funciones para creacion de datos

# Funciones de consulta
def getNodeDiGraphAmount(analyzer):
    return gr.numVertices(analyzer['digraph'])


def getNodeGraphAmount(analyzer):
    return gr.numVertices(analyzer['graph'])


def getEdgeDigraphAmount(analyzer):
    return gr.numEdges(analyzer['digraph'])


def getEdgeGraphAmount(analyzer):
    return gr.numEdges(analyzer['graph'])


def getFirstAirportLoaded(analyzer, is_digraph):
    """
    Obtiene el primer aeropuerto agregado al grafo solicitado.
    El parámetro `is_digraph` determimna en cuál grafo se analizará.

    Retorna el código IATA del aeropuerto.
    """
    if is_digraph:
        vertices = gr.vertices(analyzer['digraph'])
    else:
        vertices = gr.vertices(analyzer['graph'])
    first = lt.firstElement(vertices)
    mapentry = mp.get(analyzer['airports'], first)
    return me.getValue(mapentry)


def getLastAirportLoaded(analyzer, is_digraph):
    """
    Obtiene el último aeropuerto agregado al grafo solicitado.
    El parámetro `is_digraph` determimna en cuál grafo se analizará.

    Retorna el código IATA del aeropuerto.
    """
    if is_digraph:
        vertices = gr.vertices(analyzer['digraph'])
    else:
        vertices = gr.vertices(analyzer['graph'])
    last = lt.lastElement(vertices)
    mapentry = mp.get(analyzer['airports'], last)
    return me.getValue(mapentry)


def getFirstCityAdded(analyzer):
    return lt.firstElement(analyzer['cities_list'])


def getLastCityAdded(analyzer):
    return lt.lastElement((analyzer['cities_list']))


def getConnectedAirports(analyzer, amount):
    """
    Retorna una tupla que contiene una lista del top N con los
    aeropuertos más conectados en formato código IATA. Y la cantidad
    total de interconexiones.

    El parámetro `amount` indica de cuántos elementos será el top.
    """
    pre_top = lt.newList()
    total_count = 0
    for vertex in lt.iterator(gr.vertices(analyzer['digraph'])):
        # others = gr.adjacents(analyzer['digraph'], vertex)
        connections = gr.degree(analyzer['digraph'], vertex)
        if connections > 0:
            total_count += 1
        vertex_map = mp.newMap()
        mp.put(vertex_map, 'vertex', vertex)
        mp.put(vertex_map, 'connections', connections)
        lt.addLast(pre_top, vertex_map)
    # Obtiene el top de aeropuertos conectados
    top = getTopConnectedAirports(pre_top)
    top_list = lt.newList()
    i = 0
    while lt.size(top_list) < amount:
        item = lt.getElement(top, i)
        vertex = me.getValue(mp.get(item, 'vertex'))
        if not lt.isPresent(top_list, vertex):
            lt.addLast(top_list, vertex)
        i += 1
    return top_list, total_count


def getMoreInformationOfAirports(analyzer, vertex_list):
    """
    Retorna una lista de aeropuertos para la lista de vértices dados.
    """
    info_list = lt.newList()
    for airport in lt.iterator(vertex_list):
        keyvalue = mp.get(analyzer['airports'], airport)
        # degree = gr.degree(analyzer['digraph'], airport)
        outdegree = gr.outdegree(analyzer['digraph'], airport)
        indegree = gr.indegree(analyzer['digraph'], airport)
        value = me.getValue(keyvalue)
        value['connections'] = indegree + outdegree
        value['inbound'] = indegree
        value['outbound'] = outdegree
        lt.addLast(info_list, value)
    return info_list


def findAllSCC(analyzer):
    return scc.KosarajuSCC(analyzer['digraph'])


def amountOfCluster(analyzer):
    scc_ = findAllSCC(analyzer)
    return scc.connectedComponents(scc_)


def checkIfTheVerticesAreConnected(analyzer, v1, v2):
    scc_ = findAllSCC(analyzer)
    return scc.stronglyConnected(scc_, v1, v2)


# Funciones utilizadas para comparar elementos dentro de una lista
def cmpTopConnected(m1, m2):
    """
    Compara la cantidad de conexión entre dos elementos.
    """
    kv1 = mp.get(m1, 'connections')
    kv2 = mp.get(m2, 'connections')
    conns1 = me.getValue(kv1)
    conns2 = me.getValue(kv2)
    return conns1 > conns2


def findCities(analyzer, city_name):
    """
    Retorna una lista de todas las ciudades que tiene el mismo nombre
    que el nombre proporcionado.
    """
    city_list = lt.newList()
    for city in lt.iterator(analyzer['cities_list']):
        if city['city'].strip().lower().find(city_name.strip().lower()) != -1 \
           or city['city_ascii'].strip().lower().find(city_name.strip().lower()) != -1:
            lt.addLast(city_list, city)
    return city_list


def getAllAirportsFor(analyzer, city):
    """
    Retorna una lista de todos los aeropuertos de una ciudad.
    """
    airports = lt.newList()
    for airport in lt.iterator(mp.valueSet(analyzer['airports'])):
        if (airport['City'] == city['city'] or airport['City'] == city['city_ascii']) and airport['Country'] == city['country']:
            lt.addLast(airports, airport)
    return airports, lt.size(airports)


def getNearestAirportTo(airports, lat, lng):
    """
    Retorna el aeropuerto más cercano entre una lista de aeropuertos a
    la coordenada proporcionada.
    """
    best = None
    score = sys.maxsize
    for airport in lt.iterator(airports):
        distance = haversine(airport['Longitude'], airport['Latitude'], lng, lat)
        if distance < score:
            score = distance
            best = airport
    return best


def getStepsToGo(analyzer, origin, dest):
    """
    Retorna una pila de los aeropuertos (en código IATA) que
    se deben recorrer para llegar a un destino desde un origen.
    """
    search = dijsktra.Dijkstra(analyzer['digraph'], origin)
    paths = dijsktra.pathTo(search, dest)
    return paths


def findAirportByIATA(analyzer, iata):
    """
    Dado el código IATA, retorna el aeropuerto.
    """
    return me.getValue(mp.get(analyzer['airports'], iata))


def wait_loop(q, processes):
    while True:
        try:
            time.sleep(0.01)
            if all(map(lambda process: not process.is_alive(), processes)):
                break
        except KeyboardInterrupt:
            if q.empty():
                try:
                    print()
                    input('Aún no se ha encontrado nada. Enter para continuar buscando.')
                except KeyboardInterrupt:
                    print()
                    print('La búsqueda se detiene.')
                    break
            else:
                print()
                break


def inter_worker(q_out, vscore, analyzer, origin, dest):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    search = dijsktra.Dijkstra(analyzer['digraph'], origin)
    pstack = dijsktra.pathTo(search, dest)
    if pstack is None:
        return
    list = lt.newList()
    cost = 0.0
    best = None
    if stack.size(pstack) == 1:
        # Puede ser que justo estemos mirando un punto que tiene de vuelta
        # por allí mismo, entonces lo ignoramos
        return
    for _ in range(stack.size(pstack)):
        edge = stack.pop(pstack)
        cost += ed.weight(edge)
        next_airport = findAirportByIATA(analyzer, ed.other(edge, ed.either(edge)))
        lt.addLast(list, next_airport)
    # print('cost < vscore.value', cost, vscore.value, cost < vscore.value)
    if cost < vscore.value:
        vscore.value = cost
        best = list
    if not (best is None):
        q_out.put(best)


def worker(q_in, q_out, vscore, analyzer):
    """
    Find a route to home.
    """
    while not q_in.empty():
        origin, dest = q_in.get()
        inter_worker(q_out, vscore, analyzer, origin, dest)


def findNodeCycles(analyzer, airport):
    vscore = multiprocessing.Value('d')
    vscore.value = sys.maxsize
    adjacents = gr.adjacents(analyzer['digraph'], airport['IATA'])
    print(lt.size(adjacents), 'posibles opciones')
    print(
        'Ctrl+C para detener la búsqueda y usar el mejor hasta el momento',
        end='... ',
        flush=True,
    )

    q_in = multiprocessing.Queue()
    q_out = multiprocessing.Queue()
    for other in lt.iterator(adjacents):
        q_in.put((other, airport['IATA']))

    processes = []
    for i in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=worker, args=(q_in, q_out, vscore, analyzer))
        processes.append(process)
        process.start()

    wait_loop(q_out, processes)

    results = []
    while not q_out.empty():
        results.append(q_out.get())

    [process.terminate() for process in processes]
    [process.join(0) for process in processes]

    if len(results) == 0:
        print('No results')
        return
    return results[-1]  # Último mejor


def convertStackToList(sk):
    list = lt.newList()
    for i in range(stack.size(sk)):
        lt.addLast(list, stack.pop(sk))
    return list


def showInformationAboutFlights(analyzer, flight_list):
    total_distance = 0.0
    for flight in lt.iterator(flight_list):
        iata_from = ed.either(flight)
        iata_to = ed.other(flight, iata_from)
        distance = ed.weight(flight)
        airport_from = findAirportByIATA(analyzer, iata_from)
        airport_to = findAirportByIATA(analyzer, iata_to)
        print('|',
              airport_from['Name'], 'de', airport_from['City'],
              '->',
              airport_to['Name'], 'de', airport_to['City'],
              f' (distance: {distance} km)'
             )
        total_distance += float(distance)
    return total_distance


def getAirportsAffectedForIATA(analyzer, iata):
    """
    Dado el código IATA de un aeropuerto fuera de servicio,
    busca todos los aeropuertos que tienen ruta a/desde él.
    """
    airport_list = lt.newList()
    analyzed_list = lt.newList()
    for edge in lt.iterator(gr.edges(analyzer['digraph'])):
        edge_data = {
            'edge': None,
            'type': None,
            'airport': None
        }
        either = ed.either(edge)
        other = ed.other(edge, either)
        if either == iata:
            edge_data['type'] = 'from'
            edge_data['airport'] = findAirportByIATA(analyzer, other)
        elif other == iata:
            edge_data['type'] = 'to'
            edge_data['airport'] = findAirportByIATA(analyzer, either)
        else:
            continue
        code = edge_data['airport']['IATA'] + '_' + edge_data['type']
        if not lt.isPresent(analyzed_list, code):
            lt.addFirst(analyzed_list, code)
            lt.addLast(airport_list, edge_data)
    return airport_list


# Funciones de ordenamiento
def getTopConnectedAirports(list):
    """
    Ordena una lista de aeropuertos conectados.
    """
    return sa.sort(list, cmpTopConnected)


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)

    Source: https://stackoverflow.com/a/4913653
    """
    lon1, lat1, lon2, lat2 = float(lon1), float(lat1), float(lon2), float(lat2)
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
