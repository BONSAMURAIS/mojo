#system_model.py

'''
BONSAI system model
'''


import pysut
import pandas as pd
import numpy as np
import os
import argparse
import configparser
import mojo_logger
from mojo_logger import LogMessage
import load_exiobase
import aggregation as agg


def system_model(config,logger,log_dir):
    '''
    Function description
    '''
    exio_v, exio_u = load_exiobase.get_sut(config.get('exio_data','ddir'),
                                   config.get('exio_data','supply'),
                                   config.get('exio_data','use'), logger)
    iot_names, country_dic, prod_dic = load_exiobase.\
                                 get_aggregated_product_names(
                                 config.get('exio_data','ddir'),
                                 config.get('exio_data', 'aggregated_names'),
                                 logger)
    
    aggregation_matrix = agg.get_aggregation_matrix(
                                  config.get('exio_data','ddir'),
                                  config.get('exio_data','aggregation_matrix'),
                                  config.get('exio_data','calvals_matrix'),
                                  log_dir, config.get('project_info',
                                  'aggregation_report_file'), logger)
    exio_vagg, exio_uagg = agg.aggregate(exio_v, exio_u, aggregation_matrix,
                                         logger)




def ParseArgs():
    '''
    ParsArgs parser the command line options
    and returns them as a Namespace object
    '''
    print("Parsing arguments...")
    parser = argparse.ArgumentParser()


    parser.add_argument("-c", "--config", type=str, dest='config_file',
                        default='./ConfigFile.ini', help='path to the\
                        configuration file. Default file script folder.')

    parser.add_argument("--cc", dest="copy_config", action="store_true",
                        help="If True saves the config file to the log dir")

    parser.add_argument("--cs", dest="copy_script", action="store_true",
                        help="If True saves the script file to the log dir")

    args = parser.parse_args()

    print("Arguments parsed.")
    return args

if __name__ == "__main__":
    args = ParseArgs()
    if os.path.exists(args.config_file):
        print('Using configuration file: {}'.format(args.config_file))
        config = configparser.ConfigParser()
        config.read(args.config_file)
        print(config.sections())
        projectName = config.get('project_info', 'project_name')
        if config.get('project_info', 'log_dir'):
            log_dir = config.get('project_info', 'log_dir')
        else:
            log_dir = config.get('project_info', 'project_outdir')
        this_script_name = __file__
        logger = mojo_logger.Logger(log_dir, projectName, this_script_name,
                                    args.copy_script, args.copy_config,
                                    os.path.realpath(args.config_file))

        system_model(config,logger, log_dir)

    else:
        print('Config file does not exist, please check path')
        print('exiting...')





