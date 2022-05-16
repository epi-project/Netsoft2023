## k8s RL autoscaler
The gym\_k8s\_real folder contains custom gym environment that controls the k8s cluster and obtains states.

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