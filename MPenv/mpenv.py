

from argparse import ArgumentParser
import os
from os.path import expanduser
import shutil
import string
import subprocess
import traceback

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
    parser.add_argument('--dev', help='dev_mode', action='store_true')
    parser.add_argument('--pymatpro', help='install pymatpro', action='store_true')

    args = parser.parse_args()

    root_dir = os.getcwd()
    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(module_dir, 'mpenv_static')
    files_dir = os.path.join(root_dir, args.name+CONFIG_TAG)


    BASHRC_FILE = os.path.join(expanduser("~"), ".bashrc.ext")
    MACHINES = ('Mendel', 'Hopper')  # note: you must modify BASH_template.txt when adding machines

    print 'VALIDATING DIRECTORY'
    envtype = "FW"
    if not os.path.exists(files_dir):
        raise ValueError("Files directory: {} does not exist! Please make sure you are typing the ENVIRONMENT name and not the directory name.".format(files_dir))

    if not os.path.exists(os.path.join(files_dir, 'my_launchpad.yaml')):
        raise ValueError("Missing file: {}".format(files_dir, 'my_launchpad.yaml'))

    if os.path.exists(os.path.join(files_dir, 'tasks_db.json')):
        envtype = "MP"

    if os.path.exists(os.path.join(files_dir, 'molecules_db.json')):
        envtype = "rubicon"

    print 'OK, we are going to install a {} environment'.format(envtype)

    c = []
    c.append(('print', 'SETTING UP VIRTUALENV'))
    c.append(("mkdir", args.name))
    c.append(("cd", args.name))
    c.append(("mkdir", "virtenv_{}".format(args.name)))
    c.append("virtualenv --no-site-packages virtenv_{}".format(args.name))
    c.append(("activate", os.path.join(root_dir, args.name, 'virtenv_{}/bin/activate_this.py'.format(args.name))))

    if not args.dev:
        c.append(('print', 'INSTALLING FireWorks (developer mode)'))
        c.append(("mkdir", "codes"))
        c.append(("cd", 'codes'))
        c.append("git clone git@github.com:materialsproject/fireworks.git")
        c.append(("cd", 'fireworks'))
        c.append("python setup.py develop")
        if envtype == "MP" or envtype == "rubicon":
            c.append(('print', 'INSTALLING pymatgen (developer mode)'))
            c.append(("cd", '..'))
            c.append("pip install pycifrw==3.6.2")
            c.append("pip install pyhull")
            c.append("pip install pyyaml")
            c.append("git clone git@github.com:materialsproject/pymatgen.git")
            c.append(("cd", 'pymatgen'))
            c.append("python setup.py develop")

            c.append(('print', 'INSTALLING pymatgen-db (developer mode)'))
            c.append(("cd", '..'))
            c.append("git clone git@github.com:materialsproject/pymatgen-db.git")
            c.append(("cd", 'pymatgen-db'))
            c.append("python setup.py develop")

            c.append(('print', 'INSTALLING custodian (developer mode)'))
            c.append(("cd", '..'))
            c.append("git clone git@github.com:materialsproject/custodian.git")
            c.append(("cd", 'custodian'))
            c.append("python setup.py develop")

            c.append(('print', 'INSTALLING MPWorks (developer mode)'))
            c.append(("cd", '..'))
            c.append("git clone git@github.com:materialsproject/MPWorks.git")
            c.append(("cd", 'MPWorks'))
            c.append("python setup.py develop")

        if args.pymatpro:
            c.append(('print', 'INSTALLING pymatpro (developer mode)'))
            c.append(("cd", '..'))
            c.append("git clone git@github.com:materialsproject/pymatpro.git")
            c.append(("cd", 'pymatpro'))
            c.append("python setup.py develop")

        if envtype == "rubicon":
            c.append(('print', 'INSTALLING rubicon (developer mode)'))
            c.append(("cd", '..'))
            c.append("git clone git@github.com:materialsproject/rubicon.git")
            c.append(("cd", 'rubicon'))
            c.append("python setup.py develop")

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
                try:
                    subprocess.check_call(command, shell=True, executable="/bin/bash")
                except:
                    if 'pip install' in command:
                        easy_command = 'easy_install ' + command.split(' ')[-1]
                        subprocess.check_call(easy_command, shell=True, executable="/bin/bash")
                    else:
                        traceback.print_exc()
                        raise ValueError('Error executing command')

            elif command[0] == 'mkdir':
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
                    replacements["PACKAGES"] += "\n  - rubicon.firetasks\n  - rubicon.dupefinders"

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