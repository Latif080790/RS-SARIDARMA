"""
Grid Detector Module
Handles grid reference detection from DXF drawings.
Extracted from auto_volume_calculator.py for better maintainability.
"""

import re
from typing import Dict, List, Tuple, Optional


class GridDetector:
    """Detects and manages grid references from DXF data"""
    
    def __init__(self):
        self.grid_references: Dict[str, Dict[str, float]] = {'x': {}, 'y': {}}
    
    def detect_grid_bubbles(self, texts: List[Dict]) -> bool:
        """
        ✅ CRITICAL FIX: Detect actual grid bubbles from drawing
        
        Args:
            texts: List of text entities from DXF data
            
        Returns:
            True if grids were detected, False otherwise
        """
        print("\n→ Detecting grid references from drawing...")
        
        grid_pattern_alpha = r'^[A-Z]$'  # Single letter: A, B, C
        grid_pattern_num = r'^\d{1,2}$'  # Single/double digit: 1, 2, 10
        
        x_grids = {}  # {'A': x_pos, 'B': x_pos}
        y_grids = {}  # {'1': y_pos, '2': y_pos}
        
        for text in texts:
            content = text.get('content', '').strip().upper()
            position = text.get('position', (0, 0))
            layer = text.get('layer', '').lower()
            
            # Check if layer contains 'grid' or 'as' (common grid layer names)
            is_grid_layer = any(kw in layer for kw in ['grid', 'as', 'axis'])
            
            if is_grid_layer or len(content) <= 2:
                # Check for alphabetic grid (A, B, C, etc)
                if re.match(grid_pattern_alpha, content):
                    if content not in x_grids:
                        x_grids[content] = position[0]
                    else:
                        # Average if multiple occurrences (handle duplicates)
                        x_grids[content] = (x_grids[content] + position[0]) / 2
                
                # Check for numeric grid (1, 2, 3, etc)
                elif re.match(grid_pattern_num, content):
                    if content not in y_grids:
                        y_grids[content] = position[1]
                    else:
                        y_grids[content] = (y_grids[content] + position[1]) / 2
        
        # Store in class variable
        self.grid_references = {'x': x_grids, 'y': y_grids}
        
        print(f"  ✓ Found {len(x_grids)} horizontal grids: {list(x_grids.keys())}")
        print(f"  ✓ Found {len(y_grids)} vertical grids: {list(y_grids.keys())}")
        
        return len(x_grids) > 0 or len(y_grids) > 0
    
    def find_nearest_grid(self, position: Tuple[float, float]) -> str:
        """
        Find nearest grid reference using proximity
        
        Args:
            position: (x, y) coordinates
            
        Returns:
            Grid reference like "A1", "B2", etc., or "Unknown" if no grids
        """
        x_pos, y_pos = position
        
        x_grids = self.grid_references.get('x', {})
        y_grids = self.grid_references.get('y', {})
        
        # Find nearest X grid (alphabetic)
        nearest_x = 'Unknown'
        min_x_dist = float('inf')
        for grid_name, grid_pos in x_grids.items():
            dist = abs(x_pos - grid_pos)
            if dist < min_x_dist:
                min_x_dist = dist
                nearest_x = grid_name
        
        # Find nearest Y grid (numeric)
        nearest_y = 'Unknown'
        min_y_dist = float('inf')
        for grid_name, grid_pos in y_grids.items():
            dist = abs(y_pos - grid_pos)
            if dist < min_y_dist:
                min_y_dist = dist
                nearest_y = grid_name
        
        # Return combined grid reference
        if nearest_x != 'Unknown' and nearest_y != 'Unknown':
            return f"{nearest_x}{nearest_y}"
        elif nearest_x != 'Unknown':
            return f"{nearest_x}-?"
        elif nearest_y != 'Unknown':
            return f"?-{nearest_y}"
        else:
            return 'Unknown'
    
    def get_grid_references(self) -> Dict[str, Dict[str, float]]:
        """Get current grid references"""
        return self.grid_references
    
    def set_grid_references(self, grid_references: Dict[str, Dict[str, float]]):
        """Set grid references (for compatibility)"""
        self.grid_references = grid_references
