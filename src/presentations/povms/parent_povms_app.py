from typing import Tuple, List

import dash
import numpy as np
from dash import dcc, html, Input, Output
from dash.development.base_component import Component
from dash_extensions import Keyboard

from povms import get_povm3, get_pvm, get_uniform_povm4
from presentations.povms.povm3 import plot_flat_povm, plot_flat_povm_proof
from presentations.povms.povm4 import plot_povm4, plot_povm3_response
from presentations.povms.pvm import plot_pvm
from presentations.povms.slides import SlideBuilder, create_title_slide

title = "Parent POVM Constructions"

app = dash.Dash(__name__)
app.title = title

pvm = get_pvm()
povm3 = get_povm3(0.25, 0.32, 0.43,
                  np.array([1, 0, 0]), np.array([0, 1, 0]))
povm4 = get_uniform_povm4()

slides: List[SlideBuilder] = [create_title_slide(title),
                              create_title_slide("Parent POVM for projectors", level=2),
                              plot_pvm(pvm),
                              create_title_slide("Parent POVM for 3-outcome measurements", level=2),
                              plot_flat_povm(povm3),
                              plot_flat_povm_proof(),
                              create_title_slide("Parent POVM for 4-outcome measurements", level=2),
                              plot_povm4(povm4),
                              plot_povm3_response()]
max_slides = sum([s.n_steps for s in slides])


def build_slide(step_idx: int) -> Tuple[List[Component], dict]:
    current_step_idx = step_idx
    for current_slide in slides:
        if current_slide.n_steps > current_step_idx:
            return current_slide.build_components(current_step_idx)
        current_step_idx -= current_slide.n_steps
    return slides[-1].build_components(slides[-1].n_steps - 1)


base_style = {"display": "flex", "flexDirection": "row",
              "height": "100vh", "width": "100%"}
app.layout = html.Div([
    html.Link(href="https://fonts.googleapis.com/css2?family=Lato&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css2?family=STIX+Two+Math&display=swap", rel="stylesheet"),
    dcc.Store(id="slide-index", data=0),
    Keyboard(id="keyboard", captureKeys=["ArrowRight", "ArrowLeft", " "]),
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
    if e["key"] == "ArrowRight" or e["key"] == " ":
        return min(current_slide + 1, max_slides)
    elif e["key"] == "ArrowLeft":
        return max(current_slide - 1, 0)
    return current_slide


@app.callback(
    Output("slide-content", "children"),
    Output("slide-content", "style"),
    Input("slide-index", "data")
)
def update_slide(slide: int) -> Tuple[List[Component], dict]:
    components, style = build_slide(slide)
    return components, {**base_style, **style}


if __name__ == "__main__":
    app.run(debug=True)
