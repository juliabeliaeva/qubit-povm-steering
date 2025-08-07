import random
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict, Set

import numpy as np
import plotly.graph_objects as go
from numpy.ma.core import zeros_like
from plotly.basedatatypes import BaseTraceType
from scipy.spatial import ConvexHull

from crossections import make_orthogonal
from latex_util import latex_to_html
from plotly_utils import get_color, parse_rgb, mix_color_uniform, rgb_to_str, apply_orthographic_zoom, create_cylinder
from povms import QubitPovm, plot_sphere
from presentations.povms.povm3 import get_x_y, get_response_table
from presentations.povms.povms_common import read_md
from presentations.povms.slides import SlideBuilder
from quantum_utils import normalize

povm4_text = read_md("data/povm4.md")

color_sequence = "D3"
x5_labels = [latex_to_html("x̂_{5^{+}}"), latex_to_html("x̂_{5^{-}}")]

colors = [get_color("D3", 0), get_color("D3", 2),
          get_color("D3", 3), get_color("T10", 5)]
x5_colors = [get_color(color_sequence, i) for i in [7, 7]]


def plot_povm4(povm: QubitPovm, radius=1.0) -> SlideBuilder:
    slide_builder = SlideBuilder("4-Outcome POVMs")
    slide_builder.add_line(povm4_text['4out'])

    slide_builder.add_trace(plot_sphere(radius=radius))

    labels = [latex_to_html(f"x̂_{str(i + 1)}") for i in range(povm.n_outcomes)]
    plot_vectors(slide_builder, povm.vectors, colors, labels, radius=radius)

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['pseudo1'])

    x5, mu5 = get_x5_mu5(povm)
    plot_vectors(slide_builder, [x5, -x5], x5_colors, x5_labels)

    slide_builder.next_step()

    triangle1_points = np.vstack([povm.vectors[0], povm.vectors[1], x5, povm.vectors[0]])
    triangle2_points = np.vstack([povm.vectors[2], povm.vectors[3], -x5, povm.vectors[2]])
    for tp, color in zip([triangle1_points, triangle2_points], x5_colors):
        x = tp[:, 0]
        y = tp[:, 1]
        z = tp[:, 2]
        slide_builder.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color=color, width=1)))
        mesh = get_polygon_mesh(x, y, z, 'white', opacity=0.7)
        slide_builder.add_trace(mesh)

    povm3_lines = []
    povm3_lines.append(slide_builder.add_line(povm4_text['povm3']))
    povm3_lines.append(slide_builder.add_line(povm4_text['pseudo2']))

    slide_builder.next_step()
    povm3_lines.append(slide_builder.add_line(povm4_text['povm3weknow']))

    slide_builder.next_step()
    slide_builder.hide_all_lines()
    slide_builder.add_line(povm4_text['povm3weknow2'])

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['povm3weknow3'])

    update_layout(slide_builder)
    update_meshes_lighting(slide_builder)

    return slide_builder


def get_polygon_mesh(x: np.ndarray, y: np.ndarray, z: np.ndarray, color: str,
                     opacity: float = 0.5) -> BaseTraceType:
    vertices = np.hstack([x[:, None], y[:, None], z[:, None]])
    vertices = np.vstack([np.array([[0, 0, 0]]), vertices])

    n = len(x)

    ti, tj, tk = [], [], []
    ti.extend([0] * (n - 1))
    tj.extend(list(range(1, n)))
    tk.extend(list(range(2, n + 1)))

    return go.Mesh3d(
        x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
        i=ti, j=tj, k=tk, opacity=opacity, color=color, showscale=False
    )


def update_layout(slide_builder: SlideBuilder):
    slide_builder.fig.update_layout(scene=dict(xaxis=dict(visible=False),
                                               yaxis=dict(visible=False),
                                               zaxis=dict(visible=False)),
                                    scene_camera=dict(eye=dict(x=1, y=0, z=1)),
                                    font=dict(family="Palatino Linotype, Book Antiqua, Palatino, serif"),
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    plot_bgcolor='white', title=None, showlegend=False, hovermode=False)
    apply_orthographic_zoom(slide_builder.fig, zoom=2)


def update_meshes_lighting(slide_builder: SlideBuilder):
    for trace in slide_builder.fig.data:
        if isinstance(trace, go.Mesh3d):
            trace.lighting = dict(ambient=0.95, diffuse=0.8, specular=0.7, roughness=0.9)
            trace.lightposition = dict(x=0.5, y=1, z=0)


def plot_povm3_response() -> SlideBuilder:
    slide_builder = SlideBuilder("Response Functions for Coarse-Grained POVMs")
    slide_builder.add_line(povm4_text['responsepm'])
    return slide_builder


