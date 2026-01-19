"""
Height Detector Module
Handles height detection from layer names and context.
Extracted from auto_volume_calculator.py for better maintainability.
"""

import re
from typing import Optional, Tuple


class HeightDetector:
    """Detects height values from layer names and drawing context"""
    
    @staticmethod
    def detect_height_from_context(layer: str, position: Tuple[float, float] = None) -> Optional[float]:
        """
        ✅ CRITICAL FIX: Detect height from context (NO HARDCODED DEFAULT!)
        
        Try to find height from:
        1. Layer name (e.g., "KOLOM_H400" → 4.0m)
        2. Patterns: H400, H=4.0, T400, HEIGHT=400
        
        Args:
            layer: Layer name to extract height from
            position: Position for future context-based detection (not used yet)
            
        Returns:
            Height in meters, or None if cannot detect (forces manual review)
        """
        # Try extract from layer name (H400, H=4.0, HEIGHT=400, etc)
        height_patterns = [
            r'[Hh][-_=]?(\d{2,4})',  # H400, H=400, H_400
            r'[Tt][-_=]?(\d{2,4})',  # T400, T=400 (tinggi)
            r'HEIGHT[-_]?(\d{2,4})',
        ]
        
        for pattern in height_patterns:
            match = re.search(pattern, layer)
            if match:
                height_value = float(match.group(1))
                # Convert from cm or mm to meters
                if height_value > 100:
                    return height_value / 100  # cm → m
                elif height_value > 10:
                    return height_value  # already in m
                else:
                    return height_value / 10  # dm → m
        
        # ⚠️ If cannot detect, return None (don't assume!)
        return None
    
    @staticmethod
    def detect_height_from_layer(layer: str) -> Optional[float]:
        """
        Convenience method for detecting height from layer name only
        
        Args:
            layer: Layer name
            
        Returns:
            Height in meters, or None
        """
        return HeightDetector.detect_height_from_context(layer, None)
