from gym.envs.registration import register

register(
    id='k8s-env-discrete-state-discrete-action-v0',
    entry_point='gym_k8s_real.envs:K8sEnvDiscreteStateDiscreteAction',
)
