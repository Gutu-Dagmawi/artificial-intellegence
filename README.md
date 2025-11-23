# Route Search on OpenStreetMap

A Python system for finding optimal routes on real-world road networks using OpenStreetMap data and multiple search algorithms.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

- **Real-world map data** from OpenStreetMap (Addis Ababa, Ethiopia)
- **Three search algorithms**: BFS, A* (with Haversine heuristic), and UCS
- **Interactive visualization** with zoom, pan, and street name labels
- **Intelligent geocoding** with validation and error handling
- **Performance comparison** showing algorithm efficiency
- **Named POI extraction** for easy location discovery
- **Comprehensive statistics** including distance, nodes explored, and path details

---

## 📦 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for first-time map download)
- ~500MB disk space for cached map data

### Installation (Fedora)

**Option 1: Automated Setup (Recommended)**
```bash
./setup_fedora.sh
```

**Option 2: Manual Installation**
```bash
# Install system dependencies
sudo dnf install -y gdal gdal-devel python3-devel python3-tkinter gcc gcc-c++

# Install Python GDAL (must match system GDAL version)
GDAL_VERSION=$(gdal-config --version)
pip install GDAL==$GDAL_VERSION

# Install other Python packages
pip install -r requirements.txt

# Verify installation
python3 -c "import osmnx; print('✅ Ready to go!')"
```

### Installation (Ubuntu/Debian)

```bash
# System dependencies
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-tk gcc g++

# Python packages
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version)
pip install -r requirements.txt
```

### Installation (Using Conda - All Platforms)

```bash
# Create environment
conda create -n route_search python=3.11 -y
conda activate route_search

# Install all dependencies
conda install -c conda-forge osmnx matplotlib networkx scipy -y
pip install Pillow
```

---

## 🚀 Usage

### Basic Route Search

```bash
python3 route_search_osm.py
```

Then:
1. Choose whether to see available locations (y/n)
2. Enter starting location (e.g., "Bole, Addis Ababa")
3. Enter destination (e.g., "Meskel Square, Addis Ababa")
4. View results from all three algorithms
5. Optionally visualize the optimal route

### Discover Available Locations

```bash
python3 show_locations.py
```

This displays:
- Named points of interest (POIs)
- Landmarks and amenities
- Major streets and areas
- Common neighborhood names

### Example Session

```
======================================================================
               ROUTE SEARCH ON OPENSTREETMAP
                    Addis Ababa, Ethiopia
======================================================================

Loading road network for Addis Ababa, Ethiopia...
✓ Successfully loaded 45231 nodes and 98764 edges
✓ Graph projected to UTM for accurate distance calculations

📍 Would you like to see available locations from the map? (y/n): n

📝 Enter locations (you can use addresses or landmark names):

🚀 Starting location: Bole, Addis Ababa
🎯 Destination: Meskel Square, Addis Ababa

======================================================================
ROUTE SEARCH SYSTEM
======================================================================

📍 Geocoding locations...

   'Bole, Addis Ababa':
      Query: Bole, Addis Ababa
      Geocoded: (9.012345, 38.756789)
      Nearest node: 123456789
      Node location: (9.012350, 38.756790)
      Distance: 23.4m

   'Meskel Square, Addis Ababa':
      Query: Meskel Square, Addis Ababa
      Geocoded: (9.010229, 38.760631)
      Nearest node: 987654321
      Node location: (9.010230, 38.760632)
      Distance: 18.7m

📊 Route Overview:
   Direct distance: 3456.7m (3.46km)

🔍 Running search algorithms...
   Running BFS...
   Running UCS...
   Running A*...

======================================================================
RESULTS
======================================================================

BFS:
   Distance:        5234.56 meters (5.23 km)
   Nodes explored:  1247
   Path length:     45 nodes

UCS:
   Distance:        4987.32 meters (4.99 km)
   Nodes explored:  892
   Path length:     38 nodes

A*:
   Distance:        4987.32 meters (4.99 km)
   Nodes explored:  456
   Path length:     38 nodes

----------------------------------------------------------------------
🏆 Optimal path distance: 4987.32 meters (4.99 km)
⚠️  Multiple optimal paths found!
   Algorithms with optimal path: UCS, A*

----------------------------------------------------------------------
ALGORITHM EFFICIENCY COMPARISON:
----------------------------------------------------------------------
BFS      -   Sub-optimal   | Explored:   1247 nodes
UCS      - ✓ OPTIMAL       | Explored:    892 nodes
A*       - ✓ OPTIMAL       | Explored:    456 nodes
======================================================================

📊 Would you like to visualize the optimal route? (y/n): y

🗺️  Interactive map opened!
   💡 Use your mouse to zoom and pan the map
   💡 Use the toolbar buttons for more controls
   💡 Close the window when done
```

