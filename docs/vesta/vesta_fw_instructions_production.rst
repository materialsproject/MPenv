===========================================
 Getting started on Vesta with Fireworks
===========================================

Verbose Introduction
====================

Basics
------

In 90% of cases, the Cobalt scheduler takes a job submission in which a user specifies a particular node count, the number of tasks per node, and the binary to run. Cobalt then schedules a partition, boots it, and runs the binary across all of the nodes in that partition, polling the Blue Gene control system to ensure success.

Cobalt is configured for partitions at least 32 nodes in size on Vesta, 128 nodes in size on Cetus, and 512 in size on Mira. Partitions scale up in size based on torus and I/O wiring rules to describe a system's full node count and network topology. If we have multiple runs larger than the smallest available partition, we can request a larger partition and divide the partition into multiple blocks each with its own runs from the same user. Generally, our users running in this "ensemble" mode are running across blocks that are at least the size of the smallest schedulable partition. Users must manage these blocks themselves -- booting blocks, tracking block state, scheduling where runs of a given binary and parameter set are all the user's responsibility. [#f1]_ It is a bit of a pain and can be wasteful for very small jobs as the tools provided by most sites only address the partitions the site deem schedulable.

You can go one step further and run multiple binaries with differing parameter sets on nodes within a block as subblock jobs. All management and the calculation of where the job should be within the block in terms of corner and geometry is entirely your responsibility. If a node goes bad or a job crashes, you need to manage the cleanup - while waiting for existing jobs to exit or making arrangements to re-run them. This is no fun when you have a large number of jobs.

To address the issues with subblock jobs, we run a special version of Cobalt within Cobalt which tracks subblock jobs and then run Fireworks jobs against it. 

User instructions
=================

Things to remember immediately
------------------------------

1. The Blue Gene is a cross compiling environment. Even though the front and backend systems are both PowerPC 64, they're running very different operating systems and vectorized code (including NumPy) will die with SIGILL if the wrong binary is run in the wrong environment. Most of what we're building is for the frontend to drive particular workflows that run computational jobs on the backend.

2. There is no way to log into the compute nodes. The compute node OS isn't just single user, it's also single process, lacking things like exec(). You'll have to count on stderr / stdout / Cobalt to tell you what's going on.

3. The Blue Gene community uses the words block and partition, as well as job and run in a way that sounds interchangable. They mostly are.

4. Nothing you do in your partition can crash jobs running on another partition - except really bad I/O. The worst thing that happens if you fork bomb a compute node is the control system waits for running jobs on your block to end and shuts down the block. Every run arranged through the parent Cobalt gets a fresh block.

4. I/O nodes are another matter - /tmp is automatically swept after every run, but anything an application writes there is stealing memory from the application's ability to do I/O during that run. If an I/O node does down, it will take all runs with it.

External documentation
----------------------

- `Vesta Status`
.. _Vesta Status: http://status.alcf.anl.gov/vesta/activity
- `PARTS Wiki - distilled developer instructions`
.. _PARTS Wiki - distilled developer instructions: https://wiki.alcf.anl.gov/parts/index.php/Blue_Gene/Q
- `IBM BG/Q Application Developers Manual`
.. _IBM BG/Q Application Developers Manual: http://www.redbooks.ibm.com/redpieces/abstracts/sg247948.html


Where to find things
--------------------

Almost everything is provided by adding +JCESR to your ~/.soft file. If hardcoded paths are needed, they are at:

- VASP 5.33 /projects/JCESR/bin
- QChem  /projects/JCESR/bin
- Python 2.7.10 /projects/JCESR/python/2.7.10/powerpc64-linux-gnu/gcc-4.4.7/bin


Getting started
---------------

1. Logging into Vesta, you'll first immediately want to edit your .soft file to set a mpi and compiler. [#f2]_ Typically, William's softenv file looks like::

    [wscullin@vestalac2 build]$ cat ~/.soft
    #
    # This is your SoftEnv configuration run control file.
    #
    #   It is used to tell SoftEnv how to customize your environment by
    #   setting up variables such as PATH and MANPATH.  To learn more
    #   about this file, do a "man softenv".
    
    +mpiwrapper-gcc.legacy
    +JCSER
    +git
    +cmake
    @default
    
    # EOF END OF FILE
    
2. Run a quick test to ensure basic functionality::

    qsub --mode script -t 10 -n 128 -q Q.JCESR -A JCESR ${WORKDIR}/bin/subblock_cobalt_launcher.sh

  you should get a job ID back with three files, an .output, .error, and .cobaltlog. The .output line should contain the line::

    COBALT_CONFIG_FILES=${path to the subblock-cobalt config file for that session}
    
  when you issue::
    
    export COBALT_CONFIG_FILES=${path to the subblock-cobalt config file for that session}

  then all commands like ``qstat`` and ``qsub`` will use the subblock-cobalt and not the system cobalt. Typing::

    unset COBALT_CONFIG_FILES
    
  will return your environment to normal. 
  
3. At this point, we should be able to move forward in a mostly generic fashion, but we'll need to adjust the scripts to use system packages. If pip tries to install PyYAML, NumPy, or SciPy, everything will fail::
    
    virtualenv --system-site-packages admin_env
    source admin_env/bin/activate
    cd admin_env
    git clone git@github.com:materialsproject/MPenv.git
    cd MPenv
    perl -p -i -e 's/virtualenv --no-site-packages/virtualenv --system-site-packages/g' MPenv/mpenv.py
    python setup.py develop

4. As the install progresses, almost everything should install automatially. In general, if a component gets hung up on install, one needs to track down a line with ``--no-site-packages`` and replace it with ``--system-site-packages`` to force the use of the site version we installed.
    
  to use the version of Fireworks with Cobalt support baked in.
    
5. At this point individual scripts and paths may require modification, but it should be possible to use consituent parts together to get something done. Just adjust the ``qsub`` in line 8 to fit the wallclock needed for your runs and remember to set ``COBALT_CONFIG_FILES`` to the run for the parent Cobalt. William is looking at adding convienience functions in the shell to make going back and forth between the parent environment and subblock-cobalt environment easier based on feedback from early users. Other feedback is greatly welcomed.



Building everything from bare metal
-----------------------------------

1. This is done for you in softenv by adding +JCESR. The system Python on Vesta is dated, so we have a few things to build on our own. We'll start with a wide-char enabled Python and pip::

    ## Build python with wide character support and install pip.
    export DC=$(date +%Y%m%d%H%M)
    export WORKDIR=/gpfs/vesta-fs0/projects/JCESR/${USER}/${DC}
    mkdir -p ${WORKDIR}
    
    # we first need a Python with full unicode support, the system interpreter will cause issues with many of the MP tools
    mkdir -p /dev/shm/${USER}
    pushd /dev/shm/${USER}
    wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
    tar -xvf Python-2.7.10.tgz
    mkdir buildPython-2.7.10
    pushd buildPython-2.7.10
    export LDFLAGS=-Wl,-rpath=${WORKDIR}/lib:${WORKDIR}/lib64:\\\$\$LIB,--enable-new-dtags
    ../Python-2.7.10/configure --enable-unicode=ucs4 --disable-ipv6 --prefix=${WORKDIR}
    make
    make install
    popd
    export LD_LIBRARY_PATH=${WORKDIR}/lib:${LD_LIBRARY_PATH}
    export PATH=${WORKDIR}/bin:${PATH}
    wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
    python get-pip.py
    
2. This is done for you in softenv by adding +JCESR. PyYAML, despite a lot of prodding isn't accepting patches, including an important one that uses size_t rather than int on 64-bit platforms::
    
    # PyYAML has issues with 64-bit endianness we need to fix
    wget http://pyyaml.org/download/pyyaml/PyYAML-3.11.tar.gz
    tar -zxvf PyYAML-3.11.tar.gz
    pushd PyYAML-3.11
    wget -O size_t.patch https://bitbucket.org/xi/pyyaml/issue-attachment/35/xi/pyyaml/1410527863.03/35/debian-patch.patch
    patch -p1 <  size_t.patch
    python setup.py --without-libyaml build
    python setup.py --without-libyaml test
    python setup.py --without-libyaml install
    popd
    
3. This is done for you in softenv by adding +JCESR. NumPy and SciPy fail a number of regression tests using the system LAPACK, BLAS, and FFTW, so we build them too, then run the NumPy regression tests. One test will fail which we're fine with as it's a unicode problem and there's a ticket open::
    
    wget http://www.netlib.org/lapack/lapack-3.5.0.tgz
    gunzip lapack-3.5.0.tgz
    tar -xvf lapack-3.5.0.tar
    pushd lapack-3.5.0
    cp INSTALL/make.inc.gfortran make.inc
    perl -p -i -e 's/-O[123]/-O0/g' make.inc
    cmake -DCMAKE_INSTALL_PREFIX=${WORKDIR} -DBUILD_SHARED_LIBS:BOOL=ON \
    -DCMAKE_SHARED_LINKER_FLAGS=$LDFLAGS -DCMAKE_Fortran_COMPILER=gfortran \
    -DCMAKE_INSTALL_RPATH:STRING="${WORKDIR}/lib" -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE
    make all && make test
    cp lib/* ${WORKDIR}/lib
    popd
    
    wget http://fftw.org/fftw-3.3.4.tar.gz
    tar -xvf fftw-3.3.4.tar.gz
    cd fftw-3.3.4
    CC=gcc FC=gfortran F77=gfortran ./configure --prefix=${WORKDIR} --enable-openmp --enable-fma
    make
    make check
    make install
    
    pip install nose
    pip install numpy
    

  Remember to run the numpy regression tests::

    python -c "import numpy; import numpy.testing; numpy.testing.test()"
    Running unit tests for numpy.testing
    NumPy version 1.9.1
    NumPy is installed in /projects/JCESR/wscullin/201502040618/lib/python2.7/site-packages/numpy
    Python version 2.7.10 (default, Feb  4 2015, 06:19:57) [GCC 4.4.7 20120313 (Red Hat 4.4.7-4)]
    nose version 1.3.4
    .....................................K.............................................
    ----------------------------------------------------------------------
    Ran 83 tests in 0.211s
    
    OK (KNOWNFAIL=1)
    
    pip install scipy

4. This is done for you in softenv by adding +JCESR. This is done for you in softenv by adding +JCESR. Now on to the bits we'll need to run Subblock-Cobalt within fireworks::

    pip install virtualenv
    pip install jinja2    

    pip install git+https://github.com/wscullin/subblock-cobalt
    

.. [#f1] http://www.alcf.anl.gov/files/ensemble_jobs_0.pdf
.. [#f2] http://www.alcf.anl.gov/user-guides/overview-how-compile-and-link
