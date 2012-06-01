import SimPy.Simulation as Sim
from Agent import LangRelativeAgent as Agent
from Plot import Plotter
from Population import LangRelPop
import random
import time

params = {
	#inital language values
	'white x mean': 100.0,
	'white y mean': 100.0,
	'white x std dev': 10.0,
	'white y std dev': 10.0,
	
	'seasoned x mean': 150.0,
	'seasoned y mean': 150.0,
	'seasoned x std dev': 25.0,
	'seasoned y std dev': 25.0,
	
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

	'num white': 50,
	'num seasoned': 50,
	'num bozal': 300,
	
	#agent behavior parameters
	'white talk radius': 50.0,
	'seasoned talk radius': 20.0,
	'bozal talk radius': 5.0,
	'mean speak': 0.1,
	'mean learn': 0.03,
	'mean innovation': 0.3,
	'lang tolerance': 20.0,
	
	#other sim parameters
	'stop time': 10000.0,
	'plot period': 1000.0,
	'random seed': time.time()
}

def main():
	print 'Initializing...'
	Sim.initialize()
	
	Agent.lang_tolerance = params['lang tolerance']
	
	white = LangRelPop( params['white x mean'], params['white y mean'],
				params['white x std dev'], params['white y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['white mean loc'], 
				params['white loc sd'], params['white talk radius'], 'white' )
	
	seasoned = LangRelPop( params['seasoned x mean'], params['seasoned y mean'],
				params['seasoned x std dev'], params['seasoned y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['seasoned mean loc'], 
				params['seasoned loc sd'], params['seasoned talk radius'], 'seasoned' )
	
	bozal0 = LangRelPop( params['bozal0 x mean'], params['bozal0 y mean'],
				params['bozal0 x std dev'], params['bozal0 y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['bozal mean loc'], 
				params['bozal loc sd'], params['bozal talk radius'], 'bozal 0')
	
	bozal1 = LangRelPop( params['bozal1 x mean'], params['bozal1 y mean'],
				params['bozal1 x std dev'], params['bozal1 y std dev'], params['mean speak'], 
				params['mean learn'], params['mean innovation'], params['bozal mean loc'], 
				params['bozal loc sd'], params['bozal talk radius'], 'bozal 1' )
	
	for i in range(params['num white']):
		white.new_agent()	
	for i in range(params['num seasoned']):
		seasoned.new_agent()
	for i in range(params['num bozal']):
		if i%2 == 0:
			bozal0.new_agent()
		else:
			bozal1.new_agent()
	
	plotter = Plotter('centripetal by lang', params['plot period'], params['stop time'], params)
	Sim.activate( plotter, plotter.go() )
	
	print 'Simulating...'
	Sim.simulate(until=params['stop time'])
	print 'Simulation Complete at t=%s' % Sim.now()
	
	plotter.cleanup()

if __name__ == '__main__':
	main()
