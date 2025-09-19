import requests


class SimClient:
    def __init__(self, base_url, token, tenant_id):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json",
        }

    def create_simulation(self, config):
        return requests.post(
            f"{self.base_url}/api/v1/simulations",
            headers=self.headers,
            json={"tenant_id": self.headers["X-Tenant-ID"], "config": config},
        ).json()

    def fetch_simulation(self, sim_id):
        return requests.get(
            f"{self.base_url}/api/v1/simulations/{sim_id}", headers=self.headers
        ).json()

    def terminate_simulation(self, sim_id):
        return requests.post(
            f"{self.base_url}/api/v1/simulations/{sim_id}/terminate",
            headers=self.headers,
        ).json()

    def post_event(self, sim_id, actor, action, metadata):
        return requests.post(
            f"{self.base_url}/api/v1/simulations/{sim_id}/events",
            headers=self.headers,
            json={"actor": actor, "action": action, "metadata": metadata},
        ).json()

    def post_memory(self, sim_id, event_id, tags, rolling_stats):
        return requests.post(
            f"{self.base_url}/api/v1/simulations/{sim_id}/memories",
            headers=self.headers,
            json={"event_id": event_id, "tags": tags, "rolling_stats": rolling_stats},
        ).json()

    def get_narrative(self, sim_id):
        return requests.get(
            f"{self.base_url}/api/v1/simulations/{sim_id}/narrative",
            headers=self.headers,
        ).json()

    def generate_highlights(self, sim_id, criteria):
        return requests.post(
            f"{self.base_url}/api/v1/simulations/{sim_id}/narrative/highlights",
            headers=self.headers,
            json={"criteria": criteria},
        ).json()

    def get_stats(self, sim_id):
        return requests.get(
            f"{self.base_url}/api/v1/simulations/{sim_id}/stats", headers=self.headers
        ).json()

    def query_memories(self, sim_id, filter_query):
        return requests.get(
            f"{self.base_url}/api/v1/simulations/{sim_id}/memories?filter={filter_query}",
            headers=self.headers,
        ).json()
