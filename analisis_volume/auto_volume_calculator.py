"""
Auto Volume Calculator dari File DXF
Otomatis identifikasi item pekerjaan dan hitung volume dari geometri DXF

Refactored with modular components (Priority #10):
- GridDetector: Grid reference detection
- VoidDetector: Void/hole detection in polylines
- HeightDetector: Height extraction from layer names
- ItemAggregator: Multi-key aggregation by location
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

# Import dimension parser (Priority #7)
try:
    from .dimension_parser import DimensionParser
except ImportError:
    from dimension_parser import DimensionParser

# Import modular components (Priority #10)
try:
    from .grid_detector import GridDetector
    from .void_detector import VoidDetector
    from .height_detector import HeightDetector
    from .item_aggregator import ItemAggregator
except ImportError:
    from grid_detector import GridDetector
    from void_detector import VoidDetector
    from height_detector import HeightDetector
    from item_aggregator import ItemAggregator


class AutoVolumeCalculator:
    """Class untuk auto-calculate volume dari data DXF"""
    
    def __init__(self, dxf_data: Dict):
        self.dxf_data = dxf_data
        self.items = []
        
        # ✅ Priority #10: Initialize modular components
        self.grid_detector = GridDetector()
        
        # ✅ Priority #3: Store detected grid references from drawing
        self.grid_references = {}  # {'A': x_position, 'B': x_position, '1': y_position, etc}
        
        # ✅ Priority #7: Initialize dimension parser for robust regex
        self.dimension_parser = DimensionParser()
        
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
    
    def _detect_grid_bubbles(self):
        """✅ CRITICAL FIX: Detect actual grid bubbles from drawing (delegates to GridDetector)"""
        texts = self.dxf_data.get('texts', [])
        result = self.grid_detector.detect_grid_bubbles(texts)
        
        # Sync grid_references for backward compatibility
        self.grid_references = self.grid_detector.get_grid_references()
        
        return result
    
    def _detect_height_from_context(self, layer: str, position: Tuple[float, float]) -> Optional[float]:
        """
        ✅ CRITICAL FIX: Detect height from context (NO HARDCODED DEFAULT!)
        Delegates to HeightDetector module
        """
        return HeightDetector.detect_height_from_context(layer, position)
    
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
        
        # ✅ CRITICAL FIX: Use proximity-based grid detection
        if self.grid_references and (self.grid_references.get('x') or self.grid_references.get('y')):
            return self._find_nearest_grid(position)
        else:
            # ⚠️ Fallback: Cannot detect grids from drawing
            return 'Unknown'
    
    def _point_in_polygon(self, point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        """Check if point is inside polygon (delegates to VoidDetector)"""
        return VoidDetector.point_in_polygon(point, polygon)
    
    def _polyline_contains_polyline(self, outer: List[Tuple[float, float]], inner: List[Tuple[float, float]]) -> bool:
        """Check if outer polyline contains inner polyline (delegates to VoidDetector)"""
        return VoidDetector.polyline_contains_polyline(outer, inner)
    
    def _calculate_polyline_area(self, points: List[Tuple[float, float]]) -> float:
        """Calculate polygon area (delegates to VoidDetector)"""
        return VoidDetector.calculate_polyline_area(points)
    
    def _detect_voids_in_polyline(self, outer_points: List[Tuple[float, float]], 
                                   all_polylines: List[Dict]) -> Tuple[float, List[Dict]]:
        """Detect void polylines inside outer polyline (delegates to VoidDetector)"""
        return VoidDetector.detect_voids_in_polyline(outer_points, all_polylines)
    
    def _extract_all_rectangles(self) -> List[Dict]:
        """Extract all rectangular geometries (from closed polylines with 4-5 points)"""
        rectangles = []
        
        for polyline in self.dxf_data.get('polylines', []):
            points = polyline.get('points', [])
            
            # Check if it's a rectangle (4 corners + optional closing point)
            if len(points) in [4, 5]:
                # Get bounding box
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)
                
                width = abs(max_x - min_x)
                height = abs(max_y - min_y)
                
                # Skip if too small (likely annotation)
                if width < 10 or height < 10:  # Less than 10mm
                    continue
                
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                rectangles.append({
                    'type': 'rectangle',
                    'position': (center_x, center_y),
                    'width': width,
                    'height': height,
                    'layer': polyline.get('layer', ''),
                    'points': points
                })
        
        return rectangles
    
    def _extract_all_circles(self) -> List[Dict]:
        """Extract all circular geometries"""
        circles = []
        
        for circle in self.dxf_data.get('circles', []):
            radius = circle.get('radius', 0)
            
            # Skip if too small (likely annotation)
            if radius < 5:  # Less than 5mm radius
                continue
            
            circles.append({
                'type': 'circle',
                'position': circle.get('position', (0, 0)),
                'radius': radius,
                'layer': circle.get('layer', '')
            })
        
        return circles
    
    def _extract_all_text_labels(self) -> List[Dict]:
        """Extract all text labels with dimensions and codes"""
        labels = []
        
        for text in self.dxf_data.get('texts', []):
            raw_content = text.get('content', '')
            position = text.get('position', (0, 0))
            layer = text.get('layer', '')
            
            if not raw_content or len(raw_content.strip()) < 2:
                continue
            
            # Clean and parse text
            content = clean_text(raw_content)
            content = parse_abbreviation(content)
            
            if not content or len(content.strip()) < 2:
                continue
            
            # Extract dimensions (✅ Priority #7: now using robust parser)
            dimensions = self.extract_dimensions_from_text(content, layer=layer)
            
            # Extract kode
            kode = self.extract_kode_from_text(content)
            
            # Identify item type
            item_type = self.identify_item_type(content, layer)
            
            if dimensions or kode or item_type != 'unknown':
                labels.append({
                    'text': content,
                    'position': position,
                    'layer': layer,
                    'dimensions': dimensions,
                    'kode': kode,
                    'item_type': item_type
                })
        
        return labels
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _match_geometry_to_text(self, geometries: List[Dict], labels: List[Dict], 
                                max_distance: float = 1000.0) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Match geometries to nearest text labels
        Returns: (matched_pairs, unmatched_geometries, unmatched_labels)
        """
        matched_pairs = []
        unmatched_geometries = []
        unmatched_labels = []
        
        used_geometry_indices = set()
        used_label_indices = set()
        
        # For each label, find nearest geometry
        for label_idx, label in enumerate(labels):
            label_pos = label['position']
            min_distance = float('inf')
            nearest_geom_idx = None
            
            for geom_idx, geom in enumerate(geometries):
                if geom_idx in used_geometry_indices:
                    continue
                
                geom_pos = geom['position']
                distance = self._calculate_distance(label_pos, geom_pos)
                
                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    nearest_geom_idx = geom_idx
            
            if nearest_geom_idx is not None:
                matched_pairs.append({
                    'geometry': geometries[nearest_geom_idx],
                    'label': label,
                    'distance': min_distance
                })
                used_geometry_indices.add(nearest_geom_idx)
                used_label_indices.add(label_idx)
        
        # Collect unmatched items
        for geom_idx, geom in enumerate(geometries):
            if geom_idx not in used_geometry_indices:
                unmatched_geometries.append(geom)
        
        for label_idx, label in enumerate(labels):
            if label_idx not in used_label_indices:
                unmatched_labels.append(label)
        
        return matched_pairs, unmatched_geometries, unmatched_labels
    
    def _warn_unmatched_items(self, unmatched_geometries: List[Dict], unmatched_labels: List[Dict]):
        """Print warnings for unmatched items"""
        if unmatched_geometries:
            print(f"\n  ⚠️  WARNING: Found {len(unmatched_geometries)} geometries WITHOUT labels:")
            for i, geom in enumerate(unmatched_geometries[:5]):  # Show first 5
                pos = geom['position']
                layer = geom['layer']
                if geom['type'] == 'rectangle':
                    print(f"    - Rectangle at ({pos[0]:.0f}, {pos[1]:.0f}) | {geom['width']:.0f}x{geom['height']:.0f} | Layer: {layer}")
                elif geom['type'] == 'circle':
                    print(f"    - Circle at ({pos[0]:.0f}, {pos[1]:.0f}) | r={geom['radius']:.0f} | Layer: {layer}")
            if len(unmatched_geometries) > 5:
                print(f"    ... and {len(unmatched_geometries) - 5} more")
        
        if unmatched_labels:
            print(f"\n  ⚠️  WARNING: Found {len(unmatched_labels)} labels WITHOUT nearby geometry:")
            for i, label in enumerate(unmatched_labels[:5]):  # Show first 5
                pos = label['position']
                text = label['text'][:30]  # Truncate long text
                print(f"    - '{text}' at ({pos[0]:.0f}, {pos[1]:.0f}) | Layer: {label['layer']}")
            if len(unmatched_labels) > 5:
                print(f"    ... and {len(unmatched_labels) - 5} more")
    
    def _find_nearest_grid(self, position: Tuple[float, float]) -> str:
        """Find nearest grid reference (delegates to GridDetector)"""
        return self.grid_detector.find_nearest_grid(position)
    
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
    
    def extract_dimensions_from_text(self, text: str, layer: str = '') -> Optional[Tuple[float, float, float]]:
        """
        ✅ Priority #7: Robust dimension extraction with smart unit detection
        
        Ekstrak dimensi dari teks dengan berbagai format
        Contoh: 
            "K1 (20x30)" → (0.20, 0.30, None)
            "K1 (200x300)" → (0.20, 0.30, None)  # Smart: large numbers = mm
            "BALOK 15/25" → (0.15, 0.25, None)
            "KOLOM 30x40 H=400" → (0.30, 0.40, 4.00)
            "K1 0.2x0.3" → (0.20, 0.30, None)  # Decimal = meters
            "200x300mm" → (0.20, 0.30, None)  # Explicit units
            "20 x 30 cm" → (0.20, 0.30, None)  # Spaced with units
        
        Args:
            text: Text to parse
            layer: Layer name for context (helps unit detection)
        
        Returns:
            Tuple of (width, length, height) in meters, or None
        """
        # Use robust dimension parser (Priority #7)
        result = self.dimension_parser.parse(text, context=layer)
        
        if result:
            return result
        
        # Fallback: No dimensions found
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
    
    def calculate_volume_from_polyline(self, polyline: Dict, thickness: float = 0.12, 
                                       all_polylines: List[Dict] = None) -> float:
        """Hitung volume dari polyline (untuk plat lantai) dengan void detection"""
        try:
            points = polyline['points']
            if len(points) < 3:
                return 0.0
            
            # Use void detection if all_polylines provided
            if all_polylines and len(all_polylines) > 1:
                net_area, voids = self._detect_voids_in_polyline(points, all_polylines)
                
                if voids:
                    print(f"    ✓ Detected {len(voids)} void(s), net area: {net_area:.2f} m²")
                
                volume = net_area * thickness
                return volume
            else:
                # Original calculation without void detection
                area = self._calculate_polyline_area(points)
                
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
                # Extract dimensions from text (✅ Priority #7: now using robust parser)
                dimensions = self.extract_dimensions_from_text(content, layer=layer)
                
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
        """Process polylines sebagai plat lantai with void detection"""
        print("\n→ Processing polylines as plat...")
        
        polylines = self.dxf_data.get('polylines', [])
        plat_count = 0
        
        for idx, polyline in enumerate(polylines):
            layer = polyline.get('layer', '')
            
            # Check if layer contains plat/slab/lantai keywords
            if any(keyword in layer.lower() for keyword in ['plat', 'slab', 'lantai', 'floor', 'dak']):
                # Assume 12cm thickness for plat
                thickness = 0.12
                
                # Calculate volume WITH void detection (pass all polylines)
                volume = self.calculate_volume_from_polyline(polyline, thickness, polylines)
                
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
                # ⚠️ CRITICAL FIX: Remove hardcoded height!
                # Try to detect height from nearby vertical dimension or layer name
                height = self._detect_height_from_context(layer, circle.get('position', (0, 0)))
                if not height:
                    print(f"  ⚠️ WARNING: Cannot detect height for circle at {circle.get('position')}, skipping...")
                    continue
                
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
        """✅ CRITICAL FIX: Aggregate dengan breakdown per LOKASI (delegates to ItemAggregator)"""
        self.items = ItemAggregator.aggregate_similar_items(self.items)
    
    def process_geometry_first_approach(self):
        """
        NEW: Geometry-first approach to prevent missing items
        Extract ALL geometries first, then match with text labels
        """
        print("\n→ Processing with Geometry-First approach...")
        
        # Step 1: Extract all geometries
        rectangles = self._extract_all_rectangles()
        circles = self._extract_all_circles()
        all_geometries = rectangles + circles
        
        print(f"  ✓ Found {len(rectangles)} rectangles, {len(circles)} circles")
        
        # Step 2: Extract all text labels
        labels = self._extract_all_text_labels()
        print(f"  ✓ Found {len(labels)} text labels with dimensions/codes")
        
        if not all_geometries:
            print("  ⚠️  No geometries detected, skipping geometry-first approach")
            return
        
        # Step 3: Match geometries to text labels
        matched_pairs, unmatched_geometries, unmatched_labels = self._match_geometry_to_text(
            all_geometries, labels, max_distance=1000.0  # 1000mm = 1m tolerance
        )
        
        print(f"  ✓ Matched {len(matched_pairs)} geometry-label pairs")
        
        # Step 4: Process matched pairs
        processed_count = 0
        for pair in matched_pairs:
            geom = pair['geometry']
            label = pair['label']
            
            # Get common attributes
            layer = geom['layer']
            position = geom['position']
            lantai = self.identify_lantai_from_layer(layer)
            grid = self._find_nearest_grid(position)
            
            # Determine item type from label or layer
            item_type = label.get('item_type', 'unknown')
            if item_type == 'unknown':
                item_type = self.identify_item_type('', layer)
            
            # Get dimensions: prefer label dimensions, fallback to geometry
            dimensions = label.get('dimensions')
            kode = label.get('kode', '')
            
            if geom['type'] == 'rectangle':
                # Convert mm to m
                width = geom['width'] / 1000 if geom['width'] > 10 else geom['width']
                height = geom['height'] / 1000 if geom['height'] > 10 else geom['height']
                
                # If label has dimensions, use those (more accurate)
                if dimensions and len(dimensions) >= 2:
                    panjang, lebar = dimensions[0], dimensions[1]
                    tinggi = dimensions[2] if len(dimensions) > 2 else None
                else:
                    # Use geometry dimensions
                    panjang, lebar = width, height
                    tinggi = None
                
                # Detect height from context if needed
                if not tinggi and item_type in ['balok', 'kolom', 'sloof']:
                    tinggi = self._detect_height_from_context(layer, position)
                
                # Calculate volume
                if tinggi:
                    volume = panjang * lebar * tinggi
                    
                    self.items.append({
                        'item': label['text'],
                        'kode': kode,
                        'kategori': item_type,
                        'layer': layer,
                        'lantai': lantai,
                        'grid': grid,
                        'panjang': panjang,
                        'lebar': lebar,
                        'tinggi': tinggi,
                        'volume': volume,
                        'count': 1,
                        'source': 'geometry-first'
                    })
                    processed_count += 1
            
            elif geom['type'] == 'circle':
                # Circle geometry (kolom bulat)
                radius = geom['radius'] / 1000 if geom['radius'] > 10 else geom['radius']
                diameter = radius * 2
                
                # Detect height
                height = self._detect_height_from_context(layer, position)
                if height:
                    area = math.pi * radius * radius
                    volume = area * height
                    
                    self.items.append({
                        'item': label['text'],
                        'kode': kode,
                        'kategori': item_type if item_type != 'unknown' else 'kolom',
                        'layer': layer,
                        'lantai': lantai,
                        'grid': grid,
                        'panjang': diameter,
                        'lebar': diameter,
                        'tinggi': height,
                        'volume': volume,
                        'count': 1,
                        'source': 'geometry-first'
                    })
                    processed_count += 1
        
        print(f"  ✓ Processed {processed_count} items from geometry-first approach")
        
        # Step 5: Warn about unmatched items
        self._warn_unmatched_items(unmatched_geometries, unmatched_labels)
    
    def calculate_all_volumes(self) -> List[Dict]:
        """Main method: Calculate semua volume dari DXF data"""
        print("\n" + "="*70)
        print("AUTO VOLUME CALCULATION FROM DXF")
        print("="*70)
        
        # Step 0: ✅ Detect grid references from drawing (CRITICAL FIX)
        has_grids = self._detect_grid_bubbles()
        if not has_grids:
            print("  ⚠️ WARNING: No grid bubbles detected - grid assignments may be inaccurate!")
        
        # Step 1: NEW - Geometry-First Approach (HIGH PRIORITY FIX)
        self.process_geometry_first_approach()
        
        # Step 2: Process texts and dimensions (legacy fallback)
        self.process_texts_and_dimensions()
        
        # Step 3: Process polylines as plat
        self.process_polylines_as_plat()
        
        # Step 4: Process circles as kolom (legacy fallback)
        self.process_circles_as_kolom()
        
        # Step 5: Aggregate similar items
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
