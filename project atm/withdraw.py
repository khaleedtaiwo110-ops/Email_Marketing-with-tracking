print("Welcome ! ")
balance = 1003
Amount = int(input("How much would you like to withdraw 10000, 5000, 3000, 2000, 1000 Quit "))
def withdrawal():
    if balance >= Amount:
        print("Withdrawing.....")
        print("Done")
        input("Would you like to perform another transaction ")
    else:
        print("Insufficient balance")


if Amount == 10000 :
    withdrawal()
elif Amount == 5000 :
    withdrawal()
elif Amount == 3000 :
    withdrawal()
elif Amount == 1000 :
    withdrawal()
else:
    print("'Sorry Fixed amount only")