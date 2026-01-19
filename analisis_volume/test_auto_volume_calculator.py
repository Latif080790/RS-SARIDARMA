"""
Priority #9: Comprehensive Unit Tests for AutoVolumeCalculator
Tests critical methods: grid detection, void detection, dimension extraction, aggregation
"""

import pytest
import sys
import os
from typing import Dict, List

# Add parent directory to path to support both direct execution and pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analisis_volume.auto_volume_calculator import AutoVolumeCalculator


class TestGridDetection:
    """Test grid detection and proximity-based assignment"""
    
    def setup_method(self):
        """Setup test data"""
        self.dxf_data = {
            'texts': [
                # Grid bubbles (horizontal - vary in Y axis, letters run vertically)
                {'content': 'A', 'position': (5000, 1000), 'layer': 'GRID'},
                {'content': 'B', 'position': (10000, 1000), 'layer': 'GRID'},
                {'content': 'C', 'position': (15000, 1000), 'layer': 'GRID'},
                
                # Grid bubbles (vertical - vary in X axis, numbers run horizontally)
                {'content': '1', 'position': (1000, 5000), 'layer': 'GRID'},
                {'content': '2', 'position': (1000, 10000), 'layer': 'GRID'},
                {'content': '3', 'position': (1000, 15000), 'layer': 'GRID'},
                
                # Non-grid texts (should be ignored)
                {'content': 'K1', 'position': (7000, 7000), 'layer': 'STRUCTURE'},
                {'content': 'Balok', 'position': (8000, 8000), 'layer': 'STRUCTURE'},
            ]
        }
        self.calculator = AutoVolumeCalculator(self.dxf_data)
    
    def test_detect_grid_bubbles(self):
        """Test grid bubble detection"""
        self.calculator._detect_grid_bubbles()
        
        # Check horizontal grids detected (stored in x with their x-coordinate)
        assert 'A' in self.calculator.grid_references.get('x', {})
        assert 'B' in self.calculator.grid_references.get('x', {})
        assert 'C' in self.calculator.grid_references.get('x', {})
        
        # Check vertical grids detected (stored in y with their y-coordinate)
        assert '1' in self.calculator.grid_references.get('y', {})
        assert '2' in self.calculator.grid_references.get('y', {})
        assert '3' in self.calculator.grid_references.get('y', {})
        
        # Verify positions stored correctly
        assert self.calculator.grid_references['x']['A'] == 5000
        assert self.calculator.grid_references['y']['1'] == 5000
    
    def test_find_nearest_grid(self):
        """Test proximity-based grid assignment"""
        self.calculator._detect_grid_bubbles()
        
        # Test position near grid intersection A-1 (A at x=5000, 1 at y=5000)
        position = (5100, 5100)
        grid_ref = self.calculator._find_nearest_grid(position)
        assert grid_ref == 'A1'
        
        # Test position near B-2 (B at x=10000, 2 at y=10000)
        position = (10100, 10100)
        grid_ref = self.calculator._find_nearest_grid(position)
        assert grid_ref == 'B2'
        
        # Test position far from any grid (still returns nearest, even if far)
        # Note: Implementation doesn't have distance threshold, always returns nearest
        position = (50000, 50000)
        grid_ref = self.calculator._find_nearest_grid(position)
        assert grid_ref == 'C3'  # Nearest to C (x=15000) and 3 (y=15000)
    
    def test_grid_detection_edge_cases(self):
        """Test edge cases in grid detection"""
        # Empty data
        calculator_empty = AutoVolumeCalculator({'texts': []})
        calculator_empty._detect_grid_bubbles()
        assert len(calculator_empty.grid_references.get('x', {})) == 0
        assert len(calculator_empty.grid_references.get('y', {})) == 0
        
        # Only numbers (no letters)
        dxf_numbers_only = {
            'texts': [
                {'content': '1', 'position': (5000, 1000), 'layer': 'GRID'},
                {'content': '2', 'position': (10000, 1000), 'layer': 'GRID'},
            ]
        }
        calculator_numbers = AutoVolumeCalculator(dxf_numbers_only)
        calculator_numbers._detect_grid_bubbles()
        assert '1' in calculator_numbers.grid_references.get('y', {})
        assert '2' in calculator_numbers.grid_references.get('y', {})


