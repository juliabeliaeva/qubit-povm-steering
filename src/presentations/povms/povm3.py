import math
from typing import Dict, Tuple

import numpy as np
from plotly import graph_objects as go

from plotly_utils import get_color
from povms import QubitPovm
from presentations.povms.parent_povms import get_angles, get_labels, plot_povm_vectors, plot_hemispheres, \
    get_response_table_pvm, plot_response_function, get_hemisphere_indices, update_layout, read_md
from presentations.povms.slides import SlideBuilder


def plot_flat_povm(povm: QubitPovm, radius=1.0, num_lines=102) -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(povm3_text['3out'])

    slide_builder.fig.add_shape(type="circle", xref="x", yref="y",
                                x0=-radius, y0=-radius, x1=radius, y1=radius,
                                line_color='black')

    angles = get_angles(povm)
    labels = get_labels(povm)
    colors = [get_color("D3", i) for i in range(len(povm.vectors))]
    vectors = list(zip(angles, labels, colors))

    vector_traces, label_traces = plot_povm_vectors(slide_builder, vectors, radius)
    slide_builder.add_line(povm3_text['3outnoisy'])

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['parent'])

    line_angles = [2 * np.pi * i / num_lines for i in range(num_lines)]
    parent_traces = []
    for line_angle in line_angles:
        trace = slide_builder.add_trace(go.Scatter(x=[radius * math.cos(line_angle), 2 * radius * math.cos(line_angle)],
                                                   y=[radius * math.sin(line_angle), 2 * radius * math.sin(line_angle)],
                                                   mode='lines', line=dict(color='black', width=2),
                                                   showlegend=False, hoverinfo='skip'))
        parent_traces.append(trace)

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['simpleresponce'])
    slide_builder.next_step()
    slide_builder.add_line(povm3_text['simpleintegral'])
    slide_builder.next_step()
    slide_builder.add_line(povm3_text['simplenormalization'])

    slide_builder.next_step()
    slide_builder.hide_traces(label_traces)
    plot_hemispheres(slide_builder, vectors, radius)

    slide_builder.next_step()

    response_table_before = get_response_table_pvm(povm)
    traces_before = plot_response_function(slide_builder, povm, angles, colors, line_angles,
                                           response_table_before, radius)

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['letsfix'])

    slide_builder.next_step()
    slide_builder.hide_all_lines()
    slide_builder.hide_traces(traces_before)
    # slide_builder.hide_traces(vector_traces)

    sector_angles = get_sector_angles(angles)
    sector_traces = []
    for sector_angle in sector_angles:
        hemisphere_indices = get_hemisphere_indices(sector_angle, angles)
        sector_trace = slide_builder.add_trace(go.Scatter(x=[0.8 * radius * math.cos(sector_angle)],
                                                          y=[0.8 * radius * math.sin(sector_angle)],
                                                          text=[",".join([str(i + 1) for i in hemisphere_indices])],
                                                          mode="text", textfont=dict(size=32), zorder=15,
                                                          showlegend=False))
        sector_traces.append(sector_trace)

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['coarse'])
    # slide_builder.hide_traces(sector_traces)
    slide_builder.hide_traces(parent_traces)
    # slide_builder.show_traces(vector_traces)

    for sector_angle in sector_angles:
        x = radius * math.cos(sector_angle)
        y = radius * math.sin(sector_angle)
        hemisphere_indices = get_hemisphere_indices(sector_angle, angles)
        slide_builder.add_trace(go.Scatter(x=[x, 2 * x], y=[y, 2 * y],
                                           mode='lines', line=dict(color='black', width=2),
                                           name=",".join([str(i + 1) for i in hemisphere_indices])))

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['coarseexplicit'])
    slide_builder.next_step()
    slide_builder.add_line(povm3_text['responceunnorm'])

    traces_before2 = plot_response_function(slide_builder, povm, angles, colors, sector_angles,
                                            response_table_before, radius)
    slide_builder.next_step()
    slide_builder.hide_all_lines()
    slide_builder.add_line(povm3_text['responceunnorm'])
    slide_builder.add_line(povm3_text['responcenorm'])

    slide_builder.next_step()
    slide_builder.hide_traces(traces_before2)
    traces_after2 = []
    for alpha in np.linspace(0.0, 1.0, 10):
        slide_builder.hide_traces(traces_after2)
        response_table_after = get_response_table(povm, alpha=alpha)
        traces_after2 = plot_response_function(slide_builder, povm, angles, colors, sector_angles,
                                               response_table_after, radius)
        slide_builder.next_step()

    update_layout(slide_builder.fig)

    return slide_builder


povm3_text = read_md("data/povm3.md")


def get_response_table(povm: QubitPovm, alpha: float) -> Dict[Tuple[int, Tuple], float]:
    result = get_response_table_pvm(povm)

    x = 0.05 * alpha + (1 - 2 * povm.mus[0] - 0.05) * (1 - alpha)
    y = 1 - 2 * povm.mus[0] - x
    result[(1, (0,))] = y
    result[(2, (0,))] = x
    result[(1, (1,))] = 1
    result[(2, (2,))] = 1
    result[(1, (1, 2))] = result[(1, (1, 2))] - x
    result[(2, (1, 2))] = result[(2, (1, 2))] - y
    result[(1, (0, 1))] = 1 - result[(0, (0, 1))]
    result[(2, (0, 2))] = 1 - result[(0, (0, 2))]

    return result


def get_sector_angles(angles):
    segment_borders = np.append((np.asarray(angles) + math.pi / 2), (np.asarray(angles) - math.pi / 2))
    segment_borders = sorted(np.mod(segment_borders, 2 * np.pi))
    segment_angles = []
    for angle1, angle2 in zip(segment_borders, np.roll(segment_borders, -1)):
        if angle1 > angle2:
            angle1 = angle1 - 2 * math.pi
        angle = (angle1 + angle2) / 2
        segment_angles.append(angle)
    return segment_angles
