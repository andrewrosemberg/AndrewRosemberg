+++
title = "Software"
hascode = true
rss = ""
rss_title = "Software"
rss_pubdate = Date(2023, 10, 1)
+++

~~~
<style>
    .container {
        display: flex;
        align-items: center; /* Center items vertically */
    }

    .stats {
        width: 100%; /* Adjust the width as needed to control the stats section */
        margin-right: 20px;
    }

    .stats img {
        max-width: 100%; /* Ensure the stats image takes up the available width */
        height: auto;
    }

    .symbol-container {
        display: flex;
        flex-wrap: wrap; /* Allow symbols to wrap to the next row */
        gap: 10px; /* Adjust the gap as needed */
    }

    /* Set a fixed width and height for symbol images */
    .symbol-container a img {
        width: 40px;
        height: 40px;
    }
</style>

<div class="container">
    <div class="stats">
        <a href="https://github.com/andrewrosemberg/github-readme-stats">
            <img src="https://github-readme-stats.vercel.app/api?username=andrewrosemberg" alt="Andrew's GitHub stats">
        </a>
    </div>
    <div class="symbol-container">
        <a href="https://julialang.org/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/julia/julia-original.svg" alt="Julia"></a>
        <a href="https://www.python.org/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python"></a>
        <a href="https://en.wikipedia.org/wiki/C_(programming_language)"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/c/c-original.svg" alt="C"></a>
        <a href="https://en.wikipedia.org/wiki/C%2B%2B"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/cplusplus/cplusplus-original.svg" alt="C++"></a>
        <a href="https://docs.microsoft.com/en-us/dotnet/csharp/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/csharp/csharp-original.svg" alt="C#"></a>
        <a href="https://www.java.com/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg" alt="Java"></a>
        <a href="https://code.visualstudio.com/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vscode/vscode-original.svg" alt="VS Code"></a>
        <a href="https://www.linux.org/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="Linux"></a>
        <a href="https://www.apple.com/mac/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/apple/apple-original.svg" alt="Mac"></a>
        <a href="https://www.microsoft.com/"><img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" alt="Microsoft"></a>
        <a href="https://ohmyz.sh/"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Z_Shell_Logo_Color_Horizontal.svg/2560px-Z_Shell_Logo_Color_Horizontal.svg.png" alt="Zsh"></a>
    </div>
</div>
~~~

~~~
<div style="display: flex; align-items: center;">
  <h1><a href="https://github.com/andrewrosemberg/HydroPowerModels.jl">HydroPowerModels.jl</a></h1>
  <a href="https://github.com/andrewrosemberg/HydroPowerModels.jl/stargazers">
    <img src="https://img.shields.io/github/stars/andrewrosemberg/HydroPowerModels.jl?style=social" alt="GitHub Stars" style="width: auto;">
  </a>
</div>
~~~

~~~
<style>
  .badge-img {
    height: 18px; /* Adjust the height as needed */
    margin-right: 10px;
    margin-left: 10px;
  }
</style>

<div style="display: flex; align-items: right;">
  <a href="https://zenodo.org/badge/DOI/10.5281/zenodo.3842130">
    <img class="badge-img" src="https://zenodo.org/badge/DOI/10.5281/zenodo.3842130.svg" alt="DOI" style="width: auto;">
  </a>
  <a href="https://andrewrosemberg.github.io/HydroPowerModels.jl/latest/">
    <img class="badge-img" src="https://img.shields.io/badge/docs-latest-blue.svg" alt="Documentation" style="width: auto;">
  </a>
  <a href="https://travis-ci.com/andrewrosemberg/HydroPowerModels.jl">
    <img class="badge-img" src="https://travis-ci.com/andrewrosemberg/HydroPowerModels.jl.svg?branch=master" alt="Build Status" style="width: auto;">
  </a>
  <a href="https://codecov.io/gh/andrewrosemberg/HydroPowerModels.jl?branch=master">
    <img class="badge-img" src="https://codecov.io/gh/andrewrosemberg/HydroPowerModels.jl/coverage.svg?branch=master" alt="Coverage" style="width: auto;">
  </a>
  <a href="https://proceedings.juliacon.org/papers/10.21105/jcon.00035#status">
    <img class="badge-img" src="https://proceedings.juliacon.org/papers/10.21105/jcon.00035/status.svg" alt="Paper" style="width: auto;">
  </a>
</div>
~~~

HydroPowerModels.jl is an open-source tool for Hydrothermal Multistage Steady-State Power Network Optimization solved by Stochastic Dual Dynamic Programming (SDDP).

~~~
<img src="/assets/graph_grid.png" align="right" style="width: auto; margin-left: -100px; margin-right: -100px; margin-bottom: 1px;">
~~~

