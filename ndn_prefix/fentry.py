import re

class Fentry():
	def __init__(self, prefix, domain):
		self.prefix = prefix
		self.domain = domain
	def get_prefix(self):
		return self.prefix
	def get_domain(self):
		return self.domain
	def __str__(self):
		output = "prefix: "
		output += self.get_prefix()
		output += "\ndomain: " + self.get_domain() + "\n"
		return output
