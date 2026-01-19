"""
Modul untuk membaca file RAB Excel
Ekstrak data volume, harga, dan item pekerjaan dari RAB yang sudah ada
"""

import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List, Tuple
import re


class RABReader:
    """Class untuk membaca dan mengekstrak data dari file RAB Excel"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = {
            'struktur': [],
            'arsitektur': [],
            'mep': []
        }
        self.summary = {}
        
    def identify_category(self, text: str) -> str:
        """Identifikasi kategori pekerjaan berdasarkan nama item"""
        text_lower = str(text).lower()
        
        struktur_keywords = [
            'beton', 'kolom', 'balok', 'plat', 'sloof', 'pondasi', 'footplate',
            'pembesian', 'bekisting', 'galian', 'urugan', 'rabat', 'ring',
            'k-', 'fc', 'cor', 'foundation', 'structure'
        ]
        
        mep_keywords = [
            'listrik', 'kabel', 'lampu', 'saklar', 'stop kontak', 'panel',
            'plumbing', 'pipa', 'air', 'pompa', 'ac', 'mechanical', 'electrical',
            'sanitair', 'closet', 'wastafel', 'shower', 'kran', 'septictank',
            'exhaust', 'ducting', 'electrical', 'mep'
        ]
        
        for keyword in struktur_keywords:
            if keyword in text_lower:
                return 'struktur'
        
        for keyword in mep_keywords:
            if keyword in text_lower:
                return 'mep'
        
        return 'arsitektur'
    
    def clean_numeric_value(self, value) -> float:
        """Bersihkan nilai numerik dari format Excel"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            # Remove thousand separators and convert
            value_str = str(value).replace(',', '').replace('.', '').strip()
            return float(value_str) if value_str else 0.0
        except:
            return 0.0
    
    def read_excel_generic(self) -> pd.DataFrame:
        """Membaca Excel dengan pendekatan generic"""
        print(f"\n→ Membaca file: {self.filepath}")
        
        try:
            # Try to read all sheets
            excel_file = pd.ExcelFile(self.filepath)
            print(f"  Sheets found: {excel_file.sheet_names}")
            
            all_data = []
            
            for sheet_name in excel_file.sheet_names:
                print(f"\n→ Memproses sheet: {sheet_name}")
                
                try:
                    df = pd.read_excel(self.filepath, sheet_name=sheet_name, header=None)
                    
                    # Find header row (biasanya ada kata 'No', 'Item', 'Volume', dll)
                    header_row = None
                    for idx, row in df.iterrows():
                        row_str = ' '.join([str(cell).lower() for cell in row if pd.notna(cell)])
                        if any(keyword in row_str for keyword in ['no', 'uraian', 'pekerjaan', 'volume', 'satuan']):
                            header_row = idx
                            print(f"  Header ditemukan di baris: {idx + 1}")
                            break
                    
                    if header_row is not None:
                        # Read again with proper header
                        df = pd.read_excel(self.filepath, sheet_name=sheet_name, header=header_row)
                        
                        # Find relevant columns
                        col_mapping = {}
                        for col in df.columns:
                            col_lower = str(col).lower()
                            if any(k in col_lower for k in ['no', 'nomor']):
                                col_mapping['no'] = col
                            elif any(k in col_lower for k in ['uraian', 'pekerjaan', 'item', 'jenis']):
                                col_mapping['item'] = col
                            elif 'volume' in col_lower:
                                col_mapping['volume'] = col
                            elif any(k in col_lower for k in ['satuan', 'unit']):
                                col_mapping['satuan'] = col
                            elif any(k in col_lower for k in ['harga satuan', 'harga/satuan', 'h.satuan']):
                                col_mapping['harga_satuan'] = col
                            elif any(k in col_lower for k in ['jumlah', 'total', 'harga total']):
                                col_mapping['jumlah'] = col
                        
                        print(f"  Kolom teridentifikasi: {list(col_mapping.keys())}")
                        
                        # Extract data
                        for idx, row in df.iterrows():
                            try:
                                if 'item' in col_mapping:
                                    item_name = str(row[col_mapping['item']])
                                    
                                    # Skip if item is empty or looks like header/total
                                    if pd.isna(row[col_mapping['item']]) or \
                                       any(k in item_name.lower() for k in ['total', 'jumlah', 'sub total', 'grand total']):
                                        continue
                                    
                                    volume = self.clean_numeric_value(row[col_mapping.get('volume', 0)])
                                    
                                    # Skip if volume is 0 or nan
                                    if volume == 0:
                                        continue
                                    
                                    item_data = {
                                        'sheet': sheet_name,
                                        'no': str(row[col_mapping.get('no', '')]) if 'no' in col_mapping else '',
                                        'item': item_name,
                                        'volume': volume,
                                        'satuan': str(row[col_mapping.get('satuan', '')]) if 'satuan' in col_mapping else '',
                                        'harga_satuan': self.clean_numeric_value(row[col_mapping.get('harga_satuan', 0)]),
                                        'jumlah': self.clean_numeric_value(row[col_mapping.get('jumlah', 0)]),
                                        'kategori': self.identify_category(item_name)
                                    }
                                    
                                    all_data.append(item_data)
                            
                            except Exception as e:
                                continue
                    
                except Exception as e:
                    print(f"  Warning: Error reading sheet {sheet_name}: {e}")
                    continue
            
            if all_data:
                result_df = pd.DataFrame(all_data)
                print(f"\n✓ Total {len(result_df)} item berhasil diekstrak")
                return result_df
            else:
                print("\n✗ Tidak ada data yang berhasil diekstrak")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"\n✗ Error membaca file: {e}")
            return pd.DataFrame()
    
    def extract_data(self) -> Dict[str, List[Dict]]:
        """Ekstrak data dari file RAB"""
        print("\n" + "="*70)
        print("EKSTRAKSI DATA DARI RAB EXCEL")
        print("="*70)
        
        df = self.read_excel_generic()
        
        if df.empty:
            return self.data
        
        # Group by category
        for category in ['struktur', 'arsitektur', 'mep']:
            category_df = df[df['kategori'] == category]
            self.data[category] = category_df.to_dict('records')
            print(f"\n→ {category.upper()}: {len(category_df)} item")
        
        # Create summary
        self.summary = {
            'total_items': len(df),
            'struktur_items': len(df[df['kategori'] == 'struktur']),
            'arsitektur_items': len(df[df['kategori'] == 'arsitektur']),
            'mep_items': len(df[df['kategori'] == 'mep']),
            'total_volume_struktur': df[df['kategori'] == 'struktur']['volume'].sum(),
            'total_volume_arsitektur': df[df['kategori'] == 'arsitektur']['volume'].sum(),
            'total_volume_mep': df[df['kategori'] == 'mep']['volume'].sum(),
            'total_nilai': df['jumlah'].sum()
        }
        
        print("\n" + "="*70)
        print("RINGKASAN RAB")
        print("="*70)
        print(f"Total Item: {self.summary['total_items']}")
        print(f"  - Struktur: {self.summary['struktur_items']} item")
        print(f"  - Arsitektur: {self.summary['arsitektur_items']} item")
        print(f"  - MEP: {self.summary['mep_items']} item")
        print(f"\nTotal Nilai RAB: Rp {self.summary['total_nilai']:,.0f}")
        print("="*70 + "\n")
        
        return self.data
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        return self.summary
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export semua data ke DataFrame"""
        all_data = []
        for category, items in self.data.items():
            all_data.extend(items)
        return pd.DataFrame(all_data)


if __name__ == "__main__":
    # Test dengan file RAB yang ada
    rab_files = [
        r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA\rab\ars\ANALISA VOLUME PEK  ARSITEKTUR.xlsx",
        r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA\rab\ars\REKAPITULASI PEMBANGUNAN RSU SARI DHARMA.xlsx",
        r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA\rab\str\BOQ-Dokumen Struktur.xlsx"
    ]
    
    for rab_file in rab_files:
        print(f"\n{'='*70}")
        print(f"Testing: {rab_file.split('\\')[-1]}")
        print('='*70)
        
        reader = RABReader(rab_file)
        data = reader.extract_data()
        
        # Show sample data
        if data:
            print("\nContoh data yang berhasil diekstrak:")
            df = reader.export_to_dataframe()
            if not df.empty:
                print(df[['item', 'volume', 'satuan', 'kategori']].head(10))
