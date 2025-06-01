import math
from typing import List, Tuple, Set, Dict

import numpy as np
import plotly.graph_objects as go

from plotly_utils import get_color_with_alpha
from povms import QubitPovm, plot_povm
from presentations.povms.slides import SlideBuilder
from quantum_utils import normalize


def read_md(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content.split('<!---->')


def get_angle(u: np.ndarray, v: np.ndarray, normal: np.ndarray) -> float:
    u = normalize(u)
    v = normalize(v)
    cross = np.cross(u, v)
    angle = np.arccos(np.clip(np.dot(u, v), -1.0, 1.0))
    if np.dot(cross, normal) < 0:
        return 2 * np.pi - angle
    return angle


def get_angles(povm: QubitPovm) -> List[float]:
    if povm.n_outcomes == 2:
        start_angle = math.pi / 4
        return [start_angle, start_angle + math.pi]
    normal = np.cross(povm.vectors[0], povm.vectors[1])
    return [0.0,
            get_angle(povm.vectors[0], povm.vectors[1], normal),
            get_angle(povm.vectors[0], povm.vectors[2], normal)]


def get_labels(povm: QubitPovm) -> List[str]:
    if povm.n_outcomes == 2:
        return ["x", "-x"]
    return [f"x<sub>{i + 1}</sub>" for i in range(povm.n_outcomes)]


def get_response_table_pvm(povm: QubitPovm) -> Dict[Tuple[int, Tuple], float]:
    result: Dict[Tuple[int, Tuple], float] = {}
    for hemisphere_indices in [{0}, {1}, {2}, {0, 1}, {0, 2}, {1, 2}]:
        result.update({(idx, tuple(sorted(hemisphere_indices))): 2 * povm.mus[idx] for idx in range(povm.n_outcomes)
                       if idx in hemisphere_indices})
    return result


def plot_response_function(slide_builder: SlideBuilder, povm: QubitPovm,
                           vector_angles: List[float], vector_colors: List[str],
                           line_angles: List[float], response_table: Dict[Tuple[int, Tuple], float],
                           radius: float = 1) -> Set[int]:
    traces = set()
    for line_angle in line_angles:
        hemisphere_indices = get_hemisphere_indices(line_angle, vector_angles)

        start = radius
        for vector_index in range(povm.n_outcomes):
            response_key = (vector_index, tuple(sorted(hemisphere_indices)))
            if not response_key in response_table:
                continue

            line_color = vector_colors[vector_index]
            end = start + radius * response_table[response_key]
            trace_id = slide_builder.add_trace(
                go.Scatter(x=[start * math.cos(line_angle), end * math.cos(line_angle)],
                           y=[start * math.sin(line_angle), end * math.sin(line_angle)],
                           mode='lines', line=dict(color=line_color, width=8),
                           showlegend=False, hoverinfo='skip'))
            traces.add(trace_id)
            start = end
    return traces


def get_hemisphere_indices(angle: float, vector_angles: List[float]) -> Set[int]:
    inner_products = [math.cos(angle - vector_angle) for vector_angle in vector_angles]
    return set([i for i, inner in enumerate(inner_products) if inner >= 0])


def plot_povm_vectors(slide_builder: SlideBuilder, vectors: List[Tuple[float, str, str]],
                      radius: float) -> List[int]:
    traces = []
    for vector_angle, vector_name, vector_color in vectors:
        x = radius * math.cos(vector_angle)
        y = radius * math.sin(vector_angle)
        traces.append(slide_builder.add_trace(go.Scatter(x=[0, x / 2, x], y=[0, y / 2, y],
                                                         mode='lines+text', line=dict(color=vector_color, width=8),
                                                         text=['', " " + vector_name, ''], textposition='bottom center',
                                                         textfont=dict(size=32), zorder=10,
                                                         name=vector_name)))
    return traces


def plot_hemispheres(slide_builder: SlideBuilder, vectors: List[Tuple[float, str, str]], radius: float):
    for vector_angle, vector_name, vector_color in vectors:
        thetas = np.linspace(vector_angle - np.pi / 2, vector_angle + math.pi / 2, 50)
        arc_x = radius * np.cos(thetas)
        arc_y = radius * np.sin(thetas)
        hemisphere_x = np.concatenate([arc_x, [0], [arc_x[0]]])
        hemisphere_y = np.concatenate([arc_y, [0], [arc_y[0]]])

        transparent_color = get_color_with_alpha(vector_color, 0.3)
        slide_builder.add_trace(go.Scatter(x=hemisphere_x, y=hemisphere_y,
                                           fill='toself', fillcolor=transparent_color, line=dict(color='black'),
                                           hoverinfo='skip'))


def update_layout(fig: go.Figure):
    fig.update_layout(xaxis=dict(range=[-2.5, 2.5], showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(range=[-2.5, 2.5], showgrid=False, zeroline=False, showticklabels=False,
                                 scaleanchor="x", scaleratio=1),
                      font=dict(family="Palatino Linotype, Book Antiqua, Palatino, serif"),
                      margin=dict(l=0, r=0, t=0, b=0),
                      plot_bgcolor='white', title=None, showlegend=False)


def plot_3d_povm(povm: QubitPovm) -> go.Figure:
    fig = plot_povm(povm)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                      scene=dict(dragmode="orbit"),
                      uirevision="constant")
    return fig
