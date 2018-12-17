# H. Hadipour
# 1397/04/18

from mibs import Mibs

if __name__ == "__main__":

    ROUND = int(input("Input the target round number: "))
    while not (ROUND > 0):
        print("Input a round number greater than 0.")
        ROUND = int(input("Input the target round number again: "))    

    target_bit = int(input("Input the target bit (input -1 for finding the max degree after the given rounds):"))    

    mibs = Mibs(ROUND, target_bit)

    mibs.make_model()

    mibs.solve_model()
