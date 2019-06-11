from stop_condition.stop_condition_abs import StopCondition
import logging


class StopConditionImprovementBased(StopCondition):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.max_configs_without_improvement = self.stop_condition_config["MaxConfigsWithoutImprovement"]

    def is_final_prediction(self, current_best_configurations, solution_candidate_configurations):
        # if self.configs_without_improvement is higher or equal to self.max_configs_without_improvement,
        # then validation is True.
        self.logger.info("Solution validation success! Solution features: %s, solution labels: %s."
                         %(self.best_solution_configuration[0].get_parameters(),
                           self.best_solution_configuration[0].get_average_result()))
        return True