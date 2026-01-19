# File Converter Utility

Auto-convert DWG and PDF drawings to DXF format for volume calculation.

## 🎯 Features

- **DWG → DXF**: Automatic conversion using ODA File Converter
- **PDF → DXF**: Automatic conversion using pdf2cad or alternatives
- **Auto-detection**: Detects file format and uses appropriate converter
- **Graceful degradation**: Shows installation instructions if converters not found
- **Error handling**: Clear messages with troubleshooting guidance

## 📦 Requirements

### ODA File Converter (for DWG files)

**FREE for commercial use**

1. Download: https://www.opendesign.com/guestfiles/oda_file_converter
2. Install to: `C:\Program Files\ODA\ODAFileConverter\`
3. Restart terminal after installation

### pdf2cad (for PDF files)

**Option 1: pdf2cad (Commercial)**
- Download: https://visual-integrity.com/pdf2cad/
- License required

**Option 2: Alternative Methods**
- **Online converters**: pdf2cad.com, zamzar.com, cloudconvert.com
- **Adobe Illustrator**: Open PDF → Save As DXF
- **AutoCAD**: Import PDF → Export DXF

## 🚀 Usage

### Method 1: Integrated Workflow

```bash
# Auto-convert and process DWG
python analisis_volume\auto_read_workflow.py "path\to\file.dwg"

# Auto-convert and process PDF
python analisis_volume\auto_read_workflow.py "path\to\file.pdf"
```

### Method 2: Batch Script

```bash
# Easy conversion with batch script
scripts\CONVERT_TO_DXF.bat "path\to\file.dwg"
scripts\CONVERT_TO_DXF.bat "path\to\file.pdf"
```

### Method 3: Direct API

```python
from analisis_volume.file_converter import FileConverter

converter = FileConverter()

# Convert DWG
success, result = converter.convert_dwg_to_dxf("input.dwg", "output_dir")
if success:
    print(f"DXF saved to: {result}")
else:
    print(f"Error: {result}")

# Convert PDF
success, result = converter.convert_pdf_to_dxf("input.pdf", "output_dir")

# Auto-detect and convert
success, result = converter.auto_convert("input.dwg")  # Works for .dwg, .pdf, .dxf
```

## 📋 Examples

### Example 1: Convert Structure Drawing

```bash
# You have: drawing\struktur.dwg
# You want: drawing\dxf\str\struktur.dxf

python analisis_volume\auto_read_workflow.py "drawing\struktur.dwg"

# System will:
# 1. Detect it's a DWG file
# 2. Convert to DXF using ODA
# 3. Save to drawing\dxf\str\
# 4. Process and create Excel
```

### Example 2: Convert PDF Plan

```bash
# You have: drawing\plan.pdf
# You want: drawing\dxf\ars\plan.dxf

python analisis_volume\auto_read_workflow.py "drawing\plan.pdf"

# If pdf2cad not installed:
# System shows instructions for:
# - Online converters
# - Adobe Illustrator method
# - Manual conversion
```

### Example 3: Check Converter Status

```bash
python analisis_volume\file_converter.py

# Output:
# ✓ ODA File Converter found: C:\Program Files\ODA\...
# ✗ pdf2cad not found
# [Installation instructions shown]
```

## ⚙️ Technical Details

### ODA File Converter Command

```bash
ODAFileConverter.exe ^
    "input_folder" ^          # Where DWG files are
    "output_folder" ^         # Where to save DXF
    "ACAD2018" ^             # Output version (compatible)
    "DXF" ^                  # Output format
    "0" ^                    # Don't recurse subfolders
    "1" ^                    # Enable audit
    "filename.dwg"           # File to convert
```

### pdf2cad Command

```bash
pdf2cad.exe ^
    -f "input.pdf" ^         # Input file
    -o "output.dxf" ^        # Output file
    -t "dxf"                 # Output format
```

## 🔧 Troubleshooting

### Issue: "ODA File Converter not found"

**Solution:**
1. Download from https://www.opendesign.com/guestfiles/oda_file_converter
2. Install to `C:\Program Files\ODA\ODAFileConverter\`
3. Verify: `"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe" --help`

### Issue: "Conversion timeout"

**Solution:**
- File too large (>100MB)
- Split drawing into smaller parts
- Convert manually in AutoCAD

### Issue: "PDF conversion failed"

**Solution:**
1. Use online converter: pdf2cad.com
2. Use Adobe Illustrator: Open PDF → Save As DXF
3. Use AutoCAD: Import PDF → Export DXF

### Issue: "Output file not created"

**Solution:**
- Check file permissions
- Check disk space
- Try converting to different folder
- Run as Administrator

## 📊 Supported Formats

| Input Format | Output Format | Tool Required | Status |
|--------------|---------------|---------------|--------|
| .dxf | .dxf | None (pass-through) | ✅ Native |
| .dwg | .dxf | ODA File Converter | ✅ Free |
| .pdf | .dxf | pdf2cad or alternatives | ⚠️ Commercial |

## 🎓 Learning Resources

- **ODA Platform**: https://www.opendesign.com/
- **DWG vs DXF**: https://www.autodesk.com/products/autocad/dwg
- **PDF to CAD**: https://visual-integrity.com/resources/

## 📝 Notes

- **DXF compatibility**: System generates ACAD2018 format (widely compatible)
- **File size**: Large files (>50MB) may take several minutes
- **Quality**: DWG conversion is lossless, PDF conversion depends on PDF quality
- **Batch processing**: Can be integrated into batch scripts for multiple files

## ⚡ Performance

| File Size | DWG → DXF Time | PDF → DXF Time |
|-----------|----------------|----------------|
| 5 MB | ~5 seconds | ~10 seconds |
| 25 MB | ~30 seconds | ~1 minute |
| 50 MB | ~1 minute | ~2 minutes |
| 100 MB+ | ~2-5 minutes | May timeout |

## 🔒 Security

- **ODA**: Official OpenDesign Alliance tool, safe
- **pdf2cad**: Commercial tool from Visual Integrity, safe
- **Online converters**: Upload at your own risk (consider data confidentiality)

## 📞 Support

If conversion fails:
1. Check error message
2. Try manual conversion
3. Verify file is not corrupted
4. Check file format is supported
5. Contact drafter for DXF version directly
