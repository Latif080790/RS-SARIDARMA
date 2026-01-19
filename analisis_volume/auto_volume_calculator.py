"""
Auto Volume Calculator dari File DXF
Otomatis identifikasi item pekerjaan dan hitung volume dari geometri DXF
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Import text utilities
try:
    from .text_utils import clean_text, parse_abbreviation, detect_category
except ImportError:
    from text_utils import clean_text, parse_abbreviation, detect_category


class AutoVolumeCalculator:
    """Class untuk auto-calculate volume dari data DXF"""
    
    def __init__(self, dxf_data: Dict):
        self.dxf_data = dxf_data
        self.items = []
        
        # ========== EXTENDED KEYWORDS (MEP ADDED) ==========
        self.keywords = {
            # Struktur
            'kolom': ['kolom', 'column', 'k1', 'k2', 'k3', 'k4', 'col'],
            'balok': ['balok', 'beam', 'b1', 'b2', 'b3', 'b4', 'bm'],
            'plat': ['plat', 'slab', 'lantai', 'floor', 'dak', 'pl'],
            'sloof': ['sloof', 'tie beam', 'ground beam', 's1', 's2'],
            'pondasi': ['pondasi', 'foundation', 'footplate', 'foot', 'p1', 'p2', 'p3'],
            'dinding': ['dinding', 'wall', 'tembok'],
            'ring': ['ring', 'ring balok', 'ring balk'],
            'tangga': ['tangga', 'stair', 'stairs'],
            
            # MEP - HVAC & AC
            'ac': ['ac', 'air conditioner', 'return air grille', 'supply air diffuser', 
                   'supply air grille', 'fresh air diffuser', 'exhaust grille'],
            'ducting': ['ducting', 'duct', 'saluran udara'],
            'grille': ['grille', 'diffuser', 'rag', 'sad', 'sag', 'fad', 'exh', 'eg'],
            
            # MEP - Plumbing
            'pipa': ['pipa', 'pipe', 'pwc', 'swp', 'vwp', 'saluran'],
            'hydrant': ['hydrant', 'hyd', 'pemadam'],
            'sprinkler': ['sprinkler', 'spr'],
            'gas': ['gas', 'medis', 'o2', 'oxygen', 'vac', 'vacuum', 'compressed air'],
            
            # MEP - Electrical
            'kabel': ['kabel', 'cable', 'wire'],
            'panel': ['panel', 'mdp', 'sdp', 'lp', 'pp', 'distribution'],
            'lampu': ['lampu', 'lighting', 'light', 'led'],
            'stop kontak': ['stop kontak', 'sk', 'outlet', 'power outlet'],
        }
        # ===================================================
        
        # Layer to Lantai mapping
        self.layer_mapping = {
            'basement': 'Basement',
            'lt_1': 'Lantai 1',
            'lt_2': 'Lantai 2',
            'lt1': 'Lantai 1',
            'lt2': 'Lantai 2',
            'lantai_1': 'Lantai 1',
            'lantai_2': 'Lantai 2',
            'ground': 'Lantai 1',
            'atap': 'Atap',
            'roof': 'Atap',
        }
    
    def extract_kode_from_text(self, text: str) -> Optional[str]:
        """Ekstrak kode item dari text (K1, K2, B1, B2, P1, dll)"""
        # Pattern untuk kode: K1, K2, B1, B2, P1, P2, S1, S2, PL1, PL2
        patterns = [
            r'\b([KBPS])(\d{1,2})\b',  # K1, B2, P3, S1
            r'\b(PL)(\d{1,2})\b',       # PL1, PL2
            r'([KBPS])[-\s]*(\d{1,2})',  # K-1, B 2, P-3
        ]
        
        text_upper = text.upper()
        for pattern in patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                prefix, number = matches[0]
                return f"{prefix}{number}"
        
        return None
    
    def extract_grid_reference(self, text: str, position: Tuple[float, float]) -> str:
        """Ekstrak As Grid dari text atau calculate dari position"""
        # Try extract from text first
        # Pattern: As A1, As B2, Grid C3, A-B, 1-2
        patterns = [
            r'[Aa][Ss]\s*([A-Z]\d+)',  # As A1, As B2
            r'[Gg]rid\s*([A-Z]\d+)',   # Grid A1
            r'\b([A-Z])(\d+)\b',       # A1, B2 standalone
            r'[Aa][Ss]\s*([A-Z])-([A-Z])',  # As A-B
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    if len(matches[0]) == 2 and matches[0][1].isdigit():
                        return f"{matches[0][0]}{matches[0][1]}"
                    else:
                        return f"{matches[0][0]}-{matches[0][1]}"
                else:
                    return matches[0]
        
        # Calculate from position if not in text
        # Assume grid spacing 5000mm = 5m
        grid_x = chr(65 + int(position[0] / 5000)) if position[0] >= 0 else 'A'
        grid_y = int(position[1] / 5000) + 1 if position[1] >= 0 else 1
        return f"{grid_x}{grid_y}"
    
    def identify_lantai_from_layer(self, layer: str) -> str:
        """Identifikasi lantai dari layer name"""
        layer_lower = layer.lower()
        
        for key, lantai in self.layer_mapping.items():
            if key in layer_lower:
                return lantai
        
        # Check for numeric indicators
        if 'lt 1' in layer_lower or 'lt1' in layer_lower or 'ground' in layer_lower:
            return 'Lantai 1'
        elif 'lt 2' in layer_lower or 'lt2' in layer_lower:
            return 'Lantai 2'
        elif 'basement' in layer_lower or 'bsmt' in layer_lower:
            return 'Basement'
        elif 'atap' in layer_lower or 'roof' in layer_lower:
            return 'Atap'
        
        return 'Unknown'
    
    def extract_dimensions_from_text(self, text: str) -> Optional[Tuple[float, float, float]]:
        """
        Ekstrak dimensi dari teks
        Contoh: "K1 (20x30)" → (0.20, 0.30, None)
                "BALOK 15/25" → (0.15, 0.25, None)
                "KOLOM 30x40 H=400" → (0.30, 0.40, 4.00)
        """
        text_lower = text.lower()
        dimensions = []
        
        # Pattern 1: 20x30 atau 20×30
        pattern1 = r'(\d+)\s*[xX×]\s*(\d+)'
        matches = re.findall(pattern1, text)
        if matches:
            for match in matches:
                dim1 = float(match[0]) / 100  # Convert cm to m
                dim2 = float(match[1]) / 100
                dimensions.extend([dim1, dim2])
        
        # Pattern 2: 15/25 (format balok)
        pattern2 = r'(\d+)\s*/\s*(\d+)'
        matches = re.findall(pattern2, text)
        if matches:
            for match in matches:
                dim1 = float(match[0]) / 100
                dim2 = float(match[1]) / 100
                dimensions.extend([dim1, dim2])
        
        # Pattern 3: h=400, H=4.00 (tinggi)
        pattern3 = r'[hH]\s*[=:]\s*(\d+\.?\d*)'
        matches = re.findall(pattern3, text)
        if matches:
            height = float(matches[0])
            if height > 10:  # Assume cm
                height = height / 100
            dimensions.append(height)
        
        # Pattern 4: t=12, tebal=12
        pattern4 = r't(?:ebal)?\s*[=:]\s*(\d+\.?\d*)'
        matches = re.findall(pattern4, text_lower)
        if matches:
            thickness = float(matches[0])
            if thickness > 1:  # Assume cm
                thickness = thickness / 100
            dimensions.append(thickness)
        
        if len(dimensions) >= 2:
            return tuple(dimensions[:3]) if len(dimensions) >= 3 else tuple(dimensions + [None])
        
        return None
    
    def identify_item_type(self, text: str, layer: str = '') -> str:
        """Identifikasi tipe item dari text dan layer"""
        text_lower = text.lower()
        layer_lower = layer.lower()
        combined = text_lower + ' ' + layer_lower
        
        for item_type, keywords in self.keywords.items():
            if any(keyword in combined for keyword in keywords):
                return item_type
        
        return 'unknown'
    
    def calculate_volume_rectangular(self, length: float, width: float, height: float, 
                                    count: int = 1) -> float:
        """Hitung volume untuk bentuk rectangular (kolom, balok)"""
        return length * width * height * count
    
    def calculate_area(self, length: float, width: float, count: int = 1) -> float:
        """Hitung luas untuk dinding, plat, dll"""
        return length * width * count
    
    def calculate_volume_from_polyline(self, polyline: Dict, thickness: float = 0.12) -> float:
        """Hitung volume dari polyline (untuk plat lantai)"""
        try:
            points = polyline['points']
            if len(points) < 3:
                return 0.0
            
            # Calculate area using Shoelace formula
            area = 0.0
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            area = abs(area) / 2.0
            
            # Convert to square meters if needed
            if area > 100000:  # Probably in mm²
                area = area / 1000000
            elif area > 1000:  # Probably in cm²
                area = area / 10000
            
            volume = area * thickness
            return volume
        except Exception as e:
            print(f"    Warning: Error calculating polyline volume - {e}")
            return 0.0
    
    def calculate_volume_from_circle(self, circle: Dict, height: float) -> float:
        """Hitung volume dari circle (untuk kolom bulat, tiang)"""
        try:
            radius = circle['radius']
            
            # Convert to meters if needed
            if radius > 10:  # Probably in mm
                radius = radius / 1000
            elif radius > 1:  # Probably in cm
                radius = radius / 100
            
            area = math.pi * radius * radius
            volume = area * height
            return volume
        except Exception as e:
            print(f"    Warning: Error calculating circle volume - {e}")
            return 0.0
    
    def group_by_layer_and_type(self) -> Dict[str, List[Dict]]:
        """Grouping items by layer and type"""
        grouped = defaultdict(list)
        
        for item in self.items:
            key = f"{item.get('kategori', 'unknown')}_{item.get('layer', 'default')}"
            grouped[key].append(item)
        
        return dict(grouped)
    
    def process_texts_and_dimensions(self):
        """Process text dan dimension entities untuk ekstrak item"""
        print("\n→ Processing texts and dimensions...")
        
        # Process texts
        text_items = {}
        for text in self.dxf_data.get('texts', []):
            raw_content = text.get('content', '')
            layer = text.get('layer', '')
            position = text.get('position', (0, 0))
            
            if not raw_content or len(raw_content.strip()) < 2:
                continue
            
            # ========== TEXT CLEANING (NEW) ==========
            # Clean AutoCAD formatting codes
            content = clean_text(raw_content)
            
            # Parse MEP abbreviations
            content = parse_abbreviation(content)
            # =========================================
            
            if not content or len(content.strip()) < 2:
                continue
            
            # Identify item type
            item_type = self.identify_item_type(content, layer)
            
            if item_type != 'unknown':
                # Extract dimensions from text
                dimensions = self.extract_dimensions_from_text(content)
                
                if dimensions:
                    # Extract kode dan grid
                    kode = self.extract_kode_from_text(content)
                    grid = self.extract_grid_reference(content, position)
                    lantai = self.identify_lantai_from_layer(layer)
                    
                    # Create position key for grouping
                    pos_key = f"{int(position[0]/100)}_{int(position[1]/100)}"
                    
                    if pos_key not in text_items:
                        text_items[pos_key] = {
                            'item': content,
                            'kode': kode,
                            'kategori': item_type,
                            'layer': layer,
                            'lantai': lantai,
                            'grid': grid,
                            'position': position,
                            'dimensions': dimensions,
                            'count': 1
                        }
        
        # Process dimensions
        dimension_values = {}
        for dim in self.dxf_data.get('dimensions', []):
            measurement = dim.get('measurement', 0)
            layer = dim.get('layer', '')
            
            if measurement > 0:
                # Store dimension value (might be referenced by position)
                dimension_values[layer] = dimension_values.get(layer, [])
                
                # Convert to meters if needed
                if measurement > 100:  # Probably mm
                    measurement = measurement / 1000
                elif measurement > 10:  # Probably cm
                    measurement = measurement / 100
                
                dimension_values[layer].append(measurement)
        
        # Add text items to self.items
        for pos_key, item_data in text_items.items():
            dims = item_data['dimensions']
            kategori = item_data['kategori']
            
            # Determine satuan dan calculate volume
            if kategori in ['kolom', 'balok', 'sloof', 'pondasi', 'ring']:
                satuan = 'm3'
                if dims[2] is not None:
                    volume = self.calculate_volume_rectangular(dims[0], dims[1], dims[2], item_data['count'])
                else:
                    # Assume standard height if not provided
                    default_height = 4.0 if kategori == 'kolom' else 0.3
                    volume = self.calculate_volume_rectangular(dims[0], dims[1], default_height, item_data['count'])
            elif kategori in ['plat', 'dinding']:
                satuan = 'm2'
                volume = self.calculate_area(dims[0], dims[1], item_data['count'])
            else:
                satuan = 'm3'
                volume = dims[0] * dims[1] if len(dims) >= 2 else 0
            
            self.items.append({
                'kode': item_data.get('kode', ''),
                'item': item_data['item'],
                'lantai': item_data.get('lantai', 'Unknown'),
                'grid': item_data.get('grid', ''),
                'kategori': kategori,
                'layer': item_data['layer'],
                'panjang': dims[0] if len(dims) > 0 else 0,
                'lebar': dims[1] if len(dims) > 1 else 0,
                'tinggi': dims[2] if len(dims) > 2 else None,
                'jumlah': item_data['count'],
                'satuan': satuan,
                'volume': volume,
                'method': 'text_extraction'
            })
        
        print(f"  ✓ Found {len(self.items)} items from texts")
        return dimension_values
    
    def process_polylines_as_plat(self):
        """Process polylines sebagai plat lantai"""
        print("\n→ Processing polylines as plat...")
        
        polylines = self.dxf_data.get('polylines', [])
        plat_count = 0
        
        for idx, polyline in enumerate(polylines):
            layer = polyline.get('layer', '')
            
            # Check if layer contains plat/slab/lantai keywords
            if any(keyword in layer.lower() for keyword in ['plat', 'slab', 'lantai', 'floor', 'dak']):
                # Assume 12cm thickness for plat
                thickness = 0.12
                volume = self.calculate_volume_from_polyline(polyline, thickness)
                
                if volume > 0:
                    lantai = self.identify_lantai_from_layer(layer)
                    kode = self.extract_kode_from_text(layer)
                    
                    self.items.append({
                        'kode': kode if kode else 'PL',
                        'item': f'Plat Lantai - {layer}',
                        'lantai': lantai,
                        'grid': 'Full Area',
                        'kategori': 'plat',
                        'layer': layer,
                        'panjang': 0,
                        'lebar': 0,
                        'tinggi': thickness,
                        'jumlah': 1,
                        'satuan': 'm3',
                        'volume': volume,
                        'method': 'polyline_area'
                    })
                    plat_count += 1
        
        print(f"  ✓ Found {plat_count} plat items from polylines")
    
    def process_circles_as_kolom(self):
        """Process circles sebagai kolom bulat"""
        print("\n→ Processing circles as kolom...")
        
        circles = self.dxf_data.get('circles', [])
        kolom_count = 0
        
        for idx, circle in enumerate(circles):
            layer = circle.get('layer', '')
            
            # Check if layer contains kolom/column keywords
            if any(keyword in layer.lower() for keyword in ['kolom', 'column', 'col', 'pile']):
                # Assume 4m height for kolom
                height = 4.0
                volume = self.calculate_volume_from_circle(circle, height)
                
                if volume > 0:
                    radius = circle['radius']
                    if radius > 10:
                        radius = radius / 1000
                    elif radius > 1:
                        radius = radius / 100
                    
                    diameter = radius * 2
                    position = circle.get('center', (0, 0))
                    lantai = self.identify_lantai_from_layer(layer)
                    grid = self.extract_grid_reference(layer, position)
                    kode = self.extract_kode_from_text(layer) if self.extract_kode_from_text(layer) else 'K'
                    
                    self.items.append({
                        'kode': kode,
                        'item': f'Kolom Bulat ⌀{diameter*100:.0f}cm - {layer}',
                        'lantai': lantai,
                        'grid': grid,
                        'kategori': 'kolom',
                        'layer': layer,
                        'panjang': diameter,
                        'lebar': diameter,
                        'tinggi': height,
                        'jumlah': 1,
                        'satuan': 'm3',
                        'volume': volume,
                        'method': 'circle_volume'
                    })
                    kolom_count += 1
        
        print(f"  ✓ Found {kolom_count} kolom items from circles")
    
    def aggregate_similar_items(self):
        """Aggregate items yang sama untuk mendapatkan jumlah total"""
        print("\n→ Aggregating similar items...")
        
        aggregated = {}
        
        for item in self.items:
            # Ensure all dimensions have values (not None)
            panjang = item.get('panjang') or 0
            lebar = item.get('lebar') or 0
            tinggi = item.get('tinggi') or 0
            
            # Create key based on item name and dimensions
            key = f"{item['item']}_{panjang:.3f}_{lebar:.3f}_{tinggi:.3f}"
            
            if key in aggregated:
                aggregated[key]['jumlah'] += item.get('jumlah', 1)
                aggregated[key]['volume'] += item.get('volume', 0)
            else:
                aggregated[key] = item.copy()
        
        self.items = list(aggregated.values())
        print(f"  ✓ Aggregated to {len(self.items)} unique items")
    
    def calculate_all_volumes(self) -> List[Dict]:
        """Main method: Calculate semua volume dari DXF data"""
        print("\n" + "="*70)
        print("AUTO VOLUME CALCULATION FROM DXF")
        print("="*70)
        
        # Step 1: Process texts and dimensions
        self.process_texts_and_dimensions()
        
        # Step 2: Process polylines as plat
        self.process_polylines_as_plat()
        
        # Step 3: Process circles as kolom
        self.process_circles_as_kolom()
        
        # Step 4: Aggregate similar items
        self.aggregate_similar_items()
        
        print("\n" + "="*70)
        print(f"✓ TOTAL: {len(self.items)} items calculated")
        print("="*70 + "\n")
        
        return self.items
    
    def get_summary_by_category(self) -> Dict[str, Dict]:
        """Get summary statistics by category"""
        summary = defaultdict(lambda: {'count': 0, 'total_volume': 0})
        
        for item in self.items:
            kategori = item.get('kategori', 'unknown')
            summary[kategori]['count'] += item['jumlah']
            summary[kategori]['total_volume'] += item['volume']
        
        return dict(summary)
    
    def export_to_dict(self) -> Dict[str, List[Dict]]:
        """Export items grouped by category"""
        grouped = defaultdict(list)
        
        kategori_mapping = {
            'kolom': 'struktur',
            'balok': 'struktur',
            'plat': 'struktur',
            'sloof': 'struktur',
            'pondasi': 'struktur',
            'ring': 'struktur',
            'tangga': 'struktur',
            'dinding': 'arsitektur',
        }
        
        for item in self.items:
            kategori = item.get('kategori', 'unknown')
            group = kategori_mapping.get(kategori, 'arsitektur')
            grouped[group].append(item)
        
        return dict(grouped)


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'texts': [
            {'content': 'K1 (20x30)', 'layer': 'KOLOM', 'position': (100, 200)},
            {'content': 'BALOK B1 15/25', 'layer': 'BALOK', 'position': (200, 300)},
            {'content': 'PLAT t=12', 'layer': 'PLAT_LANTAI', 'position': (300, 400)},
        ],
        'dimensions': [
            {'measurement': 400, 'layer': 'DIM_KOLOM'},  # 400cm = 4m
            {'measurement': 500, 'layer': 'DIM_BALOK'},  # 500cm = 5m
        ],
        'polylines': [],
        'circles': []
    }
    
    calculator = AutoVolumeCalculator(sample_data)
    items = calculator.calculate_all_volumes()
    
    print("\nCalculated Items:")
    for item in items:
        print(f"  • {item['item']}: {item['volume']:.3f} {item['satuan']}")
    
    print("\nSummary by Category:")
    summary = calculator.get_summary_by_category()
    for kategori, stats in summary.items():
        print(f"  • {kategori.upper()}: {stats['count']} items, Total: {stats['total_volume']:.2f} m³")
