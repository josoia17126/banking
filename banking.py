#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 22:21:42 2020

@author: apple
"""

import random
import sys
import sqlite3

conn = sqlite3.connect('card.s3db', timeout=10)
cur = conn.cursor()

try:
    cur.execute('drop table if exists card')
    cur.execute('CREATE TABLE card(id INTEGER,number TEXT,PIN TEXT,Balance INTEGER DEFAULT 0)')
except sqlite3.OperationalError:
    pass
conn.commit()

def checkLuhn(purportedCC=''):
        sum_ = 0
        parity = len(purportedCC) % 2
        for i, digit in enumerate([int(x) for x in purportedCC]):
            if i % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum_ += digit
        return sum_ % 10 == 0
    
class banking:
    def __init__(self):
        self.balance = 0

    def generate_pin(self):
        random_str = []
        for i in range(4):
            random_str.append(str(random.randint(0, 9)))
        return "".join(random_str)

    def card_number(self):
        IIN = '400000'
        random_str = [IIN]
        count = 0
        for i in range(9):
            digit = str(random.randint(0, 9))
            random_str.append(digit)
            if i % 2 == 1:
                count += int(digit)
            else:
                if int(digit) > 4:
                    count += int(digit) * 2 - 9
                else:
                    count += int(digit) * 2
        count += 8
        last_digit = (10 - count % 10) % 10
        random_str.append(str(last_digit))
        return ''.join(random_str)

    def operation(self):
        print('Enter your card number:')
        enter_number = int(input())
        print('Enter your PIN:')
        enter_pin = input()
        cur = conn.cursor()
        cur.execute('SELECT * FROM card WHERE number = ?', (enter_number,))
        conn.commit()
        result = cur.fetchone()
        if (result is not None) and enter_pin == list(result)[2]:
            print('You have successfully logged in!')
            while True:
                print('''1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit''')
                order = input()
                if order == '0':
                    print('Bye!')
                    sys.exit()
                elif order == '1':
                    cur = conn.cursor()
                    cur.execute('SELECT Balance FROM card WHERE number = ?', (enter_number,))
                    balance = list(cur.fetchone())[0]
                    print('Balance: ' + str(balance))
                elif order == '2':
                    print('Enter income:')
                    income = int(input())
                    cur = conn.cursor()
                    cur.execute('SELECT Balance FROM card WHERE number = ?', (enter_number,))
                    balance = list(cur.fetchone())[0]
                    balance = income + int(balance)
                    cur.execute('UPDATE card SET Balance = ? WHERE number = ?', (balance, enter_number))
                    print('Income was added!')
                    conn.commit()
                elif order == '3':
                    print('Transfer')
                    print('Enter card number:')
                    cnum = input()
                    if checkLuhn(cnum) == True:
                        cur = conn.cursor()
                        cur.execute('SELECT number FROM card')
                        card_list = list(cur.fetchall())
                        conn.commit()
                        if (cnum,) in card_list and int(cnum) != enter_number:
                            print('Enter how much money you want to transfer:')
                            money = int(input())
                            cur = conn.cursor()
                            cur.execute('SELECT Balance FROM card WHERE number = ?', (enter_number,))
                            result1 = list(cur.fetchone())[0]
                            cur.execute('SELECT Balance FROM card WHERE number = ?', (cnum,))
                            result2 = list(cur.fetchone())[0]
                            conn.commit()
                            if int(result1) >= money:
                                new_money1 = int(result1) - money
                                new_money2 = int(result2) + money
                                cur = conn.cursor()
                                cur.execute('UPDATE card SET Balance = ? WHERE number = ?', (new_money1, enter_number))
                                cur.execute('UPDATE card SET Balance = ? WHERE number = ?', (new_money2, cnum))
                                conn.commit()
                                print('Success!')
                            else:
                                print('Not enough money!')
                        elif int(cnum) == enter_number:
                            print("You can't transfer money to the same account!")
                        else:
                            print('Such a card does not exist.')
                    else:
                        print('Probably you made a mistake in the card number. Please try again!')
                elif order == '4':
                    cur = conn.cursor()
                    cur.execute('DELETE FROM card WHERE number = ?', (enter_number,))
                    conn.commit()
                    print('The account has been closed!')
                    banking.start()
                elif order == '5':
                    print('You have successfully logged out!')
                    banking.start()
                else:
                    continue
        else:
            print('Wrong card number or PIN!')
            conn.close()
            
    def start(self):
        while True:
            print('''1. Create an account
2. Log into account
0. Exit''')
            order = input()
            if order == '0':
                print('Bye!')
                sys.exit()
            elif order == '1':
                print('Your card has been created')
                print('Your card number:')
                card_number = banking.card_number()
                print(card_number)
                print('Your card PIN:')
                generate_pin = banking.generate_pin()
                print(generate_pin)
                cur = conn.cursor()
                cur.execute('INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);', (card_number, generate_pin, 0))
                conn.commit()
            elif order == '2':
                banking.operation()
            else:
                continue

banking = banking()
banking.start()
conn.close()