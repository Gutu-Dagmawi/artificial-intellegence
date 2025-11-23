#!/usr/bin/env python3
"""
Route Search on OpenStreetMap Data
===================================

This module implements route finding algorithms on real-world road networks
using OpenStreetMap data. It supports multiple search algorithms including
BFS, A*, and Uniform Cost Search (UCS).

Author: Amanuel Berhane, Edilawit Gerum and Dagmawi Gutu
Date: 2025-11-23
Dependencies: osmnx, networkx, matplotlib, geopy
"""

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict, Set
from collections import deque
import heapq
import math


class RouteSearchSystem:
    """
    A system for finding optimal routes on real-world road networks.

    This class loads OpenStreetMap data for a specified location and provides
    multiple pathfinding algorithms to find routes between locations.
    """

    def __init__(self, place_name: str = "Addis Ababa, Ethiopia"):
        """
        Initialize the route search system with a road network.

        Args:
            place_name: Name of the place to download road network for
        """
        print(f"Loading road network for {place_name}...")

        try:
            # Download road network as a MultiDiGraph (in WGS84 lat/lon)
            # network_type='drive' gets drivable roads
            self.graph_unprojected = ox.graph_from_place(
                place_name, network_type="drive", simplify=True
            )

            print(
                f"[OK] Successfully loaded {len(self.graph_unprojected.nodes)} nodes and {len(self.graph_unprojected.edges)} edges"
            )

            # Keep the unprojected graph for geocoding (lat/lon coordinates)
            # Project a copy for accurate distance calculations
            self.graph = ox.project_graph(self.graph_unprojected)

            print(f"[OK] Graph projected to UTM for accurate distance calculations")

        except Exception as e:
            raise RuntimeError(f"Failed to load road network: {e}")

    def get_places_from_graph(self, limit: int = 50) -> Dict[str, Tuple[float, float]]:
        """
        Extract actual places from the OSM graph data.

        This method searches through the graph nodes to find those with
        name tags, which typically represent actual landmarks and places.

        Args:
            limit: Maximum number of places to return

        Returns:
            Dictionary mapping place names to (latitude, longitude) tuples
        """
        places = {}

        for node_id, data in self.graph_unprojected.nodes(data=True):
            # Check if node has a name tag
            if "name" in data and data["name"]:
                name = data["name"]
                lat = data["y"]
                lon = data["x"]

                # Avoid duplicates and overly technical names
                if name not in places and len(name) < 50:
                    places[name] = (lat, lon)

                    if len(places) >= limit:
                        break

        return places

    def display_available_locations(self):
        """
        Display actual locations extracted from the map.

        This shows real places from the OSM data, not hardcoded values.
        """
        print("\n" + "=" * 70)
        print("EXTRACTING LOCATIONS FROM MAP...")
        print("=" * 70)

        places = self.get_places_from_graph(limit=30)

        if not places:
            print("\n[WARNING] Could not extract named locations from the graph.")
            print("   You can still use general area names like:")
            print("   • Bole, Addis Ababa")
            print("   • Meskel Square, Addis Ababa")
            print("   • Piazza, Addis Ababa")
            print("=" * 70)
            return

        print(f"\n[OK] Found {len(places)} named locations in the map:")
        print()

        # Sort alphabetically and display
        sorted_places = sorted(places.items())

        # Display in two columns
        mid = (len(sorted_places) + 1) // 2

        for i in range(mid):
            left = f"  • {sorted_places[i][0]}"
            if i + mid < len(sorted_places):
                right = f"  • {sorted_places[i + mid][0]}"
                print(f"{left:<35} {right}")
            else:
                print(left)

        print("\n" + "=" * 70)
        print("\n[INFO] Tips:")
        print("   • Use the exact names shown above")
        print("   • Or use general area names: 'Bole', 'Merkato', 'Piazza'")
        print("   • Add 'Addis Ababa' for better results: 'Bole, Addis Ababa'")
        print("   • You can also use coordinates: '9.0320, 38.7469'")
        print("=" * 70)

    def geocode_location(self, location: str, verbose: bool = True) -> Optional[int]:
        """
        Convert a location string to the nearest OSM node ID.

        Args:
            location: Address or place name to geocode
            verbose: If True, print detailed geocoding information

        Returns:
            Node ID of nearest graph node, or None if geocoding fails
        """
        try:
            # Improve specificity by adding city/country if not present
            search_query = location
            if "Addis Ababa" not in location and "Ethiopia" not in location:
                # Try multiple query formats for better results
                search_queries = [
                    f"{location}, Addis Ababa, Ethiopia",
                    f"{location} neighborhood, Addis Ababa, Ethiopia",
                    f"{location} area, Addis Ababa, Ethiopia",
                ]
            else:
                search_queries = [location]

            # Try geocoding with different query formats
            point = None
            used_query = None

            for query in search_queries:
                try:
                    point = ox.geocode(query)
                    used_query = query
                    break
                except Exception:
                    continue

            if point is None:
                raise ValueError(f"Could not geocode any variant of '{location}'")

            lat, lon = point

            # Find nearest node in the UNPROJECTED graph (lat/lon coordinates)
            # This ensures we're comparing in the same coordinate system
            nearest_node = ox.distance.nearest_nodes(
                self.graph_unprojected, lon, lat  # longitude  # latitude
            )

            # Get the actual node coordinates from unprojected graph
            node_data = self.graph_unprojected.nodes[nearest_node]
            node_lat, node_lon = node_data["y"], node_data["x"]

            # Calculate distance between geocoded point and nearest node
            distance = ox.distance.great_circle(lat, lon, node_lat, node_lon)

            if verbose:
                print(f"   '{location}':")
                print(f"      Query: {used_query}")
                print(f"      Geocoded: ({lat:.6f}, {lon:.6f})")
                print(f"      Nearest node: {nearest_node}")
                print(f"      Node location: ({node_lat:.6f}, {node_lon:.6f})")
                print(f"      Distance: {distance:.1f}m")

            # Warn if the nearest node is very far from the geocoded point
            if distance > 1000:  # More than 1km away
                print(
                    f"   [WARNING] Nearest road is {distance:.0f}m ({distance/1000:.1f}km) from geocoded location"
                )
                print(f"      '{location}' might need to be more specific")

            return nearest_node

        except Exception as e:
            print(f"Error geocoding '{location}': {e}")
            return None

    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """
        Get latitude and longitude for a node.

        Args:
            node_id: OSM node identifier

        Returns:
            Tuple of (latitude, longitude)
        """
        node_data = self.graph_unprojected.nodes[node_id]
        return (node_data["y"], node_data["x"])

    def haversine_distance(self, node1: int, node2: int) -> float:
        """
        Calculate great-circle distance between two nodes using Haversine formula.

        This is used as the heuristic function for A* search.

        Args:
            node1: First node ID
            node2: Second node ID

        Returns:
            Distance in meters
        """
        lat1, lon1 = self.get_node_coordinates(node1)
        lat2, lon2 = self.get_node_coordinates(node2)

        # Earth radius in meters
        R = 6371000

        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def get_edge_length(self, node1: int, node2: int, edge_key: int = 0) -> float:
        """
        Get the length of an edge between two nodes.

        Args:
            node1: Source node
            node2: Target node
            edge_key: Edge key for multigraph (default 0)

        Returns:
            Edge length in meters
        """
        try:
            edge_data = self.graph.get_edge_data(node1, node2, edge_key)
            return edge_data.get("length", 0)
        except:
            return 0

    def bfs_search(self, start: int, goal: int) -> Tuple[Optional[List[int]], Dict]:
        """
        Breadth-First Search (BFS) - Unweighted search algorithm.

        BFS explores nodes level by level, guaranteeing the shortest path
        in terms of number of edges (not distance). It's simple but doesn't
        consider edge weights.

        Args:
            start: Starting node ID
            goal: Goal node ID

        Returns:
            Tuple of (path as list of nodes, statistics dict)
        """
        if start == goal:
            return [start], {"nodes_explored": 0, "algorithm": "BFS"}

        # Queue for BFS: stores nodes to visit
        queue = deque([start])

        # Track visited nodes and their parents
        visited = {start}
        parent = {start: None}
        nodes_explored = 0

        while queue:
            current = queue.popleft()
            nodes_explored += 1

            # Check if we reached the goal
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()

                return path, {"nodes_explored": nodes_explored, "algorithm": "BFS"}

            # Explore neighbors
            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        # No path found
        return None, {"nodes_explored": nodes_explored, "algorithm": "BFS"}

    def uniform_cost_search(
        self, start: int, goal: int
    ) -> Tuple[Optional[List[int]], Dict]:
        """
        Uniform Cost Search (UCS) - Weighted search algorithm.

        UCS always expands the node with the lowest path cost from the start.
        It guarantees finding the optimal (shortest distance) path but explores
        more nodes than A* because it doesn't use a heuristic.

        This is essentially Dijkstra's algorithm and serves as a baseline
        for comparison with A*.

        Args:
            start: Starting node ID
            goal: Goal node ID

        Returns:
            Tuple of (path as list of nodes, statistics dict)
        """
        if start == goal:
            return [start], {"nodes_explored": 0, "algorithm": "UCS", "path_cost": 0}

        # Priority queue: (cost, node)
        pq = [(0, start)]

        # Track best cost to reach each node
        cost_so_far = {start: 0}

        # Track parent for path reconstruction
        parent = {start: None}
        nodes_explored = 0

        while pq:
            current_cost, current = heapq.heappop(pq)
            nodes_explored += 1

            # Check if we reached the goal
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()

                return path, {
                    "nodes_explored": nodes_explored,
                    "algorithm": "UCS",
                    "path_cost": current_cost,
                }

            # Skip if we've found a better path to this node
            if current_cost > cost_so_far.get(current, float("inf")):
                continue

            # Explore neighbors
            for neighbor in self.graph.successors(current):
                # Get edge length
                edge_length = self.get_edge_length(current, neighbor)
                new_cost = current_cost + edge_length

                # If this path is better, update
                if new_cost < cost_so_far.get(neighbor, float("inf")):
                    cost_so_far[neighbor] = new_cost
                    parent[neighbor] = current
                    heapq.heappush(pq, (new_cost, neighbor))

        # No path found
        return None, {"nodes_explored": nodes_explored, "algorithm": "UCS"}

    def astar_search(self, start: int, goal: int) -> Tuple[Optional[List[int]], Dict]:
        """
        A* Search - Informed search algorithm with heuristic.

        A* uses both the actual cost from start (g) and estimated cost to goal (h)
        to guide the search. The heuristic (Haversine distance) makes it more
        efficient than UCS while still guaranteeing optimality if the heuristic
        is admissible (never overestimates).

        Args:
            start: Starting node ID
            goal: Goal node ID

        Returns:
            Tuple of (path as list of nodes, statistics dict)
        """
        if start == goal:
            return [start], {"nodes_explored": 0, "algorithm": "A*", "path_cost": 0}

        # Priority queue: (f_score, node) where f = g + h
        # g = actual cost from start, h = heuristic to goal
        h_start = self.haversine_distance(start, goal)
        pq = [(h_start, start)]

        # Track costs
        g_score = {start: 0}  # Cost from start to node

        # Track parent for path reconstruction
        parent = {start: None}
        nodes_explored = 0

        while pq:
            f_score, current = heapq.heappop(pq)
            nodes_explored += 1

            # Check if we reached the goal
            if current == goal:
                # Reconstruct path
                path = []
                node = goal
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()

                return path, {
                    "nodes_explored": nodes_explored,
                    "algorithm": "A*",
                    "path_cost": g_score[goal],
                }

            # Skip if we've found a better path to this node
            current_g = g_score.get(current, float("inf"))
            if f_score > current_g + self.haversine_distance(current, goal):
                continue

            # Explore neighbors
            for neighbor in self.graph.successors(current):
                # Get edge length
                edge_length = self.get_edge_length(current, neighbor)
                tentative_g = current_g + edge_length

                # If this path is better, update
                if tentative_g < g_score.get(neighbor, float("inf")):
                    g_score[neighbor] = tentative_g
                    h_score = self.haversine_distance(neighbor, goal)
                    f_score = tentative_g + h_score
                    parent[neighbor] = current
                    heapq.heappush(pq, (f_score, neighbor))

        # No path found
        return None, {"nodes_explored": nodes_explored, "algorithm": "A*"}

    def calculate_path_distance(self, path: List[int]) -> float:
        """
        Calculate total distance of a path.

        Args:
            path: List of node IDs representing the path

        Returns:
            Total distance in meters
        """
        if not path or len(path) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(path) - 1):
            total_distance += self.get_edge_length(path[i], path[i + 1])

        return total_distance

    def search_route(self, start_location: str, goal_location: str) -> Dict:
        """
        Master function to search for routes using all algorithms.

        This function:
        1. Geocodes the start and goal locations
        2. Validates inputs
        3. Runs all three search algorithms
        4. Compares results
        5. Returns comprehensive statistics

        Args:
            start_location: Starting location (address or place name)
            goal_location: Destination location (address or place name)

        Returns:
            Dictionary containing paths, statistics, and comparison results
        """
        print("\n" + "=" * 70)
        print("ROUTE SEARCH SYSTEM")
        print("=" * 70)

        # Step 1: Geocode locations
        print(f"\n[GEOCODING] Geocoding locations...")
        print()

        start_node = self.geocode_location(start_location, verbose=True)
        print()
        goal_node = self.geocode_location(goal_location, verbose=True)

        # Step 2: Validate inputs
        if start_node is None:
            print(f"\n[ERROR] Invalid input: location not found - '{start_location}'")
            return {"error": "start_not_found"}

        if goal_node is None:
            print(f"\n[ERROR] Invalid input: location not found - '{goal_location}'")
            return {"error": "goal_not_found"}

        # Get coordinates for comparison
        start_coords = self.get_node_coordinates(start_node)
        goal_coords = self.get_node_coordinates(goal_node)
        direct_distance = self.haversine_distance(start_node, goal_node)

        print(f"\n[ROUTE] Route Overview:")
        print(
            f"   Direct distance: {direct_distance:.1f}m ({direct_distance/1000:.2f}km)"
        )

        # Step 3: Check if already at destination
        if start_node == goal_node:
            # Check if the location names are actually different
            if start_location.lower().strip() != goal_location.lower().strip():
                print(
                    f"\n[WARNING] Warning: '{start_location}' and '{goal_location}' geocoded to the same location!"
                )
                print(f"   This may mean:")
                print(f"   • The locations are very close together")
                print(f"   • The location names are too general")
                print(
                    f"   • Try being more specific (e.g., add street names or landmarks)"
                )
            print("\n[OK] You are already at the destination.")
            return {"error": "already_at_destination"}

        # Step 4: Run all algorithms
        print(f"\n[SEARCH] Running search algorithms...")

        results = {}

        # BFS
        print("   Running BFS...")
        bfs_path, bfs_stats = self.bfs_search(start_node, goal_node)
        if bfs_path:
            bfs_distance = self.calculate_path_distance(bfs_path)
            results["BFS"] = {
                "path": bfs_path,
                "distance": bfs_distance,
                "nodes_explored": bfs_stats["nodes_explored"],
            }

        # UCS
        print("   Running UCS...")
        ucs_path, ucs_stats = self.uniform_cost_search(start_node, goal_node)
        if ucs_path:
            ucs_distance = self.calculate_path_distance(ucs_path)
            results["UCS"] = {
                "path": ucs_path,
                "distance": ucs_distance,
                "nodes_explored": ucs_stats["nodes_explored"],
            }

        # A*
        print("   Running A*...")
        astar_path, astar_stats = self.astar_search(start_node, goal_node)
        if astar_path:
            astar_distance = self.calculate_path_distance(astar_path)
            results["A*"] = {
                "path": astar_path,
                "distance": astar_distance,
                "nodes_explored": astar_stats["nodes_explored"],
            }

        # Step 5: Check if any path was found
        if not results:
            print("\n[ERROR] No path found between the locations.")
            return {"error": "no_path_found"}

        # Step 6: Display results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        for algo_name, data in results.items():
            print(f"\n{algo_name}:")
            print(
                f"   Distance:        {data['distance']:.2f} meters ({data['distance']/1000:.2f} km)"
            )
            print(f"   Nodes explored:  {data['nodes_explored']}")
            print(f"   Path length:     {len(data['path'])} nodes")

        # Step 7: Find optimal path(s)
        min_distance = min(data["distance"] for data in results.values())
        optimal_algorithms = [
            algo
            for algo, data in results.items()
            if abs(data["distance"] - min_distance) < 0.01  # Account for floating point
        ]

        print("\n" + "-" * 70)
        print(
            f"[OPTIMAL] Optimal path distance: {min_distance:.2f} meters ({min_distance/1000:.2f} km)"
        )

        if len(optimal_algorithms) > 1:
            print(f"[WARNING] Multiple optimal paths found!")
            print(f"   Algorithms with optimal path: {', '.join(optimal_algorithms)}")
        else:
            print(f"   Found by: {optimal_algorithms[0]}")

        # Step 8: Algorithm efficiency comparison
        print("\n" + "-" * 70)
        print("ALGORITHM EFFICIENCY COMPARISON:")
        print("-" * 70)

        for algo_name, data in results.items():
            efficiency = "[OPTIMAL]" if algo_name in optimal_algorithms else "[SUB-OPT]"
            print(
                f"{algo_name:8} - {efficiency:15} | Explored: {data['nodes_explored']:6} nodes"
            )

        print("=" * 70)

        return {
            "results": results,
            "optimal_algorithms": optimal_algorithms,
            "optimal_distance": min_distance,
            "start_node": start_node,
            "goal_node": goal_node,
        }

    def _is_latin_script(self, text: str) -> bool:
        """
        Check if text contains primarily Latin/ASCII characters.

        Args:
            text: String to check

        Returns:
            True if text is in Latin script, False for Amharic or other scripts
        """
        if not text:
            return False

        # Count Latin/ASCII characters (including common punctuation and numbers)
        latin_count = sum(1 for char in text if ord(char) < 0x0370)  # Before Greek

        # If more than 80% of characters are Latin, consider it readable
        return (latin_count / len(text)) > 0.8

    def get_street_name_at_edge(self, node1: int, node2: int) -> str:
        """
        Get the street name for the edge between two nodes.

        Args:
            node1: First node ID
            node2: Second node ID

        Returns:
            Street name or "Unnamed Road"
        """
        try:
            # Get all edges between the two nodes
            edge_data = self.graph_unprojected.get_edge_data(node1, node2)

            if edge_data is None:
                return "Unnamed Road"

            # If multiple edges, take the first one
            if isinstance(edge_data, dict):
                for key, data in edge_data.items():
                    if "name" in data:
                        name = data["name"]
                        # Handle list of names (sometimes OSM has multiple names)
                        if isinstance(name, list):
                            return name[0] if name else "Unnamed Road"
                        return str(name)

            return "Unnamed Road"
        except:
            return "Unnamed Road"

    def visualize_route(
        self,
        path: List[int],
        algorithm_name: str = "Route",
        start_name: str = "Start",
        goal_name: str = "Goal",
        distance_km: float = 0,
    ):
        """
        Visualize a route on the map with enhanced aesthetics and interactivity.

        Args:
            path: List of node IDs representing the route
            algorithm_name: Name of algorithm (for title)
            start_name: Name of starting location
            goal_name: Name of destination location
            distance_km: Total route distance in kilometers
        """
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            from matplotlib.patches import FancyBboxPatch

            # Use interactive backend
            matplotlib.use("TkAgg")

            # Create the base plot with route
            fig, ax = ox.plot_graph_route(
                self.graph_unprojected,  # Use unprojected for proper visualization
                path,
                route_linewidth=4,
                node_size=0,
                bgcolor="#f8f9fa",
                edge_color="#dee2e6",
                edge_linewidth=0.5,
                route_color="#0066cc",
                route_alpha=0.8,
                show=False,
                close=False,
                figsize=(16, 12),
            )

            # Get start and end coordinates
            start_node = path[0]
            end_node = path[-1]

            start_y = self.graph_unprojected.nodes[start_node]["y"]
            start_x = self.graph_unprojected.nodes[start_node]["x"]
            end_y = self.graph_unprojected.nodes[end_node]["y"]
            end_x = self.graph_unprojected.nodes[end_node]["x"]

            # Add intermediate waypoint markers with street names
            waypoint_interval = max(1, len(path) // 8)  # Show ~8 waypoints
            waypoint_coords = []

            for i in range(waypoint_interval, len(path) - 1, waypoint_interval):
                node = path[i]
                y = self.graph_unprojected.nodes[node]["y"]
                x = self.graph_unprojected.nodes[node]["x"]
                waypoint_coords.append((x, y))

                # Add small waypoint markers
                ax.scatter(
                    x,
                    y,
                    c="#ffc107",  # Amber color
                    s=150,
                    marker="o",
                    edgecolors="white",
                    linewidths=2,
                    zorder=4,
                    alpha=0.85,
                )

                # Get street name for this segment
                prev_node = path[i - 1]
                street_name = self.get_street_name_at_edge(prev_node, node)

                # Add label for waypoint with street name (skip only if "Unnamed Road")
                if street_name != "Unnamed Road":
                    bbox_props_waypoint = dict(
                        boxstyle="round,pad=0.3",
                        facecolor="#fff9e6",
                        edgecolor="#ffc107",
                        linewidth=1.5,
                        alpha=0.85,
                    )
                    ax.annotate(
                        street_name,
                        xy=(x, y),
                        xytext=(10, 10),
                        textcoords="offset points",
                        fontsize=8,
                        color="#856404",
                        bbox=bbox_props_waypoint,
                        zorder=4,
                        ha="left",
                    )

            # Add START marker (green circle)
            ax.scatter(
                start_x,
                start_y,
                c="#28a745",
                s=500,
                marker="o",
                edgecolors="white",
                linewidths=3,
                zorder=5,
                label="Start",
                alpha=0.95,
            )

            # Add END marker (red star)
            ax.scatter(
                end_x,
                end_y,
                c="#dc3545",
                s=700,
                marker="*",
                edgecolors="white",
                linewidths=3,
                zorder=5,
                label="Destination",
                alpha=0.95,
            )

            # Add location labels with background boxes
            # START label
            bbox_props_start = dict(
                boxstyle="round,pad=0.6",
                facecolor="#28a745",
                edgecolor="white",
                linewidth=2.5,
                alpha=0.95,
            )
            ax.annotate(
                f"[START]\n{start_name}",
                xy=(start_x, start_y),
                xytext=(20, 20),
                textcoords="offset points",
                fontsize=11,
                fontweight="bold",
                color="white",
                bbox=bbox_props_start,
                zorder=6,
                ha="left",
            )

            # END label
            bbox_props_end = dict(
                boxstyle="round,pad=0.6",
                facecolor="#dc3545",
                edgecolor="white",
                linewidth=2.5,
                alpha=0.95,
            )
            ax.annotate(
                f"[DESTINATION]\n{goal_name}",
                xy=(end_x, end_y),
                xytext=(20, -20),
                textcoords="offset points",
                fontsize=11,
                fontweight="bold",
                color="white",
                bbox=bbox_props_end,
                zorder=6,
                ha="left",
                va="top",
            )

            # Add title with algorithm and distance info
            title = f"{algorithm_name} Route Visualization"
            if distance_km > 0:
                title += f" - Distance: {distance_km:.2f} km"

            ax.set_title(title, fontsize=18, fontweight="bold", pad=25, color="#212529")

            # Add legend with waypoints
            # Create custom legend entries
            from matplotlib.lines import Line2D

            legend_elements = [
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="#28a745",
                    markersize=12,
                    label="Start",
                    markeredgecolor="white",
                    markeredgewidth=2,
                ),
                Line2D(
                    [0],
                    [0],
                    marker="*",
                    color="w",
                    markerfacecolor="#dc3545",
                    markersize=14,
                    label="Destination",
                    markeredgecolor="white",
                    markeredgewidth=2,
                ),
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor="#ffc107",
                    markersize=8,
                    label="Waypoints",
                    markeredgecolor="white",
                    markeredgewidth=1.5,
                ),
                Line2D([0], [0], color="#0066cc", linewidth=3, label="Route Path"),
            ]

            legend = ax.legend(
                handles=legend_elements,
                loc="upper right",
                frameon=True,
                fancybox=True,
                shadow=True,
                fontsize=10,
                framealpha=0.95,
            )
            legend.get_frame().set_facecolor("white")
            legend.get_frame().set_edgecolor("#dee2e6")

            # Add info box with route details
            info_text = f"Route: {start_name} → {goal_name}\n"
            info_text += f"Algorithm: {algorithm_name}\n"
            info_text += f"Waypoints: {len(path)} nodes"
            if distance_km > 0:
                info_text += f"\nDistance: {distance_km:.2f} km"

            # Add text box in lower left
            props = dict(
                boxstyle="round,pad=0.8",
                facecolor="white",
                alpha=0.95,
                edgecolor="#dee2e6",
                linewidth=2.5,
            )
            ax.text(
                0.02,
                0.02,
                info_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment="bottom",
                bbox=props,
                family="monospace",
            )

            # Add interactive controls info box in upper left
            controls_text = "[CONTROLS] INTERACTIVE CONTROLS:\n"
            controls_text += "• Zoom: Scroll wheel or toolbar\n"
            controls_text += "• Pan: Click & drag\n"
            controls_text += "• Home: Reset view (toolbar)\n"
            controls_text += "• Save: Export image (toolbar)"

            controls_props = dict(
                boxstyle="round,pad=0.6",
                facecolor="#e3f2fd",
                alpha=0.9,
                edgecolor="#0066cc",
                linewidth=2,
            )
            ax.text(
                0.02,
                0.98,
                controls_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment="top",
                bbox=controls_props,
                family="monospace",
            )

            # Enable grid for better navigation when zoomed
            ax.grid(True, alpha=0.2, linestyle="--", linewidth=0.5)

            # Adjust layout
            plt.tight_layout()

            # Enable interactive mode
            plt.ion()

            # Show the plot with interactive toolbar
            print("\n[MAP] Interactive map opened!")
            print("   [INFO] Use your mouse to zoom and pan the map")
            print("   [INFO] Use the toolbar buttons for more controls")
            print("   [INFO] Close the window when done\n")

            plt.show(block=True)

        except Exception as e:
            print(f"[ERROR] Error visualizing route: {e}")
            import traceback

            traceback.print_exc()


