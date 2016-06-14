import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/my_module')
# print(111,os.path.dirname(os.path.abspath(__file__)) +'/my_module')
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
            DataReader.__init__(self, *args, **kwargs)
        self.cur_file_num = 0

    # @time_deco.time_deco(TIME_PRINT, CLASS_NAME)
    # def data_viewer(self):
    #     start = 0
    #     end = len(self.x)
    #     inp = 2
    #     while not inp == 'end':
    #         inp = input('press key:')
    #         print(inp)
    #         _dif = end - start
    #         if inp == '0':
    #             _start = start + _dif / 2
    #             _end = end
    #         elif inp == '9':
    #             _start = start - _dif
    #             _end = end
    #         elif inp == '1':
    #             _start = start
    #             _end = end - _dif / 2
    #         elif inp == '2':
    #             _start = start
    #             _end = end + _dif
    #         else:
    #             pass

    #         if _start > 0:
    #             start = _start
    #         else:
    #             start = 0
    #         if _end <= len(self.x):
    #             end = _end
    #         else:
    #             end = len(self.x)
    #         if _dif == 0:
    #             if start == 0:
    #                 end = start + 1
    #             elif end == len(self.x):
    #                 start = end - 1
    #             else:
    #                 start = end - 1

    #         self.plot_timecorse_of_move_sparsely(show_it=1, start=int(start), end=int(end))

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


@time_deco.time_deco(TIME_PRINT, __name__)
def main():
    # dr1=DataReader(name='data', print_it=0)
    # dr1.DataReader_msg_test()
    # dr1.select_file(num=1)
    # dr1.convert_file_tx_txt_to_bin()
    # del dr1
    # dr2=DataReader('data', print_it=0)
    # dr2.DataReader_bin_test2()

    # dr3=DataReader('data', print_it=0)
    # txt_dict=dr3.rd.get_children_ext_files_dict([dr3.rd.root], 'txt')
    # _file_list=[fil for key in txt_dict.values() for fil in key]
    # dr3.select_file(num=1, file=_file_list[7])
    # dr3.read_msg_file_to_tx2(_file_num=0)
    # dr3.plot_timecorse_of_move_sparsely(show_it=1)

    dh = DataHandler(dbg=True)
    dh.data_viewer2()

    # ---------------------convert txt to msg-------------------
    # rd = Reader('data')
    # _file_list = rd.get_children_ext_files_list(rd.root, 'txt')
    # print([fil.name for fil in _file_list])
    # # _file_list=[fil for key in txt_dict.values() for fil in key]
    # for prnt in _file_list:
    #     try:
    #         print(prnt.name)
    #         print(int(os.path.getsize(prnt.get_path()) / 31.482113747553814 / 10**7) + 1)
    #         cur_dr=DataReader('data', print_it=0)
    #         cur_dr.select_file(file=prnt)
    #         cur_dr.convert_file_tx_txt_to_msgpack2()
    #         del cur_dr
    #         cur_dr = DataReader('data', print_it=0)
    #         cur_dr.select_file(file=prnt)
    #         cur_dr.read_msg_file_to_tx2(_file_num=0)
    #         cur_dr.plot_timecorse_of_move_sparsely(show_it=1)
    #     except Exception:
    #         exctype, value, tb = sys.exc_info()
    #         er = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #         for val in er:
    #             print(str(val))

    # _i=0
    # for line in open(prnt.get_path(), 'r', encoding='shift_jis'):
    # # with open(prnt.get_path(), 'rb') as f:
    # #     lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
    # #             'shift_jis', 'shift_jis_2004','shift_jisx0213',
    # #             'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
    # #             'iso2022_jp_ext','latin_1', 'ascii')
    # #     encode = None
    # #     for encoding in lookup:
    # #         try:
    # #             line = f.read(100).decode(encoding)
    # #             encode = encoding
    # #             # break
    # #         except:
    # #             pass
    # #     # if isinstance(line, unicode):
    # #     #     return data,encode
    # #     # else:
    # #     #     raise LookupError
    #     print(_i,line.split('\t'))
    #     # print(222,f.read(1000))
    #     # print(222,chardet.detect(f.read(1000)))

    #     # print(_i, len(line), line)
    #     _i+=1
    #     if _i%12==0:break

    print('end')

    # loop_num = 2**20
    # k = 10**(i + 2)
    # a = Simulator(print_it=0, k=k, loop_num=loop_num)
    # a.simpleMD(show_it=1, save_it=0, save_dir='fig',
    #            save_path='1_k={}_loop-num={}_time_course.png'.format(k, loop_num))
    # a.norm_fit(show_it=1, save_it=0, save_dir='fig',
    #            save_path='2_k={}_loop-num={}_norm_fit.png'.format(k, loop_num))
    # a.calc_power_spectrum(window_size_num=1, overlap_rate_num=1, show_it=1, save_it=0,
    #                       save_dir='fig',
    #                       save_path='3_k={}_loop-num={}_pwspctrm.png'.format(k, loop_num))
    # a.lorentzian_fit()


if __name__ == '__main__':
    main()

# print('computed K is ',1/((mu**2+sig**2)*beta))
# print(stats.tmean(x), stats.tstd(x))
