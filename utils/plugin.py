# -*- coding: utf-8 -*-
import collections
import os
import hashlib

from utils import tool


HelpMessage = collections.namedtuple('HelpMessage', 'prefix message plugin_name')


class Plugin:
	def __init__(self, server, file_path):
		self.server = server
		self.file_path = file_path
		self.file_name = os.path.basename(file_path)
		self.plugin_name = tool.remove_suffix(self.file_name, '.py')
		self.module = None
		self.old_module = None
		self.help_messages = []
		self.file_hash = None
		self.thread_pool = self.server.plugin_manager.thread_pool

	def call(self, func_name, args=()):
		if hasattr(self.module, func_name):
			func = self.module.__dict__[func_name]
			if callable(func):
				return self.thread_pool.add_task(func, args, func_name, self)
		return None

	def load(self):
		self.old_module = self.module
		self.module = tool.load_source(self.file_path)
		self.help_messages = []
		self.file_hash = self.get_file_hash()
		self.server.logger.debug('Plugin {} loaded, file sha256 = {}'.format(self.file_path, self.file_hash))

	# on_load event sometimes cannot be called right after plugin gets loaded, so here's its separated method for the call
	def call_on_load(self):
		self.call('on_load', (self.server.server_interface, self.old_module))

	def unload(self):
		self.call('on_unload', (self.server.server_interface, ))

	def add_help_message(self, prefix, message):
		self.help_messages.append(HelpMessage(prefix, message, self.file_name))
		self.server.logger.debug('Plugin Added help message "{}: {}"'.format(prefix, message))

	def get_file_hash(self):
		if os.path.isfile(self.file_path):
			with open(self.file_path, 'rb') as file:
				return hashlib.sha256(file.read()).hexdigest()
		else:
			return None

	def file_changed(self):
		return self.get_file_hash() != self.file_hash

