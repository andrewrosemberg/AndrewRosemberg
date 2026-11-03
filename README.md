# Andrew Rosemberg

PhD candidate in Machine Learning at [Georgia Tech](https://www.isye.gatech.edu/) and [AI4OPT](https://www.ai4opt.org/), advised by [Pascal Van Hentenryck](https://www.isye.gatech.edu/users/pascal-van-hentenryck). I work at the intersection of machine learning and mathematical optimization, developing methods for **reliable, effective, and computationally efficient decision-making under uncertainty**: learned solution maps and policies, the local response of optimization models, value functions, and decisions under estimated uncertainty and model mismatch.

**[Website](https://andrewrosemberg.github.io/AndrewRosemberg/)** · [CV](https://andrewrosemberg.github.io/AndrewRosemberg/assets/files/Andrew_Rosemberg_CV.pdf) · [Google Scholar](https://scholar.google.com/citations?user=jOuzK3EAAAAJ) · [LinkedIn](https://www.linkedin.com/in/andrew-rosemberg-46ba8613b/)

- **NeurIPS 2026:** [Masked Sobolev Training for Feasibility-Reliable Optimization Proxies](https://andrewrosemberg.github.io/NeurIPS2026-Masked-Sobolev-Optimization-Proxies/)
- **[DiffOpt.jl](https://github.com/jump-dev/DiffOpt.jl):** sensitivities of nonconvex programs with respect to JuMP parameters
- **[LearningToOptimize](https://github.com/LearningToOptimize):** learned proxies and policies for constrained decision problems, including [DecisionRules.jl](https://github.com/LearningToOptimize/DecisionRules.jl)
- **[HydroPowerModels.jl](https://github.com/andrewrosemberg/HydroPowerModels.jl)**, **[PortfolioOpt.jl](https://github.com/andrewrosemberg/PortfolioOpt.jl)**, **[OptimalBids.jl](https://github.com/andrewrosemberg/OptimalBids.jl)**

If these tools help your work, consider [sponsoring them](https://github.com/sponsors/andrewrosemberg).

<details>
<summary>About this repository (source of the website)</summary>

The website is a hand-built static site with no runtime dependencies.

```
src/            pages (HTML with a metadata comment) and assets
src/_partials/  shared head, header and footer
data/           publications.json, projects.json, news.json
build.py        renders src/ + data/ into _site/ (Python 3, standard library only)
tools/          make_figures.py regenerates the site-styled charts;
                make_diagrams.js regenerates the decision-process diagrams
```

- Preview: `python3 build.py --serve`, then open http://localhost:8000/
- Deploy: pushing to `main` runs `.github/workflows/Deploy.yml`, which builds `_site/` and publishes it to the `gh-pages` branch.
- Add a paper: append an entry to `data/publications.json` (set `"selected": true` to feature it on the home page).
- Add a project: add an entry to `data/projects.json`. An internal page lives at `src/research/<slug>/index.html`; copy an existing project page as a template. A project with its own website just sets `href` to that URL, and its card links straight to it.
- Diagrams: pages include `{{diagram:stage focus=state,duals}}` or `{{diagram:through}}`; the SVG lives in `src/_partials/diagrams/` and is regenerated with `npm install --no-save mathjax-full@3.2.2 && node tools/make_diagrams.js`.
- Regenerate charts: `python3 -m venv .venv && .venv/bin/pip install matplotlib numpy && .venv/bin/python tools/make_figures.py`

</details>
