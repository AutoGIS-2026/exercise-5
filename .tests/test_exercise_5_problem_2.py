"""Basic checks for exercise 5, problem 2 (interactive map). Graded manually: no points."""

import re

from points_decorator import points


# Signatures of common web mapping libraries in a saved HTML file
WEB_MAP_LIBRARIES = ("leaflet", "plotly", "bokeh", "maplibre", "mapbox", "openlayers", "deck.gl", "kepler")

# Leaflet (folium) layers that show data (base map tiles do not count)
LEAFLET_DATA_LAYERS = re.compile(
    r"L\.(geoJson|marker|circleMarker|circle|polygon|polyline|rectangle|heatLayer|"
    r"markerClusterGroup|imageOverlay|tileLayer\.wms|vectorGrid\.\w+)\("
)
LEAFLET_INTERACTIONS = re.compile(r"bindPopup|bindTooltip|L\.control\.layers|L\.Control\.")


def html_files(output_directory):
    return sorted(output_directory.glob("*.html"))


def html_texts(output_directory):
    return [path.read_text(encoding="utf-8", errors="replace") for path in html_files(output_directory)]


def is_leaflet(html):
    return "leaflet" in html.lower() and "L.map(" in html


class TestProblem2:
    @points(0, "Problem 2: Save your interactive map as an HTML file in the `docs` folder, and add, commit and push it.")
    def test_html_file_exists(self, output_directory):
        assert html_files(output_directory)

    @points(0, "Problem 2: The HTML file in `docs` does not seem to contain an interactive (web) map.")
    def test_html_is_web_map(self, output_directory):
        texts = html_texts(output_directory)
        assert texts
        assert any(
            library in html.lower()
            for html in texts
            for library in WEB_MAP_LIBRARIES
        )

    @points(0, "Problem 2: Your interactive map seems to show only one data layer (base maps do not count).")
    def test_html_has_two_layers(self, output_directory):
        texts = html_texts(output_directory)
        assert texts
        leaflet_maps = [html for html in texts if is_leaflet(html)]
        if not leaflet_maps:
            return  # can only check maps made with folium/leaflet
        assert any(len(LEAFLET_DATA_LAYERS.findall(html)) >= 2 for html in leaflet_maps)

    @points(0, "Problem 2: Your interactive map does not seem to have interactive elements, such as pop-ups, tooltips or a layer control.")
    def test_html_is_interactive(self, output_directory):
        texts = html_texts(output_directory)
        assert texts
        leaflet_maps = [html for html in texts if is_leaflet(html)]
        if not leaflet_maps:
            return  # can only check maps made with folium/leaflet
        assert any(LEAFLET_INTERACTIONS.search(html) for html in leaflet_maps)

    @points(0, "Problem 2: Add, commit and push the code you used to create your map to `Exercise-5-problem-2.ipynb`.")
    def test_notebook_has_code(self, problem2_code):
        assert len(problem2_code) >= 5
