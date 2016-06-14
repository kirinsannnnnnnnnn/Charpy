import sys
import os, os.path
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from line_profiler import LineProfiler
from time_deco import time_deco
import analyzer
import importlib
importlib.reload(analyzer)
from reader import Reader
import msgpack
import struct
import numpy as np
import math
import re
TIME_PRINT = 1

print('aaaaaaa')
class DataReader(analyzer.Analyzer):
    CLASS_NAME = 'DataReader'

    @time_deco(TIME_PRINT, CLASS_NAME)
    def __init__(self, name=None, *args, **kwargs):
        analyzer.Analyzer.__init__(self, *args, **kwargs)
        self.rd = Reader(name) if name else Reader()
        self.x, self.ttt, self.y, self.I = [], [], [], []
        self.file = None
        self.bin_file_name = None
        self.bin_file_dataN = None
        self.msg_x_path, self.msg_t_path, self.msg_y_path, self.msg_I_path, self.msg_tx_path = None, None, None, None, None
        self.msg_t_path_list, self.msg_x_path_list, self.msg_y_path_list, self.msg_I_path_list = [], [], [], []
        self.msg_dat_dir = None
        self.msg_t_file_list, self.msg_x_file_list, self.msg_y_file_list, self.msg_I_file_list = [], [], [], []

    @time_deco(TIME_PRINT, CLASS_NAME)
    def select_file(self, num=None, file=None, convert=False, *args, **kwargs):
        if file:
            self.file = file
            # self.bin_file_path=self.file.get_path()[0:-3]+'dat'
            # _file_num=int(os.path.getsize(self.file.get_path())/31.482113747553814/10**7)+1
            # if self.file.name[0:-4] not in [i.name for i in self.file.parent.child if i.isfolder()][0]:
            self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4])
            if not self.msg_dat_dir:
                self.msg_dat_dir = [i for i in self.file.parent.child if i.isfolder() if self.file.name[0:-4] in i.name][0]
            _msg_list = self.rd.get_children_ext_files_list(self.msg_dat_dir, 'dat')
            if _msg_list:
                self.msg_t_file_list = [_fil for _fil in _msg_list if 't' in _fil.name[0:-4]]
                self.msg_x_file_list = [_fil for _fil in _msg_list if 'x' in _fil.name[0:-4]]
                self.msg_y_file_list = [_fil for _fil in _msg_list if 'y' in _fil.name[0:-4]]
                self.msg_I_file_list = [_fil for _fil in _msg_list if 'I' in _fil.name[0:-4]]
            return 'for looping'
        _i = 0
        _file_list = self.rd.get_children_ext_files_list(self.rd.root, 'txt')
        if num:
            _nmn = 0 if len(_file_list) == 1 else num
            self.file = _file_list[_nmn]
            self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4])
            if not self.msg_dat_dir:
                self.msg_dat_dir = [i for i in self.file.parent.child if i.isfolder() if self.file.name[0:-4] in i.name][0]
            _msg_list = self.rd.get_children_ext_files_list(self.msg_dat_dir, 'dat')
            if _msg_list:
                self.msg_t_file_list = [_fil for _fil in _msg_list if 't' in _fil.name[0:-4]]
                self.msg_x_file_list = [_fil for _fil in _msg_list if 'x' in _fil.name[0:-4]]
                self.msg_y_file_list = [_fil for _fil in _msg_list if 'y' in _fil.name[0:-4]]
                self.msg_I_file_list = [_fil for _fil in _msg_list if 'I' in _fil.name[0:-4]]
            return 'for test'
        for _file in _file_list:
            print(_i, _file.get_path())
            _i += 1
        _file_num = input('select the number of file : ')
        self.file = _file_list[int(_file_num)]
        self.bin_file_path = self.file.get_path()[0:-3] + 'dat'
        self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4])
        if not self.msg_dat_dir:
            self.msg_dat_dir = [i for i in self.file.parent.child if i.isfolder() if self.file.name[0:-4] in i.name][0]
        _msg_list = self.rd.get_children_ext_files_list(self.msg_dat_dir, 'dat')
        if _msg_list:
            self.msg_t_file_list = [_fil for _fil in _msg_list if 't' in _fil.name[0:-4]]
            self.msg_x_file_list = [_fil for _fil in _msg_list if 'x' in _fil.name[0:-4]]
            self.msg_y_file_list = [_fil for _fil in _msg_list if 'y' in _fil.name[0:-4]]
            self.msg_I_file_list = [_fil for _fil in _msg_list if 'I' in _fil.name[0:-4]]

    # @time_deco(TIME_PRINT, CLASS_NAME)
    # def read_txt_file_to_tx(self):
    #     # self.x=[line for line in open(self.file.get_path())]
    #     # self.ttt=[line for line in open(self.file.get_path())]
    #     _i = -1
    #     _nnn = 9
    #     # _mmm = _nnn + NNN
    #     for line in open(self.file.get_path(), 'r'):
    #         print(line)
    #         _i += 1
    #         if _i < _nnn:
    #             continue
    #         line = line.split('\t')
    #         try:
    #             self.ttt.append(float(line[0]))
    #             self.x.append(float(line[1]))
    #         except:
    #             pass
    #         if _i > _mmm:
    #             break
    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_bin(self):
        # self.x=[line for line in open(self.file.get_path())]
        # self.ttt=[line for line in open(self.file.get_path())]
        _i = -1
        _nnn = 9
        with open(self.bin_file_path, 'wb+') as f:
            for line in open(self.file.get_path(), 'r'):
                _i += 1
                if _i < _nnn:
                    continue
                line = line.split('\t')
                f.write(struct.pack('ff', float(line[0]), float(line[1])))
                if _i % 10**6 == 0:
                    print(_i)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_msgpack(self):
        _i = -1
        _nnn = 9
        sta = self.ttt.append
        sxa = self.x.append
        sya = self.y.append
        sIa = self.I.append
        for line in open(self.file.get_path(), 'r', encoding='shift_jis'):
            _i += 1
            line = line.split('\t')
            if _i < _nnn:
                if line[0] == 'ChannelTitle=':
                    for i in range(len(line)):
                        if 'x raw' in line[i]:
                            _xi = i
                        elif 'y raw' in line[i]:
                            _yi = i
                        elif 'total intensity' in line[i]:
                            _Ii = i
                continue
            sta(float(line[0]))
            sxa(float(line[_xi]))
            sya(float(line[_yi]))
            sIa(float(line[_Ii]))
            if _i % 5 * 10**7 == 0:
                print(int(_i / 5 * 10**7))
                with open(self.msg_t_path, 'wb') as f:
                    msgpack.dump(self.ttt, f)
                    self.ttt = []
                with open(self.msg_x_path, 'wb') as f:
                    msgpack.dump(self.x, f)
                    self.x = []
                with open(self.msg_y_path, 'wb') as f:
                    msgpack.dump(self.y, f)
                    self.y = []
                with open(self.msg_I_path, 'wb') as f:
                    msgpack.dump(self.I, f)
                    self.I = []

    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_msgpack2(self):
        if self.msg_t_file_list:
            return 1
        _file_separate_num = 10**7
        _i = 0
        _beads_num = 1
        _file_num = 1
        _nnn = 10
        sta = self.ttt.append
        sxa = self.x.append
        sya = self.y.append
        sIa = self.I.append
        for line in open(self.file.get_path(), 'r', encoding='shift_jis'):
            _i += 1
            line = line.split('\t')
            if _i < _nnn:
                if line[0] == 'ChannelTitle=':
                    for k in range(len(line)):
                        if 'x raw' in line[k]:
                            _xi = k
                        elif 'y raw' in line[k]:
                            _yi = k
                        elif 'total intensity' in line[k]:
                            _Ii = k
                # print(_i, line)
                # print('_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                continue
            try:
                sta(float(line[0])), sxa(float(line[_xi])), sya(float(line[_yi])), sIa(float(line[_Ii]))
                RESET = True
            except ValueError:
                if RESET:
                    _i = 1
                    RESET = False
                    print(111, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    print(111, 'len(x):{}'.format(len(self.x)), line)
                    sta, sxa, sya, sIa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                    _beads_num += 1
                    _file_num = 1
                # print('_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                # print(line)
            except Exception:
                exctype, value, tb = sys.exc_info()
                er = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                for val in er:
                    print(str(val))
                print(_i, line)
            if _i % _file_separate_num == 9:
                # print(111, int(_i/_file_separate_num))
                # print(222, len(self.x))
                # print(333, len(self.x), math.log10((len(self.x))))
                print(222, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                print(222, 'len(x):{}'.format(len(self.x)), line)
                sta, sxa, sya, sIa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                _file_num += 1
        if len(self.ttt) > 0:
            print(333, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
            print(333, 'len(x):{}'.format(len(self.x)), line)
            self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)


    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_msgpack3(self):
        if self.msg_t_file_list:
            return 'msg file is already exist'
        _file_separate_num = 10**7
        _i = 0
        _beads_num = 1
        _file_num = 1
        _nnn = 10
        sta = self.ttt.append
        sxa = self.x.append
        sya = self.y.append
        sIa = self.I.append
        com=re.compile('#.{1} (.*)')
        MERGE=False

        for line in open(self.file.get_path(), 'r', encoding='shift_jis'):
            _i += 1
            line = line.strip().split('\t')
            if _i < _nnn:
                if line[0] == 'ChannelTitle=':
                    for k in range(len(line)):
                        if 'x raw' in line[k]:
                            _xi = k
                        elif 'y raw' in line[k]:
                            _yi = k
                        elif 'total intensity' in line[k]:
                            _Ii = k
                    _line_length=len(line)
                # print(_i, line)
                # print('_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                continue
            try:
                assert _line_length<=len(line), 'if it\'s merging, it\'s indicated error.'
                _x=float(line[_xi])
                _x=2*10**(-6)*_x**3 + 4*10**(-5)*_x**2 + 1.0154*_x + 0.6723
                sta(float(line[0])), sxa(float(_x)), sya(float(line[_yi])), sIa(float(line[_Ii]))
                RESET = True
                if len(line)>_line_length:
                    try:
                        _cur_res = re.search(com,line[-1].strip())
                        if _cur_res:
                            if _cur_res.group(1)=='merge':
                                MERGE=True
                    except:
                        pass

            except ValueError:
                if MERGE:
                    RESET = False
                    MERGE = False
                    print('000', '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    print('000', 'len(x):{}'.format(len(self.x)), line)
                    sta, sxa, sya, sIa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                    _file_num += 1

                if RESET:
                    _i = 1
                    RESET = False
                    print(111, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    print(111, 'len(x):{}'.format(len(self.x)), line)
                    sta, sxa, sya, sIa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                    _beads_num += 1
                    _file_num = 1

            except Exception:
                exctype, value, tb = sys.exc_info()
                er = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                for val in er:
                    print(str(val))
                print('erer',_i, line)
                print('erer', '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                print('erer', 'len(x):{}'.format(len(self.x)), line)
            if _i % _file_separate_num == 9:
                # print(111, int(_i/_file_separate_num))
                # print(222, len(self.x))
                # print(333, len(self.x), math.log10((len(self.x))))
                print(222, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                print(222, 'len(x):{}'.format(len(self.x)), line)
                sta, sxa, sya, sIa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                _file_num += 1
        if len(self.ttt) > 0:
            print(333, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
            print(333, 'len(x):{}'.format(len(self.x)), line)
            self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def dump_to_dat_txyI(self, _j=-1, _beads_num=None, _file_num=None):
        mdd_path = self.msg_dat_dir.get_path()
        self.msg_t_path_list.append(mdd_path + '/t{0:0>2}-{1:0>2}.dat'.format(_beads_num, _file_num))
        self.msg_x_path_list.append(mdd_path + '/x{0:0>2}-{1:0>2}.dat'.format(_beads_num, _file_num))
        self.msg_y_path_list.append(mdd_path + '/y{0:0>2}-{1:0>2}.dat'.format(_beads_num, _file_num))
        self.msg_I_path_list.append(mdd_path + '/I{0:0>2}-{1:0>2}.dat'.format(_beads_num, _file_num))
        with open(self.msg_t_path_list[_j], 'wb') as f:
            msgpack.dump(self.ttt, f)
            self.ttt = []
        with open(self.msg_x_path_list[_j], 'wb') as f:
            msgpack.dump(self.x, f)
            self.x = []
        with open(self.msg_y_path_list[_j], 'wb') as f:
            msgpack.dump(self.y, f)
            self.y = []
        with open(self.msg_I_path_list[_j], 'wb') as f:
            msgpack.dump(self.I, f)
            self.I = []
        return self.ttt.append, self.x.append, self.y.append, self.I.append

    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_msg_to_txt_file(self):
        pat=re.compile('t(\d{2})-(\d{2})\.dat')
        for _file_num in range(len(self.msg_t_file_list)):
            with open(self.msg_t_file_list[_file_num].get_path(), 'rb') as f:
                self.ttt.extend(msgpack.load(f))
            with open(self.msg_x_file_list[_file_num].get_path(), 'rb') as f:
                self.x.extend(msgpack.load(f))
            with open(self.msg_y_file_list[_file_num].get_path(), 'rb') as f:
                self.y.extend(msgpack.load(f))
            with open(self.msg_I_file_list[_file_num].get_path(), 'rb') as f:
                self.I.extend(msgpack.load(f))
            print(123,self.msg_t_file_list[_file_num].get_path())
            print(234,len(self.ttt),len(self.x),len(self.y),len(self.I))

            _cur_res = re.search(pat, self.msg_t_file_list[_file_num].name)
            beads_num=_cur_res.group(1)
            file_num=_cur_res.group(2)
            _cur_dir_path=self.msg_t_file_list[_file_num].parent.parent.get_path()+'/txt/'+self.msg_t_file_list[_file_num].parent.name
            if not os.path.exists(_cur_dir_path): os.makedirs(_cur_dir_path)
            _cur_file_path=_cur_dir_path+'/beads{}_{}.txt'.format(beads_num, file_num)
            print(555,len(self.ttt))
            with open(_cur_file_path, 'w+') as f:
                f.write('time(sec),x(nm),y(nm),total intensity(V)\r\n')
                for i in range(len(self.ttt)):
                    f.write('{},{},{},{}\r\n'.format(self.ttt[i], self.x[i], self.y[i], self.I[i]))
                    if i%10**6==0:print(i)

            self.ttt, self.x, self.y, self.I = [],[],[],[]
        # for nm in [ fil.name for fil in self.msg_t_file_list]:
        #     print(nm)



    @time_deco(TIME_PRINT, CLASS_NAME)
    def read_bin_file_to_tx2(self, start, datapoints, _plot_N=10**3):
        start *= 8
        _plot_N = 10**3
        with open(self.bin_file_path, 'rb') as f:
            if not self.bin_file_dataN:
                f.seek(0, 2)
                self.bin_file_dataN = f.tell()
                f.seek(0, 0)
            _plot_data_length = 8 * _plot_N * datapoints if 8 * _plot_N * datapoints < self.bin_file_dataN - start else self.bin_file_dataN - start
            # print(111,_plot_data_length, math.log10(_plot_data_length))
            # print(222,self.bin_file_dataN, math.log10(self.bin_file_dataN))
            # print(333,self.bin_file_dataN-start, math.log10(self.bin_file_dataN-start))
            # print(444,start, math.log10(start))
            # print(555,np.arange(start,_plot_data_length,_plot_data_length/_plot_N, int))
            for i in np.arange(start, start + _plot_data_length, _plot_data_length / _plot_N, int):
                f.seek(i, 0)
                _cur_unpacked = f.read(8)
                _cur_tx = struct.unpack('ff', _cur_unpacked)
                self.ttt.append(_cur_tx[0])
                self.x.append(_cur_tx[1])


    @time_deco(TIME_PRINT, CLASS_NAME)
    def read_msg_file_to_tx2(self, _file_num=None):
        if _file_num == None:
            print('please assign file_number')
        with open(self.msg_t_file_list[_file_num].get_path(), 'rb') as f:
            self.ttt.extend(msgpack.load(f))
        with open(self.msg_x_file_list[_file_num].get_path(), 'rb') as f:
            self.x.extend(msgpack.load(f))
            print(222,self.msg_t_file_list[_file_num].get_path())
            print(len(self.ttt))

    def tetetet(self):
        with open(self.file.get_path(), 'rb') as f:
            _i = 0
            _buf = [0]
            while len(_buf) > 0:
                _buf = f.read(10**8)
                print(_i, len(_buf), type(_buf))
                _i += 1

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_txt_test(self):
        # self.select_file(num=1)
        # self.read_txt_file_to_tx()
        # print(len(self.x), math.log10((len(self.x))))
        # self.plot_timecorse_of_move(show_it=1)
        # self.norm_fit(show_it=1)

        self.select_file(num=1)
        self.read_txt_bufed_file_to_tx()
        print(len(self.x), math.log10((len(self.x))))
        self.plot_timecorse_of_move(show_it=1)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_txt_test2(self):
        self.select_file(num=1)
        self.convert_file_tx_txt_to_msgpack()
        del self.x
        self.read_msg_file_to_tx()
        print(len(self.x), math.log10((len(self.x))))
        # self.plot_timecorse_of_move(show_it=1)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_bin_test(self):
        self.select_file(num=1)
        self.read_bin_file_to_tx()
        print(len(self.x), math.log10((len(self.x))))
        self.plot_timecorse_of_move(show_it=1)
        # self.norm_fit(show_it=1)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_bin_test2(self):
        self.select_file(num=1)
        prf = LineProfiler()
        prf.add_function(self.read_bin_file_to_tx2)
        prf.runcall(self.read_bin_file_to_tx2, start=3 * 10**7, datapoints=10**6)
        prf.print_stats()
        print(len(self.x), math.log10((len(self.x))))
        self.plot_timecorse_of_move(show_it=1)
        # self.norm_fit(show_it=1)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_msg_test(self):
        self.select_file(num=1)
        # prf=LineProfiler()
        # prf.add_function(self.read_msg_file_to_tx)
        # prf.runcall(self.read_msg_file_to_tx)
        self.read_msg_file_to_tx()
        # prf.print_stats()
        print(len(self.x), math.log10((len(self.x))))
        self.plot_timecorse_of_move_sparsely(show_it=1)
        # self.norm_fit(show_it=1)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def DataReader_msg_test2(self):
        self.select_file(num=1)
        self.convert_file_tx_txt_to_msgpack2()
        self.plot_timecorse_of_move_sparsely(show_it=1)

if __name__=='__main__':
    a=DataReader(name='/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data', print_it=0)
    currd=Reader('/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data')
    txtFileList=currd.get_children_ext_files_list(currd.root, 'txt')
    curFileName=[fil for fil in txtFileList if '1-3' in fil.name][0]
    a.select_file(file=curFileName)
    print(a.file.name)
    a.convert_file_tx_txt_to_msgpack3()
    del a
    del currd

    a=DataReader(name='/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data', print_it=0)
    currd=Reader('/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data')
    txtFileList=currd.get_children_ext_files_list(currd.root, 'txt')
    curFileName=[fil for fil in txtFileList if '1-3' in fil.name][0]
    a.select_file(file=curFileName)
    print(a.file.name)
    a.convert_msg_to_txt_file()
    del a
    del currd


    # a=DataReader(name='/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data', print_it=0)
    # currd=Reader('/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data')
    # txtFileList=currd.get_children_ext_files_list(currd.root, 'txt')
    # curFileName=[fil for fil in txtFileList if '2-3' in fil.name][0]
    # a.select_file(file=curFileName)
    # print(a.file.name)
    # a.convert_file_tx_txt_to_msgpack3()
    # del a
    # del currd

    # a=DataReader(name='/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data', print_it=0)
    # currd=Reader('/mnt/hgfs/gnuplot/160516_beadsTrap@higuchiLab/data')
    # txtFileList=currd.get_children_ext_files_list(currd.root, 'txt')
    # curFileName=[fil for fil in txtFileList if '2-3' in fil.name][0]
    # a.select_file(file=curFileName)
    # print(a.file.name)
    # a.convert_msg_to_txt_file()
    # del a
    # del currd


