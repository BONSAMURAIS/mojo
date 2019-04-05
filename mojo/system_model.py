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
    iot_names, country_dic, prod_dic, country_list = load_exiobase.\
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
    V_without_elec, U_without_elec, V_elecmarkets, U_elecmarkets,\
           elec_martket_product_supply, elec_martket_product_use =\
           create_electricity_grids(exio_vagg, exio_uagg, N_reg,
                                    N_sec, iot_names)

    

    #check if for the existence of exclusive byproducts
def get_exclusive_byproducts(v,u,N_regions, product_names, logger):
    """Function checks for exclusive byproducts and returns them in an
    array.
    Input:
    v               : numpy array containing the supply table
    u               : numpy array containing the use table
    N_regions       : number of regions in the MRIO
    product_names   : Pandas dataframe with the product names in the aggregated
                      SUTs.

    Output:
    excl_byprod_names   :   numpy array with a list of exclusive by products
                            The same product miight show up multiple times but
                            for different regions
    """
    _name = get_exclusive_byproducts.__name__ #function name for logging
    logger.info(LogMessage(_name, 'Checking for exclusive by products'))
    SUT_obj = pysut.SupplyUseTable(V=v, U=u, regions=N_reg)
    supply_diag_check_eval = SUT_obj.supply_diag_check()
    excl_byprod_names = product_names.values[supply_diag_check_eval[:,2]==1,:]
    if len(excl_byprod_names) == 0:
        logger.info(LogMessage(_name,'No exclusive byproducts found'))
    else:
        logger.info(LogMessage(_name, 'Found total of {} instances of an'\
                                      'exclusive byproduct'))
    return excl_byprod_names

def create_market_and_product_names(prod_names, N_reg, Reg_list, logger):
    """Create market names, and product names.
    Input:
    prod_names      :   array of exclusive byproducts (this should include at
                        at least one electricity byproduct e.g. electricity
                        from coal (as byproduct from heat from coal).
    N_reg           :   number of regions in the MRIO system
    
    Output:
    excl_byproducts :   array of exclusive byproducts (excl electricity)
    market_names    :   array of market names corresponding to the excl byprods
    grid_electricity:   array of 'Electricity from grid' names for the different
                        regions. i.e. 1 entry for each electricity market
    elec_markets    :   Like grid_electricity but now "Market for electricity"

    All outputs have the format [['Region', 'Name', 'code 1', 'code 2', 'unit']]
    where the unit only exists for the products not for the markets. 
    """
    #get a unique list of the product names to create global markets
    unique_prod_indices = np.unique(prod_names[:,1], return_index=True)[-1]
    excl_byproducts = prod_names[unique_prod_indices]
    #print(market_names)
    market_names = excl_byproducts.copy()
    market_names[:,0] = 'GLO' #set the region to global
    #now change the names of the products to Market for 'product', incl codes.
    #also remove the electricity from the excl_byproducts
    rm_index = []
    for i,prod in enumerate(excl_byproducts):
        market_names[i,1] = 'Market for ' + market_names[i,1]
        market_names[i,2] = market_names[i,2].replace('p','m')
        market_names[i,3] = market_names[i,3].replace('C_','M_')
        #there are multiple electricity byproducts. they supplyt the same market
        #so give them the same code/market name
        if 'm40.11' in market_names[i,2]:
            market_names[i,2] = 'm40.11'
            market_names[i,1] = 'Market for electricity'
            market_names[i,3] = 'M_ELEC'
        if 'p40.11.' in prod[2]:
            rm_index.append(i)
    #remove electricity from excl byproducts
    excl_byproducts = np.delete(excl_byproducts, np.array(rm_index), axis=0)
    #drop the duplicate electricity markets
    market_name_indices = np.unique(market_names[:,1], return_index=True)[-1]
    market_names = market_names[market_name_indices]
    #split the markets into exclusive byproduct markets and electricity markets
    elec_markets = np.array([x for x in market_names if x[2]=='m40.11']*N_reg).\
                                                                reshape(N_reg,5)
    elec_markets[:,0] = Reg_list
    market_names = np.delete(market_names,
                             np.where(market_names[:,2]=='m40.11')[0], axis=0)
    #create electricity market products ('Electricity from the grid')
    grid_electricity = elec_markets.copy()
    for i in range(len(elec_markets)):
        grid_electricity[i,1] = 'Electricity from the grid'
        grid_electricity[i,2] = grid_electricity[i,2].replace('m','p')
        grid_electricity[i,3] = grid_electricity[i,3].replace('M_','C_',)
    #drop units for markets:
    elec_markets = elec_markets[:,:-1]
    market_names = market_names[:,:-1]
    return excl_byproducts, market_names, grid_electricity, elec_markets


