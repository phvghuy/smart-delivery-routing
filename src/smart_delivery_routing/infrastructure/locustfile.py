from locust import HttpUser, task, constant_pacing

class DeliveryUser(HttpUser):
    token = None
    wait_time = constant_pacing(3)

    def on_start(self):
        if DeliveryUser.token is None:
            response = self.client.post("/auth/login", json={
                "email": "admin@sdr.com",
                "password": "admin"
            })
            DeliveryUser.token = response.json()["access_token"]

    @task
    def get_health(self):
        self.client.get("/health")

    @task
    def get_shipping_requests(self):
        self.client.get("/shipping-requests", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task
    def get_parcels(self):
        self.client.get("/parcels", headers={
            "Authorization": f"Bearer {self.token}"
        })
