"""
MAIN SCRIPT: Sistem Analisis Volume RS Sari Dharma
Jalankan script ini untuk melakukan analisis perbandingan volume
"""

import os
import sys

# Add analisis_volume directory to path (go up from examples/ to root)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level to project root
analisis_dir = os.path.join(project_root, 'analisis_volume')
sys.path.insert(0, project_root)
sys.path.insert(0, analisis_dir)

from analisis_volume.volume_comparator import VolumeComparator


def print_header():
    """Print header yang menarik"""
    print("\n" + "╔" + "="*76 + "╗")
    print("║" + " "*25 + "SISTEM ANALISIS VOLUME" + " "*29 + "║")
    print("║" + " "*23 + "RS SARI DHARMA PROJECT" + " "*31 + "║")
    print("╚" + "="*76 + "╝")


def check_files():
    """Check apakah file-file yang dibutuhkan ada"""
    print("\n┌" + "─"*76 + "┐")
    print("│  PENGECEKAN FILE                                                           │")
    print("└" + "─"*76 + "┘\n")
    
    # Get project root dynamically (go up from examples/ to root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    
    files_to_check = {
        'Template Volume': os.path.join(base_dir, 'templates', 'Volume_dari_Gambar_TEMPLATE_V2.xlsx'),
        'Volume AUTO (DXF)': os.path.join(base_dir, 'output', 'volumes', 'Volume_dari_Gambar_AUTO.xlsx'),
        'File DXF ARS': os.path.join(base_dir, 'drawing', 'dxf', 'ars', '20251108_Plan RS Sari Dharma.dxf'),
        'RAB Struktur': os.path.join(base_dir, 'rab', 'str', 'BOQ-Dokumen Struktur.xlsx'),
        'RAB Arsitektur': os.path.join(base_dir, 'rab', 'ars', 'ANALISA VOLUME PEK  ARSITEKTUR.xlsx'),
    }
    
    all_ok = True
    has_dxf = False
    has_auto = False
    
    for name, filepath in files_to_check.items():
        exists = os.path.exists(filepath)
        status = "✓ Ada" if exists else "✗ Tidak Ada"
        print(f"  {status:12} │ {name}")
        
        if 'Volume AUTO' in name and not exists:
            all_ok = False
        if 'File DXF' in name and exists:
            has_dxf = True
        if 'Volume AUTO' in name and exists:
            has_auto = True
    
    print()
    return all_ok, has_dxf, has_auto


def main():
    """Main function"""
    print_header()
    
    # Check files
    files_ok, has_dxf, has_auto = check_files()
    
    if not files_ok:
        print("┌" + "─"*76 + "┐")
        print("│  ⚠ FILE 'Volume_dari_Gambar_AUTO.xlsx' TIDAK DITEMUKAN                    │")
        print("└" + "─"*76 + "┘\n")
        
        if has_dxf:
            print("📌 STEP 1: AUTO-READ DARI DXF (REQUIRED!)")
            print("   Anda punya file DXF! Jalankan batch file untuk auto-extract:")
            print("   → Jalankan: 2_AUTO_READ_DXF.bat")
            print("   → File akan auto-generate di output/volumes/")
            print("   → Review dan sesuaikan jika perlu\n")
        else:
            print("📌 STEP 1: PREPARE DXF FILE")
            print("   1. Pastikan file DXF ada di folder: drawing/dxf/ars/")
            print("   2. Atau convert DWG ke DXF:")
            print("      • Buka DWG di AutoCAD → Save As → DXF")
            print("      • Atau gunakan ODA File Converter (gratis)")
            print("   3. Lalu jalankan: 2_AUTO_READ_DXF.bat\n")
        
        print("📌 STEP 0 (Optional): Generate Template")
        print("   Jika belum ada template:")
        print("   → Jalankan: 1_GENERATE_TEMPLATE.bat\n")
        
        return
    
    # Configuration - use dynamic paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    
    gambar_file = os.path.join(base_dir, 'output', 'volumes', 'Volume_dari_Gambar_AUTO.xlsx')
    
    rab_files = {
        'struktur': os.path.join(base_dir, 'rab', 'str', 'BOQ-Dokumen Struktur.xlsx'),
        'arsitektur': os.path.join(base_dir, 'rab', 'ars', 'ANALISA VOLUME PEK  ARSITEKTUR.xlsx'),
    }
    
    output_dir = os.path.join(base_dir, 'output', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'LAPORAN_PERBANDINGAN_VOLUME.xlsx')
    
    print("┌" + "─"*76 + "┐")
    print("│  MULAI ANALISIS                                                            │")
    print("└" + "─"*76 + "┘")
    
    # Run comparison
    try:
        comparator = VolumeComparator(gambar_file, rab_files)
        comparator.run_comparison(output_file)
        
        print("\n┌" + "─"*76 + "┐")
        print("│  ✓ ANALISIS BERHASIL                                                       │")
        print("└" + "─"*76 + "┘\n")
        print(f"Laporan tersimpan di:")
        print(f"  {output_file}\n")
        print("Silakan buka file Excel untuk melihat hasil perbandingan detail.")
        print()
        
    except Exception as e:
        print("\n┌" + "─"*76 + "┐")
        print("│  ✗ ERROR                                                                   │")
        print("└" + "─"*76 + "┘\n")
        print(f"Error: {e}")
        print("\nJika masalah berlanjut, silakan hubungi administrator.")
        print()


if __name__ == "__main__":
    main()
