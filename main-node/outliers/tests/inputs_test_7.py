# This file contains inputs for all test cases of outliers module
from outliers.tests.test_outliers import TestOutliers

def get_inputs_for_outliers_test(results_init, outlier_criterions_init, result_structure_init):
    # All outlier detection criterias are disabled
    # with 1 outlier

    # Create results check values
    # Take initial values from head of this file
    # Change some values according to test
    # All artificially added outliers values mark as 'Outlier'
    # expected_results is used as check value  

    results = results_init
    outlier_criterions = outlier_criterions_init
    outlier_criterions["Detectors"] = [{'Parameters': {'MaxActiveNumberOfTasks': 0, 'MinActiveNumberOfTasks': 0}, 'Type': 'Dixon'}, 
    {'Parameters': {'MaxActiveNumberOfTasks': 0, 'MinActiveNumberOfTasks': 0}, 'Type': 'Chauvenet'}, 
    {'Parameters': {'MaxActiveNumberOfTasks': 0, 'MinActiveNumberOfTasks': 0}, 'Type': 'MAD'}, 
    {'Parameters': {'MaxActiveNumberOfTasks': 0, 'MinActiveNumberOfTasks': 0}, 'Type': 'Grubbs'}, 
    {'Parameters': {'MaxActiveNumberOfTasks': 0, 'MinActiveNumberOfTasks': 0}, 'Type': 'Quartiles'}]

    expected_results, actual_results, outlier_detectors_used = TestOutliers.get_expected_and_actual_values_of_outliers(results, outlier_criterions, result_structure_init)
    # If all OD criterias are disabled, no outlier could appear in task result marks
    for task in range(1, len(expected_results)):
        expected_results[task] = "OK"
    return expected_results, actual_results, outlier_detectors_used
