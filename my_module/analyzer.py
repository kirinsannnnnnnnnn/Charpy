import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from time_deco import time_deco
import matplotlib.pyplot as plt
import numpy as np
from scipy import special
import os, os.path
import math
from scipy import stats
from scipy import optimize
import random

TIME_PRINT=1

@time_deco(TIME_PRINT, '')
def test():
    print('ok')

if __name__=='__main__':
    test()

if __name__=='data_reader':
    print('tttttttttttttttttttesttttttttttttttttttt')
print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')

TIME_PRINT=1
class Data():
    CLASS_NAME='Data'
    @time_deco(TIME_PRINT, CLASS_NAME)
    def __init__(self,print_it=1, k=None, loop_num=None,*args, **kwds):# ):
        self.loop_num = loop_num if loop_num else 2**20
        self.x, self.v = [], []
        self.deltat = 1 * 10**(-3)  # [us]
        self.ttt = [i * self.deltat for i in range(self.loop_num + 1)]
        self.freq, self.power_spectrum = [], []

        self.yeta = 0.001  # [Pa*s]=[pN*us*nm^-2]=[pg*us^-1*nm^-1]
        self.a = 1000  # [nm]
        self.gamma = 6 * math.pi * self.yeta * \
            self.a  # [kg/s]->[pN*us*nm^-1]=[pg*us^-1]
        self.k = k if k else 10**3  # [pN*nm^-1]=[pg*us^-2]
        self.T = 25 + 273.15  # [K]
        # [J*K^-1]=[N*m*K^-1]->[pN*nm*K^-1]=[pg*nm^2*us^-2*K^-1]
        self.kb = 1.38064852 * 10**(-2)
        # [1/J]->[1/pN*nm]=[1/pg*nm^2*us^-2]
        self.beta = 1. / (self.kb * self.T)
        self.m = 9.2 / 10**2  # [pg] (9.2*10^-17 kg)
        self.D = 1 / self.beta / self.gamma  # []
        self.n = self.loop_num
        self.omega = 2 * math.pi / math.sqrt(self.k / self.m)
        if print_it:
            print(
                "gamma    is  " + str(round(self.gamma, 3)) + "   pN*usec/nm")
            print(" k   is  " + str(self.k) + " pN/nm")
            print(" deltat  is  " + str(self.deltat) + "        usec")
            print("beta is  " + str(round(self.beta, 3)) + "    1/pJ")
            print(" m   is  " + str(self.m) + " pg")
            print(" D   is  " + str(round(self.D, 3)) + "   nm^2/us")
            print(" n   is  10^" + str(round(np.log10(self.n), 3)))
            print('omega is ', self.omega)
            print('4mk is ', 4 * self.m * self.k, 'gamma^2 is ', self.gamma**2)
            print('\n')

        self.norm_dist_CDF = lambda x, mu, sig: 1. / 2. * \
            (1. + special.erf((x - mu) / np.sqrt(2.) / sig))
        self.norm_dist_PDF = lambda x, mu, sig: (
            1. / np.sqrt((2. * np.pi * sig**2.))) * np.exp(-((x - mu)**2.) /
                                                           (2. * sig**2.))
        self.norm_params, self.norm_params_covariance = [], []
        self.lorentzian_func = lambda f, k_est: (
            4. * self.gamma / k_est**2. / self.beta) / (1. + (2. * np.pi * f * self.gamma / k_est)**2.)
        self.lorentzian_params, self.lorentzian_params_covariance = [], []


