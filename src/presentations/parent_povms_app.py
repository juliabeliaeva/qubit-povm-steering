from typing import Tuple, List

import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
from dash_extensions import Keyboard

from povms import get_povm, get_pvm
from presentations.parent_povms import plot_flat_povm, plot_pvm
from presentations.slides import SlideBuilder

app = dash.Dash(__name__)
app.title = "Parent POVM Constructions"

pvm = get_pvm()
povm3 = get_povm(0.25, 0.32, 0.43,
                 np.array([1, 0, 0]), np.array([0, 1, 0]))

slides: List[SlideBuilder] = [plot_pvm(pvm), plot_flat_povm(povm3)]


def build_slide(step_idx: int) -> Tuple[go.Figure, str]:
    current_step_idx = step_idx
    for current_slide in slides:
        if current_slide.n_steps > current_step_idx:
            return current_slide.build(current_step_idx)
        current_step_idx -= current_slide.n_steps
    return slides[-1].build(slides[-1].n_steps - 1)


app.layout = html.Div([
    dcc.Store(id="slide-index", data=0),
    Keyboard(id="keyboard", captureKeys=["ArrowRight", "ArrowLeft"]),
    html.Div(id='slide-content', children=[
        dcc.Graph(id="3d-plot", config={"scrollZoom": True}, style={
            "flex": "1", "height": "100vh"
        }),
        html.Div(id="formula", style={
            "flex": "1", "padding": "1px", "fontSize": "30px",
            "overflow": "auto"
        }),
    ], style={"display": "flex", "flexDirection": "row", "height": "100vh", "width": "100%"}),
])


@app.callback(
    Output("slide-index", "data"),
    Input("keyboard", "keydown"),
    Input("keyboard", "n_keydowns"),
    Input("slide-index", "data")
)
def on_key(e: dict, n_keydowns: int, current_slide: int) -> int:
    if not e or "key" not in e:
        return current_slide
    if e["key"] == "ArrowRight":
        return current_slide + 1
    elif e["key"] == "ArrowLeft":
        return max(current_slide - 1, 0)
    return current_slide


@app.callback(
    Output("3d-plot", "figure"),
    Output("formula", "children"),
    Input("slide-index", "data")
)
def update_slide(slide: int) -> Tuple[go.Figure, dcc.Markdown]:
    fig, text = build_slide(slide)
    markdown = dcc.Markdown(text, mathjax=True)
    return fig, markdown


if __name__ == "__main__":
    app.run(debug=True)