It is designed to be a flexible and extensible framework for modeling and solving hydrothermal scheduling problems. It is currently under active development and is being used in research projects at [LAMPS](https://github.com/LAMPSPUC/HydroPowerModels.jl).

Built as a Julia/JuMP package, it allows users to explore network formulations from [PowerModels.jl](https://github.com/lanl-ansi/PowerModels.jl) and solve the resulting optimization problems using [SDDP.jl](https://github.com/odow/SDDP.jl).

~~~
<br clear="left"/>
~~~

~~~
<div style="display: flex; align-items: left; height: auto; width: 500px;">
    <img src="/assets/plot_agg_result_hydrogen.png" alt="Image 1" style="width: 50%;">
    <img src="/assets/plot_agg_result_load.png" alt="Image 2" style="width: 50%;">
</div>
~~~

In particular, in my master's thesis, I used HydroPowerModels.jl to assess the impact of network model assumptions on the operation of hydrothermal power systems. Planning under model simplifications can lead to (time)-inconsistent policies when operating the realistic system. The suboptimal decisions often cause higher operational costs, over-consumption of natural resources and increased environmental impacts. A simple but representative example of the such impact is shown below for realistic data from the Bolivian system.


| Policy    | Planning Cost ($10^6$) | Implementation Cost ($10^6$) | Cost GAP (%) | Time (min.) |
|-----------|-------------------|--------------------------|---------|-------------|
| NFA-AC    | 0.58687           | 0.68735                  | 17.067  | 4.67        |
| SOC-AC    | 0.60818           | 0.60935                  | 0.193   | 119.23      |
| DC-AC     | 0.58714           | 0.64523                  | 9.855   | 5.22        |
| DCLL-AC   | 0.61310           | 0.60941                  | -0.602  | 54.33       |


Linearizations of the power flow equations such as those in the Network-Flow Approximation (NFA) and the Direct-Current (DC) models are commonly used in the literature and in practice by system operators. However, these models can lead to drastically suboptimal decisions (with hight implementation cost) and optimistic estimations of the operational costs (a.k.a planning cost). The gap from expected to actual costs can be as high as 17% for the NFA model. 

The results of this work were published in [IEEE Transactions on Sustainable Energy](https://doi.org/10.1109/TSTE.2021.3106810) and presented at [INFORMS](https://www.youtube.com/watch?v=0itXxcjW--s) and PES General Meeting.

~~~
<div style="display: flex; align-items: center;">
  <h1><a href="https://github.com/andrewrosemberg/OptimalBids.jl">OptimalBids.jl</a></h1>
  <a href="https://github.com/andrewrosemberg/OptimalBids.jl/stargazers">
    <img src="https://img.shields.io/github/stars/andrewrosemberg/OptimalBids.jl?style=social" alt="GitHub Stars" style="width: auto;">
  </a>
</div>
~~~

~~~
<style>
  .badge-img {
    height: 18px; /* Adjust the height as needed */
    margin-right: 10px;
    margin-left: 10px;
  }
</style>

<div style="display: flex; align-items: right;">
  <a href="https://andrewrosemberg.github.io/OptimalBids.jl/stable">
    <img class="badge-img" src="https://img.shields.io/badge/docs-stable-blue.svg" alt="Documentation (Stable)" style="width: auto;">
  </a>
  <a href="https://andrewrosemberg.github.io/OptimalBids.jl/dev">
    <img class="badge-img" src="https://img.shields.io/badge/docs-dev-blue.svg" alt="Documentation (Dev)" style="width: auto;">
  </a>
  <a href="https://codecov.io/gh/andrewrosemberg/OptimalBids.jl">
    <img class="badge-img" src="https://codecov.io/gh/andrewrosemberg/OptimalBids.jl/branch/main/graph/badge.svg" alt="Coverage" style="width: auto;">
  </a>
  <a href="https://github.com/invenia/BlueStyle">
    <img class="badge-img" src="https://img.shields.io/badge/code%20style-blue-4495d1.svg" alt="Code Style: Blue" style="width: auto;">
  </a>
  <a href="https://github.com/SciML/ColPrac">
    <img class="badge-img" src="https://img.shields.io/badge/ColPrac-Contributor's%20Guide-blueviolet" alt="ColPrac: Contributor's Guide on Collaborative Practices for Community Packages" style="width: auto;">
  </a>
</div>
~~~

OptimalBids.jl is a Julia package to help users build simple simulators for markets (with pontentially complicated rules). It is designed to be a flexible and extensible framework for modeling and solving market clearing problems.

Significant use cases are electricity markets. Complex and dynamic, the price of electricity is determined by grid physics besides the usual interaction of supply and demand.

Bellow is a small comparison example of bidding strategies for a generator in a spot market based on IEEE-188 system. Even with complete information of what other participants will offer and the demand bids placed by load (demand) agents, maximizing the profit of the generator is not a simple task. 

~~~
<img src="/assets/bayesopt_profit.png" alt="optbids" style="width: 750px; height: 500px; margin-left: -100px; margin-right: -100px; margin-bottom: 1px;">
~~~