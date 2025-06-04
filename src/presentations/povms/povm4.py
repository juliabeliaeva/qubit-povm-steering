from typing import Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType

from crossections import make_orthogonal
from latex_util import latex_to_html
from plotly_utils import get_color
from povms import QubitPovm, plot_sphere
from presentations.povms.povms_common import read_md, get_labels
from presentations.povms.slides import SlideBuilder
from quantum_utils import normalize

povm4_text = read_md("data/povm4.md")


def plot_povm4(povm: QubitPovm, radius=1.0) -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(povm4_text['4out'])
    slide_builder.add_line(povm4_text['4outnoisy'])

    slide_builder.add_trace(plot_sphere(radius))

    labels = get_labels(povm)
    color_sequence = "D3"
    colors = [get_color(color_sequence, 0), get_color(color_sequence, 2), get_color(color_sequence, 1),
              get_color(color_sequence, 3)]
    for vec, mu, label, color in zip(povm.vectors, povm.mus, labels, colors):
        slide_builder.add_trace(go.Scatter3d(x=[0, radius * vec[0]],
                                             y=[0, radius * vec[1]],
                                             z=[0, radius * vec[2]],
                                             mode='lines',
                                             line=dict(width=5, color=color)))
        slide_builder.add_trace(go.Scatter3d(x=[1.1 * radius * vec[0]],
                                             y=[1.1 * radius * vec[1]],
                                             z=[1.1 * radius * vec[2]],
                                             mode='text', textfont=dict(size=30),
                                             text=[label], textposition='middle center'))

    slide_builder.next_step()

    slide_builder.add_line(povm4_text['pseudo1'])

    x5 = -(povm.mus[0] * povm.vectors[0] + povm.mus[1] * povm.vectors[1])
    mu5 = np.linalg.norm(x5)
    x5 = x5 / mu5

    x5_colors = [get_color(color_sequence, 9), get_color(color_sequence, 8)]
    x5_labels = [latex_to_html("x̂_{5^{+}}"), latex_to_html("x̂_{5^{-}}")]
    for x, color, label in zip([x5, -x5], x5_colors, x5_labels):
        slide_builder.add_trace(go.Scatter3d(x=[0, radius * x[0]],
                                             y=[0, radius * x[1]],
                                             z=[0, radius * x[2]],
                                             mode='lines',
                                             line=dict(width=5, color=color)))
        slide_builder.add_trace(go.Scatter3d(x=[1.1 * radius * x[0]],
                                             y=[1.1 * radius * x[1]],
                                             z=[1.1 * radius * x[2]],
                                             mode='text', textfont=dict(size=30),
                                             text=[label], textposition='middle center'))
    slide_builder.next_step()

    # circles = [get_circle(povm.vectors[0], povm.vectors[1]), get_circle(povm.vectors[2], povm.vectors[3])]
    triangle1_points = np.vstack([povm.vectors[0], povm.vectors[1], x5, povm.vectors[0]])
    triangle2_points = np.vstack([povm.vectors[2], povm.vectors[3], -x5, povm.vectors[2]])
    for tp, color in zip([triangle1_points, triangle2_points], x5_colors):
        x = tp[:, 0]
        y = tp[:, 1]
        z = tp[:, 2]
        slide_builder.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color=color, width=1)))
        mesh = get_polygon_mesh(x, y, z, 'white', opacity=0.5)
        slide_builder.add_trace(mesh)

    slide_builder.add_line(povm4_text['pseudo2'])
    slide_builder.add_line(povm4_text['povm3'])

    slide_builder.next_step()
    slide_builder.add_line(povm4_text['povm3weknow'])

    eye_distance = 1.2
    slide_builder.fig.update_layout(scene=dict(xaxis=dict(visible=False),
                                               yaxis=dict(visible=False),
                                               zaxis=dict(visible=False),
                                               aspectmode="manual", aspectratio=dict(x=1, y=1, z=1)),
                                    scene_camera=dict(eye=dict(x=eye_distance * 1, y=eye_distance * (-0.2),
                                                               z=eye_distance * 1)),
                                    font=dict(family="Palatino Linotype, Book Antiqua, Palatino, serif"),
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    plot_bgcolor='white', title=None, showlegend=False)

    return slide_builder


def plot_povm3_response() -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(povm4_text['responsepm'])
    return slide_builder


def get_circle(x1: np.ndarray, x2: np.ndarray, n: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    u = x1
    v = normalize(make_orthogonal(x2, x1))
    angles = np.linspace(0, 2 * np.pi, n)
    circle = np.outer(np.cos(angles), u) + np.outer(np.sin(angles), v)
    return circle[:, 0], circle[:, 1], circle[:, 2]


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
