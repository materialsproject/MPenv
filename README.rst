=====
MPenv
=====

This codebase helps users create a virtual environment for running FireWorks within Materials Project in a semi-automated way.


User instructions
=================

Warnings
--------

1. If you are planning on running VASP or any other commercial code, make sure you have communicated your license to NERSC and have access to running it. The MPEnv will not give you access to any codes for which you are not a licensed user.

2. This only works on NERSC

3. This only works if your NERSC shell is BASH, not CSH. Note that by default NERSC often sets CSH. **Seriously, BASH needs to be your DEFAULT shell. You cannot just start bash within CSH or virtualenv fails at NERSC.** To change your default shell, login to nim.nersc.gov, go to 'Logins by host', then 'change login shell', then change your shells.

4. After creating your environment, you can't move or rename it. If you need to delete it see the instructions below.

Part 1 - Install the MPenv code at NERSC and request an environment
-------------------------------------------------------------------

1. Log into Carver. In theory, Hopper and Edison should also work, but recent changes at NERSC might have changed this.

2. Type::

    module load python/2.7.3
    module swap numpy numpy/1.8.1
    module load virtualenv/1.8.2
    module load virtualenvwrapper
    mkdir admin_env
    virtualenv --no-site-packages admin_env
    source admin_env/bin/activate
    cd admin_env
    git clone git@github.com:materialsproject/MPenv.git
    cd MPenv
    python setup.py develop


  .. note:: If the virtualenv command fails, make sure you have set your *default* shell to be BASH and not CSH.
  .. note:: If the ``git clone`` command fails, make sure your SSH key for the NERSC machine is registered under your GitHub username. This is done by typing ``ssh-keygen -t dsa`` (hit enter at all prompts) and then copying your ``~/.ssh/id_dsa.pub`` file to your Github account (log into github.com, click account settings at top-right, then the 'SSH keys' section). ``git clone`` might also fail if you're using non-default ssh-key names configured in ``~/.ssh/config``. Please make sure to start the ssh-agent and add your private key in this case: ``eval `ssh-agent -s` && ssh-add <path-to-private-key>``

3. Type::

    which mpenv

   If the installation was successful, the system should find an executable.

4. Request an environment from an administrator (currently Patrick Huck; backup Anubhav Jain). The current procedure is just to send an email with a requested environment name, e.g. "aj_vasp". A good environment name should look like "A_B" where "A" is your initials and "B" is some SHORT description that will help you remember what the environment is for. another example: "wc_surfaces".

5. An administrator will create a suite of databases hosted at NERSC for you and send you back a directory, lets call this "aj_vasp_files". *Do not rename or change this directory in any way*.

6. Once you receive the directory, move to the next part.

Part 2 - Install at NERSC
-------------------------

1. Upload the entire files directory you received from an admin (e.g., *aj_vasp_files*) to your home directory at NERSC. Remember to not change this directory!

2. Log onto Hopper and enter the admin environment that allows you to use MPenv::

    module load python/2.7.3
    module swap numpy numpy/1.8.1
    module load virtualenv/1.8.2
    module load virtualenvwrapper
    source admin_env/bin/activate

3. Now, you can install your environment. Staying in your home directory, type::

    mpenv aj_vasp

  .. note:: Replace ``aj_vasp`` with whatever environment name you requested, e.g. ``wc_surfaces``. There is a ``--pymatpro`` option if you need to install pymatpro (people working with meta db builders might need this). See note in part 1 if ``git clone`` fails here. The ``rubicon`` clone might still fail and claim a not-existing repo if you don't have the correct permissions. Contact an administrator to be granted access.
  
  .. note:: The "aj_vasp" must currently be a *directory*. If you received a .tar.gz file, you should unzip and untar it first

4. A whole bunch of stuff will happen...just wait for it. Hopefully it will succeed at the end and create a new directory with your environment name.

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

.. note:: Currently this only seems to work on Hopper due to strange NERSC updates messing with SSL certs.

