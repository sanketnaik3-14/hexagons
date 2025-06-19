import folium
import h3

def visualize_h3_grid_on_map():
    """
    Generates an interactive Folium map with H3 hexagons for Navi Mumbai.
    This version is corrected for h3-py v4.x and the removal of the 'geo_json' parameter.
    """
    # 1. Define the center of our map (Vashi, Navi Mumbai)
    NAVI_MUMBAI_CENTER_LAT = 19.0760
    NAVI_MUMBAI_CENTER_LNG = 72.9945

    # Create the base map
    m = folium.Map(location=[NAVI_MUMBAI_CENTER_LAT, NAVI_MUMBAI_CENTER_LNG], zoom_start=13)

    # Add markers for context
    folium.Marker(
        [19.0671, 72.9987], popup="Vashi Railway Station", icon=folium.Icon(color="black", icon="train")
    ).add_to(m)
    folium.Marker(
        [19.0649, 73.0016], popup="Inorbit Mall, Vashi", icon=folium.Icon(color="black", icon="shopping-cart")
    ).add_to(m)
    folium.Marker(
        [19.0330, 73.0297], popup="Seawoods Grand Central", icon=folium.Icon(color="black", icon="building")
    ).add_to(m)

    # 2. Define the different resolutions we want to visualize
    COARSE_RESOLUTION = 7  # Regional level
    NEIGHBORHOOD_RESOLUTION = 9 # Neighborhood/Sector level
    HYPERLOCAL_RESOLUTION = 10 # Mall/Large Complex level

    # Helper function to draw hexagons
    def draw_hexagon(h3_index, color, popup_text, opacity):
        # --- START OF CORRECTION ---
        # v4 of the h3 library removed the `geo_json` parameter.
        # The function now returns a tuple of (lat, lng) tuples.
        # We need to format this for GeoJSON, which expects (lng, lat).
        lat_lng_boundary = h3.cell_to_boundary(h3_index)
        
        # GeoJSON format requires closing the loop by making the last point the same as the first.
        # And the coordinate order is [longitude, latitude].
        geojson_boundary = [[lon, lat] for lat, lon in lat_lng_boundary]
        geojson_boundary.append(geojson_boundary[0]) # Close the loop

        # Create the GeoJSON structure
        geo_json_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [geojson_boundary] # Needs to be nested in a list
            }
        }
        # --- END OF CORRECTION ---

        folium.GeoJson(
            data=geo_json_data,
            style_function=lambda x, color=color: {
                "fillColor": color,
                "color": "black",
                "weight": 1.5,
                "fillOpacity": opacity,
            },
            popup=folium.Popup(popup_text)
        ).add_to(m)

    # 3. Generate and draw the hexagons

    # a) Coarse Hexagon (Regional View)
    coarse_hex = h3.latlng_to_cell(NAVI_MUMBAI_CENTER_LAT, NAVI_MUMBAI_CENTER_LNG, COARSE_RESOLUTION)
    draw_hexagon(coarse_hex, '#007bff', f'<b>Resolution {COARSE_RESOLUTION} Hexagon</b><br>(Covers a large part of the city)', 0.2)

    # b) Neighborhood Hexagons
    neighborhood_hexes = h3.cell_to_children(coarse_hex, NEIGHBORHOOD_RESOLUTION)
    for hex_index in neighborhood_hexes:
        draw_hexagon(hex_index, '#ffc107', f'<b>Resolution {NEIGHBORHOOD_RESOLUTION} Hexagon</b><br>(Neighborhood/Sector Level)', 0.4)

    # c) Hyperlocal Hexagons around a specific point (Inorbit Mall)
    center_hyperlocal_hex = h3.latlng_to_cell(19.0649, 73.0016, HYPERLOCAL_RESOLUTION)
    hyperlocal_hexes = h3.grid_disk(center_hyperlocal_hex, 2)
    for hex_index in hyperlocal_hexes:
        draw_hexagon(hex_index, '#dc3545', f'<b>Resolution {HYPERLOCAL_RESOLUTION} Hexagon</b><br>(Hyperlocal: Mall/Complex Level)', 0.6)

    # 4. Save the map to an HTML file
    output_filename = "navi_mumbai_hex_grid_final.html"
    m.save(output_filename)
    
    return f"Successfully generated the map. Please open the file '{output_filename}' in your web browser."

# Run the function and print the result
print(visualize_h3_grid_on_map())
