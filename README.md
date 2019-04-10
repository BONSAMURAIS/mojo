# System-model (mojo)
The system model frame work. Turning the raw data into into a computational structure.

This project will be take care of all the modelling choices and data reconciliation between the different data sources. As the very core it will take the raw data from the rdf database and turn it into a computational structure (such as an A-matrix). It will then export it again to the rdf database.

## Hackathon objective (initial version of Bonsai)
For the purpose of the  Barcelona hackathon this will need to update the electricity information in EXIOBASE with the information from the B-entso project. For the first simple model we will use [pySUT](https://github.com/stefanpauliuk/pySUT) to construct an input-output table from supply and use tables (SUTs). pySUT takes numpy arrays (SUTs) as an input and outputs a numpy array A-matrix. 

For this we will need to following:
* Function to query exiobase rdf data and turn it into supply use tables. (main work)
* Function to query electricity mix rdf data. 
* Function to map/aggregate the regional electricity data to the exiobase region/activity/unit name classification.
* Function to insert updated electricity mix information into the the SUTs
* Function (wrapper) to give user options which constructs to apply to turn the SUTs into an A matrix. 
* Function to write the A-matrix to the rdf database.

# Methodology of mojo

### Choice of the construct

For the initial version of Bonsai, it has been decided to use the [Exiobase hybrid version](https://github.com/BONSAMURAIS/EXIOBASE-conversion-software). 

With regard to hybrid tables, the choice on the construct to be used [Majeau-Bettez et al. (2014)](https://doi.org/10.1111/jiec.12142)  is very limited. The industry technology assumption is not an option since an activity may produce outputs in different units. Product technology assumption and by-product technology assumptions give the same results [Suh et al. (2010)]( https://doi.org/10.1111/j.1530-9290.2010.00235.x), unless negative values in the IOTs are manipulated. Usually, this manipulation of negatives is not implemented in LCA. Therefore, the by-product technology results to be the best choice for the current version of Bonsai. However, in order to give more choice to the user, the monetary version of Exiobase could still be an option of further versions. The monetary version of Exiobase provides the product by product (pxp) and industry by industry (ixi) IOTs. The monetary IOTs adopt the industry technology assumption, which is an allocation method.

So, to resume, the Bonsai user may have three choices:
    1. hybrid tables with by-product technology assumption (substitution method) 
    2. monetary ixi IOTs (with allocation method)
    3. monetary pxp IOTs (with allocation method)
       
However, the current version of mojo only deals with bullet 1.

### Aggregation and generation of global markets of exclusive by-products (GMPs)

[Exiobase HSUTs]( https://doi.org/10.1111/jiec.12713) have a format products by activities (pXa). There are 200 products and 164 activities. The initial step consists of aggregating the rows in order to get squared matrices. Before doing that, exclusive by-products are selected. An exclusive by-product is a product carried out as secondary production in a country and not produced elsewhere as principal production (determining production). For example blast furnace gas is a by-product of steel production and it is not produced in any other activity as principal production. In the current version of mojo, a global market is generated for each exclusive by-product. This means that an input of blast furnace gas will be replaced by an input from the global market of gas.

A global market of product (GMP) is an activity with outputs and inputs. Inputs consist of all the productions of that specific product by activities. Only principal productions can feed to GMPs. In our example, the global market of gas is fed by the production of natural gas. The output of a GMP is the sum of all the inputs and is defined as product from global market (pGM) (for example, 'gas from the global market'). The output of GMP is used by any activity replacing exclusive by-products. 

However, because exclusive by-products and the substituting principal productions may have different properties, an homogenization is performed. The latter is implemented by mean of conversion coefficients. For example, in the current version of mojo, a gas global market is built that is only fed by natural gas. Therefore, all the gases defined as exclusive by-products are converted into gas by mean of calorific values.



