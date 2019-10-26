# System-model (mojo)
This repository describes the making of the system model framework, i.e. turning the raw data into into a computational structure.

This system model deals with of all the modelling choices and data reconciliation between the different data sources. The very core takes the raw data from the rdf database and turn it into a computational structure (such as an A-matrix). Then, it exports it again to the rdf database.

## Hackathon objective (initial version of Bonsai)
For the purpose of the 2019 Barcelona hackathon, the electricity information in EXIOBASE needs to be updated with the information from the B-entso project. For the first simple model we use [pySUT](https://github.com/stefanpauliuk/pySUT) to construct an input-output table from supply and use tables (SUTs). pySUT takes numpy arrays (SUTs) as an input and outputs a numpy array A-matrix. 

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

Resuming, the Bonsai user may have three choices:

 1. hybrid tables with by-product technology assumption (substitution method) 
 2. monetary ixi IOTs (with allocation method)
 3. monetary pxp IOTs (with allocation method)
       
However, the current version of mojo only deals with bullet 1.

### Why flows do not have a location
In Supply & Use tables the flows and flow Objects do not need to be specified by location, since they obtain that from the location of the activity.
In a Direct Requirements Table the Supply data and the Use data are combined by applying some specific assumptions about how activities supply each other. In other words, each flow is connected to both a supplying and a using activity. The flows still do not need to be specified by location, since this is given by the supplying and using activities. Several assumptions can be be made for linking of activities and flows. Different Requirement Tables can be produced simply by changing the linking assumptions.

Yet, in the EXIOBASE hybrid Use table, we find that Flows have been provided with (country of origin) location, because EXIOBASE hybrid Use table combines data from two original data sources: The national Supply & Use tables and a balanced version of the international bi-lateral trade data. For transparency reasons, as well as to allow flexibility of use, is important to keep the original Supply & Use data separate from the linking assumptions. To do so the EXIOBASE Hybrid tables shall be de-constructed into the original national Supply & Use tables and a trade matrix, both of which can be stored in the BONSAI format, without the need to assign a location to any flow. The original Supply & Use data is simply obtained by summing all uses of each flow object into one flow. The trade information is preserved by taking the off-diagonal trade flows from the EXIOBASE Use table and placing them in the separate trade matrix.

This is furhter explained in the [docs](https://github.com/BONSAMURAIS/mojo/blob/master/docs/Why_flows_dont_need_location.md) attached to this repository, in the file [Why do flows not have a location](https://github.com/BONSAMURAIS/mojo/blob/master/docs/Why_flows_dont_need_location.md) and in the related [excel file](https://github.com/BONSAMURAIS/mojo/blob/master/docs/Why_flows_%20dont_have_%20location.xlsx).

### Aggregation and generation of global markets for exclusive by-products

[Exiobase HSUTs]( https://doi.org/10.1111/jiec.12713) have a format products by activities (pXa). There are 200 products and 164 activities. The initial step consists of aggregating the rows in order to get squared matrices. Before doing that, exclusive by-products are selected. Given a country, an exclusive by-product is a product carried out as secondary production  and not produced elsewhere as principal production ([determining production](https://consequential-lca.org/glossary/#determining-product)). For example blast furnace gas is a by-product of steel production and it is not produced in any other activity as principal production. In the current version of mojo, a *global market* is generated for each exclusive by-product. 

A *global market of product* (GMP) is an activity with outputs and inputs. Inputs consist of all the principal productions of that specific product by activities across the world. It is important to notice that only principal productions can be inputs to GMPs.The output of a GMP is the sum of all the inputs and is defined as *product from the global market* (pGM) (for example, 'gas from the global market'). The pGM is used by any activity insted of exclusive by-products. In our example, an input of blast furnace gas will be replaced by an input of gas from the global market, which consists of natural gas produced in all countries across the world. In this case it is implicitly assumed that an activity can use blast furnace gas or natural gas indifferently. At the same time, as for activity producing exclusive by-products, it is assumed that the by-product will replace the product from the global market. In our example, when the steel activity produces blast furnace gas, it will reduce the supply of gas from the global market. Notice that the substitution of exclusive by-products with product from the global market is not valid for internal uses.

When building markets, it is important to take into account the properties of produts. Indeed exclusive by-products and the substituting principal productions may have different properties, therefore an homogenization must be performed. This is implemented by mean of conversion coefficients. For example, in the current version of mojo a global market of gas is homogenized using calorific values.

![Figure](https://github.com/BONSAMURAIS/mojo/blob/master/docs/Mojo_aggreg_exclusive_BP.jpeg)

*Figure 1 - Generation of global markets for exclusive by-products*

### Integration of ENTSO-E data: generation of electricity markets

The introduction of *national electricity markets* (NEMs) is necessary to integrate the [ENTSO-E data](https://www.entsoe.eu/data/) into Exiobase. For each country/region of Exiobase, a NEM is built. NEMs can be seen as the national electricity grids, which provide electricity supplied by different power plants, including imported electricity.
In Bonsai NEMs are activities with outputs and inputs. Inputs are directly taken from the ENTSO-E data and output are just the sum of these inputs. The output of electricity market is the *electricity from the grid* (EfG). Because of the by-product technology assumption, electricity from waste in the ENTSO data is excluded from the inputs to the market. Electricity carried out by waste treatment activities as by-product is assumed to replace the electricity from NEMs. In this way mojo internalizes the electricity from waste tretment in the system model.

Al the activities are assumed to use the electricity from the grid. Therefore the inputs of different types in Exiobase are replaced by an unique input form the grid.

![Figure2](https://github.com/BONSAMURAIS/mojo/blob/master/docs/Entsoe_tables_v1.jpg)

*Figure 2 - ENTSO-E data incorporated into Exiobase HSUTs