---

## 🧠 Algorithm Details

### 1. Breadth-First Search (BFS)

**Type:** Unweighted search

**How it works:**
- Explores nodes level by level from the start
- Guarantees shortest path in terms of **number of edges**
- Does NOT consider edge weights (road distances)

**Performance:** Usually finds sub-optimal paths for distance-based routing

**Use case:** When minimizing turns is more important than distance

---

### 2. Uniform Cost Search (UCS)

**Type:** Weighted search (uninformed)

**How it works:**
- Always expands the node with lowest total cost from start
- Essentially Dijkstra's algorithm
- Guarantees optimal path based on actual distances

**Why chosen:** Serves as a baseline for comparison with A*. Shows the efficiency gain from using heuristics.

**Performance:** Explores 2-3x more nodes than A* while finding the same optimal path

---

### 3. A* Search

**Type:** Informed search with heuristic

**How it works:**
- Uses both actual cost from start (g) and estimated cost to goal (h)
- Heuristic: Haversine great-circle distance
- Prioritizes nodes that appear closer to the goal

**Heuristic:** Straight-line distance using the Haversine formula. Admissible (never overestimates) because you can't drive through buildings.

**Performance:** Most efficient - explores ~50% fewer nodes than UCS while maintaining optimality

**Winner:** Best balance of speed and accuracy! ⭐

---

### Performance Comparison

For typical 5km routes in Addis Ababa:

| Algorithm | Optimality | Nodes Explored | Relative Speed |
|-----------|-----------|----------------|----------------|
| **BFS**   | ❌ No      | ~2000+         | Slow           |
| **UCS**   | ✅ Yes     | ~800           | Medium         |
| **A***    | ✅ Yes     | ~400           | **Fast** ⚡    |

---

## 🗺️ Interactive Visualization

The route visualization is fully interactive with zoom, pan, and detailed annotations.

### Visual Elements

- 🚀 **Green Circle**: START location with label
- 🎯 **Red Star**: DESTINATION with label
- 🟡 **Amber Dots**: Waypoints along the route with street names
- 🔵 **Blue Line**: The optimal route path
- 🛣️ **Street Labels**: Names of roads the route follows

### Interactive Controls

| Control | Action |
|---------|--------|
| **Scroll Wheel** | Zoom in/out |
| **Click + Drag** | Pan the map |
| **Toolbar → Home** | Reset to original view |
| **Toolbar → Zoom** | Draw rectangle to zoom to area |
| **Toolbar → Save** | Export image (PNG/PDF/SVG) |

### Grid & Info Boxes

- **Upper Left (Blue)**: Interactive controls guide
- **Lower Left (White)**: Route statistics (distance, waypoints, algorithm)
- **Upper Right**: Legend showing all map elements
- **Waypoint Labels**: Street names displayed at each amber marker

### Tips for Exploration

1. **For Long Routes:** Start zoomed out, then zoom into areas of interest
2. **See Street Names:** Zoom in on amber waypoint markers to read labels
3. **Save Views:** Use toolbar save button to export interesting angles
4. **Multiple Routes:** Don't close the window - run another search to compare

---

## 📁 Project Structure

```
route_search_osm.py      # Main program (900+ lines)
├── RouteSearchSystem class
│   ├── __init__()                  # Load & project OSM graph
│   ├── get_places_from_graph()     # Extract named locations
│   ├── geocode_location()          # Convert address → node
│   ├── bfs_search()                # BFS implementation
│   ├── uniform_cost_search()       # UCS implementation
│   ├── astar_search()              # A* implementation
│   ├── search_route()              # Master search function
│   ├── get_street_name_at_edge()   # Extract street names
│   └── visualize_route()           # Interactive map display
└── main()                          # CLI entry point

show_locations.py        # POI & location discovery tool
examples.py              # Programmatic usage examples  
test_route_search.py     # Automated test suite
setup_fedora.sh          # Automated installer (Fedora)
requirements.txt         # Python dependencies
```

