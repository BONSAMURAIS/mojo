import pandas as pd
import numpy as np
import os
from mojo_logger import LogMessage
import sys

def get_sut(path_name, v_name, u_name, logger):
    """Read in the supply and use tables from csv file.
    Input:
    path_name   Directory of data
    v_name      File name supply table
    u_name      File name use table
    
    Output:
    exio_v      Numpy array with the supply table
    exio_u      Numpy array with the use table
    """
    _name = get_sut.__name__#record function name for logging
    u_p2f = os.path.join(path_name, u_name)
    v_p2f = os.path.join(path_name, v_name)
    if not os.path.exists(u_p2f):
        logger.error(LogMessage(_name,'Use table file {} does not exist.'
                                       'Exiting!'.format(u_p2f)))
        sys.exit("Please check the file paths in the configuration file. Exit")
    elif not os.path.exists(v_p2f):
        logger.error(LogMessage(_name,'Supply table file {} does not exist.'
                                       'Exiting!'.format(v_p2f)))
        sys.exit("Please check the file paths in the configuration file. Exit")
    else:
        logger.info(LogMessage(_name, 'Reading in V from: {}'.format(v_p2f)))
        exio_v = pd.read_csv(v_p2f, header=[0,1,2,3], index_col=[0,1,2,3,4])
        logger.info(LogMessage(_name, 'Reading in U from: {}'.format(u_p2f)))
        exio_u = pd.read_csv(u_p2f, header=[0,1,2,3], index_col=[0,1,2,3,4])
    
    return exio_v.values, exio_u.values


def get_aggregated_product_names(path_name, prod_name_file, logger):
    '''Returns a pandas DataFrame with the product names of the aggregated
    SUT/IOT, along with ditionaries mapping the countries and products to their
    index in the table.
    Input:
    path_name       Directory of file
    prod_name_file  File name
    
    Ouput:
    
    '''
    _name = get_aggregated_product_names.__name__ #function name for logging
    p2f = os.path.join(path_name, prod_name_file)
    if not os.path.exists(p2f):
        logger.error(LogMessage(_name,'File path {} does not exist. Exiting!'.
                                        format(p2f)))
        sys.exit("Please check the file paths in the configuration file. Exit")
    agg_names = pd.read_csv(p2f)
    logger.info(LogMessage(_name, 'Loading aggregated product names from {}'.
                           format(p2f)))

    country_list = agg_names['Country code'].unique()
    country_dic = {}
    for i,c in enumerate(country_list):
        country_dic[c] = i
    
    
    products = agg_names[['Product name', 'Product code 1']]
    products.drop_duplicates(inplace=True)
    prod_dic = {}
    for i,prod in enumerate(products['Product name'].values):
        prod_dic[prod] = i
    
    return agg_names, country_dic, prod_dic, country_list


