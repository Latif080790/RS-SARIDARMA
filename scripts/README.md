# 📂 SCRIPTS FOLDER - BATCH FILES WORKFLOW

## 📋 DAFTAR SCRIPT (BERURUTAN SESUAI WORKFLOW)

### ✅ MAIN WORKFLOW (URUT DARI 1-3):

1. **`1_GENERATE_TEMPLATE_V2.bat`** 
   - **Fungsi:** Generate template Excel V2 (enhanced, 12 kolom)
   - **Output:** `Volume_dari_Gambar_TEMPLATE_V2.xlsx`
   - **Kapan:** Jalankan pertama kali atau saat butuh template baru
   - **Duration:** ~3-5 detik

2. **`2_AUTO_READ_DXF.bat`**
   - **Fungsi:** Auto-scan DXF files → Extract data → Populate Excel
   - **Input:** DXF files di folder `drawing/dxf/` (str/ars/mep)
   - **Output:** `Volume_dari_Gambar_AUTO.xlsx`
   - **Kapan:** Setelah ada DXF files yang sudah di-convert
   - **Duration:** ~10-30 detik (tergantung ukuran DXF)

3. **`3_RUN_ANALISIS.bat`**
   - **Fungsi:** Compare Volume Gambar vs RAB → Generate report
   - **Input:** `Volume_dari_Gambar_AUTO.xlsx` + RAB files di `rab/`
   - **Output:** Report comparison (di folder output)
   - **Kapan:** Setelah auto-read DXF selesai & ada file RAB
   - **Duration:** ~5-15 detik

### 📦 OPTIONAL SCRIPT:

4. **`OPTIONAL_GENERATE_TEMPLATE_V1.bat`**
   - **Fungsi:** Generate template V1 (legacy, 10 kolom)
   - **Output:** `Volume_dari_Gambar_TEMPLATE.xlsx`
   - **Kapan:** Hanya jika butuh backward compatibility
   - **Note:** ⚠️ Tidak recommended, gunakan V2!


## 🔄 COMPLETE WORKFLOW DIAGRAM

```
START
  │
  ├─→ [1] GENERATE_TEMPLATE_V2.bat
  │    │
  │    ├─ Generate: Volume_dari_Gambar_TEMPLATE_V2.xlsx
  │    │   (12 columns: No, Kode, Item, Lantai, Lokasi/Grid, P, L, T, 
  │    │    Jumlah, Satuan, Volume, Metode)
  │    │
  │    └─→ ✅ Template V2 ready!
  │
  │
  ├─→ [USER ACTION] Convert DWG to DXF
  │    │
  │    ├─ Tool: AutoCAD / ODA File Converter
  │    ├─ Format: R2013 DXF (recommended)
  │    └─ Copy to: drawing/dxf/str/ (atau /ars/, /mep/)
  │
  │
  ├─→ [2] AUTO_READ_DXF.bat
  │    │
  │    ├─ Scan folder: drawing/dxf/
  │    ├─ List all DXF files found
  │    ├─ User select file atau auto-select latest
  │    ├─ Extract entities (TEXT, POLYLINE, CIRCLE, etc)
  │    ├─ Calculate volume auto (P × L × T)
  │    ├─ Extract kode (K1, B1, P1, dll)
  │    ├─ Detect lantai from layer
  │    ├─ Extract grid reference (As A1-A4)
  │    └─ Populate to Excel
  │         │
  │         └─→ Output: Volume_dari_Gambar_AUTO.xlsx
  │              (Populated dengan data dari DXF)
  │
  │
  ├─→ [USER ACTION] Prepare RAB files
  │    │
  │    ├─ Copy RAB Excel to: rab/str/ (atau /ars/, /mep/)
  │    └─ Pastikan format sesuai
  │
  │
  └─→ [3] RUN_ANALISIS.bat
       │
       ├─ Read: Volume_dari_Gambar_AUTO.xlsx
       ├─ Read: RAB files dari rab/
       ├─ Compare volumes:
       │   ├─ Match by item name/kode
       │   ├─ Calculate difference
       │   └─ Identify discrepancies
       │
       └─→ Output: Comparison Report
            ├─ Volume dari Gambar vs RAB
            ├─ Selisih (absolute & percentage)
            └─ Highlight yang berbeda signifikan
            
END ✅
```


## 🎯 QUICK START

### First Time Setup:
```batch
1. Buka terminal di folder project
2. Jalankan: scripts\1_GENERATE_TEMPLATE_V2.bat
3. Convert DWG ke DXF, copy ke drawing/dxf/str/ (atau ars/mep)
4. Jalankan: scripts\2_AUTO_READ_DXF.bat
5. Copy RAB Excel ke folder rab/str/ (atau ars/mep)
6. Jalankan: scripts\3_RUN_ANALISIS.bat
```

### Daily Workflow:
```batch
# Jika ada DXF baru:
scripts\2_AUTO_READ_DXF.bat
scripts\3_RUN_ANALISIS.bat

# Jika perlu re-generate template:
scripts\1_GENERATE_TEMPLATE_V2.bat
```


## 📁 FOLDER STRUCTURE (AFTER SCRIPTS CREATED)

