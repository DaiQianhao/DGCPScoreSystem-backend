import json
import logging
import random
import threading

import pymysql as sql
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_cors import CORS



class Server(threading.Thread):
	def __init__(self, logger: logging.Logger):
		super().__init__()
		self.app = Flask("Server")
		self.setDaemon(True)
		self.name = "Server"
		self.tokens = {}
		self.logger = logger
		self.__chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
		              't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
		              'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
		              '5', '6', '7', '8', '9']
		self.__ua = "Get Score System Pro"
		self.scores = {}
		self.lock = threading.Lock()
		self.cursor_lock = threading.Lock()
		self.conn = sql.connect('localhost', 'root', 'abcd1234', 'scoresystem')
		self.cursor = self.conn.cursor()
		CORS(self.app, resources={r"/*": {"origins": "*"}})

		@self.app.route("/api/login", methods=["POST"])
		def login():
			uid = request.json.get("uid")
			if uid is None:
				return json.dumps({"code": 1, "msg": "缺少uid参数"})
			password = request.json.get("password")
			if password is None:
				return json.dumps({"code": 1, "msg": "缺少password参数"})
			return self.login(uid, password)

		@self.app.route("/api/getScore", methods=["GET"])
		def get_score():
			token = request.values.get("token")
			if token is None:
				return json.dumps({"code": 1, "msg": "缺少token参数"})
			self.logger.info(token)
			return self.get_score(token)

	def run(self) -> None:
		self.app.run("0.0.0.0", 44444)

	def login(self, uid: str, password: str):
		try:
			response = requests.post("http://www.dgcz.cn/jjwtMobile/login.htm", headers={"User-Agent": self.__ua}, data={"username": uid, "password": password}, allow_redirects=False)
		except Exception:
			self.logger.error("Error when user [{0}] logging".format(uid), exc_info=True)
			return json.dumps({"code": -1, "msg": "学校服务器爆炸了, 请重试"})

		self.logger.debug("user [{0}] is logging".format(uid))
		if response.status_code == 302:
			if response.url != "http://www.dgcz.cn/jjwtMobile/CasmCenter/login.jsp":
				self.clear_token_from_uid(uid)
				token = self.create_token(32)
				username = self.get_username_from_sid(response.cookies["JSESSIONID"])

				self.lock.acquire()
				self.tokens[token] = {}
				self.tokens[token]["sid"] = response.cookies["JSESSIONID"]
				self.tokens[token]["uid"] = uid
				self.tokens[token]["username"] = username
				self.lock.release()

				return_result = {"code": 0, "token": token, "username": username, "uid": uid, "sid": response.cookies["JSESSIONID"]}
				self.logger.debug("user [{0}] logged success, sid:[{1}], token:[{2}]".format(uid, response.cookies["JSESSIONID"], token))
			else:
				self.logger.debug("user [{0}] logged failed, reason: 'UidOrPasswordError'".format(uid))
				return_result = {"code": 1, "msg": "账号或密码错误"}
		else:
			self.logger.warning("user [{0}] logged failed, reason: 'StatusCodeError', StatusCode:[{1}]".format(uid, response.status_code))
			return_result = {"code": -1, "msg": "学校服务器爆炸了, 请重试, 状态码:" + str(response.status_code)}
		return json.dumps(return_result), 200

	def get_score(self, token):
		if token not in self.tokens:
			return json.dumps({"code": 10, "msg": "登录信息失效，请重新登录"})
		self.lock.acquire()
		sid = self.tokens[token]["sid"]
		self.lock.release()
		validity = self.check_sid_validity(sid)
		if validity["success"] is True and validity["valid"] is not True:
			return json.dumps({"code": 10, "msg": "登录信息失效，请重新登录"})

		scores = {"code": 0, "exams": {}}
		grade = self.tokens[token]["uid"][0:4]
		self.cursor_lock.acquire()
		self.cursor.execute("SELECT * FROM `exams` WHERE `grade`=" + grade)
		rows = self.cursor.fetchall()
		for row in rows:
			examid = row[3]
			self.cursor.execute("SELECT * FROM `" + grade + "-" + str(row[3]) + "` where `id`=" + self.tokens[token]["uid"])
			rows2 = self.cursor.fetchone()
			print(rows2)
			scores["exams"][examid] = {}
			scores["exams"][examid]["examinfo"] = {}
			scores["exams"][examid]["examinfo"]["name"] = row[1]
			scores["exams"][examid]["scores"] = {}
			if rows2[4] != -1:  # chinese
				scores["exams"][examid]["scores"]["chinese"] = {"score": rows2[4], "rank": rows2[5]}
			if rows2[6] != -1:  # maths
				scores["exams"][examid]["scores"]["maths"] = {"score": rows2[6], "rank": rows2[7]}
			if rows2[8] != -1:  # english
				scores["exams"][examid]["scores"]["english"] = {"score": rows2[8], "rank": rows2[9]}
			if rows2[10] != -1:  # physics
				scores["exams"][examid]["scores"]["physics"] = {"score": rows2[10], "rank": rows2[11]}
			if rows2[12] != -1:  # history
				scores["exams"][examid]["scores"]["history"] = {"score": rows2[12], "rank": rows2[13]}
			if rows2[14] != -1:  # chemistry
				scores["exams"][examid]["scores"]["chemistry"] = {"score": rows2[14], "rank": rows2[15]}
			if rows2[16] != -1:  # geography
				scores["exams"][examid]["scores"]["geography"] = {"score": rows2[16], "rank": rows2[17]}
			if rows2[18] != -1:  # biology
				scores["exams"][examid]["scores"]["biology"] = {"score": rows2[18], "rank": rows2[19]}
			if rows2[20] != -1:  # politics
				scores["exams"][examid]["scores"]["politics"] = {"score": rows2[20], "rank": rows2[21]}
			if rows2[22] != -1:  # pe
				scores["exams"][examid]["scores"]["pe"] = {"score": rows2[22], "rank": rows2[23]}
			if rows2[24] != -1:  # music
				scores["exams"][examid]["scores"]["music"] = {"score": rows2[24], "rank": rows2[25]}
			if rows2[26] != -1:  # art
				scores["exams"][examid]["scores"]["art"] = {"score": rows2[26], "rank": rows2[27]}
			if rows2[28] != -1:  # computer
				scores["exams"][examid]["scores"]["computer"] = {"score": rows2[28], "rank": rows2[29]}
			if rows2[30] != -1:
				scores["exams"][examid]["scores"]["special"] = {"total": rows2[30], "grade_rank": rows2[31]}
		self.cursor_lock.release()
		self.logger.debug(self.tokens[token]["username"] + "'s result " + json.dumps(scores))
		return json.dumps(scores)

	def get_username_from_sid(self, sid: str) -> str:
		response = requests.get("http://www.dgcz.cn/jjwtMobile/CasmCenter/main.jsp", headers={"User-Agent": self.__ua, "Cookie": "JSESSIONID=" + sid})
		soup = BeautifulSoup(response.text, 'html.parser')
		return soup.find("a").text.strip()

	def clear_token_from_uid(self, uid: str) -> bool:
		self.lock.acquire()
		for (k, v) in self.tokens.items():
			if v["uid"] == uid:
				del(self.tokens[k])
				self.lock.release()
				return True
		self.lock.release()
		return False

	def check_sid_validity(self, sid: str) -> dict:
		try:
			response = requests.post("http://www.dgcz.cn/jjwtMobile/role.htm", headers={"User-Agent": self.__ua, "Cookie": "JSESSIONID=" + sid}, allow_redirects=False)
		except Exception:
			self.logger.error("Error when check sid[{0}] validity".format(sid), exc_info=True)
			return {"successs": False}
		if response.status_code == 302:
			if response.url != "/jjwtMobile/CasmCenter/login.jsp":
				return {"success": True, "valid": True}
			else:
				return {"success": True, "valid": False}
		else:
			self.logger.warning("check sid validity failed, reason: 'StatusCodeError', StatusCode:[{1}]".format(sid, response.status_code))
			return {"success": False, "response": response}

	def create_token(self, length: int) -> str:
		result = ""
		for i in range(length):
			result += random.choice(self.__chars)
		return result


