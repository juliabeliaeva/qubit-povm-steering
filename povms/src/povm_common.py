import math
from typing import List, Tuple, Set, Dict

import numpy as np
from plotly import graph_objects as go
from plotly.basedatatypes import BaseTraceType
from qubit_povm import QubitPovm
from slides import SlideBuilder
from util.plotly import get_color_with_alpha
from util.utils import normalize


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
    return get_labels_for_outcomes(povm.n_outcomes)


def get_labels_for_outcomes(n_outcomes: int):
    if n_outcomes == 2:
        result = [r"\hat{x}", r"-\hat{x}"]
    else:
        result = [r"\hat{x}_{" + str(i + 1) + "}" for i in range(n_outcomes)]
    return [rf"${r}$" for r in result]


def get_response_table_pvm(povm: QubitPovm) -> Dict[Tuple[int, Tuple], float]:
    result: Dict[Tuple[int, Tuple], float] = {}
    for hemisphere_indices in [{0}, {1}, {2}, {0, 1}, {0, 2}, {1, 2}]:
        result.update({(idx, tuple(sorted(hemisphere_indices))): 2 * povm.mus[idx] for idx in range(povm.n_outcomes)
                       if idx in hemisphere_indices})
    return result


def plot_response_function(slide_builder: SlideBuilder, povm: QubitPovm,
                           vector_angles: List[float], vector_colors: List[str],
                           line_angles: List[float], response_table: Dict[Tuple[int, Tuple], float],
                           radius: float = 1, width=8) -> Set[int]:
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
                           mode='lines', line=dict(color=line_color, width=width),
                           showlegend=False, hoverinfo='skip'))
            traces.add(trace_id)
            start = end
    return traces


def get_hemisphere_indices(angle: float, vector_angles: List[float]) -> Set[int]:
    inner_products = [math.cos(angle - vector_angle) for vector_angle in vector_angles]
    return set([i for i, inner in enumerate(inner_products) if inner >= 0])


def plot_povm_vectors(slide_builder: SlideBuilder, vectors: List[Tuple[float, str, str]],
                      radius: float, label_distance=0.1) -> Tuple[List[int], List[int]]:
    vector_traces = []
    label_traces = []
    for vector_angle, vector_name, vector_color in vectors:
        x = radius * math.cos(vector_angle)
        y = radius * math.sin(vector_angle)
        vector_traces.append(slide_builder.add_trace(go.Scatter(x=[0, x], y=[0, y],
                                                                mode='lines', zorder=10,
                                                                line=dict(color=vector_color, width=8),
                                                                name=vector_name)))
        normal_x, normal_y = (y, -x) if x > 0 else (-y, x)
        label_traces.append(slide_builder.add_trace(go.Scatter(x=[0.5 * x + normal_x * label_distance],
                                                               y=[0.5 * y + normal_y * label_distance],
                                                               mode='text',
                                                               text=[vector_name],
                                                               textposition='middle center',
                                                               textfont=dict(size=32), zorder=10)))
    vector_traces.append(slide_builder.add_trace(go.Scatter(x=[0], y=[0], mode='markers',
                                                            marker=dict(color='black', size=8), zorder=11)))
    return vector_traces, label_traces


def plot_hemispheres(slide_builder: SlideBuilder, vectors: List[Tuple[float, str, str]], radius: float):
    for vector_angle, vector_name, vector_color in vectors:
        thetas = np.linspace(vector_angle - np.pi / 2, vector_angle + math.pi / 2, 50)
        arc_x = radius * np.cos(thetas)
        arc_y = radius * np.sin(thetas)
        hemisphere_x = np.concatenate([arc_x, [0], [arc_x[0]]])
        hemisphere_y = np.concatenate([arc_y, [0], [arc_y[0]]])

        transparent_color = get_color_with_alpha(vector_color, 0.35)
        slide_builder.add_trace(go.Scatter(x=hemisphere_x, y=hemisphere_y,
                                           fill='toself', fillcolor=transparent_color, line=dict(color='black'),
                                           hoverinfo='skip'))


def plot_sphere(center: np.ndarray = np.zeros(3), radius: float = 1) -> BaseTraceType:
    u, v = np.mgrid[0:2 * np.pi:60j, 0:np.pi:30j]
    xs = radius * np.cos(u) * np.sin(v) + center[0]
    ys = radius * np.sin(u) * np.sin(v) + center[1]
    zs = radius * np.cos(v) + center[2]
    return go.Surface(x=xs, y=ys, z=zs, opacity=0.03, showscale=False, hoverinfo='skip')
