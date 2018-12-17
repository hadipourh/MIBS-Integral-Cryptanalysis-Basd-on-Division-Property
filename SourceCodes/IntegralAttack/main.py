# H. Hadipour
# 1397/04/18

from mibs import Mibs

if __name__ == "__main__":

    ROUND = int(input("Input the target round number: "))
    while not (ROUND > 0):
        print("Input a round number greater than 0.")
        ROUND = int(input("Input the target round number again: "))

    ACTIVEBITS = int(input("Input the number of acitvebits: "))
    while not (ACTIVEBITS < 64 and ACTIVEBITS > 0):
        print("Input a number of activebits with range (0, 64):")
        ACTIVEBITS = int(input("Input the number of acitvebits again: "))

    mibs = Mibs(ROUND, ACTIVEBITS)

    mibs.make_model()

    mibs.solve_model()