---

## ⚙️ Technical Details

### Graph Representation

The system maintains **two versions** of the road network:

1. **`graph_unprojected`** (WGS84 lat/lon)
   - Used for: Geocoding, visualization, coordinate display
   - Format: Latitude/Longitude (e.g., 9.0120, 38.7568)

2. **`graph`** (UTM projected)
   - Used for: Pathfinding algorithms, distance calculations
   - Format: UTM meters (e.g., 454321, 987654)
   - Provides accurate meter-based distances

**Why Both?** Geocoding returns WGS84 coordinates, but accurate distance calculations require a projected coordinate system. Using both ensures correctness throughout the pipeline.

### Geocoding Process

1. User enters location name (e.g., "Bole")
2. System adds "Addis Ababa, Ethiopia" if not present
3. Geocoder returns latitude/longitude
4. Find nearest node in **unprojected graph** (same coordinate system)
5. Validate distance to nearest node (warn if > 1km)
6. Return node ID for pathfinding

### Distance Calculations

- **Haversine Formula**: Great-circle distance for heuristic (A*)
- **Edge Lengths**: Pre-computed in projected graph (meters)
- **Path Distance**: Sum of edge lengths along the route

---

## 🛡️ Error Handling & Edge Cases

The system handles all common scenarios:

### 1. Same Location
```
Input: Start = "Bole", Goal = "Bole"
Output: "You are already at the destination."
```

### 2. Invalid Location
```
Input: Start = "NonexistentPlace123"
Output: "❌ Invalid input: location not found - 'NonexistentPlace123'"
```

### 3. Locations Geocode to Same Node
```
Input: Start = "CMC", Goal = "Nearby Street"
Output: ⚠️ Warning: 'CMC' and 'Nearby Street' geocoded to the same location!
        This may mean:
        • The locations are very close together
        • The location names are too general
        • Try being more specific (e.g., add street names or landmarks)
```

### 4. Multiple Optimal Paths
```
Output: ⚠️ Multiple optimal paths found!
        Algorithms with optimal path: UCS, A*
```

### 5. No Path Exists
```
Output: ❌ No path found between the locations.
```

---

## 🐛 Troubleshooting

### "Failed to load road network"
**Cause:** No internet connection or OSM server issues  
**Solution:** Check connection, wait a moment, try again

### "Location not found"
**Cause:** Location name is ambiguous or misspelled  
**Solution:** 
- Run `python3 show_locations.py` to see valid names
- Add "Addis Ababa" to your query
- Use more specific names (e.g., street names)

### "Cannot import name 'ImageTk' from 'PIL'"
**Cause:** Missing Pillow package  
**Solution:** `pip install Pillow --upgrade`

### "No module named 'tkinter'"
**Cause:** Tkinter not installed (needed for interactive visualization)  
**Solution:** 
- Fedora: `sudo dnf install python3-tkinter`
- Ubuntu: `sudo apt-get install python3-tk`
- macOS: Usually pre-installed

### Visualization is slow or laggy
**Cause:** Very detailed map area with many roads  
**Solution:** 
- Zoom out slightly
- Close other visualization windows
- This is normal for dense urban areas

### "GDAL version mismatch"
**Cause:** Python GDAL doesn't match system GDAL  
**Solution:**
```bash
# Reinstall GDAL Python bindings
pip uninstall GDAL
GDAL_VERSION=$(gdal-config --version)
pip install GDAL==$GDAL_VERSION
```

---

## 📊 Example Test Cases

Try these routes to test the system:

### Short Route (~1-2 km)
```
Start: Bole Medhanialem Church, Addis Ababa
Goal: Edna Mall, Addis Ababa
Expected: Fast computation, clear street-level detail
```

### Medium Route (~5 km)
```
Start: Bole, Addis Ababa
Goal: Meskel Square, Addis Ababa
Expected: Multiple waypoints, visible algorithm differences
```

### Long Route (~10+ km)
```
Start: Bole Airport, Addis Ababa
Goal: Entoto, Addis Ababa
Expected: Significant node count differences between algorithms
```

### Edge Case: Same Location
```
Start: Meskel Square, Addis Ababa
Goal: Meskel Square, Addis Ababa
Expected: "You are already at the destination."
```

---

## 🎓 Educational Value

This project demonstrates:

