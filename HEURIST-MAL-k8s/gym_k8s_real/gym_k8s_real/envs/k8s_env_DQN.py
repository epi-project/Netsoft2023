import datetime
import math
import random
import time
import os
from pprint import pprint

import numpy as np
import requests
from gym import spaces
from gym.envs.toy_text import discrete
from kubernetes import client, config

twenty = 0
forty = 1
sixty = 2
eighty = 3
hundred = 4
hundred_fifty = 5
two_hundred = 6

class K8sEnvDiscreteStateDiscreteAction15Rres(discrete.DiscreteEnv):
    metadata = {
        'render.modes': ['human']
    }

    #app_names: store names of functions need to be placed and scaled; eg: ['firewall', 'encrypt', 'decrypt']
    #app_configs: store the number of different configs of different functions; eg[2, 3, 2]
    #cluster_names: store the names of clusters; eg: []
    def __init__(self, timestep_duration, app_names, app_configs, cluster_names, sla_latency,
            sla_host, sla_latency_metric_name, max_pods, min_pods):
        config.load_kube_config()

        # General variables defining the environment
        # Get following info from k8s
        self.num_cluster = len(cluster_names)
        self.num_app = len(app_names)
        self.num_states = 7 * self.num_cluster + (2 ** self.num_cluster) * self.num_app + 6 * self.num_cluster + 7
        #total number of actions
        self.num_actions = 7 * self.num_app + sum(app_configs)
        P = {
            state: {
                action: [] for action in range(self.num_actions)
            } for state in range(self.num_states)
        }
        initial_state_distrib = np.zeros(self.num_states)
        self.done = False
        self.MAX_PODS = max_pods
        self.MIN_PODS = min_pods
        self.timestep_duration = timestep_duration
        self.app_names = app_names
        self.cluster_names = cluster_names
        self.sla_latency = float(sla_latency)
        self.sla_host = sla_host
        self.sla_latency_metric_name = sla_latency_metric_name

        self.observation_space = spaces.Discrete(self.num_states)

        self.action_space = spaces.Discrete(self.num_actions)
        discrete.DiscreteEnv.__init__(
            self, self.num_states, self.num_actions, P, initial_state_distrib
        )

    #Function to take step

    def step(self, action):
        """
        Returns
        -------
        encoded_observation, reward, done, dt_dict : tuple
            encoded_observation : int
                discretized environment observation encoded in an integer
            real_observation: list
                list of observations that contains the current cpu utilization,
                the hpa cpu threshold, the current number of pods and the
                latency
            reward : float
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            done : boolean
                boolean value of whether training is done or not. Becomes True
                when errors occur.
            dt_dict : Dict
                dictionary of formatted date and time.
        """
        encoded_observation, now_observation = self._get_state()
        if action == 0 and now_observation[1] <= 20:
            return now_observation, 0, self.done, encoded_observation
        if action == 2 and now_observation[1] >= 80:
            return now_observation, 0, self.done, encoded_observation
