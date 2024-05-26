import json
import sqlite3
import os
import urllib3
import urllib.parse
import logging

class DigiKeyApi:
	def __init__(self) :
		self.con = sqlite3.Connection(os.path.expanduser("~/.cache/horizon-stock_info_provider_digikey_cache.db"), check_same_thread=False)
		self.http = urllib3.PoolManager()
		with open(os.path.expanduser("~/.config/horizon/prefs.json"), "r") as fi :
			j = json.load(fi)
			self.client_id = j["digikey_api"]["client_id"]
			self.client_secret = j["digikey_api"]["client_secret"]
	
	def get_refresh_token(self) :
		cur = self.con.cursor()
		cur.execute("SELECT value FROM tokens WHERE key = 'refresh' AND valid_until > datetime()")
		res = cur.fetchone()
		if res is None :
			raise IOError("no refresh token")
		else :
			return res[0]
	
	def update_token(self, key, value, expiry_seconds):
		with self.con :
			self.con.execute("INSERT OR REPLACE INTO tokens (key, value, valid_until) VALUES (?, ?, datetime('now', ? || ' "
					"seconds'))", (key, value, expiry_seconds))

	
	def update_tokens_from_response(self, j) :
		self.update_token("access", j["access_token"], j["expires_in"])
		self.update_token("refresh", j["refresh_token"], j["refresh_token_expires_in"])
	
	def get_access_token(self) :
		refresh_token = self.get_refresh_token()
		cur = self.con.cursor()
		cur.execute("SELECT value FROM tokens WHERE key = 'access' AND valid_until > datetime()")
		res = cur.fetchone()
		if res is None :
			fields = {
				"client_id": self.client_id,
				"client_secret": self.client_secret,
				"grant_type": "refresh_token",
				"refresh_token": refresh_token
			}
			r = self.http.request_encode_body('POST', 'https://api.digikey.com/v1/oauth2/token', encode_multipart=False, fields=fields)
			print(r.data)
			assert(r.status == 200)
			j = json.loads(r.data.decode())
			self.update_tokens_from_response(j)
			return j["access_token"]
		else :
			return res[0]
	
	def get_barcode(self, barcode) :
		headers = {
			"accept":"application/json",
			"Authorization": f"Bearer {self.get_access_token()}",
			"X-DIGIKEY-Client-Id": self.client_id
		}
		url = "https://api.digikey.com/Barcoding/v3/Product2DBarcodes/" + urllib.parse.quote(barcode, safe='')
		r = self.http.request('GET', url, headers=headers)
		if r.status != 200 :
			print(r.data.decode())
		assert(r.status == 200)
		return json.loads(r.data.decode())
"""
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""
if __name__ == "__main__" :
	api = DigiKeyApi()
	
	print(api.get_barcode(bc))
