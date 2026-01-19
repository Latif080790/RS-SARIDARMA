# 🔧 ANALISIS STRUKTUR DETAIL - Enhanced Structure Analysis

**Created**: January 20, 2026  
**Purpose**: Provide detailed and accurate matching analysis for structural work items

---

## 🎯 Problem Statement

User feedback:
> "Coba lebih detail lagi untuk menganalisa pekerjaan struktur, dari item pekerjaan, dan volume pekerjaan, karena nyatanya masih banyak yg tidak sama dengan RAB Struktur"

**Issue**: The general comparison tool was not matching structural items accurately enough with the RAB Struktur.

---

## ✅ Solution Implemented

### New Module: `struktur_analyzer.py`

A specialized analyzer for structural work with:

#### 1. **Automatic Categorization**
Items are automatically categorized into:
- TANAH (Excavation, backfill, compaction)
- PONDASI (Foundation, pile caps, footings)
- BETON (Concrete, ready mix, slabs)
- BEKISTING (Formwork)
- PEMBESIAN (Reinforcement, rebar)
- BALOK (Beams)
- KOLOM (Columns)
- DINDING (Walls)
- TANGGA (Stairs)
- ATAP (Roof)
- LAIN-LAIN (Others)

#### 2. **Specification Extraction**
Automatically extracts technical specifications:
- **Beton grade**: K-225, K-300, K-350, fc 25, fc 30
- **Rebar diameter**: D10, D13, D16, diameter 19, ø16
- **Dimensions**: 40x60, 30x40, 400x500
- **Thickness**: t=12, tebal 15cm
- **Length**: p=6000, panjang 8m

#### 3. **Smart Matching**
- **Specification-aware**: Compares K-grades, diameters, dimensions
- **Different specs = Different items**: K-225 ≠ K-300, D13 ≠ D16
- **Higher threshold**: 75% minimum similarity (vs 60% in general tool)
- **Spec boost**: Items with matching specs get similarity boost

#### 4. **Detailed Comparison**
For each matched item:
- Volume from Gambar
- Volume from RAB
- Difference (absolute and percentage)
- Status classification:
  - ✓ OK: ≤5% difference
  - ⚠ MINOR: 5-10% difference
  - ⚠ WARNING: 10-25% difference
  - ❌ MAJOR: >25% difference
- Unit price from RAB
- **Cost impact** calculation (volume difference × unit price)

#### 5. **Gap Analysis**
- **Items in Gambar but not in RAB** (missing from budget)
- **Items in RAB but not in Gambar** (not yet constructed/designed)

---

## 📊 Output: Excel Report with 4 Sheets

### Sheet 1: Summary
Category-wise summary showing:
- Total items per category
- Matched items count
- Missing items count
- Major differences count
- **Total cost impact per category**

### Sheet 2: Matched Items
Detailed list of all matched items with:
- Item from Gambar
- Location/Floor
- Volume Gambar vs Volume RAB
- Difference (volume and %)
- Status (OK/MINOR/WARNING/MAJOR)
- Similarity percentage
- Specs match (YES/NO)
- Unit price from RAB
- **Cost impact (Rp)**

### Sheet 3: Missing in RAB
Items found in Gambar but not in RAB:
- These represent work not budgeted
- Potential cost additions
- Need review with QS

### Sheet 4: RAB Not in Gambar
Items in RAB but not in Gambar:
- Work budgeted but not yet designed/extracted
- May need verification
- Could be in different drawings

---

## 🚀 How to Use

### Step 1: Prepare Files
```
Ensure you have:
✓ output/volumes/Volume_dari_Gambar_AUTO.xlsx (from Step 2)
✓ rab/str/BOQ-Dokumen Struktur.xlsx
```

### Step 2: Run Analysis
```batch
# From project root:
4_ANALISIS_STRUKTUR_DETAIL.bat

# Or from scripts/batch/:
cd scripts\batch
4_ANALISIS_STRUKTUR_DETAIL.bat
```

