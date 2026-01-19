"""
Robust Dimension Parser
Handles multiple formats and smart unit detection
"""

import re
from typing import Optional, Tuple, List


class DimensionParser:
    """
    Robust parser for dimension extraction with smart unit detection
    
    Supports formats:
    - 20x30, 200x300, 0.2x0.3
    - 20/30, 200/300  
    - 20 x 30, 200 X 300
    - 20×30 (multiplication sign)
    - 200x300mm, 20x30cm, 0.2x0.3m
    - H=400, h=4.0, HEIGHT=400
    """
    
    def __init__(self):
        # Regex patterns ordered by specificity (most specific first)
        self.patterns = [
            # Pattern 1: With explicit units (highest priority)
            # Examples: 200x300mm, 20x30cm, 0.2x0.3m
            {
                'regex': r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)\s*(mm|cm|m)',
                'handler': self._parse_with_unit,
                'priority': 1
            },
            
            # Pattern 2: Decimal format (likely meters)
            # Examples: 0.2x0.3, 0.25x0.40
            {
                'regex': r'(\d*\.\d+)\s*[xX×]\s*(\d*\.\d+)',
                'handler': self._parse_decimal,
                'priority': 2
            },
            
            # Pattern 3: Large numbers (likely mm)
            # Examples: 200x300, 250x400
            {
                'regex': r'(\d{3,})\s*[xX×]\s*(\d{3,})',
                'handler': self._parse_large_numbers,
                'priority': 3
            },
            
            # Pattern 4: Medium numbers (likely cm)
            # Examples: 20x30, 25x40
            {
                'regex': r'(\d{2})\s*[xX×]\s*(\d{2})',
                'handler': self._parse_medium_numbers,
                'priority': 4
            },
            
            # Pattern 5: Slash notation (balok format)
            # Examples: 15/25, 20/30
            {
                'regex': r'(\d+)\s*/\s*(\d+)',
                'handler': self._parse_slash_format,
                'priority': 5
            },
            
            # Pattern 6: Spaced format
            # Examples: 20 x 30, 200 X 300
            {
                'regex': r'(\d+\.?\d*)\s+[xX×]\s+(\d+\.?\d*)',
                'handler': self._parse_spaced,
                'priority': 6
            },
            
            # Pattern 7: Height patterns
            # Examples: H=400, h=4.0, HEIGHT=400, h:400
            {
                'regex': r'[hH][eEiIgGhHtT]*\s*[=:]\s*(\d+\.?\d*)',
                'handler': self._parse_height,
                'priority': 7
            },
            
            # Pattern 8: Thickness patterns
            # Examples: T=150, t=0.15, THICK=150
            {
                'regex': r'[tT][hHiIcCkK]*\s*[=:]\s*(\d+\.?\d*)',
                'handler': self._parse_thickness,
                'priority': 8
            }
        ]
    
    def _parse_with_unit(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse dimensions with explicit unit"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        unit = match.group(3).lower()
        
        # Convert to meters
        if unit == 'mm':
            return val1 / 1000, val2 / 1000, None
        elif unit == 'cm':
            return val1 / 100, val2 / 100, None
        else:  # m
            return val1, val2, None
    
    def _parse_decimal(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse decimal format (likely meters)"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        
        # Decimal format usually means meters
        # 0.2x0.3 = 20cm x 30cm
        return val1, val2, None
    
    def _parse_large_numbers(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse large numbers (>= 100, likely mm)"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        
        # Numbers >= 100 likely in millimeters
        # 200x300 = 0.2m x 0.3m
        return val1 / 1000, val2 / 1000, None
    
    def _parse_medium_numbers(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse medium numbers (10-99, likely cm)"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        
        # Numbers 10-99 likely in centimeters
        # 20x30 = 0.2m x 0.3m
        return val1 / 100, val2 / 100, None
    
    def _parse_slash_format(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse slash format (balok notation)"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        
        # Slash format typically cm
        # 15/25 = 0.15m x 0.25m
        return val1 / 100, val2 / 100, None
    
    def _parse_spaced(self, match: re.Match) -> Tuple[float, float, Optional[float]]:
        """Parse spaced format"""
        val1 = float(match.group(1))
        val2 = float(match.group(2))
        
        # Smart detection based on magnitude
        if val1 >= 100 or val2 >= 100:
            # Large numbers = mm
            return val1 / 1000, val2 / 1000, None
        elif val1 >= 10 or val2 >= 10:
            # Medium numbers = cm
            return val1 / 100, val2 / 100, None
        else:
            # Small numbers = m
            return val1, val2, None
    
    def _parse_height(self, match: re.Match) -> Tuple[Optional[float], Optional[float], float]:
        """Parse height notation"""
        val = float(match.group(1))
        
        # Smart unit detection for height
        if val >= 1000:
            # Very large = mm
            height = val / 1000
        elif val >= 100:
            # Large = cm
            height = val / 100
        elif val > 10:
            # Could be dm (decimeter) or large cm
            # Treat as cm for construction
            height = val / 100
        else:
            # Small = m
            height = val
        
        return None, None, height
    
    def _parse_thickness(self, match: re.Match) -> Tuple[Optional[float], Optional[float], float]:
        """Parse thickness notation"""
        val = float(match.group(1))
        
        # Similar to height
        if val >= 100:
            thickness = val / 1000  # mm to m
        elif val >= 10:
            thickness = val / 100   # cm to m
        else:
            thickness = val         # already in m
        
        return None, None, thickness
    
    def parse(self, text: str, context: Optional[str] = None) -> Optional[Tuple[float, float, float]]:
        """
        Parse dimensions from text with context-aware unit detection
        
        Args:
            text: Text to parse (e.g., "K1 20x30", "Balok 15/25", "KOLOM 300x400mm")
            context: Optional context (layer name, nearby text) for better detection
        
        Returns:
            Tuple of (width, length, height) in meters, or None if not found
            Any dimension can be None if not detected
        """
        text = text.strip()
        
        # Try patterns in priority order
        for pattern_info in sorted(self.patterns, key=lambda x: x['priority']):
            regex = pattern_info['regex']
            handler = pattern_info['handler']
            
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                result = handler(match)
                
                # Validate result
                if result and any(v is not None and v > 0 for v in result):
                    return result
        
        return None
    
    def parse_all(self, text: str) -> List[Tuple[float, float, float]]:
        """
        Parse all dimensions from text (may contain multiple)
        
        Returns:
            List of dimension tuples found
        """
        results = []
        
        for pattern_info in sorted(self.patterns, key=lambda x: x['priority']):
            regex = pattern_info['regex']
            handler = pattern_info['handler']
            
            matches = re.finditer(regex, text, re.IGNORECASE)
            for match in matches:
                result = handler(match)
                if result and any(v is not None and v > 0 for v in result):
                    results.append(result)
        
        # Remove duplicates (keep first occurrence)
        unique_results = []
        for result in results:
            if result not in unique_results:
                unique_results.append(result)
        
        return unique_results
    
    def smart_unit_detection(self, value: float, context: Optional[str] = None) -> float:
        """
        Smart unit detection based on magnitude and context
        
        Args:
            value: Numeric value to interpret
            context: Optional context string (layer name, etc)
        
        Returns:
            Value in meters
        """
        # Context clues
        if context:
            context_lower = context.lower()
            if 'mm' in context_lower:
                return value / 1000
            elif 'cm' in context_lower:
                return value / 100
            elif 'm' in context_lower and 'mm' not in context_lower:
                return value
        
        # Magnitude-based detection
        if value >= 1000:
            # Very large = mm (e.g., 4000 = 4m)
            return value / 1000
        elif value >= 100:
            # Large = cm (e.g., 400 = 4m)
            return value / 100
        elif value >= 10:
            # Medium = could be cm or dm
            # In construction, usually cm
            return value / 100
        else:
            # Small = m (e.g., 4.0 = 4m)
            return value


def test_parser():
    """Test dimension parser with various formats"""
    parser = DimensionParser()
    
    test_cases = [
        # Format variations
        ("20x30", (0.20, 0.30, None)),
        ("200x300", (0.20, 0.30, None)),
        ("20/30", (0.20, 0.30, None)),
        ("20 x 30", (0.20, 0.30, None)),
        ("200 X 300", (0.20, 0.30, None)),
        ("0.2x0.3", (0.20, 0.30, None)),
        
        # With units
        ("200x300mm", (0.20, 0.30, None)),
        ("20x30cm", (0.20, 0.30, None)),
        ("0.2x0.3m", (0.20, 0.30, None)),
        
        # Height patterns
        ("H=400", (None, None, 4.0)),
        ("h=4.0", (None, None, 4.0)),
        ("HEIGHT=400", (None, None, 4.0)),
        ("h:400", (None, None, 4.0)),
        
        # Thickness
        ("T=150", (None, None, 0.15)),
        ("t=0.15", (None, None, 0.15)),
        
        # Combined
        ("K1 (30x40) H=400", (0.30, 0.40, None)),  # Would need parse_all
        ("Balok 25/60", (0.25, 0.60, None)),
    ]
    
    print("Testing Dimension Parser:")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for text, expected in test_cases:
        result = parser.parse(text)
        
        # Compare with tolerance
        if result and expected:
            match = True
            for i in range(3):
                if expected[i] is not None and result[i] is not None:
                    if abs(result[i] - expected[i]) > 0.001:
                        match = False
                        break
                elif expected[i] != result[i]:
                    match = False
                    break
            
            if match:
                print(f"✓ '{text}' → {result}")
                passed += 1
            else:
                print(f"✗ '{text}' → {result} (expected {expected})")
                failed += 1
        else:
            print(f"✗ '{text}' → {result} (expected {expected})")
            failed += 1
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    test_parser()
