import os
from typing import Tuple, List, Optional

import numpy as np
from plotly import colors as pc, graph_objects as go
from plotly.basedatatypes import BaseTraceType
from util.latex import latex_to_html
from util.utils import normalize


def parse_rgb(color: str) -> Tuple[int, int, int]:
    if color.startswith('#'):
        hex_color = color.lstrip('#')
        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    else:
        r, g, b = map(int, color.strip('rgb()').split(','))
    return r, g, b


def rgb_to_str(color: Tuple[int, int, int], alpha: Optional[float] = None) -> str:
    if alpha is not None:
        return f'rgba({color[0]}, {color[1]}, {color[2]}, {alpha})'
    return f'rgb({color[0]}, {color[1]}, {color[2]})'


def mix_color_uniform(rgb_list: List[Tuple[int, int, int]]) -> Tuple[int, int, int]:
    if len(rgb_list) == 1:
        return rgb_list[0]

    rgb_array = np.asarray(rgb_list)
    return (int(np.mean(rgb_array[:, 0])),
            int(np.mean(rgb_array[:, 1])),
            int(np.mean(rgb_array[:, 2])))


def get_color_with_alpha(color: str, alpha: float) -> str:
    rgb = parse_rgb(color)
    return rgb_to_str(rgb, alpha)


def get_color(color_sequence_name: str, idx: int) -> str:
    color_sequence = getattr(pc.qualitative, color_sequence_name)
    return color_sequence[idx % len(color_sequence)]


def export_figure(figure: go.Figure, file_name: str, dir_name: str = "html"):
    os.makedirs(dir_name, exist_ok=True)
    figure.layout.height = None
    figure.layout.width = None
    figure.layout.autosize = True
    figure.write_html(os.path.join(dir_name, file_name), full_html=True, include_plotlyjs='cdn')


def plot_bloch_sphere() -> List[BaseTraceType]:
    traces: List[BaseTraceType] = []

    u, v = np.mgrid[0:2 * np.pi:60j, 0:np.pi:30j]
    xs = np.cos(u) * np.sin(v)
    ys = np.sin(u) * np.sin(v)
    zs = np.cos(v)
    traces.append(go.Surface(x=xs, y=ys, z=zs, opacity=0.03, showscale=False))

    axis_len = 1
    scale = 1.1
    traces.append(go.Scatter3d(x=[-axis_len, axis_len], y=[0, 0], z=[0, 0],
                               mode='lines', line=dict(color='red', width=1), name='x', showlegend=False))
    traces.append(go.Scatter3d(x=[-axis_len * scale, axis_len * scale], y=[0, 0], z=[0, 0],
                               mode='text', text=[latex_to_html(r'\ket{-}'), latex_to_html(r'\ket{+}')],
                               textposition='middle center', showlegend=False))
    traces.append(go.Scatter3d(x=[0, 0], y=[-axis_len, axis_len], z=[0, 0],
                               mode='lines', line=dict(color='green', width=1), name='y', showlegend=False))
    traces.append(go.Scatter3d(x=[0, 0], y=[-axis_len * scale, axis_len * scale], z=[0, 0],
                               mode='text', text=[latex_to_html(r'\ket{-i}'), latex_to_html(r'\ket{i}')],
                               textposition='middle center', showlegend=False))
    traces.append(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-axis_len, axis_len],
                               mode='lines', line=dict(color='blue', width=1), name='z', showlegend=False))
    traces.append(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-axis_len * scale, axis_len * scale],
                               mode='text', text=[latex_to_html(r'\ket{1}'), latex_to_html(r'\ket{0}')],
                               textposition='middle center', showlegend=False))

    return traces


def get_data_bounds(fig: go.Figure) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    xs, ys, zs = [], [], []
    for trace in fig.data:
        if hasattr(trace, 'x') and hasattr(trace, 'y') and hasattr(trace, 'z'):
            xs.extend(np.asarray(trace.x).ravel())
            ys.extend(np.asarray(trace.y).ravel())
            zs.extend(np.asarray(trace.z).ravel())
    return np.array(xs), np.array(ys), np.array(zs)


def apply_orthographic_zoom(fig: go.Figure, zoom: float) -> None:
    x, y, z = get_data_bounds(fig)
    cx, cy, cz = np.mean(x), np.mean(y), np.mean(z)
    rx, ry, rz = np.ptp(x), np.ptp(y), np.ptp(z)

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[cx - rx / 2 * zoom, cx + rx / 2 * zoom]),
            yaxis=dict(range=[cy - ry / 2 * zoom, cy + ry / 2 * zoom]),
            zaxis=dict(range=[cz - rz / 2 * zoom, cz + rz / 2 * zoom]),
            aspectmode='manual',
            aspectratio=dict(x=rx, y=ry, z=rz),
            camera=dict(
                projection=dict(type='orthographic')
            )
        )
    )


def create_cylinder(p0: np.ndarray, p1: np.ndarray, radius: float, color: str,
                    resolution: int = 40) -> go.Mesh3d:
    v = normalize(p1 - p0)

    not_v = np.array([1, 0, 0]) if abs(v[0]) < 0.99 else np.array([0, 1, 0])
    n1 = normalize(np.cross(v, not_v))
    n2 = np.cross(v, n1)

    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    circle = radius * (np.outer(np.cos(theta), n1) + np.outer(np.sin(theta), n2))

    bottom = p0 + circle
    top = p1 + circle

    x = np.hstack([bottom[:, 0], top[:, 0], p0[0], p1[0]])
    y = np.hstack([bottom[:, 1], top[:, 1], p0[1], p1[1]])
    z = np.hstack([bottom[:, 2], top[:, 2], p0[2], p1[2]])

    faces = []
    for i in range(resolution):
        j = (i + 1) % resolution
        faces.append([i, j, resolution + i])
        faces.append([j, resolution + j, resolution + i])

    for i in range(resolution):
        j = (i + 1) % resolution
        faces.append([i, j, 2 * resolution])

    for i in range(resolution):
        j = (i + 1) % resolution
        faces.append([resolution + i, 2 * resolution + 1, resolution + j])

    i, j, k = zip(*faces)

    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=1.0, flatshading=True)


def update_layout(fig: go.Figure):
    fig.update_layout(xaxis=dict(range=[-2.5, 2.5], showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(range=[-2.5, 2.5], showgrid=False, zeroline=False, showticklabels=False,
                                 scaleanchor="x", scaleratio=1),
                      margin=dict(l=0, r=0, t=0, b=0),
                      plot_bgcolor='white', title=None, showlegend=False)
