"""
Void Detector Module
Handles void detection in polylines using spatial analysis.
Extracted from auto_volume_calculator.py for better maintainability.
"""

from typing import List, Tuple, Dict


class VoidDetector:
    """Detects voids (holes) inside polylines using spatial containment"""
    
    @staticmethod
    def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        """
        Check if point is inside polygon using ray casting algorithm
        
        Args:
            point: (x, y) coordinates
            polygon: List of (x, y) coordinates forming the polygon
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    @staticmethod
    def polyline_contains_polyline(outer: List[Tuple[float, float]], 
                                   inner: List[Tuple[float, float]]) -> bool:
        """
        Check if outer polyline contains inner polyline (for void detection)
        
        Args:
            outer: Outer polyline points
            inner: Inner polyline points
            
        Returns:
            True if all points of inner are inside outer
        """
        # Check if all points of inner polyline are inside outer polyline
        for point in inner:
            if not VoidDetector.point_in_polygon(point, outer):
                return False
        return True
    
    @staticmethod
    def calculate_polyline_area(points: List[Tuple[float, float]]) -> float:
        """
        Calculate polygon area using Shoelace formula
        
        Args:
            points: List of (x, y) coordinates
            
        Returns:
            Area in the same units as input coordinates (usually mm²)
        """
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        n = len(points)
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2.0
    
    @staticmethod
    def detect_voids_in_polyline(outer_points: List[Tuple[float, float]], 
                                 all_polylines: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Detect void polylines inside outer polyline and calculate net area
        
        Args:
            outer_points: Points of the outer polyline
            all_polylines: List of all polyline dictionaries to check for voids
            
        Returns:
            Tuple of (net_area in m², list of void dictionaries)
        """
        # Calculate outer area
        outer_area = VoidDetector.calculate_polyline_area(outer_points)
        
        # Convert to square meters if needed
        if outer_area > 100000:  # Probably in mm²
            outer_area = outer_area / 1000000
        elif outer_area > 1000:  # Probably in cm²
            outer_area = outer_area / 10000
        
        # Find potential void polylines
        voids = []
        total_void_area = 0.0
        
        for poly_dict in all_polylines:
            inner_points = poly_dict.get('points', [])
            if len(inner_points) < 3:
                continue
            
            # Skip if same as outer (compare first points)
            if len(outer_points) > 0 and len(inner_points) > 0:
                if outer_points[0] == inner_points[0]:
                    continue
            
            # Check if inner is contained by outer
            if VoidDetector.polyline_contains_polyline(outer_points, inner_points):
                void_area = VoidDetector.calculate_polyline_area(inner_points)
                
                # Convert to square meters
                if void_area > 100000:
                    void_area = void_area / 1000000
                elif void_area > 1000:
                    void_area = void_area / 10000
                
                voids.append({
                    'points': inner_points,
                    'area': void_area,
                    'layer': poly_dict.get('layer', 'unknown')
                })
                total_void_area += void_area
        
        net_area = outer_area - total_void_area
        
        # Validation: warn if void ratio too high
        if outer_area > 0:
            void_ratio = (total_void_area / outer_area) * 100
            if void_ratio > 30:
                print(f"    ⚠️  WARNING: Void ratio {void_ratio:.1f}% seems high (outer: {outer_area:.2f} m², voids: {total_void_area:.2f} m²)")
        
        return net_area, voids
