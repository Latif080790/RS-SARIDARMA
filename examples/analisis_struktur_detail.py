"""
SCRIPT: Analisis Detail Pekerjaan Struktur
Menjalankan analisis mendalam untuk matching item pekerjaan struktur dengan RAB
"""

import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from analisis_volume.struktur_analyzer import analyze_struktur_detail
import pandas as pd


def print_header():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "ANALISIS DETAIL PEKERJAAN STRUKTUR" + " "*24 + "║")
    print("║" + " "*28 + "RS SARI DHARMA" + " "*36 + "║")
    print("╚" + "="*78 + "╝")


def check_files():
    """Check if required files exist"""
    base_dir = project_root
    
    files = {
        'Volume Gambar': os.path.join(base_dir, 'output', 'volumes', 'Volume_dari_Gambar_AUTO.xlsx'),
        'RAB Struktur': os.path.join(base_dir, 'rab', 'str', 'BOQ-Dokumen Struktur.xlsx'),
    }
    
    print("\n┌" + "─"*78 + "┐")
    print("│  CHECKING FILES" + " "*62 + "│")
    print("└" + "─"*78 + "┘\n")
    
    all_ok = True
    for name, path in files.items():
        exists = os.path.exists(path)
        status = "✓ Found" if exists else "✗ Not Found"
        print(f"  {status:12} │ {name}")
        if not exists:
            all_ok = False
            print(f"              │ Expected: {path}")
    
    print()
    return all_ok, files


def main():
    """Main function"""
    print_header()
    
    # Check files
    files_ok, files = check_files()
    
    if not files_ok:
        print("┌" + "─"*78 + "┐")
        print("│  ⚠ REQUIRED FILES NOT FOUND" + " "*50 + "│")
        print("└" + "─"*78 + "┘\n")
        print("Please ensure:")
        print("  1. Run 2_AUTO_READ_DXF.bat first to generate volume gambar")
        print("  2. RAB Struktur file exists in rab/str/ folder")
        print()
        return
    
    print("┌" + "─"*78 + "┐")
    print("│  STARTING DETAILED ANALYSIS" + " "*50 + "│")
    print("└" + "─"*78 + "┘\n")
    
    try:
        # Run detailed analysis
        results_df = analyze_struktur_detail(
            gambar_file=files['Volume Gambar'],
            rab_file=files['RAB Struktur'],
            output_dir=os.path.join(project_root, 'output', 'reports')
        )
        
        print("\n┌" + "─"*78 + "┐")
        print("│  ✅ ANALYSIS COMPLETE" + " "*57 + "│")
        print("└" + "─"*78 + "┘\n")
        
        # Display quick summary
        if not results_df.empty:
            print("📊 Quick Summary:")
            print(f"   Total items analyzed: {len(results_df)}")
            
            if 'Status' in results_df.columns:
                status_counts = results_df['Status'].value_counts()
                for status, count in status_counts.items():
                    print(f"   {status}: {count} items")
            
            if 'Dampak_Biaya' in results_df.columns:
                total_dampak = results_df['Dampak_Biaya'].sum()
                print(f"\n   💰 Total Cost Impact: Rp {total_dampak:,.0f}")
            
            print(f"\n📁 Output Location: output/reports/")
            print(f"   Look for: STRUKTUR_ANALYSIS_DETAIL_*.xlsx")
        
        print("\n" + "="*80)
        print("DONE! Check the Excel report for detailed analysis.")
        print("="*80 + "\n")
        
    except Exception as e:
        print("\n┌" + "─"*78 + "┐")
        print("│  ✗ ERROR DURING ANALYSIS" + " "*53 + "│")
        print("└" + "─"*78 + "┘\n")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
