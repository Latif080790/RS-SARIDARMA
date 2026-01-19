# USER GUIDE - Auto Volume Calculator

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Step-by-Step Usage](#step-by-step-usage)
5. [Best Practices](#best-practices)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

**Auto Volume Calculator** adalah aplikasi otomatis untuk menghitung volume pekerjaan struktur dari file gambar DXF. Sistem ini menganalisis geometri, mendeteksi item pekerjaan (kolom, balok, plat), dan menghasilkan laporan volume yang siap untuk RAB (Rencana Anggaran Biaya).

### Key Features
- ✅ **Automatic Grid Detection** - Deteksi otomatis grid reference (A, B, C / 1, 2, 3)
- ✅ **Smart Height Extraction** - Ekstrak tinggi dari layer name (H3000, T120)
- ✅ **Void Detection** - Hitung net area dengan deteksi void/opening
- ✅ **Multi-Floor Support** - Support multiple lantai dalam satu drawing
- ✅ **RAB Integration** - Fuzzy matching dengan RAB template
- ✅ **Production Logging** - Comprehensive error tracking dan audit trail

---

## Installation

### Prerequisites
- Python 3.8 atau lebih baru
- Windows 10/11 (tested), Linux, atau macOS

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd RS-SARIDARMA
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- `ezdxf` - DXF file parsing
- `pandas` - Data processing
- `openpyxl` - Excel file handling
- `rapidfuzz` - Fuzzy string matching
- `pytest` - Testing (development only)

---

## Quick Start

### Option 1: Using Batch File (Windows)
```cmd
RUN_ANALISIS.bat
```

### Option 2: Using Python Script
```bash
python run_analisis_volume.py <path_to_dxf_file>
```

### Option 3: Programmatic Usage
```python
from analisis_volume.auto_volume_calculator import AutoVolumeCalculator
from analisis_volume.dxf_reader import DXFReader

# Read DXF file
reader = DXFReader("drawing/ars/LANTAI_1.dxf")
dxf_data = reader.extract_all()

# Calculate volumes
calculator = AutoVolumeCalculator(dxf_data)
items = calculator.calculate_all_volumes()

# Export to Excel
import pandas as pd
df = pd.DataFrame(items)
df.to_excel("output/hasil_volume.xlsx", index=False)
```

---

## Step-by-Step Usage

### Step 1: Prepare Your DXF File

**Drawing Requirements:**
1. **Grid Bubbles** (sangat disarankan)
   - Buat grid references: A, B, C (horizontal) dan 1, 2, 3 (vertical)
   - Letakkan di layer "GRID" atau layer khusus
   - Posisi: di tepi drawing, di intersection grid lines

2. **Layer Naming Convention**
   ```
   Format: LT_[FLOOR]_[TYPE]_[HEIGHT/THICKNESS]
   
   Examples:
   - LT_1_K_H3000   → Lantai 1, Kolom, Height 3000mm
   - LT_2_B_H400    → Lantai 2, Balok, Height 400mm
   - LT_1_S_T120    → Lantai 1, Slab, Thickness 120mm
   ```

3. **Dimension Text**
   - Letakkan dimension text (300x400, 20x40) dekat dengan geometri
   - Format: WIDTHxHEIGHT (misalnya: 30x40, 300x400)
   - Layer: DIM atau TEXT

4. **Code Labels** (optional)
   - Tambahkan kode item dekat geometri (K1, B1, S1)
   - Helps dengan RAB matching

### Step 2: Run the Analyzer

**Method A: Interactive Mode**
```bash
python run_analisis_volume.py
```
Program akan meminta:
1. Path ke file DXF
2. Path ke RAB template (optional)
3. Output filename

**Method B: Direct Path**
```bash
python run_analisis_volume.py "drawing/ars/LANTAI_1.dxf"
```

**Method C: With RAB Template**
```bash
python run_analisis_volume.py "drawing/ars/LANTAI_1.dxf" --rab "rab/ars/template.xlsx"
```

### Step 3: Review Output

Output Excel file contains:
- **Lantai** - Floor level (LT 1, LT 2, etc.)
- **Grid** - Grid reference (A1, B2, etc.)
- **Jenis Item** - Item type (KOLOM, BALOK, PLAT)
- **Kode** - Item code (K1, B1, S1)
- **Dimension** - Dimensions (30x40, 20x40)
- **Height** - Height/thickness in meters
- **Volume** - Calculated volume (m³ or m²)
- **Count** - Number of similar items
- **Satuan** - Unit (m³, m², m')

### Step 4: Validation

1. **Check Grid Assignments**
   - Verify grid references match drawing
   - Look for "Unknown" or "N/A" - indicates missing grids

2. **Verify Dimensions**
   - Cross-check with actual drawing dimensions
   - Check for missing or incorrect dimensions

3. **Review Volumes**
   - Spot-check calculations:
     - Kolom: width × height × length
     - Balok: width × height × length
     - Plat: area × thickness

4. **Check Aggregation**
   - Items with same location + dimension should be aggregated
   - Count should match actual quantity

---

## Best Practices

### Drawing Preparation

✅ **DO:**
- Use consistent layer naming (LT_X_TYPE_HEIGHT)
- Add grid bubbles for accurate location tracking
- Place dimension text near geometries
- Use closed polylines for slabs/plates
- Export as DXF R2010 or R2013 ASCII format

❌ **DON'T:**
- Mix different naming conventions in one drawing
- Use blocks extensively (system prefers polylines)
- Leave layers unnamed or use generic names
- Create overlapping geometries without proper void handling

### Performance Tips

**For Large Files (>100MB):**
1. Split by floor level (one DXF per floor)
2. Remove unnecessary layers before processing
3. Purge unused blocks and styles
4. Use "Save As" to reduce file size

**For Better Accuracy:**
1. Place dimension text within 500mm of geometry
2. Use exact grid references (A, B, C not A1, A2)
3. Add floor level indicators in drawing
4. Label special items (voids, openings)

### RAB Matching Best Practices

**RAB Template Format:**
```
| Kode | Uraian                    | Volume | Satuan |
|------|---------------------------|--------|--------|
| K1   | Kolom Beton K-300 30x40   | 0      | m³     |
| B1   | Balok Beton 20x40         | 0      | m³     |
| S1   | Plat Lantai t=12cm        | 0      | m²     |
```

**Matching Tips:**
- Include dimensions in Uraian (30x40, 20x40)
- Use consistent naming (Kolom, not Column)
- Match satuan with item type (m³ for volume, m² for area)

---

## Advanced Features

### Void Detection

System automatically detects voids/openings in slabs:
```python
# Slabs with openings will show net area
# Example: 100m² slab with 4m² opening = 96m² net area
```

Void detection criteria:
- Inner polyline must be completely inside outer polyline
- Void area must be >30% of outer to avoid false positives
- Both polylines must be on same layer

### Multi-Floor Processing

Process multiple floors in one drawing:
```python
# Layer naming automatically separates floors
LT_1_K_H3000  # Floor 1
LT_2_K_H3000  # Floor 2
LT_3_K_H3000  # Floor 3
```

Output will be grouped by floor level.

### Custom Aggregation

Three aggregation modes:
1. **By Location + Dimension** (default)
   - Groups: Lantai + Grid + Item Type + Dimension
   
2. **By Location Only**
   ```python
   calculator.aggregate_by_location_only()
   ```
   - Summary per grid location

3. **By Item Type**
   ```python
   calculator.aggregate_by_item_type()
   ```
   - Total per item type across all locations

### Production Logging

Enable comprehensive logging:
```python
from analisis_volume.production_logger import create_logger

logger = create_logger("MyProject", log_level="DEBUG")
calculator = AutoVolumeCalculator(dxf_data, logger=logger)
calculator.calculate_all_volumes()

logger.print_summary()  # Show errors/warnings
logger.close()
```

Log files location: `logs/`
- `AutoVolumeCalculator.log` - Rotating log file (max 10MB)
- `AutoVolumeCalculator_audit.jsonl` - JSON audit trail

### File Validation

Validate files before processing:
```python
from analisis_volume.file_validator import FileValidator, ValidationError

validator = FileValidator(logger)

try:
    result = validator.validate_dxf_file("drawing.dxf")
    print(f"File size: {result['file_size_mb']}MB")
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Suggestions: {e.suggestions}")
```

---

## Troubleshooting

### Common Issues

**1. "No grid bubbles detected"**
- **Cause**: No grid references in drawing
- **Solution**: Add grid bubbles or accept "Unknown" grid assignments
- **Workaround**: Use layer names for location info

**2. "File not found or not readable"**
- **Cause**: File path incorrect or permission issue
- **Solution**: 
  - Check file path (use absolute path)
  - Close file if open in CAD software
  - Run with appropriate permissions

**3. "No items detected"**
- **Cause**: Layer naming doesn't match patterns or no geometries found
- **Solution**:
  - Check layer names follow LT_X_TYPE_HEIGHT format
  - Verify geometries are polylines (not blocks)
  - Check if drawing has actual structural elements

**4. "Dimensions not extracted"**
- **Cause**: Dimension text too far from geometry or wrong format
- **Solution**:
  - Place dimension within 500mm-1000mm of geometry
  - Use format: WIDTHxHEIGHT (30x40, 300x400)
  - Check text is in TEXT or DIM layer

**5. "Volume calculations seem wrong"**
- **Cause**: Wrong units or incorrect height detection
- **Solution**:
  - Verify drawing units (should be mm)
  - Check layer naming includes height (H3000, T120)
  - Manually verify a few samples

### Getting Help

1. **Check Logs**: Review `logs/AutoVolumeCalculator.log` for detailed errors
2. **Run Tests**: `pytest analisis_volume/test_*.py -v` to verify system health
3. **Enable Debug Mode**: Set `log_level="DEBUG"` for verbose logging
4. **Review Documentation**: Check `CRITICAL_FIXES_PRODUCTION_READY.md` for known issues

### Performance Issues

**Slow Processing (>5 minutes for one file):**
- File too large (>200MB) - split into smaller files
- Too many polylines (>10,000) - simplify drawing
- Complex void detection - check for many nested polylines

**Memory Issues:**
- Close other applications
- Process one floor at a time
- Increase system RAM if possible

---

## Support & Contact

For issues, questions, or feature requests:
- **Internal**: Contact IT/Engineering team
- **GitHub**: Create an issue in repository
- **Email**: [your-support-email]

---

## Version History

**v2.0 (Current) - Production Ready (100%)**
- ✅ Integration test suite (20+ tests)
- ✅ Production logging system
- ✅ File validation with error recovery
- ✅ Complete documentation
- ✅ All 10 priorities implemented

**v1.5 - Refactored Architecture (98%)**
- ✅ Modular components (GridDetector, VoidDetector, etc.)
- ✅ Unit tests (15/15 passing)
- ✅ Robust regex patterns
- ✅ Fuzzy RAB matching

**v1.0 - Initial Release (85%)**
- Basic volume calculation
- Grid detection
- Excel export

---

*Last Updated: January 20, 2026*
*Auto Volume Calculator - RS Sari Darma*