#         if action == 1:
#             reward = self._get_reward(now_observation)
#             return now_observation, reward, self.done, encoded_observation
        
        self._take_action(action)  # Create HPA
        wait_time = self.timestep_duration * 60
        time.sleep(wait_time)  # Wait timestep_duration minutes for the changes to take place

        encoded_observation, real_observation = self._get_state()
        reward = self._get_reward(real_observation)

        if -1 in self.decode(encoded_observation):
            self.done = True
            reward = 0

        now = datetime.datetime.now()
        dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
        dt_dict = {
            'datetime': dt_string
        }

        return real_observation, reward, self.done, encoded_observation

    #function to get state
    def _get_state(self):
        #get cpu_states of all clusters
        cpu_states = []
        for cluster in self.cluster_names:
            cpu = 0
            count = 0
            for app in self.app_names:
                cpu += self._get_average_cpu(app, cluster)
                if cpu > 0:
                    count += 1
            cpu_states.append(self._get_discrete(cpu/count * 100))
        
        #get number_of_pods in all clusters
        pod_states = []
        for cluster in self.cluster_names:
            num = 0
            for app in self.app_names:
                num += self._get_pods_num(app, cluster)
            pod_states.append(self._get_discrete(100 * num / self.MAX_PODS))
        
        #get placement_of_pods in all clusters
        placement = []
        for app in self.app_names:
            present = self._get_placement(app, self.cluster_names)
            placement.append(self._get_discrete_place(present))

        #get latency
        latency = 100 * self._query_latency(self.sla_latency_metric_name) / self.sla_latency
        
        if math.isnan(latency):
            latency = self.sla_latency

        #define real observation
        real_observation = [
            cpu_states,
            pod_states,
            placement,
            latency
        ]

        #encode each metric
        #return encoded state
        encoded_observation = self.encode(
            cpu_states,
            pod_states,
            placement,
            latency
        )

        return encoded_observation, real_observation
    
    #get average_cpu for all pods with app_name on cluster with cluster
    #return 0.xx
    def _get_average_cpu(self, app_name, cluster, cpuReqs):
        aver_cpu = 0
        #obtain from metric server and calculate
        output = os.popen('kubectl top pod --context=' + cluster).read()
        lines = output.split("\n")
        numPods = 0
        cpuUsage = 0
        for line in lines[:-1]:
            items = line.split()
            if len(items[0]) > 8 and items[0][:8] == app_name:
                numPods += 1
                cpuUsage += int(items[1][:-1])
        aver_cpu = cpuUsage / (numPods * cpuReqs) if numPods else 0.0
        # return numPods, cpuUsage / (numPods * cpuReqs)
        return aver_cpu
    
    #get number of active pods with app_name on cluster with cluster
    def _get_pods_num(self, app_name, cluster):
        #first judge if there exists app_name pod on cluster-x through kubectl get command; if not, return 0
        #obtain from metric server
        output = os.popen('kubectl top pod --context=' + cluster).read()
        lines = output.split("\n")
        numPods = 0
        for line in lines[:-1]:
            items = line.split()
            if len(items[0]) > 8 and items[0][:8] == app_name:
                numPods += 1
        return numPods
    
    #get the index of allocated clusters with active pod
    def _get_placement(self, app_name, clusters):
        #use _get_pods_num to calculate number on each cluster and output
        present = [0 for _ in range(len(clusters))]
        for i in range(len(clusters)):
            num = self._get_pods_num(app_name, clusters[i])
            present[i] = 1 if num else 0
        return present

    #get latency metric
    def _query_latency(self, query_name):
        latency_endpoint = self.sla_host + query_name
        response = requests.get(
            latency_endpoint
        )
        results = response.json()
        if results:
            return results
        else:
            return float('NaN')

    #get discrete number of each percent
    def _get_discrete(self, number):
        """
        Get a number and return the discrete level it belongs to
        """
        number = round(number, 0)

        if number in range(-1, 20):
            return twenty
        elif number in range(20, 40):
            return forty
        elif number in range(40,60):
            return sixty
        elif number in range(60, 80):
            return eighty
        elif number in range(80, 101):
            return hundred
        elif number in range(101, 150):
            return hundred_fifty
        elif number in range(150, 200) or number >= 200:
            return two_hundred
        else:
            return -1
    
    #get discrete number of placement
    def _get_discrete_place(self, place):
        code = 0
        num = 1
        for idx in place:
            if idx != 0:
                code += num
            num *= 2
        return code
    
    #encode state to one dimension discrete space
    def encode(self, cpu_util, pods, places, latency):
        """
        Encode the discrete observation values in one single number.
        CPU utilization and latency can take values in {0, 1, 2, 3, 4, 5, 6}
        Pod utilization can take values in {0, 1, 2, 3, 4}
        Place can take values in {1, ..., 2^n-1}
        """
        state = []
        for cpu in cpu_util:
            tmp = [0 for _ in range(7)]
            tmp[cpu] = 1
            state += tmp[:]
        
        for pod in pods:
            tmp = [0 for _ in range(6)]
            tmp[pod] = 1
            state += tmp[:]
        
        for place in places:
            tmp = [0 for _ in range(2 ** self.num_cluster)]
            tmp[place] = 1
            state += tmp[:]
        
        tmp = [0 for _ in range(7)]
        tmp[latency] = 1
        state += tmp[:]

        return state

    #TO-DO: Decode action
    def _decode_action(action):
        res = 0
        return res


    def _create_pod(number, appName, containerUrl, commands, cpuReq, cpuLimit, contextName):
        config.load_kube_config(context=contextName)
        v1 = client.AppsV1Api()
        body = client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=client.V1ObjectMeta(name=appName, labels={'app': appName}),
            spec=client.V1DeploymentSpec(
                replicas=number,
                selector=client.V1LabelSelector(match_labels={'app': appName}),
                strategy=client.V1DeploymentStrategy(),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={'app': appName}),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            image=containerUrl,
                            name=appName,
                            resources=client.V1ResourceRequirements(
                                limits={'cpu': cpuLimit},
                                requests={'cpu': cpuReq}
                            )
                        )],
                        restart_policy='Always'
                    )
                )
            ),
            status= client.V1DeploymentStatus()
        )
        # Create new HPA with updated thresholds
        try:
            api_response = v1.replace_namespaced_deployment(name=appName, namespace='default', body=body, pretty=True)
            print('Modified deployment for function ' + appName)
        except Exception:
            api_response = v1.create_namespaced_deployment(namespace='default', body=body, pretty=True)
            print('Created deployment for function ' + appName)