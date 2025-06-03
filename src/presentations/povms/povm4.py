import plotly.graph_objects as go

from plotly_utils import get_color
from povms import QubitPovm, plot_sphere
from presentations.povms.povms_common import read_md, get_labels
from presentations.povms.slides import SlideBuilder

povm4_text = read_md("data/povm4.md")


def plot_povm4(povm: QubitPovm, radius=1.0) -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(povm4_text['4out'])
    slide_builder.add_line(povm4_text['4outnoisy'])

    slide_builder.add_trace(plot_sphere(radius))

    labels = get_labels(povm)
    for i, (vec, mu, label) in enumerate(zip(povm.vectors, povm.mus, labels)):
        color = get_color("D3", i)
        slide_builder.add_trace(go.Scatter3d(x=[0, radius * vec[0]],
                                             y=[0, radius * vec[1]],
                                             z=[0, radius * vec[2]],
                                             mode='lines',
                                             line=dict(width=5, color=color)))
        slide_builder.add_trace(go.Scatter3d(x=[1.1 * radius * vec[0]],
                                             y=[1.1 * radius * vec[1]],
                                             z=[1.1 * radius * vec[2]],
                                             mode='text',
                                             text=[label], textposition='middle center'))

    slide_builder.fig.update_layout(scene=dict(xaxis=dict(visible=False),
                                               yaxis=dict(visible=False),
                                               zaxis=dict(visible=False),
                                               aspectmode="manual", aspectratio=dict(x=1, y=1, z=1)),
                                    scene_camera=dict(eye=dict(x=0.8, y=0.9, z=2)),
                                    font=dict(family="Palatino Linotype, Book Antiqua, Palatino, serif"),
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    plot_bgcolor='white', title=None, showlegend=False)

    return slide_builder
