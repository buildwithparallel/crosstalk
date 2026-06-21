# Crosstalk on Docker

A docker image is automatically built by GitHub actions, and can be downloaded from the GitHub container registry.

```
docker pull ghcr.io/buildwithparallel/crosstalk:latest
```

Additionally, an example [docker-compose.yml](../docker-compose.yml) is available.

The example automatically generates a new reticulum config file in the `crosstalk-config` volume. The Crosstalk database is also stored in this volume.
