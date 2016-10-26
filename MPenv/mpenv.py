

from argparse import ArgumentParser
import os, re
from os.path import expanduser
import shutil
import string
import subprocess
import traceback
from urllib3.util.ssl_ import HAS_SNI

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Aug 20, 2013'

CONFIG_TAG = "_files"

def create_env():
    m_description = 'This program creates a self-contained environment for running ' \
                    'and testing FireWorks workflows at NERSC'
    parser = ArgumentParser(description=m_description)

    parser.add_argument('name', help='directory containing environment files', default=None)
    parser.add_argument('--pymatpro', help='install pymatpro', action='store_true')

    root_dir = os.getcwd()
    args = parser.parse_args()
    env_exists = os.path.exists(args.name)
    virtenv_dir = os.path.join(root_dir, args.name, "virtenv_{}".format(args.name))
    virtenv_exists = os.path.exists(virtenv_dir)

    if env_exists:
        print 'OK, environment directory {} exists.'.format(args.name)
        print '  => Will overwrite config files and clone missing code repositories.'
        print '  => FYI: Remove {} directory to start from scratch'.format(args.name)
        if virtenv_exists:
            print 'OK, virtenv directory for {} exists.'.format(args.name)
            print '  => Will NOT install codes (i.e. run `pip install -e .` in code repos).'
            print '  => FYI: remove {} to reinstall codes'.format(virtenv_dir)
        else:
            print 'OK, virtenv directory for {} does not exist.'.format(args.name)
            print '  => Will install codes (i.e. run `pip install -e .` in all code repos).'
    else:
      print 'OK, will install brand-new {} environment'.format(args.name)

    BASHRC_FILE = os.path.join(expanduser("~"), ".bashrc.ext")
    with open(BASHRC_FILE, 'r') as f:
        if re.search(r'<---MPenv {}'.format(args.name), f.read()):
            print 'ERROR: make sure to remove {} section from {}!'.format(args.name, BASHRC_FILE)
            return

    cont = raw_input("Continue? (y/N) ").lower() == 'y'
    if not cont: return

    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(module_dir, 'mpenv_static')
    files_dir = os.path.join(root_dir, args.name+CONFIG_TAG)
    codes_dir = os.path.join(root_dir, args.name, 'codes')

    MACHINES = ('Mendel', 'Vesta', 'Edison', 'Cori')  # note: you must modify BASH_template.txt when adding machines

    print 'VALIDATING DIRECTORY'
    envtype = "FW"
    if not os.path.exists(files_dir):
        print "ERROR: Files directory {} does not exist! Please make sure you are typing the ENVIRONMENT name and not the directory name.".format(files_dir)
        return

    if not os.path.exists(os.path.join(files_dir, 'my_launchpad.yaml')):
        print "ERROR: Missing file: {}".format(files_dir, 'my_launchpad.yaml')
        return

    if os.path.exists(os.path.join(files_dir, 'tasks_db.json')):
        envtype = "MP"

    if os.path.exists(os.path.join(files_dir, 'molecules_db.json')):
        envtype = "rubicon"

    print 'OK, we are going to install a {} environment'.format(envtype)

    c = []
    c.append(("mkdir", args.name))
    c.append(("cd", args.name))

    if not virtenv_exists:
        c.append(('print', 'SETTING UP VIRTUALENV'))
        c.append(("mkdir", "virtenv_{}".format(args.name)))
        c.append("virtualenv --no-site-packages virtenv_{}".format(args.name))

    c.append(('print', 'ACTIVATE VIRTUALENV'))
    c.append(("activate", os.path.join(root_dir, args.name, 'virtenv_{}/bin/activate_this.py'.format(args.name))))
    c.append(("mkdir", "codes"))
    c.append(("cd", 'codes'))

    if not os.path.exists(os.path.join(codes_dir, 'fireworks')):
        c.append(('print', 'CLONING FireWorks'))
        c.append("git clone git@github.com:materialsproject/fireworks.git")

    if not virtenv_exists:
        c.append(('print', 'INSTALLING FireWorks (developer mode)'))
        c.append(("cd", 'fireworks'))
        c.append("pip install -e .")
        c.append(("cd", '..'))

    if envtype == "MP" or envtype == "rubicon":

      if not os.path.exists(os.path.join(codes_dir, 'pymatgen')):
        c.append(('print', 'CLONING pymatgen'))
        c.append("git clone git@github.com:materialsproject/pymatgen.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING pymatgen (developer mode)'))
          c.append("pip install spglib")
          c.append("pip install pyhull")
          c.append("pip install pyyaml")
          c.append("pip install pybtex")
          c.append("pip install smoqe")  # for pymatgen-db
          c.append("pip install mongomock")  # for pymatgen-db
          c.append("pip install django")  # for pymatgen-db
          c.append(("cd", 'pymatgen'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

        if not os.path.exists(os.path.join(codes_dir, 'pymatgen-db')):
          c.append(('print', 'CLONING pymatgen-db'))
          c.append("git clone git@github.com:materialsproject/pymatgen-db.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING pymatgen-db (developer mode)'))
          c.append(("cd", 'pymatgen-db'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

        if not os.path.exists(os.path.join(codes_dir, 'custodian')):
          c.append(('print', 'CLONING custodian'))
          c.append("git clone git@github.com:materialsproject/custodian.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING custodian (developer mode)'))
          c.append(("cd", 'custodian'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

        if not os.path.exists(os.path.join(codes_dir, 'MPWorks')):
          c.append(('print', 'CLONING MPWorks'))
          c.append("git clone git@github.com:materialsproject/MPWorks.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING MPWorks (developer mode)'))
          c.append(("cd", 'MPWorks'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

    if args.pymatpro:

        if not os.path.exists(os.path.join(codes_dir, 'pymatpro')):
          c.append(('print', 'CLONING pymatpro'))
          c.append("git clone git@github.com:materialsproject/pymatpro.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING pymatpro (developer mode)'))
          c.append(("cd", 'pymatpro'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

    if envtype == "rubicon":

        if not os.path.exists(os.path.join(codes_dir, 'rubicon')):
          c.append(('print', 'CLONING rubicon'))
          c.append("git clone git@github.com:materialsproject/rubicon.git")

        if not virtenv_exists:
          c.append(('print', 'INSTALLING rubicon (developer mode)'))
          c.append("pip install simplerandom")
          c.append(("cd", 'rubicon'))
          c.append("pip install -e .")
          c.append(("cd", '..'))

    c.append(('print', 'ADDING SETTINGS'))
    c.append(("cd", os.path.join(root_dir, args.name)))
    c.append(("mkdir", "config"))
    c.append(("cd", "config"))
    for machine in MACHINES:
        c.append(("mkdir", "config_{}".format(machine)))
    c.append(("mkdir", "dbs"))
    c.append(("mkdir", "logs"))
    c.append(("mkdir", "scripts"))
    c.append(("cp_script", "update_codes.py"))

    if envtype == "MP" or envtype == "rubicon":
        c.append(('print', 'MAKING / MOVING DB files'))
        c.append(("cp", "snl_db.yaml"))
        c.append(("cp", "submission_db.yaml"))
        c.append(("cp", "tasks_db.json"))

    if envtype == "rubicon":
        c.append(("cp", "molecules_db.json"))

    c.append(('print', 'UPDATING ENVIRONMENT'))
    c.append(("append", ))
    c.append(('print', 'MPenv is done!'))

    try:
        for command in c:
            if isinstance(command, str):
	        if not HAS_SNI and 'pip install' in command:
		    easy_command = 'easy_install ' + command.split(' ')[-1]
		    subprocess.check_call(easy_command, shell=True, executable="/bin/bash")
		else:
		    subprocess.check_call(command, shell=True, executable="/bin/bash")

            elif command[0] == 'mkdir':
                if not os.path.exists(command[1]):
                    os.mkdir(command[1])
            elif command[0] == 'cd':
                os.chdir(command[1])
            elif command[0] == 'activate':
                execfile(command[1], dict(__file__=command[1]))
            elif command[0] == 'print':
                print '---' + command[1]
            elif command[0] == 'cp':
                shutil.copyfile(os.path.join(files_dir, command[1]), os.path.join(root_dir, args.name, 'config', 'dbs', command[1]))
            elif command[0] == 'cp_script':
                shutil.copyfile(os.path.join(static_dir, command[1]), os.path.join(root_dir, args.name, 'config', 'scripts', command[1]))
            elif command[0] == 'append':
                replacements = {}
                replacements["ACTIVATE"] = os.path.join(root_dir, args.name, 'virtenv_{}/bin/activate'.format(args.name))
                replacements["CONFIG_LOC"] = os.path.join(root_dir, args.name, 'config')
                replacements["ENV_LOC"] = os.path.join(root_dir, args.name)
                replacements["LOGDIR"] = os.path.join(root_dir, args.name, 'config', 'logs')
                replacements["NAME"] = args.name
                replacements["OPENBABEL"] = "export PYTHONPATH=/project/projectdirs/jcesr/openbabel/lib:$PYTHONPATH" if envtype=="rubicon" else ""
                replacements["PACKMOL"] = "export PATH=$PATH:/project/projectdirs/jcesr/packmol_hopper" if envtype=="rubicon" else ""
                replacements["MATERIALSPROJECT"] = "export VASP_PSP_DIR=/project/projectdirs/matgen/POTCARs" if envtype=="MP" else ""

                if envtype == "FW":
                    replacements["PACKAGES"] = '[]'
                elif envtype == "MP" or envtype == "rubicon":
                    replacements["PACKAGES"] = "\n  - mpworks.firetasks\n  - mpworks.dupefinders\n  - mpworks.examples"
                if envtype == "rubicon":
                    replacements["PACKAGES"] += "\n  - rubicon.firetasks.qchem\n  - rubicon.firetasks.gaussian\n  - rubicon.firetasks.lammps"

                with open(os.path.join(static_dir, 'BASH_template.txt')) as f:
                    t = CustomTemplate(f.read())
                    appendtext = t.substitute(replacements)
                    with open(BASHRC_FILE, 'a') as f2:
                        f2.write(appendtext)

                for machine in MACHINES:
                    replacements['MACHINE'] = machine
                    with open(os.path.join(static_dir, 'FW_config.yaml')) as f:
                        t = CustomTemplate(f.read())
                        appendtext = t.substitute(replacements)
                        with open(os.path.join(root_dir, args.name, 'config',
                                               'config_{}'.format(machine), 'FW_config.yaml'), 'w+') as f2:
                            f2.write(appendtext)

                    with open(os.path.join(static_dir, 'my_fworker.yaml')) as f:
                        t = CustomTemplate(f.read())
                        appendtext = t.substitute(replacements)
                        with open(os.path.join(root_dir, args.name, 'config',
                                               'config_{}'.format(machine), 'my_fworker.yaml'), 'w+') as f2:
                            f2.write(appendtext)

                    with open(os.path.join(static_dir, 'qadapter_{}.yaml'.format(machine))) as f:
                        t = CustomTemplate(f.read())
                        appendtext = t.substitute(replacements)
                        with open(os.path.join(root_dir, args.name, 'config',
                                               'config_{}'.format(machine), 'my_qadapter.yaml'), 'w+') as f2:
                            f2.write(appendtext)

                    with open(os.path.join(files_dir, 'my_launchpad.yaml')) as f:
                        t = CustomTemplate(f.read())
                        appendtext = t.substitute(replacements)
                        with open(os.path.join(root_dir, args.name, 'config',
                                               'config_{}'.format(machine), 'my_launchpad.yaml'), 'w+') as f2:
                            f2.write(appendtext)


            else:
                raise ValueError("Invalid command! {}".format(command))
    except:
        traceback.print_exc()


class CustomTemplate(string.Template):
    delimiter = '$$'


if __name__ == '__main__':
    create_env()
