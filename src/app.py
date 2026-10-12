import json
import shutil
from pathlib import Path
from typing import List, Optional

import dominate
import numpy as np
from dominate import tags
from dominate.util import raw
from plotly.offline import get_plotlyjs

from povm3 import plot_flat_povm, plot_flat_povm_proof
from povm4 import plot_povm4_plus_minus_regions, plot_povm4, plot_povm4_normalization, \
    plot_povm3_response, plot_povm4_response_diagram, plot_povm4_response
from pvm import plot_pvm
from qubit_povm import get_povm3, get_pvm, get_sample_povm4
from slides import AbstractSlideBuilder, TitleSlideBuilder, json_script

MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
# formulas are typeset by slides.js when they become visible,
# glyphs are cached per formula since plotly removes the formulas it rendered when it redraws a figure
MATHJAX_CONFIG = "window.MathJax = {startup: {typeset: false}, svg: {fontCache: 'local'}};"
FONT_URLS = ["https://fonts.googleapis.com/css2?family=Lato&display=swap",
             "https://fonts.googleapis.com/css2?family=STIX+Two+Math&display=swap"]


def build_slides(title: str) -> tuple[List[AbstractSlideBuilder], List[AbstractSlideBuilder]]:
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
    return main_slides, extra_slides


def get_page_name(slide_idx: int) -> str:
    return "index.html" if slide_idx == 0 else f"slide-{slide_idx}.html"


def get_navigation(slide_idx: int, num_main_slides: int, num_total_slides: int) -> dict:
    last_slide_idx = num_total_slides - 1 if slide_idx < num_total_slides else num_total_slides - 1
    previous_page: Optional[str] = get_page_name(slide_idx - 1) if slide_idx > 0 else None
    next_page: Optional[str] = get_page_name(slide_idx + 1) if slide_idx < last_slide_idx else None
    return {"previous": previous_page, "next": next_page,
            "home": get_page_name(0), "end": get_page_name(num_main_slides - 1)}


def build_page(title: str, slide: AbstractSlideBuilder, navigation: dict) -> str:
    doc = dominate.document(title=title)
    with doc.head:
        tags.meta(charset="utf-8")
        for font_url in FONT_URLS:
            tags.link(href=font_url, rel="stylesheet")
        tags.link(href="style.css", rel="stylesheet")
        tags.script(raw(MATHJAX_CONFIG))
        tags.script(src=MATHJAX_URL)
        tags.script(src="plotly.min.js")

    doc.add(slide.build_html())
    doc.add(json_script(json.dumps({**navigation, "steps": slide.build_steps()}), "slide-data"))
    doc.add(tags.script(src="slides.js"))

    return doc.render()


def generate_site(title: str, main_slides: List[AbstractSlideBuilder], extra_slides: List[AbstractSlideBuilder],
                  assets_dir: Path, site_dir: Path):
    site_dir.mkdir(parents=True, exist_ok=True)

    slides = main_slides + extra_slides
    for slide_idx, slide in enumerate(slides):
        page = build_page(title, slide, get_navigation(slide_idx, len(main_slides), len(slides)))
        (site_dir / get_page_name(slide_idx)).write_text(page, encoding="utf-8")

    for asset in ["style.css", "slides.js"]:
        shutil.copy(assets_dir / asset, site_dir / asset)
    (site_dir / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")

    print(f"Generated {len(slides)} slides in '{site_dir}'")


if __name__ == "__main__":
    title = "Joint Measurability of Noisy Qubit POVMs"
    main_slides, extra_slides = build_slides(title)

    assets_dir = Path(__file__).parent / "assets"
    output_dir = Path(__file__).parent.parent / "site"

    generate_site(title=title, main_slides=main_slides, extra_slides=extra_slides,
                  assets_dir=assets_dir, site_dir=output_dir)
