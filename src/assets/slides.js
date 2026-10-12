(function () {
    'use strict';

    const slideData = JSON.parse(document.getElementById('slide-data').textContent);
    const steps = slideData.steps;

    const figureElement = document.getElementById('figure-data');
    const figure = figureElement ? JSON.parse(figureElement.textContent) : null;
    const graph = document.getElementById('graph');
    const row = document.querySelector('.slide-row');
    const lines = Array.from(document.querySelectorAll('.md-line'));

    const plotConfig = {
        scrollZoom: true,
        responsive: true,
        toImageButtonOptions: {width: null, height: null, scale: 2}  // use current dimensions
    };

    const typesetElements = new Set();
    let currentStep = parseStep(window.location.hash);
    let plotted = false;

    function parseStep(hash) {
        const value = hash.replace('#', '');
        if (value === 'last') {
            return steps.length - 1;
        }
        const step = parseInt(value, 10);
        return Number.isNaN(step) ? 0 : Math.min(Math.max(step, 0), steps.length - 1);
    }

    function typesetMath(elements) {
        const pending = elements.filter(element => !typesetElements.has(element));
        pending.forEach(element => typesetElements.add(element));
        return pending.length > 0 ? MathJax.typesetPromise(pending) : Promise.resolve();
    }

    function showStep() {
        const step = steps[currentStep];

        const visibleLines = new Set(step.lines);
        lines.forEach((line, i) => {
            line.hidden = !visibleLines.has(i);
        });
        typesetMath(lines.filter((_, i) => visibleLines.has(i)));
        if (row) {
            row.classList.toggle('no-text', visibleLines.size === 0);
        }

        if (figure) {
            const visibleTraces = new Set(step.traces);
            const visible = figure.data.map((_, i) => visibleTraces.has(i));
            if (!plotted) {
                figure.data.forEach((trace, i) => {
                    trace.visible = visible[i];
                });
                Plotly.newPlot(graph, figure.data, figure.layout, plotConfig);
                plotted = true;
            } else {
                Plotly.restyle(graph, {visible: visible});
                Plotly.Plots.resize(graph);
            }
        }

        history.replaceState(null, '', '#' + currentStep);
    }

    function goToPage(page, step) {
        if (page) {
            window.location.href = page + '#' + step;
        }
    }

    function nextStep() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep();
        } else {
            goToPage(slideData.next, 0);
        }
    }

    function previousStep() {
        if (currentStep > 0) {
            currentStep--;
            showStep();
        } else {
            goToPage(slideData.previous, 'last');
        }
    }

    document.addEventListener('keydown', event => {
        switch (event.key) {
            case 'ArrowRight':
            case ' ':
                nextStep();
                break;
            case 'ArrowLeft':
                previousStep();
                break;
            case 'Home':
                goToPage(slideData.home, 0);
                break;
            case 'End':
                goToPage(slideData.end, 'last');
                break;
            default:
                return;
        }
        event.preventDefault();
    });

    // navigating to the same page with a different step only changes the hash
    window.addEventListener('hashchange', () => {
        currentStep = parseStep(window.location.hash);
        showStep();
    });

    // plotly needs MathJax to render formulas in the figures
    MathJax.startup.promise.then(() => {
        typesetMath(Array.from(document.querySelectorAll('.slide-title')));
        showStep();
    });
})();
