from typing import Tuple, List, Optional

import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
from dash.development.base_component import Component
from dash_extensions import Keyboard

from povms import get_povm, get_pvm
from presentations.parent_povms import plot_flat_povm, plot_pvm
from presentations.slides import SlideBuilder, create_text_slide

title = "Parent POVM Constructions"

app = dash.Dash(__name__)
app.title = title

pvm = get_pvm()
povm3 = get_povm(0.25, 0.32, 0.43,
                 np.array([1, 0, 0]), np.array([0, 1, 0]))

slides: List[SlideBuilder] = [create_text_slide(f"<p style=\"text-align:center;\"><h1>{title}</h1></p>"),
                              plot_pvm(pvm),
                              plot_flat_povm(povm3)]


def build_slide(step_idx: int) -> Tuple[Optional[go.Figure], str]:
    current_step_idx = step_idx
    for current_slide in slides:
        if current_slide.n_steps > current_step_idx:
            return current_slide.build(current_step_idx)
        current_step_idx -= current_slide.n_steps
    return slides[-1].build(slides[-1].n_steps - 1)


base_style = {"display": "flex", "flexDirection": "row",
              "height": "100vh", "width": "100%"}
app.layout = html.Div([
    dcc.Store(id="slide-index", data=0),
    Keyboard(id="keyboard", captureKeys=["ArrowRight", "ArrowLeft"]),
    html.Div(id='slide-content', children=[], style=base_style),
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
    Output("slide-content", "children"),
    Output("slide-content", "style"),
    Input("slide-index", "data")
)
def update_slide(slide: int) -> Tuple[List[Component], dict]:
    figure, text = build_slide(slide)

    result = []
    if figure:
        result.append(dcc.Graph(figure=figure, config={"scrollZoom": True}, style={
            "flex": "1", "height": "100vh"
        }))
    result.append(
        html.Div(children=(dcc.Markdown(text, mathjax=True, dangerously_allow_html=True)), style={
            "flex": "1", "padding": "1px", "fontSize": "30px",
            "overflow": "auto"
        }))
    if not figure:
        style = {**base_style, "alignItems": "center"}
    else:
        style = {**base_style, "alignItems": "flex-start"}
    return result, style


if __name__ == "__main__":
    app.run(debug=True)
