@def title = "Andrew Rosemberg"
@def hasmath = false
@def hascode = false
<!-- Note: by default hasmath == true and hascode == false. You can change this in
the config file by setting hasmath = false for instance and just setting it to true
where appropriate -->

## About me

<!-- raw html to allow a responsive row  -->
~~~
<style>
  .link-container {
    display: flex;
    justify-content: space-between;
    gap: 10px; /* Adjust the gap as needed to control spacing */
  }

  /* Style for the last link to push it to the right */
  .link-container a:last-child {
    margin-left: auto;
  }
</style>

<div class="row">
  <div class="container">
    <img class="left" style="width:20%; float: left; margin-right: 20px;" src="assets/avatar.jpeg">
    <div class="link-container">
      <div style="float: left;">
        <a href="https://github.com/andrewrosemberg"><img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="Github Profile" style="max-width:60px; max-height:60px; width=auto; height=auto"></a>
        <a href="https://www.linkedin.com/in/andrew-rosemberg-46ba8613b/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linkedin/linkedin-original.svg" alt="Linkedin Profile" style="max-width:60px; max-height:60px; width=auto; height=auto"></a>
      </div>
      <a href="https://www.ai4opt.org/"><img src="https://www.ai4opt.org/themes/custom/baltarai4opt/images/ai4opt.png" alt="AI4OPT" style="max-width:250px; max-height:250px; width=auto; height=auto"></a>
    </div>
    <div style="clear: both;"></div>
    <div style="overflow: hidden;">
      <p>
        👋 Hi, there! I'm <strong>Andrew</strong>, a Machine Learning and Optimization researcher at AI4OPT and a ML PhD student at Georgia Tech.
      </p>
      <p>
        I am persuing a PhD at the <a href="https://www.isye.gatech.edu/" target="_blank">H. Milton Stewart School of Industrial and Systems Engineering</a>, <a href="https://www.gatech.edu/" target="_blank">Georgia Tech</a>, under the guidance of <a href="https://www.isye.gatech.edu/users/pascal-van-hentenryck" target="_blank">Dr. Pascal Van Hentenryck</a>. My research focuses on the intersection of machine learning, optimization, and their practical applications within the realm of energy systems and sustainability.
      </p>
      <p>
        Presently, I am actively engaged as a researcher at the <a href="https://www.ai4opt.org/" target="_blank">Artificial Intelligence Institute for Advances in Optimization (AI4OPT)</a>.
      </p>
    </div>
  </div>
</div>

~~~

## Experiences

#### 2023-Present: Researcher (Machine Learning and Optimization) 
##### @AI4OPT, Atlanta, US
Research in automated decision-making methods under uncertainty, combining Machine Learning and Optimization. The main emphasis is on the development of interpretable AI for pressing global challenges using tractable models and robust decision frameworks.

#### 2020-2023: Researcher (Machine Learning and Optimization)
##### @ Invenia Labs, Cambridge, UK

Strategic algorithmic operation in energy markets to support the renewable energy transition.
- Led projects on the implementation of stochastic, robust, and distributionally robust optimization approaches to tackle uncertainty in daily bidding operations, coupling Machine Learning techniques to estimate uncertainty and appropriate optimization methods to find robust decisions.
- Contributed to the construction of a detailed market simulator for counterfactual analysis. Led the data analysis of simulation results accuracy.
- Led work on decomposition techniques for large-scale Integer and continuous optimization problems, proposed methods for estimation of unknown parameters of the grid through Inverse Optimization and other heuristics.
- Exploration of exact and surrogate approaches to bi-level optimization (for hyperparameter optimization and strategic bidding). Including integration of Automatic Differentiation and Automatic Dualization of optimization problems to help implement explored approaches.
- Experience in MISO, PJM, ERCOT, CAISO, SPP, ISO-NE, and NYISO.

#### 2017-2019: Research Staff Member
##### @ LAMPS PUC-Rio, Rio de Janeiro, Brazil

Laboratory for Applied Mathematical Programming and Statistics (LAMPS).
- Research and development of mathematical programming solutions to find power systems transmission usage optimal contracting strategies for one of Brazil's biggest electricity services companies (Energisa Group).
- Development of flexible software for Hydrothermal Multistage Economic dispatch in a consulting project for FGV Energia to help assess network and installed capacity changes. (HydroPowerModels Project).
