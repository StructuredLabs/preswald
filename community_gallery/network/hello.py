import pandas as pd
import plotly.graph_objects as go

from preswald import plotly, table, text


text("# Network Topology Visualizer")
text("Visualize the topology of a network.")

df = pd.read_csv("data.csv")
table(df)

# Create a list of devices
devices = df["Device Name"].unique()

# Generate device positions programmatically (spread along x and y)
device_positions = {}
y_offset = 1.25  # initial y offset for device positioning
x_offset = 0.0  # initial x offset for device positioning
layer_spacing = 2  # spacing between layers

# Place devices along the x-axis with layers for the connections
for i, device in enumerate(devices):
    device_positions[device] = (
        x_offset,
        y_offset - (0.25 if x_offset % 4 == 0 else -0.25),
    )
    y_offset -= layer_spacing  # Adjust vertical spacing between layers
    if i % 3 == 2:  # Every 3 devices, move to the next column
        x_offset += 2
        y_offset = 1  # Reset the y-offset for new column

# Create a mapping of device names to their IDs for easy indexing
device_name_to_id = {device: idx for idx, device in enumerate(devices)}

# Create edges from the 'Connected To' column in the CSV
edges = []
for _, row in df.iterrows():
    from_device = row["Device Name"]
    to_device = row["Connected To"]

    if to_device in device_name_to_id:
        edges.append((device_name_to_id[from_device], device_name_to_id[to_device]))

# Extract node positions and labels
node_x = [device_positions[device][0] for device in devices]
node_y = [device_positions[device][1] for device in devices]
node_labels = devices

# Create edge coordinates (midpoints)
edge_x = []
edge_y = []
for edge in edges:
    x0, y0 = device_positions[devices[edge[0]]]
    x1, y1 = device_positions[devices[edge[1]]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_y.append(y0)
    edge_y.append(y1)

# Create Plotly figure
fig = go.Figure()

# Add edges
fig.add_trace(
    go.Scatter(
        x=edge_x,
        y=edge_y,
        line={"width": 1, "color": "gray"},
        hoverinfo="none",
        mode="lines",
    )
)

# Add nodes
fig.add_trace(
    go.Scatter(
        x=node_x,
        y=node_y,
        text=node_labels,
        mode="markers+text",
        marker={
            "size": 18,
            "color": "#00cccc",
            "line": {"width": 1, "color": "#006a6a"},
        },
        textposition="bottom center",
    )
)

# Layout
fig.update_layout(
    title="Network Topology",
    showlegend=False,
    xaxis={"showgrid": False, "zeroline": False, "range": [-1, x_offset + 1]},
    yaxis={"showgrid": False, "zeroline": False, "range": [-len(devices) / 3 - 1, 2]},
    plot_bgcolor="white",
)

plotly(fig)
