=====
MPenv
=====

This codebase helps users create a virtual environment for running FireWorks
within Materials Project in a semi-automated way.


User instructions
=================

Warnings
--------

1. If you are planning on running VASP or any other commercial code, make sure
   you have communicated your license to NERSC and have access to running it.
   The MPEnv will not give you access to any codes for which you are not a
   licensed user.

2. This only works on NERSC

3. This only works if your NERSC shell is BASH, not CSH. Note that by default
   NERSC often sets CSH. **Seriously, BASH needs to be your DEFAULT shell. You
   cannot just start bash within CSH or virtualenv fails at NERSC.** To change
   your default shell, login to nim.nersc.gov, go to 'Logins by host', then
   'change login shell', then change your shells. Type `echo $SHELL` when
   logged in to confirm that your shell is BASH (e.g. `/bin/bash`).

4. After creating your environment, you can't move or rename it. If you need to
   delete it see the instructions below.
   
5. Unfortunately, differences between python versions on cori, edison, and matgen
   require you to install a separate environment for each machine.  However, you 
   can use the same database configuration files for multiple machines.  For example, you 
   might have wc_surfaces installed on matgen, and can then copy wc_surface_files to create
   a new environment, say wc_surface_cori_files to install the environment wc_surface_cori.

Part 1 - Install the MPenv code at NERSC and request an environment
-------------------------------------------------------------------

