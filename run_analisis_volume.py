"""
MAIN SCRIPT: Sistem Analisis Volume RS Sari Dharma
Jalankan script ini untuk melakukan analisis perbandingan volume
"""

import os
import sys

# Add analisis_volume directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
analisis_dir = os.path.join(current_dir, 'analisis_volume')
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
    
    base_dir = r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA"
    
    files_to_check = {
        'Template Volume': os.path.join(base_dir, 'Volume_dari_Gambar_TEMPLATE.xlsx'),
        'Volume dari Gambar': os.path.join(base_dir, 'Volume_dari_Gambar.xlsx'),
        'Volume AUTO (DXF)': os.path.join(base_dir, 'Volume_dari_Gambar_AUTO.xlsx'),
        'File DXF': os.path.join(base_dir, 'drawing', 'ars', '20251108_Plan RS Sari Dharma.dxf'),
        'RAB Struktur': os.path.join(base_dir, 'rab', 'str', 'BOQ-Dokumen Struktur.xlsx'),
        'RAB Arsitektur': os.path.join(base_dir, 'rab', 'ars', 'ANALISA VOLUME PEK  ARSITEKTUR.xlsx'),
        'RAB Rekapitulasi': os.path.join(base_dir, 'rab', 'ars', 'REKAPITULASI PEMBANGUNAN RSU SARI DHARMA.xlsx'),
    }
    
    all_ok = True
    has_dxf = False
    has_auto = False
    
    for name, filepath in files_to_check.items():
        exists = os.path.exists(filepath)
        status = "✓ Ada" if exists else "✗ Tidak Ada"
        print(f"  {status:12} │ {name}")
        
        if name == 'Volume dari Gambar' and not exists:
            all_ok = False
        if name == 'File DXF' and exists:
            has_dxf = True
        if name == 'Volume AUTO (DXF)' and exists:
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
        print("│  ⚠ FILE 'Volume_dari_Gambar.xlsx' TIDAK DITEMUKAN                         │")
        print("└" + "─"*76 + "┘\n")
        
        if has_dxf:
            print("📌 OPSI 1: AUTO-READ DARI DXF (RECOMMENDED!)")
            print("   Anda punya file DXF! Bisa auto-extract dimensi dan volume")
            print("   → Jalankan: AUTO_READ_DXF.bat")
            print("   → File akan auto-populate ke Excel")
            print("   → Review dan sesuaikan jika perlu\n")
        
        print("📌 OPSI 2: INPUT MANUAL")
        print("   1. Buka file 'Volume_dari_Gambar_TEMPLATE.xlsx'")
        print("   2. Isi data volume berdasarkan gambar DED")
        print("   3. Simpan dengan nama 'Volume_dari_Gambar.xlsx'")
        print("   4. Jalankan script ini lagi\n")
        
        if not has_dxf:
            print("💡 TIP: Convert DWG ke DXF untuk auto-read:")
            print("   • Buka DWG di AutoCAD → Save As → DXF")
            print("   • Atau gunakan ODA File Converter (gratis)")
            print("   • Lalu jalankan: AUTO_READ_DXF.bat\n")
        
        print("Atau jika belum ada template, jalankan:")
        print("  python analisis_volume/template_generator.py\n")
        
        return
    
    # Configuration
    base_dir = r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA"
    
    gambar_file = os.path.join(base_dir, 'Volume_dari_Gambar.xlsx')
    
    rab_files = {
        'struktur': os.path.join(base_dir, 'rab', 'str', 'BOQ-Dokumen Struktur.xlsx'),
        'arsitektur': os.path.join(base_dir, 'rab', 'ars', 'ANALISA VOLUME PEK  ARSITEKTUR.xlsx'),
        'mep': os.path.join(base_dir, 'rab', 'mep', 'RAB MEP RS SARI DARMA 17 APRIL 2025.pdf')
    }
    
    output_file = os.path.join(base_dir, 'LAPORAN_PERBANDINGAN_VOLUME.xlsx')
    
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
