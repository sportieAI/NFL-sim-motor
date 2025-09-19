from fastapi import Request
from api.rbac import get_payload_from_request


def serve_dashboard(request: Request):
    try:
        payload = get_payload_from_request(request)
        # TODO: Implement dashboard logic
        return {"status": "dashboard placeholder"}
    except Exception:
        return {"error": "Dashboard not available"}
