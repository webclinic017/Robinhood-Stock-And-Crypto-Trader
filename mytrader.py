import robin_stocks.robinhood as robin
import pyotp
import sys
from time import sleep
import pandas as pd
from os import system
import colorama
from colorama import Fore, Back, Style
import time
import json
from datetime import datetime
colorama.init(autoreset=True)
login = robin.login('yourrobinhood@email.com','yourrobinhoodpassword')
#print("Current OTP:", totp)

enteredTrade = False
rsiPeriod = 5

t0=time.time()
system('clear')

# Dollarsleft
# OwnedAmount
# Buys[]

def QUOTE(ticker):
	r = robin.get_latest_price(ticker)
	print(ticker.upper() + ": $" + str(r[0]))
	
def BUY(ticker, amount):
	r = robin.order_buy_market(ticker, amount)
	print(r)
	
def SELL(ticker, amount):
	r = robin.order_sell_market(ticker, amount)
	print(r)
	
def BUYC(ticker, amount):
	r = robin.order_buy_crypto_by_quantity(ticker, amount)
	print(r)
	
def SELLC(ticker, amount):
	r = robin.order_sell_crypto_by_quantity(ticker, amount)
	print(r)
	
def AUTO(ticker, maxDollars):
	print("\nStarted\n")
	ownedAmount = float(0);
	dollarsLeft = float(maxDollars);
	buys = []
	houraverages = []
	lastprice = float(0)
	onehourlowlast = float(0)
	onehourhighlast = float(0)
	fiftytwoweekaverage = float(0)
	lasttotal = float(0)
	runtime = float(1) #Runtime is in hours
	
	currentPrice = float(robin.stocks.get_latest_price(ticker)[0])
	
	stock_data_day = robin.stocks.get_stock_historicals(ticker, interval="day", span="week")
	stock_historical_day = pd.DataFrame(stock_data_day)
	
	stock_data_week = robin.stocks.get_stock_historicals(ticker, interval="week", span="year")
	stock_historical_week = pd.DataFrame(stock_data_week)
	one_week_low = float(stock_historical_week.iloc[-1]['low_price']) * 1.0
	one_week_high = float(stock_historical_week.iloc[-1]['high_price'])
	
	fifty_two_week_average = (float(robin.stocks.get_fundamentals(ticker, info='high_52_weeks')[0])+float(robin.stocks.get_fundamentals(ticker, info='high_52_weeks')[0]))/2
	amounttotrade = float(dollarsLeft) / float(currentPrice)
	while True:
		actionThisTime = ""
		print("")
		
		# If the current price is more than the 1 week high
		if float(currentPrice) > float(one_week_high):
			print(Fore.RED + "\033[1m" + "SELL!" + "\033[0m")
			r = robin.order_sell_fractional_by_quantity(ticker, amounttotrade)
			try:
				count = float(0)
				while True:
					sleep(1)
					count += 1
					if robin.orders.get_stock_order_info(r['id'])['state'] == 'filled':
						dollarsLeft += amounttotrade * float(robin.orders.get_stock_order_info(r['id'])['price'])
						ownedAmount -= amounttotrade
						buys.remove(x)
						actionThisTime = "sold"
						break
					if count >= 6 and robin.orders.get_stock_order_info(r['id'])['state'] != 'filled':
						robin.cancel_all_stock_orders()
						actionThisTime = "failed"
						break
			except:
				print("failed")
				robin.cancel_all_stock_orders()
				actionThisTime = "failed"
		# If the current price is less than the 1 week low, greater than the large average
		if float(currentPrice) < float(one_week_low) and float(currentPrice) > float(fifty_two_week_average):
			print(Fore.GREEN + "\033[1m" + "BUY!" + "\033[0m")
			r = robin.order_buy_fractional_by_quantity(ticker, amounttotrade)
			try:
				count = float(0)
				while True:
					sleep(1)
					count += 1
					if robin.orders.get_stock_order_info(r['id'])['state'] == 'filled':
						dollarsLeft -= float(robin.orders.get_stock_order_info(r['id'])['price'])*amounttotrade
						ownedAmount += amounttotrade
						buys.append(float(robin.orders.get_stock_order_info(r['id'])['price'])*amounttotrade)
						actionThisTime = "bought"
						break
					if count >= 6 and robin.orders.get_stock_order_info(r['id'])['state'] != 'filled':
						robin.cancel_all_stock_orders()
						actionThisTime = "failed"
						break
			except:
				print("failed")
				robin.cancel_all_stock_orders()
				actionThisTime = "failed"
		#Information indicators
		if float(currentPrice) > float(lastprice):
			print("Price:          $" + Fore.GREEN + str(round(float(currentPrice)*1000)/1000))
		else:
			print("Price:          $" + Fore.RED + str(round(float(currentPrice)*1000)/1000))
		print("Amnt Owned:      " + str(ownedAmount) + " at $" + str((round(float(ownedAmount) * float(currentPrice)*1000)/1000)))
		print("52   " + str(fifty_two_week_average))
		print("high " + str(one_week_high))
		print("low  " + str(one_week_low))
		print()
		if actionThisTime == "bought":
			print(Fore.GREEN + "Successfully completed trading session, bought")
		elif actionThisTime == "sold":
			print(Fore.RED + "Successfully completed trading session, sold")
		if actionThisTime == "":
			print(Fore.YELLOW + "Successfully completed trading session, no trades were made")
		else:
			print(Fore.MAGENTA + "Error during trading session")
		#system('clear')
		exit()
		
		
		
