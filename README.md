# Finance Health APP
Brief summary of the project.

# ✅ Install
Follow the steps to install the project.

### 1. Create the environment
To create a new environment we can execute the following instructions.

```bash
# Conda
conda create --name project_env python=3.13
```

Alternatively, we can create the virtual environment with `venv` with the follwing commands:
```bash
# venv
...
```

### 2. Install Poetry
This project uses Poetry as a Package Manager, so first of all we need to install the tool:

```bash
# Install Package Manager
pip install poetry
```
### 3. Install dependencies
We use poetry and `pyproject.toml` to install all the dependencies.
Take into account that all the project is installed as package, so we don't need to modify PYTHON_PATH to do relative imports.
```bash
# Install all project dependencies including QA
poetry install --with QA
```

In case we need to add and install new dependencies we can use:
```bash
# Install and add new packages to the project
poetry add pandas numpy

# To install libraries for an specific group like `dev`
# Used in case we want to separate groups of deopendencies
poetry add pytest --group dev
```

### 4. Install and configure QA
This project uses `pre-commit` for code QA. This tool allow us to ensure that our code follow good practices before commiting it. To configure the tool, we only need to run the following commands:
```bash
pre-commit install
pre-commit install --hook-type commit-msg --hook-type pre-push
```


# 🔎 QA Code
This project has installed the `pre-commit` tool. This means that we won't be able to commit/push code unless we pass all the QA rules. This evaluation is executed automatically when we try to commit changes to git. To commit it is essential to write the commit message correctly, to do so, we need to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

```bash
# New features
git commit -m "feat: New feature"

# Fix errors
git commit -m "fix: Fix error ..."

# Refactor code
git commit -m "refactor: Refactor some code"
```

In case we need to ignore this evaluation, we can add the following flag:
```bash
git commit --no-verify
```

Otherwise, we can run the QA code manually with the following command lines:
```bash
# Ejecutar sobre un conjunto de ficheros especifico
pre-commit run --files file1 file2 ...

# Ejecutar sobre todos los ficheros
pre-commit run --all-files
```


## 🖥 Usage

To know how to use the code and implement new functionalities, pleases read the [Developer Guide](docs/DeveloperGuide.md) documentation.

### Execution Options
The project can be executed in three different ways:

- End-to-End Execution: Runs the entire project, executing a main script that orchestrates all pipelines.
- Single Pipeline Execution: Runs a specific pipeline along with all its steps.
- Single Step Execution: Runs a specific step of a pipeline.

### Examples of Execution
Each execution can be done from the terminal:

```bash
# 1. Execute all the code workflow
python src/main.py --json data/json

# 2 Executing only a specific pipeline
python src/cto_extension/pipeline.py

# 3. Execute only a pipeline step
python src/cto_extension/load/planex_loader.py
```
### Available Arguments

Each execution may require specific arguments, and some optional arguments might also be available. To see the list of available arguments, you can use the -h option:

```bash
# 1. Execute all the code workflow
streamlit run src/main.py
```

## 🏛 Estructura del repositorio (#TODO)

A continuación, se muestra la estructura del repositorio:
```
Redes
├── docs/                     --> Directorio de documentación de código (Sphinx)
├── notebooks/                --> Notebooks de exploración: un notebook por cada sección de desarrollo
└── src/                      --> Repositorio de código para promoción de modelos
    ├── core/                 --> Código de clases básicas a todo el proyecto
    ├── cto_extension/        --> Código para el caso de uso de Ampliación de CTO
    ├── cto_missing/          --> Código para preparar los datos
    ├── utils/                --> Funcionalidades útiles y generales
    ├── config.py             --> Script donde almacenar variables y configuraciones globales
    └── main.py               --> Script Orquestador
├── test/                     --> Directorio con los test unitarios de cada sección de desarrollo
├── .pre-commit-config.yaml   --> Configuración del QA
├── pyproject.toml            --> Configuración de proyecto y herramientas como QA
└── sonar-project.properties  --> Configuración de Sonar
```


# 🤝 Collaborate

Los Pull requests son bienvenidos. Para cambios importantes, por favor abra primero un issue para discutir qué te gustaría cambiar.

## Contribution rules
- Numpy docstring
- pre-commit

## Contribution flow
1. Actualiza tu repositorio local con `git fetch` y `git pull origin feature`
2. Crea una nueva rama de trabajo con `git switch -c feature/nombre_feature`
3. Realiza tus cambios en tu rama y agrégalos al área de preparación con `git add`
4. Confirma tus cambios localmente con `git commit -m "feat: New feature"`
5. Sube los cambios (incluyendo tu nueva rama) al repositorio remoto con `git push origin feature/nombre_feature`
6. Ve al repositorio remoto donde ahora deberías ver tu nueva rama
7. Crea una Pull Request para solicitar su fusión en `feature`
8. Una vez se valida la PR, se inicia el proceso de integración con la rama `develop`

# 👥 Team

### NTT Data AI CoE

- [Marc Domènech i Vila](mailto:mdomenei@emeal.nttdata.com) - Data Scientist at NTT Data AI CoE
- ...

# 📜 Licence

[MIT](https://choosealicense.com/licenses/mit/)
