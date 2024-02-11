from socket import *
import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
import time
import pickle
import threading

HOST = "localhost"
PORT = 5000

ADDRESS = (HOST, PORT)

BUFFSIZE = 1024

HEIGHT = 720
WIDTH = 1280


class Client:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.connect(ADDRESS)
        self.response = ""
        self.thread = None

    def SendToServer(self, message):
        time.sleep(0.1)
        message_pickled = pickle.dumps(message)
        self.server.sendall(message_pickled)

    def StartThread(self):
        self.thread = threading.Thread(target=self.ReceiveData)
        self.thread.start()
        self.thread.join()
        return self.response

    def ReceiveData(self):
        while True:
            response_pickled = self.server.recv(BUFFSIZE)
            self.response = pickle.loads(response_pickled)
            print(self.response)
            if self.response:
                break


class MainApp(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title_screen_name_text = None
        self.title("Bitcoiner")
        self.geometry("1280x720")
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)

        self.username = ""
        self.client_id = ""
        self.client = client

        self.login_screen_frame = LoginScreen(self)
        self.login_screen_frame.pack()

        self.welcome_screen_frame = None
        self.portfolio_screen_frame = None
        self.invest_screen_frame = None

    def SetUsername(self, username):
        self.username = username

    def SetClientId(self, client_id):
        self.client_id = client_id

    def CheckEmptyFields(self, string):
        if not bool(string.strip()):
            return True
        return False

    def LoginToWelcomePack(self):
        self.login_screen_frame.pack_forget()
        self.welcome_screen_frame = WelcomeScreen(self)
        self.welcome_screen_frame.pack()

    def WelcomeToPortfolioPack(self):
        self.welcome_screen_frame.pack_forget()
        self.portfolio_screen_frame = PortfolioScreen(self)
        self.portfolio_screen_frame.pack()

    def PortfolioToWelcomePack(self):
        self.portfolio_screen_frame.pack_forget()
        self.welcome_screen_frame = WelcomeScreen(self)
        self.welcome_screen_frame.pack()
    def WelcomeToInvestPack(self):
        self.welcome_screen_frame.pack_forget()
        self.invest_screen_frame = InvestScreen(self)
        self.invest_screen_frame.pack()

    def InvestToWelcomePack(self):
        self.invest_screen_frame.pack_forget()
        self.welcome_screen_frame = WelcomeScreen(self)
        self.welcome_screen_frame.pack()

    def CreateAccount(self, username, password):
        self.client.SendToServer("CreateAccount")
        self.client.SendToServer(username)
        self.client.SendToServer(password)
        return self.client.StartThread()

    def SetInitMoney(self, username, money):
        self.client.SendToServer("SetInitMoney")
        self.client.SendToServer(username)
        self.client.SendToServer(money)

    def CheckLogin(self, username, password):
        self.client.SendToServer("CheckLogin")
        self.client.SendToServer(username)
        self.client.SendToServer(password)
        return self.client.StartThread()

    def RetrieveUserInfo(self):
        self.client.SendToServer("RetrieveInfo")
        self.client.SendToServer(self.username)
        return self.client.StartThread()

    def DepositMoney(self, cash):
        self.client.SendToServer("DepositMoney")
        self.client.SendToServer(self.username)
        self.client.SendToServer(cash)

    def WithdrawMoney(self, cash):
        self.client.SendToServer("WithdrawMoney")
        self.client.SendToServer(self.username)
        self.client.SendToServer(cash)
        return self.client.StartThread()

    def BuyCrypto(self, value, amount_money, crypto):
        self.client.SendToServer("BuyCrypto")
        self.client.SendToServer(self.client_id)
        self.client.SendToServer(value)
        self.client.SendToServer(amount_money)
        self.client.SendToServer(crypto)
        return self.client.StartThread()

    def SellCrypto(self, value, amount_money, crypto):
        self.client.SendToServer("SellCrypto")
        self.client.SendToServer(self.client_id)
        self.client.SendToServer(value)
        self.client.SendToServer(amount_money)
        self.client.SendToServer(crypto)
        return self.client.StartThread()

    def RetrieveCryptoData(self):
        self.client.SendToServer("RetrieveCryptoData")
        return self.client.StartThread()

    def RetrieveTransactions(self):
        self.client.SendToServer("RetrieveTransactions")
        self.client.SendToServer(self.client_id)
        return self.client.StartThread()