def AUTOCA(ticker, maxDollars):
	print("\nStarted\n")
	ownedAmount = float(0);
	dollarsLeft = float(maxDollars);
	while True:
		print("")
		stock_data_minute = robin.crypto.get_crypto_historicals(ticker, interval="5minute", span="week")
		stock_historical_minute = pd.DataFrame(stock_data_minute)
		price_diff_fiveminutes = float(stock_historical_minute.iloc[-1]['close_price']) - float(stock_historical_minute.iloc[0]['close_price'])
		
		stock_data_day = robin.crypto.get_crypto_historicals(ticker, interval="day", span="week")
		stock_historical_day = pd.DataFrame(stock_data_day)
		price_diff_oneday = float(stock_historical_day.iloc[-1]['close_price']) - float(stock_historical_day.iloc[0]['close_price'])
		
		stock_data_hour = robin.crypto.get_crypto_historicals(ticker, interval="hour", span="week")
		stock_historical_hour = pd.DataFrame(stock_data_hour)
		one_hour_low = float(stock_historical_hour.iloc[-1]['low_price']) * 1.022
		one_hour_high = float(stock_historical_hour.iloc[-1]['high_price'])
		
		fifty_two_week_average = (float(pd.DataFrame(stock_data_hour).iloc[0]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-1]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-2]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-3]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-4]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-5]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-6]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-7]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-8]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-9]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-10]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-11]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-12]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-13]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-14]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-15]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-16]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-17]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-18]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-19]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-20]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-21]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[-22]['close_price']))/23
		#r = robin.order_sell_crypto_by_quantity(ticker, amount)
		print("Price:      $" + str(robin.crypto.get_crypto_quote(ticker, info="mark_price")) + "\nHour high:  $" + str(one_hour_high) + "\nHour low:   $" + str(one_hour_low) + "\n23 Hr Avg:  $" + str(fifty_two_week_average) + "\nDollars:    $" + str(dollarsLeft) + "\nAmnt Owned: " + str(ownedAmount) + " at $" + str(float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))))
		# If the current price is more than the 1 hour high and you own at least one
		if float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > one_hour_high and float(ownedAmount) >= 1:
			print("SELL!")
			dollarsLeft += float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
			ownedAmount -= 1
		# If the current price is less than the 1 hour low, greater than the large average, and you can pay for it
		elif (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) < float(one_hour_low)) and (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > fifty_two_week_average) and (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) < float(dollarsLeft)):
			print("BUY!")
			dollarsLeft -= float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
			ownedAmount += 1
		else:
			print("Stay.")
		sleep(4)
		#system('clear')
		
