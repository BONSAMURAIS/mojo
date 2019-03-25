# system-model
The system model frame work. Turning the raw data into into a computational structure.

This project will be take care of all the modelling choices and data reconciliation between the different data sources. As the very core it will take the raw data from the rdf database and turn it into a computational structure (such as an A-matrix). It will then export it again to the rdf database.

## Hackathon objective
For the purpose of the  Barcelona hackathon this will need to update the electricity information in EXIOBASE with the information from the B-entso project. For the first simple model we will use [pySUT](https://github.com/stefanpauliuk/pySUT) to construct an input-output table from supply and use tables (SUTs). pySUT takes numpy arrays (SUTs) as an input and outputs a numpy array A-matrix. 

For this we will need to following:
* Module to query exiobase rdf data and turn it into supply use tables. (main work)
* Module to query electricity mix rdf data. 
* Module to insert updated electricity mix information into the the SUTs
* Module (wrapper) to give user options which constructs to apply to turn the SUTs into an A matrix. 
* Module to write the A-matrix to the rdf database.


