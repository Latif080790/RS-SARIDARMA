"""
Item Aggregator Module
Handles aggregation of construction items with location breakdown.
Extracted from auto_volume_calculator.py for better maintainability.
"""

from typing import List, Dict


class ItemAggregator:
    """Aggregates construction items with multi-key grouping by lantai, grid, item type, and dimensions"""
    
    @staticmethod
    def aggregate_similar_items(items: List[Dict]) -> List[Dict]:
        """
        ✅ CRITICAL FIX: Aggregate with breakdown per LOCATION (Lantai + Grid + Item)
        
        Instead of grouping all items of same dimension together, this keeps them separate
        by location to enable:
        - Per-zone progress tracking for mandor
        - Floor-by-floor volume calculation
        - Specific grid identification for field verification
        
        Args:
            items: List of item dictionaries with lantai, grid, item name, kode, dimensions
            
        Returns:
            List of aggregated items with jumlah and volume summed per location
        """
        print("\n→ Aggregating with location breakdown (Lantai + Grid + Item)...")
        
        aggregated = {}
        
        for item in items:
            # Ensure all dimensions have values (not None)
            panjang = item.get('panjang') or 0
            lebar = item.get('lebar') or 0
            tinggi = item.get('tinggi') or 0
            
            # ✅ NEW: Create key based on LANTAI + GRID + ITEM + DIMENSIONS
            # This enables per-zone opname for mandor!
            lantai = item.get('lantai', 'Unknown')
            grid = item.get('grid', 'Unknown')
            item_name = item.get('item', 'Unknown')
            kode = item.get('kode', '')
            
            # Key format: "Lantai_Grid_Item_Kode_Dimensions"
            key = f"{lantai}_{grid}_{item_name}_{kode}_{panjang:.3f}_{lebar:.3f}_{tinggi:.3f}"
            
            if key in aggregated:
                # Same lantai, grid, item, dimensions → aggregate
                aggregated[key]['jumlah'] += item.get('jumlah', 1)
                aggregated[key]['volume'] += item.get('volume', 0)
            else:
                # New unique combination → keep separate
                aggregated[key] = item.copy()
        
        result_items = list(aggregated.values())
        print(f"  ✓ Aggregated to {len(result_items)} unique items (with location breakdown)")
        
        return result_items
    
    @staticmethod
    def aggregate_by_location_only(items: List[Dict]) -> List[Dict]:
        """
        Alternative aggregation: group by location only (lantai + grid)
        Useful for summary reports
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List aggregated by location
        """
        aggregated = {}
        
        for item in items:
            lantai = item.get('lantai', 'Unknown')
            grid = item.get('grid', 'Unknown')
            
            key = f"{lantai}_{grid}"
            
            if key in aggregated:
                aggregated[key]['jumlah'] += item.get('jumlah', 1)
                aggregated[key]['volume'] += item.get('volume', 0)
            else:
                aggregated[key] = {
                    'lantai': lantai,
                    'grid': grid,
                    'jumlah': item.get('jumlah', 1),
                    'volume': item.get('volume', 0)
                }
        
        return list(aggregated.values())
    
    @staticmethod
    def aggregate_by_item_type(items: List[Dict]) -> List[Dict]:
        """
        Alternative aggregation: group by item type only (across all locations)
        Useful for total material estimation
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List aggregated by item type
        """
        aggregated = {}
        
        for item in items:
            item_name = item.get('item', 'Unknown')
            panjang = item.get('panjang') or 0
            lebar = item.get('lebar') or 0
            tinggi = item.get('tinggi') or 0
            
            key = f"{item_name}_{panjang:.3f}_{lebar:.3f}_{tinggi:.3f}"
            
            if key in aggregated:
                aggregated[key]['jumlah'] += item.get('jumlah', 1)
                aggregated[key]['volume'] += item.get('volume', 0)
            else:
                aggregated[key] = item.copy()
        
        return list(aggregated.values())