1. Log into Edison/Cori/Matgen. Note that the matgen nodes ("Mendel") are accessible 
   by logging into into ``matgen.nersc.gov`` to submit jobs to Mendel. If you cannot
   log into ``matgen.nersc.gov``, run ``id`` on another NERSC system (Cori, Edison)
   and check that you're in the ``matcomp`` group. If not, request to be added
   to the group by sending an e-mail to an administrator (Patrick Huck). Hopper
   has been retired as of January 2016.


   Also, add the following line to your ``~/.bashrc.ext`` to export the
   PIP_CERT environment variable to the path of the PEM file (see
   http://stackoverflow.com/a/28724886)::

    export PIP_CERT=/project/projectdirs/matgen/DigiCertHighAssuranceEVRootCA.pem

2. Load necessary modules::

    # Edison
    module load python/2.7.9
    module load numpy/1.9.2
    module load virtualenv
    module load virtualenvwrapper

    # Cori
    module load python
    module load numpy
    module load virtualenv

    # matgen
    module load vim
    module unload intel
    module load python/2.7.3
    module swap numpy numpy/1.9.2
    module swap scipy scipy/0.14.0
    module load virtualenv

  .. note::
    See bullet #4 in Part 4 for the role of the intel module when updating
    codes on matgen!

3. Create virtual environment and install MPenv code::

    mkdir admin_env
    virtualenv admin_env
    source admin_env/bin/activate
    cd admin_env
    eval `ssh-agent -s` && ssh-add <path-to-private-github-key>
    git clone git@github.com:materialsproject/MPenv.git
    cd MPenv
    python setup.py develop

  .. note::
   * If the virtualenv command fails, make sure you have set your *default*
     shell to be BASH and not CSH.
   * If the ``git clone`` command fails, make sure your SSH key for the NERSC
     machine is registered under your GitHub username. This is done by typing
     ``ssh-keygen -t dsa`` (hit enter at all prompts) and then copying your
     ``~/.ssh/id_dsa.pub`` file to your Github account (log into github.com,
     click account settings at top-right, then the 'SSH keys' section).

3. Type ``which mpenv``. If the installation was successful, the system should
   find an executable.

4. Request an environment from an administrator (currently Patrick Huck). The current procedure is just to send an email with a
   requested environment name, e.g. ``aj_vasp``. A good environment name should
   look like ``A_B`` where ``A`` is your initials and ``B`` is some SHORT
   description that will help you remember what the environment is for. another
   example: ``wc_surfaces``.

5. An administrator will create a suite of databases hosted at NERSC for you
   and send you back an archive (a.k.a tarball), let's call this
   ``aj_vasp_files.tar.gz``. *Do not rename or change this archive in any way*.

6. Once you receive the tarball, move to the next part.

Part 2 - Install MP codes at NERSC
----------------------------------

1. Upload the tarball you received from an admin (e.g.,
   ``aj_vasp_files.tar.gz``) via ``scp`` to your home directory at NERSC, log
   into Edison or matgen, and unpack it (i.e. ``tar -xvzf
   aj_vasp_files.tar.gz``). Remember to not change this archive or the
   resulting directory contents!

2. Load the necessary modules::

    # Edison
    module load python/2.7.9
    module load numpy/1.9.2
    module load virtualenv
    module load virtualenvwrapper

    # Cori
    module load python
    module load numpy
    module load virtualenv

    # matgen
    module load vim
    module unload intel
    module load python/2.7.3
    module swap numpy numpy/1.9.2
    module swap scipy scipy/0.14.0
    module load virtualenv

3. add GitHub ssh-key and activate the admin environment that allows you to use
   ``mpenv``::

    eval `ssh-agent -s` && ssh-add <path-to-private-github-key>
    source admin_env/bin/activate

4. Now, you can install your environment. Staying in your home directory, type::

    mpenv aj_vasp

  .. note::
   * Replace ``aj_vasp`` with whatever environment name you requested, e.g.
     ``wc_surfaces``.
   * There is a ``--pymatpro`` option if you need to install pymatpro (people
     working with meta db builders might need this).
   * See note in part 1 if ``git clone`` fails here.
   * The ``rubicon`` git clone might still fail and claim a not-existing repo
     if you don't have the correct permissions. Contact an administrator to be
     granted access.

5. A whole bunch of stuff will happen... just wait for it. Hopefully it will
   succeed at the end and create a new directory with your environment name.

6. Log out and in to NERSC again (or ``source ~/.bashrc.ext``).

7. Activate your environment by typing ``use_<ENV_NAME>``, e.g., ``use_aj_vasp``.

8. If you don't need the data within them, reset your databases 
   by typing ``go_testing --clear -n 'reset'``.

If all this goes OK, your environment should be installed!

Part 3 - Customize your environment
-----------------------------------

There are many things about your environment that you can (and might have to)
customize. Here are a few.

1. Go to ``<ENV_NAME>/config/config_<MACHINE>`` where ``<ENV_NAME>`` is
   something like ``aj_vasp`` and ``<MACHINE>`` is either ``Mendel``,
   ``Hopper``, or ``Edison``. Modify ``my_qadapter.yaml`` so that queue scripts
   are submitted to the queue you want with the walltime, mppwidth, and account
   you want. You might want to change the queue to "debug" for example in order
   to test your environment. If the ``account`` field says ``jcesr`` but you
   are not a member of the ``jcesr`` NERSC repository, either delete the
   ``account`` field or change to an account that you can charge at NERSC. If
   you are using Hopper to run VASP, you *must* change the mppwidth to 48.
   Repeat for all machines that you're using.

2. Since ``Mendel`` is using SLURM, you'll also need to add the following to
   ``my_fworker.yaml`` to run VASP on multiple nodes in parallel::

    env:
        mpi_cmd: srun

3. In your ``.bashrc.ext``, you'll want to add two lines (if not already done
   by ``mpenv``)::

    export VASP_PSP_DIR=<PATH_TO_POTCARS>
    export MAPI_KEY=<MAPI_KEY>

   where <PATH_TO_POTCARS> contains your POTCARs dir and MAPI_KEY is your
   Materials Project API key. See the pymatgen docs for more details. Some
   features of the code (e.g. VASP input generation) won't work without these.
   Note that members of the ``matgen`` group at NERSC should be able to set
   their <PATH_TO_POTCARS> as ``/project/projectdirs/matgen/POTCARs``.

4. If you modify your ``bashrc.ext``, remember the changes are not applied
   unless you type ``source ~/.bashrc.ext``.

Part 4 - Modifying or updating your codebases
---------------------------------------------

.. note::
  Currently this only seems to work on Hopper due to strange NERSC updates
  messing with SSL certs.

1. The codes installed with your environment are in ``<ENV_NAME>/codes``. If
   you modify these codes (e.g. change a workflow in MPWork's ``snl_to_wf()``
   method) they will modify the behavior of your environment.

