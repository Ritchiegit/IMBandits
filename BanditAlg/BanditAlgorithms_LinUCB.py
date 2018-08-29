from random import choice, random, sample
import numpy as np
import networkx as nx
from BanditAlg.BanditAlgorithms import ArmBaseStruct

class LinUCBUserStruct:
	def __init__(self, featureDimension, lambda_, userID, RankoneInverse = False):
		self.userID = userID
		self.d = featureDimension
		self.A = lambda_*np.identity(n = self.d)
		self.b = np.zeros(self.d)
		self.AInv = np.linalg.inv(self.A)
		self.UserTheta = np.zeros(self.d)

		self.RankoneInverse = RankoneInverse

		self.pta_max = 1
		
	def updateParameters(self, articlePicked_FeatureVector, click):
		self.A += np.outer(articlePicked_FeatureVector, articlePicked_FeatureVector)
		self.b += articlePicked_FeatureVector*click
		if self.RankoneInverse:
			temp = np.dot(self.AInv, articlePicked_FeatureVector)
			self.AInv = self.AInv - (np.outer(temp,temp))/(1.0+np.dot(np.transpose(articlePicked_FeatureVector),temp))
		else:
			self.AInv =  np.linalg.inv(self.A)

		self.UserTheta = np.dot(self.AInv, self.b)
		
	def getTheta(self):
		return self.UserTheta
	
	def getA(self):
		return self.A

	def getProb(self, alpha, article_FeatureVector):
		mean = np.dot(self.UserTheta,  article_FeatureVector)
		var = np.sqrt(np.dot(np.dot(article_FeatureVector, self.AInv),  article_FeatureVector))
		pta = mean + alpha * var
		if pta > self.pta_max:
			pta = self.pta_max
		return pta

class N_LinUCBAlgorithm:
	def __init__(self, G, seed_size, oracle, dimension, alpha,  lambda_ , FeatureScaling, feedback = 'edge'):
		self.G = G
		self.oracle = oracle
		self.seed_size = seed_size

		self.dimension = dimension
		self.alpha = alpha
		self.lambda_ = lambda_
		self.FeatureScaling = FeatureScaling
		self.feedback = feedback

		self.currentP =nx.DiGraph()
		self.users = {}  #Nodes
		for u in self.G.nodes():
			self.users[u] = LinUCBUserStruct(dimension, lambda_ , u)
			for v in self.G[u]:
				self.currentP.add_edge(u,v, weight=random())

	def decide(self):
		S = self.oracle(self.G, self.seed_size, self.currentP)
		return S

	def updateParameters(self, S, live_nodes, live_edges, feature_vec):
		for u in S:
			for (u, v) in self.G.edges(u):
				if (u,v) in live_edges:
					reward = live_edges[(u,v)]
				else:
					reward = 0
				self.users[u].updateParameters(feature_vec, reward)
				self.currentP[u][v]['weight']  = self.users[v].getProb(self.alpha, feature_vec)
	def getCoTheta(self, userID):
		return self.users[userID].UserTheta
	def getP(self):
		return self.currentP		

class LinUCBAlgorithm:
	def __init__(self, G, seed_size, oracle, dimension, alpha,  lambda_ , feedback = 'edge'):
		self.G = G
		self.oracle = oracle
		self.seed_size = seed_size

		self.dimension = dimension
		self.alpha = alpha
		self.lambda_ = lambda_
		self.feedback = feedback

		self.currentP =nx.DiGraph()
		self.USER = LinUCBUserStruct(dimension, lambda_ , 0)
		for u in self.G.nodes():
			for v in self.G[u]:
				self.currentP.add_edge(u,v, weight=0)

	def decide(self):
		S = self.oracle(self.G, self.seed_size, self.currentP)
		return S

	def updateParameters(self, S, live_nodes, live_edges, feature_vec):
		for u in S:
			for (u, v) in self.G.edges(u):
				if (u,v) in live_edges:
					reward = live_edges[(u,v)]
				else:
					reward = 0
				self.USER.updateParameters(feature_vec, reward)
				self.currentP[u][v]['weight']  = self.USER.getProb(self.alpha, feature_vec)
	def getCoTheta(self, userID):
		return self.USER.UserTheta
	def getP(self):
		return self.currentP