class LoginScreen(tk.Frame):
    def __init__(self, main_app):
        super().__init__()

        self.main_app = main_app

        self.login_bgimg_open = Image.open("graphics/stockmarket.png")
        self.login_bgimg = ImageTk.PhotoImage(self.login_bgimg_open)

        self.login_titleimg_open = Image.open("graphics/bitcoiner2.png")
        self.login_titleimg = ImageTk.PhotoImage(self.login_titleimg_open)

        self.login_image_open = Image.open("graphics/LoginRect.png")
        self.login_image = ImageTk.PhotoImage(self.login_image_open)

        self.signup_image_open = Image.open("graphics/CreateAcc.png")
        self.signup_image = ImageTk.PhotoImage(self.signup_image_open)

        self.init_bal_image_open = Image.open("graphics/InitBal.png")
        self.init_bal_image = ImageTk.PhotoImage(self.init_bal_image_open)

        self.dollar_sign_image_open = Image.open("graphics/dollar_sign.png")
        self.dollar_sign_image = ImageTk.PhotoImage(self.dollar_sign_image_open)

        self.login_signin_button = None
        self.login_signup_button = None
        self.login_creatacc_button = None
        self.login_return_button = None
        self.login_entry_uname = None
        self.login_entry_pass = None
        self.init_entry_balance = None
        self.error_message_label = None

        self.username = None
        self.client_id = None

        self.login_canvas = tk.Canvas(self, width=self.login_bgimg.width(), height=self.login_bgimg.height())
        self.login_canvas.pack()

        self.LoginImages()

    def LoginImages(self):
        self.login_canvas.create_image(0, 0, anchor=tk.NW, image=self.login_bgimg)
        self.login_canvas.create_image((1280 - self.login_titleimg.width()) / 2, 20, anchor=tk.NW,
                                       image=self.login_titleimg)
        self.LoginWidgets()

    def LoginWidgets(self):
        self.login_canvas.create_image((1280 - self.login_image.width()) / 2, 160, anchor=tk.NW, image=self.login_image)

        self.login_entry_uname = tk.Entry(width=20, justify="center", font=font.Font(size=20))
        self.login_entry_uname.place(rely=0.57, relx=0.5, anchor=tk.CENTER)

        self.login_entry_pass = tk.Entry(width=20, justify="center", font=font.Font(size=20))
        self.login_entry_pass.place(rely=0.77, relx=0.5, anchor=tk.CENTER)

        self.login_signin_button = tk.Button(self, text="Login", command=self.LoginButtonPressed, width=20, height=2,
                                             font=font.Font(size=10))
        self.login_signin_button.place(relx=0.42, rely=0.9, anchor=tk.CENTER)

        self.login_signup_button = tk.Button(self, text="Sign Up", command=self.SignUpButtonPressed, width=20, height=2,
                                             font=font.Font(size=10))
        self.login_signup_button.place(relx=0.58, rely=0.9, anchor=tk.CENTER)

        self.error_message_label = tk.Label(self, text="",
                                            font=font.Font(size=20, weight="bold"),
                                            fg="red")

    def SignUpWidgets(self):
        self.login_canvas.create_image((1280 - self.login_image.width()) / 2, 160, anchor=tk.NW,
                                       image=self.signup_image)

        self.login_creatacc_button = tk.Button(self, text="Create Account", command=self.CreateAccButtonPressed,
                                               width=20, height=2, font=font.Font(size=10))
        self.login_creatacc_button.place(relx=0.58, rely=0.9, anchor=tk.CENTER)

        self.login_return_button = tk.Button(self, text="Return Back", command=self.ReturnBackButtonPressed, width=20,
                                             height=2, font=font.Font(size=10))
        self.login_return_button.place(relx=0.42, rely=0.9, anchor=tk.CENTER)

    def InitialMoneyWidgets(self):
        self.login_canvas.create_image((1280 - self.login_image.width()) / 2, 160, anchor=tk.NW,
                                       image=self.init_bal_image)

        self.login_creatacc_button = tk.Button(self, text="Confirm Amount", command=self.ConfirmButtonPressed,
                                               width=20, height=2, font=font.Font(size=10))
        self.login_creatacc_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        self.init_entry_balance = tk.Entry(width=20, justify="center", font=font.Font(size=20))
        self.init_entry_balance.place(rely=0.65, relx=0.51, anchor=tk.CENTER)

        self.login_canvas.create_image(450, 445, anchor=tk.NW, image=self.dollar_sign_image)

    def LoginButtonPressed(self):
        self.username = self.login_entry_uname.get()
        password = self.login_entry_pass.get()

        # checking for empty strings
        if not bool(self.username.strip()) or not bool(password.strip()):
            self.error_message_label.configure(text="Fields cannot be empty!")
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()
        self.username = self.username.strip()

        self.main_app.CheckLogin(self.username, password)

        response = self.main_app.CheckLogin(self.username, password)
        if response == "Account Found":
            self.main_app.SetUsername(self.username)

            self.main_app.LoginToWelcomePack()
        else:
            self.error_message_label.configure(text=response)
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return

    def SignUpButtonPressed(self):
        self.login_signin_button.destroy()
        self.login_signup_button.destroy()
        self.SignUpWidgets()

    def ReturnBackButtonPressed(self):
        self.login_return_button.destroy()
        self.login_creatacc_button.destroy()
        self.login_entry_pass.destroy()
        self.login_entry_uname.destroy()
        self.LoginWidgets()

    def CreateAccButtonPressed(self):
        self.username = self.login_entry_uname.get()
        password = self.login_entry_pass.get()

        # checking for empty strings
        if self.main_app.CheckEmptyFields(self.username) or self.main_app.CheckEmptyFields(password):
            self.error_message_label.configure(text="Fields cannot be empty!")
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()
        # removing empty spaces
        self.username = self.username.strip()

        response = self.main_app.CreateAccount(self.username, password)

        if response == "Username already exists":
            self.error_message_label.configure(text=response)
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return

        self.main_app.SetUsername(self.username)

        self.error_message_label.place_forget()

        self.login_return_button.destroy()
        self.login_creatacc_button.destroy()
        self.login_entry_uname.destroy()
        self.login_entry_pass.destroy()
        self.InitialMoneyWidgets()

    def ConfirmButtonPressed(self):
        amount = self.init_entry_balance.get()
        # Checking for empty strings
        if self.main_app.CheckEmptyFields(amount):
            self.error_message_label.configure(text="Field cannot be empty!")
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return
        # Checking if user inputs a number or not
        self.error_message_label.place_forget()
        try:
            amount = float(amount)
        except ValueError:
            amount = "string"

        if not (type(amount) is int or type(amount) is float):
            self.error_message_label.configure(text="Only digits allowed!")
            self.error_message_label.place(relx=0.5, rely=0.39, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        amount = amount

        self.main_app.SetInitMoney(self.username, amount)

        self.init_entry_balance.destroy()
        self.login_canvas.delete("all")
        self.main_app.LoginToWelcomePack()
class WelcomeScreen(tk.Frame):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self.welcome_bgimg_open = Image.open("graphics/WelcomePage.png")
        self.welcome_bgimg = ImageTk.PhotoImage(self.welcome_bgimg_open)

        self.balance_adjust_image_open = Image.open("graphics/With_Dep.png")
        self.balance_adjust_image = ImageTk.PhotoImage(self.balance_adjust_image_open)

        self.welcome_canvas = tk.Canvas(self, width=self.welcome_bgimg.width(), height=self.welcome_bgimg.height())
        self.welcome_canvas.pack()

        self.error_message_label = None

        self.invest_now_button = None
        self.portfolio_button = None
        self.balance_button = None
        self.confirm_balance = None
        self.balance_return_button = None
        self.withdraw_button = None
        self.deposit_button = None
        self.hold_image = None

        self.client_id_text = None
        self.name_text = None
        self.total_invest_text = None
        self.cash_text = None
        self.loss_gain = None
        self.user_info = None

        self.balance_entry = None
        self.cash_mode = None

        self.WelcomePage()

    def WelcomePage(self):
        self.welcome_canvas.create_image(0, 0, anchor=tk.NW, image=self.welcome_bgimg)
        self.WelcomePageWidgets()

    def UpdateCash(self):
        self.cash_text.place_forget()
        self.total_invest_text.place_forget()
        self.loss_gain.place_forget()
        self.WelcomePageWidgets()

    def WelcomePageWidgets(self):
        self.RetrieveUserInfo()
        self.main_app.SetClientId(self.user_info[0])

        self.client_id_text = self.welcome_canvas.create_text(530, 335, anchor=tk.NW, fill='white',
                                                              font=font.Font(size=20))
        self.welcome_canvas.itemconfig(self.client_id_text, text=self.user_info[0])

        self.name_text = self.welcome_canvas.create_text(530, 378, anchor=tk.NW, fill='white',
                                                         font=font.Font(size=20))
        self.welcome_canvas.itemconfig(self.name_text, text=self.user_info[1])

        self.total_invest_text = self.welcome_canvas.create_text(530, 430, anchor=tk.NW, fill='white',
                                                                 font=font.Font(size=20))
        self.welcome_canvas.itemconfig(self.total_invest_text, text=self.user_info[4])

        self.cash_text = self.welcome_canvas.create_text(530, 480, anchor=tk.NW, fill='white',
                                                         font=font.Font(size=20))
        self.welcome_canvas.itemconfig(self.cash_text, text=self.user_info[3])

        self.loss_gain = self.welcome_canvas.create_text(530, 520, anchor=tk.NW, fill='white',
                                                         font=font.Font(size=20))
        self.welcome_canvas.itemconfig(self.loss_gain, text=self.user_info[5])

        self.balance_button = tk.Button(self, text="Add/Remove Cash", command=self.BalanceButtonPressed, width=20,
                                        height=2,
                                        font=font.Font(size=10), )
        self.balance_button.place(relx=0.7, rely=0.9, anchor=tk.CENTER)

        self.portfolio_button = tk.Button(self, text="Portfolio", command=self.PortfolioButtonPressed, width=20,
                                          height=2,
                                          font=font.Font(size=10))
        self.portfolio_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        self.invest_now_button = tk.Button(self, text="Invest Now", command=self.InvestNowButtonPressed, width=20,
                                           height=2,
                                           font=font.Font(size=10))
        self.invest_now_button.place(relx=0.3, rely=0.9, anchor=tk.CENTER)

        self.error_message_label = tk.Label(self, text="",
                                            font=font.Font(size=20, weight="bold"),
                                            fg="red")

    def RetrieveUserInfo(self):
        response = self.main_app.RetrieveUserInfo()
        self.user_info = response[0]

    def BalanceButtonPressed(self):
        self.balance_button.destroy()
        self.portfolio_button.destroy()
        self.invest_now_button.destroy()
        self.hold_image = self.welcome_canvas.create_image((1280 - self.balance_adjust_image.width()) / 2, 50,
                                                           anchor=tk.NW,
                                                           image=self.balance_adjust_image)

        self.balance_entry = tk.Entry(width=20, justify="center", font=font.Font(size=20))
        self.balance_entry.place(rely=0.59, relx=0.5, anchor=tk.CENTER)

        self.confirm_balance = tk.Button(self, text="Confirm", command=self.BalanceConfirmButtonPressed,
                                         width=20, height=2, font=font.Font(size=10))
        self.confirm_balance.place(relx=0.58, rely=0.75, anchor=tk.CENTER)

        self.balance_return_button = tk.Button(self, text="Return Back", command=self.BalanceReturnButtonPressed,
                                               width=20,
                                               height=2, font=font.Font(size=10))
        self.balance_return_button.place(relx=0.42, rely=0.75, anchor=tk.CENTER)

        self.withdraw_button = tk.Button(self, text="Withdraw", command=self.WithdrawButtonPressed,
                                         width=20, height=2, font=font.Font(size=10))
        self.withdraw_button.place(relx=0.58, rely=0.42, anchor=tk.CENTER)

        self.deposit_button = tk.Button(self, text="Deposit", command=self.DepositButtonPressed,
                                        width=20, height=2, font=font.Font(size=10))
        self.deposit_button.place(relx=0.42, rely=0.42, anchor=tk.CENTER)

    def PortfolioButtonPressed(self):
        self.main_app.WelcomeToPortfolioPack()

    def InvestNowButtonPressed(self):
        self.main_app.WelcomeToInvestPack()

    def WithdrawButtonPressed(self):
        self.cash_mode = "WithdrawMoney"
        self.withdraw_button.destroy()
        self.deposit_button.destroy()

        self.withdraw_button = tk.Button(self, text="Withdraw", command=self.WithdrawButtonPressed,
                                         width=20, height=2, font=font.Font(size=10), bg="green")
        self.withdraw_button.place(relx=0.58, rely=0.42, anchor=tk.CENTER)

        self.deposit_button = tk.Button(self, text="Deposit", command=self.DepositButtonPressed,
                                        width=20, height=2, font=font.Font(size=10))
        self.deposit_button.place(relx=0.42, rely=0.42, anchor=tk.CENTER)

    def DepositButtonPressed(self):
        self.cash_mode = "DepositMoney"
        self.withdraw_button.destroy()
        self.deposit_button.destroy()

        self.withdraw_button = tk.Button(self, text="Withdraw", command=self.WithdrawButtonPressed,
                                         width=20, height=2, font=font.Font(size=10))
        self.withdraw_button.place(relx=0.58, rely=0.42, anchor=tk.CENTER)

        self.deposit_button = tk.Button(self, text="Deposit", command=self.DepositButtonPressed,
                                        width=20, height=2, font=font.Font(size=10), bg="green")
        self.deposit_button.place(relx=0.42, rely=0.42, anchor=tk.CENTER)

    def BalanceConfirmButtonPressed(self):
        cash = self.balance_entry.get()
        if self.main_app.CheckEmptyFields(cash):
            self.error_message_label.configure(text="Field cannot be empty!")
            self.error_message_label.place(relx=0.5, rely=0.53, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        try:
            cash = float(cash)
        except ValueError:
            cash = "string"

        if not (type(cash) is int or type(cash) is float):
            self.error_message_label.configure(text="Only digits allowed!")
            self.error_message_label.place(relx=0.5, rely=0.53, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        if self.cash_mode == "DepositMoney":
            self.error_message_label.place_forget()
            cash = self.balance_entry.get()
            self.main_app.DepositMoney(cash)
        elif self.cash_mode == "WithdrawMoney":
            self.error_message_label.place_forget()
            response = self.main_app.WithdrawMoney(cash)
            if response == "Not enough money in account":
                self.error_message_label.configure(text=response)
                self.error_message_label.place(relx=0.5, rely=0.53, anchor=tk.CENTER)
                return

        else:
            self.error_message_label.configure(text="Choose An Option!")
            self.error_message_label.place(relx=0.5, rely=0.53, anchor=tk.CENTER)
            return

        self.BalanceDestroyAll()

    def BalanceReturnButtonPressed(self):
        self.BalanceDestroyAll()

    def BalanceDestroyAll(self):
        self.error_message_label.place_forget()
        self.welcome_canvas.delete(self.hold_image)
        self.welcome_canvas.delete(self.cash_text)
        self.deposit_button.destroy()
        self.withdraw_button.destroy()
        self.balance_return_button.destroy()
        self.confirm_balance.destroy()
        self.balance_entry.destroy()
        self.WelcomePageWidgets()


class PortfolioScreen(tk.Frame):
    def __init__(self, main_app):
        super().__init__()
        self.row0_text = None
        self.row1_text = None
        self.row2_text = None
        self.row3_text = None
        self.row4_text = None
        self.row5_text = None
        self.row6_text = None
        self.row7_text = None
        self.row8_text = None
        self.main_app = main_app
        self.crypto_data = None
        self.user_portfolio = None
        self.user_edited_portfolio = []

        self.portfolio_image_open = Image.open("graphics/Portfolio.png")
        self.portfolio_image = ImageTk.PhotoImage(self.portfolio_image_open)

        self.return_button = None

        self.portfolio_canvas = tk.Canvas(self, width=self.portfolio_image.width(),
                                          height=self.portfolio_image.height())
        self.portfolio_canvas.pack()
        self.PortfolioImages()

    def PortfolioImages(self):
        self.portfolio_canvas.create_image(0, 0, anchor=tk.NW, image=self.portfolio_image)
        self.PortfolioWidgets()

    def PortfolioWidgets(self):
        self.return_button = tk.Button(self, text="Return", command=self.ReturnButtonPressed, width=10,
                                       height=2,
                                       font=font.Font(size=10), )
        self.return_button.place(relx=0.23, rely=0.96, anchor=tk.CENTER)

        self.RetrievePortfolio()
        if self.user_portfolio == " ":
            return
        self.ArrangePortfolio()

        self.row0_text = self.portfolio_canvas.create_text(270, 100, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))

        self.row1_text = self.portfolio_canvas.create_text(270, 165, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row2_text = self.portfolio_canvas.create_text(270, 230, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row3_text = self.portfolio_canvas.create_text(270, 295, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row4_text = self.portfolio_canvas.create_text(270, 360, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row5_text = self.portfolio_canvas.create_text(270, 420, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row6_text = self.portfolio_canvas.create_text(270, 485, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row7_text = self.portfolio_canvas.create_text(270, 550, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))
        self.row8_text = self.portfolio_canvas.create_text(270, 615, anchor=tk.NW, fill='white',
                                                           font=font.Font(size=20))

        self.portfolio_canvas.itemconfig(self.row0_text, text=self.user_edited_portfolio[0])
        self.portfolio_canvas.itemconfig(self.row1_text, text=self.user_edited_portfolio[1])
        self.portfolio_canvas.itemconfig(self.row2_text, text=self.user_edited_portfolio[2])
        self.portfolio_canvas.itemconfig(self.row3_text, text=self.user_edited_portfolio[3])
        self.portfolio_canvas.itemconfig(self.row4_text, text=self.user_edited_portfolio[4])
        self.portfolio_canvas.itemconfig(self.row5_text, text=self.user_edited_portfolio[5])
        self.portfolio_canvas.itemconfig(self.row6_text, text=self.user_edited_portfolio[6])
        self.portfolio_canvas.itemconfig(self.row7_text, text=self.user_edited_portfolio[7])
        self.portfolio_canvas.itemconfig(self.row8_text, text=self.user_edited_portfolio[8])

    def ArrangePortfolio(self):
        for row in self.user_portfolio:
            date_string = row[1].strftime('%Y-%m-%d')
            new_text = str(row[0]) + "          " + date_string + "         " + str(row[2]) + "               " + str(
                row[3]) + "          " + str(row[4])
            self.user_edited_portfolio.append(new_text)
        if len(self.user_portfolio) < 10:
            for i in range(len(self.user_portfolio), 9):
                self.user_edited_portfolio.append(" ")

    def RetrievePortfolio(self):
        self.user_portfolio = self.main_app.RetrieveTransactions()

    def ReturnButtonPressed(self):
        self.main_app.PortfolioToWelcomePack()


class InvestScreen(tk.Frame):
    def __init__(self, main_app):
        super().__init__()
        self.option_buy_sell = None
        self.option_money_amount = None
        self.sell_button = None
        self.buy_button = None
        self.quantity_button = None
        self.money_button = None
        self.view_return_button = None
        self.buy_sell_image = None
        self.buy_sell_image_open = None
        self.balance_adjust_image = None
        self.confirm_button = None
        self.money_amount_entry = None
        self.hold_image = None
        self.current_crypto = None
        self.y_gain = 100
        self.crypto_data = None
        self.crypto_name = []
        self.crypto_price = []
        self.crypto_id = []
        self.main_app = main_app

        self.crypto_name_text = None
        self.crypto_price_text = None

        self.invest_image_open = Image.open("graphics/Invest.png")
        self.invest_image = ImageTk.PhotoImage(self.invest_image_open)

        self.return_button = None

        self.view_button_1 = None
        self.view_button_2 = None
        self.view_button_3 = None
        self.view_button_4 = None
        self.view_button_5 = None
        self.view_button_6 = None
        self.view_button_7 = None
        self.view_button_8 = None
        self.view_button_9 = None

        self.error_message_label = None

        self.invest_canvas = tk.Canvas(self, width=self.invest_image.width(),
                                       height=self.invest_image.height())
        self.invest_canvas.pack()
        self.InvestImages()

    def InvestImages(self):
        self.invest_canvas.create_image(0, 0, anchor=tk.NW, image=self.invest_image)
        self.InvestWidgets()
        self.buy_sell_image_open = Image.open("graphics/BuySell.png")
        self.buy_sell_image = ImageTk.PhotoImage(self.buy_sell_image_open)

    def InvestWidgets(self):
        self.return_button = tk.Button(self, text="Return", command=self.ReturnButtonPressed, width=10,
                                       height=2, font=font.Font(size=10))

        self.error_message_label = tk.Label(self, text="",
                                            font=font.Font(size=20, weight="bold"),
                                            fg="red")

        self.view_button_1 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(0), font=font.Font(size=10),
                                       width=8,
                                       height=1)
        self.view_button_2 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(1), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_3 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(2), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_4 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(3), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_5 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(4), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_6 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(5), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_7 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(6), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_8 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(7), font=font.Font(size=10),
                                       width=8, height=1)
        self.view_button_9 = tk.Button(self, text="VIEW", command=lambda: self.CryptoIndex(8), font=font.Font(size=10),
                                       width=8, height=1)
        self.RetrieveCryptoData()

    def CryptoIndex(self, index):
        self.current_crypto = index
        self.BuySellCrypto()

    def RetrieveCryptoData(self):
        self.crypto_data = self.main_app.RetrieveCryptoData()

        for crypto in self.crypto_data:
            self.crypto_name.append(crypto[1])
            self.crypto_price.append(crypto[2])
            self.crypto_id.append(crypto[0])
        self.PlaceCryptoData()

    def PlaceCryptoData(self):
        for i in range(0, 9):
            self.crypto_name_text = self.invest_canvas.create_text(315, self.y_gain + self.y_gain / 1.559 * i,
                                                                   anchor=tk.NW, fill='white',
                                                                   font=font.Font(size=20))
            self.invest_canvas.itemconfig(self.crypto_name_text, text=self.crypto_name[i])

            self.crypto_price_text = self.invest_canvas.create_text(595, self.y_gain + self.y_gain / 1.559 * i,
                                                                    anchor=tk.NW, fill='white',
                                                                    font=font.Font(size=20))
            self.invest_canvas.itemconfig(self.crypto_price_text, text=self.crypto_price[i])

        self.view_button_1.place(relx=0.713, rely=0.165, anchor=tk.CENTER)
        self.view_button_2.place(relx=0.713, rely=0.255, anchor=tk.CENTER)
        self.view_button_3.place(relx=0.713, rely=0.345, anchor=tk.CENTER)
        self.view_button_4.place(relx=0.713, rely=0.435, anchor=tk.CENTER)
        self.view_button_5.place(relx=0.713, rely=0.520, anchor=tk.CENTER)
        self.view_button_6.place(relx=0.713, rely=0.610, anchor=tk.CENTER)
        self.view_button_7.place(relx=0.713, rely=0.700, anchor=tk.CENTER)
        self.view_button_8.place(relx=0.713, rely=0.790, anchor=tk.CENTER)
        self.view_button_9.place(relx=0.713, rely=0.880, anchor=tk.CENTER)
        self.return_button.place(relx=0.23, rely=0.96, anchor=tk.CENTER)

    def BuySellCrypto(self):
        self.view_button_1.place_forget()
        self.view_button_2.place_forget()
        self.view_button_3.place_forget()
        self.view_button_4.place_forget()
        self.view_button_5.place_forget()
        self.view_button_6.place_forget()
        self.view_button_7.place_forget()
        self.view_button_8.place_forget()
        self.view_button_9.place_forget()
        self.return_button.place_forget()
        self.hold_image = self.invest_canvas.create_image((1280 - self.buy_sell_image.width()) / 2, 50,
                                                          anchor=tk.NW,
                                                          image=self.buy_sell_image)

        self.money_amount_entry = tk.Entry(width=20, justify="center", font=font.Font(size=20))
        self.money_amount_entry.place(rely=0.59, relx=0.5, anchor=tk.CENTER)

        self.confirm_button = tk.Button(self, text="Confirm", command=self.ConfirmButtonPressed,
                                        width=20, height=2, font=font.Font(size=10))
        self.confirm_button.place(relx=0.58, rely=0.75, anchor=tk.CENTER)

        self.view_return_button = tk.Button(self, text="Return Back", command=self.ViewReturnButtonPressed,
                                            width=20,
                                            height=2, font=font.Font(size=10))
        self.view_return_button.place(relx=0.42, rely=0.75, anchor=tk.CENTER)

        self.money_button = tk.Button(self, text="Money", command=self.MoneyButtonPressed,
                                      width=20, height=2, font=font.Font(size=10))
        self.money_button.place(relx=0.58, rely=0.42, anchor=tk.CENTER)

        self.quantity_button = tk.Button(self, text="Amount", command=self.AmountButtonPressed,
                                         width=20, height=2, font=font.Font(size=10))
        self.quantity_button.place(relx=0.42, rely=0.42, anchor=tk.CENTER)

        self.sell_button = tk.Button(self, text="Sell", command=self.SellButtonPressed,
                                     width=20, height=2, font=font.Font(size=10))
        self.sell_button.place(relx=0.42, rely=0.32, anchor=tk.CENTER)
        self.buy_button = tk.Button(self, text="Buy", command=self.BuyButtonPressed,
                                    width=20, height=2, font=font.Font(size=10))
        self.buy_button.place(relx=0.58, rely=0.32, anchor=tk.CENTER)

    def ViewReturnButtonPressed(self):
        self.RemoveBuySellWindow()

    def BuyButtonPressed(self):
        self.option_buy_sell = "Buy"
        self.buy_button.configure(bg="green")
        self.sell_button.configure(bg="grey94")

    def SellButtonPressed(self):
        self.option_buy_sell = "Sell"
        self.sell_button.configure(bg="green")
        self.buy_button.configure(bg="grey94")

    def MoneyButtonPressed(self):
        self.option_money_amount = "Money"
        self.money_button.configure(bg="green")
        self.quantity_button.configure(bg="grey94")

    def AmountButtonPressed(self):
        self.option_money_amount = "Amount"
        self.quantity_button.configure(bg="green")
        self.money_button.configure(bg="grey94")

    def ReturnButtonPressed(self):
        self.main_app.InvestToWelcomePack()

    def ConfirmButtonPressed(self):
        value = self.money_amount_entry.get()

        if self.option_buy_sell is None:
            self.error_message_label.configure(text="Select Buy Or Sell")
            self.error_message_label.place(relx=0.5, rely=0.525, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        if self.option_money_amount is None:
            self.error_message_label.configure(text="Select Money or Amount")
            self.error_message_label.place(relx=0.5, rely=0.525, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        if self.main_app.CheckEmptyFields(value):
            self.error_message_label.configure(text="Fields cannot be empty!")
            self.error_message_label.place(relx=0.5, rely=0.525, anchor=tk.CENTER)
            return

        self.error_message_label.place_forget()

        try:
            value = float(value)
        except ValueError:
            value = "string"
        if not (type(value) is int or type(value) is float):
            self.error_message_label.configure(text="Only digits allowed!")
            self.error_message_label.place(relx=0.5, rely=0.525, anchor=tk.CENTER)
            return
        self.error_message_label.place_forget()

        if self.option_buy_sell == "Buy":
            response = self.main_app.BuyCrypto(value, self.option_money_amount, self.crypto_id[self.current_crypto])
        else:
            response = self.main_app.SellCrypto(value, self.option_money_amount, self.crypto_id[self.current_crypto])
        if response != "Transaction Successful!":
            self.error_message_label.configure(text=response)
            self.error_message_label.place(relx=0.5, rely=0.525, anchor=tk.CENTER)
            return
        self.RemoveBuySellWindow()

    def RemoveBuySellWindow(self):
        self.invest_canvas.delete(self.hold_image)
        self.error_message_label.place_forget()
        self.sell_button.place_forget()
        self.buy_button.place_forget()
        self.money_amount_entry.place_forget()
        self.money_button.place_forget()
        self.confirm_button.place_forget()
        self.quantity_button.place_forget()
        self.view_return_button.place_forget()
        self.RetrieveCryptoData()


def Main():
    client = Client()
    app = MainApp(client)
    app.mainloop()
Main()