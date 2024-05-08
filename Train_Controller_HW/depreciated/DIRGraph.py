import networkx as nx
import matplotlib.pyplot as plt
import os


#on polarity edge case:
    #greenline:
        #curr++, read txt
    #redline:
        #if beacon: curr_override
        #else: calc block number from traveled since beacon

#return:
    #speed limit
    #distance alloted from authority


#graph of nodes for each line
#node data: block number (int)
#use node to get block data from a list
#yard=0


class base_DIRGraph():
    def __init__(self):
        pass
#================================================================================
class Graph_RedLine():
    def __init__(self):
        path = os.getcwd()
        print(path)
        
        self.curr = 0#curr block on
        self.direction=True #0:down, 1:up
        self.G = nx.read_edgelist('Resources/graph_data/redline.txt', nodetype=int, create_using=nx.Graph())
        
        pass
    def curr_update(self):
        neigh = [n for n in line.G.neighbors(self.curr)]
        if len(neigh) == 0: raise Exception("TrainC: DIRGraph: no neighbors")
        elif len(neigh) == 1: self.curr = neigh[0]
        else:
            if self.direction: self.curr = neigh[0]#up
        
    #beacon
    def curr_override(self, index):
        self.curr = index
        
    def debug_show(self):
        print(self.G.edges(data=True))
        nx.draw_spring(self.G, with_labels = True)
        plt.savefig("filename.png")
        plt.show()



#================================================================================
class Graph_GreenLine():
    def __init__(self):
        self.G = nx.DiGraph()
        pass
    def Greenline_grab(self, index):
        pass



#================================================================================
if __name__ == "__main__":
    line = Graph_RedLine()
    print([n for n in line.G.neighbors(76)])
    print([n for n in line.G.neighbors(76)][0])
    line.debug_show()