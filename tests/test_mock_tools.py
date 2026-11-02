import json
from app.servers.logs import search_logs, get_error_details
from app.servers.database import get_db_metrics, get_slow_queries
from app.servers.kubernetes import get_pod_status, get_deployment_status
from app.servers.github import get_recent_commits, get_open_incidents

def test_logs_search():
    result=json.loads(search_logs("payment-service",level="ERROR"))
    assert result["count"]==2 and all(x["level"]=="ERROR" for x in result["logs"])

def test_trace_lookup():
    assert json.loads(get_error_details("tr-1001"))["found"] is True

def test_db_pool_saturated():
    result=json.loads(get_db_metrics("payment-service"))
    assert result["connection_utilization_percent"]==100 and result["pool_waiters"]==37

def test_slow_queries():
    assert json.loads(get_slow_queries("payment-service"))["queries"]

def test_kubernetes_pod_not_ready():
    assert any(x["ready"]=="0/1" for x in json.loads(get_pod_status("payment-service"))["pods"])

def test_deployment_degraded():
    assert json.loads(get_deployment_status("payment-service"))["unavailable_replicas"]==1

def test_github_mock_data():
    assert json.loads(get_recent_commits("adm-l/demo"))["commits"]
    assert json.loads(get_open_incidents("payment-service"))["incidents"]
