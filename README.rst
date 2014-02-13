=====
MPenv
=====

This codebase helps users create a virtual environment for running FireWorks within Materials Project in a semi-automated way.


User instructions
=================

Warnings
--------

1. This only works on NERSC

2. This only works if your NERSC shell is BASH, not CSH. Note that by default NERSC often sets CSH. **Seriously, BASH needs to be your DEFAULT shell. You cannot just start bash within CSH or virtualenv fails at NERSC.** To change your default shell, login to nim.nersc.gov, go to 'Logins by host', then 'change login shell', then change your shells.

3. After creating your environment, you can't move or rename it. If you need to delete it see the instructions below.

Part 1 - Install the MPenv code at NERSC and request an environment
-------------------------------------------------------------------

1. Log onto ANY NERSC machine, e.g. Hopper or Carver. At this stage it doesn't matter which one. Let's pick Hopper.

2. Type::

    module load python/2.7.5
    module load virtualenv
    mkdir admin_env
    virtualenv --no-site-packages admin_env
    source admin_env/bin/activate
    cd admin_env
    git clone git@github.com:materialsproject/MPenv.git
    cd MPenv
    python setup.py develop


  .. note:: If the ``git clone`` command fails, make sure your SSH key for the NERSC machine is registered under your GitHub username. This is done by typing ``ssh-keygen -t dsa`` (hit enter at all prompts) and then copying your ``~/.ssh/id_dsa.pub`` file to your Github account (log into github.com, click account settings at top-right, then the 'SSH keys' section).

3. Type::

    which mpenv

   If the installation was successful, the system should find an executable.

4. Request an environment from an administrator (currently Anubhav Jain). The current procedure is just to send an email with a requested environment name, e.g. "aj_vasp". A good environment name should look like "A_B" where "A" is your initials and "B" is some SHORT description that will help you remember what the environment is for. another example: "wc_surfaces".

5. An administrator will create a suite of databases hosted at NERSC for you and send you back a directory, lets call this "aj_vasp_files". *Do not rename or change this directory in any way*.

6. Once you receive the directory, move to the next part.

Part 2 - Install at NERSC
-------------------------

1. Upload the entire files directory you received from an admin (e.g., *aj_vasp_files*) to your home directory at NERSC. Remember to not change this directory!

2. Log onto a NERSC machine (e.g. Hopper) and enter the admin environment that allows you to use MPenv::

    source admin_env/bin/activate

3. Now, you can install your environment. Staying in your home directory, type::

    mpenv aj_vasp

  .. note:: Replace ``aj_vasp`` with whatever environment name you requested, e.g. ``wc_surfaces``. There is a ``--pymatpro`` option if you need to install pymatpro (people working with meta db builders might need this). If you get an error regarding PyCIFRW, try ``--alternate_pycifrw``.

4. A whole bunch of stuff will happen...just wait for it. Hopefully it will succeed at the end and create a new directory with your environment name. Again, you should use ``--alternate_pycifrw`` if you got an error on the pycifrw installation step.

5. Type::

   source ~/.bashrc.ext

  (or log out and log into NERSC again)

6. Activate your environment by typing::

   use_<ENV_NAME>

  e.g., ``use_aj_vasp``.

7. Reset your databases by typing::

    go_testing --clear -n 'reset'

If all this goes OK, your environment should be installed!

Part 3 - Customize your environment
-----------------------------------

There are many things about your environment that you can (and might have to) customize. Here are a few.

1. Go to ``<ENV_NAME>/config/config_Hopper`` where <ENV_NAME> is something like ``aj_vasp``. Modify ``my_qadapter.yaml`` so that queue scripts are submitted to the queue you want with the walltime, mppwidth, and account you want. You might want to change the queue to "debug" for example in order to test your environment. If you are not a member of the ``jcesr`` NERSC repository, either delete the ``account`` field or change to an account that you can charge at NERSC.  Do the same thing for ``config_Mendel``. (Note: Carver is not currently supported) If you are using Hopper to run VASP, you *must* change the mppwidth to 48.

2. In your ``.bashrc.ext``, you'll want to add two lines::

    export VASP_PSP_DIR=<PATH_TO_POTCARS>
    export MAPI_KEY=<MAPI_KEY>

   where <PATH_TO_POTCARS> contains your POTCARs dir and MAPI_KEY is your Materials Project API key. See the pymatgen docs for more details. Some features of the code (e.g. VASP input generation) won't work without these. Note that members of the ``matgen`` group at NERSC should be able to set their <PATH_TO_POTCARS> as ``/project/projectdirs/matgen/POTCARs``.

3. If you modify your ``bashrc.ext``, remember the changes are not applied unless you type ``source ~/.bashrc.ext``.

Part 4 - Modifying code to add workflows
----------------------------------------

1. The codes installed with your environment are in ``<ENV_NAME>/codes``. If you modify these codes (e.g. change a workflow in MPWork's ``snl_to_wf()`` method) they will modify the behavior of your environment.

2. Use ``git pull`` within each codebase to update that code to the latest version.

3. Use the ``update_codes`` command to pull the latest changes from all codes. **Be careful!** If there is a merge conflict or other problem, the script won't tell you; you need to monitor the output to make sure the pull completed OK.

Updating your environment itself
================================

From time to time MPenv will have new features and you will want to update your environment. You can do so without deleting any data you might have accumulated in your database (contact an admin if you want your DBs reset). However you should know that:

* this will delete any code updates you made to your environment unless they are backed up on git
* this will delete any configuration updates you made to your environment (e.g., ``my_qadapter.yaml``)

If you want to retain these changes, copy the files you need to another directory and copy them back after upgrading your environment.

When you're ready to begin:

1. Edit your ``.bashrc.ext`` file - look for the commented section referring to your environment name and delete that section. This will be rewritten when you reinstall the environment along with any new changes.

2. Delete the entire directory containing your environment. (e.g. ``aj_vasp``). *Make sure you do NOT delete your files directory, e.g. ``aj_vasp_files``. If you lose this directory contact an admin, they can fix it!*

3. Activate your admin environment::

    module load python/2.7.3
    module load virtualenv
    source admin_env/bin/activate

4. Pull admin environment changes::

    cd admin_env/MPenv
    git pull

5. Go back to your home directory and reinstall the virutalenv::

    cd ~
    mpenv aj_vasp
    source ~/.bashrc.ext

  .. note:: Replace ``aj_vasp`` with whatever environment name you requested, e.g. ``wc_surfaces``. Also, there is a ``--pymatpro`` option if you need to install pymatpro (people working with meta db builders might need this). If you get an error regarding PyCIFRW, try ``--alternate_pycifrw``.

6. Finally, remember to go back and make any configuration or code changes you need!

Deleting your environment
=========================

If you ever want to remove your environment completely (this is different than resetting DBs), you should:

#. Contact an administrator to tear down the DB backends

#. Remove the entire directory containing your environment AND your files (e.g. ``aj_vasp`` and ``aj_vasp_files``)

#. Edit your ``.bashrc.ext`` file - look for the commented section referring to your environment name and delete that section.

Administrator instructions
==========================

#. To create an environment, start in a directory that has your "private" directory containing the admin DB credentials.

#. Type ``mpdbmake <ENV_NAME> <TYPE>`` where <ENV_NAME> is the name the user requested and <TYPE> is either ``FW`` or ``MP`` or ``rubicon``.

#. Archive the resulting DB files somewhere

#. Send the DB files to the user.
