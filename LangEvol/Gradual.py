import SimPy.Simulation as Sim
from Agent import LineAgent
from Plot import Plotter
from Population import LinePopulation
import random
import time
import math

params = {
	#inital language values
	'white x mean': 100.0,
	'white y mean': 100.0,
	'white x std dev': 10.0,
	'white y std dev': 10.0,
		
	'bozal0 x mean': 350.0,
	'bozal0 y mean': 750.0,
	'bozal0 x std dev': 100.0,
	'bozal0 y std dev': 100.0,
	'bozal1 x mean': 750.0,
	'bozal1 y mean': 350.0,
	'bozal1 x std dev': 100.0,
	'bozal1 y std dev': 100.0,
	
	#population structure parameters
	'white mean loc': 100.0,
	'white loc sd': 20.0,
	'seasoned mean loc': 220.0,
	'seasoned loc sd': 50.0,
	'bozal mean loc': 300.0,
	'bozal loc sd': 30.0,
	
	#population adjustment parameters
	'update period': 300,
	'proportion seasoned': 0.3, #num seasoned = proportion * white population
	#South Carolina population figures. Each agent is 100 people.
	#starting population numbers
	# 'num white': 7,
	# 'num slaves': 2,
	# 'pop schedule': [3000.0*x for x in range(1, 9)],
	# 'white pop targets': [14, 38, 55, 98, 203, 386, 716, 1402],
	# 'slave pop targets': [5, 28, 86, 216, 406, 579, 1073, 1089],
	#Suriname population figures. Each agent is 10 people.
	'num white': 20,
	'num slaves': 20,
	'pop schedule': [3000.0*x for x in range(1, 7)] + [20000.0],
	'white pop targets': [150, 44, 75, 84, 109, 122, 145],
	'slave pop targets': [300, 101, 893, 1167, 1819, 2514, 3343],
	
	#agent behavior parameters
	'white talk radius': 50.0,
	'seasoned talk radius': 20.0,
	'bozal talk radius': 5.0,
	'mean speak': 1.0,
	'mean learn': 0.03,
	'mean innovation': 0.3,
	
	#other sim parameters
	'stop time': 30000.0,
	'plot period': 3000.0,
	'random seed': time.time()
}

