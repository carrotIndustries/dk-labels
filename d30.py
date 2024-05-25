import socket
import cairo
import sys

class Printer:
    def __init__(self, addr):
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        port = 1
        self.sock.connect((addr, port))

    def get_battery(self) :
        self.sock.send(bytes([31, 17, 8]))
        resp = list(self.sock.recv(3))
        assert(resp[:2] == [0x1a, 0x04])
        return resp[2]

    def get_serial(self) :
        self.sock.send(bytes([31, 17, 9]))
        resp = list(self.sock.recv(17))
        assert(resp[:2] == [0x1a, 0x08])
        return bytes(resp[2:]).decode("ascii")

    def get_paper_state(self) :
        self.sock.send(bytes([31, 17, 17]))
        resp = list(self.sock.recv(3))
        assert(resp[:2] == [0x1a, 0x06])
        return resp[2] != 136

    def print_surface(self, surf) :
        assert surf.get_format() == cairo.Format.RGB24

        def getpixel(x, y):
            offset = surf.get_stride() * y + x * 4
            return surf.get_data()[offset] == 0

        #from https://github.com/polskafan/phomemo_d30/blob/master/print_text.py#L72
        buf = list(bytes.fromhex('1f1124001b401d7630000c004001'))

        width = surf.get_width()
        height = surf.get_height()

        assert(width == 320)
        assert(height == 96)

        height8 = height//8

        ibuf = [0]*height8*width
        for y in range(height) :
            for x in range(width) :
                if getpixel(x,height-1-y) :
                    ibuf[y//8 + x*height8] |= (1<<(7-(y&7)))

        buf += ibuf
        self.sock.send(bytes(buf))

if __name__ == "__main__" :
    import config
    surf = cairo.ImageSurface.create_from_png(sys.argv[1])
    printer = Printer(config.printer_mac)
    printer.print_surface(surf)
