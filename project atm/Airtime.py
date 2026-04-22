balance  = 100
Airtime = input("MTN, GLO, AIRTEL, ETISALAT")
Numbers = input("Whats your number")
if len(Numbers) != 11:
    print("Wrong number")

else:
    Airtime_amount = int(input("how much airtime would you like to buy"))
    if Airtime_amount <= balance:
        print("Airtime succesfully purchased")
    else:
        print("Insufficient amount")