class Plotter(Data):
    CLASS_NAME='Plotter'
    @time_deco(TIME_PRINT, CLASS_NAME)
    def show_save_fig(self, fig, show_it=0, save_it=0, save_dir=None, save_name=None):
        if show_it:
            plt.show()
        if save_it:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            plt.savefig(save_dir + '/' + save_name)
        plt.close()

    @time_deco(TIME_PRINT, CLASS_NAME)
    def plot_timecorse_of_move(self, show_it=0, save_it=0, save_dir=None, save_name=None, _xAxis_label=None):
        _fig = plt.figure()
        ax1 = _fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax1.plot(self.ttt, self.x)
        if not _xAxis_label:_xAxis_label='sec'
        ax1.set_xlabel(_xAxis_label)
        ax1.set_ylabel('nm')
        ax1.set_xlim(min(self.ttt), max(self.ttt))
        self.show_save_fig(_fig, show_it=show_it, save_it=save_it,
                           save_dir=save_dir, save_name=save_name)
    
    @time_deco(TIME_PRINT, CLASS_NAME)
    def plot_timecorse_of_move_sparsely(self, show_it=0, save_it=0, save_dir=None, save_name=None, _xAxis_label=None, start=0,end=None):
        _data_num=len(self.ttt)
        _sparseness=3333
        _start=int(start)
        if not end==None:
            _end=int(end)
            _data_num=_end-_start
        _fig = plt.figure()
        ax1 = _fig.add_axes([0.1, 0.1, 0.8, 0.8])
        print(123,'int(data_num/sparseness + 1):{}, data_num:{}'.format(int(_data_num/_sparseness+1), _data_num))
        _cur_t=[self.ttt[i] for i in range(_start,_end,int(_data_num/_sparseness+1))]
        _cur_x=[self.x[i] for i in range(_start,_end,int(_data_num/_sparseness+1))]
        ax1.plot(_cur_t, _cur_x)
        if not _xAxis_label:_xAxis_label='sec'
        ax1.set_xlabel(_xAxis_label)
        ax1.set_ylabel('nm')
        ax1.set_xlim(min(_cur_t), max(_cur_t))
        ax1.set_ylim(min(_cur_x), max(_cur_x))
        self.show_save_fig(_fig, show_it=show_it, save_it=save_it,
                           save_dir=save_dir, save_name=save_name)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def hist_norm_of_move(self, show_it=0, save_it=0, save_dir=None, save_name=None):
        _mu, _sig = self.norm_params[0], self.norm_params[1]
        _a, _b, _patch = plt.hist(self.x, normed=False, bins=100)
        plt.close()
        _minx, _maxx, _maxheight = min(self.x), max(self.x), max([_patch[i].get_height() for i in range(len(_patch))])
        _n = self.norm_dist_PDF(
            _mu, _mu, _sig) / _maxheight

        _fig = plt.figure()
        _ax1 = _fig.add_axes([0.1, 0.1, 0.8, 0.8])
        _ax1.hist(self.x, cumulative=True, bins=100,
                  normed=False, histtype='step')
        _tx = np.linspace(min(self.x), max(self.x), 100)
        _ax1.plot(_tx, self.norm_dist_CDF(_tx, _mu, _sig) * len(self.x))
        _ax1.set_xlabel('[nm]')
        _ax1.set_ylim(0, len(self.x))
        _ax2 = _ax1.twinx()
        _ax2.hist(self.x, normed=False, alpha=0.2, bins=100)
        _ax2.plot(_tx, self.norm_dist_PDF(_tx, _mu, _sig) / _n)
        plt.text(_minx+0.8*(_maxx - _minx), 1*_maxheight,'ave:{} nm'.format(str(round(self.norm_params[0], 2))))
        plt.text(_minx+0.8*(_maxx - _minx), 0.95*_maxheight,'std:{} nm'.format(str(round(self.norm_params[1], 2))))
        self.show_save_fig(_fig, show_it=show_it, save_it=save_it,
                           save_dir=save_dir, save_name=save_name)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def hist_norm_of_move_sparsely(self, show_it=0, save_it=0, save_dir=None, save_name=None, start=0, end=0):
        _sparseness=10**4
        if not end:print('asign statr and end!')
        _start=int(start)
        _end=int(end)
        _data_num=_end-_start
        print(223,'int(data_num/sparseness + 1):{}, data_num:{}'.format(int(_data_num/_sparseness+1), _data_num))
        _cur_x=[self.x[i] for i in range(_start,_end,int(_data_num/_sparseness+1))]

        _bin_num=1000
        _mu, _sig = self.norm_params[0], self.norm_params[1]
        _a, _b, _patch = plt.hist(_cur_x, normed=False, bins=_bin_num)
        plt.close()
        _minx, _maxx, _maxheight = min(_cur_x), max(_cur_x), max([_patch[i].get_height() for i in range(len(_patch))])
        _n = self.norm_dist_PDF(_mu, _mu, _sig) / _maxheight

        _fig = plt.figure()
        _ax1 = _fig.add_axes([0.1, 0.1, 0.8, 0.8])
        _ax1.hist(_cur_x, cumulative=True, bins=_bin_num,normed=False, histtype='step')
        _tx = np.linspace(min(_cur_x), max(_cur_x), 100)
        _ax1.plot(_tx, self.norm_dist_CDF(_tx, _mu, _sig) * len(_cur_x))
        _ax1.set_xlabel('[nm]')
        _ax1.set_ylim(0, len(_cur_x))
        _ax2 = _ax1.twinx()
        _ax2.hist(_cur_x, normed=False, alpha=0.2, bins=_bin_num)
        _ax2.plot(_tx, self.norm_dist_PDF(_tx, _mu, _sig) / _n)
        plt.text(_minx+0.8*(_maxx - _minx), 1*_maxheight,'ave:{} nm'.format(str(round(self.norm_params[0], 2))))
        plt.text(_minx+0.8*(_maxx - _minx), 0.95*_maxheight,'std:{} nm'.format(str(round(self.norm_params[1], 2))))
        self.show_save_fig(_fig, show_it=show_it, save_it=save_it,
                           save_dir=save_dir, save_name=save_name)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def plot_powerspectrum(self, show_it=0, save_it=0, save_dir=None, save_name=None):
        _fig = plt.figure()
        _ax1 = _fig.add_axes([0.1, 0.1, 0.8, 0.8])
        _ax1.set_xscale('log')
        _ax1.set_yscale('log')
        _ax1.plot(self.freq, self.power_spectrum)
        self.show_save_fig(_fig, show_it=show_it, save_it=save_it,
                           save_dir=save_dir, save_name=save_name)

