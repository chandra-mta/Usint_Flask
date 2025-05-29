============================
Usint Flask Application
============================

This repo contains the Python Flask application supporting the `Usint Website <https://cxc.cfa.harvard.edu/wsgi/cus/usint/>`_ .
For information related to the webserver backend and support and development of this application, consult the Flask/Usint folder in the MTA shared drive.

Structure
=========

* usint (and usint.py) --- Python script for instantiating the Flask application. Navigating to this file in a web browser starts the application.
* config.py --- Configuration file.
* localhost --- A tcsh shell script used for quickly starting a localhost test of the application by using the /data/mta4/CUS/ska3-cus-r2d2-v environment.
* instance --- instance folder for storing the specific application instance files, such as logs and the usint.db file.
  * logs --- A directory for containing ocat.log files for logging application running information. Used by web server processes.
* cus_app --- Main Flask application folder containing relevant page generation scripts.

  * __init__.py --- Application instantiation script.
  * emailing.py --- Email related functions for all notification purposes.
  * models.py --- Module for defining the SQLAlchemy ORM classes which let the python application interface with the Usint Revision database.
  * chkupdata --- A directory to keep parameter check page related scripts.
  * errors --- A directory to keep error handler page related scripts.
  * express --- A directory to keep express signoff page related scripts.
  * ocatdatapage --- A directory to keep ocat data page related scripts.
  * orupdate --- A directory to keep parameter status page related scripts.
  * scheduler --- A directory to keep TOO duty scheduler page related scripts.
  * supple --- A directory to keep supplemental python scripts.
  * static:

    * color.json --- JSON file matching color names to rgb strings.
    * labels.json --- JSON file matching ocat parameters to visual labels.
    * parameter_selections.json --- JSON file matching sets of parameters for various purposes across the application.
    * usint.js --- jQuery library for the ocatdatapage.
    * ocat_style.css --- Ocat CSS style sheets.
    * ocatdatapage --- A directory to keep ocatdatapage related static files/HTML pages.
    * orupdate --- A directory to keep orupdate related static HTML page.
    * scheduler --- A directory to keep scheduler related static HTML page.
  * templates:

    * base.html --- A base HTML template.
    * index.html --- A main index page.
    * page-related templates --- these directories will be described in the page-specific sections below.

chkupdata
=========

Display all original/requested/current parameter values for a given <obsid>.<rev>.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the parameter check page.
* __init__.py --- Script to setup the function.

templates:
    
* index.html --- Main page.
* provide_obsidrev.html --- Page to display the notice when <obsid>.<rev> is not found.
* macros.html --- Macro holder.

error
=====

Error handler.

* handlers.py --- Main script.
* __init__.py --- Script to setup the function.

templates:
    
* 404.html --- 404 error page.
* 500.html --- 500 error page.

express
=======

Express sign-off/approval page.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the express approval page.
* __init__.py --- Script to setup the function.

templates:
    
* index.html --- Main page.
* confirm.html --- Confirmation page.
* macros.html --- Macro holder.

ocatdatapage
============

Ocat data page to update the parameter values.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the ocat data page.
* format_ocat_data.py --- Module for formatting ocat parameter data structures.
* __init__.py --- Script to setup the function.

additional data:

* <obs_ss>/mp_long_term --- Planned roll angle from MP site.
* <obs_ss>/scheduled_obs_list --- Scheduled obsids.

templates:
    
* index.html --- Main page/parameter value update page.
* macros.html --- Macro holder.
* confirm.html --- Updated parameter value confirmation page.
* finalize.html --- Page to display the job complete notification.
* provide_obsid.html --- Page to display <obsid> if it was not found.

orupdate
========

Target parameter status page.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the parameter status page.
* __init__.py --- Script to setup the function.

templates:
    
* index.html --- Main page.
* macros.html --- Macro holder.

The page is refreshed every 3 minutes to display the most recent data. This is done because multiple users can be updating the databases and someone else might update them while a user tries to update the database.

rm_submission
=============

Remove an accidental submission.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the remove submission status page.
* __init__.py --- Script to setup the function.

templates:
    
* index.html --- Main page.
* macros.html --- Macro holder.

scheduler
=========

POC duty sign-up sheet.

* routes.py --- Main script.
* forms.py --- Module for Python WTForms relating to the TOO duty scheduler page.
* __init__.py --- Script to setup the function.

templates:

* index.html --- Main page.
* macros.html --- Macro holder.

supple
======

Provide supplemental scripts used by several groups.

* database_interface.py --- Module containing SQLAlchemy functions for interfacing with the Usint Revision SQLite database
* helper_functions.py --- Module containing helper functions for multiple scripts.
* read_ocat_data.py --- Module for using the ska_dbi SQSH interface to fetch Ocat Sybase data and format result into python native objects.

data:

* CXC Ocat Sybase database (via read_ocat_data.py)
* Usint Revision SQLite database (via database_interface.py)