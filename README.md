# Licences Catalogue
A Linked Data catalogue of policies (licenses, laws etc.) presented as Policies according to the [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/).

This catalogue is a website tool to allow people to find policies according to certain criteria and is also a policy writing tool; with it you can author both new abstract policies and also specific implementations of policies for particular purposes.

The technology used is Python Flask - a bare-bones HTTP framework - configured as a simple Model-View-Controller application with the application data being stored in SQLite. Data can be viewed in RDF/Turtle, JSON, and JSON-LD formats.

Further project documentation is in the [_docs/](_docs/) folder of this repository.

## Setup

1. Install Python modules found in requirements.txt
2. Copy template.py in _conf, rename the duplicate to \_\_init\_\_.py, and fill in the configuration options.
3. Run create_database.py
4. Run seed_database.py (if you want the app populated with licences, otherwise skip this step)
5. Ensure that the database file and its parent directory have read/write permissions.
6. Run app.py


## License
This repository is licensed under Creative Commons 4.0 International. See the [LICENSE deed](LICENSE) for details.

## Contacts
Project Lead:  
**Nicholas Car**  
*Senior Experimental Scientist*  
CSIRO Land & Water, Environmental Informatics Group  
Brisbane, Qld, Australia  
<nicholas.car@csiro.au>  
<http://orcid.org/0000-0002-8742-7730>  

Developer:  
**Laura Guillory**  
*Software Engineer*  
CSIRO Land & Water, Environmental Informatics Group  
Brisbane, Qld, Australia  
<laura.guillory@csiro.au>  
