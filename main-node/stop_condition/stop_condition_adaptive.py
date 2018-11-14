from stop_condition.stop_condition_abs import StopCondition
import logging
from tools.is_better_point import is_better_point


class StopConditionAdaptive(StopCondition):

    def __init__(self, search_space_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        # max_configs_without_improvement is calculated as part of full search space size.
        # The part is determined by configs's value - "SearchSpacePercentageWithoutImprovement".
        self.max_configs_without_improvement = \
            round(self.stop_condition_config["SearchSpacePercentageWithoutImprovement"] / 100 * search_space_size)

    def find_solution(self):
        if self.configs_without_improvement < self.max_configs_without_improvement:
            return True
        else:
            return False

    def solution_validation(self, current_best_labels, solution_candidate_labels):
        # if self.configs_without_improvement is higher or equal to self.max_configs_without_improvement,
        # then validation is True.
        self.logger.info("Solution validation success! Solution features: %s, solution labels: %s."
                         %(self.best_solution_features,self.best_solution_labels))
        self.prediction_is_final = True