def main():
    """
    Main entry point for the route search system.

    This function handles user interaction and orchestrates the route search.
    Users can perform multiple route searches without restarting the program.
    """
    print("\n" + "=" * 70)
    print(" " * 15 + "ROUTE SEARCH ON OPENSTREETMAP")
    print(" " * 20 + "Addis Ababa, Ethiopia")
    print("=" * 70)

    try:
        # Initialize the system
        system = RouteSearchSystem("Addis Ababa, Ethiopia")

        # Ask if user wants to see popular locations
        print(
            "\n[LOCATIONS] Would you like to see available locations from the map? (y/n): ",
            end="",
        )
        show_locations = input().strip().lower()

        if show_locations == "y":
            system.display_available_locations()

        # Main loop for multiple route searches
        while True:
            # Get user input
            print(
                "\n[INPUT] Enter locations (you can use addresses or landmark names):"
            )
            if show_locations != "y":
                print("   Examples: 'Bole Airport', 'Meskel Square', 'Piazza'")
            print()

            start_location = input("[START] Starting location: ").strip()
            if not start_location:
                print("[ERROR] Starting location cannot be empty.")
                continue

            goal_location = input("[DESTINATION] Destination: ").strip()
            if not goal_location:
                print("[ERROR] Destination cannot be empty.")
                continue

            # Search for routes
            result = system.search_route(start_location, goal_location)

            # Check for errors
            if "error" in result:
                pass  # Continue to next search
            else:
                # Ask if user wants visualization
                print("\n" + "=" * 70)
                visualize = (
                    input(
                        "\n[VISUALIZATION] Would you like to visualize the optimal route? (y/n): "
                    )
                    .strip()
                    .lower()
                )

                if visualize == "y":
                    # Visualize the first optimal algorithm's path
                    optimal_algo = result["optimal_algorithms"][0]
                    optimal_path = result["results"][optimal_algo]["path"]
                    optimal_distance_km = result["optimal_distance"] / 1000

                    system.visualize_route(
                        optimal_path,
                        optimal_algo,
                        start_location,
                        goal_location,
                        optimal_distance_km,
                    )

                print("\n[SUCCESS] Route search completed successfully!")

            # Ask if user wants to search again
            print("\n" + "=" * 70)
            again = (
                input("\n[REPEAT] Would you like to search for another route? (y/n): ")
                .strip()
                .lower()
            )
            if again != "y":
                print("\n[EXIT] Thank you for using Route Search System!")
                break

    except KeyboardInterrupt:
        print("\n\n[WARNING] Operation cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
