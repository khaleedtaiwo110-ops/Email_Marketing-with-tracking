def trans( ) :
    balance = 100
    Transfer = input("What bank are you transfering to\n1, Opay\n2, Palmpay\n3, Zenit\n4, First bank\n  ")
    Transfer_amount = int(input("how much would you like to transfer?\n1, 10000\n2, 5000\n3, 3000\n4, 2000\n5, 1000\nx"))
    if Transfer_amount == 1:
        balance -= 10000
        print("Transfer succesful")
    elif Transfer_amount == 2:
        balance -= 5000
        print("Transfer done")
    elif Transfer_amount == 3:
        balance -= 3000
        print("Transfer done")
    elif Transfer_amount == 4:
        balance -= 2000
        print("Transfer done")
    elif Transfer_amount == 5:
        balance -= 1000
        print("Transfer done")
    else:
        print("Fixed amount only")


