## Spring 2019 Research
## Collision Resolution Using Reinforcement Learning

This repo contains my research work from the Spring 2019 semester at Columbia University. View this slide deck for more info on the scope of the research and its findings (contact me for access permissions): [Slides](https://docs.google.com/presentation/d/1nHjgszYuplgnmDD4mo8NVOwhFHHzewMdl8g7cVq1O_M/edit?usp=sharing)

The research has two parts:</br>
- D* Lite: In the *d_star_lite* directory, running *main.py* will start a D* Lite simulation with a specified number of robots (the default is three).
  - Pressing the space bar will advance the simulation. The simulation ends once all robots have reached their respective goals.
  - The parameters of the simulation (number of robots and size of the state space) can be changed from within *main.py*.
  - **NOTE**: pygame is required to run the simulation. Instructions for installing pygame can be found [here](https://www.pygame.org/wiki/GettingStarted).
- Reinforcement Learning: In the *d_star_RL* directory, running _D*_*RL.py* will generate policies for all possible jam configurations of a specified size using Q-learning.
