#!/usr/bin/env python3
"""
Test script for the Route Search System
Demonstrates the system with predefined test cases
"""

from route_search_osm import RouteSearchSystem


def test_basic_route():
    """Test a basic route search between two landmarks."""
    print("\n" + "="*70)
    print("TEST 1: Basic Route Search")
    print("="*70)
    
    try:
        # Initialize system
        system = RouteSearchSystem("Addis Ababa, Ethiopia")
        
        # Test with well-known landmarks
        start = "Bole, Addis Ababa"
        goal = "Meskel Square, Addis Ababa"
        
        print(f"\nSearching route from '{start}' to '{goal}'...")
        result = system.search_route(start, goal)
        
        if 'error' not in result:
            print("\n✅ Test 1 PASSED: Route found successfully")
            return True
        else:
            print(f"\n⚠️ Test 1 WARNING: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        return False


def test_same_location():
    """Test the edge case where start equals goal."""
    print("\n" + "="*70)
    print("TEST 2: Same Location (Edge Case)")
    print("="*70)
    
    try:
        system = RouteSearchSystem("Addis Ababa, Ethiopia")
        
        location = "Meskel Square, Addis Ababa"
        
        print(f"\nTesting with start = goal = '{location}'...")
        result = system.search_route(location, location)
        
        if result.get('error') == 'already_at_destination':
            print("\n✅ Test 2 PASSED: Correctly detected same location")
            return True
        else:
            print("\n❌ Test 2 FAILED: Did not detect same location")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        return False


def test_invalid_location():
    """Test handling of invalid location."""
    print("\n" + "="*70)
    print("TEST 3: Invalid Location (Error Handling)")
    print("="*70)
    
    try:
        system = RouteSearchSystem("Addis Ababa, Ethiopia")
        
        start = "Bole, Addis Ababa"
        goal = "ThisPlaceDoesNotExist12345XYZ"
        
        print(f"\nTesting with invalid goal: '{goal}'...")
        result = system.search_route(start, goal)
        
        if result.get('error') == 'goal_not_found':
            print("\n✅ Test 3 PASSED: Correctly handled invalid location")
            return True
        else:
            print("\n❌ Test 3 FAILED: Did not handle invalid location properly")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*15 + "ROUTE SEARCH SYSTEM - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Basic Route Search", test_basic_route()))
    results.append(("Same Location Edge Case", test_same_location()))
    results.append(("Invalid Location Handling", test_invalid_location()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
    
    print("="*70)


if __name__ == "__main__":
    main()
