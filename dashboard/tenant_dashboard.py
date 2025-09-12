from fastapi import Request
from api.rbac import get_payload_from_request, has_permission

def serve_dashboard(request: Request):
    try:
        payload = get_payload_from_request(request)
    except Exception as e:
        print(f"Error: {e}")
