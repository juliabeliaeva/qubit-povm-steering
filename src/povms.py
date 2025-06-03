import math
from dataclasses import dataclass
from random import uniform
from typing import List, Tuple

import numpy as np
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
from scipy.spatial.transform import Rotation

from crossections import make_orthogonal
from quantum_utils import normalize


@dataclass(frozen=True)
class QubitPovm:
    vectors: List[np.ndarray]
    mus: List[float]
    r: float

    @property
    def n_outcomes(self) -> int:
        return len(self.vectors)


def get_random_vector():
    return normalize(np.random.normal(1, size=3))


def get_random_triangle():
    a = uniform(0, 0.5)
    b = uniform(max(a, 0.5 - a), 0.5)
    c = 1 - a - b
    return a, b, c


def get_random_plane() -> Tuple[np.ndarray, np.ndarray]:
    x = get_random_vector()
    y = normalize(make_orthogonal(get_random_vector(), x))
    return x, y


def get_angle_from_sides(a: float, b: float, c: float) -> float:
    cos_alpha = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    assert 1 >= cos_alpha >= -1
    return math.acos(cos_alpha)


def get_random_povm() -> QubitPovm:
    mu1, mu2, mu3 = get_random_triangle()
    x, y = get_random_plane()

    return get_povm3(mu1, mu2, mu3, x, y)


def get_povm3(mu1: float, mu2: float, mu3: float, plane_x: np.ndarray, plane_y: np.ndarray) -> QubitPovm:
    alpha3 = get_angle_from_sides(mu1, mu2, mu3)
    x1 = plane_x
    x2 = -math.cos(alpha3) * plane_x - math.sin(alpha3) * plane_y
    x3 = (-mu1 * x1 - mu2 * x2) / mu3
    return QubitPovm([x1, x2, x3], [mu1, mu2, mu3], 1)


def get_pvm() -> QubitPovm:
    x = Rotation.from_euler(seq='xyz', angles=[0, np.pi / 3, 0]).as_matrix() @ np.array([1, 0, 0])
    return QubitPovm([x, -x], [0.5, 0.5], 1)


def get_uniform_povm3() -> QubitPovm:
    mus = [1 / 3, 1 / 3, 1 / 3]
    x1 = np.array([1, 0, 0])
    x2 = Rotation.from_euler(seq='xyz', angles=[0, 0, 2 * np.pi / 3]).as_matrix() @ x1
    x3 = Rotation.from_euler(seq='xyz', angles=[0, 0, - 2 * np.pi / 3]).as_matrix() @ x1
    return QubitPovm([x1, x2, x3], mus, 1)


def get_uniform_povm4() -> QubitPovm:
    mus = [1 / 4, 1 / 4, 1 / 4, 1 / 4]
    x1 = np.array([1, 1, 1]) / math.sqrt(3)
    x2 = np.array([1, -1, -1]) / math.sqrt(3)
    x3 = np.array([-1, 1, -1]) / math.sqrt(3)
    x4 = np.array([-1, -1, 1]) / math.sqrt(3)
    return QubitPovm([x1, x2, x3, x4], mus, 1)


def add_noise(povm: QubitPovm, r: float) -> QubitPovm:
    return QubitPovm(povm.vectors, povm.mus, povm.r * r)


def plot_sphere(radius: float = 1) -> BaseTraceType:
    u, v = np.mgrid[0:2 * np.pi:60j, 0:np.pi:30j]
    xs = radius * np.cos(u) * np.sin(v)
    ys = radius * np.sin(u) * np.sin(v)
    zs = radius * np.cos(v)
    return go.Surface(x=xs, y=ys, z=zs, opacity=0.03, showscale=False)


def plot_povm(povm: QubitPovm) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(plot_sphere())

    color_sequence_name = "D3"
    for i, (vec, mu) in enumerate(zip(povm.vectors, povm.mus)):
        scaled = povm.r * vec
        color = getattr(pc.qualitative, color_sequence_name)[i]
        fig.add_trace(go.Scatter3d(x=[0, scaled[0]],
                                   y=[0, scaled[1]],
                                   z=[0, scaled[2]],
                                   mode='lines',
                                   line=dict(width=5, color=color)))

    fig.update_layout(scene=dict(xaxis=dict(visible=False),
                                 yaxis=dict(visible=False),
                                 zaxis=dict(visible=False),
                                 aspectmode='data'),
                      title=None,
                      showlegend=False)
    return fig
