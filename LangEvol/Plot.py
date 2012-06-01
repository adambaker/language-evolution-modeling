from SimPy.SimPlot import *
import SimPy.Simulation as Sim
from Population import Population
import os

class Plotter(Sim.Process):
	def __init__(self, directory, period, stop, parameters):
		Sim.Process.__init__(self)
		self.numplots = 0
		self.directory = directory+'/trial'+str(trial_number(directory))
		os.makedirs( self.directory )
		self.period = period
		self.stop = stop
		
		param_file = open( self.directory+'/params.txt', 'w')
		for key in parameters.keys():
			param_file.write( key +':\t\t' + repr(parameters[key]) + '\n' )
			
		param_file.close()
		
		self.means = open(self.directory+'/means.txt', 'w')
	
	def go(self):
		while True:
			print '\t' + str(100*Sim.now()/self.stop) + '%'
			self.plot()
			yield Sim.hold, self, self.period


	def plot(self):
		colors = iter(['red', 'green', 'blue', 'black', 'yellow', 'cyan', 'magenta'])
		plt=SimPlot()                                       # step 1
		title = '\nTime: '+str(Sim.now()) +'\n'
		plt.root.title(title)				           # step 3
		lines = []
		
		self.means.write('Time ' + str(Sim.now()) + ':\n')
		
		for name, population in Population.all_pops.items():
			if population.num_agents() == 0:
				continue
			plot_list = population.lang_plot_list()
			
			#make scatter chart of this population's language values
			color = colors.next()
			title += name + ': ' + color +';  '
			lines.append(plt.makeSymbols(plot_list,marker='dot',color=color))
			
			#calculate mean language values for this population
			sum_x = 0.0
			sum_y = 0.0
			for point in plot_list:
				sum_x += point[0]
				sum_y += point[1]
			self.means.write( '\t'+str(population.num_agents())+' '+name+'\t'+\
							str(sum_x/population.num_agents())+', '+\
							str(sum_y/population.num_agents()) + '\n' )	
		
		obj=plt.makeGraphObjects(lines)           		   # step 5
		frame=Frame(plt.root)                               # step 6
		graph=plt.makeGraphBase(frame,640,480, title=title) # step 7
		graph.pack()                                        # step 8
		graph.draw(obj)     # step 9
		graph.postscr(self.directory+'/plot'+str(self.numplots)+'.ps')
		self.numplots+=1
		

	def cleanup(self):
		self.means.close()
	

def trial_number( dir ):
	file_list = os.listdir( dir )
	
	number = 0
	while 'trial'+str(number) in file_list:
		number += 1
	return number

