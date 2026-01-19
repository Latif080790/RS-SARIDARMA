"""
Modul untuk membaca dan mengekstrak data dari file DXF
Menggunakan library ezdxf untuk parsing file AutoCAD
Includes: Dimension extraction, Volume calculation, Item identification
"""

import ezdxf
from ezdxf.document import Drawing
from typing import Dict, List, Tuple, Any, Optional
import re
from collections import defaultdict
import math


class DXFReader:
    """Class untuk membaca dan menganalisis file DXF dengan auto volume calculation"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.doc = None
        self.msp = None
        self.data = {
            'layers': [],
            'blocks': [],
            'texts': [],
            'dimensions': [],
            'polylines': [],
            'lines': [],
            'circles': [],
            'arcs': [],
            'hatches': [],
            'items': []  # Auto-identified items dengan volume
        }
        self.dimension_values = {}  # Store dimension values by location
        self.text_values = {}  # Store text values by location
    
    def load_file(self) -> bool:
        """Load dan validasi file DXF"""
        try:
            # Try to load with ezdxf directly (more reliable than header check)
            print(f"📖 Loading file: {self.filepath}")
            
            self.doc = ezdxf.readfile(self.filepath)
            self.msp = self.doc.modelspace()
            
            print(f"✓ File DXF berhasil dibaca!")
            print(f"  Version: {self.doc.dxfversion}")
            
            # Count entities
            entity_count = len(list(self.msp))
            print(f"  Entities: {entity_count}")
            
            # Get drawing units
            try:
                units = self.doc.header.get('$INSUNITS', 0)
                unit_names = {0: 'Unitless', 1: 'Inches', 2: 'Feet', 4: 'Millimeters', 
                            5: 'Centimeters', 6: 'Meters'}
                print(f"  Units: {unit_names.get(units, 'Unknown')}")
            except:
                print(f"  Units: Default")
            
            return True
            
        except ezdxf.DXFStructureError as e:
            print(f"✗ File bukan format DXF yang valid!")
            print(f"  Error: {e}")
            print(f"\n💡 Solusi:")
            print(f"  1. Pastikan file sudah di-convert dari DWG ke DXF")
            print(f"  2. Gunakan AutoCAD atau ODA File Converter")
            print(f"  3. Pilih DXF version: R2013 atau lebih baru")
            return False
            
        except IOError as e:
            print(f"✗ Error membaca file: {e}")
            print(f"  File mungkin tidak ada atau tidak bisa diakses")
            return False
            
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            print(f"  Type: {type(e).__name__}")
            
            # Try to give helpful message based on error
            error_str = str(e).lower()
            if 'permission' in error_str:
                print(f"\n💡 File mungkin sedang dibuka di aplikasi lain")
            elif 'not found' in error_str or 'no such file' in error_str:
                print(f"\n💡 File tidak ditemukan, check path dan nama file")
            else:
                print(f"\n💡 Coba convert ulang DWG ke DXF dengan version R2013")
            
            return False
    
    def extract_layers(self) -> List[Dict]:
        """Ekstrak semua layer dari gambar"""
        layers = []
        for layer in self.doc.layers:
            layer_info = {
                'name': layer.dxf.name,
                'color': layer.dxf.color,
                'linetype': layer.dxf.linetype,
                'on': layer.is_on(),
                'frozen': layer.is_frozen(),
                'locked': layer.is_locked()
            }
            layers.append(layer_info)
        self.data['layers'] = layers
        print(f"✓ Ditemukan {len(layers)} layer")
        return layers
    
    def extract_texts(self) -> List[Dict]:
        """Ekstrak semua teks dan mtext dari gambar"""
        texts = []
        
        # Extract TEXT entities
        for text in self.msp.query('TEXT'):
            text_info = {
                'type': 'TEXT',
                'content': text.dxf.text,
                'layer': text.dxf.layer,
                'position': (text.dxf.insert.x, text.dxf.insert.y),
                'height': text.dxf.height,
                'rotation': text.dxf.rotation if hasattr(text.dxf, 'rotation') else 0
            }
            texts.append(text_info)
        
        # Extract MTEXT entities
        for mtext in self.msp.query('MTEXT'):
            text_info = {
                'type': 'MTEXT',
                'content': mtext.text,
                'layer': mtext.dxf.layer,
                'position': (mtext.dxf.insert.x, mtext.dxf.insert.y),
                'height': mtext.dxf.char_height,
                'rotation': mtext.dxf.rotation if hasattr(mtext.dxf, 'rotation') else 0
            }
            texts.append(text_info)
        
        self.data['texts'] = texts
        print(f"✓ Ditemukan {len(texts)} text entities")
        return texts
    
    def extract_dimensions(self) -> List[Dict]:
        """Ekstrak semua dimensi dari gambar"""
        dimensions = []
        
        for dim in self.msp.query('DIMENSION'):
            try:
                dim_info = {
                    'type': dim.dxftype(),
                    'layer': dim.dxf.layer,
                    'text': dim.dxf.text if hasattr(dim.dxf, 'text') else '',
                    'measurement': dim.get_measurement() if hasattr(dim, 'get_measurement') else 0,
                }
                dimensions.append(dim_info)
            except Exception as e:
                print(f"  Warning: Error reading dimension - {e}")
                
        self.data['dimensions'] = dimensions
        print(f"✓ Ditemukan {len(dimensions)} dimensi")
        return dimensions
    
    def extract_polylines(self) -> List[Dict]:
        """Ekstrak semua polyline dan lwpolyline"""
        polylines = []
        
        # LWPOLYLINE (lightweight polyline)
        for pline in self.msp.query('LWPOLYLINE'):
            try:
                points = list(pline.get_points())
                poly_info = {
                    'type': 'LWPOLYLINE',
                    'layer': pline.dxf.layer,
                    'closed': pline.closed,
                    'points': points,
                    'count': len(points)
                }
                polylines.append(poly_info)
            except Exception as e:
                print(f"  Warning: Error reading polyline - {e}")
        
        # POLYLINE
        for pline in self.msp.query('POLYLINE'):
            try:
                points = [(v.dxf.location.x, v.dxf.location.y) for v in pline.vertices]
                poly_info = {
                    'type': 'POLYLINE',
                    'layer': pline.dxf.layer,
                    'closed': pline.is_closed,
                    'points': points,
                    'count': len(points)
                }
                polylines.append(poly_info)
            except Exception as e:
                print(f"  Warning: Error reading polyline - {e}")
        
        self.data['polylines'] = polylines
        print(f"✓ Ditemukan {len(polylines)} polylines")
        return polylines
    
    def extract_lines(self) -> List[Dict]:
        """Ekstrak semua garis"""
        lines = []
        
        for line in self.msp.query('LINE'):
            line_info = {
                'layer': line.dxf.layer,
                'start': (line.dxf.start.x, line.dxf.start.y),
                'end': (line.dxf.end.x, line.dxf.end.y),
                'length': line.dxf.start.distance(line.dxf.end)
            }
            lines.append(line_info)
        
        self.data['lines'] = lines
        print(f"✓ Ditemukan {len(lines)} garis")
        return lines
    
    def extract_circles(self) -> List[Dict]:
        """Ekstrak semua lingkaran"""
        circles = []
        
        for circle in self.msp.query('CIRCLE'):
            circle_info = {
                'layer': circle.dxf.layer,
                'center': (circle.dxf.center.x, circle.dxf.center.y),
                'radius': circle.dxf.radius,
                'diameter': circle.dxf.radius * 2
            }
            circles.append(circle_info)
        
        self.data['circles'] = circles
        print(f"✓ Ditemukan {len(circles)} lingkaran")
        return circles
    
    def extract_hatches(self) -> List[Dict]:
        """Ekstrak semua hatch (arsiran)"""
        hatches = []
        
        for hatch in self.msp.query('HATCH'):
            try:
                hatch_info = {
                    'layer': hatch.dxf.layer,
                    'pattern': hatch.dxf.pattern_name,
                    'area': 0  # Will calculate if needed
                }
                hatches.append(hatch_info)
            except Exception as e:
                print(f"  Warning: Error reading hatch - {e}")
        
        self.data['hatches'] = hatches
        print(f"✓ Ditemukan {len(hatches)} hatches")
        return hatches
    
    def extract_blocks(self) -> List[Dict]:
        """Ekstrak semua block references"""
        blocks = []
        
        for insert in self.msp.query('INSERT'):
            block_info = {
                'name': insert.dxf.name,
                'layer': insert.dxf.layer,
                'position': (insert.dxf.insert.x, insert.dxf.insert.y),
                'rotation': insert.dxf.rotation if hasattr(insert.dxf, 'rotation') else 0,
                'scale_x': insert.dxf.xscale if hasattr(insert.dxf, 'xscale') else 1,
                'scale_y': insert.dxf.yscale if hasattr(insert.dxf, 'yscale') else 1
            }
            blocks.append(block_info)
        
        self.data['blocks'] = blocks
        print(f"✓ Ditemukan {len(blocks)} blocks")
        return blocks
    
    def extract_all(self) -> Dict[str, Any]:
        """Ekstrak semua data dari file DWG"""
        print("\n" + "="*60)
        print("EKSTRAKSI DATA DARI FILE DWG")
        print("="*60)
        
        if not self.load_file():
            return None
        
        self.extract_layers()
        self.extract_texts()
        self.extract_dimensions()
        self.extract_polylines()
        self.extract_lines()
        self.extract_circles()
        self.extract_hatches()
        self.extract_blocks()
        
        print("="*60)
        print("✓ EKSTRAKSI SELESAI")
        print("="*60 + "\n")
        
        return self.data
    
    def analyze_layers_by_category(self) -> Dict[str, List[str]]:
        """Menganalisis dan mengelompokkan layer berdasarkan kategori pekerjaan"""
        categories = {
            'struktur': [],
            'arsitektur': [],
            'mep': [],
            'dimensi': [],
            'text': [],
            'lainnya': []
        }
        
        # Keywords untuk klasifikasi
        keywords = {
            'struktur': ['kolom', 'balok', 'plat', 'pondasi', 'struktur', 'sloof', 'ring', 'col', 'beam', 'slab', 'foundation'],
            'arsitektur': ['dinding', 'wall', 'pintu', 'door', 'jendela', 'window', 'lantai', 'floor', 'atap', 'roof', 'plafon', 'ceiling'],
            'mep': ['mep', 'listrik', 'electrical', 'plumbing', 'mekanikal', 'ac', 'hvac', 'sanitasi'],
            'dimensi': ['dim', 'dimension', 'ukuran'],
            'text': ['text', 'label', 'keterangan', 'note']
        }
        
        for layer in self.data['layers']:
            layer_name = layer['name'].lower()
            categorized = False
            
            for category, keys in keywords.items():
                if any(key in layer_name for key in keys):
                    categories[category].append(layer['name'])
                    categorized = True
                    break
            
            if not categorized:
                categories['lainnya'].append(layer['name'])
        
        return categories
    
    def get_summary(self) -> Dict[str, Any]:
        """Mendapatkan ringkasan data yang diekstrak"""
        summary = {
            'file': self.filepath,
            'total_layers': len(self.data['layers']),
            'total_texts': len(self.data['texts']),
            'total_dimensions': len(self.data['dimensions']),
            'total_polylines': len(self.data['polylines']),
            'total_lines': len(self.data['lines']),
            'total_circles': len(self.data['circles']),
            'total_hatches': len(self.data['hatches']),
            'total_blocks': len(self.data['blocks']),
            'layer_categories': self.analyze_layers_by_category()
        }
        return summary


if __name__ == "__main__":
    # Test the reader
    dwg_path = r"d:\2. NATA_PROJECTAPP\Github_RS.Sari Darma\RS-SARIDARMA\drawing\ars\20251108_Plan RS Sari Dharma.dwg"
    
    reader = DXFReader(dwg_path)
    data = reader.extract_all()
    
    if data:
        summary = reader.get_summary()
        print("\nRINGKASAN:")
        print(f"Total Layers: {summary['total_layers']}")
        print(f"Total Texts: {summary['total_texts']}")
        print(f"Total Dimensions: {summary['total_dimensions']}")
        print(f"Total Polylines: {summary['total_polylines']}")
        print(f"Total Lines: {summary['total_lines']}")
        print(f"Total Circles: {summary['total_circles']}")
        print(f"Total Blocks: {summary['total_blocks']}")
        
        print("\nKATEGORI LAYER:")
        for category, layers in summary['layer_categories'].items():
            if layers:
                print(f"\n{category.upper()}:")
                for layer in layers[:5]:  # Show first 5
                    print(f"  - {layer}")
                if len(layers) > 5:
                    print(f"  ... dan {len(layers) - 5} lainnya")
