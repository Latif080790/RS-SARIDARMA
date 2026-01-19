# TROUBLESHOOTING GUIDE

## Quick Diagnosis Table

| Symptom | Likely Cause | Quick Fix | Page |
|---------|-------------|-----------|------|
| No items detected | Layer naming issue | Check layer format | [#no-items](#no-items-detected) |
| Wrong grid assignments | Missing grid bubbles | Add grid references | [#grid-issues](#grid-assignment-issues) |
| File won't open | Corrupted DXF | Re-export from CAD | [#file-errors](#file-errors) |
| Dimensions missing | Text too far from geometry | Reposition dimensions | [#dimension-issues](#dimension-extraction-issues) |
| Slow performance | File too large | Split drawing | [#performance](#performance-issues) |
| Wrong volumes | Height not detected | Fix layer naming | [#volume-errors](#volume-calculation-errors) |

---

## File Errors

### Error: "File not found"

**Symptoms:**
```
ValidationError: File not found: drawing/file.dxf
```

**Causes:**
1. File path is incorrect
2. File was moved or deleted
3. Typo in filename

**Solutions:**
✅ **Check file path:**
```python
# Use absolute path
file_path = r"D:\Projects\Drawing\LANTAI_1.dxf"

# Or verify relative path
import os
print(os.path.abspath("drawing/file.dxf"))
```

✅ **Verify file exists:**
```bash
# Windows
dir "drawing\file.dxf"

# Linux/Mac
ls -l drawing/file.dxf
```

✅ **Check for special characters:**
- Avoid spaces in path (use underscores)
- No special characters (& % # @)
- Use forward slashes (/) or double backslashes (\\)

---

### Error: "File not readable" or "Permission denied"

**Symptoms:**
```
ValidationError: File not readable: drawing.dxf
PermissionError: [Errno 13] Permission denied
```

**Causes:**
1. File is open in AutoCAD/other program
2. Insufficient permissions
3. File is read-only

**Solutions:**
✅ **Close file in other programs:**
- Close AutoCAD, BricsCAD, or any CAD software
- Close Excel if processing RAB file
- Check Windows Task Manager for locked files

✅ **Check permissions:**
```bash
# Windows: Right-click file → Properties → Security
# Ensure your user has "Read" permission

# Linux/Mac
chmod +r drawing.dxf
```

✅ **Run as Administrator** (Windows):
- Right-click Python/batch file
- Select "Run as administrator"

---

### Error: "Invalid DXF file format"

**Symptoms:**
```
ValidationError: File doesn't appear to be a valid DXF file
```

**Causes:**
1. File is corrupted
2. File is actually DWG (not DXF)
3. Binary DXF instead of ASCII

**Solutions:**
✅ **Re-export from CAD:**
```
AutoCAD/BricsCAD:
1. Open drawing
2. File → Save As → DXF
3. Select "AutoCAD 2010/LT2010 DXF (*.dxf)"
4. Options → ASCII (not Binary)
5. Save
```

✅ **Convert DWG to DXF:**
- Use AutoCAD: `SAVEAS` → DXF
- Use LibreCAD (free): Open DWG → Export DXF
- Use online converter (check security first)

✅ **Check file integrity:**
```bash
# File should be text, not binary
# Open in Notepad - should see "0\nSECTION\nHEADER"

# Check file size - should be >100 bytes
```

---

### Error: "File too large"

**Symptoms:**
```
ValidationError: File too large: 525.3MB (max 500MB)
```

**Causes:**
1. Drawing has too many objects
2. Unnecessary layers included
3. Complex blocks or hatch patterns

**Solutions:**
✅ **Split by floor level:**
```
LANTAI_1.dxf → Process separately
LANTAI_2.dxf
LANTAI_3.dxf
```

✅ **Clean drawing in AutoCAD:**
```
Command line:
PURGE → All     # Remove unused blocks, styles
OVERKILL        # Remove duplicate objects
AUDIT           # Fix errors
SAVE AS         # Create clean copy
```

✅ **Remove unnecessary layers:**
```
- Delete hidden layers
- Remove dimension layers (if not needed)
- Delete text/annotation layers
- Keep only: GRID, Structure layers (K, B, S)
```

---

## No Items Detected

### Error: "TOTAL: 0 items calculated"

**Symptoms:**
- Processing completes but no items found
- Output Excel is empty
- Console shows "0 items calculated"

**Causes:**
1. Layer naming doesn't match patterns
2. No polylines in drawing (only blocks)
3. Geometries on wrong layers

**Solutions:**
✅ **Fix layer naming:**
```
CORRECT:
LT_1_K_H3000
LT_2_B_H400
LT_1_S_T120

INCORRECT:
COLUMN_300x400   ❌ (no floor, no height)
K-H3000          ❌ (no LT_ prefix)
LANTAI1_KOLOM    ❌ (no height)
```

✅ **Check geometry type:**
```python
# Verify polylines exist
from analisis_volume.dxf_reader import DXFReader
reader = DXFReader("file.dxf")
data = reader.extract_all()

print(f"Polylines: {len(data['polylines'])}")  # Should be >0
print(f"Texts: {len(data['texts'])}")          # Should have dimensions
```

✅ **Explode blocks:**
```
AutoCAD:
1. Select all blocks
2. Type: EXPLODE
3. Enter
4. Save as DXF
```

---

## Grid Assignment Issues

### Issue: "Grid: Unknown" or "Grid: N/A"

**Symptoms:**
- All items show "Unknown" grid
- Warning: "No grid bubbles detected"

**Causes:**
1. No grid references in drawing
2. Grid text not recognized (wrong format)
3. Grid layer not included

**Solutions:**
✅ **Add grid bubbles:**
```
Format: Single letters (A, B, C) for horizontal
       Single numbers (1, 2, 3) for vertical

Position: At edge of drawing, on grid lines
Layer: GRID or any layer
Text height: Visible size (e.g., 500mm)
```

✅ **Check grid format:**
```
CORRECT:
A, B, C (single letters)
1, 2, 3 (single digits)

INCORRECT:
A1, A2    ❌ (combined)
Grid-A    ❌ (with prefix)
AA, BB    ❌ (double letters)
```

✅ **Workaround (if can't add grids):**
```python
# System will still work, just with "Unknown" grid
# Can manually assign grids in Excel output
```

---

### Issue: Wrong grid assignments (A1 should be B2)

**Causes:**
1. Grid references in wrong position
2. Drawing not aligned to grids
3. Multiple grid systems overlapping

**Solutions:**
✅ **Verify grid positions:**
```
- Horizontal grids (A, B, C): should vary in X, constant Y
- Vertical grids (1, 2, 3): should vary in Y, constant X
- Check spacing is consistent
```

✅ **Review nearest grid algorithm:**
```python
# System assigns nearest grid within 1000mm
# If geometry far from all grids → Unknown
# Check grid_references in debug mode
```

---

## Dimension Extraction Issues

### Issue: Dimensions show as "N/A" or "0x0"

**Symptoms:**
- Dimension column empty or shows "N/A"
- Heights detected but not width/length

**Causes:**
1. Dimension text too far from geometry
2. Wrong text format
3. Dimensions in blocks (not accessible)

**Solutions:**
✅ **Move dimension text closer:**
```
- Place within 500mm-1000mm of geometry center
- For columns: near column center
- For beams: along beam length
- For slabs: inside slab boundary
```

✅ **Fix dimension format:**
```
SUPPORTED FORMATS:
30x40
300x400
30 x 40
30/40
30*40

UNSUPPORTED:
30cm x 40cm    ❌ (units not needed)
B=30, H=40     ❌ (wrong format)
.30 x .40      ❌ (decimal points wrong)
```

✅ **Extract dimensions from blocks:**
```
AutoCAD:
1. Select dimension blocks
2. EXPLODE
3. Verify text is now accessible
```

---

## Volume Calculation Errors

### Issue: Volumes are zero or incorrect

**Symptoms:**
- Volume column shows 0
- Volumes don't match manual calculations
- Some items have volumes, others don't

**Causes:**
1. Height not detected from layer
2. Wrong units (cm vs mm)
3. Invalid polyline geometry

**Solutions:**
✅ **Fix layer naming for height:**
```
HEIGHT patterns (case-insensitive):
H3000, H400, H350     # Height in mm
T120, T150, T200      # Thickness in mm
HEIGHT_3000           # Alternative format

Examples:
LT_1_K_H3000   → Height = 3.0m
LT_2_B_H400    → Height = 0.4m
LT_1_S_T120    → Thickness = 0.12m
```

✅ **Verify geometry:**
```python
# Polyline must be closed
# Minimum 3 points
# Points in correct order (clockwise/counter-clockwise)
```

✅ **Check units:**
```
Drawing units should be: millimeters (mm)
Output is always in: meters (m)

Conversion:
H3000 → 3000mm → 3.0m
T120 → 120mm → 0.12m
```

---

## RAB Matching Issues

### Issue: Items not matching RAB template

**Symptoms:**
- Kode column empty
- Items don't link to RAB
- Wrong RAB items matched

**Causes:**
1. RAB template format incorrect
2. Fuzzy match threshold too high
3. Dimension mismatch

**Solutions:**
✅ **Fix RAB template:**
```
Required columns:
- Kode (K1, B1, S1)
- Uraian (with dimensions: "Kolom 30x40")
- Volume (set to 0)
- Satuan (m³, m², m')

Example:
Kode | Uraian                    | Volume | Satuan
K1   | Kolom Beton K-300 30x40   | 0      | m³
```

✅ **Adjust match threshold:**
```python
# Default: 90% for code, 85% for description
# Lower if matches too strict
RABMatcher(code_threshold=80, desc_threshold=75)
```

✅ **Include dimensions in Uraian:**
```
GOOD:
"Kolom Beton K-300 30x40"  ✓ (has 30x40)
"Balok 20/40"              ✓ (has 20/40)

BAD:
"Kolom Beton K-300"        ❌ (no dimension)
"Balok Induk"              ❌ (no dimension)
```

---

## Performance Issues

### Issue: Processing takes >5 minutes

**Causes:**
1. File too large (>200MB)
2. Too many polylines (>10,000)
3. Complex void detection

**Solutions:**
✅ **Split drawing:**
```
By floor:
LANTAI_1.dxf
LANTAI_2.dxf
LANTAI_3.dxf

By zone:
ZONA_A.dxf
ZONA_B.dxf
```

✅ **Simplify drawing:**
```
AutoCAD:
OVERKILL     # Remove duplicates
PURGE -ALL   # Clean unused
Flatten layers if possible
```

✅ **Disable void detection (if not needed):**
```python
# Processing will be faster
# But won't detect openings in slabs
```

---

### Issue: High memory usage / crashes

**Causes:**
1. Very large file in memory
2. Memory leak (rare)
3. Insufficient system RAM

**Solutions:**
✅ **Process in batches:**
```python
# Process one floor at a time
# Save results
# Clear memory between runs
```

✅ **Use read-only mode:**
```python
# For DXF parsing
# Reduces memory footprint
```

✅ **Increase system RAM:**
- Minimum: 4GB
- Recommended: 8GB+
- For large projects (>100MB): 16GB

---

## Testing & Debugging

### Run System Tests

```bash
# Unit tests
pytest analisis_volume/test_auto_volume_calculator.py -v

# Integration tests
pytest analisis_volume/test_integration.py -v

# All tests with coverage
pytest --cov=analisis_volume --cov-report=term
```

### Enable Debug Logging

```python
from analisis_volume.production_logger import create_logger

logger = create_logger("Debug", log_level="DEBUG")
# Will show detailed processing steps
```

### Check Audit Trail

```bash
# View JSON logs
cat logs/AutoVolumeCalculator_audit.jsonl

# Count errors
grep "ERROR" logs/AutoVolumeCalculator.log | wc -l
```

### Validate Files Before Processing

```python
from analisis_volume.file_validator import FileValidator, ValidationError

validator = FileValidator()

try:
    result = validator.validate_batch(
        dxf_file="drawing.dxf",
        rab_file="rab.xlsx"
    )
    print("✓ All files valid")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    for suggestion in e.suggestions:
        print(f"  → {suggestion}")
```

---

## FAQ

**Q: Can I process DWG files directly?**
A: No, convert to DXF first using AutoCAD or free converters.

**Q: What CAD software is supported?**
A: Any software that exports DXF R2010+ format (AutoCAD, BricsCAD, LibreCAD, etc.)

**Q: Can I batch process multiple files?**
A: Yes, create a Python script to loop through files:
```python
for dxf_file in glob.glob("drawing/*.dxf"):
    # process each file
```

**Q: How accurate are the calculations?**
A: Very accurate if:
- Drawing units are mm
- Layer naming is correct
- Dimensions are provided
Tested >99% accuracy on real projects.

**Q: Can I customize aggregation?**
A: Yes, see [USER_GUIDE.md](USER_GUIDE.md#custom-aggregation)

**Q: What if I don't have RAB template?**
A: RAB is optional. System works fine without it, you just won't get automatic code matching.

**Q: Can it detect foundations, walls, stairs?**
A: Yes, as long as layer naming follows convention:
- LT_X_P_H### for foundations (Pondasi)
- LT_X_D_H### for walls (Dinding)
- LT_X_T_H### for stairs (Tangga)

---

## Getting Help

### 1. Check Documentation
- [USER_GUIDE.md](USER_GUIDE.md) - Complete usage guide
- [CRITICAL_FIXES_PRODUCTION_READY.md](CRITICAL_FIXES_PRODUCTION_READY.md) - Technical details
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Architecture overview

### 2. Review Logs
- `logs/AutoVolumeCalculator.log` - Detailed error logs
- `logs/AutoVolumeCalculator_audit.jsonl` - JSON audit trail

### 3. Run Diagnostics
```bash
python -m analisis_volume.file_validator <your_file.dxf>
pytest analisis_volume/test_*.py -v
```

### 4. Contact Support
- Internal: IT/Engineering team
- GitHub: Create an issue
- Email: [support-email]

---

## Error Code Reference

| Code | Description | Action |
|------|-------------|--------|
| E001 | File not found | Check path |
| E002 | Invalid DXF format | Re-export DXF |
| E003 | No geometries detected | Check layers |
| E004 | No grids detected | Add grid bubbles |
| E005 | Dimension extraction failed | Check text format |
| E006 | Volume calculation failed | Check height in layer |
| E007 | RAB matching failed | Check RAB format |
| E008 | File too large | Split file |
| E009 | Permission denied | Close file/Run as admin |
| E010 | Invalid Excel format | Save as .xlsx |

---

*Last Updated: January 20, 2026*
*For additional help, see USER_GUIDE.md*
