__doc__ = """
    Module to read config and tasks for execute."""
import json
import logging
# import os 
# from sys import path
# from os.path import abspath, join

# print("----------------")
# print(os.getcwd())
# print("----------------")

from tools.file_system_io import load_json_file, create_folder_if_not_exists
from Resources.validator import is_experiment_description_valid


def read_global_config(global_config_path):
    """
    Method reads configuration for BRISE from GlobalConfig.json configuration file.
    :param global_config_path: sting path to file.
    :return: dict with configuration for BRISE
    """
    logger = logging.getLogger(__name__)
    try:
        config = load_json_file(global_config_path)
        return config

    except IOError as e:
        logger.error('No config file found: %s' % e, exc_info=True)
        exit(3)
    except ValueError as e:
        logger.error('Invalid configuration file: %s' % e, exc_info=True)
        exit(3)


def load_task(path_to_file="./Resources/task.json"):
    """
    Method reads task configuration from task.json file.
    :param path_to_file: sting path to task file.
    :return: dict with task parameters and task data.
    """
    # TODO: Add task file validation. The file contains all parameters of the task that BRISE require
    logger = logging.getLogger(__name__)
    try:
        task = load_json_file(path_to_file)
        data = load_json_file(task["DomainDescription"]["DataFile"])
        taskDataPoints = []
        #TODO the dimensions validation in the task data file
        for dimension in task["DomainDescription"]["FeatureNames"]:
            taskDataPoints.append(data[dimension])
        task["DomainDescription"]["AllConfigurations"] = taskDataPoints
    except IOError as e:
        logger.error('Error with reading task.json file: %s' % e, exc_info=True)
        exit(1)
    except json.JSONDecodeError as e:
        logger.error('Error with decoding task: %s' % e, exc_info=True)
        exit(1)
    return task


def initialize_config(argv):
    """
    Load global config and task config.
    :return: (dict globalConfiguration, dict taskConfiguration)
    """
    logger = logging.getLogger(__name__)

    taskPath = argv[1] if len(argv) > 1 else './Resources/task.json'
    global_config_path = argv[2] if len(argv) > 2 else './GlobalConfig.json'
    schemaPath = './Resources/schema/task.schema.json' # validation for task.json in `taskPath`

    logger.info("Global BRISE configuration file: %s, task description file path: %s" % (taskPath, global_config_path))
    #   Reading config file
    globalConfig = read_global_config(global_config_path)

    #   Loading task config and creating config points distribution according to Sobol.
    # {"task_name": String, "params": Dict, "taskDataPoints": List of points }
    task = load_task(taskPath)

    create_folder_if_not_exists(globalConfig['results_storage'])

    if is_experiment_description_valid(schema_path=schemaPath, file_path=taskPath):
        logger.info(" Task file %s is valid" % taskPath)
        return globalConfig, task  
    else: exit(1)

if __name__ == "__main__":
    initialize_config({})
