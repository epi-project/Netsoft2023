## HEURIST-MAL-k8s
## Folder Structure
![structure](structure.png)


#### agents folder
1. `DQN_agent.ipynb`: jupyter notebook for the pure deep Q-learning agent;
2. `DQN_agent_with_HValue.ipynb`: jupyter notebook for the heuristic accelerated deep Q-learning agent;


#### gym\_k8s\_real 
1. `gym_k8s_real`: 
2. the subfolder `envs` contains python files that define all properties or actions gym environments have; one python file correspond to one gym environment; 
3. the `k8s_env_DQN.py` file is the gym environment for deep Q-learning or heuristic accelerated deep Q-learning;
2. `gym_k8s_real.egg-info`: generate automatically when you run `pip install xxx` command to install this `gym_k8s_real` package;

## Pipeline of training
#### Prepare initial training enviroment
1. remove all deployments or svc of BF functions(encrypt, decrypt, firewall);
2. deploy all proxy pods according to usecases;
3. make sure `gym_k8s_real` package is installed;

#### Start the training loop
1. start `DQN_agent.ipynb` or `DQN_agent_with_HValue.ipynb` jupyter notebook;
2. run all the cells in this notebook;
3. run the `train` function in the notebook, then it will automatically start training and recording.

#### Stages in the training loop


