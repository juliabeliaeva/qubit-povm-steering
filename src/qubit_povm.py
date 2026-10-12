import math
from dataclasses import dataclass
from typing import List

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class QubitPovm:
    vectors: List[np.ndarray]
    mus: List[float]
    r: float

    @property
    def n_outcomes(self) -> int:
        return len(self.vectors)


def get_angle_from_sides(a: float, b: float, c: float) -> float:
    cos_alpha = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    assert 1 >= cos_alpha >= -1
    return math.acos(cos_alpha)


def get_pvm() -> QubitPovm:
    x = Rotation.from_euler(seq='xyz', angles=[0, np.pi / 3, 0]).as_matrix() @ np.array([1, 0, 0])
    return QubitPovm([x, -x], [0.5, 0.5], 1)


def get_povm3(mu1: float, mu2: float, mu3: float, plane_x: np.ndarray, plane_y: np.ndarray) -> QubitPovm:
    alpha3 = get_angle_from_sides(mu1, mu2, mu3)
    x1 = plane_x
    x2 = -math.cos(alpha3) * plane_x - math.sin(alpha3) * plane_y
    x3 = (-mu1 * x1 - mu2 * x2) / mu3
    return QubitPovm([x1, x2, x3], [mu1, mu2, mu3], 1)


def get_sample_povm4() -> QubitPovm:
    mus = np.array([0.25, 0.4, 0.35, 0.4, 0.20])
    povm31 = get_povm3(mus[0], mus[1], mus[2],
                       np.array([1, 0, 0]), np.array([0, 1, 0]))
    povm32 = get_povm3(mus[1], mus[3], mus[4],
                       -povm31.vectors[1], np.array([0, 0, 1]))

    mu_sum = mus[0] + mus[2] + mus[3] + mus[4]
    return QubitPovm([povm31.vectors[0], povm31.vectors[2], povm32.vectors[1], povm32.vectors[2]],
                     [mus[0] / mu_sum, mus[2] / mu_sum, mus[3] / mu_sum, mus[4] / mu_sum], r=1)
