from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, Set, Iterable, List, Tuple, Optional

import plotly.graph_objects as go
from dash import dcc, html
from dash.development.base_component import Component
from plotly.basedatatypes import BaseTraceType


class AbstractSlideBuilder(ABC):
    @property
    @abstractmethod
    def n_steps(self):
        ...

    @abstractmethod
    def build_components(self, step: int) -> List[Component]:
        ...


class SlideBuilder(AbstractSlideBuilder):
    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.current_step: int = 0
        self.visible_traces: Dict[int, Set[int]] = defaultdict(set)
        self.visible_lines: Dict[int, Set[int]] = defaultdict(set)
        self.fig = go.Figure()
        self.lines: List[str] = []

    @property
    def n_steps(self) -> int:
        return max([*self.visible_traces.keys(), *self.visible_lines.keys()]) + 1

    def add_line(self, line: str) -> int:
        self.lines.append(line)
        line_id = len(self.lines) - 1
        self.visible_lines[self.current_step].add(line_id)
        return line_id

    def add_trace(self, trace: BaseTraceType) -> int:
        self.fig.add_trace(trace)
        trace_id = len(self.fig.data) - 1
        self.visible_traces[self.current_step].add(trace_id)
        return trace_id

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

    def build(self, step: int) -> Tuple[Optional[go.Figure], str]:
        visible_traces = self.visible_traces[step]
        for i, trace in enumerate(self.fig.data):
            trace.visible = i in visible_traces

        visible_lines = self.visible_lines[step]
        text = "\n\n".join([line for i, line in enumerate(self.lines) if i in visible_lines])

        if not self.fig.data:
            return None, text

        return self.fig, text

    def build_components(self, step: int) -> List[Component]:
        title = html.H2(self.title,
                        style={"width": "100%", "textAlign": "center", "margin": "16px 0"}) if self.title else None

        figure, text = self.build(step)

        content = []
        if figure:
            content.append(dcc.Graph(figure=figure, mathjax=True, config={"scrollZoom": True}))

        text_style = {"flex": "1", "padding": "1px", "overflow": "auto"}
        if not figure:
            text_style = {**text_style, "paddingLeft": "20px"}
        content.append(html.Div(children=(dcc.Markdown(text, mathjax=True, dangerously_allow_html=True)),
                                style=text_style))

        row = html.Div(content, style={"display": "flex", "flexDirection": "row", "flex": "1", "width": "100%"})
        layout = [title, row] if title else [row]

        return [html.Div(layout, style={"display": "flex", "flexDirection": "column", "height": "100%",
                                        "width": "100%", "alignItems": "flex-start"})]


class TitleSlideBuilder(AbstractSlideBuilder):
    def __init__(self, title: str, level: int = 1):
        self.title = title
        self.level = level

    @property
    def n_steps(self):
        return 1

    def build_components(self, step: int) -> List[Component]:
        heading_constructor = [html.H1, html.H2, html.H3, html.H4, html.H5, html.H6][self.level - 1]
        heading = heading_constructor(self.title,
                                      style={'textAlign': "center", 'fontFamily': "'Lato', sans-serif"})
        return [html.Div(children=[heading],
                         style={"display": "flex", "justifyContent": "center", "alignItems": "center",
                                "height": "100vh", "width": "100vw"})]
