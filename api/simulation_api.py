from fastapi import FastAPI, Depends
from api.rbac import require_role

app = FastAPI()

@app.get("/dashboard", dependencies=[Depends(require_role(["admin", "analyst", "viewer"]))])
def dashboard_view(payload=Depends(require_role(["admin", "analyst", "viewer"]))):
    # payload contains user and tenant info
    return {"msg": f"Welcome, user {payload['sub']} from tenant {payload['tenant_id']}"}

@app.post("/run-simulation", dependencies=[Depends(require_role(["admin", "analyst"]))])
def run_simulation(payload=Depends(require_role(["admin", "analyst"]))):
    # Only admin or analyst can run this
    return {"msg": "Simulation started"}

@app.get("/manage-users", dependencies=[Depends(require_role(["admin"]))])
def manage_users(payload=Depends(require_role(["admin"]))):
    return {"msg": "User management portal"}