#!/usr/bin/env python3

from http.server import *
from subprocess import *
import queue
import threading
import shlex
import io
import json
import multiprocessing

langtb = {
	"cpp" : "g++ -x c++ -o {} -",
}

def diff(a, b):
	return a != b

class Problem:
	def __init__(self, data_set, bufsize = 10240, run_time_limit = 1):
		self.data_set = data_set
		self.bufsize = bufsize
		self.run_time_limit = run_time_limit
		self.diff = diff

q = queue.Queue()

def worker():
	import subprocess
	tid = threading.get_ident()
	while True:
		try:
			obj = q.get()
			proc = Popen(
				shlex.split(langtb[obj["lang"]].format(tid)),
				stdin=PIPE,
				stdout=DEVNULL,
				stderr=PIPE,
			)
			out, err = proc.communicate(obj["src"].encode(), 10)
			if proc.returncode != 0:
				print("{}:\n{}".format(CE, err.decode()))
			else:
				prob = probtb.get(obj["pid"])
				for din, dout in prob.data_set:
					proc = Popen(
						shlex.split('./'+str(tid)),
						bufsize=prob.bufsize,
						stdin=PIPE,
						stdout=PIPE,
						stderr=DEVNULL,
					)
					out, err = proc.communicate(din.encode(), prob.run_time_limit)
					if prob.diff(out.decode(), dout):
						print(WA)
						break
				else:
					print(AC)
		except subprocess.TimeoutExpired:
			proc.kill()
			print(TLE)
		except Exception as e:
			print(e)
		finally:
			call(shlex.split('rm -f '+str(tid)))
			q.task_done()

class OJRequestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		data = self.rfile.read(int(self.headers['content-length'])).decode()
		obj = json.loads(data)
		self.send_response(200)
		self.end_headers()
		if self.is_valid(obj):
			q.put(obj)
			self.wfile.write(("1").encode())
		else:
			self.wfile.write(("0").encode())

	def is_valid(self, obj):
		return "pid" in obj and "lang" in obj and "src" in obj and obj["pid"] in probtb and obj["lang"] in langtb

probtb = {
	"0" : Problem([("1 2\n", "3\n"), ("4 5\n", "9\n")])
}

AC = "Accept"
WA = "Wrong Answer"
TLE = "Time Limit Exceeded"
CE = "Compile Error"

print("Problem ids:", list(probtb.keys()))
print("Supported languages:", list(langtb.keys()))

for i in range(multiprocessing.cpu_count()):
	threading.Thread(target=worker, daemon=True).start()

HTTPServer(('0.0.0.0', 80), OJRequestHandler).serve_forever()
