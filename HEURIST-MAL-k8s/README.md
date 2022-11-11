## HEURIST-MAL-k8s
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster, obtains state, take actions and calculates reward.

The agents folder contains the two Deep Q-learning RL auto-scaling agents. 

## Install the gym environment
 
```shell
  $ cd gym_k8s_real
  $ pip install -e gym_k8s_real
```

Install once is enough.


#### There is one environment for DQN:
1. `k8s_env_DQN.py`. 

## Run agents

```shell
  $ cd agents
  $ jupyter notebook
```

#### There are two agents implemented with DQN algorithm:
1. `DQN_agent`: the simple DQN agent for base environment without considering heuristic guides;
2. `DQN_agent_with_HValue`: the simple DQN agent for base environment considering heuristic guides;

## Metrics(discrete)
#### Cluster Status
1. CPU utilization: average percent of CPU utilization of all pods on each cluster;
2. Placement of pods: the index of allocated clusters with active pods;
3. Number of active pods on each cluster;

#### Performance/SLA
1. Latency(request time): The ratio of average response time to the SLA response time


#### Data(three clusters)
1. CPU utilization: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
2. Placement of functions: {}, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3};
3. Number of active pods on each cluster: 0, 1-2, 3-4, 5-6, 7-8, 9-10;
4. Latency: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
5. Size: 7 CPU utilization * 3 clusters + 8 placement * 3 functions  + 6 no. of pods * 3 clusters + 7 latency = 70 input neurons in the DQN network

## Action
#### Definition
Each action: [cluster-idx, action-idx, config-idx, app-idx, proxy-idx]: 

1. action-idx == 2: **deploy** the config-idx of app-idx function on cluster-idx and **assign** the corresponding ip in the chain of proxy-idx;
2. action-idx == 0: **remove** the config-idx of app-idx function on cluster-idx and **assign** random ip of  app-idx function in the chain of proxy-idx;
3. action-idx == 1: **assign** ip of the config-idx of app-idx function on cluster-idx in the chain of proxy-idx;

#### Data

1. Dimension: 3\*3\*3\*3\*5 = 405 output neurons in the DQN network;

## Reward
#### Overall Reward
R_all = $\alpha$ * R_res + $\beta$ * R_perf 

#### Resource Reward
R_res = (total number of pods in all clusters) / (maximum number of pods)

#### Performance Reward
No change