class PopAdjuster(Sim.Process):
	def __init__(self, white, seasoned, bozal0, bozal1, period, schedule, 
					white_pops, slave_pops, season_prop ):
		Sim.Process.__init__(self)
		self.white = white
		self.seasoned = seasoned
		self.bozal0 = bozal0
		self.bozal1 = bozal1
		self.period = period
		self.schedule = schedule
		self.white_pops = white_pops
		self.slave_pops = slave_pops
		self.season_prop = season_prop
	
	def go(self):
		stop = self.schedule[-1]
		while Sim.now() < stop:
			next_target_time = self.schedule.pop(0)
			white_target = self.white_pops.pop(0)
			slave_target = self.slave_pops.pop(0)
			
			slaves = self.bozal0.num_agents()+self.bozal1.num_agents()+self.seasoned.num_agents()
			
			num_updates = math.floor((next_target_time-Sim.now())/self.period)
			
			white_adjust = int((white_target-self.white.num_agents())//num_updates)
			slave_adjust = int((slave_target-slaves)//num_updates)
			
			while Sim.now() < next_target_time:
				yield Sim.hold, self, self.period
				self.adjust_pops(white_adjust, slave_adjust)
				
			#take care of remainder
			slaves = self.bozal0.num_agents()+self.bozal1.num_agents()+self.seasoned.num_agents()
			white_adjust = (white_target-self.white.num_agents())
			slave_adjust = (slave_target-slaves)
			self.adjust_pops(white_adjust, slave_adjust)
			
	def adjust_pops(self, white_adjust, slave_adjust):
		if white_adjust >= 0:
			for i in range(white_adjust):
				self.white.new_agent()
		else:
			for i in range(-white_adjust):
				gone = random.choice(self.white.all_agents())
				self.white.all_agents().remove(gone)
		if slave_adjust >= 0:
			for i in range(slave_adjust):
				if(self.bozal0.num_agents() < self.bozal1.num_agents()):
					self.bozal0.new_agent()
				else:
					self.bozal1.new_agent()
		else:
			for i in range(-slave_adjust):
				if(self.bozal0.num_agents() < self.bozal1.num_agents()):
					gone = random.choice(self.bozal1.all_agents())
					self.bozal1.all_agents().remove(gone)
				else:
					gone = random.choice(self.bozal0.all_agents())
					self.bozal0.all_agents().remove(gone)
				
		num_seasoned = int(math.ceil(self.season_prop*self.white.num_agents()))
		if( num_seasoned > self.seasoned.num_agents() ):
			self.get_seasoned( num_seasoned-self.seasoned.num_agents(), 
								self.white, self.bozal0, self.bozal1, self.seasoned )
	
	@staticmethod
	def get_seasoned( number, white, bozal0, bozal1, seasoned ):
		def distance( agent ):
			x = white.mean_x - agent.lang_x
			y = white.mean_y - agent.lang_y
			return math.hypot(x, y)
		
		new_seasoned = []
		for i, agent in enumerate(bozal0.all_agents() + bozal1.all_agents()):
			if i < number:
				new_seasoned.append(agent)
			else:
				if i == number:
					new_seasoned.sort(lambda x,y:cmp(distance(x),distance(y)))
				worst = new_seasoned[-1]
				if( distance(agent) < distance(worst) ):
					new_seasoned.pop() #removes worst
					new_seasoned.append(agent)
					new_seasoned.sort(lambda x,y:cmp(distance(x),distance(y)))
		
		for agent in new_seasoned:
			try:
				bozal0.all_agents().remove(agent)
			except ValueError:
				#musta been in bozal1
				bozal1.all_agents().remove(agent)
			seasoned.add_agent(agent)
		LineAgent.all_agents.sort(lambda x,y:cmp(x.location,y.location))

def main():
	print 'Initializing...'
	Sim.initialize()
		
	white = LinePopulation( params['white x mean'], params['white y mean'],
				params['white x std dev'], params['white y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['white mean loc'], 
				params['white loc sd'], params['white talk radius'], 'white' )
	
	seasoned = LinePopulation( 0.0, 0.0, 0.0, 0.0, params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['seasoned mean loc'], 
				params['seasoned loc sd'], params['seasoned talk radius'], 'seasoned' )
	
	bozal0 = LinePopulation( params['bozal0 x mean'], params['bozal0 y mean'],
				params['bozal0 x std dev'], params['bozal0 y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['bozal mean loc'], 
				params['bozal loc sd'], params['bozal talk radius'], 'bozal 0')
	
	bozal1 = LinePopulation( params['bozal1 x mean'], params['bozal1 y mean'],
				params['bozal1 x std dev'], params['bozal1 y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['bozal mean loc'], 
				params['bozal loc sd'], params['bozal talk radius'], 'bozal 1' )
	
	for i in range(params['num white']):
		white.new_agent()
	for i in range(params['num slaves']):
		if i%2 == 0:
			bozal0.new_agent()
		else:
			bozal1.new_agent()
	
	adjuster = PopAdjuster( white, seasoned, bozal0, bozal1, params['update period'],
					params['pop schedule'], params['white pop targets'],
					params['slave pop targets'], params['proportion seasoned'] )
	Sim.activate( adjuster, adjuster.go() )
	
	number = math.ceil(params['proportion seasoned']*white.num_agents())
	adjuster.get_seasoned( number, white, bozal0, bozal1, seasoned )
	
	plotter = Plotter('gradual', params['plot period'], params['stop time'], params)
	Sim.activate( plotter, plotter.go() )
	
	print 'Simulating...'
	Sim.simulate(until=params['stop time'])
	print 'Simulation Complete at t=%s' % Sim.now()
	
	plotter.cleanup()

if __name__ == '__main__':
	main()