def plot_povm4_plus_minus_regions(povm: QubitPovm, radius=1) -> SlideBuilder:
    slide_builder = SlideBuilder("Merging Regions $\\operatorname{POVM}_+$ and $\\operatorname{POVM}_-$")

    center1 = np.array([0, -1.3 * radius, 0])
    center2 = np.array([0, 1.3 * radius, 0])

    sphere_trace1 = slide_builder.add_trace(plot_sphere(center=center1, radius=radius))
    sphere_trace2 = slide_builder.add_trace(plot_sphere(center=center2, radius=radius))

    x5, mu5 = get_x5_mu5(povm)
    vectors_plus = [povm.vectors[0], povm.vectors[1], x5]
    vectors_minus = [povm.vectors[2], povm.vectors[3], -x5]

    labels = [latex_to_html(f"x̂_{str(i + 1)}") for i in range(povm.n_outcomes)]
    labels_plus = [*labels[:2], x5_labels[0]]
    labels_minus = [*labels[2:], x5_labels[1]]

    colors_plus = [*colors[:2], x5_colors[0]]
    colors_minus = [*colors[2:], x5_colors[1]]

    region_colors_plus = [*colors_plus[:2], "rgb(0, 0, 0)"]
    region_colors_minus = [*colors_minus[:2], "rgb(255, 255, 255)"]

    vector_traces1 = plot_vectors(slide_builder, vectors_plus, colors_plus, labels_plus, center=center1,
                                  radius=radius)
    vector_traces2 = plot_vectors(slide_builder, vectors_minus, colors_minus, labels_minus, center=center2,
                                  radius=radius)
    label_height = 1.5 * radius
    label_depth = 0.3 * radius
    label_traces = plot_plot_labels(slide_builder, [center1, center2], ["$POVM_+$", "$POVM_-$"],
                                    label_height, label_depth)

    slide_builder.next_step()

    slide_builder.hide_traces(label_traces)

    x5_axes_traces = []
    for x, center in zip([x5, -x5], [center1, center2]):
        d = 1.3
        t = slide_builder.add_trace(go.Scatter3d(x=[-d * radius * x[0] + center[0], d * radius * x[0] + center[0]],
                                                 y=[-d * radius * x[1] + center[1], d * radius * x[1] + center[1]],
                                                 z=[-d * radius * x[2] + center[2], d * radius * x[2] + center[2]],
                                                 mode='lines',
                                                 line=dict(width=2, color='black')))
        x5_axes_traces.append(t)

    label_traces = plot_plot_labels(slide_builder, [center1, center2], ["$\\Pi^+_{A_+}$", "$\\Pi^-_{A_-}$"],
                                    label_height, label_depth)

    slide_builder.hide_trace(sphere_trace1)
    slide_builder.hide_trace(sphere_trace2)

    circle_traces = []
    for i, (c, v) in enumerate(zip([center1, center2], [x5, -x5])):
        circle_x, circle_y, circle_z = get_circle_points(c, v, radius=1.0005, num_points=200)
        width = 7
        circle_traces.append(slide_builder.add_trace(go.Scatter3d(x=circle_x, y=circle_y, z=circle_z,
                                                                  mode='lines',
                                                                  line={"width": width, "color": "black"})))

    slide_builder.hide_traces(vector_traces1 + vector_traces2)

    regions_plus = plot_6regions(center1, vectors_plus, region_colors_plus)
    regions_minus = plot_6regions(center2, vectors_minus, region_colors_minus)
    traces_6regions = slide_builder.add_traces(regions_plus + regions_minus)

    slide_builder.next_step()
    slide_builder.hide_traces(traces_6regions + x5_axes_traces + circle_traces + label_traces)

    new_center1 = np.array([0, -2.3 * radius, 0])
    new_center2 = np.array([0, 2.3 * radius, 0])
    regions_plus2 = plot_6regions(new_center1, vectors_plus, region_colors_plus)
    regions_minus2 = plot_6regions(new_center2, vectors_minus, region_colors_minus)

    slide_builder.add_traces(regions_plus2 + regions_minus2)
    center3 = np.array([0, 0, 0])
    slide_builder.add_traces(plot_regions(get_18_regions(vectors_plus, region_colors_plus,
                                                         vectors_minus, region_colors_minus),
                                          center3))

    plot_plot_labels(slide_builder, [new_center1, new_center2, zeros_like(new_center1)],
                     ["$\\Pi^+_{A_+}$", "$\\Pi^-_{A_-}$", "$\\Pi_{A = A_+ ∩ A_-}$"],
                     label_height, label_depth)

    update_layout(slide_builder)
    update_meshes_lighting(slide_builder)

    return slide_builder


