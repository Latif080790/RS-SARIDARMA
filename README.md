# Sistem Analisis Volume Pekerjaan
## RS Sari Dharma Project

Sistem otomatis untuk membandingkan volume pekerjaan dari gambar DED dengan RAB (Rencana Anggaran Biaya).

---

## 📋 Fitur

✓ **Template Excel Terstruktur** - Input volume dari gambar dengan panduan lengkap  
✓ **Pembaca RAB Otomatis** - Ekstrak data dari file Excel RAB yang ada  
✓ **Perbandingan Otomatis** - Bandingkan volume gambar vs RAB  
✓ **Laporan Detail** - Excel dengan analisis lengkap dan color-coding  
✓ **Fuzzy Matching** - Deteksi item yang mirip meski nama berbeda  
✓ **Statistik Lengkap** - Ringkasan per kategori (Struktur, Arsitektur, MEP)

---

## 🚀 Cara Penggunaan

### Langkah 1: Generate Template Excel

```bash
python analisis_volume/template_generator.py
```

Akan menghasilkan file: `Volume_dari_Gambar_TEMPLATE.xlsx`

### Langkah 2: Isi Template

1. Buka gambar DED dengan viewer (AutoCAD/DWG TrueView/DraftSight)
2. Buka file template Excel yang baru dibuat
3. Isi data volume mengikuti panduan di sheet "PANDUAN"
4. Ada 3 sheet: STRUKTUR, ARSITEKTUR, MEP
5. **Simpan dengan nama**: `Volume_dari_Gambar.xlsx` (tanpa TEMPLATE)

**Contoh Pengisian:**

| No | Item Pekerjaan | Lokasi | Panjang | Lebar | Tinggi | Jumlah | Satuan | Volume | Rumus |
|----|----------------|--------|---------|-------|--------|--------|--------|--------|-------|
| 1  | Kolom K1 (20x30) | As A1-A5 | 0.20 | 0.30 | 4.00 | 5 | m3 | 1.20 | P×L×T×Jml |
| 2  | Balok B1 (15x25) | As 1-5 | 20.00 | 0.15 | 0.25 | 4 | m3 | 3.00 | P×L×T×Jml |

### Langkah 3: Jalankan Analisis

```bash
python run_analisis_volume.py
```

Akan menghasilkan: `LAPORAN_PERBANDINGAN_VOLUME.xlsx`

---

## 📁 Struktur File

```
RS-SARIDARMA/
│
├── drawing/                          # Folder gambar DED
│   ├── ars/                          # Gambar arsitektur
│   │   └── 20251108_Plan RS Sari Dharma.dwg
│   ├── str/                          # Gambar struktur
│   │   └── Gambar Struktur.pdf
│   └── mep/                          # Gambar MEP
│
├── rab/                              # Folder RAB
│   ├── ars/                          # RAB Arsitektur
│   │   ├── ANALISA VOLUME PEK ARSITEKTUR.xlsx
│   │   └── REKAPITULASI PEMBANGUNAN RSU SARI DHARMA.xlsx
│   ├── str/                          # RAB Struktur
│   │   └── BOQ-Dokumen Struktur.xlsx
│   └── mep/                          # RAB MEP
│       └── RAB MEP RS SARI DARMA 17 APRIL 2025.pdf
│
├── analisis_volume/                  # Script sistem
│   ├── __init__.py
│   ├── template_generator.py        # Generator template
│   ├── rab_reader.py                # Pembaca RAB
│   ├── volume_comparator.py         # Engine perbandingan
│   ├── dwg_reader.py                # Pembaca DWG (optional)
│   └── dwg_converter.py             # Converter DWG (optional)
│
├── run_analisis_volume.py           # ⭐ SCRIPT UTAMA
├── Volume_dari_Gambar_TEMPLATE.xlsx # Template input
├── Volume_dari_Gambar.xlsx          # Data input (Anda isi)
└── LAPORAN_PERBANDINGAN_VOLUME.xlsx # Hasil analisis
```

---

## 📊 Format Laporan

Laporan Excel berisi:

### Sheet RINGKASAN
- Total item per kategori
- Jumlah match, selisih, dan item unik
- Status overall (OK / Perlu Review)

