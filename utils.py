from constants import CLA, INS


def build_header(cla=CLA, ins=INS, p1='', p2=''):
    return ''.join([cla, ins, p1, p2])


def get_lc(pin):
    return "{:02X}".format(len(bytes.fromhex(pin)))
