# 📁 FOLDER DXF FILES

**Lokasi:** `drawing/dxf/`  
**Fungsi:** Menyimpan file DXF hasil konversi dari DWG untuk auto-processing

---

## 📂 STRUKTUR FOLDER

```
drawing/
├── dxf/              ← SIMPAN FILE DXF DI SINI
│   ├── str/         ← File DXF Struktur
│   ├── ars/         ← File DXF Arsitektur
│   └── mep/         ← File DXF MEP
│
├── ars/             ← File DWG asli (Arsitektur)
├── mep/             ← File DWG asli (MEP)
└── str/             ← File DWG asli (Struktur)
```

---

## 🎯 KENAPA PERLU FOLDER KHUSUS?

### 1. **Organization** 📋
- Pisahkan file DWG (original) dan DXF (converted)
- Mudah manage multiple versions
- Clean folder structure

### 2. **Auto-Detection** 🤖
- Script Python otomatis scan folder ini
- Tidak perlu hardcode path file
- Support multiple files

### 3. **Category Separation** 🗂️
- Struktur (str/)
- Arsitektur (ars/)
- MEP (mep/)

### 4. **Easier Workflow** ⚡
- Tinggal copy DXF ke folder yang sesuai
- Run AUTO_READ_DXF.bat
- System auto-detect dan process

---

## 📥 CARA MENGGUNAKAN

### STEP 1: Convert DWG ke DXF

**Option A: Menggunakan AutoCAD**
```
1. Buka file DWG di AutoCAD
2. File > Save As > AutoCAD DXF (*.dxf)
3. Pilih versi: AutoCAD 2013/LT2013 DXF
4. Save
```

**Option B: Menggunakan ODA File Converter (Gratis)**
```
1. Download: https://www.opendesign.com/guestfiles/oda_file_converter
2. Install dan jalankan
3. Add Files: pilih DWG file
4. Output Format: DXF
5. Output Version: R2013 (Recommended)
6. Convert!
```

### STEP 2: Copy DXF ke Folder yang Sesuai

**Untuk file Struktur:**
```
Copy ke: drawing/dxf/str/
Contoh: drawing/dxf/str/20251108_Plan RS Sari Dharma - Struktur.dxf
```

**Untuk file Arsitektur:**
```
Copy ke: drawing/dxf/ars/
Contoh: drawing/dxf/ars/20251108_Plan RS Sari Dharma - Arsitektur.dxf
```

**Untuk file MEP:**
```
Copy ke: drawing/dxf/mep/
Contoh: drawing/dxf/mep/20251108_Plan RS Sari Dharma - MEP.dxf
```

### STEP 3: Run Auto-Read

```batch
AUTO_READ_DXF.bat
```

System akan:
1. ✅ Scan semua file DXF di folder
2. ✅ Tampilkan list file yang ditemukan
3. ✅ Auto-select file terbaru atau biarkan pilih manual
4. ✅ Process dan populate ke Excel

---

## 🔍 AUTO-SCAN FEATURES

System punya **DXF Scanner** yang otomatis:

### 1. Scan All DXF Files
```python
from analisis_volume.dxf_scanner import DXFScanner

scanner = DXFScanner()
files = scanner.scan_dxf_files()

# Result:
# {
#   'str': ['path/to/struktur1.dxf', 'path/to/struktur2.dxf'],
#   'ars': ['path/to/arsitektur1.dxf'],
#   'mep': [],
#   'all': [... semua file ...]
# }
```

### 2. Get Latest DXF (by modified time)
```python
# Latest dari semua kategori
latest = scanner.get_latest_dxf()

# Latest dari kategori tertentu
latest_str = scanner.get_latest_dxf('str')
latest_ars = scanner.get_latest_dxf('ars')
```

### 3. Interactive Selection
```python
# Tampilkan menu dan biarkan user pilih
selected = scanner.select_dxf_interactive()
```

### 4. List All Files
```python
scanner.list_all_dxf()
```

Output:
```
======================================================================
SCAN HASIL FILE DXF
======================================================================

📁 STR (2 files):
  1. 20251108_Plan RS Sari Dharma - Struktur Lt.1.dxf (2.5 MB) - 2026-01-19 10:30
  2. 20251108_Plan RS Sari Dharma - Struktur Lt.2.dxf (2.3 MB) - 2026-01-19 10:35

📁 ARS (1 files):
  1. 20251108_Plan RS Sari Dharma - Arsitektur.dxf (3.1 MB) - 2026-01-19 09:45

✓ Total: 3 file DXF ditemukan
======================================================================
```

