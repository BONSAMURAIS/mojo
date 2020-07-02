#aggregation.py
import os
import numpy as np
import pandas as pd
from mojo_logger import LogMessage
import sys

def aggregate_row(v,u,aggregation_matrix, logger): #SM:this funtion aggregates only rows
    """Aggreagte supply and use tables through multiplication with
    aggregation matrix. All of the tables are considered to be of the format
    (products x industries).
    Input:
    v       : supply table (products x industries)
    u       : use table (products x industries)
    aggregation_matrix : aggregation matrix (products x industries)

    Ouput:
    vagg    : aggregated supply table (products x industries)
    uagg    : aggregated use table (products x industries)
    """
    logger.info(LogMessage(aggregate.__name__,
                'Aggregating supply and use tables...'))
    vagg = aggregation_matrix.T.dot(v)
    uagg = aggregation_matrix.T.dot(v)
    logger.info(LogMessage(aggregate.__name__,
                'Succesfully aggregated supply and use tables.'))
    return vagg, uagg


'''SM:this procedure gives different weight to the aggregation coeff
in order to generalize this procedure,besides what has been already included below, we would need
a vector where the different weights are inserted. I think this can be an input for the function

>>>for example:
cal_val_ratios=np.array([[0.0387/0.048,0.00274/0.048,0.00706/0.048,0.0387/0.048,0.0504/0.048]])
prod_code=np.array(['p.40.02a','p.40.02b','p.40.02c','p.40.02d','p.40.02e'])
act_code=np.array(['A_MGWG'])
new_key=pd.DataFrame(columns=act_code, index=prod_code,data=cal_val_ratios.T)


agg_mat[agg_mat.where(new_key>0)>0]=new_key
'''

def get_aggregation_matrix(path_name, agg_file, new_key,
                           agg_report_path, agg_report_file,logger):
    """Returns a numpy array which can be used for aggregation
    For now it aggregates by 'principle coproducts' so that each industry has
    one principle product. The products that are aggregated are written out
    to an aggregation report with filename specified by user.
    
    Input:
    path_name:      Path to directory containing the aggregation matrix
                    and matrix with the caloric values.
    agg_file        File name of aggregation matrx
    cal_file        File name of file with calorific values
    agg_report_path Path to direcotry where the aggregation report is written
    agg_report_file File name for aggregation report
    
    Output:
    new_aggregation_matrix
                    Aggregation matrix with the relative caloric values for
                    the to be aggregated values
    

    Note: For now only aggregates the 'Manufacture of gas;', 'i40.2.a', 'A_MGWG'
    using the caloric values relative to natural gas, so that it can later
    later subsitute natural gas.
    """
    _name = get_aggregation_matrix.__name__ #function name for logging purposes
    
    a_p2f = os.path.join(path_name, agg_file) #path2file
    if not os.path.exists(a_p2f):
        logger.error(LogMessage(_name, 'file {} does not exist. Exiting!'\
                                                                .format(a_p2f)))
        sys.exit("Please check the file paths in the configuration file. Exit")

    logger.info(LogMessage(_name, 'Reading aggregation matrix from {}'.format(
                                                                        a_p2f)))
    aggregation_matrix = pd.read_csv(a_p2f, header=[0,1,2], index_col=[0,1,2,3])
    
    c_p2f = os.path.join(path_name, cal_file)
    if not os.path.exists(c_p2f):
        logger.error(LogMessage(_name, 'file {} does not exist. Exiting!'\
                                                                .format(c_p2f)))
        sys.exit("Please check the file paths in the configuration file. Exit")
        
    logger.info(LogMessage(_name, 'Reading colorific values from {}'.format(
                                                                        c_p2f)))
    calval = pd.read_csv(c_p2f, header=[4], index_col=[0,1,2,3])
    calval.fillna(1, inplace=True) #fill all empty places with a 1
    
    Natural_gas_calval = calval.loc[calval.index.get_level_values(3)
                                                    == 'C_GASE'].values[0]
    #natural gas production has the same caloric value for now but we keep
    #the a specific value for now, as this might change in with better data
    #given that not all natural gas has the exact same calorix value.
    
    #Nr of regions
    N_reg = calval.loc[calval.index.get_level_values(3) == 'C_GASE'].shape[1]
    logger.info(LogMessage(_name, 'Number of regions: {}'.format(N_reg)))
    #Nr of Products
    N_prod = aggregation_matrix.shape[0]
    logger.info(LogMessage(_name, 'Number of products before aggregation: {}'
                                                               .format(N_prod)))
    #Nr of sectors
    N_sec = aggregation_matrix.shape[1]
    logger.info(LogMessage(_name, 'Number of sectors is {}'.format(N_sec)))
    logger.info(LogMessage(_name, 'Number of products after aggregation: {}'.
                                                                 format(N_sec)))
    
    #insert relative caloric values for in Manufacturing of Gas section
    new_aggregation_matrix = np.zeros((N_reg*N_prod,N_reg*N_sec))
    for i in range(N_reg):
        new_aggregation_matrix[i*N_prod:i*N_prod+N_prod,
                               i*N_sec:i*N_sec+N_sec] = aggregation_matrix
    logger.info(LogMessage(_name, 'Inserting calorific values for {}'.format(
                                   aggregation_matrix.columns[109][0])))
    for i in range(N_reg):
        #print(calval.iloc[141:146,i]/Natural_gas_calval[i])
        new_aggregation_matrix[i*N_prod+141:i*N_prod+146,i*N_sec+109] =\
                                    calval.iloc[141:146,i]/Natural_gas_calval[i]

    #write aggregation report
    country_list = list(calval.columns)
    aggregation_report(aggregation_matrix, new_aggregation_matrix,
                            ['Manufacure of Gas'], country_list,
                            agg_report_path, agg_report_file,
                            N_reg, N_prod, N_sec, logger)
    logger.info(LogMessage(_name, 'Aggregation report written to {}'.format(
                               os.path.join(agg_report_path, agg_report_file))))
    
    return new_aggregation_matrix, N_reg, N_prod, N_sec



