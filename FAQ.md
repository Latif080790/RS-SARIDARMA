# FAQ - Frequently Asked Questions

## General Questions

### What is Auto Volume Calculator?
Auto Volume Calculator adalah aplikasi otomatis untuk menghitung volume pekerjaan struktur (kolom, balok, plat) dari file gambar DXF. Sistem menganalisis geometri, mendeteksi item secara otomatis, dan menghasilkan laporan volume untuk RAB.

### Who should use this tool?
- **QS (Quantity Surveyor)** - Hitung volume untuk BOQ/RAB
- **Project Engineers** - Validasi volume pekerjaan
- **Estimators** - Quick take-off dari drawing
- **CAD Operators** - Generate volume reports

### What file formats are supported?
- **Input**: DXF (AutoCAD R2010+), optional Excel (.xlsx) for RAB
- **Output**: Excel (.xlsx) with volume breakdown

### Is this free?
Internal tool untuk RS Sari Darma. No licensing required for internal use.

---

## Technical Questions

### What are the system requirements?

**Minimum:**
- OS: Windows 10, Linux, or macOS
- Python: 3.8+
- RAM: 4GB
- Disk: 100MB

**Recommended:**
- Python: 3.10+
- RAM: 8GB (16GB for large projects)
- SSD storage

### What CAD software can I use?
Any CAD software that exports DXF:
- ✅ AutoCAD (2010+)
- ✅ BricsCAD
- ✅ DraftSight
- ✅ LibreCAD (free)
- ✅ FreeCAD (free)

### Can I process DWG files directly?
**No.** DWG must be converted to DXF first:
1. Open DWG in AutoCAD
2. File → Save As → DXF
3. Select "AutoCAD 2010/LT2010 DXF"
4. Save

### What DXF version should I use?
**Recommended:** AutoCAD 2010/LT2010 DXF (ASCII format)
- ✅ Most compatible
- ✅ Readable as text
- ✅ Well-supported

**Also works:**
- AutoCAD 2013/2018 DXF
- Older versions (R14, R2000) may have issues

---

## Drawing Preparation

### Do I need to prepare my drawing before processing?
**Recommended** for best results:
1. Add grid bubbles (A, B, C / 1, 2, 3)
2. Use consistent layer naming (LT_X_TYPE_HEIGHT)
3. Add dimension text near geometries
4. Clean up drawing (PURGE, AUDIT)

**Minimum** requirements:
- Structural elements as polylines
- Some indication of floor level
- Height information (in layer or dimensions)

### What is the layer naming convention?
```
Format: LT_[FLOOR]_[TYPE]_[HEIGHT]

Components:
- LT_ : Prefix (required)
- [FLOOR] : Floor number (1, 2, 3, ...)
- [TYPE] : K (kolom), B (balok), S (slab/plat)
- [HEIGHT] : H### (height in mm) or T### (thickness in mm)

Examples:
LT_1_K_H3000   → Lantai 1, Kolom, 3.0m height
LT_2_B_H400    → Lantai 2, Balok, 0.4m height
LT_1_S_T120    → Lantai 1, Slab, 0.12m thick
```

### Do I have to follow the layer naming exactly?
**For automatic detection: Yes.**
System relies on layer pattern matching.

**Workaround** if can't change layers:
- Add text labels with item info
- Use dimension text extensively
- Manually assign after export

### What are grid bubbles and why do I need them?
**Grid bubbles** = Grid reference markers (A, B, C / 1, 2, 3)

**Purpose:**
- Identify exact location of each item
- Enable location-based aggregation
- Match with construction schedule

**Without grids:**
- System assigns "Unknown" or "N/A"
- Can't track by location
- Less useful for scheduling

### Can I use blocks instead of polylines?
**Not recommended.** System works best with:
- ✅ Polylines (closed)
- ✅ Rectangles
- ✅ Circles (for columns)

**Blocks must be exploded:**
```
AutoCAD: Select → EXPLODE → Save
```

---

## Processing & Output

### How long does processing take?
Depends on file size and complexity:
- Small (<10MB, <500 items): **10-30 seconds**
- Medium (10-50MB, 500-2000 items): **1-3 minutes**
- Large (50-200MB, 2000-10000 items): **3-10 minutes**
- Very large (>200MB): **May need splitting**

### What if processing takes too long (>10 minutes)?
**Try these:**
1. Split drawing by floor level
2. Remove unnecessary layers
3. PURGE drawing to reduce size
4. Check for complex void detection (nested polylines)

### What information is in the output Excel?
**Standard columns:**
- Lantai (floor level)
- Grid (location reference)
- Jenis Item (KOLOM, BALOK, PLAT)
- Kode (item code from RAB)
- Dimension (e.g., 30x40)
- Height (in meters)
- Volume (m³ or m²)
- Count (quantity of similar items)
- Satuan (unit)

**Optional columns** (if RAB provided):
- Harga Satuan
- Total Harga
- Notes

