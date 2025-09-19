from fastapi import Request
from api.rbac import get_payload_from_request, has_permission


def serve_dashboard(request: Request):
    try:
        payload = get_payload_from_request(request)
        # TODO: Complete dashboard implementation
        return {"status": "Dashboard placeholder"}
    except Exception as e:
        return {"error": str(e)}
