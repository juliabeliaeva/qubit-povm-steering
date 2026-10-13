import json
import shutil
from pathlib import Path
from typing import List, Optional

import dominate
import numpy as np
from dominate import tags
from dominate.dom_tag import dom_tag as html_tag
from dominate.util import raw
from plotly.offline import get_plotlyjs

from povm3 import plot_flat_povm, plot_flat_povm_proof
from povm4 import plot_povm4_plus_minus_regions, plot_povm4, plot_povm4_normalization, \
    plot_povm3_response, plot_povm4_response_diagram, plot_povm4_response
from pvm import plot_pvm
from qubit_povm import get_povm3, get_pvm, get_sample_povm4
from slides import AbstractSlideBuilder, TitleSlideBuilder, json_script

REVEAL_URL = "https://cdn.jsdelivr.net/npm/reveal.js@6.0.2/dist"
REVEAL_CSS_URL = f"{REVEAL_URL}/reveal.css"
REVEAL_JS_URL = f"{REVEAL_URL}/reveal.js"
MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"
# formulas are typeset by slides.js when they become visible,
# glyphs are cached per formula since plotly removes the formulas it rendered when it redraws a figure
MATHJAX_CONFIG = "window.MathJax = {startup: {typeset: false}, svg: {fontCache: 'local'}};"
FONT_URLS = ["https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap",
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


def build_section(slide: AbstractSlideBuilder, section_id: Optional[str] = None) -> html_tag:
    with tags.section(id=section_id) if section_id else tags.section() as section:
        slide.build_html()
        json_script(json.dumps(slide.build_steps()), "slide-steps")
        # empty fragments make reveal.js count the steps, slides.js shows the step content
        for step_idx in range(slide.n_steps - 1):
            tags.span(cls="fragment step", data_fragment_index=step_idx)
    return section


def build_presentation(title: str, main_slides: List[AbstractSlideBuilder],
                       extra_slides: List[AbstractSlideBuilder]) -> str:
    doc = dominate.document(title=title)
    with doc.head:
        tags.meta(charset="utf-8")
        for font_url in FONT_URLS:
            tags.link(href=font_url, rel="stylesheet")
        tags.link(href=REVEAL_CSS_URL, rel="stylesheet")
        tags.link(href="style.css", rel="stylesheet")
        tags.script(raw(MATHJAX_CONFIG))
        tags.script(src=MATHJAX_URL)
        tags.script(src="plotly.min.js")
        tags.script(src=REVEAL_JS_URL)

    with doc.add(tags.div(cls="reveal")):
        with tags.div(cls="slides"):
            for slide_idx, slide in enumerate(main_slides):
                # the End key navigates to the last main slide
                build_section(slide, "end" if slide_idx == len(main_slides) - 1 else None)
            for slide in extra_slides:
                build_section(slide)
    doc.add(tags.script(src="slides.js"))

    return doc.render()


def generate_site(title: str, main_slides: List[AbstractSlideBuilder], extra_slides: List[AbstractSlideBuilder],
                  assets_dir: Path, site_dir: Path):
    site_dir.mkdir(parents=True, exist_ok=True)

    presentation = build_presentation(title, main_slides, extra_slides)
    (site_dir / "index.html").write_text(presentation, encoding="utf-8")

    for asset in ["style.css", "slides.js"]:
        shutil.copy(assets_dir / asset, site_dir / asset)
    (site_dir / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")

    print(f"Generated {len(main_slides) + len(extra_slides)} slides in '{site_dir}'")


if __name__ == "__main__":
    title = "Joint Measurability of Noisy Qubit POVMs"
    main_slides, extra_slides = build_slides(title)

    assets_dir = Path(__file__).parent / "assets"
    output_dir = Path(__file__).parent.parent / "site"

    generate_site(title=title, main_slides=main_slides, extra_slides=extra_slides,
                  assets_dir=assets_dir, site_dir=output_dir)
