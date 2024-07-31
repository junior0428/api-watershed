# Watershed API Server

### Para crear y activar este entorno conda, ejecuta:
```
conda env create -f conda_env.yml
conda activate mygisapp
conda env update -f conda_env.yml --prune

```

### Ejecuta tu aplicacion FastAPI con:

```
uvicorn main:app --reload

```