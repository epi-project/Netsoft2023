## k8s RL autoscaler
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster,obtains states and calculates reward.

The agents folder contains the Q-learing RL autoscaler. 

## Install the gym environment
 
```shell
  $ cd gym_k8s_real
  $ pip install -e gym_k8s_real
```

Or run this command in `agents/Q_Agent_*.ipynb`:

```shell
  $ !pip install -e ../gym_k8s_real
```
Install once is enough.


#### There are three environments in total:
1. `k8s-env-discrete-state-discrete-action-v0`: base discrete environment with reward function = 1\*Rres + 1.5\*Rperf; 
2. `k8s-env-discrete-state-discrete-action-v1`: base discrete environment with reward function = 1.5\*Rres + 1\*Rperf;
3. `k8s-env-discrete-state-discrete-action-v2`: base discrete environment with reward function = 2\*Rres + 0.5\*Rperf;
4. `k8s-env-discrete-state-five-action-v0`: base discrete environment with five actions

## Run agents

```shell
  $ cd agents
  $ jupyter notebook
```

#### There are three agents in total:
1. `QAgent_1.5Rperf`: the simple Q-learning agent for base environment and reward function = 1\*Rres + 1.5\*Rperf;
2. `QAgent_2Rres`: the simple Q-learning agent for base environment and reward function = 2\*Rres + 0.5\*Rperf; 
2. `QAgent_5Actions`: the simple Q-learning agent for environment with five actions. 

## Metrics
#### cpu utilization, number of pods
obtained from HPA for proxy pod

#### latency(request time)
obtained from lz-04 server, which sends multiple requests and uses the average handling time as latency

## Results visualization
#### training data
Q-table for the Q-learning agent is stored in `Q-env-discrete-state-discrete-action-data_*.npy` of each agent folder. 

Historical data of each training round, including states of the system, taken action and reward, is stored in `k8s_historical_states_discrete_*.csv` of each agent folder.

#### plots
Results are plotted in `ResultsVis_*.ipynb` of each agent folder. 


