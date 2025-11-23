#!/usr/bin/env python3
"""
Display available locations from the Addis Ababa OSM map.
This script extracts actual named locations, POIs, and features from the map data.
"""

import osmnx as ox


def load_and_display_locations():
    """Load the map and display actual named places and POIs."""
    print("\n" + "="*70)
    print("LOADING ADDIS ABABA MAP...")
    print("="*70)
    print("\nThis may take a moment on first run...")
    
    try:
        # Load POIs and amenities using OSM features
        print("\n📍 Extracting Points of Interest...")
        
        # Define tags to search for named places
        tags = {
            'amenity': True,      # Schools,hospitals, restaurants, etc.
            'tourism': True,      # Hotels, attractions, viewpoints
            'shop': True,         # Shops and markets
            'building': ['university', 'school', 'hospital', 'hotel', 'stadium'],
            'historic': True,     # Historic sites
            'leisure': True,      # Parks, stadiums
            'office': True,       # Offices, embassies
        }
        
        # Get POIs from OSM
        try:
            gdf = ox.features_from_place("Addis Ababa, Ethiopia", tags=tags)
            
            print(f"✓ Found {len(gdf)} features")
            
            # Extract named locations
            places = {}
            
            for idx, row in gdf.iterrows():
                # Try to get the name - handle different data types
                name = None
                
                if 'name' in row and row['name'] is not None:
                    potential_name = row['name']
                    # Convert to string if it's a valid value
                    if isinstance(potential_name, str):
                        name = potential_name.strip()
                    elif not isinstance(potential_name, float):
                        # Convert non-float, non-string values to string
                        name = str(potential_name).strip()
                        
                if not name and 'name:en' in row and row['name:en'] is not None:
                    potential_name = row['name:en']
                    if isinstance(potential_name, str):
                        name = potential_name.strip()
                    elif not isinstance(potential_name, float):
                        name = str(potential_name).strip()
                
                # Only process if we have a valid string name
                if name and len(name) > 0 and len(name) < 60 and name not in places:
                    # Get location type
                    loc_type = []
                    if 'amenity' in row and row['amenity']:
                        loc_type.append(str(row['amenity']))
                    if 'tourism' in row and row['tourism']:
                        loc_type.append(str(row['tourism']))
                    if 'shop' in row and row['shop']:
                        loc_type.append(f"{row['shop']} shop")
                    if 'building' in row and row['building']:
                        loc_type.append(str(row['building']))
                    
                    type_str = ', '.join(loc_type[:2]) if loc_type else 'location'
                    places[name] = type_str
                    
                    if len(places) >= 50:
                        break
            
            if not places:
                print("\n⚠️  Could not extract named POIs from the map.")
                show_fallback_locations()
                return
            
            print("\n" + "="*70)
            print(f"NAMED PLACES IN ADDIS ABABA ({len(places)} found)")
            print("="*70)
            print()
            
            # Sort alphabetically and display with types
            for name, loc_type in sorted(places.items()):
                # Truncate type if too long
                loc_type_display = loc_type[:30] + "..." if len(loc_type) > 30 else loc_type
                print(f"  📍 {name:<40} ({loc_type_display})")
            
            print("\n" + "="*70)
            print("\n💡 Usage Tips:")
            print("   • Use exact names shown above in the route search")
            print("   • Or combine with 'Addis Ababa':")
            print("     Example: 'Bole Airport, Addis Ababa'")
            print("   • You can also use general area names:")
            print("     'Bole', 'Meskel Square', 'Piazza', 'Merkato'")
            print("   • Or use coordinates: '9.0320, 38.7469'")
            print("="*70)
            print()
            
        except Exception as e:
            print(f"\n⚠️  Error extracting POIs: {e}")
            print("\nTrying alternative method...")
            show_street_names()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        show_fallback_locations()


def show_street_names():
    """Show major street names from the road network."""
    try:
        print("\n📍 Extracting major streets...")
        
        graph = ox.graph_from_place(
            "Addis Ababa, Ethiopia",
            network_type='drive',
            simplify=True
        )
        
        # Extract street names from edges
        street_names = set()
        
        for u, v, data in graph.edges(data=True):
            if 'name' in data and data['name']:
                name = data['name']
                if isinstance(name, list):
                    street_names.update(name)
                elif isinstance(name, str) and len(name) < 50:
                    street_names.add(name)
                    
                if len(street_names) >= 40:
                    break
        
        if street_names:
            print(f"\n✓ Found {len(street_names)} named streets:")
            print()
            for name in sorted(street_names):
                print(f"  🛣️  {name}")
            print("\n" + "="*70)
            print("💡 Use these street names when specifying locations")
            print("="*70)
        else:
            show_fallback_locations()
            
    except Exception as e:
        print(f"Error: {e}")
        show_fallback_locations()


def show_fallback_locations():
    """Show common area names as fallback."""
    print("\n" + "="*70)
    print("COMMON AREA NAMES IN ADDIS ABABA")
    print("="*70)
    print("\nYou can use these general area names:")
    print()
    print("  📍 Bole (Commercial area)")
    print("  📍 Meskel Square (Central landmark)")
    print("  📍 Piazza (Historic district)")
    print("  📍 Merkato (Market area)")
    print("  📍 Kazanchis (Business district)")
    print("  📍 Sidist Kilo (University area)")
    print("  📍 Arat Kilo (Central area)")
    print("  📍 CMC (Residential area)")
    print("  📍 Legehar (Central district)")
    print("  📍 Mexico (Residential area)")
    print()
    print("="*70)
    print("💡 Add 'Addis Ababa' for better results:")
    print("   Example: 'Bole, Addis Ababa'")
    print("="*70)
    print()


if __name__ == "__main__":
    load_and_display_locations()

