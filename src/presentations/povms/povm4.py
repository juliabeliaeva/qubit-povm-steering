import random
from typing import Tuple, List, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
from scipy.spatial import ConvexHull

from latex_util import latex_to_html
from plotly_utils import get_color, parse_rgb, mix_color_uniform, rgb_to_str
from povms import QubitPovm, plot_sphere
from presentations.povms.povms_common import read_md
from presentations.povms.slides import SlideBuilder
from quantum_utils import normalize

povm4_text = read_md("data/povm4.md")

color_sequence = "D3"
vector_color_ids = [0, 2, 3, 8]
x5_color_ids = [7, 7]
x5_labels = [latex_to_html("x̂_{5^{+}}"), latex_to_html("x̂_{5^{-}}")]


def plot_povm4(povm: QubitPovm, radius=1.0) -> SlideBuilder:
    slide_builder = SlideBuilder("4-Outcome POVMs")
    slide_builder.add_line(povm4_text['4out'])

    slide_builder.add_trace(plot_sphere(radius=radius))

    labels = [latex_to_html(f"x̂_{str(i + 1)}") for i in range(povm.n_outcomes)]
    colors = [get_color(color_sequence, i) for i in vector_color_ids]
    plot_vectors(slide_builder, povm.vectors, colors, labels, radius=radius)

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['pseudo1'])

    x5, mu5 = get_x5_mu5(povm)
    x5_colors = [get_color(color_sequence, i) for i in x5_color_ids]
    plot_vectors(slide_builder, [x5, -x5], x5_colors, x5_labels)

    slide_builder.next_step()

    triangle1_points = np.vstack([povm.vectors[0], povm.vectors[1], x5, povm.vectors[0]])
    triangle2_points = np.vstack([povm.vectors[2], povm.vectors[3], -x5, povm.vectors[2]])
    for tp, color in zip([triangle1_points, triangle2_points], x5_colors):
        x = tp[:, 0]
        y = tp[:, 1]
        z = tp[:, 2]
        slide_builder.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color=color, width=1)))
        mesh = get_polygon_mesh(x, y, z, 'white', opacity=0.5)
        slide_builder.add_trace(mesh)

    slide_builder.add_line(povm4_text['povm3'])
    slide_builder.add_line(povm4_text['pseudo2'])

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['povm3weknow'])

    update_layout(slide_builder)

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
        i=ti, j=tj, k=tk, opacity=opacity, color=color, showscale=False,
        lightposition=dict(x=0, y=0, z=0),
        lighting=dict(ambient=0.5, diffuse=0.8, specular=0.2, roughness=0.9, fresnel=0.1)
    )


def update_layout(slide_builder: SlideBuilder):
    eye_distance = 1.2
    slide_builder.fig.update_layout(scene=dict(xaxis=dict(visible=False),
                                               yaxis=dict(visible=False),
                                               zaxis=dict(visible=False),
                                               aspectmode="data"),
                                    scene_camera=dict(eye=dict(x=eye_distance * 1, y=0,
                                                               z=eye_distance * 1)),
                                    font=dict(family="Palatino Linotype, Book Antiqua, Palatino, serif"),
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    plot_bgcolor='white', title=None, showlegend=False)


def plot_povm3_response() -> SlideBuilder:
    slide_builder = SlideBuilder("Response Functions for Coarse-Grained POVMs")
    slide_builder.add_line(povm4_text['responsepm'])
    return slide_builder


def plot_povm4_plus_minus_regions(povm: QubitPovm, radius=1) -> SlideBuilder:
    slide_builder = SlideBuilder("Merging $\\operatorname{POVM}_+$ and $\\operatorname{POVM}_-$")

    center1 = np.array([0, -1.3 * radius, 0])
    center2 = np.array([0, 1.3 * radius, 0])

    sphere_trace1 = slide_builder.add_trace(plot_sphere(center=center1, radius=radius))
    sphere_trace2 = slide_builder.add_trace(plot_sphere(center=center2, radius=radius))

    x5, mu5 = get_x5_mu5(povm)

    color_sequence = "D3"
    colors = [get_color(color_sequence, i) for i in vector_color_ids]

    vectors_plus = [povm.vectors[0], povm.vectors[1], x5]
    vectors_minus = [povm.vectors[2], povm.vectors[3], -x5]
    colors_plus = [*colors[:2], get_color(color_sequence, x5_color_ids[0])]
    colors_minus = [*colors[2:], get_color(color_sequence, x5_color_ids[1])]
    labels = [latex_to_html(f"x̂_{str(i + 1)}") for i in range(povm.n_outcomes)]
    labels_plus = [*labels[:2], x5_labels[0]]
    labels_minus = [*labels[2:], x5_labels[1]]

    vector_traces1 = plot_vectors(slide_builder, vectors_plus, colors_plus, labels_plus, center=center1,
                                  radius=radius)
    vector_traces2 = plot_vectors(slide_builder, vectors_minus, colors_minus, labels_minus, center=center2,
                                  radius=radius)

    slide_builder.next_step()
    slide_builder.hide_trace(sphere_trace1)
    slide_builder.hide_trace(sphere_trace2)

    region_colors_plus = [*colors_plus[:2], "rgb(255, 255, 255)"]
    region_color_minus = [*colors_minus[:2], "rgb(0, 0, 0)"]

    regions_plus = plot_6regions(center1, vectors_plus, region_colors_plus, alpha=0.5)
    regions_minus = plot_6regions(center2, vectors_minus, region_color_minus, alpha=0.5)
    traces_6regions = slide_builder.add_traces(regions_plus + regions_minus)

    circle_traces = []
    for c, v in zip([center1] * 3 + [center2] * 3, vectors_plus + vectors_minus):
        circle_x, circle_y, circle_z = get_circle_points(c, v, radius=1.0005, num_points=200)
        circle_traces.append(slide_builder.add_trace(go.Scatter3d(x=circle_x, y=circle_y, z=circle_z,
                                                                  mode='lines', line={"width": 3, "color": "black"})))

    slide_builder.next_step()
    slide_builder.hide_traces(vector_traces1 + vector_traces2)
    slide_builder.hide_traces(traces_6regions + circle_traces)

    regions_plus = plot_6regions(center1, vectors_plus, region_colors_plus)
    regions_minus = plot_6regions(center2, vectors_minus, region_color_minus)
    traces_6regions = slide_builder.add_traces(regions_plus + regions_minus)

    slide_builder.next_step()
    slide_builder.hide_traces(traces_6regions)

    regions_plus2 = plot_6regions(np.array([0, -2.3 * radius, 0]), vectors_plus,
                                  region_colors_plus)
    regions_minus2 = plot_6regions(np.array([0, 2.3 * radius, 0]), vectors_minus, region_color_minus)
    slide_builder.add_traces(regions_plus2 + regions_minus2)
    slide_builder.add_traces(plot_18regions(np.array([0, 0, 0]),
                                            vectors_plus, region_colors_plus,
                                            vectors_minus, region_color_minus))

    update_layout(slide_builder)

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


