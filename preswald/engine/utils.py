import zlib
from typing import Any, Dict, List, Union

from preswald.serializer import dumps as json_dumps
from preswald.serializer import loads as json_loads


def clean_nan_values(obj):
    """Clean NaN values from an object recursively."""
    import numpy as np

    if isinstance(obj, (float, np.floating)):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, (list, tuple)):
        return [clean_nan_values(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, np.ndarray):
        if obj.dtype.kind in ["f", "c"]:  # Float or complex
            obj = np.where(np.isnan(obj), None, obj)
        return obj.tolist()
    return obj


def optimize_plotly_data(
    data: Dict[str, Any], max_points: int = 5000
) -> Dict[str, Any]:
    """Optimize Plotly data for large datasets."""
    if not isinstance(data, dict) or "data" not in data:
        return data

    optimized_data = {"data": [], "layout": data.get("layout", {})}

    for trace in data["data"]:
        if not isinstance(trace, dict):
            continue

        # Handle scatter/scattergeo traces
        if trace.get("type") in ["scatter", "scattergeo"]:
            points = (
                len(trace.get("x", [])) if "x" in trace else len(trace.get("lat", []))
            )
            if points > max_points:
                # Calculate sampling rate
                sample_rate = max(1, points // max_points)

                # Sample the data
                if "x" in trace and "y" in trace:
                    trace["x"] = trace["x"][::sample_rate]
                    trace["y"] = trace["y"][::sample_rate]
                elif "lat" in trace and "lon" in trace:
                    trace["lat"] = trace["lat"][::sample_rate]
                    trace["lon"] = trace["lon"][::sample_rate]

                # Sample other array attributes
                for key in ["text", "marker.size", "marker.color"]:
                    if key in trace:
                        if isinstance(trace[key], list):
                            trace[key] = trace[key][::sample_rate]

        optimized_data["data"].append(trace)

    return optimized_data


def compress_data(data: Union[Dict, List, str]) -> bytes:
    """Compress data using zlib."""
    json_str = json_dumps(data)
    return zlib.compress(json_str.encode("utf-8"))


def decompress_data(compressed_data: bytes) -> Union[Dict, List, str]:
    """Decompress zlib compressed data."""
    decompressed = zlib.decompress(compressed_data)
    return json_loads(decompressed.decode("utf-8"))
