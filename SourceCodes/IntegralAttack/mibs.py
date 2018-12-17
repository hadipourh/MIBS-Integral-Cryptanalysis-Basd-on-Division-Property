# H. Hadipour
# 1397/04/18
"""
x_roundNumber_nibbleNumber_bitNumber
x_roundNumber_nibbleNumber_0: msb
x_roundNumber_nibbleNumber_3: lsb

x_i_0_0,x_i_0_1,x_i_0_2,x_i_0_3,......x_i_7_0,x_i_7_1,x_i_7_2,x_i_7_3 denote the left half
  of the input of the (i+1)-th round
y_i_0_0,y_i_0_1,y_i_0_2,y_i_0_3,......y_i_7_0,y_i_7_1,y_i_7_2,y_i_7_3 denote the right half
  of the input of the (i+1)-th round


u_i_0_0,u_i_0_1,u_i_0_2,u_i_0_3,......u_i_7_0,u_i_7_1,u_i_7_2,u_i_7_3 denote the input to
  the sbox of the (i+1)-th round
v_i_0_0,v_i_0_1,v_i_0_2,v_i_0_3,......v_i_7_0,v_i_7_1,v_i_7_2,v_i_7_3 denote the output to
  the sbox of the (i+1)-th round
"""

"""
Temporary variables used in the mixing layer:
a0, ..., a7, b0, ..., b7, c0, ..., c7, d0, ..., d7
t0, ..., t15
These are 4-bit variables
"""

from gurobipy import *
import time

