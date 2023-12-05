import heapq
from collections import defaultdict
import sys
import json
from geopy.geocoders import Nominatim
from deep_translator import GoogleTranslator
from AdjacencyList import AdjacencyList
import PySimpleGUI as sg
import os.path

def bellman_ford(source, graph):
    '''
    Bellman ford algorithm implementation

    Parameters
    ----------
    source : string
        ID of source node.
    graph : AdjacencyList
        Adjacency list representing our graph.

    Returns
    -------
    distances : {nodeID, {shortest distance to it, predecessor node}}

    '''
    # Initialize distances with infinity for all nodes
    distances = {node: (float('inf'), None) for node in graph}
    distances[source] = (0, None)

    # Relax edges repeatedly
    for _ in range(len(graph) - 1):
        for u in graph:
            for v, weight in graph[u].items():
                if distances[u][0] + weight < distances[v][0]:
                    distances[v] = (distances[u][0] + weight, u)

    # Cycles don't need to be checked for since we are dealing with strictly positive weights

    return distances


def dijkstra(source, graph):
    '''
    Dijkstra's algorithm implementation

    Parameters
    ----------
    source : string
        ID of source node.
    graph : AdjacencyList
        Adjacency list representing our graph.

    Returns
    -------
    distances : {nodeID, {shortest distance to it, predecessor node}}

    '''
    distances = {node: (float('inf'), None) for node in graph}  # distance + predecessor node

    # Start with the source node
    distances[source] = (0, None)

    pq = [(0, source)]  # priority queue used for optimal time complexity

    while pq:
        dist, node = heapq.heappop(pq)

        # Skip if the distance is not up-to-date
        if dist > distances[node][0]:
            continue

        for neighbor_node, edge_weight in graph[node].items():
            new_distance = dist + edge_weight

            if new_distance < distances[neighbor_node][0]:
                distances[neighbor_node] = (new_distance, node)
                heapq.heappush(pq, (new_distance, neighbor_node))

    return distances

def print_distances(paths):
    for node, distance in paths.items():
        print(f"{node}: {distance}")
def retrieve_path(distances, src, dest):
    # works backwards from each predecessor node to retrace route
    path = []
    current = dest
    while current:  # for the specific algorithm run, src node will have a None value
        path.append(current)
        current = distances[current][1]
    path.reverse()  # currently in backwards order
    return path
def print_node_locations(node_map, node_numbers):
    out_list = []
    for node_number in node_numbers:
        # Retrieve the location for the current node
        lat, lon = node_map[node_number]
        print(f"{node_number}: {{Longitude: {lon}, Latitude: {lat}}}")
        geolocator = Nominatim(user_agent="school-project")
        location = geolocator.reverse((lat, lon))  # find location from longitude and latitude
        translator = GoogleTranslator(source='auto', target='en')
        address = translator.translate(location.address)  # translate address from chinese to english
        print(address)
        out_list.append(f"{node_number}: {{Longitude: {lon}, Latitude: {lat}}}" + "; " + address)
    return out_list
        
