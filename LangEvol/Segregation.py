import SimPy.Simulation as Sim
from Agent import LineAgent
from Plot import Plotter
from Population import LinePopulation
import random
import time

params = {
	#inital language values
	#initial x and y values are 500.0 for all trials
	'initial x std dev': 40.0,
	'initial y std dev': 40.0,
	
	#population structure parameters
	'pop1 mean loc': 700.0,
	'pop2 mean loc': 300.0,
	'pop1 loc sd': 35.0,
	'pop2 loc sd': 35.0,
	#Population 0's mean location is 500.0 for all trials
	'pop0 loc sd': 50.0,
	'num agents': 300,
	'pop1 proportion': 0.7,
	
	#agent behavior parameters
	'mean talk radius': 50.0,
	'mean speak': 1.0,
	'mean learn': 0.03,
	'mean innovation': 0.5,
	
	#other sim parameters
	'stop time': 200000.0,
	'segregate time': 20000.0,
	'plot period': 20000.0,
	'random seed': time.time()
}

class Segregator(Sim.Process):			
	def go(self):
		yield Sim.hold, self, params['segregate time']
		random.shuffle(LineAgent.all_agents)
		
		pop1 = LinePopulation( 500.0, 500.0, 20.0, 20.0, params['mean speak'], 
							params['mean learn'], params['mean innovation'],
							params['pop1 mean loc'], params['pop1 loc sd'],
							params['mean talk radius'])
		pop2 = LinePopulation( 500.0, 500.0, 20.0, 20.0, params['mean speak'], 
							params['mean learn'], params['mean innovation'],
							params['pop2 mean loc'], params['pop2 loc sd'], 
							params['mean talk radius'])
		for agent in LineAgent.all_agents:
			if len(pop1.all_agents()) < params['pop1 proportion']*LineAgent.num_agents():
				pop1.add_agent(agent)
			else:
				pop2.add_agent(agent)
				
		LineAgent.all_agents.sort(lambda x,y:cmp(x.location,y.location))
		LinePopulation.all_pops.pop('Population 0')

def initialize():
	print 'Initializing...'
	Sim.initialize()
	
	print 'Random seed: ' + repr(params['random seed'])
	random.seed(params['random seed'])
	
	pop0 = LinePopulation( 500.0, 500.0, params['initial x std dev'], params['initial y std dev'], 
							params['mean speak'], params['mean learn'], params['mean innovation'],
							500.0, params['pop0 loc sd'], params['mean talk radius'] )
	
	for i in range(params['num agents']):
		pop0.new_agent()
	
	segregator = Segregator()
	Sim.activate( segregator, segregator.go() )

def simulate():
	print 'Simulating...'
	Sim.simulate(until=params['stop time'])
	print 'Simulation Complete at t=%s' % Sim.now()
	
if __name__ == '__main__':
	initialize()
	
	plotter = Plotter('segregate', params['plot period'], params['stop time'], params)
	Sim.activate( plotter, plotter.go() )
	
	simulate()
	
	plotter.cleanup()
