# 📚 INDEX FILE - SISTEM ANALISIS VOLUME RS SARI DARMA

Selamat datang! File ini akan membantu Anda menemukan file yang Anda butuhkan.

---

## 🚀 MULAI CEPAT (Quick Start)

**Jika Anda pengguna baru, mulai dari sini:**

1. 📄 **[QUICK_START.txt](QUICK_START.txt)** ← BACA INI DULU!
   - Panduan 3 langkah mudah
   - Cocok untuk pemula
   - Visual dan mudah dipahami

2. 🖱️ **[GENERATE_TEMPLATE.bat](GENERATE_TEMPLATE.bat)** ← KLIK FILE INI
   - Generate template Excel
   - Double-click untuk jalankan

3. 📝 **Isi template yang sudah dibuat**
   - Buka: `Volume_dari_Gambar_TEMPLATE.xlsx`
   - Lihat panduan di sheet PANDUAN
   - Simpan sebagai: `Volume_dari_Gambar.xlsx`

4. 🖱️ **[RUN_ANALISIS.bat](RUN_ANALISIS.bat)** ← KLIK FILE INI
   - Jalankan analisis perbandingan
   - Double-click untuk jalankan

---

## 📖 DOKUMENTASI

### Untuk Pemula
- 📄 **[QUICK_START.txt](QUICK_START.txt)** - Panduan cepat 3 langkah
- 📊 **[DIAGRAM_SISTEM.txt](DIAGRAM_SISTEM.txt)** - Diagram visual sistem

### Untuk User Biasa
- 📗 **[RANGKUMAN_SISTEM.md](RANGKUMAN_SISTEM.md)** - Overview lengkap sistem
- 📘 **[README.md](README.md)** - Dokumentasi detail

### Untuk Developer
- 📂 **[analisis_volume/](analisis_volume/)** - Source code
- 🐍 **[run_analisis_volume.py](run_analisis_volume.py)** - Main script

---

## 📁 FILE STRUKTUR

### ⭐ File Eksekusi (Untuk Dijalankan)
```
🖱️ GENERATE_TEMPLATE.bat       ← Klik untuk buat template
🖱️ RUN_ANALISIS.bat            ← Klik untuk analisis
🐍 run_analisis_volume.py      ← Python main script
```

### 📊 File Data (Input/Output)
```
📊 Volume_dari_Gambar_TEMPLATE.xlsx   ← Template kosong
📊 Volume_dari_Gambar.xlsx            ← Data Anda (buat sendiri)
📊 LAPORAN_PERBANDINGAN_VOLUME.xlsx   ← Hasil analisis
```

### 📖 File Dokumentasi
```
📄 INDEX.md                     ← File ini (navigasi)
📄 QUICK_START.txt             ← Panduan cepat
📄 README.md                   ← Dokumentasi lengkap
📄 RANGKUMAN_SISTEM.md         ← Overview sistem
📄 DIAGRAM_SISTEM.txt          ← Diagram alur
```

### 🐍 File Python (Source Code)
```
📁 analisis_volume/
   ├── __init__.py                    ← Init module
   ├── template_generator.py          ← Generator template
   ├── rab_reader.py                  ← Pembaca RAB
   ├── volume_comparator.py           ← Engine perbandingan
   ├── dwg_reader.py                  ← Pembaca DWG (optional)
   ├── dwg_converter.py               ← Converter DWG (optional)
   └── panduan_konversi.py            ← Panduan konversi DWG
```

### 📁 File Data Project
```
📁 drawing/
   ├── ars/                    ← Gambar arsitektur
   ├── str/                    ← Gambar struktur
   └── mep/                    ← Gambar MEP

📁 rab/
   ├── ars/                    ← RAB arsitektur
   ├── str/                    ← RAB struktur
   └── mep/                    ← RAB MEP
```

---

## 🎯 BERDASARKAN TUJUAN

### Saya ingin MULAI MENGGUNAKAN sistem
→ Baca: [QUICK_START.txt](QUICK_START.txt)
→ Jalankan: [GENERATE_TEMPLATE.bat](GENERATE_TEMPLATE.bat)

### Saya ingin MEMAHAMI cara kerja sistem
→ Baca: [RANGKUMAN_SISTEM.md](RANGKUMAN_SISTEM.md)
→ Lihat: [DIAGRAM_SISTEM.txt](DIAGRAM_SISTEM.txt)

### Saya ingin DETAIL TEKNIS lengkap
→ Baca: [README.md](README.md)
→ Lihat: [analisis_volume/](analisis_volume/) source code

### Saya mengalami MASALAH
→ Baca: [README.md](README.md) bagian Troubleshooting
→ Baca: [RANGKUMAN_SISTEM.md](RANGKUMAN_SISTEM.md) bagian Troubleshooting