def main():
    try:
        # Get list of files in folder
        file_list = os.listdir("data")
    except:
        file_list = []

    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join("data", f))
           and f.lower().endswith((".txt"))
    ]

    
    list_column = [
        [
            sg.Listbox(values=fnames, enable_events=True, size=(40, 40), key="-LIST-")
        ],
    ]
    numbers_column = [
        [sg.InputText(key='input_text1'), sg.Button('Enter1', bind_return_key=True)],
        [sg.Text(size=(40, 1), key='output_text1')],
        [sg.InputText(key='input_text2'), sg.Button('Enter2', bind_return_key=True)],
        [sg.Text(size=(40, 1), key='output_text2')],
    ]

    image_viewer_column1 = [
        [sg.Text("Choose a city from the list on the left")],
        [sg.Text(size=(40, 20), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]
    image_viewer_column2 = [
        [sg.Text("Enter your source and destintation nodes.")],
        [sg.Text(size=(40, 20), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]

    layout1 = [
        [
            sg.Column(list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column1),
        ],
    ]
    layout2 = [
        [
            sg.Column(numbers_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column2),
        ],
    ]
    path_list_column = []
    infrmation_column = []
    layout3 = []
    
    window = sg.Window("Choose City & Algorithm", layout1)

    updates = 0
    graph = AdjacencyList()
    state = 1
    fileopened = False
    coordfileopened = False
    cityname = ""
    algo = ""
    src = 0
    dest = 0
    waiting_for_nums1 = True
    waiting_for_nums2 = True
    window3updated = False
    window4updated = False
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        IP = False
        #Choose city from list
        algorithms = ["Dijkstra","Bellman-Ford"]
        if event == "-LIST-" and state == 1:  # A city was chosen from the listbox
            state = 2
            IP = True
            try:
                cityname = values["-LIST-"][0]
                window["-TOUT-"].update(cityname)
            except:
                pass
        path = "data/" + cityname
        coordinates = cityname[:-4] + "_co.txt"
        coordinates_path = "coords/" + coordinates
        if not coordfileopened:
            with open(coordinates_path, 'r') as file:
                file_content = file.read().strip()
                lines = file_content.split("\n")
    
                # Remove the header lines
                data_lines = lines[6:]
    
                # Create a map with key as node number and value as a pair of latitude/longitude
                node_locations = {}
                for i, line in enumerate(data_lines):
                    lat, lon = map(float, line.split())
                    node_locations[f"{i + 1}"] = (lat, lon)
            coordfileopened = True

        try:
            if not fileopened:
                #Open file
                print("path: " + path)
                with open(path, 'r') as file:
                    # Skip the header lines
                    for _ in range(5):
                        next(file)

                    # Read each line until the end of the file
                    for line in file:
                        src, dest, weight = line.split()
                        graph.insert(src, dest, float(weight))

                    print(f"Great, your data has been loaded. {cityname} can be described by X nodes and Y edges\n")
                fileopened = True

        except FileNotFoundError:
            print("Error opening file")
            sys.exit(1)
        if state == 2:
            #Display algorithms list
            window["-LIST-"].update(algorithms)

        if event == "-LIST-" and state == 2 and not IP:  # A algorithm was chosen from the listbox
            try:
                algo = values["-LIST-"][0]
                window["-TOUT-"].update(cityname +": " + algo + "\n")
            except:
                pass
            if algo == "Dijkstra":
                state = 3
                window.Close()
                window = sg.Window("Input Source and Destination Nodes", layout2)
            elif algo == "Bellman-Ford":
                state = 4
                window.Close()
                window = sg.Window("Input Source and Destination Nodes", layout2)
        if state == 3 or state == 4:
            if waiting_for_nums1 or waiting_for_nums2:
                if event == 'Enter1' and waiting_for_nums1:
                    src = (values['input_text1'])
                    waiting_for_nums1 = False
                if event == 'Enter2' and waiting_for_nums2:
                    dest = (values['input_text2'])
                    waiting_for_nums2 = False
            if not waiting_for_nums1 and not waiting_for_nums2:
                if state == 3:
                    distances = dijkstra(src, graph.map)
                if state == 4:
                    distances = bellman_ford(src, graph.map)
                
                   
                route = retrieve_path(distances, src, dest)
                print(
                    f"Here is the shortest route to get to your destination, it requires {distances[dest][0]:.2f} meters.\n")
                shortest_path = ""
                shortest_path += route[0]
                
                for i in range(1, len(route)):
                    shortest_path += " -> "
                    shortest_path += route[i]
                if not window3updated:
                    path_list_column = [
                        [sg.Text("Node path:")],
                        [sg.Column(layout=[
                            [sg.Multiline(default_text=shortest_path, size=(90, 120), key='path_text', autoscroll=True)],
                        ], scrollable=True, vertical_scroll_only=True)],
                    ]
                    information_column = [
                        [sg.Text("Node information:")],
                        [sg.Column(layout=[
                            [sg.Listbox(values=["Node information will display here","Please wait, this may take a while..."], size=(90, 120), key='listbox', enable_events=True)],
                        ], scrollable=True, vertical_scroll_only=True)],
                    ]
                    layout3 = [
                        [
                            sg.Column(path_list_column),
                            sg.VSeperator(),
                            sg.Column(information_column),
                        ],
                    ]
                    window.Close()
                    window = sg.Window("Path Information", layout3)
                    while True:
                        event, values = window.read(timeout=100)
                        if event == "Exit" or event == sg.WIN_CLOSED:
                            break
                        if not window4updated:
                            node_info_list  = print_node_locations(node_locations, route)
                            window.Close()
                            path_list_column2 = [
                                [sg.Text("Node path:")],
                                [sg.Column(layout=[
                                    [sg.Multiline(default_text=shortest_path, size=(90, 120), key='path_text', autoscroll=True)],
                                ], scrollable=True, vertical_scroll_only=True)],
                            ]
                            information_column2 = [
                                [sg.Text("Node information:")],
                                [sg.Column(layout=[
                                    [sg.Listbox(values=node_info_list, size=(90, 120), key='listbox', enable_events=True)],
                                ], scrollable=True, vertical_scroll_only=True)],
                            ]
                            layout4 = [
                                [
                                    sg.Column(path_list_column2),
                                    sg.VSeperator(),
                                    sg.Column(information_column2),
                                ],
                            ]
                            window = sg.Window("Path Information", layout4)
                            window4updated = True
               
                


    window.close()


if __name__ == "__main__":
    main()