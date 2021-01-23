import hashlib
import json
import logging
import random
import threading

import pymysql as sql
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_cors import CORS


refresh_from_accounts = {"2020": ("2020000005", "abcd1234")}
create_exam_table = """CREATE TABLE `{0}-{1}` (
  `id` int NOT NULL,
  `grade` int NOT NULL,
  `class` int NOT NULL,
  `username` varchar(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `chinese_score` float DEFAULT NULL,
  `chinese_rank` int DEFAULT NULL,
  `maths_score` float DEFAULT NULL,
  `maths_rank` int DEFAULT NULL,
  `english_score` float DEFAULT NULL,
  `english_rank` int DEFAULT NULL,
  `physics_score` float DEFAULT NULL,
  `physics_rank` int DEFAULT NULL,
  `history_score` float DEFAULT NULL,
  `history_rank` int DEFAULT NULL,
  `chemistry_score` float DEFAULT NULL,
  `chemistry_rank` int DEFAULT NULL,
  `geography_score` float DEFAULT NULL,
  `geography_rank` int DEFAULT NULL,
  `biology_score` float DEFAULT NULL,
  `biology_rank` int DEFAULT NULL,
  `politics_score` float DEFAULT NULL,
  `politics_rank` int DEFAULT NULL,
  `pe_score` float DEFAULT NULL,
  `pe_rank` int DEFAULT NULL,
  `music_score` float DEFAULT NULL,
  `music_rank` int DEFAULT NULL,
  `art_score` float DEFAULT NULL,
  `art_rank` int DEFAULT NULL,
  `computer_score` float DEFAULT NULL,
  `computer_rank` int DEFAULT NULL,
  `total_score` float DEFAULT NULL,
  `grade_rank` int DEFAULT NULL,
  `class_rank` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `grade_UNIQUE` (`grade`),
  UNIQUE KEY `class_UNIQUE` (`class`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
exam_table_trigger = """CREATE DEFINER=`root`@`localhost` TRIGGER `{0}-{1}_BEFORE_INSERT` BEFORE INSERT ON `{0}-{1}` FOR EACH ROW BEGIN
    DECLARE done INT DEFAULT 0;
	DECLARE uid INT;
    DECLARE urank INT;
    DECLARE uscore INT;
    DECLARE unum INT;
    DECLARE uclass INT;
    DECLARE chinese_result CURSOR FOR SELECT `id`,`chinese_rank`,`chinese_score`,count(1) FROM `{0}-{1}` WHERE `chinese_score` <= new.chinese_score;
	DECLARE maths_result CURSOR FOR SELECT `id`,`maths_rank`,`maths_score`,count(1) FROM `{0}-{1}` WHERE `maths_score` <= new.maths_score;
	DECLARE english_result CURSOR FOR SELECT `id`,`english_rank`,`english_score`,count(1) FROM `{0}-{1}` WHERE `english_score` <= new.english_score;
	DECLARE physics_result CURSOR FOR SELECT `id`,`physics_rank`,`physics_score`,count(1) FROM `{0}-{1}` WHERE `physics_score` <= new.physics_score;
	DECLARE history_result CURSOR FOR SELECT `id`,`history_rank`,`history_score`,count(1) FROM `{0}-{1}` WHERE `history_score` <= new.history_score;
	DECLARE chemistry_result CURSOR FOR SELECT `id`,`chemistry_rank`,`chemistry_score`,count(1) FROM `{0}-{1}` WHERE `chemistry_score` <= new.chemistry_score;
	DECLARE geography_result CURSOR FOR SELECT `id`,`geography_rank`,`geography_score`,count(1) FROM `{0}-{1}` WHERE `geography_score` <= new.geography_score;
	DECLARE biology_result CURSOR FOR SELECT `id`,`biology_rank`,`biology_score`,count(1) FROM `{0}-{1}` WHERE `biology_score` <= new.biology_score;
	DECLARE politics_result CURSOR FOR SELECT `id`,`politics_rank`,`politics_score`,count(1) FROM `{0}-{1}` WHERE `politics_score` <= new.politics_score;
	DECLARE pe_result CURSOR FOR SELECT `id`,`pe_rank`,`pe_score`,count(1) FROM `{0}-{1}` WHERE `pe_score` <= new.pe_score;
	DECLARE music_result CURSOR FOR SELECT `id`,`music_rank`,`music_score`,count(1) FROM `{0}-{1}` WHERE `music_score` <= new.music_score;
	DECLARE art_result CURSOR FOR SELECT `id`,`art_rank`,`art_score`,count(1) FROM `{0}-{1}` WHERE `art_score` <= new.art_score;
	DECLARE computer_result CURSOR FOR SELECT `id`,`computer_rank`,`computer_score`,count(1) FROM `{0}-{1}` WHERE `computer_score` <= new.computer_score;
	DECLARE grade_result CURSOR FOR SELECT `id`,`grade_rank`,`total_score`,`class`,count(1) FROM `{0}-{1}` WHERE `total_score` <= new.total_score;
    
    set new.total_score = 0;
    
    if new.chinese_score is not null then
		set new.total_score = new.total_score + new.chinese_score;
        OPEN chinese_result;
			FETCH chinese_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `chinese_rank`,count(1) FROM `{0}-{1}` WHERE `chinese_rank` != -1 ORDER BY `chinese_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.chinese_rank = 1;
				else
					set new.chinese_rank = @r + 1;
				end if;
			else
				if uscore < new.chinese_score then
					flag_loop:loop
						FETCH chinese_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `chinese_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.chinese_rank = urank;
                end if;
			end if;
		CLOSE chinese_result;
	else
		set new.chinese_score = -1;
        set new.chinese_rank = -1;
	end if;
    
	if new.maths_score is not null then
		set new.total_score = new.total_score + new.maths_score;
        OPEN maths_result;
			FETCH maths_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `maths_rank`,count(1) FROM `{0}-{1}` WHERE `maths_rank` != -1 ORDER BY `maths_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.maths_rank = 1;
				else
					set new.maths_rank = @r + 1;
				end if;
			else
				if uscore < new.maths_score then
					flag_loop:loop
						FETCH maths_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `maths_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.maths_rank = urank;
                end if;
			end if;
		CLOSE maths_result;
	else
		set new.maths_score = -1;
        set new.maths_rank = -1;
	end if;
    
	if new.english_score is not null then
		set new.total_score = new.total_score + new.english_score;
        OPEN english_result;
			FETCH english_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `english_rank`,count(1) FROM `{0}-{1}` WHERE `english_rank` != -1 ORDER BY `english_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.english_rank = 1;
				else
					set new.english_rank = @r + 1;
				end if;
			else
				if uscore < new.english_score then
					flag_loop:loop
						FETCH english_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `english_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.english_rank = urank;
                end if;
			end if;
		CLOSE english_result;
	else
		set new.english_score = -1;
        set new.english_rank = -1;
	end if;
    
	if new.physics_score is not null then
		set new.total_score = new.total_score + new.physics_score;
        OPEN physics_result;
			FETCH physics_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `physics_rank`,count(1) FROM `{0}-{1}` WHERE `physics_rank` != -1 ORDER BY `physics_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.physics_rank = 1;
				else
					set new.physics_rank = @r + 1;
				end if;
			else
				if uscore < new.physics_score then
					flag_loop:loop
						FETCH physics_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `physics_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.physics_rank = urank;
                end if;
			end if;
		CLOSE physics_result;
	else
		set new.physics_score = -1;
        set new.physics_rank = -1;
	end if;
    
	if new.history_score is not null then
		set new.total_score = new.total_score + new.history_score;
        OPEN history_result;
			FETCH history_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `history_rank`,count(1) FROM `{0}-{1}` WHERE `history_rank` != -1 ORDER BY `history_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.history_rank = 1;
				else
					set new.history_rank = @r + 1;
				end if;
			else
				if uscore < new.history_score then
					flag_loop:loop
						FETCH history_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `history_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.history_rank = urank;
                end if;
			end if;
		CLOSE history_result;
	else
		set new.history_score = -1;
        set new.history_rank = -1;
	end if;
    
	if new.chemistry_score is not null then
		set new.total_score = new.total_score + new.chemistry_score;
        OPEN chemistry_result;
			FETCH chemistry_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `chemistry_rank`,count(1) FROM `{0}-{1}` WHERE `chemistry_rank` != -1 ORDER BY `chemistry_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.chemistry_rank = 1;
				else
					set new.chemistry_rank = @r + 1;
				end if;
			else
				if uscore < new.chemistry_score then
					flag_loop:loop
						FETCH chemistry_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `chemistry_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.chemistry_rank = urank;
                end if;
			end if;
		CLOSE chemistry_result;
	else
		set new.chemistry_score = -1;
        set new.chemistry_rank = -1;
	end if;
    
	if new.geography_score is not null then
		set new.total_score = new.total_score + new.geography_score;
        OPEN geography_result;
			FETCH geography_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `geography_rank`,count(1) FROM `{0}-{1}` WHERE `geography_rank` != -1 ORDER BY `geography_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.geography_rank = 1;
				else
					set new.geography_rank = @r + 1;
				end if;
			else
				if uscore < new.geography_score then
					flag_loop:loop
						FETCH geography_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `geography_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.geography_rank = urank;
                end if;
			end if;
		CLOSE geography_result;
	else
		set new.geography_score = -1;
        set new.geography_rank = -1;
	end if;
    
	if new.biology_score is not null then
		set new.total_score = new.total_score + new.biology_score;
        OPEN biology_result;
			FETCH biology_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `biology_rank`,count(1) FROM `{0}-{1}` WHERE `biology_rank` != -1 ORDER BY `biology_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.biology_rank = 1;
				else
					set new.biology_rank = @r + 1;
				end if;
			else
				if uscore < new.biology_score then
					flag_loop:loop
						FETCH biology_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `biology_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.biology_rank = urank;
                end if;
			end if;
		CLOSE biology_result;
	else
		set new.biology_score = -1;
        set new.biology_rank = -1;
	end if;
    
	if new.politics_score is not null then
		set new.total_score = new.total_score + new.politics_score;
        OPEN politics_result;
			FETCH politics_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `politics_rank`,count(1) FROM `{0}-{1}` WHERE `politics_rank` != -1 ORDER BY `politics_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.politics_rank = 1;
				else
					set new.politics_rank = @r + 1;
				end if;
			else
				if uscore < new.politics_score then
					flag_loop:loop
						FETCH politics_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `politics_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.politics_rank = urank;
                end if;
			end if;
		CLOSE politics_result;
	else
		set new.politics_score = -1;
        set new.politics_rank = -1;
	end if;
    
	if new.pe_score is not null then
		set new.total_score = new.total_score + new.pe_score;
        OPEN pe_result;
			FETCH pe_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `pe_rank`,count(1) FROM `{0}-{1}` WHERE `pe_rank` != -1 ORDER BY `pe_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.pe_rank = 1;
				else
					set new.pe_rank = @r + 1;
				end if;
			else
				if uscore < new.pe_score then
					flag_loop:loop
						FETCH pe_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `pe_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.pe_rank = urank;
                end if;
			end if;
		CLOSE pe_result;
	else
		set new.pe_score = -1;
        set new.pe_rank = -1;
	end if;
    
	if new.music_score is not null then
		set new.total_score = new.total_score + new.music_score;
        OPEN music_result;
			FETCH music_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `music_rank`,count(1) FROM `{0}-{1}` WHERE `music_rank` != -1 ORDER BY `music_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.music_rank = 1;
				else
					set new.music_rank = @r + 1;
				end if;
			else
				if uscore < new.music_score then
					flag_loop:loop
						FETCH music_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `music_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.music_rank = urank;
                end if;
			end if;
		CLOSE music_result;
	else
		set new.music_score = -1;
        set new.music_rank = -1;
	end if;
    
	if new.art_score is not null then
		set new.total_score = new.total_score + new.art_score;
        OPEN art_result;
			FETCH art_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `art_rank`,count(1) FROM `{0}-{1}` WHERE `art_rank` != -1 ORDER BY `art_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.art_rank = 1;
				else
					set new.art_rank = @r + 1;
				end if;
			else
				if uscore < new.art_score then
					flag_loop:loop
						FETCH art_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `art_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.art_rank = urank;
                end if;
			end if;
		CLOSE art_result;
	else
		set new.art_score = -1;
        set new.art_rank = -1;
	end if;
    
	if new.computer_score is not null then
		set new.total_score = new.total_score + new.computer_score;
        OPEN computer_result;
			FETCH computer_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `computer_rank`,count(1) FROM `{0}-{1}` WHERE `computer_rank` != -1 ORDER BY `computer_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.computer_rank = 1;
				else
					set new.computer_rank = @r + 1;
				end if;
			else
				if uscore < new.computer_score then
					flag_loop:loop
						FETCH computer_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `computer_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.computer_rank = urank;
                end if;
			end if;
		CLOSE computer_result;
	else
		set new.computer_score = -1;
        set new.computer_rank = -1;
	end if;
    
    if new.total_score = 0 then
		set new.total_score = -1;
        set new.grade_rank = -1;
        set new.class_rank = -1;
	else
		OPEN grade_result;
			FETCH grade_result into uid,urank,uscore,unum;
            if unum = 0 then
				SELECT `grade_rank`,count(1) FROM `{0}-{1}` WHERE `grade_rank` != -1 ORDER BY `grade_rank` DESC LIMIT 1 INTO @r,@num;
                if @num = 0 then
					set new.grade_rank = 1;
				else
					set new.grade_rank = @r + 1;
				end if;
			else
				if uscore < new.total_score then
					flag_loop:loop
						FETCH grade_result into uid,urank,uscore,unum;
						UPDATE `{0}-{1}` SET `grade_rank`=(urank - 1) WHERE `id`=uid;
					end loop;
				else
					set new.grade_rank = urank;
                end if;
			end if;
        CLOSE grade_result;
    end if;
