#G2Aサイトから最低値を取得して一定以下なら通知する
import datetime
import time
import json
import re
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup

lowpricetime = datetime.datetime.now()

# URL入力
def url_input():
	input_url = input('G2A製品ページのURLを入力してください。(G2A Game URL Address) : ')
	return input_url

# URLが正しいかチェック
def url_check(url):
	check = url[0:4]
	# http(s)以外なら弾く
	if "http" in check or "https" in check:
		# G2A以外なら弾く
		# https://www.g2a.com/
		if "https://www.g2a.com/" == url or "https://www.g2a.com" == url:
			print("This URL is G2A Top Page. Please enter a product page.")
			return False
		else:
			check = url
			if "www.g2a.com/" in check:
				return True
			else:
				print("Not G2A Address. Please Retry")
				return False
	else:
		print("Not http(s) Address. Please Retry")
		return False

# 値段入力
def input_price():
	# 最小数値を入力してください。
	desprice = input("希望価格を入力(Desired Price) : ")
	return desprice
	
# 数値チェック
def price_check(price):
	# isdigit()だと小数点を含む数値を入れた場合str扱いになるので正規表現を使う
	if bool(re.compile("^\d+\.?\d*\Z").match(price)):
		return True
	else:
		# 数値ではありません。数値を入力してください。
		print("It is not a number. Please enter a numerical value.")
		return False
	

def network_connecting(load_url):
	# UserAgent情報 Firefox（20220121時点）
	dummy_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
	header = {
			"User-Agent"      : dummy_user_agent,
			"Accept-Language" : "ja,en-US;q=0.7,en;q=0.3"
		}
	# タイムアウト処理
	try:
		html = requests.get(load_url, headers=header, timeout=(30.0, 15.0))
	except Timeout:
		print("Connect Time out")
		pass
	# HTTPステータスコード処理
	if html.status_code == requests.codes.ok:
		# Windows環境だとtextが内部でエンコードがcp932になっているらしいのでUTF-8に
		soup = BeautifulSoup(html.text.encode('cp932', "ignore").decode('utf-8', "ignore"),  'html.parser')
		#soup = BeautifulSoup(html.content,  'lxml')

		# Script要素を表示する
		for element in soup.find_all("script"):
			findtext = str(element.text)
			# lowPieceはユニークなのでscript内にlowPirce文字列があったら
			if "lowprice" in findtext or "lowPrice" in findtext:
				# jsonデータ型に変換
				jsondata=json.loads(findtext)
				# json内のoffers内のlowPriceを書き出し
				"""
				{
					"@context": "https://schema.org/",
					"@type": "Product",
					"name": "Game Name",
					"category": "Ganre",
					"image": "https://*********************",
					"url": "https://******************************************",
					"description": "description",
					"releaseDate": "20XX-01-01",
					"brand": {
						"name": "XXXX, LTD.",
						"@type": "Brand"
					},
					"offers": {
						"@type": "AggregateOffer",
						"priceCurrency": "JPY",
						"lowPrice": "XXXX",
						"highPrice": "NNNN",
						"offerCount": "XX",
						"availability": "https://schema.org/InStock",
						"itemCondition": "https://schema.org/NewCondition"
					}
				}
				"""
				# 現在の最低価格を表示
				print(str(datetime.datetime.now().isoformat(timespec="seconds")) + " 現在の最安値(lowPrice) : " + jsondata["offers"]["lowPrice"])
				break
		try:
			return jsondata["offers"]["lowPrice"]
		except UnboundLocalError:
			network_connecting(load_url)
	else:
		html.raise_for_status()
		print(html.txt)

def main():
	# URL入力
	load_url = url_input()
	# URLチェック
	if url_check(load_url):
		# 希望価格を入力
		desire_price = input_price()
		# 数値チェック
		while True:
			if price_check(desire_price):
				break
			else:
				desire_price = input_price()
		desire_price = float(desire_price)
		# サイト情報取得
		lowprice = float(network_connecting(load_url))
		# 希望価格と商品最低価格の比較
		while desire_price <= lowprice:
			# サーバーに負荷をかけないためにスリープ
			time.sleep(7)
			# 再度サーバーから最安値を引っ張る
			lowprice = float(network_connecting(load_url))

		while True:
			time.sleep(2)
			print(str(datetime.datetime.now().isoformat(timespec="seconds")) + " " + str(lowpricetime) + " に対象商品が希望価格以下になりました。(Target products are now below the suggested price.)")
	else:
		# URLチェックに失敗した場合は最初に戻す
		main()

main()
