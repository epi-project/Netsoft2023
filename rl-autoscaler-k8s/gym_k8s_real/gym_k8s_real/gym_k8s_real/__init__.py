from gym.envs.registration import register

#base discrete environment
register(
    id='k8s-env-discrete-state-discrete-action-v0',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteAction',
)

#discrete environment with changed discrete states definition
register(
    id='k8s-env-discrete-state-discrete-action-v1',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteActionV1',
)

#discrete environment with five actions
register(
    id='k8s-env-discrete-state-five-action-v0',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateFiveAction',
)