### Step 3: Review Report
```
Output location: output/reports/STRUKTUR_ANALYSIS_DETAIL_[timestamp].xlsx

Open the Excel file and review:
1. Summary sheet - Overall picture
2. Matched Items - Item-by-item comparison
3. Missing in RAB - Items to add to budget
4. RAB Not in Gambar - Items to verify
```

---

## 📋 Example Output

### Console Output:
```
================================================================================
DETAILED STRUKTUR ANALYSIS
================================================================================

📊 Data Overview:
   Gambar items: 145
   RAB items: 167
   Similarity threshold: 75%

📂 Categorizing items...

🔍 Checking for RAB items not in gambar...

================================================================================
SUMMARY BY CATEGORY
================================================================================

📂 TANAH:
   Total items: 12
   Matched: 10
   Missing in RAB: 2
   Major difference: 1
   Total cost impact: Rp 5,250,000

📂 BETON:
   Total items: 45
   Matched: 42
   Missing in RAB: 3
   Major difference: 5
   Total cost impact: Rp 125,000,000

📂 PEMBESIAN:
   Total items: 38
   Matched: 35
   Missing in RAB: 3
   Major difference: 7
   Total cost impact: Rp 45,000,000

...

================================================================================

📊 Overall Statistics:
   Total matched: 135
   Items in Gambar not in RAB: 10
   Items in RAB not in Gambar: 32

✅ Detailed report saved: output/reports/STRUKTUR_ANALYSIS_DETAIL_20260120_143052.xlsx
```

### Excel Report Sample:

**Matched Items Sheet:**
| Kategori | Item_Gambar | Lokasi | Vol_Gambar | Item_RAB | Vol_RAB | Selisih_% | Status | Dampak_Biaya |
|----------|-------------|--------|------------|----------|---------|-----------|---------|--------------|
| BETON | Beton K-300 Plat Lantai | Basement | 125.50 | Plat basement | 120.00 | 4.58% | ✓ OK | 1,452,000 |
| PEMBESIAN | Besi D16 Balok Lt.1 | Lt.1 | 2,450 | Balok D16 | 2,300 | 6.52% | ⚠ MINOR | 2,895,000 |
| BETON | Beton K-350 Kolom | Lt.2 | 85.00 | Kolom K-350 | 75.00 | 13.33% | ⚠ WARNING | 5,280,000 |

---

## 🎯 Key Improvements Over General Tool

| Aspect | General Tool | Struktur Analyzer |
|--------|-------------|-------------------|
| Categorization | Manual | ✅ Automatic (11 categories) |
| Spec Extraction | No | ✅ Yes (K-grade, diameter, etc) |
| Spec Matching | No | ✅ Yes (K-300 ≠ K-225) |
| Threshold | 60% | ✅ 75% (more strict) |
| Cost Impact | No | ✅ Yes (calculated) |
| Gap Analysis | Basic | ✅ Detailed (2-way check) |
| Report Detail | 1-2 sheets | ✅ 4 sheets |

---

## 🔍 Technical Details

### Matching Algorithm

```python
def calculate_similarity(text1, text2, check_specs=True):
    # 1. Extract specifications
    specs1 = extract_specifications(text1)  # K-300, D16, etc
    specs2 = extract_specifications(text2)
    
    # 2. Check if critical specs match
    if specs1 and specs2:
        # If K-grades don't match → Different material!
        if specs1['beton_grade'] != specs2['beton_grade']:
            return 0.3  # Force below threshold
        
        # If diameters don't match → Different rebar!
        if specs1['diameter_besi'] != specs2['diameter_besi']:
            return 0.3  # Force below threshold
    
    # 3. Calculate base similarity
    if text1 in text2 or text2 in text1:
        base_similarity = 0.85
    else:
        base_similarity = SequenceMatcher(text1, text2).ratio()
    
    # 4. Boost if specs match
    if specs match and specs_compared:
        base_similarity += 0.1
    
    return min(1.0, base_similarity)
```

### Category Detection

```python
CATEGORIES = {
    'TANAH': ['galian', 'urugan', 'timbunan', 'pemadatan'],
    'PONDASI': ['pondasi', 'tiang pancang', 'foot plate'],
    'BETON': ['beton', 'cor', 'concrete', 'ready mix', 'plat'],
    'PEMBESIAN': ['besi', 'baja', 'tulangan', 'reinforcement'],
    # ... etc
}

def categorize_item(item_text):
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in item_text.lower():
                return category
    return 'LAIN-LAIN'
```

