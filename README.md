# Joint Measurability of Noisy Qubit POVMs

<div align="center">
  <h3><a href="https://juliabeliaeva.github.io/qubit-povm-steering">Slides</a></h3>
</div>

I made these slides to accompany the seminar presentation of the paper “Exact Steering Bound for Two-Qubit Werner States” [[1](#Zhang2024)].
The paper determines the exact steering threshold for two-qubit Werner states (higher-dimensional case remains open [[2](#QIQCOP)]) using connection between steering and joint measurability of the noisy form of the corresponding POVMs.
The slides are meant to explain the construction of the parent POVM in a visual way.

<div align="center">
  <img width="535" height="206" alt="image" src="https://github.com/user-attachments/assets/098c661e-44f7-422b-99ec-d22d1a8b3f87"/><br/>
  <sub><sup><em>Visualisation of response function for 18-Outcome POVM constructed from two response functions for 6-Outcome POVMs</em></sup></sub>
</div>

## Technical Details

The presentation is generated as static HTML by Python code, using [Plotly](https://plotly.com/python/) graphing library for the figures.
Explanatory text and equation fragments are stored separately in the tagged Markdown files and inserted during slide generation.
Slide steps are implemented by controlling the visibility of specific Plotly traces and associated formula blocks for each stage.
The project originally used [Dash](https://plotly.com/dash/) as presentation framework, which was later switched to [reveal.js](https://revealjs.com/) with the help from Claude.

## References 
<a name="Zhang2024">[1]</a> Y. Zhang and E. Chitambar, “Exact Steering Bound for Two-Qubit Werner States,” Phys. Rev. Lett., vol. 132, no. 25, p. 250201, Jun. 2024, doi: 10.1103/PhysRevLett.132.250201.

<a name="QIQCOP">[2]</a> “POVM steering threshold of higher-dimensional Werner states,” in Quantum information and quantum computation open problem zoo (QIQCOP zoo), 2026. [Online]. Available: https://qiqc-op.com/problem/op_2982ddd94453b5b6/