class Fitter(Data):
    CLASS_NAME='Fitter'
    @time_deco(TIME_PRINT, CLASS_NAME)
    def norm_fit(self, show_it=0, save_it=0, save_dir=None, save_name=None):
        _guess = [stats.tmean(self.x), stats.tstd(self.x)]
        _x = self.x
        _x.sort()
        self.norm_params, self.norm_params_covariance = optimize.curve_fit(
            self.norm_dist_CDF, _x, [(i + 1) / len(_x) for i in range(len(_x))], _guess)
        self.hist_norm_of_move(
            show_it=show_it, save_it=save_it, save_dir=save_dir, save_name=save_name)

    def norm_fit_sparsely(self, show_it=0, save_it=0, save_dir=None, save_name=None, start=0, end=0):
        if not end:print('norm fit:asign end')
        _sparseness=10**4
        _start=int(start)
        _end=int(end)
        _data_num=_end-_start
        print(223,'int(data_num/sparseness + 1):{}, data_num:{}'.format(int(_data_num/_sparseness+1), _data_num))
        _cur_x=[self.x[i] for i in range(_start,_end,int(_data_num/_sparseness+1))]

        _guess = [stats.tmean(self.x), stats.tstd(self.x)]
        _x = _cur_x
        _x.sort()
        self.norm_params, self.norm_params_covariance = optimize.curve_fit(
            self.norm_dist_CDF, _x, [(i + 1) / len(_x) for i in range(len(_x))], _guess)
        self.hist_norm_of_move_sparsely(
            show_it=show_it, save_it=save_it, save_dir=save_dir, save_name=save_name, start=start, end=end)

    @time_deco(TIME_PRINT, CLASS_NAME)
    def lorentzian_fit(self):
        _guess = [self.k]
        self.lorentzian_params, self.lorentzian_params_covariance = optimize.curve_fit(
            self.lorentzian_func, self.freq, self.power_spectrum, _guess)
        print(111, self.lorentzian_params, self.k)

class Calculator(Data):
    CLASS_NAME='Calculator'
    @time_deco(TIME_PRINT, CLASS_NAME)
    def calc_power_spectrum(self, window_size_num, overlap_rate_num, show_it=0,
                            save_it=0, save_dir=None, save_name=None):
        _m = int(self.loop_num / window_size_num)
        _fs = 1 / self.deltat * 10**6
        _shift = int(_m / overlap_rate_num)
        # print("sampling point for FFT is  10^"+str(np.log10(m)))
        # print("sampling rate is   "+str(fs/1000)+" kHz")
        # print("overlap is "+str(shift/m*100)+" %\n")
        _hammingWindow = np.hamming(_m)
        _windowedx = []
        _x_FFT = []
        _x_pow = []

        _startx = int(-1 * _shift)
        _i = 0
        while _startx < len(self.x) - self.loop_num + 1:
            _startx += _shift
            _windowedx.append(_hammingWindow * self.x[_startx: _startx + _m])
            _x_FFT.append(np.fft.rfft(_windowedx[_i]))
            _x_pow.append([(c.real**2 + c.imag**2) * 2 / (_m * _fs)
                           for c in _x_FFT[_i]])
            _i += 1
        _x_pow_ave = [0 for i in range(len(_x_pow[0]))]
        for _xp in _x_pow:
            for i in range(len(_xp)):
                _x_pow_ave[i] += _xp[i] / len(_x_pow)
        self.freq = np.arange(0, _fs / 2., 1. * _fs / _m)
        # print('wsn='+str(window_size_num)+'_orn='+str(overlap_rate_num))
        self.power_spectrum = _x_pow_ave[0: len(self.freq)]

        if show_it:
            self.plot_powerspectrum(show_it=show_it)
        if save_it:
            self.plot_powerspectrum(
                save_it=save_it, save_dir=save_dir, save_name=save_name)


class Analyzer(Plotter, Fitter, Calculator):
    CLASS_NAME='Analyzer'
    pass

class Simulator(Analyzer):
    CLASS_NAME='Simulator'
    @time_deco(TIME_PRINT, CLASS_NAME)
    def __init__(self):
      Analyzer.__init__(self)
      self.x, self.v=[0],[0]

    @time_deco(TIME_PRINT, CLASS_NAME)
    def simpleMD(self, show_it=0, save_it=0, save_dir=None, save_name=None):
        for _t in range(self.loop_num):
            _deltav = -(self.k * self.x[_t] / self.m +
                        self.gamma * self.v[_t] / self.m) * self.deltat
            self.v.append(self.v[_t] + _deltav)
            _deltax = self.v[_t] * self.deltat + \
                random.normalvariate(0, math.sqrt(2 * self.D * self.deltat))
            self.x.append(self.x[_t] + _deltax)
        self.plot_timecorse_of_move(
            show_it=show_it, save_it=save_it, save_dir=save_dir, save_name=save_name)

