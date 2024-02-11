import time
from socket import *
import mysql.connector
import pickle
import threading
from datetime import date

HOST = "localhost"
PORT = 5000

ADDRESS = (HOST, PORT)

BUFFSIZE = 1024

CRYPTO_PRICE = ""


class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.cursor = None
        self.mydb = None
        self.sql = None
        self.val = None
        self.date = date.today()
        self.records = None

    def ConnectToDatabase(self):
        self.mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.mydb.cursor()

    def CreateAccount(self, username, password):
        self.SelectAllFromClient()
        # usernames are case-insensitive
        username = username.lower()
        for record in self.records:
            if record[1] == username:
                message = "Username already exists"
                return message
        # hash creates a unique id for each username
        client_id = abs(hash(username))
        message = "Account created"
        sql = "INSERT INTO client (client_id, username, password) VALUES (%s, %s, %s)"
        values = (client_id, username, password)
        self.cursor.execute(sql, values)
        self.mydb.commit()
        return message

    def CheckUsernamePassword(self):
        self.SelectAllFromClient()

    def SetInitMoney(self, username, money):
        sql = "UPDATE client SET cash = %s WHERE username = %s"
        values = (money, username)
        self.cursor.execute(sql, values)
        self.mydb.commit()

    def CheckLogin(self, username, password):
        result_uname = self.ExistsInClient(username, "username")
        if not result_uname:
            return "Username does not exist!"

        # Now, use the username's result to check the password
        result_pass = self.ExistsInClient(password, "password")
        if not result_pass:
            return "Wrong Password!"

        return "Account Found"

    def ExistsInClient(self, value, column):
        sql = f"SELECT * FROM client WHERE {column} = %s"
        values = (value,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()

        return result

    def RetrieveUserInfo(self, username):
        sql = "SELECT * FROM client WHERE username = %s"
        values = (username,)
        self.cursor.execute(sql, values)
        result = self.cursor.fetchall()
        return result

    def DepositMoney(self, username, cash):
        sql = "SELECT cash FROM client WHERE username = %s"
        values = (username,)
        self.cursor.execute(sql, values)

        old_cash = self.cursor.fetchall()
        old_cash = old_cash[0]
        cash = float(cash)
        new_cash = old_cash[0] + cash
        sql = "UPDATE client SET cash = %s WHERE username=%s"
        values = (new_cash, username)
        self.cursor.execute(sql, values)
        self.mydb.commit()

    def WithdrawMoney(self, username, cash):
        sql = "SELECT cash FROM client WHERE username = %s"
        values = (username,)
        self.cursor.execute(sql, values)

        old_cash = self.cursor.fetchall()
        old_cash = old_cash[0]
        cash = float(cash)
        new_cash = old_cash[0] - cash
        if new_cash < 0:
            return "Not enough money in account"

        sql = "UPDATE client SET cash = %s WHERE username=%s"
        values = (new_cash, username)
        self.cursor.execute(sql, values)
        self.mydb.commit()
        return " "

    def SelectAllFromClient(self):
        self.sql = "Select * FROM client"
        self.cursor.execute(self.sql)
        self.records = self.cursor.fetchall()

    def SelectAllFromCrypto(self):
        self.sql = f"Select Crypto_ID, Crypto_Name, {CRYPTO_PRICE} FROM crypto"
        self.cursor.execute(self.sql)
        self.records = self.cursor.fetchall()
        return self.records

    def RetrieveTransactions(self, client_id):
        rows = []
        sql = "Select Crypto_ID, Date, Type, Quantity, Price FROM Transactions WHERE client_id = %s ORDER BY Transac_ID DESC"
        values = (client_id,)
        self.cursor.execute(sql, values)
        self.records = self.cursor.fetchall()
        if len(self.records) >= 9:
            max_len = 9
        elif len(self.records) == 0:
            return " "
        else:
            max_len = len(self.records)

        for i in range(0, max_len):
            rows.append(self.records[i])

        return rows

    def BuyCrypto(self, client_id, value, amount_money, crypto_id):
        new_cash = None
        amount = None
        sql = "SELECT cash FROM client WHERE client_id = %s"
        values = (client_id,)
        self.cursor.execute(sql, values)
        client_cash = self.cursor.fetchall()
        client_cash = client_cash[0]
        client_cash = client_cash[0]

        sql = f"SELECT {CRYPTO_PRICE} FROM crypto WHERE crypto_id = %s"
        values = (crypto_id,)
        self.cursor.execute(sql, values)
        crypto_value = self.cursor.fetchall()
        crypto_value = crypto_value[0]
        crypto_value = crypto_value[0]
        if amount_money == "Amount":
            total_value = crypto_value * value
            if client_cash < total_value:
                return "Not enough money!"
            self.RecordAmount(client_id, crypto_id, value)
            new_cash = client_cash - total_value
            sql = "Select GainsLoss From client WHERE client_id=%s"
            values = (client_id,)
            self.cursor.execute(sql, values)
            current_gain_loss = self.cursor.fetchall()
            current_gain_loss = current_gain_loss[0]
            current_gain_loss = current_gain_loss[0]

            sql = "UPDATE client SET GainsLoss = %s WHERE client_id=%s"
            if type(current_gain_loss) is None:
                values = (current_gain_loss - total_value, client_id)
            else:
                values = (-total_value, client_id)

            self.cursor.execute(sql, values)
            self.mydb.commit()
            sql = "UPDATE client SET TotalInvestment = %s WHERE client_id=%s"
            if type(current_gain_loss) is None:
                values = (current_gain_loss + total_value, client_id)
            else:
                values = (total_value, client_id)
            self.cursor.execute(sql, values)
            self.mydb.commit()

            amount = value
        if amount_money == "Money":
            if value < crypto_value:
                return "Not enough money!"
            new_cash = client_cash - value
            amount = value / crypto_value

            sql = "Select GainsLoss From client WHERE client_id=%s"
            values = (client_id,)
            self.cursor.execute(sql, values)
            current_gain_loss = self.cursor.fetchall()
            current_gain_loss = current_gain_loss[0]
            current_gain_loss = current_gain_loss[0]

            sql = "UPDATE client SET GainsLoss = %s WHERE client_id=%s"
            if type(current_gain_loss) is None:
                values = (current_gain_loss - value, client_id)
            else:
                values = (-value, client_id)

            self.cursor.execute(sql, values)
            self.mydb.commit()
            sql = "UPDATE client SET TotalInvestment = %s WHERE client_id=%s"
            if type(current_gain_loss) is None:
                values = (current_gain_loss + value, client_id)
            else:
                values= (value, client_id)
            self.cursor.execute(sql, values)
            self.mydb.commit()
            self.RecordAmount(client_id, crypto_id, amount)

        sql = "UPDATE client SET cash = %s WHERE client_id=%s"
        values = (new_cash, client_id)
        self.HandleTransaction(client_id, crypto_id, "BUY ", amount, crypto_value)
        self.cursor.execute(sql, values)
        self.mydb.commit()
        return " "

    def RecordAmount(self, client_id, crypto_id, amount):
        sql = "SELECT * FROM Client_Crypto WHERE Client_ID = %s AND Crypto_ID = %s"
        values = (client_id, crypto_id)
        self.cursor.execute(sql, values)
        rows = self.cursor.fetchall()

        if len(rows) > 0:
            rows = rows[0]
            amount = rows[2] + amount
            sql = "UPDATE Client_Crypto SET amount=%s WHERE Client_ID=%s AND Crypto_ID=%s"
            values = (amount, client_id, crypto_id)
            self.cursor.execute(sql, values)
        else:
            sql = "INSERT INTO Client_Crypto (client_id, crypto_id, amount) VALUES (%s, %s, %s)"
            values = (client_id, crypto_id, amount)
            self.cursor.execute(sql, values)
        self.mydb.commit()

    def SellCrypto(self, client_id, value, amount_money, crypto_id):
        amount = None
        cash = None
        sql = f"SELECT {CRYPTO_PRICE} FROM crypto WHERE crypto_id = %s"
        values = (crypto_id,)
        self.cursor.execute(sql, values)
        rows = self.cursor.fetchall()
        rows = rows[0]
        current_price = rows[0]

        sql = "SELECT amount FROM client_crypto WHERE crypto_id = %s AND client_id = %s"
        values = (crypto_id, client_id)
        self.cursor.execute(sql, values)
        rows = self.cursor.fetchall()
        if len(rows) < 0:
            return "You do not have any!"
        rows = rows[0]
        current_amount = rows[0]
        sql = "SELECT cash FROM client WHERE client_id = %s"
        values = (client_id,)
        self.cursor.execute(sql, values)
        client_cash = self.cursor.fetchall()
        client_cash = client_cash[0]
        client_cash = client_cash[0]

        if amount_money == "Amount":
            amount = value
            cash = value * current_price
        elif amount_money == "Money":
            cash = value
            amount = value / current_price

        sql = "Select GainsLoss From client WHERE client_id=%s"
        values = (client_id,)
        self.cursor.execute(sql, values)
        current_gain_loss = self.cursor.fetchall()
        current_gain_loss = current_gain_loss[0]
        current_gain_loss = current_gain_loss[0]

        sql = "UPDATE client SET GainsLoss = %s WHERE client_id=%s"
        values = (current_gain_loss + cash, client_id)
        self.cursor.execute(sql, values)
        self.mydb.commit()

        sql = "UPDATE client SET TotalInvestment = %s WHERE client_id=%s"
        if type(current_gain_loss) is None:
            values = (current_gain_loss - value, client_id)
        else:
            values = (value, client_id)
        self.cursor.execute(sql, values)
        self.mydb.commit()

        if amount > current_amount:
            return "Not enough in portfolio!"
        new_amount = current_amount - amount
        new_cash = client_cash + cash

        sql = "UPDATE client SET cash = %s WHERE client_id=%s"
        values = (new_cash, client_id)
        self.cursor.execute(sql, values)
        self.mydb.commit()

        sql = "UPDATE client_crypto SET amount = %s WHERE client_id=%s and crypto_id = %s"
        values = (new_amount, client_id, crypto_id)
        self.cursor.execute(sql, values)
        self.mydb.commit()

        self.HandleTransaction(client_id, crypto_id, "SELL", amount, current_price)
        return " "

    def HandleTransaction(self, client_id, crypto_id, transac_type, amount, price):
        sql = "SELECT Transac_ID FROM transactions WHERE Client_ID = %s ORDER BY Transac_ID DESC"
        values = (client_id,)
        self.cursor.execute(sql, values)
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            rows = rows[0]
            new_transac_id = rows[0] + 1
        else:
            new_transac_id = 1

        sql = "INSERT INTO transactions (client_id, crypto_id, transac_id,date,type,quantity,price) VALUES (%s, " \
              "%s, %s, %s, %s, %s,%s)"
        values = (client_id, crypto_id, new_transac_id, self.date, transac_type, amount, price)
        self.cursor.execute(sql, values)
        self.mydb.commit()


class Server:
    def __init__(self, database):

        self.database = database

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(ADDRESS)
        self.server.listen(1)
        self.client = None
        self.address = None
        self.request = None

    def InitialiseConnection(self):
        while True:
            print("Waiting for connection")
            (self.client, self.address) = self.server.accept()
            if self.client is not None:
                break
        print("Connected!")
        self.MainLoop()

    def MainLoop(self):
        while True:
            request_pickled = self.client.recv(BUFFSIZE)
            self.request = pickle.loads(request_pickled)
            if self.request == "CreateAccount":
                self.CreateAccount()
            elif self.request == "CheckLogin":
                self.CheckLogin()
            elif self.request == "SetInitMoney":
                self.SetInitMoney()
            elif self.request == "RetrieveInfo":
                self.RetrieveUserInfo()
            elif self.request == "DepositMoney":
                self.DepositMoney()
            elif self.request == "WithdrawMoney":
                self.WithdrawMoney()
            elif self.request == "RetrieveCryptoData":
                self.RetrieveCryptoData()
            elif self.request == "BuyCrypto":
                self.BuyCrypto()
            elif self.request == "SellCrypto":
                self.SellCrypto()
            elif self.request == "RetrieveTransactions":
                self.RetrieveTransactions()
            elif self.request == "UpdateTotalInvestValue":
                self.UpdateTotalInvestValue()

    def UpdateTotalInvestValue(self):
        client_id_pickled = self.client.recv(BUFFSIZE)
        client_id = pickle.loads(client_id_pickled)
        self.database.UpdateTotalInvestValue(client_id)

    def CreateAccount(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        password_pickled = self.client.recv(BUFFSIZE)
        password = pickle.loads(password_pickled)

        outcome = self.database.CreateAccount(username, password)
        outcome_pickled = pickle.dumps(outcome)
        self.client.sendall(outcome_pickled)

    def SetInitMoney(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        money_pickled = self.client.recv(BUFFSIZE)
        money = pickle.loads(money_pickled)

        self.database.SetInitMoney(username, money)

    def CheckLogin(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        password_pickled = self.client.recv(BUFFSIZE)
        password = pickle.loads(password_pickled)

        outcome = self.database.CheckLogin(username, password)
        outcome_pickled = pickle.dumps(outcome)
        self.client.sendall(outcome_pickled)

    def RetrieveUserInfo(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        info = self.database.RetrieveUserInfo(username)
        info_pickled = pickle.dumps(info)
        self.client.sendall(info_pickled)

    def DepositMoney(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        cash_pickled = self.client.recv(BUFFSIZE)
        cash = pickle.loads(cash_pickled)
        self.database.DepositMoney(username, cash)

    def WithdrawMoney(self):
        username_pickled = self.client.recv(BUFFSIZE)
        username = pickle.loads(username_pickled)
        cash_pickled = self.client.recv(BUFFSIZE)
        cash = pickle.loads(cash_pickled)
        response = self.database.WithdrawMoney(username, cash)
        response_pickled = pickle.dumps(response)
        self.client.sendall(response_pickled)

    def RetrieveCryptoData(self):
        crypto_data = self.database.SelectAllFromCrypto()
        crypto_data_pickle = pickle.dumps(crypto_data)
        self.client.sendall(crypto_data_pickle)

    def BuyCrypto(self):
        client_id_pickled = self.client.recv(BUFFSIZE)
        client_id = pickle.loads(client_id_pickled)
        value_pickled = self.client.recv(BUFFSIZE)
        value = pickle.loads(value_pickled)
        amount_money_pickled = self.client.recv(BUFFSIZE)
        amount_money = pickle.loads(amount_money_pickled)
        crypto_id_pickled = self.client.recv(BUFFSIZE)
        crypto_id = pickle.loads(crypto_id_pickled)
        response = self.database.BuyCrypto(client_id, value, amount_money, crypto_id)
        response_pickled = pickle.dumps(response)
        self.client.sendall(response_pickled)

    def SellCrypto(self):
        client_id_pickled = self.client.recv(BUFFSIZE)
        client_id = pickle.loads(client_id_pickled)
        value_pickled = self.client.recv(BUFFSIZE)
        value = pickle.loads(value_pickled)
        amount_money_pickled = self.client.recv(BUFFSIZE)
        amount_money = pickle.loads(amount_money_pickled)
        crypto_id_pickled = self.client.recv(BUFFSIZE)
        crypto_id = pickle.loads(crypto_id_pickled)
        response = self.database.SellCrypto(client_id, value, amount_money, crypto_id)
        response_pickled = pickle.dumps(response)
        self.client.sendall(response_pickled)

    def RetrieveTransactions(self):
        client_id_pickled = self.client.recv(BUFFSIZE)
        client_id = pickle.loads(client_id_pickled)
        response = self.database.RetrieveTransactions(client_id)
        response_pickled = pickle.dumps(response)
        self.client.sendall(response_pickled)


def Main():
    crypto_adjust_thread = threading.Thread(target=CryptoPriceAdjust)
    crypto_adjust_thread.start()
    database = Database("localhost", "root", "22667121", "crypto")
    database.ConnectToDatabase()
    server = Server(database)
    server.InitialiseConnection()


def CryptoPriceAdjust():
    current_state = 1
    global CRYPTO_PRICE
    CRYPTO_PRICE = "VALUE" + str(current_state)
    while True:
        time.sleep(15)
        if current_state == 5:
            current_state = 1
        else:
            current_state += 1
        CRYPTO_PRICE = "VALUE" + str(current_state)
        print(current_state)


Main()
