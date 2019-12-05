

class Agent:

    def __init__(self, id):
        self.id = id
        self.infected = 0
        self.vaccinated = 0

        self.infected_n = 0

    def reset_next(self):
        self.infected = 0
