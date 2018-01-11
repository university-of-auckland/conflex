# Wiki To Capsule Integration Application

This application is designed to replace the current Wiki-to-Capsule Integration application that is written in 
Java/Groovy and run through Scriptella.

For more information about the Application, please see the following 
[wiki page](https://wiki.auckland.ac.nz/display/APPLCTN/Capsule+Future+State+Application+Design)

## Running The Application
This application is written using python v3.6. It is advisable but not necessary to run the application 
using virtualenv. Please install the required libraries through pip using: `pip install -r requirements.txt`

To run the application simply pass the containing folder to the python interpreter and the `__main__.py` will be 
invoked. i.e. `python /path/to/capsule`.

## Making Documentation
The application supports documentation through Sphinx. To generate the Documentation run `make html`. Currently the
only way to do this is through the `Makefile`, the `make.bat` script has not been correctly configured.