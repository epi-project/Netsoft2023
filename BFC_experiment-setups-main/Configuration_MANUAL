#Use case 1 - The EHR:

#The configurations:

#1.1. The clusters' connection: 
#cluster 1 and cluster 2 are only considered for placement
#To connect or disconnect a cluster, you can use the following command
cilium clustermesh connect --context $CLUSTER1 --destination-context $CLUSTER3
cilium clustermesh disconnect --context $CLUSTER1 --destination-context $CLUSTER3
#Add artificial delay to simulate the real environment of distributed clusters
sudo tc qdisc add dev cilium_host root netem delay 5ms
#1.2. The function's configurations:
#The request/limit CPUs of each function are configured in the yaml file to be 100/150m.
#Initially, we will have two proxies running: 
#Proxy 1 on jk-02, IP 145.100.135.43:30007: 
sudo kubectl apply -f proxy1.yaml --context=$CLUSTER1
#Proxy 2 on jk-04, IP 145.100.135.56:30007:
sudo kubectl apply -f proxy2.yaml --context=$CLUSTER2
#The functions requested with this use case are:
#The firewall on proxy 1 (traffic from a client running on cluster 1 to a server running on cluster 2)
#Encrypt on proxy 2 (traffic from a client running on cluster 2 to the server running on cluster 1)
#So we run the workload generator of clients on jk-02 (145.100.135.43), to connect to a server running on jk-04 (145.100.135.56) via proxy 1:
sudo locust -f ./locust.py --headless -u 10 -r 10 -H 145.100.135.56
socat -  TCP-LISTEN:30020,fork
#And we run the workload generator of clients also on jk-04, to connect to another server running on jk-02 via proxy 2:
sudo locust -f ./locust.py --headless -u 10 -r 10 -H 145.100.135.56
socat -  TCP-LISTEN:30020,fork
#1.3. The experiments: 
#In the first use case, the send rate is minimal (100kb/s) (edit client code to have that) 
#The number of clients can go up to 100 clients (or 500, if we don't see a lot of resource consumption)
#We run both locust work generators (and servers) on jk-02 and jk-4 at the same time.
#We use a tool to capture traffic and check the throughput, ex:
sudo tcpdump -i any port 30020
#Collect latency: latencyall = latencycluster1-to-2 + latencycluster2-to-1
#Collect the number of pods and CPU usage: Query on each cluster the number of pods on each one and the CPU utilised.
#Gradually increase the number of clients by 10, with every new iteration and collect metrics
#1.4. The "no-strategy" metrics: 
#In an effort to compare the results, we collect with a default state of "no strategy"
#We manually place a small and large configured firewall and encrypt on cluster 1
#We configure proxy 1 and 2 to go through these functions as before 
#We also run a proxy 0 (which will not chain anything) 
#We run the same experiments with exactly the same set-up except that we don't use the framework to adapt the placement
#Throughput metric: static small configuration handling increasing requests vs our adaptive placement
#Latency: the latency of proxy 0 (no chain) vs latencyall
#CPU and number of pods: compared to large configured function, how much CPU has been utilised (did we minimise CPU wastage?)
#1.5. The expectation output: 
#The throughput would flatline with the no-strategy compared to our approach that will keep increasing
# but not with this use case because the traffic is minimal. Maybe more apparent with the streaming use case.
#The latency overhead is minimal: latencyall - latencyproxy0 ~ 0 ms  
#A lot of CPU goes utilised compared to over approach that assigns requests to the same instance to minimise wastage. 
#Use case 2 - The ML sharing:

#2. The differences:

#2.1. The clusters' connection: 
# Clusters are all connected.
#Add artificial delay to simulate the real environment of distributed clusters, so run on both masters nodes:
sudo tc qdisc add dev cilium_host root netem delay 5ms
#2.2. The function's configurations:
# Here we have a third proxy (proxy 3 on cluster 3), running on jk-07 145.100.135.73:30007
#two clients running on jk-07 145.100.135.73, one client connecting to server on jk-02, and one connecting to server jk-04 
#Similarly, two servers also running on jk-07 to receive traffic from clients running on jk-02 and jk-04 (kind of dumb, I know) 
#This is done simultaneously.
#Collect latency: latencyall = latencycluster1-to-3 + latencycluster3-to-1  or latencycluster2-to-3 + latencycluster3-to-2  (worst value)
#We need to place firewall on proxy 3 
#We need to place encrypt on proxy 1
#We need to place encrypt on proxy 2

#Everything else is the same

#Use case 3 - The streaming:

#3. The differences:

#3.1. The clusters' connection: 
#The clusters' connection is the same as the first use case
#2.2. The function's configurations:
#place firewall then encrypt on proxy 1
#place firewall then encrypt on proxy 2
#3.3. The experiments: 
#Instead of 100kb/s it is 1Mb/s to simulate the streaming sending rate.
#Everything else is the same as the first use case
