## HEURIST-MAL-k8s
The gym\_k8s\_real folder contains predefined gym environment that controls the k8s cluster,obtains states and calculates reward.

The agents folder contains the Deep Q-learning RL autoscaler. 

## Install the gym environment
 
```shell
  $ cd gym_k8s_real
  $ pip install -e gym_k8s_real
```


Install once is enough.


#### There is one environment for DQN:
1. `k8s_env_DQN`. 

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
2. Placement of pods: the index of allocated clusters with active pods;
3. Number of active pods on each cluster;

#### Performance/SLA
1. Latency(request time): The ratio of average response time to the SLA response time


#### Data(two clusters)
1. CPU utilization: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
2. Placement of functions: {0}, {1}, {2}, {1,2};
3. Number of active pods on each cluster: 0, 1-2, 3-4, 5-6, 7-8, 9-10;
4. Latency: 0%–20%, 20%–40%, 40%–60%, 60%–80%, 80%–100%, 100%-150%, greater than 150%;
5. Size: 7 CPU utilization * 2 clusters + 4 placement * 3 functions  + 6 no. of pods * 2 clusters + 7 latency = 45 input neurons in the DQN network

## Action
#### Definition
Each function: [cluster-idx, remove/create/do nothing, config-idx, proxy-idx]: change (remove or create) the config-idx of this function on cluster-idx and add the corresponding ip in the chain of proxy-idx, or do nothing.

#### Data
1. Possible states: [1-2,0/1/-1,1-3,1-5];
2. Size: (2+3+3+5)action neurons * 3 functions = 39 output neurons in the DQN network;

## Reward
#### Overall Reward
R_all = $\alpha$ * R_res + $\beta$ * R_perf 

#### Resource Reward
R_res = (total number of pods in all clusters) / (maximum number of pods)

#### Performance Reward
No change



