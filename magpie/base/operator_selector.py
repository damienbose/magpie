from abc import ABC, abstractmethod
import random
import numpy as np

class AbstractOperatorSelector(ABC):
    def __init__(self, operators):
        self._operators = operators
    
    @abstractmethod
    def select(self, **kwargs):
        pass

def calculate_reward(initial_fitness, run):
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

class AbstractBanditsOperatorSelector(AbstractOperatorSelector):
    def __init__(self, operators):
        super().__init__(operators)
        
        self._average_qualities = {op: 0 for op in self._operators} # Note: needs to be set to 0 for an accurate average. TODO: talk about how this differs from adaptive pursuit paper. 
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
    
    def update_quality(self, operator, initial_fitness, run):
        reward = calculate_reward(initial_fitness, run)

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

# Note: UniformSelector and WeightedSelector are not bandits algorithms; however, we use inheritance to track their running statistics for comparison to bandits
class UniformSelector(AbstractBanditsOperatorSelector):
    def __init__(self, operators):
        super().__init__(operators)

    def select(self):
        super().select()
        self.prev_operator = random.choice(self._operators)
        return self.prev_operator

class WeightedSelector(AbstractBanditsOperatorSelector):
    def __init__(self, operators, weights):
        super().__init__(operators)
        self._weights = weights

        assert len(self._operators) == len(self._weights), 'number of operators and weights must match. Got {} operators and {} weights'.format(len(self._operators), len(self._weights))
        
    def select(self):
        super().select()
        self.prev_operator = random.choices(self._operators, weights=self._weights, k=1)[0]
        return self.prev_operator
    
class EpsilonGreedy(AbstractBanditsOperatorSelector):
    def __init__(self, operators, epsilon):
        super().__init__(operators)
        
        # Hyperparameters
        self._epsilon = epsilon
                
    def update_quality(self, operator, initial_fitness, run):
        super().update_quality(operator, initial_fitness, run)
        
    def select(self):
        super().select()
        if random.random() < 1 - self._epsilon:
            self.prev_operator = max(self._operators, key=lambda op: self._average_qualities[op])
        else:
            self.prev_operator = random.choice(self._operators)
        return self.prev_operator

class ProbabilityMatching(AbstractBanditsOperatorSelector):
    def __init__(self, operators, p_min):
        super().__init__(operators)
        
        # Hyperparameters
        self._p_min = p_min
        self._probabilities = np.array([1/len(self._operators) for op in self._operators]) # Index matches operators
        self.probabilities_log = [self._probabilities.copy()]
    
    def update_quality(self, operator, initial_fitness, run):
        super().update_quality(operator, initial_fitness, run)

        # Update probabilities
        total = sum(self._average_qualities.values())

        # If the total is 0, then they are all equiprobable
        if total == 0:
            self._probabilities = np.array([1/len(self._operators) for op in self._operators])
        else:
            for i, operator in enumerate(self._operators): # TODO: parallelise
                self._probabilities[i] = self._p_min + (1 - len(self._operators) * self._p_min) * (self._average_qualities[operator] / total)

        self.probabilities_log.append(self._probabilities.copy())

    def select(self):
        super().select()
        self.prev_operator = random.choices(self._operators, weights=self._probabilities, k=1)[0]
        return self.prev_operator

class UCB(AbstractBanditsOperatorSelector):
    def __init__(self, operators, c): # TODO: Look for c in literature (note c=root(2) is used in the lectures for log expected regret)
        super().__init__(operators) # TODO: look for initial quality

        # Hyperparameters
        self._c = c

        self.num_arms_not_selected = operators.copy()

    def update_quality(self, operator, initial_fitness, run):
        super().update_quality(operator, initial_fitness, run)
    
    def select(self):
        super().select()

        if len(self.num_arms_not_selected) > 0: # Makes sure each arm is selected at least once initially
            self.prev_operator = self.num_arms_not_selected.pop()
        else:
            t = sum(self._action_count.values())
            self.prev_operator = max(self._operators, key=lambda op: self._average_qualities[op] + self._c * np.sqrt(np.log(t) / self._action_count[op])) # Note: taken form COMP0098 slides
        return self.prev_operator


# Algorithms (Lectures):
# Bayesian bandits with UCB in slides
# Policy gradients (Might be a lot more interesting)
# Thompson sampling (Optimistic in the face of uncertainty)