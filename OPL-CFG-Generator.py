import os
import re
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import shutil

# --- 1. GESTIÓN DE DEPENDENCIAS ---
def install_and_import(package):
    try:
        return __import__(package)
    except ImportError:
        print(f"📦 Instalando librería necesaria: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return __import__(package)

requests = install_and_import('requests')
py7zr = install_and_import('py7zr')
pycdlib = install_and_import('pycdlib') # Librería para leer dentro de ISOs

# --- 2. CONFIGURACIÓN Y CRÉDITOS ---
VERSION = "1.2.0"
GITHUB_LINK = "https://github.com/LuiskAycardi/OPL-CFG-Generator" 
AUTHOR = "Luis Carlos Aycardi" 

def mostrar_creditos():
    print("\n" + "="*60)
    print(f"   OPL CFG GENERATOR v{VERSION}")
    print(f"   Desarrollado por: {AUTHOR}")
    print(f"   GitHub: {GITHUB_LINK}")
    print("="*60)
    print("   Gracias a GDX-X por la base de datos de PS2.")
    print("="*60 + "\n")

# --- 3. HERRAMIENTAS DE FORMATO Y LECTURA DE ISO ---
def normalize_id(raw_id):
    if not raw_id: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(raw_id)).upper()

def format_id_for_opl(raw_id):
    clean = normalize_id(raw_id)
    if len(clean) >= 9:
        return f"{clean[:4]}_{clean[4:7]}.{clean[7:]}"
    return clean

def get_id_from_inside_iso(iso_path):
    """Abre la ISO y busca el archivo con formato SLES_XXX.XX o similar"""
    iso = pycdlib.PyCdlib()
    try:
        iso.open(iso_path)
        # Recorremos los archivos en el directorio raíz de la ISO
        for child in iso.list_children(iso_path='/'):
            name = child.file_identifier().decode('utf-8').split(';')[0]
            # Buscamos el patrón: 4 letras, guion o guion bajo, 3 números, punto, 2 números
            match = re.search(r'([A-Z]{4})[_-](\d{3})\.(\d{2})', name.upper())
            if match:
                iso.close()
                return f"{match.group(1)}_{match.group(2)}.{match.group(3)}"
        iso.close()
    except Exception:
        pass
    return None

def clean_val(text):
    if not text: return ""
    return text.split('/')[-1].lower() if '/' in text else text.lower()

def force_prefix(text, prefix):
    if not text: return ""
    val = clean_val(text)
    return f"{prefix}/{val}"

# --- 4. DESCARGA DE BASE DE DATOS ---
RELEASE_URL = "https://github.com/GDX-X/OPL-Games-Infos-Database-Project/releases/download/Latest/OPL-Games-Infos-Database-Project.7z"

def get_ps2_database():
    print("\n📡 Descargando base de datos GDX-X...")
    temp_dir = "temp_gdx_data"
    archive_path = "data_bundle.7z"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(RELEASE_URL, headers=headers, stream=True, timeout=60)
        with open(archive_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=temp_dir)
        target_xml = next((os.path.join(root, f) for root, _, files in os.walk(temp_dir) for f in files if "PS2DB_ES.xml" in f), None)
        if target_xml:
            tree = ET.parse(target_xml)
            if os.path.exists(archive_path): os.remove(archive_path)
            return tree.getroot(), temp_dir
    except Exception as e:
        print(f"❌ Error: {e}")
    return None, None

# --- 5. PROCESO PRINCIPAL ---
def main():
    root = tk.Tk()
    root.withdraw()
    mostrar_creditos()

    print("Selecciona el origen de los juegos:")
    print("1. Escanear carpeta de ISOs (Lectura interna de ID)")
    print("2. Usar archivo 'cache_hdl_local.dat'")
    opcion = input("\nOpción: ")

    db_root, temp_path = get_ps2_database()
    if db_root is None: return

    db_index = {normalize_id(g.find('Serial').text): g for g in db_root.findall('.//game') if g.find('Serial') is not None}
    games_to_process = []

    if opcion == "1":
        folder = filedialog.askdirectory(title="Selecciona la carpeta de ISOs")
        if not folder: return
        files = [f for f in os.listdir(folder) if f.lower().endswith('.iso')]
        print(f"🔍 Analizando {len(files)} archivos ISO internamente...")
        for file in files:
            full_path = os.path.join(folder, file)
            game_id = get_id_from_inside_iso(full_path)
            if game_id:
                games_to_process.append({'id': game_id, 'title': file})
                print(f"🔎 ID Encontrado: {game_id} en {file[:30]}...")
            else:
                print(f"⚠️ No se pudo leer el ID dentro de: {file}")

    elif opcion == "2":
        path_dat = filedialog.askopenfilename(title="Selecciona archivo .dat", filetypes=[("Archivo DAT", "*.dat")])
        if not path_dat: return
        local_tree = ET.parse(path_dat)
        for g in local_tree.getroot().findall('.//Game'):
            gid = g.find('ID').text if g.find('ID') is not None else None
            if gid: games_to_process.append({'id': gid, 'title': g.find('Title').text or "Desconocido"})

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CFG")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🚀 GENERANDO {len(games_to_process)} ARCHIVOS CFG...\n" + "-"*65)
    encontrados = 0

    for game in games_to_process:
        user_id_clean = normalize_id(game['id'])
        opl_id = format_id_for_opl(game['id'])
        
        if user_id_clean in db_index:
            node = db_index[user_id_clean]
            def get_txt(tag):
                el = node.find(tag)
                return el.text.strip() if el is not None and el.text else ""

            raw_parental = get_txt('Parental')
            p_val = clean_val(raw_parental)
            p_text = p_val.upper()
            if "esrb" in raw_parental.lower():
                p_text = {"mature": "M", "teen": "T", "everyone": "E", "10": "E10", "17": "M"}.get(p_val, p_text[:1])

            cfg = [
                "CfgVersion=8", "$ConfigSource=1",
                f"Title={get_txt('Title') or game['title']}",
                f"Aspect={force_prefix(get_txt('Aspect'), 'aspect')}",
                f"AspectText={'16:9' if clean_val(get_txt('Aspect')) == 'w' else '4:3'}",
                f"Scan={force_prefix(get_txt('Scan'), 'scan')}",
                f"ScanText={clean_val(get_txt('Scan'))}",
                f"Players={force_prefix(get_txt('Players'), 'players')}",
                f"PlayersText={clean_val(get_txt('Players'))}",
                f"Release={get_txt('Release')}",
                f"Developer={get_txt('Developer')}",
                f"Vmode={force_prefix(get_txt('Vmode'), 'vmode')}",
                f"VmodeText={clean_val(get_txt('Vmode')).upper()}",
                f"Genre={get_txt('Genre')}",
                f"Description={' '.join(get_txt('Description').split())[:255]}",
                f"Rating={force_prefix(get_txt('Rating'), 'rating')}",
                f"RatingText={clean_val(get_txt('Rating')) or '0'}",
                f"Parental={raw_parental}",
                f"ParentalText={p_text}"
            ]
            with open(os.path.join(output_dir, f"{opl_id}.cfg"), "w", encoding="utf-8") as f:
                f.write("\n".join(cfg))
            print(f"✅ OK | {opl_id:<12} | {game['title'][:40]}")
            encontrados += 1
        else:
            print(f"❌ ?? | {opl_id:<12} | {game['title'][:40]}")

    if temp_path: shutil.rmtree(temp_path)
    mostrar_creditos()
    input("Finalizado. Presiona Enter...")

if __name__ == "__main__":
    main()