from pydantic import BaseModel
from typing import List, Optional


class CurrentMetricsResponse(BaseModel):
    workload: str
    namespace: str
    current_cpu_millicores: float
    current_memory_mib: float
    current_replicas: int


class ForecastResponse(BaseModel):
    workload: str
    forecast_points: List[float]
    unit: str = "millicores"


class RecommendationResponse(BaseModel):
    workload: str
    current_replicas: int
    recommended_replicas: int
    predicted_cpu_millicores: float
    predicted_cpu_per_pod_millicores: float
    action: str
    reason: str


class CostSummaryResponse(BaseModel):
    workload: str
    current_hourly_cost: float
    current_daily_cost: float
    current_monthly_cost: float
    optimized_hourly_cost: float
    optimized_daily_cost: float
    optimized_monthly_cost: float
    estimated_monthly_savings: float


class RightsizingResponse(BaseModel):
    workload: str
    avg_cpu_millicores: float
    requested_cpu_millicores: int
    recommended_cpu_request_millicores: int
    avg_memory_mib: float
    requested_memory_mib: int
    recommended_memory_request_mib: int
    cpu_status: str
    memory_status: str
