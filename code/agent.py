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


class Agent(object):
    """
    Agent class able to play the vaccination game
    """

    sv = 0
    snv = 0
    # Static members
    r = 0.01

    # min 3-4
    T = 5  # (monthly)  # 0.0 <= beta <= 1.0
    beta = 0.1

    num_vac = 0
    num_vacT = 0
    num_vacS = 0
    num_sus = 0
    num_inf = 0
    num_infT = 0
    num_infS = 0
    num_rec = 0

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
        self._group = group
        self._lambda_k = 0.0
        self._lambda_rel_k = 0.0
        self._gamma_k = self.estimate_gamma()

        self._health_next = None

        super().__init__()

    def run(self, group_behaviours, neighbors, depth_neighbors, agents):
        if self._health == Health.INFECTED:
            if np.random.uniform(0.0, 1.0) < self._gamma_k:
                self._health = Health.RECOVERED
                return

        if not self._health == Health.SUSCEPTIBLE:
            return

        # Get infected?
        self.look(neighbors, agents)

        p = np.random.uniform(0, 1.0)
        if p < self._lambda_k:
            self._health_next = Health.INFECTED

        # Get vaccinated? (Decide once in 30 days)
        self.look(depth_neighbors, agents)
        dec = np.random.uniform(0.0, 1.0)
        if dec < 1/self.T and not self._health_next == Health.INFECTED:
            self.act(group_behaviours)

    def look(self, neighbors, agents):
        """
        Look requests an array of shape (1, number of neighbors) from the environment, and
        calculates the local incidence of the disease and updates the probability of infection
        """

        # : neighborhood[:] is an array containing the health states ('SUSCEPTIBLE', 'INFECTED',
        # 'RECOVERED', 'VACCINATED') of the neighbors of self
        total = 0
        count_infected = 0
        for i in neighbors:
            total += 1
            if agents[i].get_health_status() == Health.INFECTED:
                count_infected += 1

        # Get relative frequency of infections
        # incidence = count_infected / len(neighbors)

        # Update probability of infection
        self._lambda_k = self.estimate_lambda(count_infected)
        self._lambda_rel_k = Agent.beta * count_infected / total

    def act(self, group_behaviours):
        # If agent is already vaccinated or recovered, no action takes place

        # Look around and update infection probability (lambda)
        # self.look(neighbors)

        # Compute Cnotv_k

        r = self.r
        T = self.T

        lambda_k = self._lambda_k  # review of lambda required -> 1 - beta^(infected neighbors)
        gamma_k = self._gamma_k
        lambda_rel_k = self._lambda_rel_k

        for i in range(0, len(group_behaviours)):
            if self._group == group_behaviours[i].type:
                Ci_k = group_behaviours[i].Ci
                Cv_k = group_behaviours[i].Cv

        sum = [0.0, 0.0]
        for t in range(1, T + 1):
            sum[0] += ((1 - lambda_rel_k) / (1 + r)) ** t
            sum[1] += ((1 - gamma_k) / (1 + r)) ** t

        Cnotv_k = Ci_k * (lambda_rel_k / (gamma_k - lambda_rel_k)) * (sum[0] - sum[1])

        # Get pvacc
        if Cv_k > Cnotv_k:
            pvacc = 0.0
        elif Cv_k < Cnotv_k:
            pvacc = 1.0
        else:
            pvacc = np.random.uniform(0.0, 1.0)
        #if lambda_rel_k > 0:
            #print(self._group, pvacc, Cv_k, Cnotv_k, "s0 / 1", sum[0], sum[1], "g, l", gamma_k, lambda_rel_k)

        # Update health state based on pvacc
        p = np.random.uniform(0.0, 1.0)
        if pvacc >= p:
            self._health = Health.VACCINATED

    def update(self):
        # Assume simulation time-step equal to 1 day
        self._age = self._age + 1 / 365
        self._gamma_k = self.estimate_gamma()

        # next state health state
        if self._health_next == Health.INFECTED:
            self._health = self._health_next
            self._health_next = None

    def estimate_lambda(self, num_infected):
        '''
        Local estimate of P(S->I), based on the relative frequency
        of infected individuals surrounding the agent and the conditional
        probability of getting infected given a local prevalence
        '''
        return 1 - pow((1-Agent.beta), num_infected)

    def estimate_gamma(self):
        '''
        Local estimate of P(I->R), based on the agent's health. Assumes
        0 < age < 100 years, and maximum probability of recovery at an
        age = 25 years
        '''
        maxGamma = 0.05
        maxGamma += 0.00000019121986216
        return maxGamma
        """
        if self._age < 25.0:
            return maxGamma * (1.0 - abs(self._age - 25.0) / 25.0)
        else:
            return maxGamma * (1.0 - abs(self._age - 25.0) / (100 - 25.0))
        """

    def get_health_status(self):
        return self._health
