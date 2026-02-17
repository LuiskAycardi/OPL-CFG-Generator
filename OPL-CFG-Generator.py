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

# --- 2. CONFIGURACIÓN Y CRÉDITOS ---
VERSION = "1.0.1"
GITHUB_LINK = "https://github.com/LuiskAycardi/OPL-CFG-Generator" 
AUTHOR = "Luis Carlos Aycardi" 

def mostrar_creditos():
    """Muestra la firma del autor en la terminal"""
    print("\n" + "="*60)
    print(f"   OPL CFG GENERATOR v{VERSION}")
    print(f"   Desarrollado por: {AUTHOR}")
    print(f"   GitHub: {GITHUB_LINK}")
    print("="*60)
    print("   Gracias a GDX-X por la base de datos de PS2.")
    print("="*60 + "\n")

# --- 3. HERRAMIENTAS DE FORMATO ---
def normalize_id(raw_id):
    if not raw_id: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(raw_id)).upper()

def format_id_for_opl(raw_id):
    clean = normalize_id(raw_id)
    if len(clean) >= 9:
        return f"{clean[:4]}_{clean[4:7]}.{clean[7:]}"
    return clean

def clean_val(text):
    if not text: return ""
    return text.split('/')[-1].lower() if '/' in text else text.lower()

def force_prefix(text, prefix):
    if not text: return ""
    val = clean_val(text)
    return f"{prefix}/{val}"

# --- 4. DESCARGA Y EXTRACCIÓN ---
RELEASE_URL = "https://github.com/GDX-X/OPL-Games-Infos-Database-Project/releases/download/Latest/OPL-Games-Infos-Database-Project.7z"

def get_ps2_database():
    print("\n📡 Conectando con GitHub para descargar la base de datos GDX-X...")
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
        print(f"❌ Error crítico: {e}")
        if os.path.exists(archive_path): os.remove(archive_path)
    return None, None

# --- 5. PROCESO PRINCIPAL ---
def main():
    root = tk.Tk()
    root.withdraw()

    # Mostrar firma al inicio
    mostrar_creditos()

    db_root, temp_path = get_ps2_database()
    if db_root is None:
        input("Presiona Enter para salir...")
        return

    db_index = {normalize_id(g.find('Serial').text): g for g in db_root.findall('.//game') if g.find('Serial') is not None}
    
    print(f"📊 Base de datos lista: {len(db_index)} juegos indexados.")
    print("\n📂 Selecciona tu archivo 'cache_hdl_local.dat'...")
    path_dat = filedialog.askopenfilename(title="Selecciona cache_hdl_local.dat", filetypes=[("Archivo DAT", "*.dat")])
    if not path_dat: return

    local_tree = ET.parse(path_dat)
    games_to_process = [{'id': g.find('ID').text, 'title': g.find('Title').text if g.find('Title') is not None else "Desconocido"} 
                        for g in local_tree.getroot().findall('.//Game') if g.find('ID') is not None]

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CFG")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🚀 PROCESANDO {len(games_to_process)} JUEGOS...\n")
    print("-" * 65)
    print(f"{'ESTADO':<10} | {'ID':<12} | {'TÍTULO'}")
    print("-" * 65)

    encontrados = 0
    faltantes = 0

    for game in games_to_process:
        user_id_clean = normalize_id(game['id'])
        opl_id = format_id_for_opl(game['id'])
        
        if user_id_clean in db_index:
            node = db_index[user_id_clean]
            
            def get_txt(tag):
                el = node.find(tag)
                return el.text.strip() if el is not None and el.text else ""

            final_title = get_txt('Title') or game['title']
            raw_parental = get_txt('Parental')
            p_val = clean_val(raw_parental)
            p_text = p_val.upper()

            if "esrb" in raw_parental.lower():
                esrb_map = {"mature": "M", "teen": "T", "everyone": "E", "10": "E10", "17": "M"}
                p_text = esrb_map.get(p_val, p_text[:1])
            
            cfg_content = [
                "CfgVersion=8",
                "$ConfigSource=1",
                f"Title={final_title[:64]}",
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
                f.write("\n".join(cfg_content))
            
            print(f"✅ OK       | {opl_id:<12} | {final_title[:45]}")
            encontrados += 1
        else:
            print(f"❌ FALTA    | {opl_id:<12} | {game['title'][:45]}")
            faltantes += 1

    if temp_path and os.path.exists(temp_path): shutil.rmtree(temp_path)

    print("-" * 65)
    print(f"\n🏁 RESUMEN FINAL:")
    print(f"   Juegos procesados: {encontrados}")
    print(f"   Juegos faltantes:  {faltantes}")
    
    # Firma final
    mostrar_creditos()
    
    input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()