import copy
import random
import time
from magpie.base.operator_selector import AbstractBanditsOperatorSelector

from ..base import Patch
from ..bin import BasicAlgorithm

class LocalSearch(BasicAlgorithm):
    def setup(self):
        super().setup()
        self.name = 'Local Search'
        self.config['delete_prob'] = 0.5
        self.config['max_neighbours'] = None
        self.config['when_trapped'] = 'continue'
        self.last_operator_is_delete_edit = False
        assert self.config['delete_prob'] >= 0 and self.config['delete_prob'] < 1, "delete_prob should be in [0, 1)"

    def reset(self):
        super().reset()
        self.stats['neighbours'] = 0

    def run(self):
        try:
            # warmup
            self.hook_warmup()
            self.warmup()

            # early stop if something went wrong during warmup
            if self.report['stop']:
                return

            # start!
            self.hook_start()

            # main loop
            current_patch = self.report['best_patch']
            current_fitness = self.report['best_fitness']
            while not self.stopping_condition():
                self.hook_main_loop()
                current_patch, current_fitness = self.explore(current_patch, current_fitness)

        except KeyboardInterrupt:
            self.report['stop'] = 'keyboard interrupt'

        finally:
            # the end
            self.hook_end()

    def mutate_helper(self, patch, delete=False):
        if delete:
            n = len(patch.edits)
            assert n > 0, "Cannot delete from an empty patch."
            del patch.edits[random.randrange(0, n)]
            self.last_operator_is_delete_edit = True
        else:
            patch.edits.append(self.create_edit())
            self.last_operator_is_delete_edit = False

    def mutate(self, patch):
        if len(patch.edits) > 0 and random.random() < self.config['delete_prob']:
            self.mutate_helper(patch, delete=True)
        else:
            self.mutate_helper(patch, delete=False)

    def evaluate_patch_wrapper(self, patch, parent_fitness=None):
        run = self.evaluate_patch(patch)
        if isinstance(self.config['operator_selector'], AbstractBanditsOperatorSelector) and not self.last_operator_is_delete_edit:
            assert run is not None, "run should not be None"
            assert parent_fitness is not None, "parent_fitness should not be None"
            self.config['operator_selector'].update_quality(self.config['operator_selector'].prev_operator, parent_fitness, run)
        return run
        
    def check_if_trapped(self):
        if self.config['max_neighbours'] is None:
            return
        if self.stats['neighbours'] < self.config['max_neighbours']:
            return
        if self.config['when_trapped'] == 'stop':
            self.report['stop'] = 'trapped'
        # TODO: restart, others?

class RandomSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Random Search'

    def explore(self, current_patch, current_fitness):
        # move
        patch = Patch()
        self.mutate_helper(patch, delete=False)

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=self.report['initial_fitness'])
        best = False
        
        if run.status == 'SUCCESS':
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # hook
        self.hook_evaluation(patch, run, False, best)

        # next
        self.stats['steps'] += 1
        return patch, run.fitness

# My local search
class FYPLocalSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'FYP Local Search'

        self.local_best_patch = None
        self.local_best_fitness = None

    def delete_rand_edit(self, current_patch):
        # Keep deleting until a feasible variant is found
        if len(current_patch.edits) == 0:
            return Patch(), self.report['initial_fitness']

        while True:
            self.program.logger.info(f"Deleting a random edit from patch: [{len(current_patch.edits)} edit(s)]")

            if len(current_patch.edits) == 1:
                return Patch(), self.report['initial_fitness']

            # Move
            patch = copy.deepcopy(current_patch)
            self.mutate_helper(patch, delete=True)

            # Compare
            run = self.evaluate_patch_wrapper(patch)
            best = run.status == 'SUCCESS' and self.dominates(run.fitness, self.report['best_fitness'])
            if best:
                self.report['best_patch'] = patch
                self.report['best_fitness'] = run.fitness

            # Hook
            self.hook_evaluation(patch, run, False, best)
            self.stats['steps'] += 1

            # Update search space
            current_patch, current_fitness = patch, run.fitness
            if run.status == 'SUCCESS':
                break

        return current_patch, current_fitness
    
    def localNeighbourhoodSearch(self, current_patch, current_fitness):
            # move
            patch = copy.deepcopy(current_patch)
            self.mutate_helper(patch, delete=False)

            # compare
            run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)

            best = best_local = False
            if run.status == 'SUCCESS':
                if self.dominates(run.fitness, self.local_best_fitness):
                    self.local_best_patch = patch
                    self.local_best_fitness = run.fitness
                    best_local = True
                    if self.dominates(run.fitness, self.report['best_fitness']):
                        best = True
            
            # hook
            self.hook_evaluation(patch, run, best_local, best)
            self.stats['steps'] += 1

    def explore(self, current_patch, current_fitness):
        self.program.logger.info(f"Performing Random Search on [{current_patch}] with fitness={current_fitness}")

        # Initialise our local neighbourhood base
        self.local_best_patch, self.local_best_fitness = current_patch, current_fitness

        # RandomSearch
        for _ in range(self.config['max_neighbours']):
            if self.stopping_condition():
                break
            self.localNeighbourhoodSearch(current_patch, current_fitness)
        
        # Update global best
        if self.dominates(self.local_best_fitness, self.report['best_fitness']):
            self.report['best_patch'] = self.local_best_patch
            self.report['best_fitness'] = self.local_best_fitness

        # Take a step into new neighbourhood
        self.program.logger.info("Updating the search space...")
        if current_patch == self.local_best_patch:
            current_patch, current_fitness = self.delete_rand_edit(current_patch)
        else:
            current_patch, current_fitness = self.local_best_patch, self.local_best_fitness

        return current_patch, current_fitness

class DummySearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Dummy Search'

    def explore(self, current_patch, current_fitness):
        self.report['stop'] = 'dummy end'
        return current_patch, current_fitness


class DebugSearch(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Debug Search'

    def explore(self, current_patch, current_fitness):
        debug_patch = self.report['debug_patch']
        for edit in debug_patch.edits:
            # move
            patch = Patch([edit])

            # compare
            run = self.evaluate_patch(patch)
            accept = best = False
            if run.status == 'SUCCESS':
                accept = True
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

            # hook
            self.hook_evaluation(patch, run, accept, best)

            # next
            self.stats['steps'] += 1

        self.report['stop'] = 'debug end'
        return current_patch, current_fitness

class RandomWalk(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Random Walk'
        self.config['accept_fail'] = False

    def explore(self, current_patch, current_fitness):
        # move
        patch = copy.deepcopy(current_patch)
        self.mutate(patch)

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = self.config['accept_fail']
        best = False
        if run.status == 'SUCCESS':
            accept = True
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.stats['neighbours'] = 0
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class FirstImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'First Improvement'
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                accept = True
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.local_tabu.clear()
            self.stats['neighbours'] = 0
        else:
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness

class FirstImprovementNoTabu(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'First Improvement No Tabu'

    def explore(self, current_patch, current_fitness):
        # move
        patch = copy.deepcopy(current_patch)
        self.mutate(patch)

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                accept = True
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

        # accept
        if accept:
            current_patch = patch
            current_fitness = run.fitness
            self.stats['neighbours'] = 0
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class BestImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Best Improvement'
        self.config['max_neighbours'] = 20
        self.local_best_patch = None
        self.local_best_fitness = None
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                if not self.dominates(self.local_best_fitness, run.fitness):
                    self.local_best_patch = patch
                    self.local_best_fitness = run.fitness
                    if self.dominates(run.fitness, self.report['best_fitness']):
                        self.report['best_fitness'] = run.fitness
                        self.report['best_patch'] = patch
                        best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_best_patch is not None:
                current_patch = self.local_best_patch
                current_fitness = self.local_best_fitness
                self.local_best_patch = None
                self.local_best_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
            else:
                self.check_if_trapped()
        else:
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness
    
class BestImprovementNoTabu(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Best Improvement No Tabu'
        self.config['max_neighbours'] = 20
        self.local_best_patch = None
        self.local_best_fitness = None

    def explore(self, current_patch, current_fitness):
        # move
        patch = copy.deepcopy(current_patch)
        self.mutate(patch)

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                if not self.dominates(self.local_best_fitness, run.fitness):
                    self.local_best_patch = patch
                    self.local_best_fitness = run.fitness
                    if self.dominates(run.fitness, self.report['best_fitness']):
                        self.report['best_fitness'] = run.fitness
                        self.report['best_patch'] = patch
                        best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_best_patch is not None:
                current_patch = self.local_best_patch
                current_fitness = self.local_best_fitness
                self.local_best_patch = None
                self.local_best_fitness = None
                self.stats['neighbours'] = 0
            else:
                self.check_if_trapped()
        else:
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class WorstImprovement(LocalSearch):
    def setup(self):
        super().setup()
        self.name = 'Worst Improvement'
        self.config['max_neighbours'] = 20
        self.local_worst_patch = None
        self.local_worst_fitness = None
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(current_fitness, run.fitness):
                if not self.dominates(self.local_worst_fitness, run.fitness):
                    self.local_worst_patch = patch
                    self.local_worst_fitness = run.fitness
                if self.dominates(run.fitness, self.report['best_fitness']):
                    self.report['best_fitness'] = run.fitness
                    self.report['best_patch'] = patch
                    best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_worst_patch is not None:
                current_patch = self.local_worst_patch
                current_fitness = self.local_worst_fitness
                self.local_worst_patch = None
                self.local_worst_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
            else:
                self.check_if_trapped()
        else:
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness


class TabuSearch(BestImprovement):
    def setup(self):
        super().setup()
        self.name = 'Tabu Search'
        self.config['tabu_length'] = 10
        self.tabu_list = [magpie.base.Patch()] # queues are not iterable
        self.local_tabu = set()

    def explore(self, current_patch, current_fitness):
        # move
        while True:
            patch = copy.deepcopy(current_patch)
            self.mutate(patch)
            if patch not in self.tabu_list and patch not in self.local_tabu:
                break

        # compare
        run = self.evaluate_patch_wrapper(patch, parent_fitness=current_fitness)
        accept = best = False
        if run.status == 'SUCCESS':
            if not self.dominates(self.local_best_fitness, run.fitness):
                self.local_best_patch = patch
                self.local_best_fitness = run.fitness
            if self.dominates(run.fitness, self.report['best_fitness']):
                self.report['best_fitness'] = run.fitness
                self.report['best_patch'] = patch
                best = True

        # accept
        accept = self.stats['neighbours'] >= self.config['max_neighbours']
        if accept:
            if self.local_best_patch is not None:
                current_patch = self.local_best_patch
                current_fitness = self.local_best_fitness
                self.local_best_patch = None
                self.local_best_fitness = None
                self.local_tabu.clear()
                self.stats['neighbours'] = 0
                self.tabu_list.append(self.local_best_patch)
                while len(self.tabu_list) >= self.config['tabu_length']:
                    self.tabu_list.pop(0)
            else:
                self.check_if_trapped()
        else:
            if len(patch.edits) < len(current_patch.edits):
                self.local_tabu.add(patch)
            self.stats['neighbours'] += 1
            self.check_if_trapped()

        # hook
        self.hook_evaluation(patch, run, accept, best)

        # next
        self.stats['steps'] += 1
        return current_patch, current_fitness
