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
            self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4]) # rd.make_dir(parent_dir_path, dir_name) return False if dir_name exists under parent_dir_path
            if not self.msg_dat_dir: #if msg_dat_dir exists already
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

    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_msgpack3(self):
        # convert txt file to binary file with messagepack
        # separate in each beads and ecery 10^6 timepoints 
        #  because 10^6 is upper limit of the amount can read fast

        if self.msg_t_file_list:
            return 'msg file is already exist'
        _file_separate_num = 10**6
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

    @time_deco(TIME_PRINT, CLASS_NAME)
    def read_msg_file_to_tx2(self, _file_num=None):
        assert _file_num != None, 'assign file_number'
        with open(self.msg_t_file_list[_file_num].get_path(), 'rb') as f:
            self.ttt.extend(msgpack.load(f))
        with open(self.msg_x_file_list[_file_num].get_path(), 'rb') as f:
            self.x.extend(msgpack.load(f))
            print(222,self.msg_t_file_list[_file_num].get_path())
            print(len(self.ttt))

if __name__=='__main__':
    pass