2. Use the ``update_codes`` command to pull the latest changes from **all**
   codes. **Be careful!** If there is a merge conflict or other problem, the
   script won't tell you; you need to monitor the output to make sure the pull
   completed OK.

3. You can also ``git pull`` individually within the repos inside
   ``<ENV_NAMES>/codes``. If the version number changed, then you also need to
   run ``python setup.py develop``.

4. On matgen, you need to *unload* the intel module when trying to build and/or
   install python code! However, make sure to load the intel module again
   before running VASP jobs! Alternatively, you can log out and into NERSC
   again or ``source ~/.bashrc.ext``.

Running Jobs
============

After getting your environment installed, you might want to run some test jobs.
See the `MPWorks page <https://github.com/materialsproject/MPWorks>`_ for more
details on how to do so.

Updating your admin environment
===============================

From time to time MPenv will have new features and you will want to update your
admin environment. This is different than updating the codes itself - it is
updating the code that *installs* the high-throughput codes. You can update
MPenv without deleting any data you might have accumulated in your database
(contact an admin if you want your DBs reset). However you should know that
this will delete any configuration updates you made to your environment (e.g.,
``my_qadapter.yaml``). If you want to retain these changes, copy the files you
need to another directory and copy/merge them back after upgrading your admin
environment.

When you're ready to begin (logged into NERSC):

1. Edit your ``.bashrc.ext`` file - look for the commented section referring to
   your environment name and delete that section. This will be rewritten when
   you reinstall the environment along with any new changes. ``mpenv`` will
   abort if you forget to do this and if the respective section already exists
   in ``.bashrc.ext``.

2. Log out and in again to ensure a clean BASH environment.

3. Load necessary modules::

    # Edison
    module load python/2.7.9
    module load numpy/1.9.2
    module load virtualenv
    module load virtualenvwrapper

    # Cori
    module load python
    module load numpy
    module load virtualenv

    # matgen
    module load vim
    module unload intel
    module load python/2.7.3
    module swap numpy numpy/1.9.2
    module swap scipy scipy/0.14.0
    module load virtualenv

4. Add your GitHub sshkey and activate your admin environment::

    eval `ssh-agent -s` && ssh-add <path-to-private-github-key>
    source admin_env/bin/activate

5. Pull admin environment changes::

    cd admin_env/MPenv
    git pull

6. Go back to your home directory and reinstall::

    cd ~
    mpenv aj_vasp

  .. note:: Replace ``aj_vasp`` with whatever environment name you requested,
  e.g. ``wc_surfaces``. Also, there is a ``--pymatpro`` option if you need to
  install pymatpro (people working with meta db builders might need this).

8. Log out and in to NERSC again, or ``source ~/.bashrc.ext``.

9. Finally, remember to go back and make any configuration or code changes you need!

Deleting your environment
=========================

If you ever want to remove your environment completely (this is different than
resetting DBs), you should:

#. Contact an administrator to tear down the DB backends

#. Remove the entire directory containing your environment AND your files (e.g.
   ``aj_vasp`` and ``aj_vasp_files``)

#. Edit your ``.bashrc.ext`` file - look for the commented section referring to
   your environment name and delete that section.

Administrator instructions
==========================

Creating an admin_env
---------------------

#. Start by creating the admin_env from the instructions listed for users. You
   might already have one installed if you've created an MPEnv in the past.

#. You will need a directory called admin_env/MP_env/MP_env/private that
   contains the DB credentials for making an environment. Obtain this from
   someone who is currently an admin.

#. Once you have the private dir in the correct spot, you have a working
   admin_env!

Managing an admin_env
---------------------

#. Activate your ``admin_env`` environment.

#. ``cd`` in your admin_env/MP_env directory, and then run ``git pull`` and
   (maybe) ``python setup.py develop``.

#. Start in a directory where you archive all the environments that you've
   made. For me, it is ``$HOME/envs``.

#. Type ``mpdbmake <ENV_NAME> <TYPE>`` where <ENV_NAME> is the name the user
   requested and <TYPE> is either ``FW`` or ``MP`` or ``rubicon``.

#. Usually, I tar.gz the resulting DB files and send them to the user by email.
   But other methods would also be OK. I keep a copy in my envs directory.