def plot_plot_labels(slide_builder: SlideBuilder, centers: List[np.ndarray], plot_labels: List[str],
                     label_height: float, label_depth: float) -> List[int]:
    label_traces = []
    for center, label in zip(centers, plot_labels):
        t = slide_builder.add_trace(go.Scatter3d(x=[center[0] - label_depth],
                                                 y=[center[1]],
                                                 z=[label_height + center[2]],
                                                 mode='text', textfont=dict(size=30),
                                                 text=[latex_to_html(label)], textposition='middle center'))
        label_traces.append(t)
    return label_traces


def plot_povm4_response(povm: QubitPovm, radius: float = 1) -> SlideBuilder:
    slide_builder = SlideBuilder("Simulation with 18-Outcome POVM")

    x5, mu5 = get_x5_mu5(povm)

    vectors_plus = [povm.vectors[0], povm.vectors[1], x5]
    vectors_minus = [povm.vectors[2], povm.vectors[3], -x5]

    colors_plus = [*colors[:2], x5_colors[0]]
    colors_minus = [*colors[2:], x5_colors[1]]

    region_colors_plus = [*colors_plus[:2], "rgb(0, 0, 0)"]
    region_colors_minus = [*colors_minus[:2], "rgb(255, 255, 255)"]

    regions = get_18_regions(vectors_plus, region_colors_plus, vectors_minus, region_colors_minus, n=5000)
    region_traces = plot_regions(regions, np.zeros(3), show_labels=True)
    region_traces = slide_builder.add_traces(region_traces)
    slide_builder.add_line(povm4_text['18regions'])

    slide_builder.next_step()
    sim1 = slide_builder.add_line(povm4_text['18regionssim'])

    slide_builder.next_step()
    slide_builder.hide_line(sim1)
    slide_builder.add_line(povm4_text['18regionssim2'])

    slide_builder.hide_traces(region_traces)
    six_regions = get_6regions(vectors_plus, region_colors_plus)
    filtered_six_regions = [r for r in six_regions if
                            r.h_idx[0] == (0, 1) or r.h_idx[0] == (0, 2) or r.h_idx[0] == (0,) or r.h_idx[0] == (2,)]
    six_regions_traces = slide_builder.add_traces(plot_regions(filtered_six_regions, np.zeros(3),
                                                               show_labels=True, d=1.2))

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionssim3'])
    slide_builder.hide_traces(six_regions_traces)

    filtered_full_regions = [r for r in regions if
                             r.h_idx[0] == (0, 1) or r.h_idx[0] == (0, 2) or r.h_idx[0] == (0,) or r.h_idx[0] == (2,)]
    filtered_full_regions_traces = slide_builder.add_traces(plot_regions(filtered_full_regions, np.zeros(3),
                                                                         show_labels=True))

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionssim4'])

    slide_builder.next_step()
    slide_builder.hide_all_lines()
    slide_builder.hide_traces(filtered_full_regions_traces)

    filtered_full_regions = [r for r in regions if
                             r.h_idx[0] == (0, 1) or r.h_idx[1] == (1, 2)]
    filtered_full_regions_traces = slide_builder.add_traces(plot_regions(filtered_full_regions, np.zeros(3),
                                                                         show_labels=True))

    slide_builder.add_line(povm4_text['18regionssimall'])

    slide_builder.next_step()
    norm_line = slide_builder.add_line(povm4_text['18regionsnorm1'])

    slide_builder.next_step()
    slide_builder.hide_line(norm_line)
    norm_line = slide_builder.add_line(povm4_text['18regionsnorm2'])

    slide_builder.next_step()
    slide_builder.hide_line(norm_line)
    norm_line = slide_builder.add_line(povm4_text['18regionsnorm3'])

    update_layout(slide_builder)
    eye_distance = 1.5
    slide_builder.fig.update_layout(scene_camera=dict(eye=dict(x=eye_distance * 1, y=0,
                                                               z=eye_distance * 1)))
    update_meshes_lighting(slide_builder)

    return slide_builder


def plot_povm4_response_diagram() -> SlideBuilder:
    slide_builder = SlideBuilder("Simulation with 18-Outcome POVM")

    slide_builder.add_line(povm4_text['18regionsdiagram'])
    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionsdiagram2'])
    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionsdiagram3'])
    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionsdiagram4'])
    slide_builder.next_step()
    slide_builder.add_line(povm4_text['18regionsnewnorm'])

    return slide_builder


