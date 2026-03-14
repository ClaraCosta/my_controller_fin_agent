from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_clients: int
    total_contacts: int
    total_requests: int
    recent_priorities: list[str]