class Mibs:
    def __init__(self, rounds, active_bits):
        self.rounds = rounds
        self.active_bits = active_bits
        self.block_size = 64
        self.shuffle = [2, 0, 3, 6, 7, 4, 5, 1]

        self.filename_model = "MIBS_" + \
            str(self.rounds) + "_" + str(self.active_bits) + ".lp"
        self.filename_result = "result_" + \
            str(self.rounds) + "_" + str(self.active_bits) + ".txt"
        fileobj = open(self.filename_model, "w")
        fileobj.close()
        fileobj = open(self.filename_result, "w")
        fileobj.close()

    # Number of inequalities
    NUMBER = 9
    # Linear inequalities for the  Sbox used in MIBS round function
    sb = [[1, 1, 4, 1, -2, -2, -2, -2, 1],\
           [0, 3, 0, 0, -1, -1, -1, -1, 1],\
           [-1, -2, -2, -1, -1, -2, 4, -1, 6],\
           [-1, -2, -2, -1, 5, 4, 5, 5, 0],\
           [-1, -1, -1, 0, -1, 3, -2, -1, 4],\
           [-1, 0, 0, -1, -2, -1, -1, 3, 3],\
           [1, 0, 0, 0, 1, -1, -1, -1, 1],\
           [-1, -1, 0, -1, 1, 2, 2, 1, 1],\
           [0, 0, -1, 0, -1, -1, 2, -1, 2]]
    
    def create_objective_function(self):
        """
        Create objective function of the MILP model.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        eqn = []
        for i in range(0, 8):
            for j in range(0, 4):
                eqn.append("x" + "_" + str(self.rounds) +
                           "_" + str(i) + "_" + str(j))
        for i in range(0, 8):
            for j in range(0, 4):
                eqn.append("y" + "_" + str(self.rounds) +
                           "_" + str(i) + "_" + str(j))
        temp = " + ".join(eqn)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    @staticmethod
    def create_variables(n, s):
        """
        Generate the variables used in the model.
        """
        array = [["" for i in range(0, 4)] for j in range(0, 8)]
        for i in range(0, 8):
            for j in range(0, 4):
                array[i][j] = s + "_" + str(n) + "_" + str(i) + "_" + str(j)
        return array
    
    def constraints_by_sbox(self, variable1, variable2):
        """
        Generate the constraints by Sbox layer.
        """
        fileobj = open(self.filename_model, "a")
        for k in range(0, 8):
            for coff in Mibs.sb:
                temp = []
                for u in range(0, 4):
                    temp.append(str(coff[u]) + " " + variable1[k][u])
                for v in range(0, 4):
                    temp.append(str(coff[4 + v]) + " " + variable2[k][v])
                temp1 = " + ".join(temp)
                temp1 = temp1.replace("+ -", "- ")
                s = str(-coff[Mibs.NUMBER - 1])
                s = s.replace("--", "")
                temp1 += " >= " + s
                fileobj.write(temp1)
                fileobj.write("\n")
        fileobj.close()
    
    def constraints_by_64bit_copy(self, variablex, variableu, variabley):
        """
        Generate the constraints by 64-bit copy operation.
        """
        fileobj = open(self.filename_model, "a")
        for i in range(0, 8):
            for j in range(0, 4):
                temp = []
                temp.append(variablex[i][j])
                temp.append(variableu[i][j])
                temp.append(variabley[i][j])
                s = " - ".join(temp)
                s += " = 0"
                fileobj.write(s)
                fileobj.write("\n")
        fileobj.close()

    def constraints_by_4bit_copy(self, variablex, variableu, variabley):
        """
        Generate the constraints by 4-bit copy operation.
        """
        fileobj = open(self.filename_model, "a")
        for j in range(0, 4):
            temp = []
            temp.append(variablex[j])
            temp.append(variableu[j])
            temp.append(variabley[j])
            s = " - ".join(temp)
            s += " = 0"
            fileobj.write(s)
            fileobj.write("\n")
        fileobj.close()
    
    def constraints_by_64bit_xor(self, variabley, variablev, variablex):
        """
        Generate the constraints by 64-bit Xor operation.
        """
        fileobj = open(self.filename_model, "a")
        for i in range(0, 8):
            for j in range(0, 4):
                temp = []
                temp.append(variablex[i][j])
                temp.append(variablev[i][j])
                temp.append(variabley[i][j])
                s = " - ".join(temp)
                s += " = 0"
                fileobj.write(s)
                fileobj.write("\n")
        fileobj.close()

    def constraints_by_4bit_xor(self, variabley, variablev, variablex):
        """
        Generate the constraints by 4-bit Xor operation.
        """
        fileobj = open(self.filename_model, "a")
        for j in range(0, 4):
            temp = []
            temp.append(variablex[j])
            temp.append(variablev[j])
            temp.append(variabley[j])
            s = " - ".join(temp)
            s += " = 0"
            fileobj.write(s)
            fileobj.write("\n")
        fileobj.close()
    
    def nibbles_shuffle(self, inputs):
        return [inputs[i] for i in self.shuffle]

    def constraints_by_mixing_layer(self, variables_in, variables_out, round_number):
        """
        Generate constraints related to mixing layer
        """
        a_vars = self.create_variables(round_number, "a")
        b_vars = self.create_variables(round_number, "b")
        c_vars = self.create_variables(round_number, "c")
        t_vars = [[0 for i in range(4)] for j in range(16)]
        for i in range(16):
            for j in range(4):
                t_vars[i][j] = "t" + "_" + str(round_number) +"_" + str(i) + "_" + str(j)
        # Constraints by 4-bit copies:
        self.constraints_by_4bit_copy(variables_in[3], t_vars[0], a_vars[3])
        self.constraints_by_4bit_copy(variables_in[2], t_vars[1], a_vars[2])
        self.constraints_by_4bit_copy(variables_in[1], t_vars[2], a_vars[1])
        self.constraints_by_4bit_copy(variables_in[0], t_vars[3], a_vars[0])

        self.constraints_by_4bit_copy(a_vars[7], b_vars[7], t_vars[4])
        self.constraints_by_4bit_copy(a_vars[6], b_vars[6], t_vars[5])
        self.constraints_by_4bit_copy(a_vars[5], b_vars[5], t_vars[6])
        self.constraints_by_4bit_copy(a_vars[4], b_vars[4], t_vars[7])

        self.constraints_by_4bit_copy(b_vars[3], c_vars[3], t_vars[8])
        self.constraints_by_4bit_copy(b_vars[2], c_vars[2], t_vars[9])
        self.constraints_by_4bit_copy(b_vars[1], c_vars[1], t_vars[10])
        self.constraints_by_4bit_copy(b_vars[0], c_vars[0], t_vars[11])

        self.constraints_by_4bit_copy(c_vars[7], variables_out[7], t_vars[12])
        self.constraints_by_4bit_copy(c_vars[6], variables_out[6], t_vars[13])
        self.constraints_by_4bit_copy(c_vars[5], variables_out[5], t_vars[14])
        self.constraints_by_4bit_copy(c_vars[4], variables_out[4], t_vars[15])

        # Constraints by 4-it xors:
        self.constraints_by_4bit_xor(variables_in[7], t_vars[0], a_vars[7])
        self.constraints_by_4bit_xor(variables_in[6], t_vars[1], a_vars[6])
        self.constraints_by_4bit_xor(variables_in[5], t_vars[2], a_vars[5])
        self.constraints_by_4bit_xor(variables_in[4], t_vars[3], a_vars[4])

        self.constraints_by_4bit_xor(a_vars[1], t_vars[4], b_vars[1])
        self.constraints_by_4bit_xor(a_vars[0], t_vars[5], b_vars[0])
        self.constraints_by_4bit_xor(a_vars[3], t_vars[6], b_vars[3])
        self.constraints_by_4bit_xor(a_vars[2], t_vars[7], b_vars[2])

        self.constraints_by_4bit_xor(b_vars[4], t_vars[8], c_vars[4])
        self.constraints_by_4bit_xor(b_vars[7], t_vars[9], c_vars[7])
        self.constraints_by_4bit_xor(b_vars[6], t_vars[10], c_vars[6])
        self.constraints_by_4bit_xor(b_vars[5], t_vars[11], c_vars[5])

        self.constraints_by_4bit_xor(c_vars[3], t_vars[12], variables_out[3])
        self.constraints_by_4bit_xor(c_vars[2], t_vars[13], variables_out[2])
        self.constraints_by_4bit_xor(c_vars[1], t_vars[14], variables_out[1])
        self.constraints_by_4bit_xor(c_vars[0], t_vars[15], variables_out[0])

    def constraint(self):
        """
        Generate the constraints used in the MILP model.
        """
        assert(self.rounds >= 1)
        fileobj = open(self.filename_model, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        variableinx = Mibs.create_variables(0, "x")
        variableiny = Mibs.create_variables(0, "y")
        variableu = Mibs.create_variables(0, "u")
        variablev = Mibs.create_variables(0, "v")
        variabled = Mibs.create_variables(0, "d")
        variableoutx = Mibs.create_variables(1, "x")
        variableouty = Mibs.create_variables(1, "y")
        if self.rounds == 1:
            self.constraints_by_64bit_copy(variableinx, variableu, variableouty)
            self.constraints_by_sbox(variableu, variablev)
            self.constraints_by_mixing_layer(variablev, variabled, 0)
            variabled = self.nibbles_shuffle(variabled)
            self.constraints_by_64bit_xor(variableiny, variabled, variableoutx)
        else:
            self.constraints_by_64bit_copy(variableinx, variableu, variableouty)
            self.constraints_by_sbox(variableu, variablev)
            self.constraints_by_mixing_layer(variablev, variabled, 0)
            variabled = self.nibbles_shuffle(variabled)
            self.constraints_by_64bit_xor(variableiny, variabled, variableoutx)
            for i in range(1, self.rounds):
                variableinx = variableoutx
                variableiny = variableouty
                variableouty = Mibs.create_variables((i + 1), "y")
                variableoutx = Mibs.create_variables((i + 1), "x")
                variableu = Mibs.create_variables(i, "u")
                variablev = Mibs.create_variables(i, "v")
                variabled = Mibs.create_variables(i, "d")
                self.constraints_by_64bit_copy(variableinx, variableu, variableouty)
                self.constraints_by_sbox(variableu, variablev)
                self.constraints_by_mixing_layer(variablev, variabled, i)
                variabled = self.nibbles_shuffle(variabled)
                self.constraints_by_64bit_xor(variableiny, variabled, variableoutx)

    # Variables declaration
    def variable_binary(self):
        """
        Specify the variables type.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Binary\n")
        for i in range(self.rounds + 1):
            for j in range(8):
                for k in range(4):
                    fileobj.write("x_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("y_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
        for i in range(self.rounds):
            for j in range(8):
                for k in range(4):
                    fileobj.write("u_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("v_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("a_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("b_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("c_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
                    fileobj.write("d_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
        for i in range(self.rounds):
            for j in range(16):
                for k in range(4):
                    fileobj.write("t_" + str(i) + "_" + str(j) + "_" + str(k))
                    fileobj.write("\n")
        fileobj.write("END")
        fileobj.close()
        
    def init(self):
        """
        Generate the initial constraints introduced by the initial division property.
        """
        variabley = Mibs.create_variables(0, "y")
        variablex = Mibs.create_variables(0, "x")
        fileobj = open(self.filename_model, "a")
        eqn = []
        if self.active_bits <= 32:
            for i in range(0, self.active_bits):
                temp = variabley[7 - (i // 4)][3 - i % 4] + " = 1"
                fileobj.write(temp)
                fileobj.write("\n")
            for i in range(self.active_bits, 32):
                temp = variabley[7 - (i // 4)][3 - i % 4] + " = 0"
                fileobj.write(temp)
                fileobj.write("\n")
            for i in range(0, 32):
                temp = variablex[7 - (i // 4)][3 - i % 4] + " = 0"
                fileobj.write(temp)
                fileobj.write("\n")

        else:
            for i in range(0, 32):
                temp = variabley[7 - (i // 4)][3 - i % 4] + " = 1"
                fileobj.write(temp)
                fileobj.write("\n")
            for i in range(0, (self.active_bits - 32)):
                temp = variablex[7 - (i // 4)][3 - i % 4] + " = 1"
                fileobj.write(temp)
                fileobj.write("\n")
            for i in range((self.active_bits - 32), 32):
                temp = variablex[7 - (i // 4)][3 - i % 4] + " = 0"
                fileobj.write(temp)
                fileobj.write("\n")
        fileobj.close()

    def make_model(self):
        """
        Generate the MILP model of LBock given the round number and activebits.
        """
        self.create_objective_function()
        self.constraint()
        self.init()
        self.variable_binary()

    def write_objective(self, obj):
        """
        Write the objective value into filename_result.
        """
        fileobj = open(self.filename_result, "a")
        fileobj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.block_size):
            u = obj.getVar(i)
            if u.getAttr("x") != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            fileobj.write(s)
            fileobj.write("\n")
        fileobj.close()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher of MIBS.
        """
        time_start = time.time()
        m = read(self.filename_model)
        counter = 0
        set_zero = []
        global_flag = False
        while counter < self.block_size:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                obj = m.getObjective()
                if obj.getValue() > 1:
                    global_flag = True
                    break
                else:
                    fileobj = open(self.filename_result, "a")
                    fileobj.write(
                        "************************************COUNTER = %d\n" % counter)
                    fileobj.close()
                    self.write_objective(obj)
                    for i in range(0, self.block_size):
                        u = obj.getVar(i)
                        temp = u.getAttr('x')
                        if temp == 1:
                            set_zero.append(u.getAttr('VarName'))
                            m.addConstr(u == 0)
                            m.update()
                            counter += 1
                            break
            # Gurobi syntax: m.Status == 3 represents the model is infeasible.
            elif m.Status == 3:
                global_flag = True
                break
            else:
                print("Unknown error!")

        fileobj = open(self.filename_result, "a")
        if global_flag:
            fileobj.write("\nIntegral Distinguisher Found!\n\n")
            print("Integral Distinguisher Found!\n")
        else:
            fileobj.write("\nIntegral Distinguisher does NOT exist\n\n")
            print("Integral Distinguisher does NOT exist\n")

        fileobj.write("Those are the coordinates set to zero: \n")
        for u in set_zero:
            fileobj.write(u)
            fileobj.write("\n")
        fileobj.write("\n")
        time_end = time.time()
        fileobj.write(("Time used = " + str(time_end - time_start)))
        fileobj.close()