def plot_povm4_normalization(povm: QubitPovm, radius: float = 1) -> SlideBuilder:
    slide_builder = SlideBuilder("Defining Response Function for 18-Outcome POVM")

    center1 = np.array([0, -1.5 * radius, 0])
    center2 = np.array([0, 1.5 * radius, 0])

    x5, mu5 = get_x5_mu5(povm)

    colors_plus = [x5_colors[0], *colors[:2]]
    colors_minus = [x5_colors[1], *colors[2:]]

    region_colors_plus = ["rgb(0, 0, 0)", *colors_plus[1:]]
    region_colors_minus = ["rgb(255, 255, 255)", *colors_minus[1:]]
    vectors_plus = [x5, povm.vectors[0], povm.vectors[1]]
    vectors_minus = [-x5, povm.vectors[2], povm.vectors[3]]

    sphere_scale = 0.5
    regions_plus = get_6regions(vectors_plus, region_colors_plus, radius=sphere_scale * radius, n=10000, alpha=None)
    regions_minus = get_6regions(vectors_minus, region_colors_minus, radius=sphere_scale * radius, n=10000, alpha=None)
    regions_plus_traces = plot_regions(regions_plus, center1)
    regions_minus_traces = plot_regions(regions_minus, center2)
    region6_traces = slide_builder.add_traces(regions_plus_traces + regions_minus_traces)

    slide_builder.next_step()

    k_plus = mu5 + povm.mus[0] + povm.mus[1]
    povm_plus = QubitPovm(vectors_plus,
                          [mu5 / k_plus, povm.mus[0] / k_plus, povm.mus[1] / k_plus], 0.5)
    x_plus, y_plus = get_x_y(povm_plus)
    response_table_plus = get_response_table(povm_plus, x_plus, y_plus)

    k_minus = mu5 + povm.mus[2] + povm.mus[3]
    povm_minus = QubitPovm(vectors_minus,
                           [mu5 / k_minus, povm.mus[2] / k_minus, povm.mus[3] / k_minus], 0.5)
    x_minus, y_minus = get_x_y(povm_minus)
    response_table_minus = get_response_table(povm_minus, x_minus, y_minus)

    r1_vector_traces = plot_response_vectors(slide_builder, regions_plus, center1,
                                             radius=radius, sphere_scale=sphere_scale)
    r2_vector_traces = plot_response_vectors(slide_builder, regions_minus, center2,
                                             radius=radius, sphere_scale=sphere_scale)

    r1_traces = plot_response_function(slide_builder, povm_plus, regions_plus, response_table_plus, center1,
                                       colors_plus, radius=radius, sphere_scale=sphere_scale)
    r2_traces = plot_response_function(slide_builder, povm_minus, regions_minus, response_table_minus, center2,
                                       colors_minus, radius=radius, sphere_scale=sphere_scale)
    slide_builder.next_step()
    slide_builder.hide_traces(r1_traces)
    slide_builder.hide_traces(r2_traces)

    r1_traces = plot_response_function(slide_builder, povm_plus, regions_plus, response_table_plus, center1,
                                       colors_plus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)
    r2_traces = plot_response_function(slide_builder, povm_minus, regions_minus, response_table_minus, center2,
                                       colors_minus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)
    slide_builder.next_step()
    slide_builder.hide_traces(r1_traces)
    slide_builder.hide_traces(r2_traces)

    response_table_plus_scaled = {k: k_plus * v if k[0] != 0 else (1 - k_plus * (1 - v))
                                  for k, v in response_table_plus.items()}
    response_table_minus_scaled = {k: k_minus * v if k[0] != 0 else (1 - k_minus * (1 - v))
                                   for k, v in response_table_minus.items()}
    r1_traces = plot_response_function(slide_builder, povm_plus, regions_plus, response_table_plus_scaled, center1,
                                       colors_plus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)
    r2_traces = plot_response_function(slide_builder, povm_minus, regions_minus, response_table_minus_scaled, center2,
                                       colors_minus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)

    slide_builder.next_step()

    distance = 1.1 * radius
    direction_plus = get_direction(regions_plus[0])
    label1 = "k_+(1 - \\frac{2μ_5}{k_+})"
    l_plus = slide_builder.add_trace(go.Scatter3d(x=[center1[0] + distance * direction_plus[0]],
                                                  y=[center1[1] + distance * direction_plus[1]],
                                                  z=[center1[2] + distance * direction_plus[2]],
                                                  mode="text", textfont=dict(size=32),
                                                  text=[latex_to_html(label1)],
                                                  textposition='middle left'))

    direction_minus = get_direction(regions_minus[3])
    label2 = "k_-"
    l_minus = slide_builder.add_trace(go.Scatter3d(x=[center2[0] + distance * direction_minus[0]],
                                                   y=[center2[1] + distance * direction_minus[1]],
                                                   z=[center2[2] + distance * direction_minus[2]],
                                                   mode="text", textfont=dict(size=32),
                                                   text=[latex_to_html(label2)],
                                                   textposition='middle left'))

    label_sum = label1 + " + " + label2 + " = k_+ + k_- - 2μ_5 = μ_1 + μ_2 + μ_5 + μ_3 + μ_4 + μ_5 - 2μ_5 = 1"
    l_sum = slide_builder.add_trace(go.Scatter3d(x=[0],
                                                 y=[0],
                                                 z=[radius * 2],
                                                 mode='text', textfont=dict(size=30),
                                                 text=[latex_to_html(label_sum)], textposition='middle center'))

    slide_builder.next_step()
    slide_builder.hide_traces(r1_traces)
    slide_builder.hide_traces(r2_traces)
    slide_builder.hide_traces(r1_vector_traces)
    slide_builder.hide_traces(r2_vector_traces)
    slide_builder.hide_traces(region6_traces)
    slide_builder.hide_traces([l_plus, l_minus, l_sum])

    regions18 = get_18_regions([povm.vectors[0], povm.vectors[1], x5],
                               [*colors_plus[1:], "rgb(0, 0, 0)"],
                               [povm.vectors[2], povm.vectors[3], -x5],
                               [*colors_minus[1:], "rgb(255, 255, 255)"], radius=sphere_scale * radius)

    def reorder(t: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(sorted(1 if x == 0 else 2 if x == 1 else 0 if x == 2 else x for x in t))

    regions18 = [Region(r.points, r.corners, r.simplices, r.color, [reorder(h) for h in r.h_idx]) for r in
                 regions18]

    new_center1 = np.array([0, -2 * radius, 0])
    new_center2 = np.array([0, 2 * radius, 0])
    r1_vector_traces = plot_response_vectors(slide_builder, regions_plus, new_center1,
                                             radius=radius, sphere_scale=sphere_scale)
    r2_vector_traces = plot_response_vectors(slide_builder, regions_minus, new_center2,
                                             radius=radius, sphere_scale=sphere_scale)
    r1_traces = plot_response_function(slide_builder, povm_plus, regions_plus, response_table_plus_scaled, new_center1,
                                       colors_plus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)
    r2_traces = plot_response_function(slide_builder, povm_minus, regions_minus, response_table_minus_scaled,
                                       new_center2,
                                       colors_minus, hide_vectors={0}, radius=radius, sphere_scale=sphere_scale)
    regions_plus_traces = plot_regions(regions_plus, new_center1)
    regions_minus_traces = plot_regions(regions_minus, new_center2)
    region6_traces = slide_builder.add_traces(regions_plus_traces + regions_minus_traces)

    center = np.zeros_like(center1)
    slide_builder.add_traces(plot_regions(regions18, center))
    r1_traces2 = plot_response_function(slide_builder, povm_plus, regions18, response_table_plus_scaled,
                                        center, colors_plus, hide_vectors={0}, radius=radius,
                                        sphere_scale=sphere_scale)
    r2_traces2 = plot_response_function(slide_builder, povm_minus, regions18, response_table_minus_scaled,
                                        center, colors_minus, hide_vectors={0}, radius=radius,
                                        sphere_scale=sphere_scale, h_idx=1)
    slide_builder.next_step()
    slide_builder.hide_traces(r1_traces)
    slide_builder.hide_traces(r2_traces)
    slide_builder.hide_traces(r1_vector_traces)
    slide_builder.hide_traces(r2_vector_traces)
    slide_builder.hide_traces(region6_traces)

    update_layout(slide_builder)
    update_meshes_lighting(slide_builder)

    return slide_builder


def get_circle_points(center: np.ndarray, normal: np.ndarray, radius: float = 1,
                      num_points: int = 100):
    if abs(normal[2]) < 0.9:
        u = np.array([normal[1], -normal[0], 0])
    else:
        u = np.array([0, normal[2], -normal[1]])
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)

    theta = np.linspace(0, 2 * np.pi, num_points)
    circle = radius * (np.outer(np.cos(theta), u) + np.outer(np.sin(theta), v)) + center
    return circle[:, 0], circle[:, 1], circle[:, 2]


