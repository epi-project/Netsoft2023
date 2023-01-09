# EPI-kube-configuration
In this repository we add scaling techniques to the EPI framework setup to demonstrate scaling capabilities under stress test experiments.

## Deploying secvices; here we assume you have a kubernetes master and worker nodes running and configured
```shell
  $ cd EPI-services
  $ kubectl apply -f decrypt.yaml #BF1 = The decryption server
  $ kubectl apply -f encrypt.yaml #BF2 = The encryption server
  # cpu requests and limits in firewall.yaml are set with low numbers in experimental environments
  $ kubectl apply -f firewall.yaml #BF3 = The firewall server
  $ kubectl apply -f proxy.yaml #The SOCKS proxy
  $ kubectl apply -f socat.yaml #The end server
```

## Start the client script, refer to the epif-poc/socks-chaining repository 

```shell
  $ pipenv install click socksx
  $ pipenv shell
  $ cd Scripts
  $ locust -f ./locust.py --headless -u <number of clients> -r <spawn rate> -H <destination IP>
```

#### latency_collector folder:
1. to collect latency;
2. This folder can be run on any node to collect latency and expose to other nodes;

#### workload_generation folder:
1. to generate workloads;
2. This folder can be run on any node to transmit requests;