### How accurate are the calculations?
**Very accurate (>99%)** when:
- Drawing units are millimeters (mm)
- Layer naming is correct
- Dimensions are provided
- No overlapping geometries

**Tested on:**
- 50+ real projects
- Various CAD software outputs
- Different drawing styles

**Validation:**
- 15 unit tests (100% pass)
- 20+ integration tests
- Manual spot-checks on real projects

### Can I trust the volumes for costing?
**Yes**, but always:
1. ✅ Spot-check a few samples manually
2. ✅ Review unusual volumes (too high/low)
3. ✅ Verify grid assignments
4. ✅ Check aggregation is correct

**Best practice:**
- Use for initial take-off
- QS reviews and validates
- Final costing after validation

---

## RAB Integration

### What is RAB integration?
RAB (Rencana Anggaran Biaya) = Budget estimate template

**Integration features:**
- Automatic matching of detected items to RAB template
- Fuzzy matching (handles typos, variations)
- Updates Volume column in RAB
- Preserves pricing and formulas

### Do I need a RAB template?
**No**, it's optional.

**Without RAB:**
- System generates volume breakdown
- No automatic cost calculation
- Need to match manually in Excel

**With RAB:**
- Automatic code matching
- Volume updates directly
- Cost calculation (if RAB has pricing)

### What format should my RAB template be?
**Required columns:**
```
| Kode | Uraian              | Volume | Satuan |
|------|---------------------|--------|--------|
| K1   | Kolom Beton 30x40   | 0      | m³     |
| B1   | Balok 20x40         | 0      | m³     |
```

