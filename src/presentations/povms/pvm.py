import math
from typing import Dict

import numpy as np
from plotly import graph_objects as go

from plotly_utils import get_color
from povms import QubitPovm
from presentations.povms.povms_common import get_angles, get_labels, plot_povm_vectors, plot_hemispheres, \
    get_response_table_pvm, plot_response_function, update_layout, read_md
from presentations.povms.slides import SlideBuilder

pvm_text: Dict[str, str] = read_md("data/povms/pvm.md")

def plot_pvm(povm: QubitPovm, radius=1.0, num_lines=102) -> SlideBuilder:
    slide_builder = SlideBuilder("Projectors")

    pvm_line = slide_builder.add_line(pvm_text['pvm'])

    slide_builder.fig.add_shape(type="circle", xref="x", yref="y",
                                x0=-radius, y0=-radius, x1=radius, y1=radius,
                                line_color='black')

    angles = get_angles(povm)
    labels = get_labels(povm)
    colors = [get_color("D3", i) for i in range(len(povm.vectors))]
    vectors = list(zip(angles, labels, colors))

    plot_povm_vectors(slide_builder, vectors, radius)
    slide_builder.next_step()

    slide_builder.hide_line(pvm_line)
    slide_builder.add_line(pvm_text['noisypvm2'])
    slide_builder.next_step()

    slide_builder.add_line(pvm_text['parentpvm'])

    line_angles = [2 * np.pi * i / num_lines for i in range(num_lines)]
    parent_traces = []
    for line_angle in line_angles:
        trace = slide_builder.add_trace(
            go.Scatter(x=[radius * math.cos(line_angle), 2 * radius * math.cos(line_angle)],
                       y=[radius * math.sin(line_angle), 2 * radius * math.sin(line_angle)],
                       mode='lines', line=dict(color='black', width=2),
                       showlegend=False, hoverinfo='skip'))
        parent_traces.append(trace)

    slide_builder.next_step()
    plot_hemispheres(slide_builder, vectors, radius)

    slide_builder.next_step()

    response_table_before = get_response_table_pvm(povm)
    plot_response_function(slide_builder, povm, angles, colors, line_angles,
                           response_table_before, radius)

    slide_builder.next_step()
    slide_builder.add_line(pvm_text['response'])

    slide_builder.next_step()
    slide_builder.add_line(pvm_text['integral'])

    update_layout(slide_builder.fig)
    return slide_builder
