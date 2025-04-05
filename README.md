# CICD Pipeline in Python

## Basic Information
This is a template for any CICD Pipeline in Python. In this template, there are folders to be aware of:

- `src/`: This is where the source code of the project is located. The name should be changed to the repository's name. For example, if the repository is called `my-repo`, then the folder should be called `my-repo`.
- `tests/`: This is where the tests of the project are located. The structure should be the same as the `src/` folder.

There are files that should be aware of:

- `conftest.py`: This file is used to configure the tests. It is used to configure the `pytest` framework. It allows us to import the `src` folder in the tests.
- `Dockerfile`: This file is used to build the Docker image of the project.
- `.github/workflows/*.yaml`: These files are used to configure the GitHub Actions workflows. They are basically used for CICD pipelines to work. Currently, only CI is configured as we depend AWS EC2 for CD. Any changes towards the pipeline should be done here, or create another `.yaml` file for workflow.
- `BUILD`: In almost every folder, you will see a BUILD file. This file is used by Pantsbuild to build the project. It is used to configure the project and its dependencies. `pants list` list all the targets of the project

## Pantsbuild
This project uses Pantsbuild as the build system. Pantsbuild is a build system that is used to build, test, and deploy software. It is used to build the project and its dependencies. To install Pantsbuild in your local machine, run the following command:

```bash
$ ./get-pants.sh
```
This installation only needs to be done once. 

### Commands
To list all the targets of the project, run the following command:

```bash
$ pants list ::
```

You will have an output similar to this one:
```
//:_python-default_lockfile
//:reqs
//:reqs#bandit
//:reqs#black
//:reqs#flake8
//:reqs#isort
//:reqs#mypy
//:reqs#pre-commit
//:reqs#pytest
//python-default.lock:_python-default_lockfile
//requirements.txt:reqs
src/optimus_terminal:optimus_terminal
src/optimus_terminal/__init__.py
src/optimus_terminal/entity:entity
src/optimus_terminal/entity/__init__.py
src/optimus_terminal/entity/entity_core.py
src/optimus_terminal/logic:logic
src/optimus_terminal/logic/__init__.py
src/optimus_terminal/logic/logic_core.py
tests/optimus_terminal:optimus_terminal
tests/optimus_terminal:test_utils
tests/optimus_terminal:tests
tests/optimus_terminal/conftest.py:test_utils
tests/optimus_terminal/test_entity.py:tests
```
With this output, you can see the targets. Those targets can be acted as dependencies in other targets. One sample `BUILD` file is shown below:

```python
python_library(
    name='optimus_terminal',
    sources=[
        'optimus_terminal/__init__.py',
    ],
    dependencies=[
        'src/optimus_terminal/entity:entity',
        'src/optimus_terminal/logic:logic',
    ],
)
```
For `sources`, you can add all the source files of the target. For `dependencies`, you can add all the dependencies of the target. If other targets would like to use this target as an import, they can add this target as a dependency.

In Python, you can import the target as follows in any folder as long as you have the `BUILD` file:

```python
from optimus_terminal import OptimusTerminal
```

To run tests, run the following command:

```bash
$ pants test :: # To run all tests
$ pants test tests/optimus_terminal/:: # To run tests in a specific folder
$ pants test tests/optimus_terminal/fastapi.py # To run tests in a specific file
```

To run formatting tools, run the following command:

```bash
$ pants fmt :: # To run all formatting tools
$ pants fmt src/optimus_terminal/:: # To run formatting tools in a specific folder
$ pants fmt src/optimus_terminal/entity/entity_core.py # To run formatting tools in a specific file
```

# Start Server, inside the cicd-pipeline-python file, not CICD_PYTHON
```zsh
$ pants run src/optimus_terminal/fast_api/main.py
```


# Steps on resolving "yf.Ticker.History()" not working
Whole situation is caused by the yfinance has latest updates which causes the previous version not working
1. pip install yfinance --upgrade --no-cache-dir
   Checking of version: pip show yfinance 

2. Update requirements.txt's yfinance version with
 - Manually: yfinance==0.2.{} 
 - pip freeze > requirements.txt

3. Regenerate update lockfiles 
 - pants generate-lockfiles [Used this before], or 
 - pants generate-lockfiles --resolve=python-default

4. Start the server with 
```zsh
$ pants run src/optimus_terminal/fast_api/main.py
```