---

## 💡 TIPS & BEST PRACTICES

### 1. Naming Convention
```
✅ GOOD:
- 20251108_Plan RS Sari Dharma - Struktur Lt.1.dxf
- 20251108_Plan RS Sari Dharma - Arsitektur.dxf
- YYYYMMDD_ProjectName - Category.dxf

❌ BAD:
- gambar.dxf
- plan.dxf
- untitled.dxf
```

### 2. File Size
```
✅ Normal: 1-5 MB per file
⚠️ Large: 5-10 MB (might be slow)
❌ Too Large: >10 MB (consider simplify/purge DWG first)
```

### 3. DXF Version
```
✅ Recommended: R2013 / AutoCAD 2013
✅ Also OK: R2010, R2018
⚠️ Avoid: R12 (too old), R2024 (might not support)
```

### 4. Layer Names
```
✅ GOOD (will be auto-detected):
- KOLOM_LT1
- BALOK_BASEMENT
- PLAT_LT2
- DINDING_ARS

❌ BAD (won't be detected):
- Layer0
- Defpoints
- A-WALL-FULL
```

### 5. Keep Original DWG
```
✅ Simpan file DWG asli di drawing/ars/, drawing/str/, drawing/mep/
✅ Jangan overwrite DWG dengan DXF
✅ DXF hanya untuk processing, bukan untuk editing
```

---

## 🔧 TROUBLESHOOTING

### ❌ "Tidak ada file DXF ditemukan"

**Penyebab:**
- File belum di-copy ke folder drawing/dxf/
- File masih format DWG (belum convert)
- Folder path salah

**Solusi:**
```
1. Check apakah file ada di folder:
   - drawing/dxf/str/
   - drawing/dxf/ars/
   - drawing/dxf/mep/

2. Check extension file: HARUS .dxf (bukan .dwg)

3. Check permission folder (read access)
```

### ❌ "Error reading DXF file"

**Penyebab:**
- DXF version terlalu lama/baru
- DXF corrupt
- Format tidak standard

**Solusi:**
```
1. Re-convert DWG ke DXF (gunakan version R2013)
2. Buka DXF di viewer untuk verify
3. Purge DWG sebelum convert (untuk reduce size)
```

### ❌ "Auto-detection tidak akurat"

**Penyebab:**
- Layer names tidak standard
- Dimension text tidak ada
- Gambar terlalu simplified

**Solusi:**
```
1. Check layer names (harus ada keyword: KOLOM, BALOK, PLAT)
2. Pastikan ada text dimension di gambar
3. Manual review dan adjust hasil auto-populate
```

---

## 📊 WORKFLOW LENGKAP

```
┌─────────────────┐
│  DWG Original   │
│  (drawing/ars/) │
└────────┬────────┘
         │
         ▼
    [CONVERT]
         │
         ▼
┌─────────────────┐
│  DXF Converted  │
│  (drawing/dxf/) │  ← YOU ARE HERE
└────────┬────────┘
         │
         ▼
   [AUTO_READ_DXF.bat]
         │
         ├─→ DXF Scanner: Scan & Select File
         ├─→ DXF Reader: Extract Data
         ├─→ Auto Calculator: Calculate Volumes
         └─→ Excel Populator: Populate Template
         │
         ▼
┌─────────────────┐
│  Excel Result   │
│  (with volumes) │
└────────┬────────┘
         │
         ▼
  [Manual Review & Adjust]
         │
         ▼
┌─────────────────┐
│ Final Excel     │
│ Volume_dari_    │
│ Gambar.xlsx     │
└────────┬────────┘
         │
         ▼
   [RUN_ANALISIS.bat]
         │
         ▼
┌─────────────────┐
│ Comparison      │
│ Report with RAB │
└─────────────────┘
```

---

## 📝 CHECKLIST

Sebelum run AUTO_READ_DXF.bat:

- [ ] File DWG sudah di-convert ke DXF
- [ ] File DXF sudah di-copy ke folder yang sesuai (str/ars/mep)
- [ ] File size reasonable (<10 MB)
- [ ] Layer names standard (KOLOM, BALOK, PLAT, dll)
- [ ] Template Excel sudah di-generate (V2)
- [ ] Virtual environment Python sudah aktif

Jika semua ✅, ready to go! 🚀

---

**Last Updated:** 19 Januari 2026  
**Version:** 2.0  
**Related:** AUTO_READ_DXF.bat, dxf_scanner.py, dxf_to_excel.py
