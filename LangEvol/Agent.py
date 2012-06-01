import SimPy.Simulation as Sim
from random import *
from math import hypot, fabs

class Agent(Sim.Process):
	all_agents = []
	innovation_distance = 3.0
	
	def __init__(self, lang_x, lang_y, speak_rate, learn_rate, innovation):
		'''Initializes the agent. The variables used are:
				lang_x: the x parameter for this agent's language
				lang_y: the y parameter for this agent's language
				speak_rate: the rate at which this agent initiates conversation.
					time between conversation events is random.expovariate(speak_rate)
					speak_rate is floored at 0.001.
				learn_rate: the amount the speaker changes his language when he hears
					another speaker. Changes his language by 
					learn_rate*(self.lang - other.lang)
				innovation: The rate at which this speaker randomly changes his language.
					time between innovation events is random.expovaraiate(innovation).
				next_conversation: the simulation time for the next conversation initiated
					by this agent.
				next_innovation: the simulation time for the next innovation introduced by
					this agent.'''
		Sim.Process.__init__(self)
		self.lang_x = lang_x
		self.lang_y = lang_y
		if speak_rate < 0.001:
			speak_rate = 0.001
		self.speak_rate = speak_rate
		self.learn_rate = learn_rate
		self.innovation = innovation
		self.next_conversation = Sim.now() + expovariate(speak_rate)
		self.next_innovation = Sim.now() + expovariate(innovation)
		
		Agent.all_agents.append(self);
	
	def find_partner(self):
		'''Finds a partner for this Agent to converse with. This should be overridden
		by subclasses of Agent. Raises an exception.'''
		raise Exception('find_partner method invoked on class Agent. Should only be '+\
			'invoked on sublcasses')
	
	def converse(self, partner):
		'''Converses with partner. First move's partner's language parameters closer to
		self's, then moves self's closer to partner's.'''
		#self initiates conversation, so partner accommodates first
		partner.lang_x += partner.learn_rate*(self.lang_x - partner.lang_x)
		partner.lang_y += partner.learn_rate*(self.lang_y - partner.lang_y)
		#partner responds, influencing self
		self.lang_x += self.learn_rate*(partner.lang_x - self.lang_x)
		self.lang_y += self.learn_rate*(partner.lang_y - self.lang_y)
	
	def innovate(self):
		'''Randomly shifts the agent's parameters up to Agent.innovation_distance from
		its present value.'''
		self.lang_x += uniform(-Agent.innovation_distance, Agent.innovation_distance)
		self.lang_y += uniform(-Agent.innovation_distance, Agent.innovation_distance)
		
	def go(self):
		'''Executes the following loop:
				wait until the next conversation or innovation event
				call converse or innovate
				find the time of the next conversation or innovation'''
		innovate = False
		while True:
			#hold until next conversation or innovation
			if self.next_conversation < self.next_innovation:
				innovate = False
				yield Sim.hold, self, self.next_conversation
			else:
				innovate = True
				yield Sim.hold, self, self.next_innovation
			if innovate:
				self.innovate()
				self.next_innovation = expovariate(self.innovation)
			else:
				#find partner and talk
				partner = self.find_partner()
				self.converse(partner)
				self.next_conversation = expovariate(self.speak_factor()*self.speak_rate)
	
	def speak_factor(self):
		return 1.0
	
	@classmethod
	def num_agents(cls):
		return len(cls.all_agents)

class LineAgent(Agent):
	
	def __init__( self, lang_x, lang_y, speak_rate, learn_rate, 
				  innovation, location, radius):
		Agent.__init__(self, lang_x, lang_y, speak_rate, learn_rate, innovation)
		self.location = location
		self.radius = radius
		
		self.all_agents.sort(lambda x,y:cmp(x.location,y.location))
	
	def find_partner(self):
		partner_loc = gauss(self.location, self.radius)
		index = self.index_after_loc(partner_loc)
		if(index) == 0:
			index = 1
		if index == self.num_agents():
			index -= 1
		
		partner0 = self.all_agents[index-1]
		if partner0 == self:
			if index == 1: #this is the first agent on the line
				return self.all_agents[1]
			partner0 = self.all_agents[index-2]
		
		partner1 = self.all_agents[index]
		if partner1 == self:
			if index == self.num_agents()-1: #this is the last agent on the line
				return partner0
			partner1 = self.all_agents[index+1]
			
		if partner_loc - partner0.location < partner1.location - partner_loc:
			return partner0
		else:
			return partner1
	
	@classmethod 
	def index_after_loc( cls, location, min=None, max=None ):
		if min == None:
			min = 0
		if max == None:
			max = cls.num_agents()
		
		if min == max:
			return min
		if min+1 == max:
			if cls.all_agents[min].location > location:
				return min
			else:
				return max
		else:
			index = (max-min)//2 + min
			if cls.all_agents[index].location < location: #location is after the middle value
				return cls.index_after_loc(location, index, max)
			else: #location is before the middle value
				return cls.index_after_loc(location, min, index)
		
	@classmethod
	def partner_test(cls):
		first = None
		middle = None
		last = None
		locations = [1, 2.1, 1.3, 3.1, 4, 3.5, 4.7, 5.2, 6.1, 6.9, 8, 9.3,
						10.2, 11, 11.3, 13.8, 13, 10.4, 14, 14.2]
		radii = [2.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.3, 0, 0, 0, 0, 0, 0, 0, 0, 2]
		for i in range(0, 20):
			a = LineAgent(1,1,1,1,1,locations[i], radii[i])
			if i == 0:
				first = a
			if i == 19:
				last = a
			if i == 10:
				middle = a
		
		print 'Finding partner for first agent. Loc: ' +str(first.location)
		partner = first.find_partner()
		print partner
		print partner.location
		print
		
		print 'Finding partner for middle agent. Loc: ' + str(middle.location)
		partner = middle.find_partner()
		print partner
		print partner.location
		print

		print 'Finding partner for last agent. Loc: ' + str(last.location)
		partner = last.find_partner()
		print partner
		print partner.location
		print
		
		locs = []
		for agent in cls.all_agents:
			locs.append(agent.location)
		print locs
	

class LangRelativeAgent(LineAgent):
	#to be set by client program
	lang_tolerance = None
	
	def speak_factor(self):
		same_lang = 0
		for agent in self.all_agents:
			lang_dist = hypot( agent.lang_x - self.lang_x, agent.lang_y - self.lang_y )
			loc_dist = fabs(agent.location - self.location)
			if lang_dist <= self.lang_tolerance and loc_dist <= self.radius:
				same_lang += 1
				
		#same_should always be at least 1, because self is in all_agents
		return same_lang
	

