from repeater.repeater_abs import Repeater
from repeater.default_repeater import DefaultRepeater
import numpy as np
from math import exp
import copy


class StudentRepeater(Repeater):
    def __init__(self, *args, **kwargs):

        # Initiating parent class and transferring WSClient in *args and other params in **kwargs
        super().__init__(*args, **kwargs)

    def decision_function(self, point, threshold=15, **configuration):
        """
        Return False if history is empty or has only 1 element for current point, and
        :param point: concrete experiment configuration that is evaluating
                      shape - tuple, e.g. ``(1200, 32)``
        :param threshold:
        :return:
        """
        # Preparing configuration
        params = configuration.keys()

        default_point = configuration['default_point'] if 'default_point' in params else None

        # For trusted probability 0.95
        student_coefficients = {
            2: 12.7,
            3: 4.30,
            4: 3.18,
            5: 2.78,
            6: 2.57,
            7: 2.45,
            8: 2.36,
            9: 2.31,
            10: 2.26,
            11: 1.96
        }

        # first of all - need at least 2 measurements
        all_experiments = self.history.get(point)
        if len(all_experiments) < 2:
            return False

        elif len(all_experiments) >= self.max_repeats_of_experiment:
            return self.summing_all_results(all_experiments, point)

        else:
            default_not_digit_parameters = {}
            not_digit_parameters = {}
            for i in range(len(all_experiments[0])):
                if type(all_experiments[0][i]) not in [int, float]:
                    not_digit_parameters[i] = all_experiments[0][i]

            for index in not_digit_parameters.keys():
                default_not_digit_parameters[index] = all_experiments[0][index]

            not_digit_parameters_indexes = list(not_digit_parameters.keys())
            not_digit_parameters_indexes.sort(reverse=True)
            for experiment in all_experiments:
                for index in not_digit_parameters_indexes:
                    experiment.pop(index)

            default_point_backup = copy.deepcopy(default_point)
            if default_point is not None:
                for index in not_digit_parameters_indexes:
                        default_point_backup.pop(index)

            # Calculating average for all dimensions
            all_experiments_np = np.matrix(all_experiments)
            all_dim_avg = all_experiments_np.mean(0)

            # Calculating standard deviation
            all_dim_sko = np.std(all_experiments_np, axis=0)

            # Pick the Student's coefficient, if number of experiments is 11 or more - pick coefficient for 11
            student_coefficient = student_coefficients[len(all_experiments) if len(all_experiments) < 11 else 11]

            # Calculating confidence interval for each dimension
            conf_interval = [student_coefficient * dim_sko / pow(len(all_experiments), 0.5) for dim_sko in all_dim_sko]

            # Calculating relative error for each dimension
            relative_errors = [interval / avg * 100 for interval, avg in zip(conf_interval, all_dim_avg)][0].tolist()[0]

            # Verifying that deviation of errors in each dimension is
            for index, error in enumerate(relative_errors):
                # Selecting needed threshold - 100/(1+exp(-x+3.3)) where x is value of measured point divided to default
                threshold = 100/(1+exp(-float((all_dim_avg.tolist()[0][index] / default_point[index]))+3.3))\
                            + len(all_experiments) - 2 if default_point else threshold + len(all_experiments)
                # If for any dimension relative error is > that threshold - abort
                if error > threshold:
                    return False
            # eval(self...)(value) - process of casting according to ResultDataTypes in task.json
            result_data_types_short = copy.deepcopy(self.WSClient._result_data_types)
            for index in not_digit_parameters_indexes:
                    result_data_types_short.pop(index)
            result = [eval(result_data_types_short[index])(round(value, 3)) for index, value in enumerate(all_dim_avg.tolist()[0])]
            not_digit_parameters_indexes.sort()
            for index in not_digit_parameters_indexes:
                result.insert(index, not_digit_parameters[index]) 
            return result
