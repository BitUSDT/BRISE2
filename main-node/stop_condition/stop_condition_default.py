from stop_condition.stop_condition_abs import StopCondition
import logging
from tools.is_better_point import is_better_point


class StopConditionDefault(StopCondition):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.configs_without_improvement = 0
        self.best_solution_labels = [[]]
        self.best_solution_features = [[]]

    def validate_solution(self, solution_candidate_labels, solution_candidate_features, current_best_labels,
                          current_best_features):
        """
        Returns prediction_is_final=True if configs_without_improvement >= "MaxConfigsWithoutImprovement",
                otherwise prediction_is_final=False
        :return: labels,
                     shape - list of lists, e.g. ``[[253.132]]``
                 feature,
                     shape - list of lists, e.g. ``[[2000.0, 32]]``
                 prediction_is_final

        """
        # Validation is False
        prediction_is_final = False

        if self.best_solution_labels == [[]] or self.best_solution_features == [[]]:
            self.best_solution_labels = current_best_labels
            self.best_solution_features = current_best_features

        # If the measured point is better than previous best value - add this point to data set and rebuild model.
        # Assign self.configs_without_improvement to its configuration value.
        if is_better_point(is_minimization_experiment=self.is_minimization_experiment,
                           solution_candidate_label=solution_candidate_labels[0][0],
                           best_solution_label=self.best_solution_labels[0][0]):
            self.configs_without_improvement = 0
            self.logger.info("New solution is found! Predicted value %s is better than previous value %s. "
                             "Max Configs Without Improvement = %s" % (solution_candidate_labels, self.best_solution_labels,
                                                                       self.configs_without_improvement))
            self.best_solution_labels = solution_candidate_labels
            self.best_solution_features = solution_candidate_features

        # If the measured point is worse than previous best value - add this point to data set and rebuild model.
        # Decrease self.configs_without_improvement by 1
        else:
            self.configs_without_improvement += 1
            self.logger.info("Predicted value %s is worse than previous value %s. Max Configs Without Improvement = %s"
                             % (solution_candidate_labels, self.best_solution_labels, self.configs_without_improvement))

        if self.configs_without_improvement >= self.stop_condition_config["MaxConfigsWithoutImprovement"]:
            # if self.configs_without_improvement is higher or equal to
            # self.stop_condition_config["MaxConfigsWithoutImprovement"], then validation is True.
            self.logger.info("Solution validation success! Solution features: %s, solution labels: %s."
                             %(self.best_solution_features,self.best_solution_labels))
            prediction_is_final = True
            return self.best_solution_labels, self.best_solution_features, prediction_is_final

        return solution_candidate_labels, solution_candidate_features, prediction_is_final