def get_x5_mu5(povm: QubitPovm) -> Tuple[np.ndarray, float]:
    x5 = -(povm.mus[0] * povm.vectors[0] + povm.mus[1] * povm.vectors[1])
    mu5 = np.linalg.norm(x5)
    x5 = x5 / mu5
    return x5, mu5


def plot_vectors(slide_builder: SlideBuilder, vectors: List[np.ndarray], colors: List[str],
                 labels: Optional[List[str]] = None,
                 center: np.ndarray = np.zeros(3), radius: float = 1) -> List[int]:
    if not labels:
        labels = [""] * len(vectors)

    traces = []
    for x, color, label in zip(vectors, colors, labels):
        traces.append(slide_builder.add_trace(go.Scatter3d(x=[center[0], radius * x[0] + center[0]],
                                                           y=[center[1], radius * x[1] + center[1]],
                                                           z=[center[2], radius * x[2] + center[2]],
                                                           mode='lines',
                                                           line=dict(width=5, color=color))))
        if label:
            traces.append(slide_builder.add_trace(go.Scatter3d(x=[1.1 * radius * x[0] + center[0]],
                                                               y=[1.1 * radius * x[1] + center[1]],
                                                               z=[1.1 * radius * x[2] + center[2]],
                                                               mode='text', textfont=dict(size=30),
                                                               text=[label], textposition='middle center')))
    return traces