1. The codes installed with your environment are in ``<ENV_NAME>/codes``. If you modify these codes (e.g. change a workflow in MPWork's ``snl_to_wf()`` method) they will modify the behavior of your environment.

2. Use ``git pull`` within each codebase to update that code to the latest version.

3. Use the ``update_codes`` command to pull the latest changes from all codes. **Be careful!** If there is a merge conflict or other problem, the script won't tell you; you need to monitor the output to make sure the pull completed OK.

Getting started with MPenv
==========================

  .. note:: This applies to Materials Project environments and to a certain extent, rubicon environments.

Part 1 - The basics
-------------------

There are 4(!) main databases that interact within MPenv. You have credentials for these 4 databases in the MPenv files sent to you by the MPenv admin. As a first step, you might set up a connection to these database via MongoHub (or similar) so you can easily check the contents of these databases. If you do not have a Mac, you cannot use Mongohub to check database contents, but you can either (i) skip monitoring databases directly and just use the tools built into FireWorks and other packages or (ii) use another program or just the MongoDB command line tools. You can read "The Little MongoDB book" (available for free online) to see how to use the MongoDB command line as one alternative. Mongohub is **not** by any means a requirement.

1. The most important database is the **FireWorks** database. This contains all the workflows that you want to run.

2. The 2nd most important database is the **VASP** database. This contains the results of your calculations

3. There is also a **submissions** database where you can submit Structure objects (actually SNL objects) for computation. Using this database is optional but (as demonstrated later) can be simpler than trying to create FireWorks directly.

4. Finally, there is an **SNL** database that contains all the structures you've submitted and relaxed. It is used for duplicate checking as well as record-keeping. Generally speaking, you do not need to do worry that this database exists.

One type of MPenv procedure is to submit Structures to the **submissions** database, then use an *automated* command to convert those submissions into **FireWorks** workflows and run them. The results are checked via the **VASP** database. The order of operations is  **submissions** -> **FireWorks** --> **VASP**, but your interaction is only with **submissions** and **VASP** databases.

Another type of MPenv procedure is to dispense with submissions database and instead submit workflows directly to the **FireWorks** database. In this case, your interaction is with **FireWorks** and **VASP** databases.

Part 2 - Running test workflows
-------------------------------

You can run test workflows by the following procedure. This test follows the **submissions** -> **FireWorks** --> **VASP** paradigm.

1. Log into a NERSC machine

2. Activate your environment::

    use_<ENV_NAME>

3. Note: the following command clears all your databases. Type the command::

    go_testing --clear

4. The command above clears all your databases AND submits ~40 test compounds to your **submissions** database. If you want, you can at this point try connecting to your **submissions** database (e.g. via MongoHub) and confirm that you see compounds there.

5. Items in the **submissions** database cannot be run directly. They must first be converted into FireWorks that state the actual calculations we want to perform. Type the command::

    go_submissions

6. You will see output saying that you have new workflows. This command *automatically* turned the new submissions into workflows in the **FireWorks** database that can can be run at NERSC. If you want, you can at this point try connecting to your **FireWorks** database (e.g. via MongoHub) and confirm that you see Workflows there. Or you can type ``lpad get_wflows -d less`` as another option to see what's in the FireWorks database.

7. Let's run our FireWorks by navigating to a scratch directory and using the ``qlaunch`` command of FireWorks::

    cd $GSCRATCH2
    mkdir first_tests
    cd first_tests
    qlaunch -r rapidfire --nlaunches infinite -m 50 --sleep 100 -b 10000

8. This should have submitted some jobs to the queues at NERSC. You should keep the qlaunch command running (or run it periodically) so that as workflow steps complete, new jobs can be submitted.

9. You can check progress of your workflows using the built-in FireWorks monitoring tools. Several such tools, including a web gui, are documented in the FW docs. If you want to be efficient, you will actually look this up (as well as how to rerun jobs, detect failures, etc.). Here is a simple command you can use for basic checking::

    lpad get_wflows -d more

10. When your workflows complete, you should see the results in the **VASP** database (e.g. connect via MongoHub or via pymatgen-db frontend).

Part 3 - Running custom structures
----------------------------------

You can run custom structures through the typical MP workflow very easily. You need to submit your Structures (as StructureNL objects) to your **submissions** database. Then simply use the same procedure as last time to convert those into FireWorks and run them (we are still following the **submissions** -> **FireWorks** --> **VASP** paradigm).

1. If you want, you can clear all your databases via::

    go_testing --clear -n 'no_submissions'

2. Here is some code you can use to submit a custom Structure to the **submissions** database (you will need to copy your ``<ENV_NAME>/configs/db/submission_db.yaml`` file to the location you run this code, and also have set up your MPRester API key if you want to grab a structure from Materials Project as in this example)::

    from mpworks.submission.submission_mongo import SubmissionMongoAdapter
    from pymatgen import MPRester
    from pymatgen.matproj.snl import StructureNL

    submissions_file = 'submission_db.yaml'
    sma = SubmissionMongoAdapter.from_file(submissions_file)

    # get a Structure object
    mpr = MPRester()
    s = mpr.get_structure_by_material_id("mp-149")  # this is Silicon

    # At this point, you could modify the structure if you want.

    # create an SNL object and submit to your submissions database
    snl = StructureNL(s, 'John Doe <my_email@gmail.com>')
    sma.submit_snl(snl, 'my_email@gmail.com', parameters=None)

3. Once all your structures are submitted, follow steps 5-10 in the previous part to run it.

4. There are many advanced options for setting priority, basic WF tailoring, auto-setting the submission database based on environment, etc. Consult the email list if you need help with a specific problem.

Part 4 - Running custom workflows
---------------------------------

Part 3 was about running custom *structures* through a typical MP workflow. If you want to run custom workflows (new types of calculations not coded in MP), you have a couple of options. You can either learn a bit more about MPWorks and try to code your workflow so that it can be run as in Part 3, but submitted with certain parameters (e.g., ``sma.submit_snl(snl, 'my_email@gmail.com', parameters={"calculation_type":"CUSTOM_STUFF"})``). This requires modifying the code that turns StructureNL into Workflows. In this case you are still following the **submissions** -> **FireWorks** --> **VASP** paradigm. Some (long and a bit outdated) documentation on this is in the MPWorks code in the docs folder.

The alternate strategy is to create Workflow objects directly and put them in the **FireWorks** database, bypassing the submissions database entirely. Then you are just doing  **FireWorks** --> **VASP**. Once the Workflow objects are in the **FireWorks** database, you can run them by following steps 7-10 in Part 2 of this guide (i.e., basically you just need to run the ``qlaunch`` command.

One code in development to create basic workflows that can run VASP is the **fireworks-vasp** repository (https://github.com/materialsvirtuallab/fireworks-vasp). This code can create Workflow objects that you can directly enter into your FireWorks database (the credentials for your FW database is in the ``my_launchpad.yaml`` given to you by the MPenv admin). This is not the code used by Materials Project for running workflows (MPWorks does that), but is considerably simpler to understand and modify for your needs. You can probably get started with custom workflows much more quickly with this strategy.

Updating your environment itself
================================

From time to time MPenv will have new features and you will want to update your environment. This is different than updating the codes itself - it is updating the code that *installs* the high-throughput codes. You can update MPenv without deleting any data you might have accumulated in your database (contact an admin if you want your DBs reset). However you should know that:

* this will delete any code updates you made to your environment unless they are backed up on git
* this will delete any configuration updates you made to your environment (e.g., ``my_qadapter.yaml``)

If you want to retain these changes, copy the files you need to another directory and copy them back after upgrading your environment.

When you're ready to begin:

1. Edit your ``.bashrc.ext`` file - look for the commented section referring to your environment name and delete that section. This will be rewritten when you reinstall the environment along with any new changes.

2. Delete the entire directory containing your environment. (e.g. ``aj_vasp``). *Make sure you do NOT delete your files directory, e.g. ``aj_vasp_files``. If you lose this directory contact an admin, they can fix it!*

3. Activate your admin environment::

    module load python/2.7.3
    module swap numpy numpy/1.8.2
    module load virtualenv/1.8.2
    module load virtualenvwrapper
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

Creating an admin_env
---------------------

#. Start by creating the admin_env from the instructions listed for users. You might already have one installed if you've created an MPEnv in the past.

#. You will need a directory called admin_env/MP_env/MP_env/private that contains the DB credentials for making an environment. Obtain this from someone who is currently an admin.

#. Once you have the private dir in the correct spot, you have a working admin_env!

Managing an admin_env
---------------------

#. Activate your ``admin_env`` environment.

#. ``cd`` in your admin_env/MP_env directory, and then run ``git pull`` and (maybe) ``python setup.py develop``.

#. Start in a directory where you archive all the environments that you've made. For me, it is ``$HOME/envs``.

#. Type ``mpdbmake <ENV_NAME> <TYPE>`` where <ENV_NAME> is the name the user requested and <TYPE> is either ``FW`` or ``MP`` or ``rubicon``.

#. Usually, I tar.gz the resulting DB files and send them to the user by email. But other methods would also be OK. I keep a copy in my envs directory.