### Spec Extraction

```python
SPEC_PATTERNS = {
    'beton_grade': r'k-?\s*(\d+)',           # K-225, K300
    'beton_fc': r'fc\s*(\d+)',               # fc 25, fc30
    'diameter_besi': r'd\s*(\d+)|ø\s*(\d+)', # D13, ø16
    'dimensi': r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # 40x60
    'tebal': r't\s*=?\s*(\d+)',              # t=12
}

def extract_specifications(text):
    specs = {}
    for spec_name, pattern in SPEC_PATTERNS.items():
        match = re.search(pattern, text.lower())
        if match:
            specs[spec_name] = match.group(1)
    return specs
```

---

## 📁 Files Created

### New Files:
1. **analisis_volume/struktur_analyzer.py** (400+ lines)
   - Main analyzer class
   - Matching algorithms
   - Report generation

2. **examples/analisis_struktur_detail.py** (100+ lines)
   - Command-line script
   - User interface
   - File validation

3. **scripts/batch/4_ANALISIS_STRUKTUR_DETAIL.bat**
   - Batch file for Windows
   - Easy execution
   - Error handling

4. **4_ANALISIS_STRUKTUR_DETAIL.bat** (root)
   - Root launcher
   - Quick access

5. **STRUKTUR_ANALYZER_DOCS.md** (this file)
   - Complete documentation
   - Usage guide
   - Technical details

---

## 💡 Usage Tips

### For Quantity Surveyors:
1. Focus on "Missing in RAB" sheet first
   - These items need to be added to budget
   - Calculate cost and add to contingency

2. Review "MAJOR" status items in "Matched Items"
   - Verify if volume difference is real
   - Check if there are design changes

3. Check "RAB Not in Gambar" sheet
   - Verify if these items are in other drawings
   - Or if they were removed from design

### For Engineers:
1. Review specification mismatches
   - "Specs_Match = NO" items need attention
   - Verify if K-grade, diameter, etc. are correct

2. Check category distribution
   - Are all work categories represented?
   - Missing categories may indicate incomplete extraction

3. Validate high cost impact items
   - Items with large "Dampak_Biaya" need verification
   - Small volume difference can have large cost impact

---

## 🔧 Troubleshooting

### Issue: Low matching rate

**Solution**:
- Reduce threshold from 75% to 70%
- Edit line in `struktur_analyzer.py`:
  ```python
  results_df = analyzer.match_items(gambar_df, rab_df, min_similarity=0.70)
  ```

### Issue: Specifications not extracted

**Solution**:
- Check item naming in gambar
- Add more patterns to `SPEC_PATTERNS`
- Example: Add SNI patterns, international standards

### Issue: Wrong categorization

**Solution**:
- Review `CATEGORIES` dictionary
- Add more keywords per category
- Check for typos in keywords

---

## 📈 Future Enhancements

Potential improvements:
1. **Machine Learning**: Train model on historical matches
2. **AHSP Integration**: Link items to AHSP (Analisa Harga Satuan Pekerjaan)
3. **3D Visualization**: Show matched/unmatched items in 3D model
4. **Multi-language**: Support English and Indonesian
5. **Auto-correction**: Suggest corrections for mismatches
6. **Historical comparison**: Compare with previous projects

---

## 📞 Support

If you encounter issues:
1. Check console output for errors
2. Verify input file formats
3. Review this documentation
4. Check `TROUBLESHOOTING.md` in docs/user-guides/

---

## ✅ Testing Checklist

Before deploying:
- [ ] Test with sample data
- [ ] Verify all 4 sheets are generated
- [ ] Check category distribution
- [ ] Validate cost impact calculations
- [ ] Review matched items accuracy
- [ ] Verify missing items lists
- [ ] Test with different similarity thresholds

---

*Last Updated: January 20, 2026*  
*Auto Volume Calculator - Struktur Analyzer*  
*Version 1.0*
