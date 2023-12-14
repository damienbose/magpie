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
        self.update_call_count = 0
        self.select_call_count = 0
        
    def update_quality(self, operator, reward): # Note: reward = -fitness, since we're trying to minimize fitness
        self._action_count[operator] += 1
        self._average_qualities[operator] += (reward - self._average_qualities[operator]) / self._action_count[operator]

        # Sanity checks
        self.select_call_count += 1
        assert self.update_call_count == self.select_call_count

    def select(self):
        # Sanity checks
        assert self.update_call_count == self.select_call_count
        self.select_call_count += 1

        if random.random() < 1 - self._epsilon:
            return max(self._operators, key=lambda op: self._average_qualities[op])
        else:
            return random.choice(self._operators)
