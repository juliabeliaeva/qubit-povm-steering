import math
from typing import Dict, Tuple

import numpy as np
from plotly import graph_objects as go

from plotly_utils import get_color
from povms import QubitPovm
from presentations.povms.povms_common import get_angles, plot_povm_vectors, plot_hemispheres, \
    get_response_table_pvm, plot_response_function, get_hemisphere_indices, update_layout, read_md, get_labels
from presentations.povms.slides import SlideBuilder

povm3_text = read_md("data/povm3.md")


def plot_flat_povm(povm: QubitPovm, radius=1.0, num_lines=102) -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(povm3_text['3out'])

    slide_builder.fig.add_shape(type="circle", xref="x", yref="y",
                                x0=-radius, y0=-radius, x1=radius, y1=radius,
                                line_color='black')

    angles = get_angles(povm)
    labels = get_labels(povm)
    # colors = [get_color("D3", i) for i in range(len(povm.vectors))]
    colors = [get_color("D3", 0),
              get_color("D3", 3),
              get_color("D3", 2)]
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

    sector_angles = get_sector_angles(angles)
    sector_traces = []
    for sector_angle in sector_angles:
        hemisphere_indices = get_hemisphere_indices(sector_angle, angles)
        label = r"$\Large" + ",".join([str(i + 1) for i in hemisphere_indices]) + "$"
        sector_trace = slide_builder.add_trace(go.Scatter(x=[0.8 * radius * math.cos(sector_angle)],
                                                          y=[0.8 * radius * math.sin(sector_angle)],
                                                          text=[label],
                                                          mode="text", textfont=dict(size=32), zorder=15,
                                                          showlegend=False))
        sector_traces.append(sector_trace)

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['coarse'])
    slide_builder.next_step()

    slide_builder.hide_traces(parent_traces)
    for sector_angle in sector_angles:
        x = radius * math.cos(sector_angle)
        y = radius * math.sin(sector_angle)
        hemisphere_indices = get_hemisphere_indices(sector_angle, angles)
        slide_builder.add_trace(go.Scatter(x=[x, 2 * x], y=[y, 2 * y],
                                           mode='lines', line=dict(color='black', width=2),
                                           name=",".join([str(i + 1) for i in hemisphere_indices])))

    slide_builder.add_line(povm3_text['coarseexplicit'])
    coarse_labels = []
    for sector_angle in sector_angles:
        x = radius * math.cos(sector_angle)
        y = radius * math.sin(sector_angle)
        hemisphere_indices = get_hemisphere_indices(sector_angle, angles)
        if len(hemisphere_indices) == 2:
            lambda_idx = next(iter(set(range(povm.n_outcomes)) - hemisphere_indices))
        else:
            lambda_idx = next(iter(hemisphere_indices))
        sign = "-" if len(hemisphere_indices) == 1 else ""
        lambda_label = rf"$\Large{sign}\hat{{\lambda}}_" + str(lambda_idx + 1) + "$"
        trace_lambda = slide_builder.add_trace(go.Scatter(x=[1.1 * 2 * x], y=[1.1 * 2 * y],
                                                          mode='text', textfont=dict(size=32),
                                                          textposition='middle center', text=[lambda_label]))
        if len(hemisphere_indices) == 1:
            theta_label = r"$\Large\theta_{" + str(lambda_idx + 1) + "}$"
            trace_theta = slide_builder.add_trace(go.Scatter(x=[0.4 * x], y=[0.4 * y],
                                                             mode='text', textfont=dict(size=32), zorder=20,
                                                             textposition='middle center', text=[theta_label]))
            coarse_labels.append(trace_theta)

        coarse_labels.append(trace_lambda)

    slide_builder.next_step()
    slide_builder.hide_traces(coarse_labels)
    slide_builder.hide_all_lines()
    slide_builder.add_line(povm3_text['responceunnorm'])

    traces_before2 = plot_response_function(slide_builder, povm, angles, colors, sector_angles,
                                            response_table_before, radius)
    slide_builder.next_step()
    slide_builder.add_line(povm3_text['responcenorm'])

    slide_builder.next_step()
    slide_builder.hide_traces(traces_before2)
    response_table_after = get_response_table(povm)
    traces_after2 = plot_response_function(slide_builder, povm, angles, colors, sector_angles,
                                           response_table_after, radius)

    slide_builder.next_step()
    slide_builder.add_line(povm3_text['simulates'])

    update_layout(slide_builder.fig)

    return slide_builder


def plot_flat_povm_proof() -> SlideBuilder:
    slide_builder = SlideBuilder(center=False)
    slide_builder.add_line(povm3_text['coarsesimple'])
    slide_builder.next_step()

    slide_builder.add_line(povm3_text['coarsesimplesim'])
    slide_builder.next_step()

    sub1 = slide_builder.add_line(povm3_text['coarsesimplesimsub1'])
    slide_builder.next_step()

    slide_builder.hide_line(sub1)
    sub2 = slide_builder.add_line(povm3_text['coarsesimplesimsub2'])
    slide_builder.next_step()

    # slide_builder.hide_line(sub2)
    sub3 = slide_builder.add_line(povm3_text['coarsesimplesimsub3'])
    slide_builder.next_step()

    slide_builder.hide_all_lines()
    slide_builder.add_line(povm3_text['coarsesimple2'])
    slide_builder.add_line(povm3_text['coarseneed1'])
    slide_builder.next_step()

    slide_builder.hide_all_lines()
    slide_builder.add_line(povm3_text['coarsesimple2'])
    slide_builder.add_line(povm3_text['coarseneed2'])
    slide_builder.next_step()

    sigma1 = slide_builder.add_line(povm3_text['coarseneedsigma1'])
    slide_builder.next_step()

    sigma2 = slide_builder.add_line(povm3_text['coarseneedsigma2'])
    slide_builder.next_step()

    sigma3 = slide_builder.add_line(povm3_text['coarseneedsigma3'])
    slide_builder.next_step()

    sigma4 = slide_builder.add_line(povm3_text['coarseneedsigma4'])
    slide_builder.next_step()

    slide_builder.hide_lines([sigma1, sigma2, sigma3, sigma4])
    i1 = slide_builder.add_line(povm3_text['coarseneedi1'])
    slide_builder.next_step()

    i2 = slide_builder.add_line(povm3_text['coarseneedi2'])
    slide_builder.next_step()

    i3 = slide_builder.add_line(povm3_text['coarseneedi3'])
    slide_builder.next_step()

    return slide_builder


def get_response_table(povm: QubitPovm) -> Dict[Tuple[int, Tuple], float]:
    result = get_response_table_pvm(povm)

    thetas = np.array([(math.acos(-np.inner(povm.vectors[1], povm.vectors[2]))),
                       math.acos(-np.inner(povm.vectors[0], povm.vectors[2])),
                       math.acos(-np.inner(povm.vectors[0], povm.vectors[1]))])

    x = ((thetas[0] * (1 - 2 * povm.mus[0]) - thetas[1] * (1 - 2 * povm.mus[1]) + thetas[2] * (1 - 2 * povm.mus[2])) /
         (2 * thetas[0]))
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
