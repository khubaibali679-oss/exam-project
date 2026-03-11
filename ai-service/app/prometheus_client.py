import requests
import pandas as pd
from app.config import PROMETHEUS_URL, WORKLOAD_NAME, NAMESPACE


def query_prometheus(query: str):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=20
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["result"]


def query_prometheus_range(query: str, start: str, end: str, step: str = "5m"):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query_range",
        params={
            "query": query,
            "start": start,
            "end": end,
            "step": step
        },
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["result"]


def get_current_cpu_millicores():
    query = f'''
    sum(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}", pod=~"{WORKLOAD_NAME}.*", container!="POD", container!=""}}[5m])) * 1000
    '''
    result = query_prometheus(query)
    if not result:
        return 0.0
    return float(result[0]["value"][1])


def get_current_memory_mib():
    query = f'''
    sum(container_memory_working_set_bytes{{namespace="{NAMESPACE}", pod=~"{WORKLOAD_NAME}.*", container!="POD", container!=""}}) / 1024 / 1024
    '''
    result = query_prometheus(query)
    if not result:
        return 0.0
    return float(result[0]["value"][1])


def get_current_replicas():
    query = f'''
    kube_deployment_status_replicas{{namespace="{NAMESPACE}", deployment="{WORKLOAD_NAME}"}}
    '''
    result = query_prometheus(query)
    if not result:
        return 1
    return int(float(result[0]["value"][1]))


def get_cpu_timeseries(start: str, end: str, step: str = "5m") -> pd.DataFrame:
    query = f'''
    sum(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}", pod=~"{WORKLOAD_NAME}.*", container!="POD", container!=""}}[5m])) * 1000
    '''
    result = query_prometheus_range(query, start, end, step)
    if not result:
        return pd.DataFrame(columns=["ds", "y"])

    values = result[0]["values"]
    df = pd.DataFrame(values, columns=["timestamp", "y"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["y"] = df["y"].astype(float)
    df.rename(columns={"timestamp": "ds"}, inplace=True)
    return df


def get_memory_timeseries(start: str, end: str, step: str = "5m") -> pd.DataFrame:
    query = f'''
    sum(container_memory_working_set_bytes{{namespace="{NAMESPACE}", pod=~"{WORKLOAD_NAME}.*", container!="POD", container!=""}}) / 1024 / 1024
    '''
    result = query_prometheus_range(query, start, end, step)
    if not result:
        return pd.DataFrame(columns=["ds", "y"])

    values = result[0]["values"]
    df = pd.DataFrame(values, columns=["timestamp", "y"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["y"] = df["y"].astype(float)
    df.rename(columns={"timestamp": "ds"}, inplace=True)
    return df
