from pydantic import BaseModel


class DashboardTrendSeries(BaseModel):
    name: str
    data: list[int]


class DashboardDonutMetric(BaseModel):
    label: str
    value: int


class DashboardSummary(BaseModel):
    total_clients: int
    total_contacts: int
    total_documents: int
    total_requests: int
    recent_priorities: list[str]
    trend_labels: list[str]
    trend_series: list[DashboardTrendSeries]
    donut_metrics: list[DashboardDonutMetric]