### Sheet STRUKTUR / ARSITEKTUR / MEP
- Item dari gambar vs RAB
- Volume perbandingan
- Selisih (absolut dan %)
- Status dengan color-coding:
  - 🟢 Hijau: MATCH (selisih < 5%)
  - 🟡 Kuning: SELISIH KECIL (5-10%)
  - 🔴 Merah: SELISIH BESAR (>10%) atau item tidak ditemukan

---

## 🔍 Status Perbandingan

| Status | Deskripsi | Action |
|--------|-----------|--------|
| **MATCH** | Volume gambar = RAB (toleransi 5%) | ✓ OK |
| **SELISIH KECIL** | Selisih 5-10% | Review jika perlu |
| **SELISIH BESAR** | Selisih > 10% | ⚠ Perlu investigasi |
| **HANYA DI GAMBAR** | Ada di gambar, tidak di RAB | ⚠ Item mungkin terlupakan di RAB |
| **HANYA DI RAB** | Ada di RAB, tidak di gambar | ⚠ Item mungkin tidak tergambar |

---

## 📖 Tips Membaca Gambar DED

### 1. Persiapan
- Gunakan viewer yang bisa zoom dan measure
- Print/screenshot gambar detail jika perlu
- Siapkan kalkulator

### 2. Identifikasi Layer
- Layer KOLOM → Item kolom
- Layer BALOK → Item balok
- Layer DINDING → Item dinding
- dst.

### 3. Baca Dimensi
- Perhatikan skala gambar
- Baca dimensi dari gambar potongan
- Check tabel/schedule jika ada
- Lihat detail untuk spesifikasi

### 4. Hitung Jumlah
- Hitung manual item yang sejenis
- Perhatikan as/grid untuk lokasi
- Check semua lantai/elevasi

### 5. Rumus Volume Umum
```
Beton (m³)    = Panjang × Lebar × Tinggi × Jumlah
Dinding (m²)  = Panjang × Tinggi × Jumlah
Lantai (m²)   = Panjang × Lebar
Pipa (m)      = Panjang total
Pintu (unit)  = Jumlah
```

---

## 🛠️ Requirements

```
Python 3.7+
pandas
openpyxl
ezdxf (optional, untuk baca DWG langsung)
```

Install dengan:
```bash
pip install pandas openpyxl ezdxf
```

Atau jika menggunakan virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install pandas openpyxl ezdxf
```

---

## ❓ FAQ

### Q: File DWG tidak bisa dibaca?
**A:** File DWG binary perlu dikonversi ke DXF dulu. Gunakan:
- AutoCAD (File > Save As > DXF)
- ODA File Converter (gratis)
- Online converter

Atau gunakan template Excel untuk input manual (lebih akurat).

### Q: Item tidak ter-match di RAB?
**A:** Script menggunakan fuzzy matching. Pastikan nama item konsisten. Misal:
- Gambar: "Kolom K1 (20×30)"
- RAB: "Kolom 20/30"
- Akan ter-match dengan similarity tinggi

### Q: Hasil volume berbeda jauh?
**A:** Check:
1. Satuan konsisten? (m vs cm)
2. Jumlah item sudah benar?
3. Dimensi sudah sesuai gambar?
4. Ada item yang overlap?

### Q: Bisa untuk proyek lain?
**A:** Ya! Template bersifat generic. Tinggal sesuaikan item pekerjaan.

---

## 📝 Catatan Penting

⚠️ **Volume dari template adalah hasil pembacaan manual dari gambar, bukan perhitungan otomatis dari file DWG**

✓ Keuntungan pendekatan ini:
- 100% akurat karena dibaca manual
- Anda memahami detail gambar dengan baik
- Tidak tergantung format DWG
- Fleksibel untuk berbagai jenis gambar

✓ Script otomatis akan:
- Bandingkan dengan RAB
- Deteksi selisih dan item yang hilang
- Generate laporan lengkap dengan visualisasi

---

## 👨‍💻 Support

Jika ada pertanyaan atau masalah:
1. Check file README ini
2. Lihat sheet PANDUAN di template
3. Review error message di terminal
4. Hubungi tim IT/Engineering

---

## 📅 Version History

- **v1.0.0** (2026-01-19)
  - Initial release
  - Template generator
  - RAB reader
  - Volume comparator
  - Report generator

---

## 📄 License

Internal use only - RS Sari Dharma Project

---

**Dibuat untuk memudahkan Quality Control volume pekerjaan**
**RS Sari Dharma - 2026**
