from preswald.interfaces.components import with_render_tracking, ComponentReturn
import folium

@with_render_tracking("map")
def map_component(
    lat: float = 28.61,
    lon: float = 77.23,
    zoom_start: int = 4,
    component_id: str | None = None,
    **kwargs
) -> ComponentReturn:
    fmap = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    html_data = fmap._repr_html_()
    print("=== FOLIUM HTML DEBUG BEGIN ===")
    print(html_data[:500])
    print("=== FOLIUM HTML DEBUG END ===")
    component = {
        "type": "map",
        "id": component_id or "test-map",
        "html": html_data,
        "center": [lat, lon],
        "zoom": zoom_start,
    }
    return ComponentReturn({}, component)

# THIS LINE IS CRUCIAL:
map = map_component()