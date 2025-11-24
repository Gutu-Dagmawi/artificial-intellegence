#!/usr/bin/env python3
"""
Example usage of the Route Search System
Shows how to use the system programmatically
"""

from route_search_osm import RouteSearchSystem


def example_1_basic_usage():
    """Example 1: Basic route search with visualization."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage with Algorithm Selection")
    print("="*70)
    
    # Initialize the system
    system = RouteSearchSystem("Addis Ababa, Ethiopia")
    
    # Define locations
    start_loc = "Bole, Addis Ababa"
    goal_loc = "Meskel Square, Addis Ababa"
    
    # Search for a route
    result = system.search_route(
        start_location=start_loc,
        goal_location=goal_loc
    )
    
    # Check if route was found
    if 'error' not in result:
        distance_km = result['optimal_distance'] / 1000
        
        print(f"\n✅ Route found!")
        print(f"   Optimal distance: {distance_km:.2f} km")
        
        # Visualize with algorithm selection
        print("\n📊 Opening visualization with algorithm selection...")
        system.visualize_with_algorithm_selection(
            result,
            start_loc,
            goal_loc
        )


def example_2_compare_algorithms():
    """Example 2: Compare all three algorithms."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Algorithm Comparison")
    print("="*70)
    
    system = RouteSearchSystem("Addis Ababa, Ethiopia")
    
    result = system.search_route(
        start_location="Bole Airport, Addis Ababa",
        goal_location="Piazza, Addis Ababa"
    )
    
    if 'error' not in result:
        print("\n📊 Algorithm Efficiency:")
        for algo, data in result['results'].items():
            print(f"\n{algo}:")
            print(f"  - Nodes explored: {data['nodes_explored']}")
            print(f"  - Path length: {len(data['path'])} nodes")
            print(f"  - Distance: {data['distance']/1000:.2f} km")


def example_3_programmatic_access():
    """Example 3: Access path details programmatically."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Programmatic Access")
    print("="*70)
    
    system = RouteSearchSystem("Addis Ababa, Ethiopia")
    
    # Get node IDs directly
    start_node = system.geocode_location("Bole, Addis Ababa")
    goal_node = system.geocode_location("Meskel Square, Addis Ababa")
    
    if start_node and goal_node:
        # Run A* search directly
        path, stats = system.astar_search(start_node, goal_node)
        
        if path:
            distance = system.calculate_path_distance(path)
            print(f"\n✅ A* Search Results:")
            print(f"   Path: {path[:5]}... (showing first 5 nodes)")
            print(f"   Total nodes in path: {len(path)}")
            print(f"   Distance: {distance:.2f} meters")
            print(f"   Nodes explored: {stats['nodes_explored']}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*10 + "ROUTE SEARCH SYSTEM - USAGE EXAMPLES")
    print("="*70)
    
    # Run examples
    example_1_basic_usage()
    example_2_compare_algorithms()
    example_3_programmatic_access()
    
    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70)