class TestVoidDetection:
    """Test void detection for plat lantai"""
    
    def setup_method(self):
        """Setup test polylines with voids"""
        # Outer polyline (10m x 10m = 100 m²)
        self.outer_polyline = [
            (0, 0), (10000, 0), (10000, 10000), (0, 10000), (0, 0)
        ]
        
        # Inner void (2m x 2m = 4 m²) - lift shaft
        self.void_polyline = [
            (2000, 2000), (4000, 2000), (4000, 4000), (2000, 4000), (2000, 2000)
        ]
        
        # Non-void polyline (outside outer)
        self.outside_polyline = [
            (20000, 20000), (21000, 20000), (21000, 21000), (20000, 21000), (20000, 20000)
        ]
        
        self.dxf_data = {'polylines': [], 'texts': []}
        self.calculator = AutoVolumeCalculator(self.dxf_data)
    
    def test_point_in_polygon(self):
        """Test point-in-polygon detection"""
        # Point inside outer polyline
        assert self.calculator._point_in_polygon((5000, 5000), self.outer_polyline) == True
        
        # Point outside outer polyline
        assert self.calculator._point_in_polygon((15000, 15000), self.outer_polyline) == False
        
        # Point on edge (should be considered inside)
        assert self.calculator._point_in_polygon((10000, 5000), self.outer_polyline) == True
    
    def test_polyline_contains_polyline(self):
        """Test if one polyline contains another"""
        # Void is inside outer
        assert self.calculator._polyline_contains_polyline(self.outer_polyline, self.void_polyline) == True
        
        # Outside polyline is NOT inside outer
        assert self.calculator._polyline_contains_polyline(self.outer_polyline, self.outside_polyline) == False
        
        # Outer does NOT contain itself
        assert self.calculator._polyline_contains_polyline(self.outer_polyline, self.outer_polyline) == False
    
    def test_calculate_polyline_area(self):
        """Test area calculation using Shoelace formula"""
        # Note: coordinates are in mm, area calculation returns mm² / 1000000 = m²
        # 10000mm x 10000mm = 100,000,000 mm² = 100 m²
        area_outer = self.calculator._calculate_polyline_area(self.outer_polyline)
        # Area is returned in mm², need to convert to m²
        area_outer_m2 = area_outer / 1000000
        assert abs(area_outer_m2 - 100.0) < 0.01
        
        # 2000mm x 2000mm = 4,000,000 mm² = 4 m²
        area_void = self.calculator._calculate_polyline_area(self.void_polyline)
        area_void_m2 = area_void / 1000000
        assert abs(area_void_m2 - 4.0) < 0.01
    
    def test_detect_voids_in_polyline(self):
        """Test void detection and area subtraction"""
        all_polylines = [
            {'points': self.outer_polyline, 'layer': 'PLAT'},
            {'points': self.void_polyline, 'layer': 'PLAT'},
            {'points': self.outside_polyline, 'layer': 'PLAT'},
        ]
        
        # Method returns tuple: (net_area, voids_list)
        net_area, voids = self.calculator._detect_voids_in_polyline(self.outer_polyline, all_polylines)
        
        # Should find 1 void
        assert len(voids) == 1
        
        # Net area = 100 - 4 = 96 m² (already converted by method)
        assert abs(net_area - 96.0) < 0.1  # Allow 0.1 tolerance for conversion
        
        # Check void details
        assert abs(voids[0]['area'] - 4.0) < 0.1


class TestDimensionExtraction:
    """Test dimension extraction with DimensionParser"""
    
    def setup_method(self):
        """Setup calculator"""
        self.calculator = AutoVolumeCalculator({'texts': []})
    
    def test_extract_standard_formats(self):
        """Test standard dimension formats"""
        # Format: 20x30 (cm)
        result = self.calculator.extract_dimensions_from_text("K1 (20x30)")
        assert result is not None
        assert abs(result[0] - 0.20) < 0.01
        assert abs(result[1] - 0.30) < 0.01
        
        # Format: 15/25 (balok format, cm)
        result = self.calculator.extract_dimensions_from_text("Balok 15/25")
        assert result is not None
        assert abs(result[0] - 0.15) < 0.01
        assert abs(result[1] - 0.25) < 0.01
    
    def test_extract_with_units(self):
        """Test extraction with explicit units"""
        # 200x300mm = 0.2m x 0.3m
        result = self.calculator.extract_dimensions_from_text("K1 200x300mm")
        assert result is not None
        assert abs(result[0] - 0.20) < 0.01
        assert abs(result[1] - 0.30) < 0.01
        
        # 20x30cm = 0.2m x 0.3m
        result = self.calculator.extract_dimensions_from_text("K1 20x30cm")
        assert result is not None
        assert abs(result[0] - 0.20) < 0.01
        assert abs(result[1] - 0.30) < 0.01
    
    def test_extract_with_height(self):
        """Test extraction with height notation"""
        # H=400 (cm) = 4.0m
        result = self.calculator.extract_dimensions_from_text("Kolom H=400")
        assert result is not None
        assert result[2] is not None
        assert abs(result[2] - 4.0) < 0.01
    
    def test_extract_edge_cases(self):
        """Test edge cases"""
        # No dimensions
        result = self.calculator.extract_dimensions_from_text("Kolom K1")
        assert result is None
        
        # Empty string
        result = self.calculator.extract_dimensions_from_text("")
        assert result is None
        
        # Invalid format
        result = self.calculator.extract_dimensions_from_text("ABC DEF")
        assert result is None


