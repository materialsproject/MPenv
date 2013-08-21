from argparse import ArgumentParser
import os
import string
import subprocess
import traceback
from MPenv.mpdbmake import CONFIG_TAG

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Aug 20, 2013'


def create_env():
    root_dir = os.getcwd()
    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(module_dir, 'mpenv_static')

    BASHRC_FILE = os.path.join(root_dir, "bashrc.temp")
    MACHINES = ('Mendel', 'Hopper')  # note: you must modify BASH_template.txt when adding machines

    m_description = 'This program creates a self-contained environment for running ' \
                    'and testing FireWorks workflows at NERSC'
    parser = ArgumentParser(description=m_description)

    parser.add_argument('name', help='directory containing environment files', default=None)
    parser.add_argument('--dev', help='dev_mode', action='store_true')

    args = parser.parse_args()

    print 'VALIDATING DIRECTORY'
    if not os.path.exists(os.path.join(root_dir, args.name+CONFIG_TAG, 'my_launchpad.yaml')):
        raise ValueError("Missing file: {}".format(os.path.join(root_dir, args.name+CONFIG_TAG, 'my_launchpad.yaml')))

    c = []
    c.append(('print', 'SETTING UP VIRTUALENV'))
    c.append(("mkdir", args.name))
    c.append(("cd", args.name))
    c.append(("mkdir", "virtenv_{}".format(args.name)))
    c.append("virtualenv --no-site-packages virtenv_{}".format(args.name))
    c.append(("activate", os.path.join(root_dir, args.name, 'virtenv_{}/bin/activate_this.py'.format(args.name))))

    c.append(('print', 'INSTALLING FIREWORKS (developer mode)'))
    if not args.dev:
        c.append(("pip install django"))
        c.append(("mkdir", "codes"))
        c.append(("cd", 'codes'))
        c.append("git clone git@github.com:materialsproject/fireworks.git")
        c.append(("cd", 'fireworks'))
        c.append("python setup.py develop")

    c.append(('print', 'ADDING SETTINGS'))
    c.append(("cd", os.path.join(root_dir, args.name)))
    c.append(("mkdir", "config"))
    c.append(("cd", "config"))
    for machine in MACHINES:
        c.append(("mkdir", "config_{}".format(machine)))
    c.append(("mkdir", "dbs"))
    c.append(("mkdir", "logs"))

    c.append(('print', 'UPDATING ENVIRONMENT'))
    c.append(("append", ))

    try:
        for command in c:
            if isinstance(command, str):
                subprocess.check_call(command, shell=True, executable="/bin/bash")
            elif command[0] == 'mkdir':
                os.mkdir(command[1])
            elif command[0] == 'cd':
                os.chdir(command[1])
            elif command[0] == 'activate':
                execfile(command[1], dict(__file__=command[1]))
            elif command[0] == 'print':
                print '---' + command[1]
            elif command[0] == 'append':
                replacements = {}
                replacements["ACTIVATE"] = os.path.join(root_dir, args.name, 'virtenv_{}/bin/activate'.format(args.name))
                replacements["CONFIG_LOC"] = os.path.join(root_dir, args.name, 'config')
                replacements["NAME"] = args.name

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


            else:
                raise ValueError("Invalid command! {}".format(command))
    except:
        traceback.print_exc()


class CustomTemplate(string.Template):
    delimiter = '$$'


if __name__ == '__main__':
    create_env()