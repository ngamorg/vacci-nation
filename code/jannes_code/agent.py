from status import Status


class Agent:
    state = Status.healthy

    num_sus = 0
    num_inf = 0
    num_rec = 0

    def __init__(self, state=Status.healthy):
        self.state = state

    def get_infected(self):
        if not self.is_infected() and self.is_healthy():
            Agent.num_sus -= 1
            Agent.num_inf += 1
        self.state = Status.infected

    def recover(self):
        if not self.is_recovered():
            if self.is_infected():
                Agent.num_inf -= 1
            if self.is_healthy():
                Agent.num_sus -= 1
            Agent.num_rec += 1
        self.state = Status.recovered

    def heal_without_immunity(self):
        if self.is_infected():
            Agent.num_inf -= 1
            Agent.num_sus += 1
        self.state = Status.healthy

    def is_healthy(self):
        return self.state == Status.healthy

    def is_infected(self):
        return self.state == Status.infected

    def is_recovered(self):
        return self.state == Status.recovered
