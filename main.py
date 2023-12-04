import heapq
from collections import defaultdict
import sys
import json

from AdjacencyList import AdjacencyList
import PySimpleGUI as sg
import os.path

def dijkstra(source, graph):
    distances = {node: (float('inf'), None) for node in graph}  # distance + predecessor node

    # Start with the source node
    distances[source] = (0, None)
    pq = [(0, source)]

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
    path = []
    current = dest
    while current:  # for the specific algorithm run, src node will have a None value
        path.append(current)
        current = distances[current][1]
    path.reverse()  # currently in backwards order
    return path
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
            sg.In(size=(40, 1), enable_events=True, key="-NODES-"),
        ],
        [
            sg.In(size=(40, 1), enable_events=True, key="-NODED-"),
        ],
        [
            sg.Listbox(values=fnames, enable_events=True, size=(40, 19), key="-LIST-")
        ],
    ]

    image_viewer_column = [
        [sg.Text("Choose a city from the list on the left")],
        [sg.Text(size=(40, 20), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]

    layout = [
        [
            sg.Column(list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ],
    ]

    window = sg.Window("City Viewer", layout)

    graph = AdjacencyList()
    state = 1
    fileopened = False
    cityname = ""
    algo = ""
    src = 0
    dest = 0
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
                #window["-IMAGE-"].update(filename=cityname)
            except:
                pass
        path = "data/" + cityname
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
                window["-TOUT-"].update(cityname +": " + algo + "\n" +
                                        f"Enter a source node in the top left text box, \n"
                                        f"please choose an integer from 1 to {len(graph.map)}\n")
                waiting = True

                while waiting:
                    src = (int)(values["-NODES-"])
                    dest = (int)(values["-NODED-"])
                    if(src != 0 and dest != 0):
                        waiting = False
            except:
                pass
            if algo == "Dijkstra":
                state = 3
                distances = dijkstra(src, graph.map)
                route = retrieve_path(distances, src, dest)

                print(f"Here is the shortest route to get to your destination, it requires {distances[dest][0]:.2f} meters.\n")
                shortest_path = ""
                shortest_path += route[0]

                for i in range(1, len(route)):
                    shortest_path += "->"
                    shortest_path += route[i]

                print(shortest_path)
        if state == 3:
            # Display algorithms list
            window["-LIST-"].update([])
    window.close()


if __name__ == "__main__":
    main()