def AUTOCB(ticker, maxDollars):
	print("\nStarted\n")
	ownedAmount = 0;
	dollarsLeft = maxDollars;
	while True:
		print("")
		stock_data_minute = robin.crypto.get_crypto_historicals(ticker, interval="5minute", span="week")
		stock_historical_minute = pd.DataFrame(stock_data_minute)
		price_diff_fiveminutes = float(stock_historical_minute.iloc[-1]['close_price']) - float(stock_historical_minute.iloc[0]['close_price'])
		
		stock_data_day = robin.crypto.get_crypto_historicals(ticker, interval="day", span="week")
		stock_historical_day = pd.DataFrame(stock_data_day)
		price_diff_oneday = float(stock_historical_day.iloc[-1]['close_price']) - float(stock_historical_day.iloc[0]['close_price'])
		
		stock_data_week = robin.crypto.get_crypto_historicals(ticker, interval="week", span="year")
		stock_historical_week = pd.DataFrame(stock_data_week)
		one_week_low = float(stock_historical_week.iloc[-1]['low_price'])
		one_week_high = float(stock_historical_week.iloc[-1]['high_price'])
		
		fifty_two_week_average = (float(pd.DataFrame(stock_data_week).iloc[0]['close_price'])+float(pd.DataFrame(stock_data_week).iloc[-1]['close_price'])+float(pd.DataFrame(stock_data_week).iloc[-2]['close_price'])+float(pd.DataFrame(stock_data_week).iloc[-3]['close_price']))/4
		#r = robin.order_sell_crypto_by_quantity(ticker, amount)
		print("Price:      " + str(robin.crypto.get_crypto_quote(ticker, info="mark_price")) + "\nWeek high:  " + str(one_week_high) + "\nWeek low:   " + str(one_week_low) + "\n52 Wk Avg:  " + str(fifty_two_week_average))
		
		if float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > one_week_high and ownedAmount >= 1:
			print("SELL!")
			dollarsLeft += float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
			ownedAmount -= 1
		elif (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) < one_week_low) and ((robin.crypto.get_crypto_quote(ticker, info="mark_price")) > fifty_two_week_average) and (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) < dollarsLeft):
			print("BUY!")
			dollarsLeft -= float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
			ownedAmount += 1
		else:
			print("Stay.")
		sleep(15)
		