class TestAggregation:
    """Test item aggregation with location breakdown"""
    
    def setup_method(self):
        """Setup calculator with sample items"""
        self.calculator = AutoVolumeCalculator({'texts': []})
        
        # Sample items (same dimensions, different locations)
        self.calculator.items = [
            {
                'item': 'Kolom K1',
                'kode': 'K1',
                'panjang': 0.30,
                'lebar': 0.30,
                'tinggi': 4.0,
                'volume': 0.36,
                'lantai': 'Lantai 1',
                'grid': 'A-1',
                'satuan': 'm³',
                'jumlah': 1  # ✅ Initialize jumlah
            },
            {
                'item': 'Kolom K1',
                'kode': 'K1',
                'panjang': 0.30,
                'lebar': 0.30,
                'tinggi': 4.0,
                'volume': 0.36,
                'lantai': 'Lantai 1',
                'grid': 'B-2',  # Different grid
                'satuan': 'm³',
                'jumlah': 1
            },
            {
                'item': 'Kolom K1',
                'kode': 'K1',
                'panjang': 0.30,
                'lebar': 0.30,
                'tinggi': 4.0,
                'volume': 0.36,
                'lantai': 'Lantai 2',  # Different lantai
                'grid': 'A-1',
                'satuan': 'm³',
                'jumlah': 1
            },
        ]
    
    def test_aggregate_by_location(self):
        """Test aggregation with location breakdown"""
        original_count = len(self.calculator.items)
        self.calculator.aggregate_similar_items()
        
        # Should have 3 separate items (different locations)
        assert len(self.calculator.items) == 3
        
        # Verify each has correct location
        locations = [(item['lantai'], item['grid']) for item in self.calculator.items]
        assert ('Lantai 1', 'A-1') in locations
        assert ('Lantai 1', 'B-2') in locations
        assert ('Lantai 2', 'A-1') in locations
    
    def test_aggregate_same_location(self):
        """Test aggregation when items have same location"""
        # Add duplicate at same location
        self.calculator.items.append({
            'item': 'Kolom K1',
            'kode': 'K1',
            'panjang': 0.30,
            'lebar': 0.30,
            'tinggi': 4.0,
            'volume': 0.36,
            'lantai': 'Lantai 1',
            'grid': 'A-1',  # Same location as first item
            'satuan': 'm³',
            'jumlah': 1
        })
        
        self.calculator.aggregate_similar_items()
        
        # Should aggregate items with same location
        lantai1_a1 = [item for item in self.calculator.items 
                      if item['lantai'] == 'Lantai 1' and item['grid'] == 'A-1']
        
        assert len(lantai1_a1) == 1
        assert lantai1_a1[0]['jumlah'] == 2
        assert abs(lantai1_a1[0]['volume'] - 0.72) < 0.01  # 0.36 * 2


class TestHeightDetection:
    """Test height detection from layer context"""
    
    def setup_method(self):
        """Setup calculator"""
        self.calculator = AutoVolumeCalculator({'texts': []})
    
    def test_detect_height_from_layer_patterns(self):
        """Test various height patterns in layer names"""
        # Pattern: H400
        height = self.calculator._detect_height_from_context("KOLOM_H400", (0, 0))
        assert height is not None
        assert abs(height - 4.0) < 0.01
        
        # Pattern: T=350
        height = self.calculator._detect_height_from_context("BALOK_T=350", (0, 0))
        assert height is not None
        assert abs(height - 3.5) < 0.01
        
        # Pattern: HEIGHT_300
        height = self.calculator._detect_height_from_context("STRUCTURE_HEIGHT_300", (0, 0))
        assert height is not None
        assert abs(height - 3.0) < 0.01
    
    def test_detect_height_no_pattern(self):
        """Test when no height pattern found"""
        height = self.calculator._detect_height_from_context("KOLOM_K1", (0, 0))
        assert height is None
        
        height = self.calculator._detect_height_from_context("", (0, 0))
        assert height is None


def run_tests():
    """Run all tests and display results"""
    print("\n" + "="*70)
    print("PRIORITY #9: AUTO VOLUME CALCULATOR UNIT TESTS")
    print("="*70 + "\n")
    
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()