def get_hemisphere_indices(point: np.ndarray, vectors: List[np.ndarray]) -> Tuple[int, ...]:
    result = []
    inners = []
    for i, v in enumerate(vectors):
        inner = np.inner(point, v)
        if inner > 0:
            result.append(i)
            inners.append(inner)
    result = tuple(sorted(result))
    if result == (0, 1, 2):
        return random.choice([(0, 1), (1, 2), (0, 2)])
    if result == ():
        return (0,)
    return result


def get_region_color(hemisphere_idx: Tuple[int, ...], colors: List[str]) -> Tuple[int, int, int]:
    return mix_color_uniform([parse_rgb(colors[i]) for i in hemisphere_idx])


@dataclass
class Region:
    points: np.ndarray
    corners: List[np.ndarray]
    simplices: np.ndarray
    color: str
    h_idx: List[Tuple[int, ...]]


def plot_response_vectors(slide_builder: SlideBuilder, regions: List[Region],
                          center: np.ndarray, povm_len: float = 0.7, radius: float = 1,
                          sphere_scale: float = 1) -> List[int]:
    traces = []
    for r, center in zip(regions, ([center] * len(regions))):
        direction = get_direction(r)
        trace_id = slide_builder.add_trace(
            go.Scatter3d(x=[sphere_scale * radius * direction[0] + center[0],
                            (sphere_scale + povm_len) * radius * direction[0] + center[0]],
                         y=[sphere_scale * radius * direction[1] + center[1],
                            (sphere_scale + povm_len) * radius * direction[1] + center[1]],
                         z=[sphere_scale * radius * direction[2] + center[2],
                            (sphere_scale + povm_len) * radius * direction[2] + center[2]],
                         mode='lines',
                         line=dict(width=5, color='black')))
        traces.append(trace_id)

    return traces


def plot_response_function(slide_builder: SlideBuilder, povm: QubitPovm, regions: List[Region],
                           response_table: Dict[Tuple[int, Tuple], float],
                           center: np.ndarray, colors: List[str], povm_len: float = 0.7,
                           radius: float = 1, sphere_scale: float = 1, h_idx: int = 0,
                           hide_vectors: Set[int] = set()) -> List[int]:
    traces = []
    for r, center in zip(regions, ([center] * len(regions))):
        direction = get_direction(r)
        start = radius * sphere_scale
        for vector_index in range(povm.n_outcomes):
            response_key = (vector_index, r.h_idx[h_idx])
            if not response_key in response_table:
                continue

            end = start + povm_len * radius * response_table[response_key]
            if vector_index in hide_vectors:
                start = end
                continue
            line_color = colors[vector_index]
            trace_id = slide_builder.add_trace(create_cylinder(start * direction + center, end * direction + center,
                                                               radius=0.05, color=line_color))
            traces.append(trace_id)
            start = end

    return traces


def get_6regions(vectors: List[np.ndarray], colors: List[str], radius: float = 1,
                 n: int = 10000, alpha: Optional[float] = None) -> List[Region]:
    sphere_x, sphere_y, sphere_z = get_sphere_points(n, radius)
    points = np.stack((sphere_x, sphere_y, sphere_z), axis=-1)

    hemispheres = [(0,), (0, 1), (1,), (1, 2), (2,), (0, 2)]
    hemisphere_colors = [get_region_color(h, colors) for h in hemispheres]
    region_indices = [hemispheres.index(get_hemisphere_indices(p, vectors)) for p in points]

    normal = normalize(np.cross(vectors[0], vectors[1]))

    result = []
    for i, h in enumerate(hemispheres):
        mask = np.array(region_indices) == i
        filtered_points = points[mask]

        borders = get_border_normals(i, hemispheres, vectors)
        for (_, border_normal) in borders:
            theta = np.linspace(0, np.pi, 100)
            half_circle = radius * (np.outer(np.cos(theta), normal) + np.outer(np.sin(theta), border_normal))
            filtered_points = np.vstack([filtered_points, half_circle])

        surface_simplices = get_surface_simplices(filtered_points)
        result.append(Region(filtered_points, [radius * normal, -radius * normal], surface_simplices,
                             rgb_to_str(hemisphere_colors[i], alpha), [h]))
    return result