### Graph Theory Concepts
- Real-world graphs with 45,000+ nodes
- Directed vs undirected edges
- Edge weights and their importance
- Heuristic functions and admissibility

### Algorithm Analysis
- Uninformed vs informed search
- Space-time tradeoffs
- Optimality guarantees
- Empirical performance comparison

### Software Engineering
- Production-quality code structure
- Comprehensive error handling
- User experience design
- Documentation practices

### Geospatial Computing
- Coordinate system transformations (WGS84 ↔ UTM)
- Geocoding and reverse geocoding
- Distance calculations on a sphere
- Map data structures and querying

---

## 📝 Dependencies

### System Packages

**Fedora:**
```bash
sudo dnf install gdal gdal-devel python3-devel python3-tkinter gcc gcc-c++
```

**Ubuntu/Debian:**
```bash
sudo apt-get install gdal-bin libgdal-dev python3-tk gcc g++
```

### Python Packages

See `requirements.txt`:
- `osmnx` (>=1.6.0) - OpenStreetMap data access
- `networkx` (>=3.0) - Graph algorithms
- `matplotlib` (>=3.5.0) - Visualization
- `scipy` (>=1.9.0) - Scientific computing (osmnx dependency)
- `Pillow` (>=9.0.0) - Image processing (interactive visualization)

**Note:** GDAL must be installed at the system level before installing Python packages.

---

## 🔧 Customization

### Change City

Edit line 28 in `route_search_osm.py`:
```python
system = RouteSearchSystem("Your City, Country")
```

### Change Network Type

Edit line 44:
```python
network_type='drive'  # Options: 'walk', 'bike', 'all'
```

### Adjust Waypoint Count

Edit line 687 in `visualize_route()`:
```python
waypoint_interval = max(1, len(path) // 8)  # Change 8 to desired count
```

### Modify Colors

Edit the color codes in `visualize_route()`:
- Route: `#0066cc` (blue)
- Start: `#28a745` (green)  
- End: `#dc3545` (red)
- Waypoints: `#ffc107` (amber)

---

## 🚀 Advanced Usage

### Programmatic API

```python
from route_search_osm import RouteSearchSystem

# Initialize
system = RouteSearchSystem("Addis Ababa, Ethiopia")

# Find route
result = system.search_route("Bole", "Meskel Square")

# Access results
if 'error' not in result:
    optimal_algo = result['optimal_algorithms'][0]
    optimal_path = result['results'][optimal_algo]['path']
    distance_m = result['optimal_distance']
    
    print(f"Route: {len(optimal_path)} nodes, {distance_m/1000:.2f} km")
    
    # Visualize
    system.visualize_route(optimal_path, optimal_algo, 
                          "Start", "Goal", distance_m/1000)
```

### Run Individual Algorithms

```python
# Get node IDs
start_node = system.geocode_location("Bole, Addis Ababa")
goal_node = system.geocode_location("Meskel Square, Addis Ababa")

# Run specific algorithm
path, stats = system.astar_search(start_node, goal_node)
distance = system.calculate_path_distance(path)

print(f"A*: {distance:.2f}m, {stats['nodes_explored']} nodes explored")
```

---

## 📄 License

This project is provided for educational purposes. 

OpenStreetMap data is © OpenStreetMap contributors and is available under the Open Database License (ODbL).

---

## 🤝 Contributing

Suggestions for improvement:
- Add more algorithms (Bidirectional A*, IDA*, etc.)
- Include traffic data and time-dependent routing
- Add turn-by-turn directions
- Support multiple cities
- Web-based interface
- Mobile app integration

---

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Verify all dependencies are installed: `python3 -c "import osmnx, networkx, matplotlib, scipy; print('All good!')"`
3. Test with simple locations first (e.g., "Bole", "Piazza")
4. Check the example test cases

---

## ✨ Features Summary

✅ Three search algorithms (BFS, UCS, A*)  
✅ Real OpenStreetMap data  
✅ Interactive visualization with zoom/pan  
✅ Street name labels on waypoints  
✅ Named POI discovery  
✅ Comprehensive error handling  
✅ Performance metrics and comparison  
✅ Production-quality code  
✅ Full documentation  
✅ Automated installation  
✅ Example scripts and tests  

---

**Built with ❤️ for learning graph algorithms on real-world data**

**Version:** 1.0  
**Updated:** 2025-11-23  
**Lines of Code:** 900+ (main) + 200+ (utilities)
