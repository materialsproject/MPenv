=====
MPenv
=====

This codebase helps users create a virtual environment for running FireWorks within Materials Project in a semi-automated way.


User instructions
=================

Warnings
--------

#. This only works on NERSC

#. This only works if your NERSC shell is BASH, not CSH. Note that by default NERSC often sets CSH.

#. After creating your environment, you can't move or rename it. If you need to delete it see the instructions below.

Part 1 - Install the MPenv code at NERSC and request an environment
-------------------------------------------------------------------

#. Log onto ANY NERSC machine, e.g. Hopper or Carver. At this stage it doesn't matter which one. Let's pick Hopper.

#. Type::

    module load python/2.7.3
    module load virtualenv
    mkdir admin_env
    virtualenv --no-site-packages admin_env
    source admin_env/bin/activate
    cd admin_env
    git clone git@github.com:materialsproject/MPenv.git
    cd MPenv
    python setup.py develop


   ..note:: If the ``git clone`` command fails, make sure your SSH key for the NERSC machine is registered under your GitHub username. This is done by typing ``ssh-keygen -t dsa`` (hit enter at all prompts) and then copying your ``~/.ssh/id_dsa.pub`` file to your Github account (log into github.com, click account settings at top-right, then the 'SSH keys' section).

#. Type::

    which mpenv

   If the installation was successful, the system should find an executable.

#. Request an environment from an administrator (currently Anubhav Jain). The current procedure is just to send an email with a requested environment name, e.g. "aj_vasp". A good environment name should look like "A_B" where "A" is your initials and "B" is some SHORT description that will help you remember what the environment is for. another example: "WC_surfaces".

#. An administrator will create a suite of databases hosted at NERSC for you and send you back a directory, lets call this "aj_vasp_files". *Do not rename or change this directory in any way*.

#. Once you receive the directory, move to the next part.

Part 2 - Install at NERSC
-------------------------

#. Upload the entire files directory you received from an admin (e.g., *aj_vasp_files*) to your home directory at NERSC. Remember to not change this directory!

#. Log onto a NERSC machine (e.g. Hopper) and enter the admin environment that allows you to use MPenv::

    source admin_env/bin/activate

#. Now, you can install your environment. Staying in your home directory, type::

    mpenv aj_vasp

  .. note:: Replace ``aj_vasp`` with whatever environment name you requested, e.g. ``WC_surfaces``.

#. A whole bunch of stuff will happen...just wait for it. Hopefully it will succeed at the end and create a new directory with your environment name.

#. Type::

   source ~/.bashrc.ext

  (or log out and log into NERSC again)

#. Whenever you want to activate your environment, type::

   use_<ENV_NAME>

  e.g., ``use_aj_vasp``.

Part 3 - Customize your environment
-----------------------------------

There are many things about your environment that you can customize. Here are a few.

#. Go to ``<ENV_NAME>/config/config_Hopper`` where <ENV_NAME> is something like ``aj_vasp``. Modify ``my_qadapter.yaml`` so that queue scripts are submitted to the queue you want with the walltime and mppwidth you want. You might want to change the queue to "debug" for example in order to test your environment. Do the same thing for ``config_Mendel``. (Note: Carver is not currently supported)

#. In your ``.bashrc.ext``, you'll want to add two lines::

    export VASP_PSP_DIR=<PATH_TO_POTCARS>
    export MAPI_KEY=<MAPI_KEY>

   where <PATH_TO_POTCARS> contains your POTCARs dir and MAPI_KEY is your Materials Project API key. See the pymatgen docs for more details. Some features of the code (e.g. VASP input generation) won't work without these.


Deleting your environment
=========================

If you ever want to remove your environment completely (this is different than resetting DBs), you should:

#. Contact an administrator to tear down the DB backends

#. Remove the entire directory containing your environment

#. Edit your ``.bashrc.ext`` file - look for the commented section referring to your environment name and delete that section.

Administrator instructions
==========================

#. To create an environment, start in a directory that has your "private" directory containing the admin DB credentials.

#. Type ``mpdbmake <ENV_NAME> <TYPE>`` where <ENV_NAME> is the name the user requested and <TYPE> is either ``FW`` or ``MP`` or ``rubicon``.

#. Archive the resulting DB files somewhere

#. Send the DB files to the user.
