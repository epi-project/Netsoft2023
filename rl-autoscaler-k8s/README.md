## k8s RL autoscaler
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster,obtains states and calculates reward.

The agents folder contains the Q-learing RL autoscaler. 

## Install the gym environment
 
```shell
  $ pip install -e gym_k8s_real
```

Or 

Run `!pip install -e ../gym_k8s_real ` in `agents/Q_agent.ipynb`

## Run agents

```shell
  $ jupyter notebook
```

agents/Q_agent.ipynb is the simple Q-learning implementation. 

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


