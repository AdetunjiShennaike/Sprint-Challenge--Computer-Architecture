"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
      """Construct a new CPU."""
      self.running = True
      self.RAM = [0] * 256
      self.Reg = [0] * 8
      self.IM = 247 #R5 Interrupt Mask
      self.IS = 248 #R6 Interrupt Status(Interrupts held betwen I0-I7[0xF8-0xFF])
      self.SP = 244 #R7 Stack Pointer(Starts at 0xF4 if stack is empty)

      # Internal Registers
      self.PC = 0 #Unmarked Program Counter
      self.IR = { #Instruction Register
        0: 'NOP', #No Operation
        1: 'HLT', #Halt
        17: 'RET', #Return
        19: 'IRET', #Interupt Return
        69: 'PUSH',
        70: 'POP',
        71: 'PRN', #Print
        72: 'PRA', #Print Alpha
        80: 'CALL', #Call a subroutine(function)
        82: 'INT', #Interupt
        84: 'JMP', #Jump
        85: 'JEQ', #Jump to Equal if set
        86: 'JNE', #Jump to Address stored if Equal not set
        87: 'JGT', #Jump to Greater-Than if set
        88: 'JLT', #Jump to Less-Than if set
        89: 'JLE', #Jump to Less-Than or Equal if set
        90: 'JGE', #Jump to Greater-Than or Equal if set
        101: 'INC', #Increment
        102: 'DEC', #Decrement
        105: 'NOT', #Bitwise NOT
        130: 'LDI', #Set value of Reg_a to input
        131: 'LD', #Load Reg_a with value at Reg_b
        132: 'ST', #Store value in Reg_b in Reg_a
        160: 'ADD',
        161: 'SUB',
        162: 'MUL',
        163: 'DIV',
        164: 'MOD', #Modulous
        167: 'CMP', #Compare
        168: 'AND', #Bitwise AND
        170: 'OR', #Bitwise OR
        171: 'XOR', #Bitwise Exclusive OR
        172: 'SHL', #Shift Left
        173: 'SHR', #Shift Right
      }
      # self.MAR #Memory Address Register
      # self.MDR #Memory Data Register
      # self.IE = 
      self.FL = { #Flags
        'E': 0, #Equals
        'G': 0, #Greater
        'L': 0, #Less
      }

      # #Instruction Grouping
      self.IRALU = ['ADD', 'SUB', 'MUL', 'DIV', 'MOD',  'INC', 'DEC',  'CMP',  'AND', 'NOT', 'OR', 'XOR', 'SHL', 'SHR',]
      self.IR00 = {
        'RET': self.RET,
        'IRET': self.IRET,
        'NOP': self.NOP,
        'HLT': self.HLT,
      }
      self.IR01 = {
        'CALL': self.CALL,
        'INT': self.INT,
        'JMP': self.JMP,
        'JEQ': self.JEQ,
        'JNE': self.JNE,
        'JGT': self.JGT,
        'JLT': self.JLT,
        'JLE': self.JLE,
        'JGE': self.JGE,
        'PUSH': self.PUSH,
        'POP': self.POP,
        'PRN': self.PRN,
        'PRA': self.PRA,
      }
      self.IR10 = {
        'LDI': self.LDI,
        'LD': self.LD,
        'ST': self.ST,
      }

    def ram_read(self, address):
      return self.RAM[address]

    def ram_write(self, address, write):
      self.RAM[address] = int(f'0b{write}', 2)

    def load(self, file):
        """Load a program into memory."""

        address = 0

        f = open(file, 'r')
        for line in f.readlines():
          split = line.split('#')
          instruction = split[0].strip()
          if instruction == '':
            continue
          self.ram_write(address, instruction)
          address += 1

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.RAM[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b = 0):
        """ALU operations."""
        if op == "INC" or op == "DEC" or op == "NOT":
          self.PC += 2
        else:
          self.PC += 3

        if op == "ADD":
            self.Reg[reg_a] += self.Reg[reg_b]
        elif op == "SUB": 
            self.Reg[reg_a] -= self.Reg[reg_b]
        elif op == "AND":
            result = self.Reg[reg_a] & self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "NOT":
            result = ~self.Reg[reg_a]
            self.Reg[reg_a] = result
        elif op == "OR":
            result = self.Reg[reg_a] | self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "XOR":
            result = self.Reg[reg_a] ^ self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "DEC":
            self.Reg[reg_a] -= 1
        elif op == "INC":
            self.Reg[reg_a] += 1
        elif op == "SHL":
            result = self.Reg[reg_a] << self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "SHR":
            result = self.Reg[reg_a] >> self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "CMP":
            if self.Reg[reg_a] > self.Reg[reg_b]:
              self.FL['L'] = 0
              self.FL['G'] = 1
              self.FL['E'] = 0
            if self.Reg[reg_a] < self.Reg[reg_b]:
              self.FL['L'] = 1
              self.FL['G'] = 0
              self.FL['E'] = 0
            else:
              self.FL['L'] = 0
              self.FL['G'] = 0
              self.FL['E'] = 1
        elif op == "MUL":
            result = self.Reg[reg_a] * self.Reg[reg_b]
            self.Reg[reg_a] = result
            self.PC += 3
        elif op == "DIV":
            if self.Reg[reg_b] == 0:
              print(f'Cannot use the value 0')
              self.HLT()
            result = self.Reg[reg_a] // self.Reg[reg_b]
            self.Reg[reg_a] = result
        elif op == "MOD":
            if self.Reg[reg_b] == 0:
              print(f'Cannot use the value 0')
              self.HLT()
            result = self.Reg[reg_a] % self.Reg[reg_b]
            self.Reg[reg_a] = result
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.FL,
            #self.IE,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.Reg[i], end='')

        print()

    def LDI(self, reg_a, reg_b):
      self.Reg[reg_a] = reg_b
      #Move the Program Counter
      self.PC += 3

    def HLT(self):
      self.running = False

    def PRN(self, reg_a):
      print(f'{self.Reg[reg_a]}')
      #Move the Program Counter
      self.PC += 2

    def CALL(self, func):
      # Store current PC for RET to use later
      self.SP -= 1
      self.RAM[self.SP] = self.PC + 2
      # Move to the location of the subroutine
      self.PC = self.Reg[func]

    def INT(self, reg_a):
      if self.IS <= 255:
        self.ram_write(self.IS, reg_a)
        self.IS += 1
      #Move the Program Counter
      self.PC += 2
    
    def IRET(self):
      # Pop all registers except R7
      for i in range(6,0):
        self.Reg[i] = 0
      # Pop the FL from stack
      # self.SP + 1
      # Grab PC from stack and pop
      self.PC = self.RAM[self.SP]
      self.SP + 1
      # Enable interrupts

    def JEQ(self, reg_a):
      if self.FL['E'] == 1:
        self.PC = reg_a

    def JGE(self, reg_a):
      if self.FL['E'] == 1 or self.FL['G'] == 1:
        self.PC = reg_a

    def JGT(self, reg_a):
      if self.FL['G'] == 1:
        self.PC = reg_a

    def POP(self, reg_a):
      self.Reg[reg_a] = self.ram_read(self.SP)
      self.SP += 1
      #Move the Program Counter
      self.PC += 2

    def PRA(self, reg_a):
      # Print ASCII character of the number
      print(str(chr(reg_a)))
      #Move the Program Counter
      self.PC += 2

    def PUSH(self, reg_a):
      self.SP -= 1
      self.RAM[self.SP] = self.Reg[reg_a]
      #Move the Program Counter
      self.PC += 2

    def RET(self):
      #Move Program Counter to the location it was at when call was invoked
      self.PC = self.ram_read(self.SP)
      self.SP += 1

    def ST(self, reg_a, reg_b):
      self.ram_write(self.Reg[reg_a], self.Reg[reg_a])
      #Move the Program Counter
      self.PC += 3

    def NOP(self):
      #Move the Program Counter
      self.PC += 1

    def JMP(self, reg_a):
      self.PC = reg_a

    def JNE(self, reg_a):
      if self.FL['E'] == 0:
        self.PC = reg_a

    def JLT(self, reg_a):
      if self.FL['L'] == 1:
        self.PC = reg_a

    def JLE(self, reg_a):
      if self.FL['E'] == 1 or self.FL['L'] == 1:
        self.PC = reg_a

    def LD(self, reg_a, reg_b):
      self.Reg[reg_a] = self.ram_read(self.Reg[reg_b])
      #Move the Program Counter
      self.PC += 3


    def run(self):
      """
      Run the CPU.
      
      When the LS-8 is booted, the following steps occur:

        R0-R6 are cleared to 0.
        R7 is set to 0xF4.
        PC and FL registers are cleared to 0.
        RAM is cleared to 0.
      
      Subsequently, the program can be loaded into RAM starting at address 0x00.
      """

      self.Reg[7] = self.SP
      while self.running:
        command = self.ram_read(self.PC)
        if command in self.IR:
          instruction = self.IR[command]
        if instruction in self.IR10:
          self.IR10[instruction](self.ram_read(self.PC + 1), self.ram_read(self.PC + 2))
        elif instruction in self.IR01:
          self.IR01[instruction](self.ram_read(self.PC + 1))
        elif instruction in self.IR00:
          self.IR00[instruction]()
        elif instruction == 'PRN':
          self.PRN(self.ram_read(self.PC + 1))
        elif instruction in self.IRALU:
          self.alu(instruction,self.ram_read(self.PC + 1), self.ram_read(self.PC + 2))
        else:
          print(f'This {instruction} does not exist.')
          sys.exit(1)