END"""


class DBHelper:
	def __init__(self, host, user, pw, schema):
		self.login_info = (host, user, pw, schema)
		self.conn = sql.connect(host, user, pw, schema)
		self.lock = threading.Lock()

	def reconnect(self):
		try:
			self.conn.close()
		except:
			pass
		self.conn = sql.connect(self.login_info[0], self.login_info[1], self.login_info[2], self.login_info[3])

	def get_exams(self, grade) -> dict:
		try:
			cursor = self.conn.cursor()
			cursor.execute("SELECT * FROM `exams` WHERE `grade`=" + str(grade))
			result = {
				"success": True,
				"data": {
					"exams": cursor.fetchall()
				}
			}
		except Exception as e:
			result = {
				"success": False,
				"exception": e
			}
		finally:
			cursor.close()
			return result

	def get_score(self, grade, examid, uid) -> dict:
		try:
			cursor = self.conn.cursor()
			cursor.execute("SELECT * FROM `{0}-{1}` where `id`={2}".format(grade, examid, uid))
			result = {
				"success": True,
				"data": {
					"scores": cursor.fetchone()
				}
			}
		except Exception as e:
			result = {
				"success": False,
				"exception": e
			}
		finally:
			cursor.close()
			return result

	# TODO: 也许有比直接传入sql更好的办法
	def add_score(self, sqll):
		self.lock.acquire()
		try:
			cursor = self.conn.cursor()
			cursor.execute(sqll)
			self.conn.commit()
		except Exception as e:
			print("[Error] Add new score failed. ROOLBACK! Exception: " + str(e) + ", sql: " + sql)
			self.conn.rollback()
		finally:
			cursor.close()
			self.lock.release()

	def add_exam(self, name, grade, examid):
		self.lock.acquire()
		try:
			cursor = self.conn.cursor()
			cursor.execute("""INSERT INTO `scoresystem`.`exams`(`id`,`name`,`grade`,`examid`)VALUES(Null,'{0}',{1},{2});""".format(name, grade, examid))
			print ("[Info] Insert exam in exams table success")
			cursor.execute(create_exam_table.format(grade, examid))
			print ("[Info] Create table`{0}-{1} in scoresystem schema`".format(grade, examid))
			cursor.execute(exam_table_trigger.format(grade, examid))
			print ("[Info] Add a trigger in table`{0}-{1}`".format(grade, examid))
			self.conn.commit()
		except Exception as e:
			print("[Error] Add a new exam failed. ROOLBACK! Exception: " + str(e))
			self.conn.rollback()
		finally:
			cursor.close()
			self.lock.release()

	def exit(self):
		self.conn.close()


class DGCPInfoGetter:
	ua = "Get Score System Pro"

	@classmethod
	def login(cls, uid: str, password: str) -> dict:
		result = {}
		try:
			response = requests.post("http://www.dgcz.cn/jjwtMobile/login.htm", headers={"User-Agent": cls.ua},
			              data={"username": uid, "password": password}, allow_redirects=False)
			response.close()
			result = {
				"success": True,
			    "data": {
					"status_code": response.status_code,
			        "sid": response.cookies.get("JSESSIONID")
			    }
			}
			if response.headers["Location"] != "/jjwtMobile/CasmCenter/login.jsp":
				result["data"]["success"] = True
			else:
				result["data"]["success"] = False
		except Exception as e:
			result = {"success": False,
			          "exception": e}
		finally:
			return result

	@classmethod
	def check_exams(cls):
		for (grade, account) in refresh_from_accounts.items():
			print("[Info] Start to check grade " + grade + " use account " + str(account))
			response_login = requests.post("http://www.dgcz.cn/jjwtMobile/login.htm",
			                               headers={"User-Agent": cls.ua},
			                               data={"username": account[0], "password": hashlib.md5(account[1].encode("utf-8")).hexdigest()},
			                               allow_redirects=False)
			response_login.close()
			if response_login.headers["Location"] == "/jjwtMobile/CasmCenter/login.jsp":
				print ("[Error] Update " + grade + " exams list failed. Reason: Account id or password error. Account: " + str(account))
				continue
			print("[Info] login in {0} success!".format(account[0]))
			requests.post("http://www.dgcz.cn/jjwtMobile/role.htm",
			                                  headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + response_login.cookies.get("JSESSIONID")},
			                                  allow_redirects=False)
			requests.post("http://www.dgcz.cn/jjwtMobile/getclazzexamsub.htm",
			              headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + response_login.cookies.get("JSESSIONID")},
			              allow_redirects=False)
			response_getscore = requests.post("http://www.dgcz.cn/jjwtMobile/CasmCenter/stu/getscore.jsp",
			              headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + response_login.cookies.get("JSESSIONID")})
			response_getscore.close()
			exams = dbh.get_exams(grade)
			if exams["success"] is not True:
				print ("[Error] Update " + grade + " exams list failed. Reason: Get exams from database failed." + json.dumps(exams))
				continue
			examids = []
			for exam in exams["data"]["exams"]:
				examids.append(str(exam[3]))
			print ("[Info] Show some info " + str(examids))

			soup = BeautifulSoup(response_getscore.text, "html.parser")
			for option in soup.find("form").find("div").find("select").findChildren("option"):
				if option.attrs["value"] == "1":
					continue
				if option.attrs["value"] in examids:
					print("[Info] Exam{0} was recorded.")
					continue
				dbh.add_exam(option.get_text(), grade, option.attrs["value"])
				print ("[Info] Add a new exam success. name: {0}, grade:{1}, examid:{2}.".format(option.get_text(), grade, option.attrs["value"]))
		print ("[Info] Check exam completed.")


	@classmethod
	def check_sid_validity(cls, sid: str) -> dict:
		try:
			response = requests.post("http://www.dgcz.cn/jjwtMobile/role.htm",
			                         headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + sid})
			response.close()
		except Exception as e:
			return {"success": False, "exception": e}

		if response.status_code == 302:
			if response.headers["Location"] == "/jjwtMobile/CasmCenter/login.jsp":
				return {"success": True, "valid": False}
			else:
				return {"success": True, "valid": True}
		else:
			return {"success": False}

	@classmethod
	def get_score(cls, sid: str, examid: int) -> dict:
		try:
			response_markscore = requests.post("http://www.dgcz.cn/jjwtMobile/getscore.htm",
			                                   headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + sid},
			                                   data={"exam": examid},
			                                   allow_redirects=False)
			response_markscore.close()
			response_score = requests.get("http://www.dgcz.cn/jjwtMobile/getscore.htm",
			                              headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + sid})
			response_score.close()
		except Exception as e:
			return {"success": False, "exception": e}

		soup = BeautifulSoup(response_score.text, "html.parser")
		result = {}
		for tr in soup.find("tbody").findChildren("tr"):
			name = tr.findChildren("td")[0].get_text()
			t = tr.findChildren("td")[1].get_text()
			score = float(t.get_text()) if t is not None else None
			if name == "三总" or name == "九总":
				continue

			# 翻 译 转 录
			if ("语文" in name) and score is not None:
				result["chinese_score"] = score
				continue
			if ("数学" in name) and score is not None:
				result["maths_score"] = score
				continue
			if ("英语" in name) and score is not None:
				result["english_score"] = score
				continue
			if ("物理" in name) and score is not None:
				result["physics_score"] = score
				continue
			if ("历史" in name) and score is not None:
				result["history_score"] = score
				continue
			if ("化学" in name) and score is not None:
				result["chemistry_score"] = score
				continue
			if ("地理" in name) and score is not None:
				result["geography_score"] = score
				continue
			if ("生物" in name) and score is not None:
				result["biology_score"] = score
				continue
			if ("政治" in name) and score is not None:
				result["politics_score"] = score
				continue
			if ("体育" in name) and score is not None:
				result["pe_score"] = score
				continue
			if ("音乐" in name) and score is not None:
				result["music_score"] = score
				continue
			if ("美术" in name) and score is not None:
				result["art_score"] = score
				continue
			if ("信息" in name) and score is not None:
				result["computer_score"] = score
				continue
		return {"success": True, "data": result}

	@classmethod
	# TODO: 再获取名字前未判断sid是否可用，可能出问题
	def get_username_from_sid(cls, sid: str) -> str:
		response = requests.get("http://www.dgcz.cn/jjwtMobile/CasmCenter/main.jsp", headers={"User-Agent": cls.ua, "Cookie": "JSESSIONID=" + sid})
		response.close()
		soup = BeautifulSoup(response.text, 'html.parser')
		return soup.find("a").text.strip()


class Server(threading.Thread):
	def __init__(self, logger: logging.Logger, dbhelper: DBHelper):
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
		self.scores = {}
		self.lock = threading.Lock()
		self.db = dbhelper
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
		login_res = DGCPInfoGetter.login(uid, password)

		self.logger.debug("user [{0}] is logging".format(uid))
		if login_res["success"] is True:
			if login_res["data"]["status_code"] == 302:
				if login_res["data"]["success"]:
					self.clear_token_from_uid(uid)
					token = self.create_token(32)
					username = DGCPInfoGetter.get_username_from_sid(login_res["data"]["sid"])

					self.lock.acquire()
					self.tokens[token] = {}
					self.tokens[token]["sid"] = login_res["data"]["sid"]
					self.tokens[token]["uid"] = uid
					self.tokens[token]["username"] = username
					self.lock.release()

					return_result = {"code": 0, "token": token, "username": username, "uid": uid, "sid": login_res["data"]["sid"]}
					self.logger.debug("user [{0}] logged success, sid:[{1}], token:[{2}]".format(uid, login_res["data"]["sid"], token))
				else:
					self.logger.debug("user [{0}] logged failed, reason: 'UidOrPasswordError'".format(uid))
					return_result = {"code": 1, "msg": "账号或密码错误"}
			else:
				self.logger.warning("user [{0}] logged failed, reason: 'StatusCodeError', StatusCode:[{1}]".format(uid, login_res["data"]["status_code"]))
				return_result = {"code": -1, "msg": "学校服务器爆炸了, 请重试, 状态码:" + str(login_res["data"]["status_code"])}
		else:
			return_result = {"code": -1, "msg": "学校服务器爆炸了, 请重试, 错误:" + str(login_res["exception"])}
			raise login_res["exception"]
		return json.dumps(return_result), 200

	def get_score(self, token):
		if token not in self.tokens:
			return json.dumps({"code": 10, "msg": "登录信息失效，请重新登录"})
		self.lock.acquire()
		sid = self.tokens[token]["sid"]
		self.lock.release()
		validity = DGCPInfoGetter.check_sid_validity(sid)
		if validity["success"] is True and validity["valid"] is not True:
			return json.dumps({"code": 10, "msg": "登录信息失效，请重新登录"})

		result = {"code": 0, "exams": {}}
		grade = self.tokens[token]["uid"][0:4]
		exams = self.db.get_exams(grade)["data"]["exams"]
		for exam_info in exams:
			examid = exam_info[3]
			score = self.db.get_score(grade, examid, self.tokens[token]["uid"])
			if score["success"] is not True:
				self.logger.warning("[Warning] Falied to get user {0}'s score, examid: {1}".format(self.tokens[token]["uid"], examid))
				raise score["exception"]
			scores = score["data"]["scores"]
			if len(scores) is None:  # 数据库没有，从学校获取数据
				self.get_score_from_school(token, examid)
				scores = self.db.get_score(grade, examid, self.tokens[token]["uid"])["data"]["scores"]
			result["exams"][examid] = {}
			result["exams"][examid]["examinfo"] = {}
			result["exams"][examid]["examinfo"]["name"] = exam_info[1]
			result["exams"][examid]["scores"] = {}
			if scores[4] != -1:  # chinese
				result["exams"][examid]["scores"]["chinese"] = {"score": scores[4], "rank": scores[5]}
			if scores[6] != -1:  # maths
				result["exams"][examid]["scores"]["maths"] = {"score": scores[6], "rank": scores[7]}
			if scores[8] != -1:  # english
				result["exams"][examid]["scores"]["english"] = {"score": scores[8], "rank": scores[9]}
			if scores[10] != -1:  # physics
				result["exams"][examid]["scores"]["physics"] = {"score": scores[10], "rank": scores[11]}
			if scores[12] != -1:  # history
				result["exams"][examid]["scores"]["history"] = {"score": scores[12], "rank": scores[13]}
			if scores[14] != -1:  # chemistry
				result["exams"][examid]["scores"]["chemistry"] = {"score": scores[14], "rank": scores[15]}
			if scores[16] != -1:  # geography
				result["exams"][examid]["scores"]["geography"] = {"score": scores[16], "rank": scores[17]}
			if scores[18] != -1:  # biology
				result["exams"][examid]["scores"]["biology"] = {"score": scores[18], "rank": scores[19]}
			if scores[20] != -1:  # politics
				result["exams"][examid]["scores"]["politics"] = {"score": scores[20], "rank": scores[21]}
			if scores[22] != -1:  # pe
				result["exams"][examid]["scores"]["pe"] = {"score": scores[22], "rank": scores[23]}
			if scores[24] != -1:  # music
				result["exams"][examid]["scores"]["music"] = {"score": scores[24], "rank": scores[25]}
			if scores[26] != -1:  # art
				result["exams"][examid]["scores"]["art"] = {"score": scores[26], "rank": scores[27]}
			if scores[28] != -1:  # computer
				result["exams"][examid]["scores"]["computer"] = {"score": scores[28], "rank": scores[29]}
			if scores[30] != -1:
				result["exams"][examid]["scores"]["special"] = {"total": scores[30], "grade_rank": scores[31]}
		self.logger.debug(self.tokens[token]["username"] + "'s result: " + json.dumps(result))
		return json.dumps(result)

	# TODO: 没有sid检测
	def get_score_from_school(self, token: str, examid: int):
		uid = self.tokens[token]["uid"]
		sid = self.tokens[token]["sid"]
		grade = int(uid[0:4])
		username = self.tokens[token]["username"]
		scores = DGCPInfoGetter.get_score(sid, examid)

		# 伞兵操作
		keys = ["id", "grade", "class", "username"] + scores["data"].keys()
		values = ["Null", grade, 0, username] + scores["data"].values()
		keys_str = json.dumps(keys).replace('"', '`')
		values_str = json.dumps(values).replace('"Null"', 'Null')
		sqll = "INSERT INTO `{0}-{1}` ({2})VALUES({3});".format(grade, examid, keys_str, values_str)
		self.db.add_score(sqll)

	def clear_token_from_uid(self, uid: str) -> bool:
		self.lock.acquire()
		for (k, v) in self.tokens.items():
			if v["uid"] == uid:
				del(self.tokens[k])
				self.lock.release()
				return True
		self.lock.release()
		return False

	def create_token(self, length: int) -> str:
		result = ""
		for i in range(length):
			result += random.choice(self.__chars)
		return result


class Console:
	def __init__(self, server, logger: logging.Logger):
		self.logger = logger
		self.server = server
		self.debug = False

	def run(self) -> None:
		while True:
			cmd = input(">>> ")
			try:
				self.progress_cmd(cmd)
			except Exception as e:
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
					print("===========tokens============")
					print(json.dumps(get_tokens(), ensure_ascii=False))
					print("=============================")

	def progress_cmd(self, cmd: str):
		args = cmd.split(" ")
		cmd = args[0].lower()
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
			print("Debug mode on" if self.debug else "Debug mode off")
		elif cmd == "checkexams":
			DGCPInfoGetter.check_exams()
		elif cmd == "exit":
			dbh.exit()
			exit(0)


if __name__ == "__main__":
	s = requests.session()
	s.keep_alive = False
	requests.adapters.DEFAULT_RETRIES = 114514

	logger = logging.getLogger("My")
	console_handler = logging.StreamHandler()
	file_handler = logging.FileHandler("log.log", encoding="utf-8")
	console_handler.setLevel(logging.DEBUG)
	file_handler.setLevel(logging.INFO)
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	logger.setLevel(logging.INFO)

	print("[Info] Connecting to mysql.")
	dbh = DBHelper("localhost", "root", "abcd1234", "scoresystem")
	print("[Info] Connect to mysql success.")
	s = Server(logger, dbh)
	s.start()
	console = Console(s, logger)
	console.run()
