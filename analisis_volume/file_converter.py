"""
File Converter Utility
Auto-convert DWG to DXF and PDF to DXF/DWG
Supports: ODA File Converter for DWG, pdf2cad for PDF
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple


class FileConverter:
    """Auto-convert CAD file formats"""
    
    def __init__(self):
        self.oda_converter_paths = [
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\ODA\ODAFileConverter\ODAFileConverter.exe",
        ]
        
        self.pdf2cad_paths = [
            r"C:\Program Files\pdf2cad\pdf2cad.exe",
            r"C:\Program Files (x86)\pdf2cad\pdf2cad.exe",
        ]
    
    def find_oda_converter(self) -> Optional[str]:
        """Find ODA File Converter installation"""
        for path in self.oda_converter_paths:
            if os.path.exists(path):
                return path
        return None
    
    def find_pdf2cad(self) -> Optional[str]:
        """Find pdf2cad installation"""
        for path in self.pdf2cad_paths:
            if os.path.exists(path):
                return path
        return None
    
    def convert_dwg_to_dxf(self, dwg_path: str, output_dir: str = None) -> Tuple[bool, str]:
        """
        Convert DWG to DXF using ODA File Converter
        
        Args:
            dwg_path: Path to DWG file
            output_dir: Output directory (default: same as input)
        
        Returns:
            (success: bool, output_path or error_message: str)
        """
        # Check if file exists
        if not os.path.exists(dwg_path):
            return False, f"File not found: {dwg_path}"
        
        # Check if already DXF
        if dwg_path.lower().endswith('.dxf'):
            return True, dwg_path
        
        # Find ODA converter
        oda_path = self.find_oda_converter()
        if not oda_path:
            return False, "ODA File Converter not installed. Download from: https://www.opendesign.com/guestfiles/oda_file_converter"
        
        # Setup paths
        dwg_path = os.path.abspath(dwg_path)
        input_dir = os.path.dirname(dwg_path)
        
        if output_dir is None:
            output_dir = input_dir
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        output_dir = os.path.abspath(output_dir)
        
        # Expected output file
        filename = Path(dwg_path).stem
        output_dxf = os.path.join(output_dir, f"{filename}.dxf")
        
        print(f"\n→ Converting DWG to DXF...")
        print(f"  Input:  {dwg_path}")
        print(f"  Output: {output_dxf}")
        
        try:
            # ODA File Converter command line:
            # ODAFileConverter.exe "input_folder" "output_folder" "ACAD2018" "DXF" "0" "1" "*.dwg"
            # Parameters:
            # - input_folder: folder containing DWG files
            # - output_folder: where to save DXF
            # - ACAD2018: output version
            # - DXF: output format
            # - 0: recurse subfolders (0=no, 1=yes)
            # - 1: audit (0=no, 1=yes)
            # - *.dwg: file filter
            
            cmd = [
                oda_path,
                input_dir,
                output_dir,
                "ACAD2018",  # Output version (compatible)
                "DXF",       # Output format
                "0",         # Don't recurse
                "1",         # Audit files
                os.path.basename(dwg_path)  # Specific file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Check if output file created
            if os.path.exists(output_dxf):
                file_size = os.path.getsize(output_dxf) / 1024  # KB
                print(f"  ✓ Conversion successful! ({file_size:.1f} KB)")
                return True, output_dxf
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                return False, f"Conversion failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Conversion timeout (file too large or process hung)"
        
        except Exception as e:
            return False, f"Conversion error: {str(e)}"
    
    def convert_pdf_to_dxf(self, pdf_path: str, output_dir: str = None) -> Tuple[bool, str]:
        """
        Convert PDF to DXF using pdf2cad or similar tool
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (default: same as input)
        
        Returns:
            (success: bool, output_path or error_message: str)
        """
        # Check if file exists
        if not os.path.exists(pdf_path):
            return False, f"File not found: {pdf_path}"
        
        # Find pdf2cad
        pdf2cad_path = self.find_pdf2cad()
        if not pdf2cad_path:
            return False, "pdf2cad not installed. Alternative: Use online converter (pdf2cad.com, zamzar.com) or Adobe Illustrator"
        
        # Setup paths
        pdf_path = os.path.abspath(pdf_path)
        
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        output_dir = os.path.abspath(output_dir)
        
        # Expected output file
        filename = Path(pdf_path).stem
        output_dxf = os.path.join(output_dir, f"{filename}.dxf")
        
        print(f"\n→ Converting PDF to DXF...")
        print(f"  Input:  {pdf_path}")
        print(f"  Output: {output_dxf}")
        
        try:
            # pdf2cad command line (varies by version)
            cmd = [
                pdf2cad_path,
                "-f", pdf_path,
                "-o", output_dxf,
                "-t", "dxf"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Check if output file created
            if os.path.exists(output_dxf):
                file_size = os.path.getsize(output_dxf) / 1024  # KB
                print(f"  ✓ Conversion successful! ({file_size:.1f} KB)")
                return True, output_dxf
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                return False, f"Conversion failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Conversion timeout (file too large or process hung)"
        
        except Exception as e:
            return False, f"Conversion error: {str(e)}"
    
    def auto_convert(self, file_path: str, output_dir: str = None) -> Tuple[bool, str]:
        """
        Auto-detect format and convert to DXF
        
        Supports:
        - .dwg → .dxf (using ODA File Converter)
        - .pdf → .dxf (using pdf2cad)
        - .dxf → return as-is
        
        Args:
            file_path: Path to input file
            output_dir: Output directory (optional)
        
        Returns:
            (success: bool, dxf_path or error_message: str)
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == '.dxf':
            return True, file_path
        
        elif ext == '.dwg':
            return self.convert_dwg_to_dxf(file_path, output_dir)
        
        elif ext == '.pdf':
            return self.convert_pdf_to_dxf(file_path, output_dir)
        
        else:
            return False, f"Unsupported format: {ext}. Supported: .dxf, .dwg, .pdf"
    
    def print_install_instructions(self):
        """Print installation instructions for converters"""
        print("\n" + "="*70)
        print("FILE CONVERTER INSTALLATION INSTRUCTIONS")
        print("="*70)
        
        print("\n📥 ODA File Converter (for DWG → DXF):")
        print("   1. Download: https://www.opendesign.com/guestfiles/oda_file_converter")
        print("   2. Install to: C:\\Program Files\\ODA\\ODAFileConverter\\")
        print("   3. Free for personal/commercial use")
        
        print("\n📥 pdf2cad (for PDF → DXF):")
        print("   Option 1: Visual Integrity pdf2cad")
        print("   - Download: https://visual-integrity.com/pdf2cad/")
        print("   - Commercial license required")
        
        print("\n   Option 2: Alternative Methods:")
        print("   - Online: pdf2cad.com, zamzar.com, cloudconvert.com")
        print("   - Adobe Illustrator: Open PDF → Save As DXF")
        print("   - AutoCAD: Import PDF → Export DXF")
        
        print("\n" + "="*70 + "\n")


def main():
    """Test converter"""
    converter = FileConverter()
    
    # Test detection
    print("Checking installed converters...")
    
    oda = converter.find_oda_converter()
    if oda:
        print(f"✓ ODA File Converter found: {oda}")
    else:
        print("✗ ODA File Converter not found")
    
    pdf2cad = converter.find_pdf2cad()
    if pdf2cad:
        print(f"✓ pdf2cad found: {pdf2cad}")
    else:
        print("✗ pdf2cad not found")
    
    if not oda and not pdf2cad:
        converter.print_install_instructions()


if __name__ == "__main__":
    main()