def aggregation_report(aggregation_matrix, new_aggregation_matrix,
                       industry_list, country_list, out_dir, out_file,
                       N_reg, N_prod, N_sec, logger):
    '''
    Writes a csv file with the names of products that are aggregated in
    which industry and with what value (i.e. just summed or weighted sum using
    relative caloric values).
    Input:
    aggregation_matrix          The original aggregation matrix as a pandas DF
    new_aggregation_matrix      The N_reg*N_prod x N_reg*Nsec aggregation matrix
                                containing the relative caloric values.
    industry_list               List containing industries that have been
                                aggregated using caloric values.
    country_list                A list of the countries
    out_dir                     Output directory name
    out_file                    Ouput file name
    '''


    nr_of_products = []
    p2f = os.path.join(out_dir, out_file)
    with open(p2f, 'w') as f:
        f.write('# Agrgegation report \n')
        f.write('# The Following industries were aggregated using'+
                'caloric values: \n')
        for industry in industry_list:
            f.write('# {} \n'.format(industry))
        f.write('|'.join(['Country code','Industry name','Industry code 1',
                  'Industry code 2', 'Number of products to be aggregated',
                  'Product name', 'Product code 1','Product code 2',
                  'Aggregation Value', '\n']))
        for c in range(N_reg):
            for i in range(aggregation_matrix.shape[1]):
                n_prods = aggregation_matrix.iloc[:,i].sum()
                if n_prods > 1:
                    prod_inds = np.where(aggregation_matrix.iloc[:,i]==1)[0]
                    #print(prod_inds)
                    aggregated_prods = [aggregation_matrix.index[x] for
                                                                 x in prod_inds]
                    aggregation_values = new_aggregation_matrix[
                                                  prod_inds+c*N_prod, i+c*N_sec]
                    #print(aggregation_values)
                    nr_of_products.append(n_prods)
                    #print(*aggregation_matrix.columns[i], n_prods)
                    for j,prod in enumerate(aggregated_prods):
                        #if j == 0:
                        #    print(prod[1:])
                            f.write('|'.join([country_list[c],'|'.join(
                                    aggregation_matrix.columns[i]),
                                    '{}'.format(n_prods), '|'.join(prod[1:]),
                                    '{}'.format(aggregation_values[j]), '\n']))
                        #else:
                        #    f.write('|'.join(['','','','','', '|'.join(
                        #            prod[1:]), '{}'.format(
                        #            aggregation_values[j]), '\n']))
    return


