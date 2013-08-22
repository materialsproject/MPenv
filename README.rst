=====
MPenv
=====

This codebase helps users create a virtual environment for running FireWorks within Materials Project in a semi-automated way.


User instructions
=================

Part 1 - Request a virtual environment and prepare for installation
-------------------------------------------------------------------

#. Request an environment from an administrator (currently Anubhav Jain). The current procedure is just to send an email with a requested environment name, e.g. "aj1".

#. An administrator will create a suite of databases hosted at NERSC for you and send you back a directory, lets call this "aj1_files". *Do not rename or change this directory in any way*. In the meantime, continue following these instructions.

#. Log onto ANY NERSC machine, e.g. Hopper or Carver. At this stage it doesn't matter which one. Let's pick Hopper.

#. Type::

    module load python/2.7.3
    module load virtualenv
    mkdir admin_env
    virtualenv --no-site-packages admin_env
    source admin_env/bin/activate
    cd admin_env
    git clone

Administrator instructions
==========================