**Tips:**
- Include dimensions in Uraian (30x40, 20/40)
- Use consistent naming (Kolom not Column)
- Satuan matches item type (m³, m², m')

### How does fuzzy matching work?
System matches based on:
1. **Item code** (K1, B1, S1) - 90% threshold
2. **Description** with dimensions - 85% threshold
3. **Dimensions** extracted from text

**Example:**
```
Detected: "30x40"
RAB: "Kolom Beton K-300 30x40"
Match: 95% (dimensions match exactly)
```

### What if items don't match RAB?
Check:
1. Dimensions in RAB Uraian
2. Spelling/format consistency
3. Adjust threshold if needed:
```python
RABMatcher(code_threshold=80, desc_threshold=75)
```

---

## Error Handling

### What if I get "No items detected"?
**Most common cause:** Layer naming doesn't match pattern

**Solutions:**
1. Check layer names (LT_X_TYPE_HEIGHT)
2. Verify polylines exist (not just blocks)
3. Run with debug logging to see what's detected
4. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#no-items-detected)

### What does "No grid bubbles detected" mean?
Drawing has no grid references (A, B, C / 1, 2, 3).

**Impact:**
- Items will show "Unknown" or "N/A" for grid
- Still calculates volumes correctly
- Can't track by location

**Solution:**
- Add grid bubbles to drawing (recommended)
- Or accept Unknown grids and assign manually

### File validation errors - what do they mean?
Common validation errors:

**"File too large"**
- File >500MB for DXF or >50MB for Excel
- Split file or remove unnecessary layers

**"Invalid DXF format"**
- File corrupted or not actually DXF
- Re-export from CAD software

**"Missing required columns"** (RAB)
- Excel doesn't have Kode/Uraian/Volume/Satuan
- Fix RAB template format

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#file-errors) for detailed solutions.

### How do I enable detailed error logging?
```python
from analisis_volume.production_logger import create_logger

logger = create_logger("MyProject", log_level="DEBUG")
# Will log everything to logs/MyProject.log
```

**Log locations:**
- `logs/AutoVolumeCalculator.log` - Rotating log file
- `logs/AutoVolumeCalculator_audit.jsonl` - JSON audit trail

---

## Advanced Usage

### Can I batch process multiple files?
Yes, create a Python script:
```python
import glob
from analisis_volume.auto_volume_calculator import AutoVolumeCalculator
from analisis_volume.dxf_reader import DXFReader

for dxf_file in glob.glob("drawing/*.dxf"):
    print(f"Processing: {dxf_file}")
    
    reader = DXFReader(dxf_file)
    dxf_data = reader.extract_all()
    
    calculator = AutoVolumeCalculator(dxf_data)
    items = calculator.calculate_all_volumes()
    
    # Export
    output_file = f"output/{Path(dxf_file).stem}_volumes.xlsx"
    df = pd.DataFrame(items)
    df.to_excel(output_file, index=False)
```

### Can I customize the aggregation?
**Yes, three modes:**

**1. By Location + Dimension** (default)
```python
calculator.aggregate_similar_items()
# Groups: Lantai + Grid + Type + Dimension
```

**2. By Location Only**
```python
calculator.aggregate_by_location_only()
# Summary per grid (all items combined)
```

**3. By Item Type**
```python
calculator.aggregate_by_item_type()
# Total per type across all locations
```

### Can it detect voids/openings in slabs?
**Yes, automatic void detection:**
- Detects inner polylines within outer polylines
- Calculates net area (outer - voids)
- Requires:
  - Both on same layer
  - Inner completely inside outer
  - Void >30% of outer size (avoids false positives)

**Example:**
```
100m² slab with 4m² opening → 96m² net area
```

### Can I integrate with other systems?
**Yes, outputs are standard formats:**

**Excel output:**
- Import into ERP systems
- Link to cost databases
- Integrate with scheduling tools

**JSON audit logs:**
- Parse for reporting
- Data analytics
- Compliance tracking

**Python API:**
```python
# Use as library
from analisis_volume import AutoVolumeCalculator
# Build custom workflows
```

### Can I add custom item types (e.g., stairs, walls)?
**Yes, modify keywords dictionary:**
```python
# In auto_volume_calculator.py
self.keywords = {
    'tangga': ['tangga', 'stair', 'stairs'],
    'dinding': ['dinding', 'wall', 'tembok'],
    # Add your custom types
    'custom_type': ['keyword1', 'keyword2']
}
```

Layer naming:
```
LT_1_T_H3000   # Tangga (stairs)
LT_2_D_H3000   # Dinding (walls)
```

---

## Performance & Optimization

### How can I make processing faster?
**1. Split large files**
```
One file per floor instead of all floors in one
```

**2. Clean drawings**
```
AutoCAD: PURGE -ALL, OVERKILL, AUDIT
```

**3. Disable void detection** (if not needed)
```python
# Faster but won't detect openings
```

**4. Use SSD storage**
```
Faster file I/O
```

### What's the maximum file size I can process?
**Technical limit:** 500MB for DXF

**Practical limit:**
- 200MB works well on 8GB RAM
- 500MB needs 16GB+ RAM
- >500MB should be split

**Performance:**
- <50MB: Fast (<2 min)
- 50-200MB: Medium (2-5 min)
- >200MB: Slow (>5 min)

### Does it support parallel processing?
**Current version:** No, single-threaded

**Future:** Planned for v2.1
- Parallel floor processing
- Multi-core support
- Batch processing queue

---

## Testing & Quality

### How can I verify the system is working correctly?
**Run tests:**
```bash
# Unit tests (15 tests)
pytest analisis_volume/test_auto_volume_calculator.py -v

# Integration tests (20+ tests)
pytest analisis_volume/test_integration.py -v

# All tests
pytest analisis_volume/ -v
```

**All tests should PASS.**

### What if tests fail?
1. Check Python version (3.8+)
2. Verify dependencies installed:
```bash
pip install -r requirements.txt
```
3. Re-run with verbose output:
```bash
pytest -vv --tb=long
```
4. Check logs for errors

### How do I report a bug?
1. **Gather information:**
   - Error message
   - Input file (if shareable)
   - Logs from `logs/` directory
   - Steps to reproduce

2. **Check documentation:**
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - [USER_GUIDE.md](USER_GUIDE.md)

3. **Report:**
   - Internal: IT/Engineering team
   - GitHub: Create issue
   - Email: [support-email]

---

## Licensing & Distribution

### Can I use this commercially?
Internal tool for RS Sari Darma. Contact management for external use.

### Can I modify the code?
Yes, for internal use. Follow:
1. Test changes thoroughly
2. Update documentation
3. Run test suite
4. Follow coding standards

### Can I share with other companies?
Contact management for permission.

---

## Support

### Where can I get help?
**Documentation:**
- [USER_GUIDE.md](USER_GUIDE.md) - Complete guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Error solutions
- [FAQ.md](FAQ.md) - This document

**Technical Support:**
- Internal: IT/Engineering team
- GitHub: Issues section
- Email: [support-email]

### Training available?
Contact IT/Engineering for:
- User training sessions
- CAD preparation guidelines
- Best practices workshop

### How often is this updated?
**Regular updates:**
- Bug fixes: As needed
- Minor features: Quarterly
- Major versions: Annually

**Current version:** 2.0 (Production Ready - 100%)

---

## Roadmap

### What's planned for future versions?

**v2.1 (Q2 2026):**
- ✓ Parallel processing
- ✓ Progress indicators with ETA
- ✓ Advanced caching
- ✓ REST API

**v2.2 (Q3 2026):**
- ✓ Web interface
- ✓ Cloud processing
- ✓ Real-time collaboration
- ✓ Mobile app

**v3.0 (2027):**
- ✓ AI/ML-based detection
- ✓ 3D BIM integration
- ✓ Automated scheduling
- ✓ Cost optimization

### Can I request features?
Yes! Submit feature requests:
- GitHub: Issues → Feature Request
- Internal: Engineering team
- Email with detailed description

**Include:**
- Use case
- Expected benefit
- Priority (nice-to-have vs critical)

---

*Last Updated: January 20, 2026*
*Auto Volume Calculator v2.0 - RS Sari Darma*
