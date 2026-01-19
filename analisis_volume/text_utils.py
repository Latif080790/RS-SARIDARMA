"""
Text Utilities for DXF Processing
Clean AutoCAD formatting codes and parse MEP abbreviations
"""

import re
from typing import Dict, Optional


class TextCleaner:
    """Clean AutoCAD text formatting codes"""
    
    @staticmethod
    def clean_autocad_text(text: str) -> str:
        """
        Remove AutoCAD formatting codes from text
        
        Examples:
            Input:  \\pxsm1,qd;{\\W0.85;\\fISOCPEUR|b0|i0|c0|p34;\\H0.8x;RAG\\P400x600mm}
            Output: RAG 400x600mm
            
            Input:  {\\T0.9;\\fISOCPEUR|b0|i0|c0|p34;\\C0;SAD.600x400}
            Output: SAD 600x400
        """
        if not text:
            return ""
        
        # Remove common AutoCAD formatting codes
        patterns_to_remove = [
            r'\\pxsm\d+,\w+;',           # \\pxsm1,qd;
            r'\{\\W[\d.]+;',             # {\\W0.85;
            r'\\f[^;]+;',                # \\fISOCPEUR|b0|i0|c0|p34;
            r'\\[HhCcTtAa][\d.]+x?;',   # \\H0.8x; \\C4; \\T0.9;
            r'\\[PpLl]',                 # \\P \\L (paragraph marks)
            r'[\{\}]',                   # { }
            r'\\\\',                     # \\
        ]
        
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Replace dot notation with space (SAD.600x400 → SAD 600x400)
        cleaned = re.sub(r'\.(?=\d)', ' ', cleaned)
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()


class MEPAbbreviationParser:
    """Parse MEP abbreviations to full names"""
    
    # Comprehensive MEP abbreviation dictionary
    ABBREVIATIONS = {
        # AC & HVAC
        'RAG': 'Return Air Grille',
        'SAG': 'Supply Air Grille',
        'SAD': 'Supply Air Diffuser',
        'FAD': 'Fresh Air Diffuser',
        'EXH': 'Exhaust Grille',
        'EG': 'Exhaust Grille',
        'AC': 'Air Conditioner',
        'FCU': 'Fan Coil Unit',
        'AHU': 'Air Handling Unit',
        'DUCT': 'Ducting',
        'VRV': 'Variable Refrigerant Volume',
        
        # Plumbing
        'PWC': 'Pipa Air Bersih/Clean Water Pipe',
        'SWP': 'Pipa Air Kotor/Soil Water Pipe',
        'VWP': 'Pipa Air Bekas/Vent Water Pipe',
        'HYD': 'Hydrant',
        'SPR': 'Sprinkler',
        'GAS': 'Gas Medis/Medical Gas',
        'O2': 'Oxygen',
        'VAC': 'Vacuum',
        'AIR': 'Compressed Air',
        
        # Electrical
        'MDP': 'Main Distribution Panel',
        'SDP': 'Sub Distribution Panel',
        'LP': 'Lighting Panel',
        'PP': 'Power Panel',
        'SK': 'Stop Kontak/Power Outlet',
        'LAMPU': 'Lighting',
        'KABEL': 'Cable',
        
        # Structure (for reference)
        'K': 'Kolom/Column',
        'B': 'Balok/Beam',
        'S': 'Sloof',
        'P': 'Pondasi/Foundation',
        'PL': 'Plat/Slab',
    }
    
    @staticmethod
    def parse_abbreviation(text: str) -> str:
        """
        Parse abbreviation to full name if found in dictionary
        
        Examples:
            Input:  RAG 400x600mm
            Output: Return Air Grille 400x600mm
            
            Input:  SAD 600x400
            Output: Supply Air Diffuser 600x400
        """
        if not text:
            return text
        
        # Extract first word (potential abbreviation)
        parts = text.split()
        if not parts:
            return text
        
        first_word = parts[0].upper()
        
        # Check if it's in dictionary
        if first_word in MEPAbbreviationParser.ABBREVIATIONS:
            full_name = MEPAbbreviationParser.ABBREVIATIONS[first_word]
            # Replace first word with full name, keep the rest
            return f"{full_name} {' '.join(parts[1:])}"
        
        return text
    
    @staticmethod
    def get_category_from_abbreviation(text: str) -> Optional[str]:
        """
        Get category hint from abbreviation
        
        Returns: 'mep', 'struktur', or None
        """
        if not text:
            return None
        
        first_word = text.split()[0].upper() if text.split() else ""
        
        # MEP abbreviations
        mep_abbr = ['RAG', 'SAG', 'SAD', 'FAD', 'EXH', 'EG', 'AC', 'FCU', 'AHU',
                   'DUCT', 'VRV', 'PWC', 'SWP', 'VWP', 'HYD', 'SPR', 'GAS',
                   'O2', 'VAC', 'AIR', 'MDP', 'SDP', 'LP', 'PP', 'SK', 'LAMPU', 'KABEL']
        
        # Structure abbreviations
        str_abbr = ['K', 'B', 'S', 'P', 'PL']
        
        if first_word in mep_abbr:
            return 'mep'
        elif first_word in str_abbr and len(first_word) <= 2:
            return 'struktur'
        
        return None


