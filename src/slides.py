from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Set, Iterable, List, Optional

import plotly.graph_objects as go
from dominate import tags
from dominate.dom_tag import dom_tag as html_tag
from dominate.util import raw, text
from plotly.basedatatypes import BaseTraceType
from util.utils import render_markdown


class AbstractSlideBuilder(ABC):
    @property
    @abstractmethod
    def n_steps(self):
        ...

    @abstractmethod
    def build_html(self) -> html_tag:
        ...

    def build_steps(self) -> List[Dict[str, List[int]]]:
        return [{"traces": [], "lines": []} for _ in range(self.n_steps)]


class SlideBuilder(AbstractSlideBuilder):
    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.current_step: int = 0
        self.visible_traces: Dict[int, Set[int]] = defaultdict(set)
        self.visible_lines: Dict[int, Set[int]] = defaultdict(set)
        self.fig = go.Figure()
        self.lines: List[str] = []
        self.line_classes: Dict[int, str] = {}

    @property
    def n_steps(self) -> int:
        return max([*self.visible_traces.keys(), *self.visible_lines.keys()]) + 1

    def add_line(self, line: str, line_class: Optional[str] = None) -> int:
        self.lines.append(line)
        line_id = len(self.lines) - 1
        self.visible_lines[self.current_step].add(line_id)
        if line_class:
            self.line_classes[line_id] = line_class
        return line_id

    def add_trace(self, trace: BaseTraceType) -> int:
        self.fig.add_trace(trace)
        trace_id = len(self.fig.data) - 1
        self.visible_traces[self.current_step].add(trace_id)
        return trace_id

    def add_traces(self, traces: List[BaseTraceType]) -> List[int]:
        result = []
        for t in traces:
            result.append(self.add_trace(t))
        return result

    def next_step(self):
        previous_step = self.current_step

        visible_traces = set()
        for trace in self.visible_traces[previous_step]:
            visible_traces.add(trace)

        visible_lines = set()
        for line in self.visible_lines[previous_step]:
            visible_lines.add(line)

        self.current_step += 1
        self.visible_traces[self.current_step] = visible_traces
        self.visible_lines[self.current_step] = visible_lines

    def hide_line(self, line_idx: int):
        self.visible_lines[self.current_step].remove(line_idx)

    def hide_lines(self, line_indices: List[int]):
        for line_idx in line_indices:
            self.visible_lines[self.current_step].remove(line_idx)

    def hide_all_lines(self):
        self.visible_lines[self.current_step].clear()

    def hide_trace(self, trace_idx: int):
        self.visible_traces[self.current_step].remove(trace_idx)

    def hide_traces(self, trace_indices: Iterable[int]):
        for trace_idx in trace_indices:
            self.hide_trace(trace_idx)

    def show_traces(self, trace_indices: Iterable[int]):
        for trace_idx in trace_indices:
            self.visible_traces[self.current_step].add(trace_idx)

    def build_steps(self) -> List[Dict[str, List[int]]]:
        return [{"traces": sorted(self.visible_traces[step]), "lines": sorted(self.visible_lines[step])}
                for step in range(self.n_steps)]

    def build_html(self) -> html_tag:
        with tags.div(cls="slide") as slide:
            if self.title:
                tags.div(raw(render_markdown(f"## {self.title}")), cls="slide-title")

            with tags.div(cls="slide-row"):
                if self.fig.data:
                    tags.div(cls="graph")
                    json_script(self.fig.to_json(), "figure-data")

                text_class = "figure-slide-text" if self.fig.data else "text-slide-text"
                with tags.div(cls=f"slide-text {text_class}"):
                    for line_id, line in enumerate(self.lines):
                        line_class = " ".join(["md-line", self.line_classes.get(line_id, "")]).strip()
                        tags.div(raw(render_markdown(line)), cls=line_class, hidden=True)

        return slide


class TitleSlideBuilder(AbstractSlideBuilder):
    def __init__(self, title: str, level: int = 1, subtitle: Optional[str] = None):
        self.title = title
        self.level = level
        self.subtitle = subtitle

    @property
    def n_steps(self):
        return 1

    def build_html(self) -> html_tag:
        heading_constructor = [tags.h1, tags.h2, tags.h3, tags.h4, tags.h5, tags.h6][self.level - 1]

        with tags.div(cls="title-slide") as slide:
            with heading_constructor():
                add_text_lines(self.title)
            if self.subtitle is not None:
                with tags.h5():
                    add_text_lines(self.subtitle)

        return slide


def add_text_lines(content: str):
    for i, line in enumerate(content.split("\n")):
        if i > 0:
            tags.br()
        text(line)


def json_script(data: str, element_class: str) -> html_tag:
    # "</" would terminate the script element early, "<\/" is an equivalent json escape
    return tags.script(raw(data.replace("</", "<\\/")), type="application/json", cls=element_class)
