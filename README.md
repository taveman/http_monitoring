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
