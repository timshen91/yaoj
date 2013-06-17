#!/usr/bin/env python3

import urllib.request
import json
import sys

if len(sys.argv) < 3:
	print("usage: {} problem_id source_file".format(sys.argv[0]))
else:
	if urllib.request.urlopen(
		"http://127.0.0.1",
		data=json.dumps({
			"pid" : sys.argv[1],
			"lang" : sys.argv[2][sys.argv[2].rindex(".")+1:],
			"src" : open(sys.argv[2]).read(),
		}).encode()
	).read().decode() == "1":
		print("Submit succ")
	else:
		print("Submit fail")
