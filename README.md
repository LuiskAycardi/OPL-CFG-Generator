# OPL CFG Generator (GDX-X Database) 🎮

![PS2](https://img.shields.io/badge/Platform-PS2-blue) ![Python](https://img.shields.io/badge/Python-3.x-yellow) ![License](https://img.shields.io/badge/License-MIT-green)

Este script automatiza la creación de archivos de configuración (`.cfg`) para **Open PS2 Loader (OPL)**. Su función principal es descargar la base de datos más actualizada del proyecto [GDX-X](https://github.com/GDX-X/OPL-Games-Infos-Database-Project) y sincronizar los metadatos con tu colección de juegos de PlayStation 2.

## 🚀 Novedades de la Versión 1.2.0
- **Escaneo Interno de ISOs**: El script ahora utiliza la librería `pycdlib` para abrir tus archivos `.iso` y buscar el ID real (Serial) dentro del sistema de archivos interno. Esto garantiza compatibilidad total aunque el archivo ISO tenga un nombre genérico o incorrecto.
- **Menú Interactivo**: Al iniciar, podrás elegir entre escanear una carpeta de juegos o procesar tu archivo de caché de OPL Manager (`cache_hdl_local.dat`).

## ✨ Características
- 📥 **Sincronización Automática**: Descarga la DB en español (`PS2DB_ES.xml`) directamente desde el repositorio de GDX-X.
- 💿 **Detección Inteligente**: Soporta y normaliza IDs de todas las regiones (`SLUS`, `SLES`, `SCES`, `SLPS`, etc.).
- 🔞 **Metadatos Detallados**: Configura automáticamente clasificación parental (ESRB/PEGI), género, desarrollador, fecha de lanzamiento y descripciones optimizadas.
- 📺 **Configuración de Pantalla**: Mapeo automático de Vmode, Aspect Ratio (4:3 / 16:9) y Scan (480p, etc.).

## 🚀 Instalación

Sigue estos pasos en tu terminal o ventana de comandos para poner en marcha el generador:

1. **Clonar el repositorio:**
   `git clone https://github.com/LuiskAycardi/OPL-CFG-Generator.git`

2. **Entrar a la carpeta:**
   `cd OPL-CFG-Generator`

3. **Ejecutar el script:**
   `python OPL-CFG-Generator.py`

> **Nota:** El script instalará automáticamente las librerías necesarias la primera vez que se ejecute. Solo asegúrate de tener **Python 3.x** instalado en tu sistema.

## 📖 Modos de Uso

1. Al abrir el script, elige el método:
   - **Opción 1**: Selecciona la carpeta donde guardas tus ISOs. El script analizará cada archivo internamente para extraer su ID.
   - **Opción 2**: Selecciona tu archivo `cache_hdl_local.dat` (propio de OPL Manager).
2. El script generará una carpeta llamada **/CFG** junto al archivo del script.
3. Copia los archivos generados dentro de la carpeta `CFG` de tu memoria USB, Disco Duro o Carpeta de Red que utilizas en tu PS2 con OPL.

## 🌟 Créditos
- **Autor**: [Luis Carlos Aycardi](https://github.com/LuiskAycardi)
- **Base de Datos**: [GDX-X Project](https://github.com/GDX-X/OPL-Games-Infos-Database-Project)
- **Tecnología**: Desarrollado en Python con ayuda de las librerías: requests, py7zr, pycdlib.

---
Si este proyecto te ha sido útil, ¡no olvides dejar una ⭐ en el repositorio!