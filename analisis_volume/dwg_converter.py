"""
Script untuk konversi DWG ke DXF
Menggunakan ODA File Converter atau AutoCAD jika tersedia
"""

import os
import subprocess
from pathlib import Path


def convert_dwg_to_dxf_with_autocad(dwg_path: str, dxf_path: str = None) -> str:
    """Konversi DWG ke DXF menggunakan AutoCAD (jika terinstall)"""
    try:
        from pyautocad import Autocad, APoint
        
        acad = Autocad(create_if_not_exists=False)
        doc = acad.app.Documents.Open(dwg_path)
        
        if dxf_path is None:
            dxf_path = dwg_path.replace('.dwg', '.dxf')
        
        doc.Export(dxf_path, "DXF", doc.ActiveLayout)
        doc.Close(False)
        
        print(f"✓ Konversi berhasil: {dxf_path}")
        return dxf_path
        
    except Exception as e:
        print(f"✗ Error konversi dengan AutoCAD: {e}")
        return None


def manual_instruction():
    """Instruksi manual untuk konversi DWG ke DXF"""
    print("\n" + "="*70)
    print("INSTRUKSI KONVERSI DWG KE DXF")
    print("="*70)
    print("\nKarena file dalam format DWG (binary), ada beberapa cara konversi:")
    print("\n1. MENGGUNAKAN AUTOCAD (Jika tersedia):")
    print("   - Buka file DWG di AutoCAD")
    print("   - File > Save As > DXF (*.dxf)")
    print("   - Pilih versi DXF yang kompatibel (R2018/2013)")
    print("   - Simpan dengan nama yang sama")
    print("\n2. MENGGUNAKAN ODA FILE CONVERTER (Gratis):")
    print("   - Download: https://www.opendesign.com/guestfiles/oda_file_converter")
    print("   - Install dan jalankan aplikasi")
    print("   - Input folder: pilih folder drawing/ars")
    print("   - Output folder: sama dengan input")
    print("   - Output version: R2018 DXF")
    print("   - Klik 'Convert'")
    print("\n3. ONLINE CONVERTER (Cepat, tapi perlu internet):")
    print("   - https://convertio.co/dwg-dxf/")
    print("   - Upload file DWG")
    print("   - Download hasil DXF")
    print("\n4. BIARKAN SCRIPT INI YANG MENGHANDLE:")
    print("   - Script akan mencoba membaca DWG langsung")
    print("   - Atau minta Anda convert manual")
    print("="*70 + "\n")


def check_file_format(filepath: str) -> str:
    """Cek format file (DWG atau DXF)"""
    with open(filepath, 'rb') as f:
        header = f.read(6)
        if header.startswith(b'AC10'):
            return 'DXF'
        elif header.startswith(b'AC1'):
            return 'DWG'
        else:
            return 'UNKNOWN'


def find_oda_converter():
    """Mencari ODA File Converter di sistem"""
    common_paths = [
        r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
        r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None


def convert_with_oda(dwg_path: str, output_dir: str = None) -> str:
    """Konversi DWG ke DXF menggunakan ODA File Converter"""
    oda_path = find_oda_converter()
    
    if not oda_path:
        print("✗ ODA File Converter tidak ditemukan")
        return None
    
    if output_dir is None:
        output_dir = os.path.dirname(dwg_path)
    
    input_dir = os.path.dirname(dwg_path)
    
    # Command line untuk ODA Converter
    cmd = [
        oda_path,
        input_dir,
        output_dir,
        "ACAD2018",  # Version
        "DXF",       # Format
        "0",         # Recurse
        "1",         # Audit
        "*.dwg"      # Filter
    ]
    
    try:
        subprocess.run(cmd, check=True)
        dxf_path = dwg_path.replace('.dwg', '.dxf')
        print(f"✓ Konversi berhasil: {dxf_path}")
        return dxf_path
    except Exception as e:
        print(f"✗ Error konversi dengan ODA: {e}")
        return None


if __name__ == "__main__":
    dwg_file = r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA\drawing\ars\20251108_Plan RS Sari Dharma.dwg"
    
    print(f"\nMemeriksa file: {dwg_file}")
    format_type = check_file_format(dwg_file)
    print(f"Format: {format_type}")
    
    if format_type == 'DWG':
        manual_instruction()
        
        print("\nMencoba konversi otomatis...")
        
        # Try ODA Converter
        result = convert_with_oda(dwg_file)
        
        if not result:
            # Try AutoCAD
            result = convert_dwg_to_dxf_with_autocad(dwg_file)
        
        if result:
            print(f"\n✓ File DXF siap: {result}")
        else:
            print("\n⚠ Silakan convert manual menggunakan salah satu cara di atas")
            print("Setelah di-convert, jalankan script lagi")