class CategoryDetector:
    """Detect category from various sources"""
    
    @staticmethod
    def from_folder_path(file_path: str) -> Optional[str]:
        """
        Detect category from folder location
        Strong hint with high confidence
        
        Examples:
            drawing/dxf/mep/AC...dxf → 'mep'
            drawing/dxf/str/Struktur.dxf → 'struktur'
        """
        if not file_path:
            return None
        
        path_lower = file_path.lower().replace('\\', '/')
        
        if 'dxf/mep' in path_lower or 'dxf\\mep' in path_lower:
            return 'mep'
        elif 'dxf/str' in path_lower or 'dxf\\str' in path_lower:
            return 'struktur'
        elif 'dxf/ars' in path_lower or 'dxf\\ars' in path_lower:
            return 'arsitektur'
        
        return None
    
    @staticmethod
    def from_layer_name(layer_name: str) -> Optional[str]:
        """
        Detect category from layer name
        
        Examples:
            HVAC, AC, MEP → 'mep'
            KOLOM, BALOK, STRUKTUR → 'struktur'
        """
        if not layer_name:
            return None
        
        layer_lower = layer_name.lower()
        
        # MEP keywords (comprehensive)
        mep_keywords = [
            'ac', 'hvac', 'mep', 'mechanical', 'electrical', 'plumbing',
            'pipa', 'pipe', 'ducting', 'duct', 'kabel', 'cable',
            'panel', 'hydrant', 'sprinkler', 'gas', 'medis',
            'fire', 'alarm', 'lighting', 'power', 'outlet',
            'air', 'water', 'sanitasi', 'plumb'
        ]
        
        # Struktur keywords
        str_keywords = [
            'kolom', 'column', 'balok', 'beam', 'plat', 'slab',
            'struktur', 'structure', 'sloof', 'pondasi', 'foundation',
            'footing', 'pile', 'tangga', 'stair'
        ]
        
        # Arsitektur keywords
        ars_keywords = [
            'dinding', 'wall', 'pintu', 'door', 'jendela', 'window',
            'arsitektur', 'architecture', 'denah', 'floor plan',
            'lantai', 'floor', 'plafon', 'ceiling', 'atap', 'roof',
            'interior', 'eksterior'
        ]
        
        # Check keywords
        if any(kw in layer_lower for kw in mep_keywords):
            return 'mep'
        elif any(kw in layer_lower for kw in str_keywords):
            return 'struktur'
        elif any(kw in layer_lower for kw in ars_keywords):
            return 'arsitektur'
        
        return None
    
    @staticmethod
    def from_text_content(text: str) -> Optional[str]:
        """
        Detect category from text content patterns
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # MEP patterns
        mep_patterns = [
            r'\b(ac|hvac|fcu|ahu)\b',
            r'\b(rag|sad|fad|exh)\b',
            r'\bpipa\b',
            r'\b(hydrant|sprinkler)\b',
            r'\b(panel|kabel|lampu)\b',
            r'\b\d+\s*pk\b',  # "2 PK" (AC capacity)
            r'pvc.*ø',         # "PVC Ø100" (pipe)
        ]
        
        # Struktur patterns
        str_patterns = [
            r'\b[ksb]\d+\b',   # K1, B2, S3
            r'\bkolom\b',
            r'\bbalok\b',
            r'\bplat\b',
        ]
        
        # Check patterns
        if any(re.search(pattern, text_lower) for pattern in mep_patterns):
            return 'mep'
        elif any(re.search(pattern, text_lower) for pattern in str_patterns):
            return 'struktur'
        
        return None
    
    @staticmethod
    def detect_with_confidence(file_path: str, layer_name: str, text: str) -> tuple[Optional[str], int]:
        """
        Detect category with confidence score (0-100)
        
        Returns: (category, confidence)
        """
        scores = {'mep': 0, 'struktur': 0, 'arsitektur': 0}
        
        # Folder path (highest confidence: 40 points)
        folder_cat = CategoryDetector.from_folder_path(file_path)
        if folder_cat:
            scores[folder_cat] += 40
        
        # Layer name (medium confidence: 30 points)
        layer_cat = CategoryDetector.from_layer_name(layer_name)
        if layer_cat:
            scores[layer_cat] += 30
        
        # Text content (lower confidence: 20 points)
        text_cat = CategoryDetector.from_text_content(text)
        if text_cat:
            scores[text_cat] += 20
        
        # Abbreviation hint (medium confidence: 10 points)
        abbr_cat = MEPAbbreviationParser.get_category_from_abbreviation(text)
        if abbr_cat:
            scores[abbr_cat] += 10
        
        # Get highest score
        if max(scores.values()) == 0:
            return None, 0
        
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        return best_category, confidence


# Convenience functions
def clean_text(text: str) -> str:
    """Clean AutoCAD text formatting"""
    return TextCleaner.clean_autocad_text(text)

def parse_abbreviation(text: str) -> str:
    """Parse MEP abbreviation to full name"""
    return MEPAbbreviationParser.parse_abbreviation(text)

def detect_category(file_path: str, layer_name: str, text: str) -> tuple[Optional[str], int]:
    """Detect category with confidence"""
    return CategoryDetector.detect_with_confidence(file_path, layer_name, text)
