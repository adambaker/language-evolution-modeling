import SimPy.Simulation as Sim
from Agent import *
from random import gauss, expovariate

class Population(object):
	all_pops = {}
	
	def __init__(self, mean_x, mean_y, sd_x, sd_y,
			mean_speak, mean_learn, mean_innovation, name='' ):
		self.mean_x = mean_x
		self.mean_y = mean_y
		self.sd_x = sd_x
		self.sd_y = sd_y
		
		self.mean_speak = mean_speak
		self.mean_learn = mean_learn
		self.mean_innovation = mean_innovation
		
		if name == '':
			self.name = 'Population '+ str(len(Population.all_pops))
		else:
			self.name = name
		
		self.agents = []
		Population.all_pops[self.name] = self
		
	def new_agent(self):
		x = gauss(self.mean_x, self.sd_x)
		y = gauss(self.mean_y, self.sd_y)
		speak = expovariate(1.0/self.mean_speak)
		learn = expovariate(1.0/self.mean_learn)
		innovation = expovariate(1.0/self.mean_innovation)
		
		agent = Agent(x, y, speak, learn, innovate)
		self.agents.append(agent)
		
		Sim.activate(agent, agent.go())
		return agent
	
	def add_agent(self, agent):
		self.agents.append(agent)
		
	def all_agents(self):
		return self.agents
	
	def num_agents(self):
		return len(self.agents)
	
	def lang_plot_list(self):
		plot_list = []
		for agent in self.agents:
			plot_list.append([agent.lang_x, agent.lang_y])
			
		return plot_list
	
class LinePopulation(Population):
	def __init__( self, mean_x, mean_y, sd_x, sd_y,
			mean_speak, mean_learn, mean_innovation, mean_loc, loc_sd,
			mean_talk_radius, name='' ):
		Population.__init__(self, mean_x, mean_y, sd_x, sd_y, mean_speak,
							mean_learn, mean_innovation, name)
		self.mean_loc = mean_loc
		self.loc_sd = loc_sd
		self.mean_talk_radius = mean_talk_radius
		
	def add_agent(self, agent):
		agent.location = gauss(self.mean_loc, self.loc_sd)
		self.agents.append(agent)
	
	def new_agent(self):
		x = gauss(self.mean_x, self.sd_x)
		y = gauss(self.mean_y, self.sd_y)
		speak = expovariate(1.0/self.mean_speak)
		learn = expovariate(1.0/self.mean_learn)
		innovation = expovariate(1.0/self.mean_innovation)
		
		location = gauss(self.mean_loc, self.loc_sd)
		radius = expovariate(1.0/self.mean_talk_radius)
		
		agent = LineAgent(x, y, speak, learn, innovation, location, radius)
		self.agents.append(agent)
		
		Sim.activate(agent, agent.go())
		return agent
	
class LangRelPop(LinePopulation):
	def new_agent(self):
		x = gauss(self.mean_x, self.sd_x)
		y = gauss(self.mean_y, self.sd_y)
		speak = expovariate(1.0/self.mean_speak)
		learn = expovariate(1.0/self.mean_learn)
		innovation = expovariate(1.0/self.mean_innovation)
		
		location = gauss(self.mean_loc, self.loc_sd)
		radius = expovariate(1.0/self.mean_talk_radius)
		
		agent = LangRelativeAgent(x, y, speak, learn, innovation, location, radius)
		self.agents.append(agent)
		
		Sim.activate(agent, agent.go())
		return agent