```
RS-SARIDARMA/
│
├── scripts/                              ← FOLDER BARU! 🆕
│   ├── 1_GENERATE_TEMPLATE_V2.bat       ← Step 1
│   ├── 2_AUTO_READ_DXF.bat              ← Step 2
│   ├── 3_RUN_ANALISIS.bat               ← Step 3
│   ├── OPTIONAL_GENERATE_TEMPLATE_V1.bat
│   └── README.md                         ← This file
│
├── drawing/
│   ├── dxf/
│   │   ├── str/                         ← Copy DXF struktur here
│   │   ├── ars/                         ← Copy DXF arsitektur here
│   │   └── mep/                         ← Copy DXF MEP here
│   ├── str/                             ← DWG original (struktur)
│   ├── ars/                             ← DWG original (arsitektur)
│   └── mep/                             ← DWG original (MEP)
│
├── rab/
│   ├── str/                             ← Copy RAB struktur here
│   ├── ars/                             ← Copy RAB arsitektur here
│   └── mep/                             ← Copy RAB MEP here
│
├── analisis_volume/                     ← Python modules
│   ├── template_generator.py
│   ├── dxf_scanner.py
│   ├── dxf_to_excel.py
│   ├── auto_volume_calculator.py
│   └── volume_comparator.py
│
└── Volume_dari_Gambar_TEMPLATE_V2.xlsx  ← Generated template
```


## 💡 TIPS & BEST PRACTICES

### 1. File Naming Convention
```
✅ GOOD:
   20251119_RS_Sari_Dharma_Struktur_Lt1.dxf
   20251119_RAB_Struktur_Final.xlsx

❌ BAD:
   gambar.dxf
   rab.xlsx
   untitled.dxf
```

### 2. Workflow Sequence
- ✅ **ALWAYS** jalankan script sesuai urutan: 1 → 2 → 3
- ⚠️ **JANGAN** skip step 1 jika belum ada template V2
- ⚠️ **JANGAN** jalankan step 3 jika step 2 belum selesai

### 3. Error Handling
Jika error muncul:
1. **Check virtual environment:** Pastikan `.venv` exist
2. **Check file locations:** DXF di `drawing/dxf/`, RAB di `rab/`
3. **Check file format:** DXF version R2013, RAB format Excel
4. **Read error message:** Script akan show detail error

### 4. Performance Tips
- DXF file besar (>10MB): ~30-60 detik processing
- Multiple DXF: Process satu-satu, jangan paralel
- RAB file besar: Pastikan hanya ada sheet yang diperlukan

### 5. Backup Strategy
```batch
# Sebelum run script, backup file penting:
copy Volume_dari_Gambar_AUTO.xlsx Volume_dari_Gambar_AUTO_backup.xlsx
```


## 🔧 TROUBLESHOOTING

### Error: "Virtual environment tidak ditemukan"
**Solution:**
```batch
cd "d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA"
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

### Error: "Template tidak ditemukan"
**Solution:**
```batch
cd scripts
1_GENERATE_TEMPLATE_V2.bat
```

### Error: "DXF file tidak ditemukan"
**Solution:**
1. Convert DWG ke DXF menggunakan AutoCAD atau ODA File Converter
2. Copy DXF ke folder: `drawing/dxf/str/` (atau ars/, mep/)
3. Run ulang: `2_AUTO_READ_DXF.bat`

### Error: "RAB file tidak ditemukan"
**Solution:**
1. Copy RAB Excel ke folder: `rab/str/` (atau ars/, mep/)
2. Run ulang: `3_RUN_ANALISIS.bat`

### Processing lambat (>1 menit)
**Possible causes:**
- DXF file terlalu besar (>50MB)
- Banyak entities (>10,000 objects)
- Layer names tidak standard

**Solution:**
- Cleanup DXF: Remove unused layers/blocks
- Simplify drawing: Keep only necessary elements
- Split by floor: Process per lantai


## 📊 OUTPUT FILES

### After Step 1:
- `Volume_dari_Gambar_TEMPLATE_V2.xlsx` (12 columns, 34+ items)

### After Step 2:
- `Volume_dari_Gambar_AUTO.xlsx` (Populated dengan data DXF)

### After Step 3:
- Comparison report (di folder output)
- Highlight selisih Gambar vs RAB


## 🚀 ADVANCED USAGE

### Batch Processing Multiple DXF:
```batch
REM Create custom script untuk loop
FOR %%F IN (drawing\dxf\str\*.dxf) DO (
    echo Processing: %%F
    REM Call dxf_to_excel.py with specific file
)
```

### Custom Template:
```batch
REM Edit template_generator.py untuk customize items
REM Lalu generate ulang dengan 1_GENERATE_TEMPLATE_V2.bat
```

### Integration with CI/CD:
```batch
REM Add to git hooks atau automation pipeline
scripts\2_AUTO_READ_DXF.bat
if errorlevel 1 exit /b 1
scripts\3_RUN_ANALISIS.bat
```


## 📞 SUPPORT

Jika ada masalah atau pertanyaan:
1. Check README.md ini
2. Lihat UPGRADE_LOG_V2.txt untuk technical details
3. Check drawing/dxf/README.md untuk DXF folder guide
4. Lihat error message di terminal


## 📝 CHANGELOG

### 2026-01-19: Scripts Organization
- ✅ Created `scripts/` folder
- ✅ Numbered workflow: 1 → 2 → 3
- ✅ Added README.md dengan complete guide
- ✅ Added navigation: `cd /d "%~dp0.."` di semua script
- ✅ Added "NEXT STEP" guidance di setiap script

### Previous Updates:
- 2026-01-19: DXF folder structure & scanner
- 2026-01-19: Enhanced template V2 (12 columns)
- 2026-01-19: Auto-calculator upgrade (kode/lantai/grid extraction)


═══════════════════════════════════════════════════════════════════════════

              ✅ SCRIPTS ORGANIZED & READY TO USE!

                 Developed by GitHub Copilot
                      January 19, 2026

═══════════════════════════════════════════════════════════════════════════
