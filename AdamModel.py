#!/usr/bin/env python

import SimPy.Simulation as Sim
from SimPy.SimPlot import *
import random, time
from random import gauss

###########################################################
# Model Components

class Speaker(Sim.Process):
   def __init__(self, language, location, radius, name='Speaker X'):
       Sim.Process.__init__(self, name=name)
       self.language = language
       self.location = location
       if radius < 0:
           radius = 0.1
       self.radius = radius
       self.affecting_speakers = []
       self.total_pop = 0
       self.total_status = 0

   def __str__(self):
       return self.name

   def set_affecting_speakers_list(self, speakers):
       for s in speakers:
           if self.affected_by(s):
               self.affecting_speakers.append(s)
	       self.total_pop += 1
	       self.total_status += s.radius

   def affected_by(self, s):
	   if self.location < s.location:
		   return self.location >= s.location - s.radius
	   else:
		   return self.location <= s.location + s.radius
       
   def shouldSwitch(self, otherLang):
       # Compute our probability of switching to it
       other_pop = 0		#number of speakers affecting this speaker 
       				#who speak otherLang
       other_status = 0.0	#total radius values of the speakers affecting
       				#this speaker who speak otherLang
       for s in self.affecting_speakers:
           if s.language == otherLang:
               other_pop = other_pop + 1
               other_status = other_status + s.radius

       otherFraction = float(other_pop) / \
           float(self.total_pop)
       status = float(other_status) / float(self.total_status)
       probChange = Parameters.c * (otherFraction ** Parameters.a) *\
           status

       # Switch to it if a random number between 0 and 1 is less
       # than our probability of switching
       rand = random.random()
       return rand < probChange

   def go(self):
       # add ourselves to our initial language
       yield Sim.put, self, self.language.population, 1
       while 1:
           yield Sim.hold, self, Parameters.timeStep

           # For each other available language
           for otherLang in Parameters.languages:
               if otherLang == self.language: continue
               if self.shouldSwitch(otherLang):
                   if Parameters.verbose:
                       print 'Time %s: %s: switching from %s to %s (with probability %s)' %\
                           (Sim.now(), self, self.language, otherLang, probChange)
                   yield Sim.hold, self, (Parameters.timeStep / 2.0)
                   # make sure we wait until other agents make their decision before switching

                   yield Sim.get, self, self.language.population, 1
                   yield Sim.put, self, otherLang.population, 1
                   self.language = otherLang
                   break


class Language:
   def __init__(self, status, name='Language X'):
       self.name = name
       self.population = Sim.Level(name=name+' Population',
           unitName='speakers', monitored=True)
       self.population.bufferMon.name = "%s Population" % (name,)
       self.status = status
       print '%s: status: %s' % (name, status)

   def __str__(self):
       return self.name

class Timer(Sim.Process):
   def tracktime(self, resolution):
       percentDone = 0.0
       while 1:
           yield Sim.hold, self, (resolution * Parameters.simLength)
           percentDone += resolution

           print '%s%%' % (percentDone * 100, )

###########################################################
# Model

def model():
   print 'Initializing...'
   Sim.initialize()

   print 'Random seed: %s' % (Parameters.randSeed,)
   random.seed(Parameters.randSeed)

   print 'Verbose:', Parameters.verbose

   Parameters.languages = [Language(Parameters.langStatuses[i],
       "Language %s" % (i,)) for i in \
               range(Parameters.numLanguages)]

   Parameters.numSpeakers = 0
   speakers = []
   langIdx = 0
   for population in Parameters.initialDistribution:
       for i in range(population):
           speakers.append(Speaker(Parameters.languages[langIdx],
		gauss(Parameters.position_distribution[langIdx][0],
			Parameters.position_distribution[langIdx][1] ),
		gauss(Parameters.position_distribution[langIdx][2],
			Parameters.position_distribution[langIdx][3] ),
               "Speaker %s" % (Parameters.numSpeakers,),))
           Parameters.numSpeakers += 1
       langIdx += 1

   for s in speakers:
       s.set_affecting_speakers_list(speakers)

   for s in speakers:
       Sim.activate(s, s.go())
   timer = Timer()
   Sim.activate(timer, timer.tracktime(resolution=0.10))

   print 'Speakers: %s' % (Parameters.numSpeakers,)
   print 'Initial population distribution:'
   for l in range(len(Parameters.languages)):
       print "\t%s: %s speakers" % (Parameters.languages[l],
               Parameters.initialDistribution[l])

   print
   print 'Simulating...'
   Sim.simulate(until=Parameters.simLength)
   print 'Simulation Complete at t=%s' % Sim.now()

   return speakers

###########################################################
# Data and Parameters

class Parameters:
   numSpeakers = None # gets set on model creation
   languages = None
   numLanguages = 2
   position_distribution = [(50.0, 20.0, 7.0, 0.8), (50.0, 1.0, 5.0, 0.5)]
	#list of (position mean, position deviation, radius mean, radius deviation)
   initialDistribution = [300, 100]
   langStatuses = [0.5, 0.5]
   c = 1.0  # constant from Abrams and Strogatz paper
   a = 1.31 # Ditto

   simLength = 200.0

   timeStep = 1.0
   randSeed = time.time()
   verbose = False

###########################################################
# Experiment

if __name__ == "__main__":
   speakers = model()
   print
   print 'Ending population distribution:'
   for l in Parameters.languages:
       print "\t%s: %s speakers" % (l, l.population.amount)

###########################################################
# Analysis and Output

   print 'Normalizing data...'
   normalizedData = {}
   for lang in Parameters.languages:
       data = []
       lastDatum = None
       for datum in lang.population.bufferMon:
           if lastDatum and datum[0] > lastDatum[0]:
               data.append(lastDatum)
           lastDatum = datum
       normalizedData[lang] = data

   colors = iter(['red', 'green', 'blue', 'black', 'yellow', 'cyan', 'magenta'])
   plt=SimPlot()                                       # step 1
   plt.root.title("Language Population Levels")              # step 3
   lines = []
   print "Language Colors:"
   for lang in Parameters.languages:
       color = colors.next()
       print "\t%s: %s" % (lang, color)
       lines.append(plt.makeLine(normalizedData[lang], color=color))
#       lines.append(plt.makeLine(lang.population.bufferMon, color=color))

   obj=plt.makeGraphObjects(lines)            # step 5
   frame=Frame(plt.root)                               # step 6
   graph=plt.makeGraphBase(frame,640,480,
                           title="Population Levels",
                           xtitle="Time",
                           ytitle="Speakers")      # step 7
   graph.pack()                                        # step 8
   graph.draw(obj)                                     # step 9
   frame.pack()                                        # step 10
   #graph.postscr()
   plt.mainloop()                                      # step 12