def create_electricity_grids(exio_vagg, exio_uagg, N_reg, N_prod, iot_names,
                             logger):
    _name = create_electricity_grids.__name__ #function name for logging
    logger.info(LogMessage(_name, 'Creating electricity grid for the {}\
                                   regions'.format(N_reg)))
    U_without_elec = exio_uagg.copy()
    V_without_elec = exio_vagg.copy()
    diag_dummy_indices = np.arange(V_without_elec.shape[0])
    V_without_elec[diag_dummy_indices, diag_dummy_indices] = 0 #set to zero for
    #principle production so we can sum off diagonal electricity
    
    V_elecmarkets = np.zeros(N_reg) #These are the totals of the
    #electricity used in a country, as this is the total that a national grid
    #will provide. Format is (N_reg x 1), will be diagonalized in
    #final V' table
    U_elecmarkets = np.zeros((exio_uagg.shape[0],N_reg)) #This
    #defines the electricity mix in a national grid. This will be updated with
    #entso data. Format (N_prod*N_reg x N_reg)
    elec_indices = iot_names['Product code 1'].str.contains('p40.11').values
    #boolean array with the electricity commodities
    elec_martket_product_use = np.zeros((N_reg, exio_uagg.shape[0])) #The input
    #vector for grid electricity for the different activities, as they now draw
    #from the grid instead of directly from producers.
    #Format (N_reg, N_reg*N_products+N_reg)
    elec_martket_product_supply = np.zeros((N_reg, exio_uagg.shape[0]))
    
    for i in range(N_reg): #loop over countries
        U_elecmarkets[elec_indices,i] = exio_uagg[elec_indices,
                                           i*N_prod:i*N_prod+N_prod].sum(axis=1)
        V_elecmarkets[i] = U_elecmarkets[elec_indices,i].sum()
        elec_martket_product_use[i,i*N_prod:i*N_prod+N_prod] = exio_uagg[
                              elec_indices,i*N_prod:i*N_prod+N_prod].sum(axis=0)
        elec_martket_product_supply[i,i*N_prod:i*N_prod+N_prod] =\
               V_without_elec[elec_indices,i*N_prod:i*N_prod+N_prod].sum(axis=0)
        V_without_elec[elec_indices,i*N_prod:i*N_prod+N_prod] = 0
    
    V_without_elec[diag_dummy_indices, diag_dummy_indices] = exio_vagg[
                                         diag_dummy_indices, diag_dummy_indices]
    U_without_elec[elec_indices,:] = 0 #is the new partial Use table where
    #electricity use from producers has been set to 0
    return V_without_elec, U_without_elec, V_elecmarkets, U_elecmarkets,\
           elec_martket_product_supply, elec_martket_product_use

def create_excl_byprod_markets(v,u,):



def ParseArgs():
    '''
    ParsArgs parser the command line options
    and returns them as a Namespace object
    '''
    print("Parsing arguments...")
    parser = argparse.ArgumentParser()


    parser.add_argument("-c", "--config", type=str, dest='config_file',
                        default='./ConfigFile.ini', help='path to the'\
                        'configuration file. Default file script folder.')

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