class Console():
	def __init__(self, server, logger: logging.Logger):
		self.logger = logger
		self.server = server
		self.debug = False

	def run(self) -> None:
		while True:
			cmd = input(">>> ")
			try:
				self.progress_cmd(cmd)
			except Exception as ex:
				self.logger.error("Error when execute command [" + cmd + "]", exc_info=True)

	def save(self, args):
		def print_help():
			print("dump all - 导出所有")
			print("dump tokens - 导出登录信息")
			print("加' --console'将打印到控制台")

		def get_tokens():
			self.server.lock.acquire()
			result = self.server.tokens
			self.server.lock.release()
			return result

		nya = args.copy()
		if "--console" in nya:
			nya.remove("--console")
		if len(nya) == 0:
			print_help()
		else:
			if args[0] == "tokens":
				if "--console" in args:
					print("=======tokens========")
					print(json.dumps(get_tokens(), ensure_ascii=False))
					print("=====================")

	def progress_cmd(self, cmd: str):
		args = cmd.split(" ")
		cmd = args[0]
		if len(args) > 1:
			args = args[1:len(args)]
		else:
			args = []
		if cmd == "dump":
			self.save(args)
		elif cmd == "error":
			raise Exception("A error")
		elif cmd == "debug":
			self.debug = False if self.debug else True
			self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
			self.logger.debug("Debug mode on" if self.debug else "Debug mode off")
		elif cmd == "exit":
			self.server.conn.close()
			exit(0)


if __name__ == "__main__":
	logger = logging.getLogger("My")
	console_handler = logging.StreamHandler()
	file_handler = logging.FileHandler("log.log", encoding="utf-8")
	console_handler.setLevel(logging.DEBUG)
	file_handler.setLevel(logging.INFO)
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	logger.setLevel(logging.INFO)

	s = Server(logger)
	s.start()
	console = Console(s, logger)
	console.run()
