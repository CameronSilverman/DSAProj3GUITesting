class AdjacencyList:
    def __init__(self):
        # Python dictionary to store the adjacency list
        self.map = {}

    def insert(self, src, dest, weight):
        # Adding the neighbor with the given weight to the node
        if src not in self.map:
            self.map[src] = {}
        self.map[src][dest] = weight 