def plot_6regions(center: np.ndarray, vectors: List[np.ndarray], colors: List[str],
                  n: int = 10000, alpha: Optional[float] = None) -> List[BaseTraceType]:
    return plot_regions(get_6regions(vectors, colors, n=n, alpha=alpha), center)


def get_border_normals(hemisphere_idx: int, hemispheres: List[Tuple[int, ...]],
                       vectors: List[np.ndarray]) -> List[Tuple[np.ndarray, np.ndarray]]:
    prev_h = hemispheres[(hemisphere_idx - 1) % len(hemispheres)]
    next_h = hemispheres[(hemisphere_idx + 1) % len(hemispheres)]

    h = hemispheres[hemisphere_idx]
    first_border_v = next(iter(set(h).symmetric_difference(set(prev_h))))
    last_border_v = next(iter(set(next_h).symmetric_difference(set(h))))

    first_sign = -1 if first_border_v in prev_h else 1
    last_sign = -1 if last_border_v in h else 1

    normal = normalize(np.cross(vectors[0], vectors[1]))
    first_vector = first_sign * vectors[first_border_v]
    last_vector = last_sign * vectors[last_border_v]
    first_normal = normalize(np.cross(first_vector, normal))
    last_normal = normalize(np.cross(last_vector, normal))
    return [(first_vector, first_normal), (last_vector, last_normal)]


