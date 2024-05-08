from pyfirmata2 import ArduinoMega, util, STRING_DATA

global board
board = ArduinoMega('COM7')


class DISP_PyF():
    def __init__(self):
        self.laststring = ""
        board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(""))
    def send(self,writing):
        #autobreaks line if over 16 characters, max length is 31 characters
        if writing != self.laststring:
            board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(writing))
            self.laststring = writing


disp = DISP_PyF()
print(len("1234567890abcdefghijklmnopqrstu"))
print(len("aaa                            "))
while True:
    #          ghijklmnopqrstuv____________
    disp.send("1234567890abcdefghijklmnopqrstuvwxyz")
    #disp.send("1234567890abcdefghijklmnopqrstu")
    #disp.send("1234567890abcdefg")