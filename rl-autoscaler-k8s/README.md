## k8s RL autoscaler
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster,obtains states and calculates reward.

The agents folder contains the Q-learing RL autoscaler. 

## Install the gym environment
 
```shell
  $ pip install -e gym_k8s_real
```

Or run this command in `agents/Q_agent.ipynb`:

```shell
  $ !pip install -e ../gym_k8s_real
```

#### There are three environments in total:
1. `k8s-env-discrete-state-discrete-action-v0`: base discrete environment; 
2. `k8s-env-discrete-state-discrete-action-v1`: discrete environment with changed discrete states definition
3. `k8s-env-discrete-state-five-action-v0`: base discrete environment with five actions

## Run agents

```shell
  $ jupyter notebook
```

#### There are three agents in total:
1. `Q_agent.ipynb`: the simple Q-learning agent for base environment. 
2. `Q_agent_five_actions.ipynb`: the simple Q-learning agent for base environment. 
3. `Q_agent_discrete_states_V1.ipynb`: the simple Q-learning agent for base environment. 

## Metrics
#### cpu utilization, number of pods
obtained from HPA for proxy pod

#### latency(request time)
obtained from lz-04 server, which sends multiple requests and uses the average handling time as latency

## Initial results visualization
#### training data
Q-table for the Q-learning agent is stored in `Q-env-discrete-state-discrete-action-data.npy`. 

Historical data of each training round, including states of the system, taken action and reward, is stored in `k8s_historical_states_discrete.csv`.

#### plots
Results are plotted in `ResultsVis.ipynb`. 


