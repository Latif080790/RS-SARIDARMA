"""
Inspect Architecture DXF to understand text patterns
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analisis_volume'))

from dwg_reader import DXFReader

# Load ARS file
dxf_file = r"drawing\dxf\ars\20251108_Plan RS Sari Dharma.dxf"
reader = DXFReader(dxf_file)
success = reader.load_file()

if success:
    # Extract all entities
    reader.extract_all()
    dxf_data = reader.data
    print("\n" + "="*80)
    print("ARSITEKTUR FILE - TEXT INSPECTION")
    print("="*80)
    
    texts = dxf_data.get('texts', [])
    print(f"\nTotal texts: {len(texts)}")
    
    # Sample first 30 texts
    print("\n" + "-"*80)
    print("SAMPLE TEXT CONTENT (First 30):")
    print("-"*80)
    print(f"{'No':<5} {'Layer':<25} {'Content':<50}")
    print("-"*80)
    
    for idx, text in enumerate(texts[:30], 1):
        content = text.get('content', '')
        layer = text.get('layer', '')
        
        # Clean for display (truncate if too long)
        content_display = content[:45] + "..." if len(content) > 45 else content
        layer_display = layer[:22] + "..." if len(layer) > 22 else layer
        
        print(f"{idx:<5} {layer_display:<25} {content_display:<50}")
    
    # Group by layer
    print("\n" + "-"*80)
    print("TEXT COUNT BY LAYER (Top 20):")
    print("-"*80)
    
    layer_counts = {}
    for text in texts:
        layer = text.get('layer', 'Unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    
    sorted_layers = sorted(layer_counts.items(), key=lambda x: x[1], reverse=True)
    
    for layer, count in sorted_layers[:20]:
        print(f"  {layer:<40} : {count:>4} texts")
    
    # Check dimensions
    dimensions = dxf_data.get('dimensions', [])
    print("\n" + "-"*80)
    print(f"DIMENSION SAMPLE (First 10 of {len(dimensions)}):")
    print("-"*80)
    
    for idx, dim in enumerate(dimensions[:10], 1):
        measurement = dim.get('measurement', 0)
        layer = dim.get('layer', '')
        print(f"  {idx}. Layer: {layer:<30} Measurement: {measurement:.2f}")
    
    print("\n" + "="*80)
