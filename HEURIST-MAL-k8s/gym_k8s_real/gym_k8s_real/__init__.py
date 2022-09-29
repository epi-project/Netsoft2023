from gym.envs.registration import register

register(
    id='k8s-env-discrete-state-discrete-action-v0',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteAction',
)

register(
    id='k8s-env-discrete-state-five-action-v0',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateFiveAction',
)

register(
    id='k8s-env-discrete-state-discrete-action-v1',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteAction15Rres',
)

register(
    id='k8s-env-discrete-state-discrete-action-v2',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteAction20Rres',
)