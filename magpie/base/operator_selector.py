from abc import ABC, abstractmethod
import random

class AbstractOperatorSelector(ABC):
    def __init__(self, operators):
        self._operators = operators
    
    @abstractmethod
    def select(self, **kwargs):
        pass

class UniformSelector(AbstractOperatorSelector):
    def __init__(self, operators):
        super().__init__(operators)

    def select(self):
        return random.choice(self._operators)

class WeightedSelector(AbstractOperatorSelector):
    def __init__(self, operators, weights):
        super().__init__(operators)
        self._weights = weights

        assert len(self._operators) == len(self._weights), 'number of operators and weights must match. Got {} operators and {} weights'.format(len(self._operators), len(self._weights))
        
    def select(self):
        return random.choices(self._operators, weights=self._weights, k=1)[0]

class EpsilonGreedy(AbstractOperatorSelector):
    def __init__(self, operators, epsilon):
        super().__init__(operators)
        
        self._epsilon = epsilon

        self._average_qualities = {op: 0 for op in self._operators}
        self._action_count = {op: 0 for op in self._operators}

        # Sanity checks
        self._update_call_count = 0
        self._select_call_count = 0
        
        # Keep track of previous operator for update_quality
        self.prev_operator = None

        # Logs
        self.reward_log = [] # Index is time step
        self.average_qualities_log = [self._average_qualities.copy()]
        self.action_count_log = [self._action_count.copy()]

    def calculate_reward(self, initial_fitness, run):
        """ current 1, previous 5
        if run.status != 'SUCCESS':    
            return 0
        else:
            return previous / current # only update previous if it complied       
        """
        if run.status != 'SUCCESS':
            return 0
        else:
            return initial_fitness / run.fitness # Return relative improvement from base fitness (TODO: change to previous fitness as discussed)
                
    def update_quality(self, operator, initial_fitness, run):

        reward = self.calculate_reward(initial_fitness, run)

        self._action_count[operator] += 1
        self._average_qualities[operator] += (reward - self._average_qualities[operator]) / self._action_count[operator]

        # Sanity checks
        self._update_call_count += 1
        assert self._update_call_count == self._select_call_count

        # Logs
        self.reward_log.append(reward)
        self.average_qualities_log.append(self._average_qualities.copy())
        self.action_count_log.append(self._action_count.copy())

    def select(self):
        # Sanity checks
        assert self._update_call_count == self._select_call_count
        self._select_call_count += 1

        if random.random() < 1 - self._epsilon:
            self.prev_operator = max(self._operators, key=lambda op: self._average_qualities[op])
        else:
            self.prev_operator = random.choice(self._operators)
        return self.prev_operator
