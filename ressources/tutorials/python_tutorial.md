# Python Tutorial

## Install a python3.6 virtual env

```bash
cd /path/to/dir
virtualenv -p python3.6 VENVNAME # Creates a python3.6 virtualenv at /path/to/dir/VENVNAME 
```

Venv using venv within a Pycharm Project, remember to remove venv from source (use .gitignore OR Right-click Mark directory as / EXCLUDED) (don't push it to github)

## Keep the pip install requirements

```bash
pip freeze > requirements.txt
```

## In Pycharm to link a project with a virtualenv

* File > Settings > Project:PROJECTNAME > Project Interpreter 
* Click on the small wheel in the top-right corner > Add local
* Choose here your virtualenv
* Click Apply

