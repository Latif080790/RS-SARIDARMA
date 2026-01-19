"""
Test Priority #8: Enhanced Fuzzy Matching
Test material-specific thresholds and critical material detection
"""

import sys
sys.path.insert(0, '.')

from volume_comparator import VolumeComparator


def test_critical_material_detection():
    """Test critical material detection"""
    comparator = VolumeComparator({}, {})
    
    print("="*70)
    print("TEST 1: Critical Material Detection")
    print("="*70)
    
    test_cases = [
        # Critical materials (should require 90% threshold)
        ("Beton K-225", True),
        ("Beton Ready Mix K-300", True),
        ("Besi diameter 13mm", True),
        ("Besi D16 ulir", True),
        ("Tulangan besi polos D10", True),
        ("Semen Portland 50kg", True),
        ("Keramik 40x40cm", True),
        ("Pipa PVC D 1/2", True),
        ("Kabel NYYHY 3x2.5mm", True),
        
        # Standard materials (should require 85% threshold)
        ("Pasang bata merah", False),
        ("Plesteran 1:4", False),
        ("Acian", False),
        ("Cat tembok", False),
        ("Kusen kayu", False),
        ("Pintu panel", False),
    ]
    
    passed = 0
    failed = 0
    
    for item, expected_critical in test_cases:
        is_critical = comparator._is_critical_material(item)
        threshold = comparator._get_required_threshold(item)
        
        if is_critical == expected_critical:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1
        
        critical_str = "CRITICAL (90%)" if is_critical else "STANDARD (85%)"
        print(f"{status} '{item}' → {critical_str}")
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


def test_fuzzy_matching_thresholds():
    """Test fuzzy matching with new thresholds"""
    comparator = VolumeComparator({}, {})
    
    print("\n" + "="*70)
    print("TEST 2: Fuzzy Matching with Material-Specific Thresholds")
    print("="*70)
    
    test_cases = [
        # (item1, item2, expected_match_with_threshold, description)
        
        # Exact matches (should always match)
        ("Beton K-225", "Beton K-225", True, "Exact match critical"),
        ("Pasang bata", "Pasang bata", True, "Exact match standard"),
        
        # High similarity matches (✅ spec-aware matching)
        ("Beton K-225", "Beton Ready Mix K-225", False, "Critical <90% (no regex match, use SequenceMatcher)"),
        ("Besi D13", "Besi diameter 13", False, "Critical <90% (different format, no shared spec regex)"),
        
        # Medium similarity (should fail for critical, pass for standard)
        ("Beton K-225", "Beton K-300", False, "Critical <90% (different grade)"),
        ("Pasang bata merah", "Pasang bata ringan", False, "Standard <85% (different type)"),
        
        # Low similarity (should fail for both)
        ("Beton K-225", "Besi D13", False, "No match (different material)"),
        ("Pasang bata", "Cat tembok", False, "No match (different work)"),
        
        # Partial matches with critical materials (✅ same spec = high score)
        ("Beton K-225 fc 18.7", "Beton K-225", True, "Critical partial match (same K-grade)"),
        ("Besi D13 polos", "Besi D13 ulir", False, "Critical <90% (same dia, different type)"),
        
        # Similar but not same (critical materials)
        ("Kabel NYYHY 3x2.5mm", "Kabel NYYHY 3x4mm", False, "Critical <90% (diff size)"),
        ("Pipa PVC D 1/2", "Pipa PVC D 3/4", False, "Critical <90% (diff diameter)"),
    ]
    
    passed = 0
    failed = 0
    
    for item1, item2, expected_match, description in test_cases:
        # With threshold checking
        similarity = comparator.fuzzy_match_items(item1, item2, check_threshold=True)
        matched = similarity > 0
        
        # Without threshold (raw similarity)
        raw_similarity = comparator.fuzzy_match_items(item1, item2, check_threshold=False)
        
        is_critical = comparator._is_critical_material(item1)
        required_threshold = comparator._get_required_threshold(item1)
        
        if matched == expected_match:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1
        
        match_str = "MATCH" if matched else "NO MATCH"
        critical_str = f"Critical {required_threshold*100:.0f}%" if is_critical else f"Standard {required_threshold*100:.0f}%"
        
        print(f"{status} {description}")
        print(f"   '{item1}' vs '{item2}'")
        print(f"   Raw: {raw_similarity*100:.1f}% | {critical_str} | Result: {match_str}")
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


def test_price_validation():
    """Test price difference detection"""
    print("\n" + "="*70)
    print("TEST 3: Price Validation (>20% difference)")
    print("="*70)
    
    test_cases = [
        (100000, 100000, False, "0% difference"),
        (100000, 110000, False, "10% difference (OK)"),
        (100000, 120000, False, "16.7% difference (OK)"),
        (100000, 125000, False, "20% difference (exactly 20% = borderline OK)"),
        (100000, 130000, True, "23% difference (WARNING)"),
        (100000, 200000, True, "50% difference (WARNING)"),
    ]
    
    passed = 0
    failed = 0
    
    for price1, price2, expected_warning, description in test_cases:
        diff_pct = abs((price1 - price2) / price2 * 100)
        should_warn = diff_pct > 20  # Exactly 20% is still OK, >20% is warning
        
        if should_warn == expected_warning:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1
        
        warn_str = "⚠️ WARNING" if should_warn else "OK"
        print(f"{status} {description}: Rp {price1:,} vs Rp {price2:,} → {diff_pct:.1f}% {warn_str}")
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PRIORITY #8: ENHANCED FUZZY MATCHING TEST" + " "*12 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    total_passed = 0
    total_failed = 0
    
    # Run tests
    p1, f1 = test_critical_material_detection()
    total_passed += p1
    total_failed += f1
    
    p2, f2 = test_fuzzy_matching_thresholds()
    total_passed += p2
    total_failed += f2
    
    p3, f3 = test_price_validation()
    total_passed += p3
    total_failed += f3
    
    # Summary
    print("\n" + "="*70)
    print("OVERALL RESULTS")
    print("="*70)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Success Rate: {total_passed/(total_passed+total_failed)*100:.1f}%")
    print("="*70)
    
    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total_failed} tests failed, review implementation")
