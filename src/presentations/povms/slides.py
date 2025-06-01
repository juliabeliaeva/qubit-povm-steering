from collections import defaultdict
from typing import Dict, Set, Iterable, List, Tuple, Optional

import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType


class SlideBuilder:
    def __init__(self):
        self.current_step: int = 0
        self.visible_traces: Dict[int, Set[int]] = defaultdict(set)
        self.visible_lines: Dict[int, Set[int]] = defaultdict(set)
        self.fig = go.Figure()
        self.lines: List[str] = []

    @property
    def n_steps(self):
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


def create_text_slide(text: str) -> SlideBuilder:
    slide_builder = SlideBuilder()
    slide_builder.add_line(text)
    return slide_builder
