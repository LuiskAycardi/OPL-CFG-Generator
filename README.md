\# OPL CFG Generator (GDX-X Database) 🎮



Este script automatiza la creación de archivos de configuración (`.cfg`) para \*\*Open PS2 Loader (OPL)\*\*.

Descarga automáticamente la base de datos más reciente del proyecto \[GDX-X](https://github.com/GDX-X/OPL-Games-Infos-Database-Project) y sincroniza la información con tus juegos locales de esta forma podrás obtener la metadata para que tu OPL muestre la toda la información de tus juegos. recomiendo usar la versión de OPL 1.1 stable. 

el script usa archivo cache_hdl_local.dat que genera automáticamente OPL manager 2.4, en posteriores versiones de este script implementare el escaneo directo de carpetas con ISOs para extraer las ID de los juegos. 



\## Características ✨

\- 📥 Descarga automática de la DB actualizada.

\- 🔍 Mapeo inteligente de IDs (insensible a guiones o puntos).

\- 📝 Generación de metadatos completos: Título, Desarrollador, Género, Descripción, etc.

\- 🔞 Soporte correcto para Clasificación Parental (ESRB/PEGI).

\- 📺 Configuración automática de Video (Vmode, Scan, Aspect).



\## Requisitos 📋

\- Python 3.x

\- Conexión a Internet



\## Instalación 🛠️

1\. Clona el repositorio:

```bash
git clone https://github.com/LuiskAycardi/OPL-CFG-Generator.git
```

2\. Cambia al directorio clonado:

```bash
cd OPL-CFG-Generator
``` 


\## Uso 🚀

1\. Ejecuta el script:

```bash
python OPL-CFG-Generator.py
```  

2\. El script descargará la base de datos.

3\. Selecciona tu archivo `cache_hdl_local.dat`

4\. Los archivos `.cfg` se generarán en la carpeta `/CFG`.

5\. Copia la carpeta CFG a la carpeta +OPL del HDD de tu PS2. 

6\. Disfruta de tu libreria de juegos con metadata.

\## Créditos

\- Base de datos por \[GDX-X Project](https://github.com/GDX-X/OPL-Games-Infos-Database-Project).

