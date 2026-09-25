# PROYECTO FINAL

Algun texto descriptivo

## Funcionalidades

El ------ siguientes características:

* 
* 
* 
* 

  
## Descarga e instalación del proyecto


## Crear entorno virtual

En la ruta raiz del proyecto, correr el siguiente comando(Asegurarse de tener python instalado y la libreria virtualenv)

* ``` python -m venv nombre_entorno```

### Activa el entorno virtual:


#### En Windows:

* ```nombre_entorno\Scripts\activate```

#### En MacOS/Linux:

* ```source nombre_entorno/bin/activate```

### Variables de entorno

#### Linux/Mac
    
* ```export FLASK_APP="run.py"```
* ```export FLASK_ENV="development"```

#### Windows

* ```set "FLASK_APP=run.py"```
* ```set "FLASK_ENV=development"```
 
### Instalación de dependencias

En el proyecto se distribuye un fichero (requirements.txt) con todas las dependencias. Para instalarlas
basta con ejectuar:

* ```pip install -r requirements.txt```

## Ejecución con el servidor que trae Flask

Una vez que hayas descargado el proyecto, creado las variables de entorno y descargado las dependencias,
puedes arrancar el proyecto ejecutando:

* ```flask run```

## Levantar el proyecto con Docker

# 1. Levantar solo la base primero
docker compose up -d db

# 2. Levantar el contenedor web pero sin correr el entrypoint todavía,
#    para poder inicializar Alembic a mano dentro del container
docker compose run --rm --entrypoint sh web

# Ya adentro del container:
flask db init
flask db migrate -m "Esquema inicial"
# Revisar el archivo generado en migrations/versions/ antes de aplicar,
# sobre todo los ENUM y el UNIQUE constraint de Asistencias
flask db upgrade
exit

# 3. Committear migrations/ al repo (sacarlo del .gitignore si estaba ignorado)
git add migrations/
git commit -m "Agrega migración inicial de Alembic"

# 4. A partir de acá, levantar todo normal — el entrypoint se encarga
docker compose up -d --build