========================
ChembioCrunch
========================

Chembiocrunch is a work in progress project to create a data analysis tool for scientists.
Sub modules will be focussed on bioassays to cover functions such as:

* Data visualisation from any CSV format

* IC50 curves

* Data import from different machines


Technologies
=======================

Front end:
-------------------------
Bootstrap, HTML, jquery datatables, django crispy forms, django floppy forms

Back end
------------------------
Django, pandas, pytables, all installed under miniconda

Development tools
-------------------------
Vagrant - currently there is a box file which runs Centos, ubuntu version coming soon.

Deployment
-------------------------
looking to add package management for linux with fpm  as well as a windows installer

Testing approach
-------------------------
Currently adding some integration tests


Development Approach
=======================


We are looking to build this project according to the django best practises outlined in Greenfeld and Roy's Two Scoops of Django.
This means as far as possible:
* DRY views, models and forms
* Single object logic abstracted to models.py
* Form and formset processing all done in forms.py
* Forms generated on the backend using crispy forms
* pandas functionality in a backend file
* Matplotlib code location TBA - it will need to be more thread safe than currently
* PEP8 (not tested yet)

Permissions 
=======================
* Initially, the graphing system is designed to lock down a user's profile so nobody else can access the graphs that they have created
* This is done by view inheritance
* Every view that is to do with workflows and data starts off with the WorkflowView or WorkflowDetailView
* The get_queryset function limits the data based on the request user, this defers to models.py. 
* Future sharing implementations will have to alter this functionality


Settings
=======================
The following has been set up in the settings file which allows the temprary file path to be read during upload

    FILE_UPLOAD_HANDLERS = ( "django.core.files.uploadhandler.TemporaryFileUploadHandler","django.core.files.uploadhandler.MemoryFileUploadHandler",)



