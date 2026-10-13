(function () {
    'use strict';

    const plotConfig = {
        scrollZoom: true,
        responsive: true,
        toImageButtonOptions: {width: null, height: null, scale: 2}  // use current dimensions
    };

    const typesetElements = new Set();
    const slides = new Map();

    function getSlide(section) {
        if (!slides.has(section)) {
            const figureElement = section.querySelector('.figure-data');
            slides.set(section, {
                steps: JSON.parse(section.querySelector('.slide-steps').textContent),
                figure: figureElement ? JSON.parse(figureElement.textContent) : null,
                graph: section.querySelector('.graph'),
                row: section.querySelector('.slide-row'),
                lines: Array.from(section.querySelectorAll('.md-line')),
                plotted: false
            });
        }
        return slides.get(section);
    }

    function typesetMath(elements) {
        const pending = elements.filter(element => !typesetElements.has(element));
        pending.forEach(element => typesetElements.add(element));
        return pending.length > 0 ? MathJax.typesetPromise(pending) : Promise.resolve();
    }

    function getCurrentStep() {
        // step i is shown together with the fragment i - 1, the fragment index is undefined for one-step slides
        const fragment = Reveal.getIndices().f;
        return fragment === undefined ? 0 : fragment + 1;
    }

    function showStep(section, stepIdx) {
        const slide = getSlide(section);
        const step = slide.steps[Math.min(stepIdx, slide.steps.length - 1)];

        const visibleLines = new Set(step.lines);
        slide.lines.forEach((line, i) => {
            line.hidden = !visibleLines.has(i);
        });
        typesetMath(slide.lines.filter((_, i) => visibleLines.has(i)));
        if (slide.row) {
            slide.row.classList.toggle('no-text', visibleLines.size === 0);
        }

        if (slide.figure) {
            const visibleTraces = new Set(step.traces);
            const visible = slide.figure.data.map((_, i) => visibleTraces.has(i));
            // figures are plotted when their slide is first shown, since plotly can't size a hidden element
            if (!slide.plotted) {
                slide.figure.data.forEach((trace, i) => {
                    trace.visible = visible[i];
                });
                Plotly.newPlot(slide.graph, slide.figure.data, slide.figure.layout, plotConfig);
                slide.plotted = true;
            } else {
                Plotly.restyle(slide.graph, {visible: visible});
                Plotly.Plots.resize(slide.graph);
            }
        }
    }

    function showCurrentStep() {
        showStep(Reveal.getCurrentSlide(), getCurrentStep());
    }

    function goToEnd() {
        Reveal.slide(Reveal.getIndices(document.getElementById('end')).h);
    }

    Reveal.initialize({
        hash: true,
        // slides fill the window without scaling, since plotly doesn't handle mouse events in scaled elements
        width: '100%',
        height: '100%',
        margin: 0,
        minScale: 1,
        maxScale: 1,
        center: false,
        transition: 'none',
        keyboard: {35: goToEnd}  // End
    })
        // plotly needs MathJax to render formulas in the figures
        .then(() => MathJax.startup.promise)
        .then(() => {
            typesetMath(Array.from(document.querySelectorAll('.slide-title')));
            showCurrentStep();
            ['slidechanged', 'fragmentshown', 'fragmenthidden', 'resize'].forEach(event => {
                Reveal.on(event, showCurrentStep);
            });
        });
})();