def plot_6regions(center: np.ndarray, vectors: List[np.ndarray], colors: List[str],
                  n: int = 10000, alpha: Optional[float] = None) -> List[BaseTraceType]:
    sphere_x, sphere_y, sphere_z = get_sphere_points(n)
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
            half_circle = (np.outer(np.cos(theta), normal) + np.outer(np.sin(theta), border_normal))
            filtered_points = np.vstack([filtered_points, half_circle])

        surface_simplices = get_surface_simplices(filtered_points)
        mesh = go.Mesh3d(x=filtered_points[:, 0] + center[0],
                         y=filtered_points[:, 1] + center[1],
                         z=filtered_points[:, 2] + center[2],
                         i=surface_simplices[:, 0], j=surface_simplices[:, 1], k=surface_simplices[:, 2],
                         color=rgb_to_str(hemisphere_colors[i], alpha), name=str(h))
        result.append(mesh)
    return result


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


def plot_18regions(center: np.ndarray, vectors1: List[np.ndarray], colors1: List[str],
                   vectors2: List[np.ndarray], colors2: List[str],
                   n: int = 5000) -> List[BaseTraceType]:
    sphere_x, sphere_y, sphere_z = get_sphere_points(n)
    points = np.stack((sphere_x, sphere_y, sphere_z), axis=-1)

    hemispheres = [(0,), (0, 1), (1,), (1, 2), (2,), (0, 2)]
    hemisphere_colors1 = [get_region_color(h, colors1) for h in hemispheres]
    hemisphere_colors2 = [get_region_color(h, colors2) for h in hemispheres]
    region_indices1 = [hemispheres.index(get_hemisphere_indices(p, vectors1)) for p in points]
    region_indices2 = [hemispheres.index(get_hemisphere_indices(p, vectors2)) for p in points]

    normal = normalize(np.cross(vectors1[0], vectors1[1]))

    result = []
    for i, h in enumerate(hemispheres):
        mask = np.array(region_indices1) == i
        if 2 in h:
            hemispheres2 = [(1,), (0, 1), (0,)]
        else:
            hemispheres2 = [(1, 2), (2,), (0, 2)]

        h_idx = [hemispheres.index(hh) for hh in hemispheres2]
        for j in h_idx:
            mask2 = np.array(region_indices2) == j
            filtered_points = points[mask & mask2]
            if len(filtered_points) < 4:
                continue

            surface_simplices = get_surface_simplices(filtered_points)
            region_color = mix_color_uniform([hemisphere_colors1[i], hemisphere_colors2[j]])
            mesh = go.Mesh3d(x=filtered_points[:, 0] + center[0],
                             y=filtered_points[:, 1] + center[1],
                             z=filtered_points[:, 2] + center[2],
                             i=surface_simplices[:, 0], j=surface_simplices[:, 1], k=surface_simplices[:, 2],
                             color=rgb_to_str(region_color), name=f"{h} {hemispheres[j]}")
            result.append(mesh)

    return result


def get_surface_simplices(filtered_points: np.ndarray) -> np.ndarray:
    hull_center = np.mean(filtered_points, axis=0)
    hull_points = np.vstack([filtered_points, -hull_center])
    center_idx = len(hull_points) - 1
    simplices = get_oriented_simplices(ConvexHull(hull_points))
    return simplices[~np.any(simplices == center_idx, axis=1)]


def get_sphere_points(n: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    golden_ratio = (1 + np.sqrt(5)) / 2
    indices = np.arange(n)
    theta = 2 * np.pi * indices / golden_ratio
    z = 1 - 2 * indices / (n - 1)
    phi = np.acos(z)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    return x, y, z


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
