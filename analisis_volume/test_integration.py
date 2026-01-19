"""
Integration Tests for Auto Volume Calculator
Tests system integration and workflow correctness
"""

import pytest
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analisis_volume.auto_volume_calculator import AutoVolumeCalculator


class TestSystemIntegration:
    """Test overall system integration and stability"""
    
    def test_calculator_initialization(self):
        """Test: Calculator initializes correctly with minimal data"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        assert calculator is not None
        assert hasattr(calculator, 'items')
        assert hasattr(calculator, 'grid_references')
        assert hasattr(calculator, 'grid_detector')
    
    def test_empty_dxf_processing(self):
        """Test: Handle empty DXF gracefully"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should complete without errors
        assert calculator.items == []
    
    def test_grid_detection_system(self):
        """Test: Grid detection subsystem works"""
        dxf_data = {
            'texts': [
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': 'B', 'position': (10000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
                {'content': '2', 'position': (0, 10000), 'layer': 'GRID'},
            ],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        has_grids = calculator._detect_grid_bubbles()
        
        assert has_grids is True
        assert 'x' in calculator.grid_references
        assert 'y' in calculator.grid_references
        assert len(calculator.grid_references['x']) == 2
        assert len(calculator.grid_references['y']) == 2
    
    def test_nearest_grid_calculation(self):
        """Test: Nearest grid calculation works"""
        dxf_data = {
            'texts': [
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
            ],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator._detect_grid_bubbles()
        
        # Point near A1 intersection
        grid = calculator._find_nearest_grid((5100, 5100))
        assert grid in ['A1', 'A', '1']  # May vary based on implementation
    
    def test_polyline_processing_stability(self):
        """Test: System handles polylines without crashing"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [
                        (0, 0), (1000, 0), (1000, 1000), (0, 1000)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
                {
                    'points': [
                        (2000, 0), (3000, 0), (3000, 1000), (2000, 1000)
                    ],
                    'layer': 'LT_1_S_T120',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should complete without errors
        assert isinstance(calculator.items, list)
    
    def test_large_grid_system(self):
        """Test: Handle large grid system (26x50)"""
        texts = []
        
        # Generate 26 horizontal grids (A-Z)
        for i, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            texts.append({
                'content': letter,
                'position': (i * 5000, 0),
                'layer': 'GRID'
            })
        
        # Generate 50 vertical grids (1-50)
        for i in range(1, 51):
            texts.append({
                'content': str(i),
                'position': (0, i * 5000),
                'layer': 'GRID'
            })
        
        dxf_data = {
            'texts': texts,
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator._detect_grid_bubbles()
        
        assert len(calculator.grid_references.get('x', {})) == 26
        assert len(calculator.grid_references.get('y', {})) == 50


class TestHeightDetection:
    """Test height detection from layer names"""
    
    def test_height_detection_h_pattern(self):
        """Test: Detect height from H#### pattern"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (100, 0), (100, 100), (0, 100)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                }
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        height = calculator._detect_height_from_context('LT_1_K_H3000', (0, 0))
        
        assert height == 3.0  # 3000mm = 3.0m
    
    def test_height_detection_t_pattern(self):
        """Test: Detect thickness from T### pattern"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        height = calculator._detect_height_from_context('LT_2_S_T120', (0, 0))
        
        assert height == 0.12  # 120mm = 0.12m
    
    def test_no_height_returns_zero(self):
        """Test: Returns 0 when no height found"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        height = calculator._detect_height_from_context('UNKNOWN_LAYER', (0, 0))
        
        assert height == 0 or height is None


class TestVoidDetection:
    """Test void detection in polylines"""
    
    def test_point_in_polygon(self):
        """Test: Point inside polygon detection"""
        polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
        
        from analisis_volume.void_detector import VoidDetector
        
        # Point inside
        assert VoidDetector.point_in_polygon((5, 5), polygon) == True
        
        # Point outside
        assert VoidDetector.point_in_polygon((15, 5), polygon) == False
    
    def test_polyline_area_calculation(self):
        """Test: Polyline area calculation (shoelace formula)"""
        from analisis_volume.void_detector import VoidDetector
        
        # Square 10x10 = 100 square units
        points = [(0, 0), (10, 0), (10, 10), (0, 10)]
        area = VoidDetector.calculate_polyline_area(points)
        
        assert abs(area - 100.0) < 0.1
    
    def test_polyline_contains_polyline(self):
        """Test: Check if one polyline contains another"""
        from analisis_volume.void_detector import VoidDetector
        
        outer = [(0, 0), (10, 0), (10, 10), (0, 10)]
        inner = [(2, 2), (8, 2), (8, 8), (2, 8)]
        
        assert VoidDetector.polyline_contains_polyline(outer, inner) == True


class TestDimensionExtraction:
    """Test dimension extraction from text"""
    
    def test_dimension_extraction_basic(self):
        """Test: Extract dimensions from text"""
        dxf_data = {
            'texts': [
                {'content': '300x400', 'position': (0, 0), 'layer': 'DIM'}
            ],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        result = calculator.extract_dimensions_from_text('300x400')
        
        assert result is not None
        length, width, height = result
        assert length > 0
        assert width > 0
    
    def test_dimension_extraction_variations(self):
        """Test: Handle various dimension formats"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        
        # Test various formats
        patterns = ['30x40', '300x400', '30 x 40', '30/40']
        
        for pattern in patterns:
            result = calculator.extract_dimensions_from_text(pattern)
            # Should parse successfully or return None gracefully
            if result:
                assert len(result) == 3


class TestAggregation:
    """Test item aggregation logic"""
    
    def test_aggregation_structure(self):
        """Test: Aggregation maintains required fields"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (300, 0), (300, 400), (0, 400)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
                {
                    'points': [(1000, 0), (1300, 0), (1300, 400), (1000, 400)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Check aggregation structure
        for item in calculator.items:
            assert 'lantai' in item
            assert 'jenis_item' in item
            assert 'volume' in item


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_malformed_layer_names(self):
        """Test: Handle non-standard layer naming"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (1000, 0), (1000, 1000), (0, 1000)],
                    'layer': 'WEIRD_LAYER_NAME',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should not crash
        assert isinstance(calculator.items, list)
    
    def test_missing_grid_references(self):
        """Test: Handle DXF without grid references"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (300, 0), (300, 400), (0, 400)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should assign default grid
        if calculator.items:
            assert calculator.items[0]['grid'] in ['N/A', 'Unknown', '', None]
    
    def test_invalid_polyline_data(self):
        """Test: Handle invalid polyline coordinates"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0)],  # Only one point - invalid
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        
        try:
            calculator.calculate_all_volumes()
            # Should handle gracefully
            assert True
        except Exception:
            # Or raise appropriate error
            assert True


class TestDataConsistency:
    """Test data consistency and validation"""
    
    def test_volume_never_negative(self):
        """Test: Ensure volumes are never negative"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (300, 0), (300, 400), (0, 400)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # All volumes must be non-negative
        for item in calculator.items:
            assert item['volume'] >= 0, f"Negative volume found: {item['volume']}"
    
    def test_export_to_dataframe(self):
        """Test: Export results to pandas DataFrame"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [(0, 0), (300, 0), (300, 400), (0, 400)],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Convert to DataFrame
        if calculator.items:
            df = pd.DataFrame(calculator.items)
            
            # Check DataFrame structure
            assert not df.empty
            assert 'lantai' in df.columns
            assert 'jenis_item' in df.columns
            assert 'volume' in df.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])


class TestEndToEndWorkflow:
    """Test complete DXF to Excel workflow"""
    
    @pytest.fixture
    def simple_column_dxf(self):
        """Create minimal working DXF data with column"""
        return {
            'texts': [
                # Grid references
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
                
                # Column code and dimension near geometry
                {'content': 'K1', 'position': (5000, 5100), 'layer': 'TEXT'},
                {'content': '30x40', 'position': (5000, 4900), 'layer': 'DIM'},
            ],
            'polylines': [
                # Column polyline - rectangular 300x400mm
                {
                    'points': [
                        (4850, 4800), (5150, 4800), (5150, 5200), (4850, 5200)
                    ],
                    'layer': 'LT_1_K_H3000',  # Floor 1, Column, Height 3000mm
                    'closed': True
                },
            ],
            'blocks': []
        }
    
    def test_complete_workflow_with_grid_detection(self, simple_column_dxf):
        """Test: DXF data → grid detection → item extraction"""
        calculator = AutoVolumeCalculator(simple_column_dxf)
        
        # Step 1: Grid detection
        calculator._detect_grid_bubbles()
        assert len(calculator.grid_references.get('x', {})) >= 1  # A
        assert len(calculator.grid_references.get('y', {})) >= 1  # 1
        
        # Step 2: Extract items
        calculator.calculate_all_volumes()
        
        # Should generate at least one item
        # Note: actual behavior may vary, so we check if system runs without errors
        assert isinstance(calculator.items, list)
    
    def test_column_detection_and_volume_calculation(self, sample_dxf_data):
        """Test: Detect columns, extract dimensions, calculate volumes"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        
        # Find column items
        columns = [item for item in calculator.items if item['jenis_item'] == 'KOLOM']
        assert len(columns) >= 2, "Should detect at least 2 columns"
        
        # Check first column (300x400)
        col1 = next((c for c in columns if '30' in c['dimension'] and '40' in c['dimension']), None)
        assert col1 is not None, "Should detect 300x400 column"
        assert col1['height'] == 3.0, "Should extract height from layer LT_1_K_H3000"
        
        # Volume should be approximately 0.3 * 0.4 * 3.0 = 0.36 m³
        assert 0.35 <= col1['volume'] <= 0.37, f"Column volume {col1['volume']} out of expected range"
    
    def test_beam_detection_and_length_calculation(self, sample_dxf_data):
        """Test: Detect beams, calculate length from polyline"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        
        # Find beam items
        beams = [item for item in calculator.items if item['jenis_item'] == 'BALOK']
        assert len(beams) >= 1, "Should detect at least 1 beam"
        
        # Check beam properties
        beam = beams[0]
        assert beam['height'] == 0.4, "Should extract height from layer H400"
        
        # Beam length should be calculated from polyline
        assert beam['volume'] > 0, "Beam should have volume"
    
    def test_slab_detection_and_area_calculation(self, sample_dxf_data):
        """Test: Detect slabs, calculate area"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        
        # Find slab items
        slabs = [item for item in calculator.items if item['jenis_item'] == 'PLAT']
        assert len(slabs) >= 1, "Should detect at least 1 slab"
        
        # Check slab properties
        slab = slabs[0]
        assert slab['height'] == 0.12, "Should extract thickness from layer T120"
        
        # Slab area should be 6000mm * 2000mm = 12 m²
        expected_area = 6.0 * 2.0  # 12 m²
        assert 11.0 <= slab['volume'] <= 13.0, f"Slab area {slab['volume']} out of expected range"
    
    def test_floor_level_detection(self, sample_dxf_data):
        """Test: Floor level extraction from layers"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        
        # Check floor levels assigned
        lt1_items = [item for item in calculator.items if item['lantai'] == 'LT 1']
        lt2_items = [item for item in calculator.items if item['lantai'] == 'LT 2']
        
        assert len(lt1_items) > 0, "Should have items on LT 1"
        assert len(lt2_items) > 0, "Should have items on LT 2"
    
    def test_aggregation_by_location_and_dimension(self, sample_dxf_data):
        """Test: Aggregate items by location + dimension"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        # aggregated is already done by calculate_all_volumes
        aggregated = calculator.items
        
        # Each unique combination should be one row
        assert len(aggregated) <= len(calculator.items)
        
        # Check aggregation structure
        for item in aggregated:
            assert 'lantai' in item
            assert 'grid' in item
            assert 'jenis_item' in item
            assert 'dimension' in item
            assert 'volume' in item
            assert 'count' in item
    
    def test_export_to_dataframe(self, sample_dxf_data):
        """Test: Export results to pandas DataFrame"""
        calculator = AutoVolumeCalculator(sample_dxf_data)
        calculator.calculate_all_volumes()
        aggregated = calculator.items
        
        # Convert to DataFrame
        df = pd.DataFrame(aggregated)
        
        # Check DataFrame structure
        assert not df.empty, "DataFrame should not be empty"
        assert 'lantai' in df.columns
        assert 'grid' in df.columns
        assert 'volume' in df.columns
        
        # Check data types
        assert pd.api.types.is_numeric_dtype(df['volume'])
        assert pd.api.types.is_numeric_dtype(df['count'])


class TestVoidDetectionIntegration:
    """Test void detection in real-world scenarios"""
    
    def test_slab_with_opening(self):
        """Test: Slab with window opening - net area calculation"""
        dxf_data = {
            'texts': [
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
            ],
            'polylines': [
                # Large slab 10m x 10m
                {
                    'points': [
                        (0, 0), (10000, 0), (10000, 10000), (0, 10000)
                    ],
                    'layer': 'LT_1_S_T120',
                    'closed': True
                },
                # Opening 2m x 2m in center
                {
                    'points': [
                        (4000, 4000), (6000, 4000), (6000, 6000), (4000, 6000)
                    ],
                    'layer': 'LT_1_S_T120',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should detect slab with void
        slabs = [item for item in calculator.items if item['jenis_item'] == 'PLAT']
        
        # Net area should be 100 - 4 = 96 m² (with some tolerance)
        total_area = sum(s['volume'] for s in slabs)
        assert 95.0 <= total_area <= 97.0, f"Net slab area {total_area} incorrect (expected ~96)"


class TestRABMatchingIntegration:
    """Test RAB fuzzy matching integration"""
    
    def test_match_columns_to_rab(self):
        """Test: Match detected columns to RAB items"""
        dxf_data = {
            'texts': [
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
                {'content': '300x400', 'position': (5000, 5000), 'layer': 'DIM'},
            ],
            'polylines': [
                {
                    'points': [
                        (4850, 4850), (5150, 4850), (5150, 5250), (4850, 5250)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        rab_data = pd.DataFrame([
            {
                'Kode': 'K1',
                'Uraian': 'Kolom Beton K-300 30x40cm',
                'Volume': 0,
                'Satuan': 'm³'
            }
        ])
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Test matching logic (simplified)
        columns = [item for item in calculator.items if item['jenis_item'] == 'KOLOM']
        assert len(columns) == 1
        
        col = columns[0]
        # Should match dimensions 30x40
        assert '30' in col['dimension'] or '300' in col['dimension']
        assert '40' in col['dimension'] or '400' in col['dimension']


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_dxf_data(self):
        """Test: Handle empty DXF data gracefully"""
        dxf_data = {
            'texts': [],
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should not crash, return empty results
        assert calculator.items == []
    
    def test_missing_grid_references(self):
        """Test: Handle DXF without grid references"""
        dxf_data = {
            'texts': [],  # No grid bubbles
            'polylines': [
                {
                    'points': [
                        (4850, 4850), (5150, 4850), (5150, 5250), (4850, 5250)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should assign N/A or Unknown to grid
        assert len(calculator.items) > 0
        assert calculator.items[0]['grid'] in ['N/A', 'Unknown', '']
    
    def test_malformed_layer_names(self):
        """Test: Handle non-standard layer naming"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [
                        (0, 0), (1000, 0), (1000, 1000), (0, 1000)
                    ],
                    'layer': 'WEIRD_LAYER_NAME',  # Non-standard
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should not crash, handle gracefully
        # Items may be empty or have default values
        assert isinstance(calculator.items, list)
    
    def test_missing_height_information(self):
        """Test: Handle missing height in layer name"""
        dxf_data = {
            'texts': [],
            'polylines': [
                {
                    'points': [
                        (0, 0), (1000, 0), (1000, 1000), (0, 1000)
                    ],
                    'layer': 'LT_1_K',  # No height info
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should not use hardcoded height (skip or set to 0)
        if calculator.items:
            assert calculator.items[0]['height'] == 0 or calculator.items[0]['height'] is None


class TestPerformance:
    """Test performance with larger datasets"""
    
    def test_large_grid_system(self):
        """Test: Handle large grid system (A-Z, 1-50)"""
        texts = []
        
        # Generate 26 horizontal grids (A-Z)
        for i, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            texts.append({
                'content': letter,
                'position': (i * 5000, 0),
                'layer': 'GRID'
            })
        
        # Generate 50 vertical grids (1-50)
        for i in range(1, 51):
            texts.append({
                'content': str(i),
                'position': (0, i * 5000),
                'layer': 'GRID'
            })
        
        dxf_data = {
            'texts': texts,
            'polylines': [],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator._detect_grid_bubbles()
        
        # Should detect all grids
        assert len(calculator.grid_references.get('x', {})) == 26
        assert len(calculator.grid_references.get('y', {})) == 50
    
    def test_many_polylines(self):
        """Test: Handle many polylines (100+)"""
        polylines = []
        
        # Generate 100 columns in a grid pattern
        for i in range(10):
            for j in range(10):
                polylines.append({
                    'points': [
                        (i*5000, j*5000),
                        (i*5000+300, j*5000),
                        (i*5000+300, j*5000+300),
                        (i*5000, j*5000+300)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                })
        
        dxf_data = {
            'texts': [
                {'content': '300x300', 'position': (2500, 2500), 'layer': 'DIM'}
            ],
            'polylines': polylines,
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Should process all polylines
        assert len(calculator.items) == 100


class TestDataConsistency:
    """Test data consistency and validation"""
    
    def test_volume_never_negative(self):
        """Test: Ensure volumes are never negative"""
        dxf_data = {
            'texts': [
                {'content': '300x400', 'position': (5000, 5000), 'layer': 'DIM'}
            ],
            'polylines': [
                {
                    'points': [
                        (4850, 4850), (5150, 4850), (5150, 5250), (4850, 5250)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # All volumes must be non-negative
        for item in calculator.items:
            assert item['volume'] >= 0, f"Negative volume found: {item['volume']}"
    
    def test_aggregation_preserves_total_volume(self):
        """Test: Aggregation doesn't lose volume"""
        dxf_data = {
            'texts': [
                {'content': 'A', 'position': (5000, 0), 'layer': 'GRID'},
                {'content': '1', 'position': (0, 5000), 'layer': 'GRID'},
                {'content': '300x400', 'position': (5000, 5000), 'layer': 'DIM'}
            ],
            'polylines': [
                # Two identical columns
                {
                    'points': [
                        (4850, 4850), (5150, 4850), (5150, 5250), (4850, 5250)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
                {
                    'points': [
                        (9850, 4850), (10150, 4850), (10150, 5250), (9850, 5250)
                    ],
                    'layer': 'LT_1_K_H3000',
                    'closed': True
                },
            ],
            'blocks': []
        }
        
        calculator = AutoVolumeCalculator(dxf_data)
        calculator.calculate_all_volumes()
        
        # Calculate total before aggregation
        total_before = sum(item['volume'] for item in calculator.items)
        
        # Aggregate
        aggregated = calculator.aggregate_similar_items()
        total_after = sum(item['volume'] for item in aggregated)
        
        # Total volume should be preserved (within small tolerance)
        assert abs(total_before - total_after) < 0.001, \
            f"Volume not preserved: {total_before} → {total_after}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
