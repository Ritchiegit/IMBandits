from random import choice, random, sample
import numpy as np
import networkx as nx

class ArmBaseStruct(object):
    def __init__(self, armID):
        self.armID = armID
        self.totalReward = 0.0
        self.numPlayed = 0
        self.averageReward  = 0.0
        self.p_max = 1
       
    def updateParameters(self, reward):
        self.totalReward += reward
        self.numPlayed +=1
        self.averageReward = self.totalReward/float(self.numPlayed)


class UCB1Struct(ArmBaseStruct):    
    def getProb(self, allNumPlayed):
        if self.numPlayed==0:
            return 0
        else:
            p = self.totalReward / float(self.numPlayed) + 0.01*np.sqrt(3*np.log(allNumPlayed) / (2.0 * self.numPlayed))
            if p > self.p_max:
                p = self.p_max
                # print 'p_max'
            return p

        
class eGreedyArmStruct(ArmBaseStruct):
    def getProb(self, allNumPlayed = None):
        if self.numPlayed == 0:
            pta = 0
        else:
            #print 'GreedyProb', self.totalReward/float(self.numPlayed)
            pta = self.totalReward/float(self.numPlayed)
            if pta > self.p_max:
                pta = self.p_max
        return random()
        
class UCB1Algorithm:
    def __init__(self, G, seed_size, oracle, feedback = 'edge'):
        self.G = G
        self.seed_size = seed_size
        self.oracle = oracle
        self.feedback = feedback
        self.arms = {}
        #Initialize P
        self.currentP =nx.DiGraph()
        for (u,v) in self.G.edges():
            self.arms[(u,v)] = UCB1Struct((u,v))
            self.currentP.add_edge(u,v, weight=0)

        self.TotalPlayCounter = 0
        
    def decide(self, feature_vec):
        self.TotalPlayCounter +=1
        S = self.oracle(self.G, self.seed_size, self.currentP)
        return S       
         
    def updateParameters(self, S, live_nodes, live_edges, feature_vec): 
        for u in live_nodes:
            for (u, v) in self.G.edges(u):
                if (u,v) in live_edges:
                    self.arms[(u, v)].updateParameters(reward=live_edges[(u,v)])
                else:
                    self.arms[(u, v)].updateParameters(reward=0)
                #update current P
                #print self.TotalPlayCounter
                self.currentP[u][v]['weight'] = self.arms[(u,v)].getProb(self.TotalPlayCounter) 

    def getP(self):
        return self.currentP

class eGreedyAlgorithm:
    def __init__(self, G, seed_size, oracle, epsilon, feedback = 'edge'):
        self.G = G
        self.seed_size = seed_size
        self.oracle = oracle
        self.feedback = feedback
        self.arms = {}
        #Initialize P
        self.currentP =nx.DiGraph()
        for (u,v) in self.G.edges():
            self.arms[(u,v)] = eGreedyArmStruct((u,v))
            self.currentP.add_edge(u,v, weight=random())

        self.TotalPlayCounter = 0
        self.epsilon = epsilon

    def decide(self, feature_vec):
        arm_Picked = None
        if random() < self.epsilon: # random exploration
            S = sample(list(self.G.nodes()), self.seed_size)
        else:
            S = self.oracle(self.G, self.seed_size, self.currentP)# self.oracle(self.G, self.seed_size, self.arms)
        return S

    def updateParameters(self, S, live_nodes, live_edges, feature_vec): 
        for u in live_nodes:
            for (u, v) in self.G.edges(u):
                if (u,v) in live_edges:
                    self.arms[(u, v)].updateParameters(reward=live_edges[(u,v)])
                else:
                    self.arms[(u, v)].updateParameters(reward=0)
                #update current P
                #print self.TotalPlayCounter
                self.currentP[u][v]['weight'] = self.arms[(u,v)].getProb(self.TotalPlayCounter) 
    def getP(self):
        return self.currentP