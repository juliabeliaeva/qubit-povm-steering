from typing import List

import dash
import numpy as np
from dash import dcc, html, Input, Output
from dash.development.base_component import Component
from dash_extensions import Keyboard
from povm3 import plot_flat_povm, plot_flat_povm_proof
from povm4 import plot_povm4_plus_minus_regions, plot_povm4, plot_povm4_normalization, \
    plot_povm3_response, plot_povm4_response_diagram, plot_povm4_response
from pvm import plot_pvm
from qubit_povm import get_povm3, get_pvm, get_sample_povm4
from slides import AbstractSlideBuilder, TitleSlideBuilder

title = "Joint Measurability of Noisy Qubit POVMs"

app = dash.Dash(__name__)
app.title = title

pvm = get_pvm()
povm3 = get_povm3(0.25, 0.32, 0.43,
                  np.array([1, 0, 0]), np.array([0, 1, 0]))
povm4 = get_sample_povm4()

main_slides: List[AbstractSlideBuilder] = [TitleSlideBuilder(title, 1,
                                                             subtitle="Based on\n"
                                                                      "\"Exact Steering Bound for Two-Qubit Werner States\"\n"
                                                                      "by Yujie Zhang and Eric Chitambar\n\n"
                                                                      "Visualizations by Julia Beliaeva\n\n\n(Navigate using Left/Right Keys)"),
                                           TitleSlideBuilder("Projectors", level=2),
                                           plot_pvm(pvm),
                                           TitleSlideBuilder("3-Outcome Measurements", level=2),
                                           plot_flat_povm(povm3),
                                           TitleSlideBuilder("4-Outcome Measurements", level=2),
                                           plot_povm4(povm4),
                                           plot_povm4_plus_minus_regions(povm4),
                                           plot_povm4_normalization(povm4),
                                           TitleSlideBuilder("The End\nThank You for Listening!", level=2)]
extra_slides: List[AbstractSlideBuilder] = [TitleSlideBuilder("Extra Slides", level=2),
                                            plot_flat_povm_proof(),
                                            plot_povm3_response(),
                                            plot_povm4_response_diagram(),
                                            plot_povm4_response(povm4)]
slides = main_slides + extra_slides
max_slides = sum([s.n_steps for s in main_slides])


def build_slide(step_idx: int) -> List[Component]:
    current_step_idx = step_idx
    for slide_idx, current_slide in enumerate(slides):
        if current_slide.n_steps > current_step_idx:
            return current_slide.build_components(slide_idx, current_step_idx)
        current_step_idx -= current_slide.n_steps

    last_slide = len(slides) - 1
    last_step = slides[-1].n_steps - 1
    return slides[-1].build_components(last_slide, last_step)


app.layout = html.Div([
    html.Link(href="https://fonts.googleapis.com/css2?family=Lato&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css2?family=STIX+Two+Math&display=swap", rel="stylesheet"),
    dcc.Store(id="slide-index", data=0),
    Keyboard(id="keyboard", captureKeys=["ArrowRight", "ArrowLeft", " ", "Home", "End"]),
    html.Div(id='slide-content', children=[],
             style={"display": "flex", "height": "100vh", "width": "100%",
                    "flexDirection": "column", "alignItems": "center"}),
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
    key = e["key"]
    if key == "ArrowRight" or key == " ":
        return min(current_slide + 1, max_slides - 1)
    elif key == "ArrowLeft":
        return max(current_slide - 1, 0)
    elif key == "Home":
        return 0
    elif key == "End":
        return max_slides - 1
    return current_slide


@app.callback(
    Output("slide-content", "children"),
    Input("slide-index", "data")
)
def update_slide(slide: int) -> List[Component]:
    return build_slide(slide)


if __name__ == "__main__":
    app.run(debug=True)
