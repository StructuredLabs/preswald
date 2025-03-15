import json
import logging
import zlib
from datetime import date, datetime
from typing import Any, Dict, List, Union

import numpy as np

logger = logging.getLogger(__name__)


class PreswaldJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Preswald data types."""

    def default(self, obj: Any) -> Any:
        """Convert object to JSON serializable format."""
        try:
            if isinstance(obj, np.ndarray):
                return self._handle_ndarray(obj)
            elif isinstance(
                obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)
            ):
                return int(obj)
            elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
                if np.isnan(obj):
                    return None
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, (set, frozenset)):
                return list(obj)
            elif isinstance(obj, bytes):
                return obj.decode("utf-8")
            elif isinstance(obj, np.void):
                return None
            return super().default(obj)
        except Exception as e:
            logger.error(f"Error encoding object {type(obj)}: {e}")
            return None

    def _handle_ndarray(self, arr: np.ndarray) -> Union[List, None]:
        """Handle numpy array conversion."""
        try:
            if arr.dtype.kind in ["U", "S"]:  # Unicode or string
                return arr.astype(str).tolist()
            elif arr.dtype.kind == "M":  # Datetime
                return arr.astype(str).tolist()
            elif arr.dtype.kind == "m":  # Timedelta
                return arr.astype("timedelta64[ns]").astype(np.int64).tolist()
            elif arr.dtype.kind == "O":  # Object
                return [self.default(x) for x in arr]
            else:
                return self._handle_array_values(arr.tolist())
        except Exception as e:
            logger.error(f"Error handling ndarray: {e}")
            return None

    def _handle_array_values(self, arr: List) -> List:
        """Handle array values recursively."""
        if isinstance(arr, (list, tuple)):
            return [self._handle_array_values(x) for x in arr]
        elif isinstance(arr, (float, np.float_, np.float16, np.float32, np.float64)):
            if np.isnan(arr):
                return None
            return float(arr)
        elif isinstance(arr, (int, np.integer)):
            return int(arr)
        elif isinstance(arr, (str, bool)):
            return arr
        elif arr is None:
            return None
        else:
            try:
                return self.default(arr)
            except Exception as e:
                logger.error(f"Error handling array value: {e}")
                return str(arr)


def dumps(obj: Any, **kwargs) -> str:
    """
    Serialize obj to a JSON formatted str using the custom encoder.

    Args:
        obj: The object to serialize
        **kwargs: Additional arguments to pass to json.dumps

    Returns:
        JSON formatted string
    """
    try:
        return json.dumps(obj, cls=PreswaldJSONEncoder, **kwargs)
    except Exception as e:
        logger.error(f"Error serializing object: {e}")
        # Return a safe fallback
        return json.dumps({"error": "Serialization failed", "message": str(e)})


def loads(s: str, **kwargs) -> Any:
    """
    Deserialize s (a str instance containing a JSON document) to a Python object.

    Args:
        s: The JSON string to deserialize
        **kwargs: Additional arguments to pass to json.loads

    Returns:
        Deserialized Python object
    """
    try:
        return json.loads(s, **kwargs)
    except Exception as e:
        logger.error(f"Error deserializing JSON: {e}")
        return None


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
    json_str = dumps(data)
    return zlib.compress(json_str.encode("utf-8"))


def decompress_data(compressed_data: bytes) -> Union[Dict, List, str]:
    """Decompress zlib compressed data."""
    decompressed = zlib.decompress(compressed_data)
    return loads(decompressed.decode("utf-8"))