### Saya ingin MODIFIKASI sistem
→ Baca: [README.md](README.md) bagian System Architecture
→ Edit: [analisis_volume/](analisis_volume/) files

---

## 📋 CHECKLIST PENGGUNAAN

Sebelum mulai, pastikan:
- [ ] Python 3.7+ terinstall
- [ ] Library terinstall (pandas, openpyxl)
- [ ] File RAB tersedia
- [ ] Gambar DED tersedia

Saat menggunakan:
- [ ] Template sudah di-generate
- [ ] Data volume sudah diisi
- [ ] File disimpan dengan nama yang benar
- [ ] Script analisis dijalankan
- [ ] Laporan diperiksa

---

## 🔍 CARI FILE BERDASARKAN FUNGSI

| Fungsi | File |
|--------|------|
| Generate template Excel | [GENERATE_TEMPLATE.bat](GENERATE_TEMPLATE.bat) |
| Jalankan analisis | [RUN_ANALISIS.bat](RUN_ANALISIS.bat) |
| Template kosong | Volume_dari_Gambar_TEMPLATE.xlsx |
| Input data (Anda isi) | Volume_dari_Gambar.xlsx |
| Hasil analisis | LAPORAN_PERBANDINGAN_VOLUME.xlsx |
| Panduan cepat | [QUICK_START.txt](QUICK_START.txt) |
| Dokumentasi lengkap | [README.md](README.md) |
| Overview sistem | [RANGKUMAN_SISTEM.md](RANGKUMAN_SISTEM.md) |
| Diagram visual | [DIAGRAM_SISTEM.txt](DIAGRAM_SISTEM.txt) |
| Source code | [analisis_volume/](analisis_volume/) |

---

## ❓ FAQ CEPAT

**Q: File mana yang harus dibuka pertama kali?**
A: [QUICK_START.txt](QUICK_START.txt)

**Q: Bagaimana cara menjalankan sistem?**
A: Double-click [GENERATE_TEMPLATE.bat](GENERATE_TEMPLATE.bat), isi template, lalu double-click [RUN_ANALISIS.bat](RUN_ANALISIS.bat)

**Q: Di mana hasil analisisnya?**
A: File `LAPORAN_PERBANDINGAN_VOLUME.xlsx` akan otomatis dibuat

**Q: Saya tidak paham Python, bisa pakai sistem ini?**
A: Bisa! Cukup double-click file .bat, tidak perlu coding

**Q: Bagaimana cara input data volume?**
A: Isi file Excel `Volume_dari_Gambar.xlsx` (ada panduan lengkap di sheet PANDUAN)

---

## 🎨 WARNA DALAM LAPORAN

🟢 **HIJAU** = OK, volume sesuai (selisih < 5%)
🟡 **KUNING** = Review, selisih kecil (5-10%)
🔴 **MERAH** = Warning, selisih besar atau item hilang (> 10%)

---

## 📞 BANTUAN

Jika masih bingung:
1. Baca [QUICK_START.txt](QUICK_START.txt) lagi
2. Lihat [DIAGRAM_SISTEM.txt](DIAGRAM_SISTEM.txt) untuk visual
3. Baca bagian Troubleshooting di [README.md](README.md)
4. Hubungi tim IT/Engineering

---

## 🗺️ PETA NAVIGASI DOKUMEN

```
INDEX.md (Anda di sini)
    │
    ├─── Pemula ──────> QUICK_START.txt
    │                   DIAGRAM_SISTEM.txt
    │
    ├─── User ────────> RANGKUMAN_SISTEM.md
    │                   README.md
    │
    └─── Developer ───> README.md (Technical)
                        analisis_volume/ (Source)
```

---

## ✅ NEXT STEPS

1. **Pahami sistem**: Baca [QUICK_START.txt](QUICK_START.txt)
2. **Generate template**: Jalankan [GENERATE_TEMPLATE.bat](GENERATE_TEMPLATE.bat)
3. **Isi data**: Buka template, isi berdasarkan gambar DED
4. **Analisis**: Jalankan [RUN_ANALISIS.bat](RUN_ANALISIS.bat)
5. **Review hasil**: Buka `LAPORAN_PERBANDINGAN_VOLUME.xlsx`

---

## 📊 STATISTIK PROJECT

- **Total File Python**: 7 files
- **Total Dokumentasi**: 5 files
- **Total Batch Scripts**: 2 files
- **Lines of Code**: ~2000+ lines
- **Fitur**: 6 major features
- **Categories**: 3 (Struktur, Arsitektur, MEP)

---

**Selamat menggunakan Sistem Analisis Volume!**

Jika Anda membaca file ini, artinya Anda di jalur yang benar! 🎉

Mulai dari [QUICK_START.txt](QUICK_START.txt) untuk memulai perjalanan Anda.

---

*Developed for RS Sari Dharma Project - January 2026*
