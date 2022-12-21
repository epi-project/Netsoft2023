import datetime
from ipaddress import ip_address
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

class K8sEnvDQN3Proxy(discrete.DiscreteEnv):
    metadata = {
        'render.modes': ['human']
    }

    #app_names: store names of functions need to be placed and scaled; eg: ['firewall', 'encrypt', 'decrypt']
    #app_configs: store the number of different configs of different functions; eg[2, 3, 2]
    #cluster_names: store the names of clusters; eg: []
    def __init__(self, timestep_duration, app_names, app_configs, cluster_names, sla_latency,
            sla_host, sla_latency_metric_name, max_pods, min_pods, app_dict, config_path, changes):
        config.load_kube_config()
        # General variables defining the environment
        # Get following info from k8s
        self.num_cluster = len(cluster_names)
        self.num_app = len(app_names)
        self.num_configs = len(app_configs)
        self.app_dict = app_dict
        #[0, 1, 2]: 0-remove, 1-no action, 2-create
        self.changes = changes
        self.config_path = config_path
        self.ip_proxy = [['miss'], ['miss', 'miss'], ['miss', 'miss', 'miss']]
        #curr_configs[i][j][k]: deployments of kth configs of ith function on jth cluster
        self.curr_configs = [[[0 for k in range(self.num_configs)] for j in range(self.num_cluster)] for i in range(self.num_app)] 
        self.num_states = 7 * self.num_cluster + (2 ** self.num_cluster) * self.num_app + 6 * self.num_cluster + 7
        #total number of actions
        self.num_actions = self.num_cluster * self.num_configs * len(self.changes) * len(self.ip_proxy) * self.num_app
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
        #app_names: ['firewall', 'encrypt', 'decrypt']
        self.app_names = app_names
        #app_configs: ['s', 'm', 'l']
        self.app_configs = app_configs
        self.cluster_names = cluster_names
        self.sla_latency = float(sla_latency)
        self.sla_host = sla_host
        self.sla_latency_metric_name = sla_latency_metric_name
        self.proxy_cluster = {0: self.cluster_names[0], 1: self.cluster_names[1], 2: self.cluster_names[2]}
        self.proxy_dict = {0: 'proxy-1', 1: 'proxy-2', 2: 'proxy-3'}
        #three proxy chainings: [firewall], [e-f], [f-e-d]
        
        self.observation_space = spaces.Discrete(self.num_states)

        self.action_space = spaces.Discrete(self.num_actions)
        discrete.DiscreteEnv.__init__(
            self, self.num_states, self.num_actions, P, initial_state_distrib
        )

    #debug the process of obtaining states
    def d_state(self):
        return self._get_state()

    #debug the process of taking action
    def d_action(self, action_idx):
        action = self._decode_action(action_idx)
        return self._take_action(action[2], action[4], action[0], action[1], action[3])

    #reset or initialize k8s cluster
    def reset(self):
        #todo: assign unreachable ip_address
        self.ip_proxy = [['miss'], ['miss', 'miss'], ['miss', 'miss', 'miss']]
        # for proxy_id in range(3):
        #     #deploy the proxy pod
        #     #configure each proxy
        #     self._deploy_proxy(proxy_id)

        return self._get_state()


    #Function to take step
    def step(self, action_idx):
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
        action = self._decode_action(action_idx)
        self._take_action(action[2], action[4], action[0], action[1], action[3]) # Deploy or remove configs of functions
        wait_time = self.timestep_duration * 60
        time.sleep(wait_time)  # Wait timestep_duration minutes for the changes to take place

        #not all proxys are patched
        if not self._check_proxy:
            encoded_observation, real_observation = self._get_state_max_latency()
            reward = 0
        else:
            encoded_observation, real_observation = self._get_state()
            reward = self._get_reward(real_observation)

        return real_observation, reward, self.done, encoded_observation

    def _check_proxy(self):
        for i in range(3):
            for ip in self.ip_proxy[i]:
                if ip == "miss":
                    return False
        return True

    def _get_reward(self, real_observation):
        """
        Calculate reward value: The environment receives the current values of
        pod_number and cpu/memory metric values that correspond to the current
        state of the system s. The reward value r is calculated based on two
        criteria:
        (i)  the amount of resources acquired,
             which directly determines the cost
        (ii) the number of pods needed to support the received load.
        """

        (cpu_states,
        pod_states,
        placement,
        latency) = real_observation

        reward_min = 0
        reward_max = 25
        reward = 0

        pod_weight = 1.5
        throughput_weight = 1

        d = 5.0  # this is a hyperparameter of the reward function

        #计算throughput的reward
        # throughput_ratio = self.sla_throughput / (pod_throughput+1)

        #用latency计算reward
        latency_ratio = latency / self.sla_latency
        pod_number = sum(sum(pod_states[i]) for i in range(len(pod_states)))

        if pod_number == 1 and latency_ratio <= 1:
            return reward_max
        elif latency_ratio > 5:
            return reward_min

        pod_reward = -10 / (self.MAX_PODS - 1) * pod_number \
            + 10 * self.MAX_PODS / (self.MAX_PODS - 1)
        reward += pod_weight * pod_reward

        #用throughput计算reward
        # throughout_ref_value = 1
        # if throughput_ratio < throughout_ref_value:
        #     throughput_reward = 10 * pow(math.e, -0.3 * d * throughput_ratio)
        # else:
        #     throughput_reward = 10 * pow(math.e, -10 * d * throughput_ratio)
        # reward += throughput_weight * throughput_reward

        #用latency计算reward
        latency_ref_value = 1
        if latency_ratio < latency_ref_value:
            throughput_reward = 10 * pow(math.e, -0.3 * d * latency_ratio)
        else:
            throughput_reward = 10 * pow(math.e, -10 * d * (latency_ratio - latency_ref_value))
        reward += throughput_weight * throughput_reward

        return reward

    def _take_action(self, config_idx, app_idx, cluster_idx, action, proxy_idx):
        #deploy the config_idx config of app_idx function on cluster_idx cluster
        if action == 2:
            #config_idx config of app_idx function already exists
            if self.curr_configs[app_idx][cluster_idx][config_idx] == 1:
                return
            self.curr_configs[app_idx][cluster_idx][config_idx] = 1
            self._create_action(config_idx, app_idx, cluster_idx, proxy_idx)
        #remove the config_idx config of app_idx function on cluster_idx cluster
        if action == 0:
            #config_idx config of app_idx function not exists
            if self.curr_configs[app_idx][cluster_idx][config_idx] == 0:
                return
            self.curr_configs[app_idx][cluster_idx][config_idx] = 0
            self._remove_action(config_idx, app_idx, cluster_idx, proxy_idx)
        #assign the config_idx of app_idx function on cluster_idx cluster to proxy_idx proxy
        if action == 1:
            self._no_action(config_idx, app_idx, cluster_idx, proxy_idx)


    def _encode_action(self, cluster_idx, change_idx, config_idx, proxy_idx, app_idx):
        """
        Encode the discrete action values in one single number.
        Clusters in {0, 1, 2}
        Change_idx, config_idx in {0, 1, 2}
        Proxy_idx in {0, 1, 2}
        App_idx in {0, 1, 2}
        """
        code = cluster_idx
        code *= 3
        code += change_idx
        code *= 3
        code += config_idx
        code *= 3
        code += proxy_idx
        code *= 3
        code += app_idx
        return code


    def _decode_action(self, i):
        out = []
        out.append(i % 3)
        i //= 3
        out.append(i % 3)
        i //= 3
        out.append(i % 3)
        i //= 3
        out.append(i % 3)
        i //= 3
        out.append(i)
        return list(reversed(out))

    def _remove_action(self, config_idx, app_idx, cluster_idx, proxy_idx):
        cluster = self.cluster_names[cluster_idx]
        #get cluster IP of pod to be removed
        sizes = ['s', 'm', 'l']
        #the name of deployment
        deploy_name = sizes[config_idx] + self.app_names[app_idx]
        #TO-DO: analyze returned content to get IP
        serviceIP = ""
        output = os.popen('kubectl get service -o wide --context=' + cluster).read()
        lines = output.split("\n")
        port=''
        which_app = len(deploy_name)
        for line in lines[:-1]:
            items = line.split()
            if items[0][:which_app] == deploy_name:
                serviceIP=items[2]+":"+items[4][:4]
        os.popen('kubectl delete deployment ' + deploy_name + ' --context=' + cluster)
        
        self._reconfig_proxy(app_idx, serviceIP, cluster_idx)
        return 

    def _reconfig_proxy(self, app_idx, ip, cluster_idx):
        newIps = self._get_ip(app_idx, cluster_idx)
        if len(newIps) > 0:
            for i in range(len(self.ip_proxy)):
                if i == 0 and app_idx == 0 and self.ip_proxy[i][app_idx] == ip:
                    self.ip_proxy[i][app_idx] = random.choice(newIps)
                    self._deploy_proxy(i)
                if i == 1 and app_idx == 0 and self.ip_proxy[i][app_idx+1] == ip:
                    self.ip_proxy[i][app_idx+1] = random.choice(newIps)
                    self._deploy_proxy(i)
                if i == 1 and app_idx == 1 and self.ip_proxy[i][app_idx-1] == ip:
                    self.ip_proxy[i][app_idx-1] = random.choice(newIps)
                    self._deploy_proxy(i)
                if i == 2 and app_idx <= 2 and self.ip_proxy[i][app_idx] == ip:
                    self.ip_proxy[i][app_idx] = random.choice(newIps)
                    self._deploy_proxy(i)




    def _create_action(self, config_idx, app_idx, cluster_idx, proxy_idx):
        cluster = self.cluster_names[cluster_idx]
        sizes = ['s', 'm', 'l']
        #the name of deployment file
        file_name = self.app_names[app_idx] + '-' + sizes[config_idx].upper() + '.yaml'
        os.popen('kubectl apply -f ' + self.config_path + file_name + ' --context=' + cluster)
        #TO-DO: analyze returned content to get IP
        sizes = ['s', 'm', 'l']
        #the name of deployment
        deploy_name = sizes[config_idx] + self.app_names[app_idx]
        #TO-DO: analyze returned content to get IP
        serviceIP = ""
        output = os.popen('kubectl get service -o wide --context=' + cluster).read()
        lines = output.split("\n")
        port=''
        which_app = len(deploy_name)
        for line in lines[:-1]:
            items = line.split()
            if items[0][:which_app] == deploy_name:
                serviceIP=items[2]+":"+items[4][:4]
        res = self._assign_proxy(serviceIP, app_idx, proxy_idx, cluster)
        return 

    def _assign_proxy(self, ip, app_idx, proxy_idx, cluster):
        if proxy_idx == 0 and app_idx == 0:
            self.ip_proxy[proxy_idx][app_idx] = ip
            self._deploy_proxy(proxy_idx)
        elif proxy_idx == 1 and app_idx == 0:
            self.ip_proxy[proxy_idx][app_idx+1] = ip
            self._deploy_proxy(proxy_idx)
        elif proxy_idx == 1 and app_idx == 1:
            self.ip_proxy[proxy_idx][app_idx-1] = ip
            self._deploy_proxy(proxy_idx)
        elif proxy_idx == 2 and app_idx <= 2:
            self.ip_proxy[proxy_idx][app_idx] = ip
            self._deploy_proxy(proxy_idx)
        #unreasonable conditions
        else:
            return -1
            
        #successful
        return 1


    def _no_action(self, config_idx, app_idx, cluster_idx, proxy_idx):
        cluster = self.cluster_names[cluster_idx]
        #get ip
        #TO-DO: analyze returned content to get IP
        sizes = ['s', 'm', 'l']
        #the name of deployment
        deploy_name = sizes[config_idx] + self.app_names[app_idx]
        serviceIP = ""
        output = os.popen('kubectl get service -o wide --context=' + cluster).read()
        lines = output.split("\n")
        port=''
        which_app = len(deploy_name)
        for line in lines[:-1]:
            items = line.split()
            if items[0][:which_app] == deploy_name:
                serviceIP=items[2]+":"+items[4][:4]
        res = self._assign_proxy(serviceIP, app_idx, proxy_idx, cluster)
        return res

    def _get_ip(self, app_idx, cluster_idx):
        ip = []
        sizes = ['s', 'm', 'l']
        for j in range(self.num_configs):
            if self.curr_configs[app_idx][cluster_idx][j] == 1:
                cluster = self.cluster_names[cluster_idx]
                #the name of deployment
                deploy_name = sizes[j] + self.app_names[app_idx]
                #TO-DO: analyze returned content to get IP
                serviceIP = ""
                output = os.popen('kubectl get service -o wide --context=' + cluster).read()
                lines = output.split("\n")
                port=''
                which_app = len(deploy_name)
                for line in lines[:-1]:
                    items = line.split()
                    if items[0][:which_app] == deploy_name:
                        serviceIP=items[2]+":"+items[4][:4]
                        ip.append(serviceIP)

        return ip

    def _remove_proxy(self, app_idx, cluster, ip):
        new_ip = self._get_ip(app_idx)
        proxys = set()
        if len(new_ip) > 0:
            for i in range(len(self.ip_proxy)):
                if i == 0 and app_idx == 0 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 1 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 2 and app_idx == 0 and self.ip_proxy[i][app_idx+1] in ip:
                    self.ip_proxy[i][app_idx+1] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 2 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 3 and app_idx < 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 4 and app_idx <= 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 0 and self.ip_proxy[i][app_idx+1] in ip:
                    self.ip_proxy[i][app_idx+1] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = random.choice(list(new_ip))
                    self._deploy_proxy(i, cluster)
        else:
            for i in range(len(self.ip_proxy)):
                if i == 0 and app_idx == 0 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 1 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 2 and app_idx == 0 and self.ip_proxy[i][app_idx+1] in ip:
                    self.ip_proxy[i][app_idx+1] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 2 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 3 and app_idx < 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 4 and app_idx <= 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 0 and self.ip_proxy[i][app_idx+1] in ip:
                    self.ip_proxy[i][app_idx+1] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 1 and self.ip_proxy[i][app_idx-1] in ip:
                    self.ip_proxy[i][app_idx-1] = "miss"
                    self._deploy_proxy(i, cluster)
                if i == 5 and app_idx == 2 and self.ip_proxy[i][app_idx] in ip:
                    self.ip_proxy[i][app_idx] = "miss"
                    self._deploy_proxy(i, cluster)
        
    #deploy the proxy_id proxy pod
    def _deploy_proxy(self, proxy_idx):
        newChain = []
        for idx in range(len(self.ip_proxy[proxy_idx])):
            #this chain is incomplete
            newChain.append('"-c",'+'"socks6://'+self.ip_proxy[proxy_idx][idx]+'",')
        
        newChain = ''.join(newChain)
        newChain = newChain[:-1]

        proxy_name = "proxy" + str(proxy_idx + 1)
        os.system("kubectl patch deployment " + proxy_name + " --namespace default --type='json' -p='[{'op': 'replace', 'path': '/spec/template/spec/containers/0/args', 'value': [" 
        + newChain + "]}] --context=" + self.proxy_cluster[proxy_idx])


    

    #function to get state
    def _get_state(self):
        #get cpu_states of all clusters
        cpu_states = []
        real_cpu = [[0,0,0], [0,0,0], [0,0,0]]
        for cluster_idx in range(self.num_cluster):
            cluster = self.cluster_names[cluster_idx]
            cpu = 0
            count = 0
            for app_idx in range(self.num_app):
                app = self.app_names[app_idx]
                aver_cpu = self._get_average_cpu(app, cluster)
                cpu += aver_cpu
                real_cpu[app_idx][cluster_idx] = aver_cpu
                if cpu > 0:
                    count += 1
            cpu_states.append(self._get_discrete(cpu/count * 100 if count > 0 else 0))
        
        #get number_of_pods in all clusters
        pod_states = []
        real_pod = [[0,0,0], [0,0,0], [0,0,0]]
        for cluster_idx in range(self.num_cluster):
            cluster = self.cluster_names[cluster_idx]
            num = 0
            for app_idx in range(self.num_app):
                app = self.app_names[app_idx]
                curr_num = self._get_pods_num(app, cluster)
                num += curr_num
                real_pod[app_idx][cluster_idx] = curr_num
            pod_states.append(self._get_discrete(100 * num / self.MAX_PODS))

        
        #get placement_of_pods in all clusters
        placement = []
        present = []
        for app in self.app_names:
            present = self._get_placement(app, self.cluster_names)
            placement.append(self._get_discrete_place(present))

        #get latency
        # latency = self._get_discrete(100 * self._query_latency(self.sla_latency_metric_name) / self.sla_latency)
        latency = random.uniform(20,30) # For debug environ
        d_latency = self._get_discrete(100 * random.uniform(20,30) / self.sla_latency) 

        if math.isnan(latency):
            latency = self.sla_latency

        #define real observation
        real_observation = [
            real_cpu,
            # pod_states,
            real_pod,
            present,
            latency
        ]

        #encode each metric
        #return encoded state
        encoded_observation = self.encode(
            cpu_states,
            pod_states,
            placement,
            d_latency
        )

        return encoded_observation, real_observation
    
    #function to get state
    def _get_state_max_latency(self):
        #get cpu_states of all clusters
        cpu_states = []
        real_cpu = [[0,0,0], [0,0,0], [0,0,0]]
        for cluster_idx in range(self.num_cluster):
            cluster = self.cluster_names[cluster_idx]
            cpu = 0
            count = 0
            for app_idx in range(self.num_app):
                app = self.app_names[app_idx]
                aver_cpu = self._get_average_cpu(app, cluster)
                cpu += aver_cpu
                real_cpu[app_idx][cluster_idx] = aver_cpu
                if cpu > 0:
                    count += 1
            cpu_states.append(self._get_discrete(cpu/count * 100 if count > 0 else 0))
        
        #get number_of_pods in all clusters
        pod_states = []
        real_pod = [[0,0,0], [0,0,0], [0,0,0]]
        for cluster_idx in range(self.num_cluster):
            cluster = self.cluster_names[cluster_idx]
            num = 0
            for app_idx in range(self.num_app):
                app = self.app_names[app_idx]
                curr_num = self._get_pods_num(app, cluster)
                num += curr_num
                real_pod[app_idx][cluster_idx] = curr_num
            pod_states.append(self._get_discrete(100 * num / self.MAX_PODS))

        
        #get placement_of_pods in all clusters
        placement = []
        present = []
        for app in self.app_names:
            present = self._get_placement(app, self.cluster_names)
            placement.append(self._get_discrete_place(present))

        #get latency
        # latency = self._get_discrete(100 * self._query_latency(self.sla_latency_metric_name) / self.sla_latency)
        latency = 30
        d_latency = self._get_discrete(100 * 30 / self.sla_latency) # max latency 

        if math.isnan(latency):
            latency = self.sla_latency

        #define real observation
        real_observation = [
            real_cpu,
            # pod_states,
            real_pod,
            placement,
            latency
        ]

        #encode each metric
        #return encoded state
        encoded_observation = self.encode(
            cpu_states,
            pod_states,
            placement,
            d_latency
        )

        return encoded_observation, real_observation
    
    #get average_cpu for all pods with app_name on cluster with cluster
    #return 0.xx
    def _get_average_cpu(self, app_name, cluster):
        aver_cpu = 0
        #obtain from metric server and calculate
        output = os.popen('kubectl top pod --context=' + cluster).read()
        lines = output.split("\n")
        numPods = 0
        cpuUsage = 0
        cpuReqs = self.app_dict[app_name]
        for line in lines[1:-1]:
            items = line.split()
            idx = items[0].index('-')
            if items[0][1:idx] == app_name:
                numPods += 1
                cpuUsage += int(items[1][:-1])
        aver_cpu = cpuUsage / (numPods * cpuReqs) if numPods > 0 else 0.0
        # return numPods, cpuUsage / (numPods * cpuReqs)
        return aver_cpu
    
    #get number of active pods with app_name on cluster with cluster
    def _get_pods_num(self, app_name, cluster):
        #first judge if there exists app_name pod on cluster-x through kubectl get command; if not, return 0
        #obtain from metric server
        output = os.popen('kubectl top pod --context=' + cluster).read()
        lines = output.split("\n")
        numPods = 0
        for line in lines[1:-1]:
            items = line.split()
            idx = items[0].index('-')
            if items[0][1:idx] == app_name:
                numPods += 1
        return numPods
    
    #get the index of allocated clusters with active pod
    def _get_placement(self, app_name, clusters):
        #use _get_pods_num to calculate number on each cluster and output
        present = [0 for _ in range(len(clusters))]
        for i in range(len(clusters)):
            num = self._get_pods_num(app_name, clusters[i])
            present[i] = 1 if num > 0 else 0
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
            tmp[cpu-1] = 1
            state += tmp[:]
        
        for pod in pods:
            tmp = [0 for _ in range(6)]
            tmp[pod-1] = 1
            state += tmp[:]
        
        for place in places:
            tmp = [0 for _ in range(2 ** self.num_cluster)]
            tmp[place-1] = 1
            state += tmp[:]
        
        tmp = [0 for _ in range(7)]
        tmp[latency-1] = 1
        state += tmp[:]

        return state

    #Not used
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
