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