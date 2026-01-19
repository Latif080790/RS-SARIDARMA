"""
Integrated DXF Scanner + DXF to Excel Converter
Auto-scan DXF files → Select → Convert to Excel
"""

import sys
from pathlib import Path

# Import modules
from dxf_scanner import DXFScanner
from dxf_to_excel import DXFToExcelConverter


def main():
    """Main workflow"""
    print("\n" + "="*70)
    print("AUTO READ DXF - INTEGRATED WORKFLOW")
    print("="*70)
    
    # 1. Scan DXF files
    scanner = DXFScanner()
    files = scanner.scan_dxf_files()
    
    if not files['all']:
        print("\n❌ Tidak ada file DXF ditemukan!")
        print("\nPastikan file DXF sudah ada di folder:")
        print("  - drawing/dxf/str/")
        print("  - drawing/dxf/ars/")
        print("  - drawing/dxf/mep/")
        return False
    
    # 2. Display list
    scanner.list_all_dxf()
    
    # 3. Check command line argument for auto-select
    if len(sys.argv) > 1:
        # Auto-select by category or latest
        category = sys.argv[1].lower() if sys.argv[1] in ['str', 'ars', 'mep'] else None
        if category:
            selected_dxf = scanner.get_latest_dxf(category)
            print(f"\n✓ Auto-selected latest {category.upper()}: {Path(selected_dxf).name}")
        else:
            selected_dxf = scanner.get_latest_dxf()
            print(f"\n✓ Auto-selected latest: {Path(selected_dxf).name}")
    else:
        # Interactive selection
        selected_dxf = scanner.select_dxf_interactive()
    
    if not selected_dxf:
        print("\n❌ Tidak ada file yang dipilih!")
        return False
    
    print(f"\n✓ File dipilih: {Path(selected_dxf).name}")
    
    # 4. Find template
    base_dir = Path(__file__).parent.parent
    template_file = base_dir / "output" / "templates" / "Volume_dari_Gambar_TEMPLATE_V2.xlsx"
    
    if not template_file.exists():
        template_file = base_dir / "output" / "templates" / "Volume_dari_Gambar_TEMPLATE.xlsx"
    
    if not template_file.exists():
        print("\n❌ Template tidak ditemukan!")
        print(f"   Lokasi dicari: {template_file}")
        print("\nJalankan dulu: scripts\\1_GENERATE_TEMPLATE_V2.bat")
        return False
    
    print(f"✓ Template: {template_file.name}")
    
    # 5. Setup output
    output_file = base_dir / "output" / "volumes" / "Volume_dari_Gambar_AUTO.xlsx"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 6. Run conversion
    print("\n" + "="*70)
    print("CONVERTING DXF TO EXCEL...")
    print("="*70)
    
    converter = DXFToExcelConverter(
        selected_dxf,
        str(template_file),
        str(output_file)
    )
    
    success = converter.run_conversion()
    
    if success:
        print("\n" + "="*70)
        print("✅ CONVERSION SUCCESS!")
        print("="*70)
        print(f"\n📁 Output: {output_file}")
        print(f"📊 Location: {output_file.relative_to(base_dir)}")
        print("\n✅ File siap untuk analisis!")
        print("\nNext step: Jalankan scripts\\3_RUN_ANALISIS.bat")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
