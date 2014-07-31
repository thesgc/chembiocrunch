========================
ChembioCrunch
========================

Chembiocrunch is a work in progress project to create a data analysis tool for bioassays.
The first release is not yet working

Use Cases
========================

A user might have a CSV file with a set of rows produced by each plate well in a 96 well plate, 
these need to be averaged just as you might if using Excel pivot tables

They may then need to select out and transform some of the rows to be used in a calculation with the other rows
This would be done using vlookup in Excel

The idea is to store each of these operations in a workflow that can be applied to other data files.

The system will then support graphing and curve fitting so that a publication-quality visualisation can be produced

Contact the team if you would like to know more. We will potentially create an online demo.

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

Based upon

A project template for Django 1.6 (with a tag for Django 1.5).

To use this project follow these steps:

#. Create your working environment
#. Install Django
#. Create the new project using the django-two-scoops template
#. Install additional dependencies
#. Use the Django admin to create the project

*note: these instructions show creation of a project called "icecream".  You
should replace this name with the actual name of your project.*

Working Environment
===================

You have several options in setting up your working environment.  We recommend
using virtualenv to separate the dependencies of your project from your system's
python environment.  If on Linux or Mac OS X, you can also use virtualenvwrapper to help manage multiple virtualenvs across different projects.

Virtualenv Only
---------------

First, make sure you are using virtualenv (http://www.virtualenv.org). Once
that's installed, create your virtualenv::

    $ virtualenv icecream

You will also need to ensure that the virtualenv has the project directory
added to the path. Adding the project directory will allow `django-admin.py` to
be able to change settings using the `--settings` flag.

Virtualenv with virtualenvwrapper
------------------------------------

In Linux and Mac OSX, you can install virtualenvwrapper (http://virtualenvwrapper.readthedocs.org/en/latest/),
which will take care of managing your virtual environments and adding the
project path to the `site-directory` for you::

    $ mkdir icecream
    $ mkvirtualenv -a icecream icecream-dev
    $ cd icecream && add2virtualenv `pwd`

Using virtualenvwrapper with Windows
----------------------------------------

There is a special version of virtualenvwrapper for use with Windows (https://pypi.python.org/pypi/virtualenvwrapper-win).::

    > mkdir icecream
    > mkvirtualenv icecream-dev
    > add2virtualenv icecream


Installing Django
=================

To install Django in the new virtual environment, run the following command::

    $ pip install django

Creating your project
=====================

To create a new Django project called '**icecream**' using
django-twoscoops-project, run the following command::

    $ django-admin.py startproject --template=https://github.com/twoscoops/django-twoscoops-project/archive/master.zip --extension=py,rst,html icecream_project

For Django 1.5 users, we recommend::

    $ django-admin.py startproject --template=https://github.com/twoscoops/django-twoscoops-project/archive/1.5.zip --extension=py,rst,html icecream_project

Installation of Dependencies
=============================

Depending on where you are installing dependencies:

In development::

    $ pip install -r requirements/local.txt

For production::

    $ pip install -r requirements.txt

*note: We install production requirements this way because many Platforms as a
Services expect a requirements.txt file in the root of projects.*

