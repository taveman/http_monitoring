# http_monitoring
### Repository includes the following code structure:

* monitoring - client application that collects metrics from the target service
* server - client server for testing purpose
 
### How to run tests

Run the following:

```bash
docker-compose run monitoring bash -c "pytest /app/tests"
```

### How to run client

```bash
docker-compose up --force-recreate --build
```


## Notice:

Speed can be improved by changing the workflow as follows:
We could collect all the metrics we get from target urls and send them in a batch to the write-metric endpoint. 
Depends on the needs.

### Current metrics:
These timings are taken under the following condition:

- 300 uniq paths
- Intel(R) Core(TM) i7-9850H CPU @ 2.60GHz

```bash
monitoring_1  | DEBUG    | 2021-02-22 07:18:23,988 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:25,068 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:26,235 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:27,324 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:28,467 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:29,543 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247
monitoring_1  | DEBUG    | 2021-02-22 07:18:30,567 | monitoring | PID 8        | service_communicator | MainThread: ServiceCommunicator: getting metrics from http://server:8000/metrics/33247

``` 