"""
Integrated DXF Scanner + DXF to Excel Converter
Auto-scan DXF files → Auto-convert DWG/PDF → Select → Convert to Excel
"""

import sys
from pathlib import Path

# Import modules
from dxf_scanner import DXFScanner
from dxf_to_excel import DXFToExcelConverter
from file_converter import FileConverter


def main():
    """Main workflow"""
    print("\n" + "="*70)
    print("AUTO READ DXF - INTEGRATED WORKFLOW")
    print("="*70)
    
    # Initialize converter
    file_converter = FileConverter()
    
    # 1. Scan DXF files
    scanner = DXFScanner()
    files = scanner.scan_dxf_files()
    
    if not files['all']:
        print("\n❌ Tidak ada file DXF ditemukan!")
        print("\nPastikan file DXF sudah ada di folder:")
        print("  - drawing/dxf/str/")
        print("  - drawing/dxf/ars/")
        print("  - drawing/dxf/mep/")
        
        # Check for DWG or PDF files that need conversion
        print("\n→ Checking for DWG/PDF files to convert...")
        base_dir = Path(__file__).parent.parent
        drawing_dir = base_dir / "drawing"
        
        dwg_files = []
        pdf_files = []
        
        for folder in ['str', 'ars', 'mep']:
            folder_path = drawing_dir / "dxf" / folder
            if folder_path.exists():
                dwg_files.extend(list(folder_path.glob("*.dwg")) + list(folder_path.glob("*.DWG")))
                pdf_files.extend(list(folder_path.glob("*.pdf")) + list(folder_path.glob("*.PDF")))
        
        if dwg_files or pdf_files:
            print(f"  Found {len(dwg_files)} DWG files, {len(pdf_files)} PDF files")
            print("\n💡 TIP: Convert these files to DXF first:")
            
            if dwg_files:
                print("\n  DWG files:")
                for dwg in dwg_files[:5]:
                    print(f"    - {dwg.name}")
                if len(dwg_files) > 5:
                    print(f"    ... and {len(dwg_files) - 5} more")
            
            if pdf_files:
                print("\n  PDF files:")
                for pdf in pdf_files[:5]:
                    print(f"    - {pdf.name}")
                if len(pdf_files) > 5:
                    print(f"    ... and {len(pdf_files) - 5} more")
            
            file_converter.print_install_instructions()
        
        return False
    
    # 2. Display list
    scanner.list_all_dxf()
    
    # 3. Check command line argument for auto-select
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        # Check if it's a file path (DWG or PDF to convert)
        if arg.endswith('.dwg') or arg.endswith('.pdf'):
            input_file = Path(arg)
            if not input_file.exists():
                print(f"\n❌ File not found: {input_file}")
                return False
            
            print(f"\n→ Auto-converting {input_file.suffix.upper()} to DXF...")
            
            # Determine output directory based on file location or type
            if 'struktur' in str(input_file).lower() or 'str' in str(input_file).lower():
                output_dir = scanner.base_dir / "drawing" / "dxf" / "str"
            elif 'arsitektur' in str(input_file).lower() or 'ars' in str(input_file).lower():
                output_dir = scanner.base_dir / "drawing" / "dxf" / "ars"
            elif 'mep' in str(input_file).lower() or 'plumbing' in str(input_file).lower() or 'elektrik' in str(input_file).lower():
                output_dir = scanner.base_dir / "drawing" / "dxf" / "mep"
            else:
                output_dir = input_file.parent
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            success, result = file_converter.auto_convert(str(input_file), str(output_dir))
            
            if success:
                selected_dxf = result
                print(f"✓ Conversion successful: {Path(selected_dxf).name}")
            else:
                print(f"✗ Conversion failed: {result}")
                return False
        
        # Auto-select by category or latest
        elif arg in ['str', 'ars', 'mep']:
            selected_dxf = scanner.get_latest_dxf(arg)
            print(f"\n✓ Auto-selected latest {arg.upper()}: {Path(selected_dxf).name}")
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
