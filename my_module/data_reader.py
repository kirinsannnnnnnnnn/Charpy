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
import reader
importlib.reload(reader)
import msgpack
import struct
import numpy as np
import math
import re
import matplotlib.pyplot as plt

TIME_PRINT = 1

print('my_module/data_reader.py is loaded')
class DataReader(analyzer.Analyzer):
    CLASS_NAME = 'DataReader'

    @time_deco(TIME_PRINT, CLASS_NAME)
    def __init__(self, name=None, *args, **kwargs):
        analyzer.Analyzer.__init__(self, *args, **kwargs)
        self.rd = reader.Reader(name) if name else reader.Reader()
        self.dat_dic={'t':[], 'x':[], 'y':[], 'I':[]}
        self.dat_sparse_dic={'t':[], 'x':[], 'y':[], 'I':[]}

        self.file, self.msg_dat_dir = None, None
        self.msg_path_list_dic={'t':[], 'x':[], 'y':[], 'I':[]}
        self.msg_file_list_dic={'t':[], 'x':[], 'y':[], 'I':[]}
        self.msg_sparse_file_dic = {'t':[], 'x':[], 'y':[], 'I':[]}
        self.dat_keys=['t', 'x', 'y', 'I']

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

        if num!=None:
            self.file = _file_list[num]
            self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4])
            if not self.msg_dat_dir:
                self.msg_dat_dir = [i for i in self.file.parent.child if i.isfolder() if self.file.name[0:-4] in i.name][0]
            _msg_list = self.rd.get_children_ext_files_list(self.msg_dat_dir, 'dat')
            if _msg_list:
                for _dat_key in self.dat_keys:
                    self.msg_file_list_dic[_dat_key] = [_fil for _fil in _msg_list if _dat_key in _fil.name[0:-4]]
            return 'for test'

        for _file in _file_list:
            print(_i, _file.get_path())
            _i += 1
        _file_num = input('select the number of file : ')
        self.file = _file_list[int(_file_num)]
        self.msg_dat_dir = self.rd.make_dir(self.file.parent, self.file.name[0:-4])
        if not self.msg_dat_dir:
            self.msg_dat_dir = [i for i in self.file.parent.child if i.isfolder() if self.file.name[0:-4] in i.name][0]
        _msg_list = self.rd.get_children_ext_files_list(self.msg_dat_dir, 'dat')

        if _msg_list:
            for _dat_key in self.dat_keys:
                self.msg_file_list_dic[_dat_key] = [_fil for _fil in _msg_list if _dat_key in _fil.name[0:-4]]

    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_file_tx_txt_to_msgpack3(self):
        # convert txt file to binary file with messagepack
        # separate in each beads and ecery 10^5 timepoints in order to read dat file fast
        try:
            assert len(self.msg_file_list_dic['t'])<=0, 'msg file is already exist'

            _file_separate_num = 10**5
            _i, _beads_num, _file_num, _nnn = 0, 1, 1, 10
            com=re.compile('#.{1} (.*)')
            MERGE=False
            _di={'t':0}

            sa={} # append function
            for _dat_key in self.dat_keys:
                sa[_dat_key] = self.dat_dic[_dat_key].append

            for line in open(self.file.get_path(), 'r', encoding='shift_jis'):
                _i += 1
                line = line.strip().split('\t')
                if _i < _nnn:
                    if line[0] == 'ChannelTitle=':
                        for k in range(len(line)):
                            for _dat_key, label in zip(self.dat_keys, ['time is arrow', 'x raw', 'y raw', 'total intensity']):
            # self.dat_keys=['t', 'x', 'y', 'I']
                                if label in line[k]:
                                    _di[_dat_key] = k
                        _line_length=len(line)
                    # print(_i, line)
                    # print('_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    continue
                try:
                    assert _line_length<=len(line), 'if it\'s merging, it\'s intentional error.'
                    line[_di['x']]=(lambda x: 2*10**(-6)*x**3 + 4*10**(-5)*x**2 + 1.0154*x + 0.6723) ( float(line[_di['x']]) )

                    for _dat_key in self.dat_keys:
                        sa[_dat_key](float( line[_di[_dat_key]] ))
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
                        print('000', 'len(x):{}'.format(len(self.dat_dic['x'])), line)
                        sa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                        _file_num += 1

                    if RESET:
                        _i = 1
                        RESET = False
                        print(111, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                        print(111, 'len(x):{}'.format(len(self.dat_dic['x'])), line)
                        sa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                        _beads_num += 1
                        _file_num = 1

                except Exception:
                    exctype, value, tb = sys.exc_info()
                    er = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    for val in er:
                        print(str(val))
                    print('erer',_i, line)
                    print('erer', '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    print('erer', 'len(x):{}'.format(len(self.dat_dic['x'])), line)
                    a=input('erer teaeeeeeeeeeeeeeest')

                if _i % _file_separate_num == 9:
                    # print(111, int(_i/_file_separate_num))
                    # print(222, len(self.x))
                    # print(333, len(self.x), math.log10((len(self.x))))
                    print(222, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                    print(222, 'len(x):{}'.format(len(self.dat_dic['x'])), line)
                    sa = self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
                    _file_num += 1

            if len(self.dat_dic['t']) > 0:
                print(333, '_i:{}, beads_num:{}, file_num:{}'.format(_i, _beads_num, _file_num))
                print(333, 'len(x):{}'.format(len(self.dat_dic['x'])), line)
                self.dump_to_dat_txyI(_beads_num=_beads_num, _file_num=_file_num)
        except AssertionError:
            pass

    @time_deco(TIME_PRINT, CLASS_NAME)
    def dump_to_dat_txyI(self, _beads_num=None, _file_num=None):
        mdd_path = self.msg_dat_dir.get_path()
        for _dat_key in self.dat_keys:
            self.msg_path_list_dic[_dat_key].append(mdd_path + '/{0}{1:0>2}-{2:0>4}.dat'.format(_dat_key, _beads_num, _file_num))
            with open(self.msg_path_list_dic[_dat_key][-1], 'wb') as f:
                msgpack.dump(self.dat_dic[_dat_key], f)
                self.dat_dic[_dat_key] = []
        sa={} # append function
        for _dat_key in self.dat_keys:
            sa[_dat_key] = self.dat_dic[_dat_key].append
        return sa


    @time_deco(TIME_PRINT, CLASS_NAME)
    def convert_msg_to_txt_file(self):
        pat=re.compile('t(\d{2})-(\d{4})\.dat')
        for _file_num in range(len(self.msg_file_list_dic['t'])):
            for _dat_key in self.dat_keys:
                with open(self.msg_file_list_dic[_dat_key][_file_num].get_path(), 'rb') as f:
                    self.dat_dic[_dat_key].extend(msgpack.load(f)) 
            print(123,self.msg_t_file_list[_file_num].get_path())
            print(234,len(self.ttt),len(self.x),len(self.y),len(self.I))

            _cur_res = re.search(pat, self.msg_file_list_dic['t'][_file_num].name)
            beads_num=int(_cur_res.group(1))
            file_num=int(_cur_res.group(2))
            _cur_dir_path=self.msg_file_list_dic['t'][_file_num].parent.parent.get_path()+'/txt/'+self.msg_file_list_dic['t'][_file_num].parent.name
            if not os.path.exists(_cur_dir_path): os.makedirs(_cur_dir_path)
            _cur_file_path=_cur_dir_path+'/beads{}_{}.txt'.format(beads_num, file_num)
            print(555,len(self.ttt))
            with open(_cur_file_path, 'w+') as f:
                f.write('time(sec),x(nm),y(nm),total intensity(V)\r\n')
                for i in range(len(self.ttt)):
                    f.write('{},{},{},{}\r\n'.format(self.dat_dic['t'][i], self.dat_dic['x'][i], self.dat_dic['y'][i], self.dat_dic['I'][i]))
                    if i%10**6==0:print(i)

            self.dat_dic['t'], self.dat_dic['x'], self.dat_dic['y'], self.dat_dic['I'] = [],[],[],[]

    @time_deco(TIME_PRINT, CLASS_NAME)
    def read_msg_file_to_tx2(self, _file_num=None):
        assert _file_num != None, 'assign file_number'
        with open(self.msg_file_list_dic['t'][_file_num].get_path(), 'rb') as f:
            self.dat_dic['t'].extend(msgpack.load(f))
        with open(self.msg_file_list['x'][_file_num].get_path(), 'rb') as f:
            self.dat_dic['x'].extend(msgpack.load(f))
            print(222,self.msg_file_list_dic['t'][_file_num].get_path())
            print(len(self.dat_dic['t']))

    @time_deco(TIME_PRINT, CLASS_NAME)
    def make_sparse_msg_file(self):
        print(self.msg_file_list_dic['t'])
        assert self.msg_file_list_dic['t'] != [], 'can\'t recognize msg files'
        try:
            assert self.msg_sparse_file_dic['t'] != [], 'msg sparse file exist already'

            for _dat_key in self.dat_keys:

                _cur_dir_path = self.msg_file_list_dic[_dat_key][0].parent.get_path()+'/sparse'
                if not os.path.exists(_cur_dir_path): os.makedirs(_cur_dir_path)
                self.msg_sparse_file_dic[_dat_key].append( _cur_dir_path+'/{}_sparse.dat'.format(_dat_key) )

                for fil in self.msg_file_list_dic[_dat_key]:
                    with open(fil.get_path(), 'rb') as f:
                        _cur_dat=msgpack.load(f)
                        self.dat_sparse_dic[_dat_key].extend([_cur_dat[i] for i in range(len(_cur_dat)) if i%1000==0])
                print(_dat_key, len(self.dat_sparse_dic[_dat_key]))
                with open(self.msg_sparse_file_dic[_dat_key][0], 'wb') as f:
                    msgpack.dump(self.dat_dic[_dat_key], f)
        except AssertionError:
            pass

if __name__=='__main__':
    pass