def AUTOCC(ticker, maxDollars):
	print("\nStarted\n")
	
	persistence= open("/home/sam/Public/Programs/mytraderdata.txt", 'r+')
	lines=persistence.read().split('\n')
	print(lines)
	if len(lines) > 2:
		dollarsLeft = float(lines[0])
		print(dollarsLeft)
	else:
		dollarsLeft = float(maxDollars)
		
	if len(lines) > 2:
		ownedAmount = float(lines[1])
		print(ownedAmount)
	else:
		ownedAmount = float(0)
		
	if len(lines) > 2:
		buyList = lines[2].split(',')
		buys = buyList
		print(buys)
	else:
		buys = []
		print(buys)
	houraverages = []
	lastprice = float(0)
	onehourlowlast = float(0)
	onehourhighlast = float(0)
	fiftytwoweekaverage = float(0)
	lasttotal = float(0)
	runtime = float(2) #Runtime is in hours
	
	if float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > float(maxDollars):
		amounttotrade = 0.50 / float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
	else:
		amounttotrade = 10
	
	while True:
		actionThisTime = ""
		print("")
		stock_data_minute = robin.crypto.get_crypto_historicals(ticker, interval="5minute", span="week")
		stock_historical_minute = pd.DataFrame(stock_data_minute)
		price_diff_fiveminutes = float(stock_historical_minute.iloc[-1]['close_price']) - float(stock_historical_minute.iloc[0]['close_price'])
		
		stock_data_day = robin.crypto.get_crypto_historicals(ticker, interval="day", span="week")
		stock_historical_day = pd.DataFrame(stock_data_day)
		price_diff_oneday = float(stock_historical_day.iloc[-1]['close_price']) - float(stock_historical_day.iloc[0]['close_price'])
		
		stock_data_hour = robin.crypto.get_crypto_historicals(ticker, interval="hour", span="week")
		stock_historical_hour = pd.DataFrame(stock_data_hour)
		
		one_hour_low = float(stock_historical_minute.iloc[-1]['low_price']) * 1.0
		one_hour_high = float(stock_historical_minute.iloc[-1]['high_price'])
		
		fifty_two_week_average = float(pd.DataFrame(stock_data_hour).iloc[0]['close_price'])
		#r = robin.order_sell_crypto_by_quantity(ticker, amount)
		largestBuy = float(0)
		for x in buys:
			if float(x) > float(largestBuy):
				largestBuy = float(x)
			# If the current price is more than the 1 hour high and it's price has increased
			if float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*amounttotrade > float(x) * 1.001 and actionThisTime == "":
				print(Fore.RED + "\033[1m" + "SELL!" + "\033[0m")
				r = robin.order_sell_crypto_by_quantity(ticker, amounttotrade)
				try:
					count = float(0)
					while True:
						sleep(1)
						count += 1
						if robin.orders.get_crypto_order_info(r['id'])['state'] == 'filled':
							dollarsLeft += amounttotrade * float(robin.orders.get_crypto_order_info(r['id'])['price'])
							ownedAmount -= amounttotrade
							buys.remove(x)
							actionThisTime = "sold"
							break
						if count >= 6 and robin.orders.get_crypto_order_info(r['id'])['state'] != 'filled':
							robin.cancel_crypto_orders(r['id'])
							actionThisTime = "failed"
							break
				except:
					print("failed")
					robin.cancel_crypto_orders(r['id'])
					actionThisTime = "failed"
			if float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*amounttotrade < float(x) * 0.0 and float(ownedAmount) >= amounttotrade and actionThisTime == "":
				r = robin.order_sell_crypto_by_quantity(ticker, amounttotrade)
				try:
					count = float(0)
					while True:
						sleep(1)
						count += 1
						if robin.orders.get_crypto_order_info(r['id'])['state'] == 'filled':
							print(Fore.RED + "\033[1m" + "SELL! (scaredy)" + "\033[0m")
							dollarsLeft += float(robin.orders.get_crypto_order_info(r['id'])['price'])*amounttotrade
							ownedAmount -= amounttotrade
							buys.remove(x)
							actionThisTime = "sold"
							break
						if count >= 6 and robin.orders.get_crypto_order_info(r['id'])['state'] != 'filled':
							robin.cancel_crypto_orders(r['id'])
							actionThisTime = "failed"
							break
				except:
					print("failed")
					robin.cancel_crypto_orders(r['id'])
					actionThisTime = "failed"
		if largestBuy == 0:
			largestBuy = float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))
		# If the current price is less than the 1 hour low, greater than the large average, you can pay for it, and the current value is less than 101% of the largest bought value so far
		if (float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > float(fifty_two_week_average)) and (float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*float(amounttotrade) < float(dollarsLeft)) and actionThisTime == "" and round(time.time()-t0) / 60 / 60 < float(runtime) and float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) <= float(largestBuy) * 1.05:
			#also code above this stops buying after a certain time, so it can close all trades for that period of time
			print(Fore.GREEN + "\033[1m" + "BUY!" + "\033[0m")
			r = robin.order_buy_crypto_by_quantity(ticker, amounttotrade)
			try:
				count = float(0)
				while True:
					sleep(1)
					count += 1
					if robin.orders.get_crypto_order_info(r['id'])['state'] == 'filled':
						dollarsLeft -= float(robin.orders.get_crypto_order_info(r['id'])['price'])*amounttotrade
						ownedAmount += amounttotrade
						buys.append(float(robin.orders.get_crypto_order_info(r['id'])['price'])*amounttotrade)
						actionThisTime = "bought"
						break
					if count >= 6 and robin.orders.get_crypto_order_info(r['id'])['state'] != 'filled':
						robin.cancel_crypto_orders(r['id'])
						actionThisTime = "failed"
						break
			except:
				print("failed")
				robin.cancel_crypto_orders(r['id'])
				actionThisTime = "failed"
		#Information indicators
		persistence.truncate(0)
		
		if float(robin.crypto.get_crypto_quote(ticker, info="mark_price")) > float(lastprice):
			print("Price:          $" + Fore.GREEN + str(round(float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*1000)/1000))
		else:
			print("Price:          $" + Fore.RED + str(round(float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*1000)/1000))
			
		if float(one_hour_high) > float(onehourhighlast):
			print("5 min high:    $" + Fore.GREEN + str(round(one_hour_high*1000)/1000))
		else:
			print("5 min high:    $" + Fore.RED + str(round(one_hour_high*1000)/1000))
			
		if float(one_hour_low) > float(onehourlowlast):
			print("5 min low:     $" + Fore.GREEN + str(round(one_hour_low*1000)/1000))
		else:
			print("5 min low:     $" + Fore.RED + str(round(one_hour_low*1000)/1000))
			
		if float(fifty_two_week_average) > float(fiftytwoweekaverage):
			print("1 Hr Avg:      $" + Fore.GREEN + str(round(fifty_two_week_average*1000)/1000))
		else:
			print("1 Hr Avg:      $" + Fore.RED + str(round(fifty_two_week_average*1000)/1000))
			
		print("Dollars:        $" + str(dollarsLeft))
		persistence.write(str(dollarsLeft) + "\n")
		print("Amnt Owned:      " + str(ownedAmount) + " at $" + str((round(float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))*1000)/1000)))
		persistence.write(str(ownedAmount) + "\n")
		if float(dollarsLeft) + (float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))) > float(lasttotal):
			print("Total:          $" + Fore.GREEN + str(round((float(dollarsLeft) + (float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))))*1000)/1000))
		else:
			print("Total:          $" + Fore.RED + str(round((float(dollarsLeft) + (float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))))*1000)/1000))
		
		if len(buys) > 0:
			cnt = int(0)
			for buy in buys:
				if cnt < len(buys):
					persistence.write(str(buy) + ",")
				else:
					persistence.write(str(buy))
				cnt+=1
		else:
			persistence.write(str(robin.crypto.get_crypto_quote(ticker, info="mark_price")) + "," + str(robin.crypto.get_crypto_quote(ticker, info="mark_price")))
		
		seconds = round(time.time()-t0)
		minutes = 0
		hours = 0
		while seconds >= 60:
			seconds-=60
			minutes+=1
		while minutes >= 60:
			minutes-=60
			hours+=1
		print("Time Elapsed:    " + str(hours) + ":" + str(minutes) + ":" + str(seconds) + " at " + str(datetime.now()))
		added = float(0)
		for y in houraverages:
			added += float(y)
		if actionThisTime != "":
			houraverages.append((((float(dollarsLeft) + (float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price"))))-float(maxDollars))/float(time.time()-t0))*60*60)
		if len(houraverages) > 0:
			if float(added)/float(len(houraverages)) > 0:
				print (Fore.YELLOW + "$ Per Hour:      $" + str(round(float(added)/float(len(houraverages))*100)/100) + " at " + Fore.GREEN + "+%" + str(((round(float(added)/float(len(houraverages))*100)/100)/float(maxDollars))*100))
			else:
				print (Fore.YELLOW + "$ Per Hour:      $" + str(round(float(added)/float(len(houraverages))*100)/100) + " at " + Fore.RED + "-%" + str(((round(float(added)/float(len(houraverages))*100)/100)/float(maxDollars))*100))
		lastprice = robin.crypto.get_crypto_quote(ticker, info="mark_price")
		onehourlowlast = one_hour_low
		onehourhighlast = one_hour_high
		fiftytwoweekaverage = fifty_two_week_average
		lasttotal = float(dollarsLeft) + (float(ownedAmount) * float(robin.crypto.get_crypto_quote(ticker, info="mark_price")))
		if float(seconds) / 60 /60 >= runtime and float(ownedAmount) <= 0:
			if (float(dollarsLeft)-float(maxDollars)) > 0:
				print("Successfully closed trading session with a profit of " + Fore.GREEN + (float(dollarsLeft)-float(maxDollars)) + Fore.WHITE + " dollars")
			else:
				print("Successfully closed trading session with a profit of " + Fore.RED + str(float(dollarsLeft)-float(maxDollars)) + Fore.WHITE + " dollars")
			exit()
		persistence.close()
		sleep(2)
		#system('clear')


# $1017 @5hrs
# $11 @5hrs
def AUTOCSIM(ticker, maxDollars):
	print("\nStarted\n")
	ownedAmount = float(0);
	dollarsLeft = float(maxDollars);
	buys = []
	houraverages = []
	lastprice = float(0)
	onehourlowlast = float(0)
	onehourhighlast = float(0)
	fiftytwoweekaverage = float(0)
	lasttotal = float(0)
	
	stock_data_minuteA = robin.crypto.get_crypto_historicals(ticker, interval="5minute", span="week")
	stock_historical_minuteA = pd.DataFrame(stock_data_minuteA)
	
	stock_data_hourA = robin.crypto.get_crypto_historicals(ticker, interval="hour", span="week")
	stock_historical_hourA = pd.DataFrame(stock_data_hourA)
	if float(stock_historical_hourA.iloc[int(-24)]['close_price']) > float(maxDollars):
		amounttotrade = 2 / float(stock_historical_hourA.iloc[int(-24)]['close_price'])
	else:
		amounttotrade = 2
	secondcount = int(0)
	while True:
		secondcount += int(60)
		seconds = secondcount
		minutes = 0
		hours = 0
		while seconds >= 60:
			seconds-=60
			minutes+=1
		while minutes >= 60:
			minutes-=60
			hours+=1
		actionThisTime = ""
		print("")
		stock_data_minute = robin.crypto.get_crypto_historicals(ticker, interval="5minute", span="week")
		stock_historical_minute = pd.DataFrame(stock_data_minute)
		
		stock_data_day = robin.crypto.get_crypto_historicals(ticker, interval="day", span="week")
		stock_historical_day = pd.DataFrame(stock_data_day)
		
		stock_data_hour = robin.crypto.get_crypto_historicals(ticker, interval="hour", span="week")
		stock_historical_hour = pd.DataFrame(stock_data_hour)
		one_hour_low = float(stock_historical_hour.iloc[int(hours)-24]['low_price']) * 1.45
		one_hour_high = float(stock_historical_hour.iloc[int(hours)-24]['high_price'])
		
		fifty_two_week_average = (float(pd.DataFrame(stock_data_hour).iloc[int(hours)-36]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-35]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-34]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-33]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-32]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-31]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-30]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-29]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-28]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-27]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-26]['close_price'])+float(pd.DataFrame(stock_data_hour).iloc[int(hours)-25]['close_price']))/13
		#r = robin.order_sell_crypto_by_quantity(ticker, amount)
		largestBuy = float(0)
		for x in buys:
			if float(x) > float(largestBuy):
				largestBuy = float(x)
			# If the current price is more than the 1 hour high and it's price has increased
			if float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*amounttotrade > float(x) * 1.01 and actionThisTime == "":
				print(Fore.RED + "\033[1m" + "SELL!" + "\033[0m")
				secondcount+=20
				dollarsLeft += amounttotrade * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])
				ownedAmount -= amounttotrade
				buys.remove(x)
				actionThisTime = "sold"
			if float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*amounttotrade < float(x) * 0.900 and float(ownedAmount) >= amounttotrade and actionThisTime == "":
				print(Fore.RED + "\033[1m" + "SELL! (scaredy)" + "\033[0m")
				secondcount+=20
				dollarsLeft += amounttotrade * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])
				ownedAmount -= amounttotrade
				buys.remove(x)
				actionThisTime = "sold"
		if largestBuy == 0:
			largestBuy = float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])
		# If the current price is less than the 1 hour low, greater than the large average, you can pay for it, and the current value is less than 101% of the largest bought value so far
		if (float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']) < float(one_hour_low) and float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']) > float(fifty_two_week_average)) and (float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*amounttotrade < float(dollarsLeft)) and actionThisTime == "" and float(secondcount) / 60 / 60 < 5 and float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']) <= float(largestBuy) * 1.02:
			#also code above this stops buying after a certain time, so it can close all trades for that period of time
					print(Fore.GREEN + "\033[1m" + "BUY!" + "\033[0m")
					secondcount+=20
					dollarsLeft -= amounttotrade * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])
					ownedAmount += amounttotrade
					buys.append(float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*amounttotrade)
					actionThisTime = "sold"
		#Information indicators
		if float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']) > float(lastprice):
			print("Price:          $" + Fore.GREEN + str(round(float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*1000)/1000))
		else:
			print("Price:          $" + Fore.RED + str(round(float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*1000)/1000))
			
		if float(one_hour_high) > float(onehourhighlast):
			print("Hour high:      $" + Fore.GREEN + str(round(one_hour_high*1000)/1000))
		else:
			print("Hour high:      $" + Fore.RED + str(round(one_hour_high*1000)/1000))
			
		if float(one_hour_low) > float(onehourlowlast):
			print("Hour low:       $" + Fore.GREEN + str(round(one_hour_low*1000)/1000))
		else:
			print("Hour low:       $" + Fore.RED + str(round(one_hour_low*1000)/1000))
			
		if float(fifty_two_week_average) > float(fiftytwoweekaverage):
			print("12 Hr Avg:      $" + Fore.GREEN + str(round(fifty_two_week_average*1000)/1000))
		else:
			print("12 Hr Avg:      $" + Fore.RED + str(round(fifty_two_week_average*1000)/1000))
			
		print("Dollars:        $" + str(dollarsLeft))
		print("Amnt Owned:      " + str(ownedAmount) + " at $" + str((round(float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])*1000)/1000)))
		if float(dollarsLeft) + (float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])) > float(lasttotal):
			print("Total:          $" + Fore.GREEN + str(round((float(dollarsLeft) + (float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])))*1000)/1000))
		else:
			print("Total:          $" + Fore.RED + str(round((float(dollarsLeft) + (float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])))*1000)/1000))
		print("Time Elapsed:    " + str(hours) + ":" + str(minutes) + ":" + str(seconds))
		added = float(0)
		for y in houraverages:
			added += float(y)
		if actionThisTime != "":
			houraverages.append((((float(dollarsLeft) + (float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price'])))-float(maxDollars))/float(time.time()-t0))*60*60)
		if len(houraverages) > 0:
			if float(added)/float(len(houraverages)) > 0:
				print (Fore.YELLOW + "$ Per Hour:      $" + str(round(float(added)/float(len(houraverages))*100)/100) + " at " + Fore.GREEN + "+%" + str(((round(float(added)/float(len(houraverages))*100)/100)/float(maxDollars))*100))
			else:
				print (Fore.YELLOW + "$ Per Hour:      $" + str(round(float(added)/float(len(houraverages))*100)/100) + " at " + Fore.RED + "-%" + str(((round(float(added)/float(len(houraverages))*100)/100)/float(maxDollars))*100))
		lastprice = pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']
		onehourlowlast = one_hour_low
		onehourhighlast = one_hour_high
		fiftytwoweekaverage = fifty_two_week_average
		lasttotal = float(dollarsLeft) + (float(ownedAmount) * float(pd.DataFrame(stock_data_minute).iloc[minutes-720]['close_price']))
		#system('clear')
		


if len(sys.argv[1:]) > 2:
	TICKER = sys.argv[1:][1].upper()
	ACTION = sys.argv[1:][0]
	AMOUNT = sys.argv[1:][2]
	if ACTION.upper() == "-BUY":
		print("Buying " + AMOUNT + " of " + TICKER + "...")
		BUY(TICKER, AMOUNT)
	if ACTION.upper() == "-SELL":
		print("Selling " + AMOUNT + " of " + TICKER + "...")
		SELL(TICKER, AMOUNT)
	if ACTION.upper() == "-BUYC":
		print("Buying " + AMOUNT + " of crypto " + TICKER + "...")
		BUYC(TICKER, AMOUNT)
	if ACTION.upper() == "-SELLC":
		print("Selling " + AMOUNT + " of crypto " + TICKER + "...")
		SELLC(TICKER, AMOUNT)
	if ACTION.upper() == "-AUTO":
		print("Automatically trading " + TICKER + " using $" + AMOUNT)
		AUTO(TICKER, AMOUNT)
	if ACTION.upper() == "-AUTOCA":
		print("Automatically trading crypto " + TICKER + " using $" + AMOUNT)
		AUTOCA(TICKER, AMOUNT)
	if ACTION.upper() == "-AUTOCB":
		print("Automatically trading crypto " + "\033[1m" + TICKER + "\033[0m" + " using $" + "\033[1m" + AMOUNT + "\033[0m")
		AUTOCB(TICKER, AMOUNT)
	if ACTION.upper() == "-AUTOCC":
		print("Automatically trading crypto " + "\033[1m" + TICKER + "\033[0m" + " using $" + "\033[1m" + AMOUNT + "\033[0m")
		AUTOCC(TICKER, AMOUNT)
	if ACTION.upper() == "-AUTOCSIM":
		print("Automatically trading crypto " + "\033[1m" + TICKER + "\033[0m" + " using $" + "\033[1m" + AMOUNT + "\033[0m")
		AUTOCSIM(TICKER, AMOUNT)
		
else:
	ACTION = sys.argv[1:][0]
	if ACTION.upper() == "-HELP":
		print("Format:     mytrader -[action] [ticker] [amount]")
		print()
		print("-buy        Buys a certain amount of a given stock")
		print("-sell       Sells a certain amount of a given stock")
		print("-buyc       Buys a certain amount of a given cryptocurrency")
		print("-sellc      Sells a certain amount of a given cryptocurrency")
		print("-auto       Automatically trades a given stock for you")
		print("-autoca     Automatically trades a given cryptocurrency for you using strategy A")
		print("-autocb     Automatically trades a given cryptocurrency for you using strategy B")
		print("-autocc     Automatically trades a given cryptocurrency for you using strategy C")
		print("-autocsim   Tests an automatic trading algorithm based on previous prices")
		print("-help       Opens this help menu")
		exit()
	if ACTION.upper() == "-QUOTE":
		TICKER = sys.argv[1:][1].upper()
		QUOTE(TICKER)
print("Syntax error, try typing -help to learn more about the commands")
