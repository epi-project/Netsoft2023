from locust import HttpUser, task
from subprocess import call

class DemoUser(HttpUser):
	@task
	def user_request(self):
		call("client.py", shell=True)

