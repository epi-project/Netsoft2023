## HEURIST-MAL-k8s
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster,obtains states and calculates reward.

The agents folder contains the Deep Q-learning RL autoscaler. 

## Install the gym environment
 
```shell
  $ cd gym_k8s_real
  $ pip install -e gym_k8s_real
```


Install once is enough.


#### There are four environments in total:
1. `k8s-env-discrete-state-discrete-action-v0`: base discrete environment with reward function = 1\*Rres + 1.5\*Rperf; 
2. `k8s-env-discrete-state-discrete-action-v1`: base discrete environment with reward function = 1.5\*Rres + 1\*Rperf;
3. `k8s-env-discrete-state-discrete-action-v2`: base discrete environment with reward function = 2\*Rres + 0.5\*Rperf;
4. `k8s-env-discrete-state-five-action-v0`: base discrete environment with five actions

## Run agents

```shell
  $ cd agents
  $ jupyter notebook
```

#### There is one agent implemented with DQN algorithm:
1. `DQN_agent`: the simple DQN agent for base environment and reward function = xxx;

## Metrics(discrete)
#### Cluster Status
1. CPU utilization: average percent of CPU utilization of all pods on each cluster;
2. Placement of pods: the index of allocated clusters with active pods
3. Number of active pods on each cluster;

#### Performance/SLA
1. Latency(request time): The ratio of average response time to the SLA response time


#### Data
1. CPU utilization: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
2. Placement of pods: {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3};
3. Number of active pods on each cluster: 0, 1-2, 3-4, 5-6, 7-8, 9-10;
4. Latency: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
5. Size: 7 CPU utilization * 3 clusters + 7 placement * 3 functions  + 6 no. of pods * 3 clusters + 7 latency = 61 input neurons in the DQN network

## Action
#### Definition
[cluster_idx, change in number of pods]: change (increment or decrement) the cluster number as in the dictionary key values, increase or decrease pods' number one at a time (scale in or out), or do nothing.

#### Data
1. Possible states: [1,+1], [1,-1], [2,+1], [2, -1], [3, +1], [3, -1], [0,0];
2. Size: _7 actions for each function_ * 3 functions + 2 actions for proxy config = 23 output neurons in the DQN network;
3. 


## Reward
#### Overall Reward
R_all = \alpha R_res + \beta R_{perf}

1. do we need to change the **range**? No
2. how to set the **weights** between resource reward and performance reward? More fine-tune

#### Resource Reward
max limit will be the same; normal sum and average

1. will the max pod limit for each function be the same?
2. how to combine each part? weighted sum or normal sum? 


#### Performance Reward
No change



