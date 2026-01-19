# 🚀 QUICK START - Analisis Struktur Detail

## Apa Itu?

Sistem analisis khusus untuk **pekerjaan STRUKTUR** yang lebih detail dan akurat dalam matching item dengan RAB Struktur.

---

## Kenapa Dibutuhkan?

**Problem**: Analisis umum kurang akurat untuk struktur karena:
- Banyak item yang mirip tapi spesifikasi berbeda (K-225 vs K-300, D13 vs D16)
- Volume tidak cocok dengan RAB
- Sulit identifikasi item mana yang hilang
- Tidak tahu dampak biaya dari selisih volume

**Solution**: Sistem analisis khusus dengan:
- ✅ Extract spesifikasi otomatis (K-grade, diameter, dimensi)
- ✅ Matching lebih cerdas (K-300 ≠ K-225!)
- ✅ Hitung dampak biaya
- ✅ Identifikasi gap (item hilang)

---

## 3 Langkah Mudah

### 1️⃣ Persiapan
```
Pastikan file ada:
✓ output/volumes/Volume_dari_Gambar_AUTO.xlsx
  (jalankan 2_AUTO_READ_DXF.bat jika belum ada)
✓ rab/str/BOQ-Dokumen Struktur.xlsx
```

### 2️⃣ Jalankan
```cmd
> 4_ANALISIS_STRUKTUR_DETAIL.bat
```

### 3️⃣ Review
```
Buka: output/reports/STRUKTUR_ANALYSIS_DETAIL_*.xlsx
```

---

## Output: 4 Sheet Excel

### Sheet 1: **Summary** 📊
Ringkasan per kategori:
- TANAH (12 items, 2 missing, cost impact Rp 5.2M)
- BETON (45 items, 3 missing, cost impact Rp 125M)
- PEMBESIAN (38 items, 3 missing, cost impact Rp 45M)
- dll...

### Sheet 2: **Matched Items** ✅
Detail item yang berhasil di-match:
- Item dari gambar vs RAB
- Volume gambar vs RAB
- Selisih (volume dan %)
- Status (OK/MINOR/WARNING/MAJOR)
- **Dampak biaya** (Rp)

### Sheet 3: **Missing in RAB** ❌
Item di gambar tapi **tidak ada di RAB**:
- Ini work yang **tidak masuk budget**
- Perlu ditambahkan ke RAB
- Review dengan QS

### Sheet 4: **RAB Not in Gambar** ⚠️
Item di RAB tapi **tidak di gambar**:
- Mungkin di gambar lain
- Atau sudah dihapus dari design
- Perlu verifikasi

---

## Contoh Output Console

```
================================================================================
DETAILED STRUKTUR ANALYSIS
================================================================================

📊 Data Overview:
   Gambar items: 145
   RAB items: 167
   Similarity threshold: 75%

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

📊 Overall Statistics:
   Total matched: 135
   Items in Gambar not in RAB: 10
   Items in RAB not in Gambar: 32

✅ Detailed report saved: output/reports/STRUKTUR_ANALYSIS_DETAIL_20260120.xlsx
```

---

## Fitur Unggulan

### 1. **Kategorisasi Otomatis**
```
TANAH       → galian, urugan, pemadatan
PONDASI     → tiang pancang, foot plate
BETON       → beton ready mix, plat, sloop
BEKISTING   → formwork, cetakan
PEMBESIAN   → besi, tulangan, wiremesh
BALOK       → beam, ring balk
KOLOM       → column, pilar
DINDING     → wall, shear wall
TANGGA      → stair, bordes
ATAP        → roof, rangka atap
```

### 2. **Extract Spesifikasi**
```
Beton K-300 plat lantai  →  K-grade: 300
Besi D16 balok           →  Diameter: 16
Kolom 40x60              →  Dimensi: 40x60
```

### 3. **Matching Cerdas**
```
❌ K-300 vs K-225  →  Similarity: 30% (BEDA!)
✅ K-300 vs K-300  →  Similarity: 95% (SAMA)
❌ D13 vs D16      →  Similarity: 30% (BEDA!)
✅ D13 vs D13      →  Similarity: 95% (SAMA)
```

### 4. **Status Classification**
```
≤5%    →  ✓ OK          (selisih kecil, wajar)
5-10%  →  ⚠ MINOR       (perlu dicek)
10-25% →  ⚠ WARNING     (selisih lumayan)
>25%   →  ❌ MAJOR      (selisih besar!)
```

### 5. **Cost Impact**
```
Selisih: 5.5 m³
Harga satuan: Rp 2,500,000/m³
Dampak biaya: Rp 13,750,000
```

---

## Tips Penggunaan

### Untuk QS (Quantity Surveyor):
1. **Prioritas**: Buka "Missing in RAB" dulu
   - Item ini perlu masuk budget!
   - Calculate cost and add to contingency
   
2. **Review MAJOR**: Lihat item dengan status "❌ MAJOR"
   - Selisih >25% perlu investigasi
   - Cek apakah ada perubahan design
   
3. **Cost Impact**: Sort by "Dampak_Biaya" (descending)
   - Focus on high-cost differences first
   - Small volume × high price = big impact

### Untuk Engineer:
1. **Check Specs**: Filter "Specs_Match = NO"
   - Verify jika K-grade benar
   - Verify jika diameter besi benar
   
2. **Validate Categories**: Review distribution
   - Apakah semua kategori ada?
   - Missing category = incomplete extraction?
   
3. **Cross-check**: Items in "RAB Not in Gambar"
   - Apakah ada di drawing lain?
   - Atau memang sudah dihapus?

---

## Troubleshooting

### ❓ Matching rate rendah (<70%)
**Solusi**: Reduce threshold
- Edit `struktur_analyzer.py`
- Change line: `min_similarity=0.75` → `min_similarity=0.70`

### ❓ Spesifikasi tidak ke-extract
**Solusi**: Check naming convention
- Harus pakai format standar: K-300, D16, fc 25
- Bukan: beton mutu 300, besi diameter 16mm

### ❓ Kategori salah
**Solusi**: Add keywords
- Edit `CATEGORIES` in `struktur_analyzer.py`
- Tambahkan keyword yang sesuai

---

## FAQ

**Q: Berapa lama prosesnya?**  
A: 30-60 detik untuk ~150 items struktur

**Q: Bisa untuk ARS dan MEP juga?**  
A: Saat ini khusus STRUKTUR. ARS/MEP analyzer coming soon!

**Q: Format RAB harus sama persis?**  
A: Tidak, sistem fleksibel. Cukup ada kolom: PEKERJAAN, VOLUME, UNIT

**Q: Bisa adjust threshold?**  
A: Ya, edit parameter `min_similarity` di code

**Q: Output bisa format lain selain Excel?**  
A: Saat ini Excel only. PDF/HTML export bisa ditambahkan

---

## Next Steps

Setelah review report:

1. **Update RAB**
   - Add missing items from "Missing in RAB"
   - Calculate prices
   - Update budget

2. **Verify Design**
   - Check items with MAJOR difference
   - Verify specs mismatch
   - Coordinate with designer if needed

3. **Document**
   - Save report with proper naming
   - Archive for reference
   - Share with stakeholders

---

## Support

Butuh bantuan?
- 📖 Docs lengkap: `docs/technical/STRUKTUR_ANALYZER_DOCS.md`
- 🔧 Troubleshooting: `docs/user-guides/TROUBLESHOOTING.md`
- ❓ FAQ: `docs/user-guides/FAQ.md`

---

**Version**: 1.0  
**Date**: January 20, 2026  
**Status**: ✅ Production Ready

---

*Happy Analyzing! 🎉*
