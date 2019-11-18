# Import libraries
import numpy as np
from enum import Enum

class Health(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    VACCINATED = 3

class Group(Enum):
    SKEPTICAL = 0
    TRUSTER = 1
 
class GroupBehavior():
    def __init__(self, type):
        self.type = type
        if type == Group.SKEPTICAL:
            self.Ci = 1.0
            self.Cv = 2.0
        elif type == Group.TRUSTER:
            self.Ci = 1.0
            self.Cv = 1.0
        
class agent(object):
    """
    Agent class able to play the vaccination game
    """
    
    # Static members
    r = 0.01
    T = 30 # (monthly)
    beta = 0.8 # 0.0 <= beta <= 1.0

    def __init__(self, id, age, health, group):
                
        '''
        SUMMARY OF STATIC ATTRIBUTES
        ----------------------------
        * r: discount rate
            quantifies the time preference of present over future utility
        * T: decision time window
            the decision to either vaccinate or not is taken rationally,
            by maximizing the expected utility during a time span T into
            the future
        * beta: conditional probability of infection
            the agent's estimate of the probability of infection P(S->I)
            requires both knowledge of the local prevalence of the disease
            (proxy for the probability of interacting with an infected agent)
            plus a conditional probability of getting infected given that an
            interaction with an infected agent occurred

        * SUMMARY OF AGENT STATE ATTRIBUTES
        -----------------------------------
        * id: agent's ID in the population (integer)
        * age: agent's age (float, years)
        * health: agent's health state (enum class, Health)
            S (susceptible)
            I (infected)
            R (recovered)
            V (vaccinated) 
        * group: agent's social aggregate (enum class, Group)
            the group is used as a category key for behavioral
            properties affecting the agent's decision process
        * lambda_k: (perceived) probability of infection / P(S -> I)
            a susceptible agent samples its neighborhood in order to estimate
            the relative frequency of infected individuals, and
            mutiplies it by the conditional probability of getting
            infected given a local prevalence
        * gamma_k: (perceived) probability of recovery / P(I -> R)
            an agent estimates its probability of recovery given that
            it is infected, wich will vary depending on age (younger
            and older agents are less likely to recover)
        '''

        # Initialize agent state
        self._id = id
        self._age = age
        self._health = health
        self._group = group;
        self._lambda_k = 0.0;
        self._gamma_k = self.EstimateGamma();

        super().__init__()    
            
    def Look(self, environment):
        """
        Look requests an array of shape (1, number of neighbors) from the environment, and
        calculates the local incidence of the disease and updates the probability of infection
        """

        # : neighborhood[:] is an array containing the health states ('SUSCEPTIBLE', 'INFECTED',
        # 'RECOVERED', 'VACCINATED') of the neighbors of self
        neighborhood = []
        for i, neighbor in enumerate(environment.edges(self._id)):
            neighborhood.append(environment.nodes[neighbor[1]]['data'].TellHealthStatus())
        
        # Get relative frequency of infections
        incidence = neighborhood.count(Health.INFECTED) / len(neighborhood)

        # Update probability of infection
        self._lambda_k = self.EstimateLambda(incidence)

    def Act(self, groups, environment):
        '''

        When an agent vaccinates it transitions according to the rule: S -> V (recovered agents
        are assumed to become fully immunized, so there is no increased payoff on vaccination).
        The agent is assumed to be a rational utility maximizer with only one possible decision
        per action, that is, to vaccinate with probability *pvacc* every *T* time steps if it
        is currently in the susceptible state *S* (otherwise no decision is taken).
        The utility function takes the following form, following the Bellman equation for a
        discrete-time Markov process:

        U_k(x) = sum_{t = 0}^{t = T} x_k(t) * f_k(t) / (1 + r)^t                                             (1)

        Where:
            x_k(t) : health state vector of agent k
            x_k(t = 0) = [ 1 - pvacc, 0, 0, pvacc ] (initial health state vector of agent k)
            f_k(t) : payoff vector of agent k
            f_k(t = 0) = [ 0, 0, 0, -Cv_k ]
            f_k(t > 0) = [ 0, -Ci_k, 0, 0 ]
            Cv_k : cost of vaccination for agent k
            Ci_k : cost of infection for agent k
            r : discount rate
            T : event duration (i.e. before a new utility estimation)

        The agent decided wether to vaccinate or not by solving the optimization problem:
            
            max pvacc {U(x)}

        Additionally, the evolution of the system is given by a stochastic matrix Q:

        x_k(t_{n + 1}) = Q_k * x_k(t_{n})                                                                        (2)
            
        Q_k = [ p_k(S -> S), p_k(I -> S), p_k(R -> S), p_k(V -> S) ]
              [ p_k(S -> I), ...                     , p_k(V -> I) ]
              [ ...                                   ...          ]
              [ p_k(S -> V), ...                     , p_k(V -> V) ]

        And in particular:

        Q_k = [ 1 - lambda_k,           0, 0, 0 ]
              [ lambda_k    , 1 - gamma_k, 0, 0 ]
              [            0,     gamma_k, 1, 0 ]
              [            0,           0, 0, 1 ]
            
        Where:
            lambda_k: probability of infection for a susceptible agent k (estimated using
            local prevalence of infection, times some contact infection probability)
            gamma_k: probability of recovery of infected agent k
            
        Equation (1) can be rewritten using equation (2):

        U_k(x) = ( f_k(t = 0) + sum_{t = 1}^{t = T} Q^t * f_k(t) / (1 + r)^t ) * x_k(0)                      (3)

        In order to compute the power Q^t, the matrix can be diagonalized:

        Q_k = P_k^-1 * L_k * P_k

        So that:
            
        U_k(x) = ( f_k(t = 0) + P_k^-1 * sum_{t = 1}^{t = T} (L_k / (1 + r))^t * P_k * f_k(t) ) * x_k(0)     (4)

        Finally, performing the required computations:

        U_k(x) = -pvacc * Cv_k - (1 - pvacc) * Cnotv_k                                                       (5)

        Where:
            Cnotv_k = Ci_k * (lambda_k / (gamma_k - lambda_k)) * 
            (sum_{t = 1}^{t = T} ((1 - lambda_k) / (1 + r)))^t - sum_{t = 1}^{t = T}((1 - gamma_k) / (1 + r))^t)

        Equation (5) is linear in pvacc, so it only has one global maximum depending on the
        relative cost of each decision. In particular:

            * Cv_k > Cnotv_k -> pvacc = 0 (not vaccinating is the preferred strategy)
            * Cnotv_k > Cv_k -> pvacc = 1 (vaccinating is the preferred strategy)
            * Cv_k = Cnotv_k -> 0 <= pvacc <= 1 (the agent is indiferent towards vaccinating or not)

        Ref.:
        * Shim et al. (2012) - A game dynamic model for vaccine skeptics and vaccine believers:
        Measles as an example
            
        '''
        # If agent is already vaccinated or recovered, no action takes place
        if self._health == Health.VACCINATED or self._health == Health.RECOVERED:
            return
        
        # Look around and update infection probability (lambda)
        self.Look(environment)

        # Compute Cnotv_k
        r = self.r
        T = self.T
        lambda_k = self._lambda_k
        gamma_k = self._gamma_k
        for i in range(0, len(groups)):
            if (self._group == groups[i].type):
                Ci_k = groups[i].Ci
                Cv_k = groups[i].Cv
            
        sum = [ 0.0, 0.0 ]
        for t in range(1, T + 1):
            sum[0] = ((1 - lambda_k) / (1 + r)) ** t
            sum[1] = ((1 - gamma_k) / (1 + r)) ** t

        Cnotv_k = Ci_k * (lambda_k / (gamma_k - lambda_k)) * (sum[0] - sum[1])

        # Get pvacc
        if Cv_k > Cnotv_k:
            pvacc = 0.0
        elif Cv_k < Cnotv_k:
            pvacc = 1.0
        else:
            pvacc = np.random.uniform(0.0,1.0)

        # Update health state based on pvacc
        p =  np.random.uniform(0.0,1.0)
        if pvacc >= p:
            self._health = Health.VACCINATED
          
    def Update(self, health):
        # Assume simulation time-step equal to 1 day
        self._age = self._age + 1 / 365

        # next state health state
        self._health = health
    
    def EstimateLambda(self, incidence):
        '''
        Local estimate of P(S->I), based on the relative frequency
        of infected individuals surrounding the agent and the conditional
        probability of getting infected given a local prevalence
        '''
        return incidence * agent.beta

    def EstimateGamma(self):
        '''
        Local estimate of P(I->R), based on the agent's health. Assumes
        0 < age < 100 years, and maximum probability of recovery at an
        age = 25 years
        '''
        maxGamma = 0.1
        if(self._age < 25.0):
            return maxGamma * (1.0 - abs(self._age - 25.0) / 25.0)
        else:
            return maxGamma * (1.0 - abs(self._age - 25.0) / (100 - 25.0))

    def TellHealthStatus(self):
        return self._health

    def PrintLambda(self):
        print("The perceived probability of infection for agent", \
            self._id, "is equal to:", self._lambda_k)

# SANITY CHECKS
import networkx as nx

# create groups
greens = GroupBehavior(Group.SKEPTICAL)
yellows = GroupBehavior(Group.TRUSTER)
groups = [greens, yellows]

# create population
a = agent(0, 15, Health.SUSCEPTIBLE, Group.TRUSTER)
b = agent(1, 24, Health.INFECTED, Group.TRUSTER)
c =agent(2, 42, Health.SUSCEPTIBLE, Group.SKEPTICAL)
population = [a,b,c]

# create network
g = nx.Graph()
gcomplete = nx.complete_graph(3)
for ag in population:
    g.add_node(ag._id, data=ag)
g.add_edges_from(gcomplete.edges())

# look and estimate infection likelihood, and tell health status
a.Look(g)
a.PrintLambda()
a.Act(groups, g)
print("Agent\'s", a._id, "health status is:", a.TellHealthStatus())