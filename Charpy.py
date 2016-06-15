# /Charpy.py
# main script

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/my_module')
import time_deco
import data_reader
import importlib
importlib.reload(data_reader)
importlib.reload(time_deco)
# reload()
# import matplotlib.pyplot as plt
# from reader import Reader
# from line_profiler import LineProfiler
# import memory_profiler
# import chardet
import traceback
# import math
# import numpy as np
# plt.style.use('ggplot')
TIME_PRINT = 1
NNN = 10**2


class DataHandler(data_reader.DataReader):
    CLASS_NAME = 'DataHandler'

    @time_deco.time_deco(TIME_PRINT, CLASS_NAME)
    def __init__(self, dbg=False, *args, **kwargs):
        if dbg:
            data_reader.DataReader.__init__(self, name='data', print_it=0, *args, **kwargs)
            _file_list = self.rd.get_children_ext_files_list(self.rd.root, 'txt')
            self.select_file(num=1, file=_file_list[9])
        else:
            data_reader.DataReader.__init__(self, *args, **kwargs)
        self.cur_file_num = 0

    def data_viewer2(self):
        self.cur_file_num = 0
        self.read_msg_file_to_tx2(_file_num=self.cur_file_num)
        start = 0
        end = len(self.ttt)
        inp = 0
        self.plot_timecorse_of_move_sparsely(show_it=1,start=int(start), end=int(end))
        while not inp == 'end':
            print(00, 'start: {}, end: {}, len(x):{} '.format(start, end, len(self.x)))
            self.plot_timecorse_of_move_sparsely(show_it=1, start=int(start), end=int(end))
            inp = input('press key')
            print(111, 'inp:{}'.format(inp), 'int(start): {}, int(end): {}'.format(int(start), int(end)))
            start, end = self.react_to_input(inp, start, end)
            print(222, 'start: {}, end: {}, len(x):{}'.format(start, end, len(self.x)))

    def react_to_input(self, inp, start, end):
        _dif = end - start
        _start, _end = start, end
        if inp == '0':
            _start = start + _dif / 2
            _end = end
        elif inp == '9':
            _start = start - _dif
            _end = end
        elif inp == '1':
            _start = start
            _end = end - _dif / 2
        elif inp == '2':
            _start = start
            _end = end + _dif
        elif inp == 'l':
            if len(self.x) > end + _dif / 4:
                print(108, len(self.x))
                _start = start + _dif / 4
                _end = end + _dif / 4
            else:
                self.cur_file_num += 1
                self.read_msg_file_to_tx2(_file_num=self.cur_file_num)
                _start = len(self.x) - _dif
                _end = len(self.x)
        elif inp == 'k':
            if 0 < start - _dif / 4:
                _start = start - _dif / 4
                _end = end - _dif / 4
            else:
                _start = 0
                _end = _dif
        elif inp=='hist':
            self.norm_fit_sparsely(show_it=1, start=start, end=end)
        else:
            pass

        if _start >= 0:
            start = _start
        else:
            start = 0
        if _end <= len(self.x):
            end = _end
        else:
            end = len(self.x)
        if int(_dif) == 0:
            if start == 0:
                end = start + 1
            elif end == len(self.x):
                start = end - 1
            else:
                start = end - 1
        return start, end

    @time_deco.time_deco(TIME_PRINT, CLASS_NAME)
    def import_text_file_manually(self):
        data_reader.DataReader.__init__(self, name='data', print_it=0)
        _file_list = self.rd.get_children_ext_files_list(self.rd.root, 'txt')
        self.select_file()
        self.convert_file_tx_txt_to_msgpack3()
        print('end of convert!')




@time_deco.time_deco(TIME_PRINT, __name__)
def main():
    dh = DataHandler(dbg=True)
    dh.data_viewer2()


if __name__ == '__main__':
    print('Charpy!')