def get_arc_points(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    if np.linalg.norm(p1 - p2) < 1e-4:
        return np.vstack([p1, (p1 + p2) / 2, p2])

    angle = np.arccos(np.clip(np.dot(p1, p2), -1, 1))
    num_points = max(2, int(angle * 100 / np.pi))
    t_values = np.linspace(0, 1, num_points + 1)
    return (np.outer(np.sin((1 - t_values) * angle), p1) +
            np.outer(np.sin(t_values * angle), p2)) / np.sin(angle)


def get_18_regions(vectors1: List[np.ndarray], colors1: List[str],
                   vectors2: List[np.ndarray], colors2: List[str],
                   radius: float = 1,
                   n: int = 5000) -> List[Region]:
    sphere_x, sphere_y, sphere_z = get_sphere_points(n, radius)
    points = np.stack((sphere_x, sphere_y, sphere_z), axis=-1)

    hemispheres = [(0,), (0, 1), (1,), (1, 2), (2,), (0, 2)]
    hemisphere_colors1 = [get_region_color(h, colors1) for h in hemispheres]
    hemisphere_colors2 = [get_region_color(h, colors2) for h in hemispheres]
    region_indices1 = [hemispheres.index(get_hemisphere_indices(p, vectors1)) for p in points]
    region_indices2 = [hemispheres.index(get_hemisphere_indices(p, vectors2)) for p in points]

    normal1 = normalize(np.cross(vectors1[0], vectors1[1]))

    result = []
    for i, h in enumerate(hemispheres):
        mask = np.array(region_indices1) == i
        if 2 in h:
            hemispheres2 = [(1,), (0, 1), (0,)]
        else:
            hemispheres2 = [(1, 2), (2,), (0, 2)]

        borders1 = get_border_normals(i, hemispheres, vectors1)
        borders2 = get_border_normals(1, hemispheres2, vectors2)

        top_corner = normal1
        bottom_corner = -normal1
        top_middle_corner_left = -normalize(np.cross(borders1[0][0], borders2[0][0]))
        top_middle_corner_right = -normalize(np.cross(borders1[1][0], borders2[0][0]))
        bottom_middle_corner_left = -normalize(np.cross(borders1[0][0], borders2[1][0]))
        bottom_middle_corner_right = -normalize(np.cross(borders1[1][0], borders2[1][0]))

        h_idx = [hemispheres.index(hh) for hh in hemispheres2]
        for j in h_idx:
            mask2 = np.array(region_indices2) == j
            filtered_points = points[mask & mask2]
            if len(filtered_points) < 4:
                continue

            corners = None
            if j == 2 or j == 3:
                corners = [top_corner, top_middle_corner_left, top_middle_corner_right]
            elif j == 1 or j == 4:
                corners = [top_middle_corner_left, bottom_middle_corner_left,
                           bottom_middle_corner_right, top_middle_corner_right]
            elif j == 0 or j == 5:
                corners = [bottom_corner, bottom_middle_corner_right, bottom_middle_corner_left]

            if corners is not None:
                for c1, c2 in zip(corners, np.roll(corners, -1, axis=0)):
                    arc_points = radius * get_arc_points(c1, c2)
                    filtered_points = np.vstack([filtered_points, arc_points])

            surface_simplices = get_surface_simplices(filtered_points)
            region_color = mix_color_uniform([hemisphere_colors1[i], hemisphere_colors2[j]])
            region = Region(filtered_points, corners, surface_simplices, rgb_to_str(region_color), [h, hemispheres[j]])
            result.append(region)

    return result


def plot_regions(regions: List[Region], center: np.ndarray,
                 show_labels: bool = False, d: float = 1.12, x5_id: int = 2) -> List[BaseTraceType]:
    result = []
    for region in regions:
        name = " ".join([str(i) for i in region.h_idx])
        mesh = go.Mesh3d(x=region.points[:, 0] + center[0],
                         y=region.points[:, 1] + center[1],
                         z=region.points[:, 2] + center[2],
                         i=region.simplices[:, 0], j=region.simplices[:, 1], k=region.simplices[:, 2],
                         color=region.color, name=name)
        if show_labels:
            if len(region.corners) <= 2:
                mean = np.mean(region.points, axis=0)
            else:
                mean = np.mean(region.corners, axis=0)
            label_position = d * normalize(mean) + center
            if len(region.h_idx) == 1:
                region_id = ",".join([str(h + 1) if h != x5_id else "5^+" for h in region.h_idx[0]])
            else:
                h1_id = [str(h + 1) if h != x5_id else "5^+" for h in region.h_idx[0]]
                h2_id = [str(h + 3) if h != x5_id else "5^-" for h in region.h_idx[1]]
                region_id = ",".join([*h1_id, *h2_id])
            latex_label = "$" + region_id + "$"
            label = latex_to_html(latex_label)
            result.append(go.Scatter3d(x=[label_position[0]], y=[label_position[1]], z=[label_position[2]],
                                       mode='text', textfont=dict(size=30),
                                       text=[label], textposition='middle center'))
        result.append(mesh)

    return result


def get_surface_simplices(filtered_points: np.ndarray) -> np.ndarray:
    hull_center = np.mean(filtered_points, axis=0)
    hull_points = np.vstack([filtered_points, -hull_center])
    center_idx = len(hull_points) - 1
    simplices = get_oriented_simplices(ConvexHull(hull_points))
    return simplices[~np.any(simplices == center_idx, axis=1)]


def get_sphere_points(n: int = 50, radius: float = 1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    golden_ratio = (1 + np.sqrt(5)) / 2
    indices = np.arange(n)
    theta = 2 * np.pi * indices / golden_ratio
    z = 1 - 2 * indices / (n - 1)
    phi = np.acos(z)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    return radius * x, radius * y, radius * z


def get_oriented_simplices(hull: ConvexHull) -> np.ndarray:
    result = []
    for simplex in hull.simplices:
        simplex_points = hull.points[simplex]
        if len(simplex_points) > 3:
            print(simplex_points)
        v0, v1, v2 = simplex_points
        triangle_normal = np.cross(v1 - v0, v2 - v0)
        if np.dot(triangle_normal, v0) < 0:
            result.append([simplex[0], simplex[2], simplex[1]])
        else:
            result.append(simplex)

    return np.array(result)


def spherical_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray):
    v1 = normalize(make_orthogonal(p1, p2))
    v3 = normalize(make_orthogonal(p3, p2))
    return np.arccos(np.clip(np.dot(v1, v3), -1, 1))


def compute_solid_angle(corners: np.ndarray) -> float:
    n = len(corners)
    angles = []
    for i in range(n):
        prev_corner = corners[(i - 1) % n, :]
        curr_corner = corners[i, :]
        next_corner = corners[(i + 1) % n, :]
        angle = spherical_angle(prev_corner, curr_corner, next_corner)
        angles.append(angle)
    return (n - 2) * np.pi - sum(angles)


def get_direction(region: Region) -> np.ndarray:
    result = np.zeros(3)
    simplices = region.simplices
    areas = []
    for s in simplices:
        triangle_points = region.points[s]
        triangle_mean = normalize(np.mean(triangle_points, axis=0))
        triangle_area = compute_solid_angle(triangle_points)
        result = result + triangle_area * triangle_mean
        areas.append(triangle_area)
    return normalize(result)
