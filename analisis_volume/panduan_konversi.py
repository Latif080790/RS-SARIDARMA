"""
Panduan Lengkap: Cara Memproses File DWG untuk Analisis Volume
"""

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║        PANDUAN KONVERSI FILE DWG UNTUK ANALISIS VOLUME                  ║
╚══════════════════════════════════════════════════════════════════════════╝

File DWG yang Anda miliki menggunakan format binary AutoCAD yang memerlukan
konversi ke DXF untuk dapat dianalisis oleh script Python.

┌──────────────────────────────────────────────────────────────────────────┐
│ OPSI 1: KONVERSI MENGGUNAKAN AUTOCAD (Paling Akurat)                    │
└──────────────────────────────────────────────────────────────────────────┘

Jika Anda memiliki AutoCAD terinstall:

1. Buka file: 20251108_Plan RS Sari Dharma.dwg di AutoCAD
2. Ketik perintah: DXFOUT (atau File > Save As > AutoCAD DXF)
3. Pilih lokasi: drawing/ars/
4. Nama file: 20251108_Plan RS Sari Dharma.dxf
5. Version: AutoCAD 2018 DXF
6. Save

┌──────────────────────────────────────────────────────────────────────────┐
│ OPSI 2: ODA FILE CONVERTER (Gratis, Tanpa AutoCAD)                      │
└──────────────────────────────────────────────────────────────────────────┘

Download ODA File Converter (Gratis):
https://www.opendesign.com/guestfiles/oda_file_converter

Langkah-langkah:
1. Install ODA File Converter
2. Jalankan aplikasi
3. Input folder: d:\\2. NATA_PROJECTAPP\\Github_RS.Sari Darma\\RS-SARIDARMA\\drawing\\ars
4. Output folder: (sama dengan input)
5. Output version: ACAD 2018 DXF
6. Recursive: No
7. Audit: Yes
8. Click "Convert"

┌──────────────────────────────────────────────────────────────────────────┐
│ OPSI 3: ONLINE CONVERTER (Cepat tapi perlu internet)                    │
└──────────────────────────────────────────────────────────────────────────┘

Website yang bisa digunakan:
• https://convertio.co/dwg-dxf/
• https://www.zamzar.com/convert/dwg-to-dxf/
• https://cloudconvert.com/dwg-to-dxf

Langkah:
1. Upload file DWG
2. Pilih convert to DXF
3. Download hasil
4. Simpan di folder: drawing/ars/

┌──────────────────────────────────────────────────────────────────────────┐
│ OPSI 4: ALTERNATIF - INPUT MANUAL DARI GAMBAR (Akurat 100%)             │
└──────────────────────────────────────────────────────────────────────────┘

Jika konversi sulit, saya bisa buatkan template Excel untuk input manual:
1. Buka gambar DWG di viewer (bisa pakai DWG TrueView - gratis dari Autodesk)
2. Input data volume ke Excel template yang saya sediakan
3. Script akan membandingkan dengan RAB

Keuntungan:
✓ 100% akurat karena Anda yang membaca gambar
✓ Tidak perlu konversi file
✓ Bisa dilakukan sambil memahami detail gambar

╔══════════════════════════════════════════════════════════════════════════╗
║ REKOMENDASI SAYA: OPSI 4 (Template Excel)                               ║
╚══════════════════════════════════════════════════════════════════════════╝

Saya akan membuatkan:
1. Template Excel untuk input volume dari gambar
2. Panduan lengkap cara membaca dan menghitung volume
3. Script otomatis untuk membandingkan dengan RAB
4. Laporan analisis lengkap dengan grafik

Dengan cara ini:
✓ Anda tetap dapat menganalisis dengan presisi tinggi
✓ Sambil mempelajari detail gambar secara mendalam
✓ Hasil 100% akurat karena dibaca manual
✓ Script akan otomatis menghitung dan membandingkan

APAKAH ANDA MAU SAYA BUATKAN TEMPLATE EXCEL + SCRIPT ANALISIS? (Y/N)

Atau jika Anda berhasil convert ke DXF, simpan dengan nama:
"20251108_Plan RS Sari Dharma.dxf"
di folder yang sama, lalu jalankan script lagi.

""")

import sys
pilihan = input("\nPilihan Anda (1/2/3/4 atau Y untuk template): ").strip().upper()

if pilihan == '4' or pilihan == 'Y':
    print("\n✓ Baik! Saya akan membuatkan sistem template Excel + Script analisis")
    print("  Proses berlanjut ke pembuatan template...")
    sys.exit(0)
else:
    print(f"\n✓ Silakan lakukan konversi dengan opsi {pilihan if pilihan in ['1','2','3'] else '1-3'}")
    print("  Setelah selesai, jalankan kembali script analisis")
    sys.exit(1)
