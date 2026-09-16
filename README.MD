# OrdenX

Organizador de archivos para la carpeta Descargas, pensado para funcionar en Windows, macOS y Linux.

## Stack

- Python 3.11 o superior.
- PySide6 para la interfaz de escritorio.
- `pathlib` y `shutil` para trabajar con archivos.
- JSON para guardar las reglas en `~/.ordenx/rules.json`.

## Primera version

- Organizacion manual mediante un boton.
- Reglas para enviar archivos a carpetas y subcarpetas.
- Clasificacion inicial por extension de archivo.
- Vista previa de los movimientos antes de aplicarlos.
- El usuario puede elegir la carpeta de origen y revisar los archivos detectados.
- Los archivos sin una regla permanecen en la carpeta Descargas.

## Como ejecutar

Desde la carpeta del proyecto:

```bash
python -m pip install -e .
python main.py
```

## Uso

1. Elegir la carpeta que se quiere organizar.
2. Crear reglas, por ejemplo `pdf` -> `Documentos/PDF`.
3. Pulsar `Analizar carpeta` para revisar la vista previa.
4. Pulsar `Organizar archivos` y confirmar.

Los archivos con conflictos o sin una regla no se mueven.

## TODO

- Agregar modo automatico para vigilar la carpeta Descargas y organizar archivos nuevos.
- Agregar reglas por nombre de archivo.
- Agregar reglas por fecha.
- Agregar reglas por tamano.
- Definir el comportamiento para archivos duplicados.
