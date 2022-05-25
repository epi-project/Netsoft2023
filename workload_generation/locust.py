from locust import HttpUser, task
from subprocess import call

class DemoUser(HttpUser):
	@task
	def user_request(self):
		call("./socksx/socksx-py/examples/client.py", shell=True)

