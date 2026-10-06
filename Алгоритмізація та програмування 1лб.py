import random
from datetime import datetime


class Account:

    def __init__(self, balance, pin, iban=None):
        if iban is None:
            random_digits = str(random.randint(100000000000000000, 999999999999999999))
            self.iban = "UA8930000100000" + random_digits
        else:
            self.iban = iban

        self.balance = balance
        self.pin = str(pin)

    def verify_pin(self, entered_pin):
        return self.pin == str(entered_pin)

    def withdraw(self, amount):
        if amount <= 0:
            return False

        if amount > self.balance:
            return False

        self.balance = self.balance - amount
        return True

    def deposit(self, amount):
        self.balance = self.balance + amount


class SavingsAccount(Account):

    def __init__(self, balance, percent, pin, iban=None):
        super().__init__(balance, pin, iban)
        self.percent = percent

    def add_percent(self):
        bonus = self.balance * (self.percent / 100)
        self.balance = self.balance + bonus
        print("Нараховано відсотки: " + str(bonus) + " грн")


class Client:

    def __init__(self, name):
        self.name = name
        self.client_accounts = []

    def add_account(self, account):
        self.client_accounts.append(account)


class Transaction:

    def __init__(self, sender, receiver, amount, status):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.status = status
        self.date = datetime.now()


class Bank:

    def __init__(self):
        self.accounts = {}
        self.transactions = []

    def add(self, account):
        account_key = account.iban
        self.accounts[account_key] = account

    def atm_deposit(self, iban):
        if iban not in self.accounts:
            print("Рахунок не знайдено")
            return

        amount_str = input("Введіть суму для поповнення в банкоматі: ")
        amount = float(amount_str)

        if amount <= 0:
            print("Некоректна сума")
            return

        account = self.accounts[iban]
        account.deposit(amount)

        log = Transaction("ATM", iban, amount, "Успішно")
        self.transactions.append(log)
        print("Банкомат: Рахунок поповнено на " + str(amount) + " грн")

    def atm_withdraw(self, iban):
        if iban not in self.accounts:
            print("Рахунок не знайдено")
            return

        account = self.accounts[iban]
        user_pin = input("Введіть PIN-код картки для зняття: ")

        if account.verify_pin(user_pin) == False:
            print("Невірний PIN-код! Операцію зняття скасовано.")
            log = Transaction(iban, "ATM", 0, "Відхилено (Невірний PIN)")
            self.transactions.append(log)
            return

        amount_str = input("Введіть суму для зняття з банкомату: ")
        amount = float(amount_str)

        success = account.withdraw(amount)

        if success == True:
            log = Transaction(iban, "ATM", amount, "Успішно")
            self.transactions.append(log)
            print("Банкомат: Заберіть ваші " + str(amount) + " грн")
        else:
            log = Transaction(iban, "ATM", amount, "Відхилено")
            self.transactions.append(log)
            print("Банкомат: Недостатньо коштів або некоректна сума")

    def transfer(self, sender_iban, receiver_iban, amount):
        if sender_iban == receiver_iban:
            print("Переказ на той самий рахунок заборонено")
            return

        if sender_iban not in self.accounts:
            print("Рахунок відправника не знайдено")
            return

        if receiver_iban not in self.accounts:
            print("Рахунок отримувача не знайдено")
            return

        sender_account = self.accounts[sender_iban]
        receiver_account = self.accounts[receiver_iban]

        user_pin = input("Введіть PIN-код відправника для підтвердження переказу: ")

        if sender_account.verify_pin(user_pin) == False:
            print("Невірний PIN-код! Переказ скасовано.")
            failed_log = Transaction(sender_iban, receiver_iban, amount, "Відхилено (Невірний PIN)")
            self.transactions.append(failed_log)
            return

        fee = amount * 0.01
        total_amount = amount + fee

        success = sender_account.withdraw(total_amount)

        if success == True:
            receiver_account.deposit(amount)

            new_log = Transaction(sender_iban, receiver_iban, amount, "Успішно")
            self.transactions.append(new_log)

            print("Переказ виконано")
        else:
            failed_log = Transaction(sender_iban, receiver_iban, amount, "Відхилено")
            self.transactions.append(failed_log)

            print("Переказ відхилено")


client1 = Client("Максим")

account1 = Account(balance=1000, pin="1234", iban="UA893000010000011111111111111")
account2 = SavingsAccount(balance=200, percent=5, pin="4321", iban="UA893000010000022222222222222")

client1.add_account(account1)
client1.add_account(account2)

account2.add_percent()

my_bank = Bank()
my_bank.add(account1)
my_bank.add(account2)

print("\n--- ТЕСТ БАНКОМАТУ ---")
print("IBAN рахунку 1: " + account1.iban)

my_bank.atm_deposit(account1.iban)
my_bank.atm_withdraw(account1.iban)

print("\n--- ТЕСТ ПЕРЕКАЗІВ МІЖ РАХУНКАМИ ---")
my_bank.transfer(account1.iban, account2.iban, 350)

successful_count = 0

for item in my_bank.transactions:
    if item.status == "Успішно":
        successful_count = successful_count + 1

print("\n--- ПІДСУМОК ---")
print("Клієнт: " + client1.name)
print("Баланс 1: " + str(account1.balance) + " грн")
print("Баланс 2: " + str(account2.balance) + " грн")
print("Успішних операцій: " + str(successful_count))