# FastAPI, Prometheus & Grafana Monitoring Project

This project is a complete, self-contained example of how to monitor a Python FastAPI application using Prometheus for metrics collection and Grafana for visualization.

It also includes a simple shell-based load generator to create traffic, allowing you to see your dashboards light up with real-time data.

## Getting Started

## Requirements

- Python 3.13 or later

### Install Python using MiniConda

1. Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2. Create a new environment:
   ```bash
   conda create -n mini-rag python=3.8
3) Activate the environment:
    ```bash
    $ conda activate mini-rag
   
## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```
You only need to have `docker` and `docker-compose` installed on your machine. And then you can simply run:
```
docker-compose up server
```
to run the project and `docker-compose` will take care of the rest.

To view Grafana, head to `localhost:3000`, the username is `admin` and the password is `grafana`. If you wish to interface directly with Prometheus, go to `localhost:9090`. And the server is exposed over `localhost:8080`. You can find all these details [here](docker-compose.yml).


## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5020
```