"""
DXF File Scanner & Auto Selector
Scan folder drawing/dxf/ dan auto-select file DXF untuk processing
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


class DXFScanner:
    """Scanner untuk mencari file DXF di folder standar"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.dxf_folder = self.base_dir / 'drawing' / 'dxf'
        
    def scan_dxf_files(self) -> Dict[str, List[str]]:
        """Scan semua file DXF di folder drawing/dxf/"""
        dxf_files = {
            'str': [],
            'ars': [],
            'mep': [],
            'all': []
        }
        
        if not self.dxf_folder.exists():
            print(f"⚠ Folder DXF tidak ditemukan: {self.dxf_folder}")
            return dxf_files
        
        # Scan each category folder
        for category in ['str', 'ars', 'mep']:
            category_folder = self.dxf_folder / category
            if category_folder.exists():
                files = list(category_folder.glob('*.dxf'))
                dxf_files[category] = [str(f) for f in files]
                dxf_files['all'].extend(dxf_files[category])
        
        return dxf_files
    
    def get_latest_dxf(self, category: str = None) -> Optional[str]:
        """Get file DXF terbaru (by modified time)"""
        dxf_files = self.scan_dxf_files()
        
        if category:
            files = dxf_files.get(category, [])
        else:
            files = dxf_files['all']
        
        if not files:
            return None
        
        # Sort by modification time (newest first)
        files_with_time = [(f, os.path.getmtime(f)) for f in files]
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        return files_with_time[0][0]
    
    def list_all_dxf(self) -> None:
        """Print semua file DXF yang ditemukan"""
        dxf_files = self.scan_dxf_files()
        
        print("\n" + "="*70)
        print("SCAN HASIL FILE DXF")
        print("="*70)
        
        total = 0
        for category in ['str', 'ars', 'mep']:
            files = dxf_files[category]
            if files:
                print(f"\n📁 {category.upper()} ({len(files)} files):")
                for idx, file in enumerate(files, 1):
                    filename = Path(file).name
                    size = os.path.getsize(file) / 1024  # KB
                    modified = os.path.getmtime(file)
                    from datetime import datetime
                    mod_time = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')
                    print(f"  {idx}. {filename} ({size:.1f} KB) - {mod_time}")
                total += len(files)
        
        if total == 0:
            print("\n⚠ Tidak ada file DXF ditemukan!")
            print(f"\nSilakan copy file DXF ke folder:")
            print(f"  - Struktur: {self.dxf_folder / 'str'}")
            print(f"  - Arsitektur: {self.dxf_folder / 'ars'}")
            print(f"  - MEP: {self.dxf_folder / 'mep'}")
        else:
            print(f"\n✓ Total: {total} file DXF ditemukan")
        
        print("="*70)
    
    def select_dxf_interactive(self) -> Optional[str]:
        """Interactive selection untuk memilih file DXF"""
        dxf_files = self.scan_dxf_files()
        
        all_files = []
        for category in ['str', 'ars', 'mep']:
            for file in dxf_files[category]:
                all_files.append((category, file))
        
        if not all_files:
            print("\n⚠ Tidak ada file DXF ditemukan!")
            return None
        
        print("\n" + "="*70)
        print("PILIH FILE DXF")
        print("="*70)
        
        for idx, (category, file) in enumerate(all_files, 1):
            filename = Path(file).name
            print(f"{idx}. [{category.upper()}] {filename}")
        
        print("="*70)
        
        try:
            choice = input(f"\nPilih file (1-{len(all_files)}) atau Enter untuk file terbaru: ").strip()
            
            if not choice:
                # Auto select latest
                latest = self.get_latest_dxf()
                print(f"✓ Auto-selected (terbaru): {Path(latest).name}")
                return latest
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(all_files):
                selected = all_files[choice_num - 1][1]
                print(f"✓ Selected: {Path(selected).name}")
                return selected
            else:
                print("✗ Pilihan tidak valid!")
                return None
                
        except ValueError:
            print("✗ Input tidak valid!")
            return None
        except KeyboardInterrupt:
            print("\n✗ Dibatalkan oleh user")
            return None


def main():
    """Test scanner"""
    scanner = DXFScanner()
    scanner.list_all_dxf()
    
    if scanner.scan_dxf_files()['all']:
        print("\n" + "="*70)
        print("TEST AUTO-SELECT")
        print("="*70)
        
        latest = scanner.get_latest_dxf()
        if latest:
            print(f"✓ Latest DXF: {Path(latest).name}")
        
        latest_str = scanner.get_latest_dxf('str')
        if latest_str:
            print(f"✓ Latest Struktur DXF: {Path(latest_str).name}")


if __name__ == "__main__":
    main()
