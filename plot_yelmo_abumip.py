#!/home/sergio/anaconda3/envs/yelmo_tools/bin/python3
#  Libraries
import yelmo_tools.yelmo_functions as yf
import yelmo_tools.yelmo_plot_functions as ypf
import yelmo_tools.yelmo_gif_functions as ygf

import os
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import netCDF4 as nc

# Variables
# GENERIC
locplot = '/home/sergio/entra/proyectos/d01/plots/'
locdata = '/home/sergio/entra/proyectos/d01/output/ismip6/abumip32km/'
locsources = '/home/sergio/entra/proyectos/d01/sources/'

experiments = ['abum_02f', 'abum_02ff5', 'abum_02ff2', 'abum_02ff',
               'abum_02fc5', 'abum_02fc5f5', 'abum_02fc5f2', 'abum_02fc5f']
control_run = None  # 'abuc_01'  # set to None if needed
out_fldr = '/ismip6_abumip/abum_02/'
plot_name, gif_name, gif3_name = 'yelmo_abum_02.png', 'yelmo_abum_02.gif', 'yelmo_abum_02_3D.gif'
set_ax = 'Off'  # Do you want to draw axis?

# PLOTTING
shades1D = [0, 0, 1]    # abuc, abuk, abum | from Sun et al., 2020
color = ['black', 'blue', 'red', 'green', 'darkgrey',
         'lightblue', 'orange', 'lime']  # ['blue', 'red', 'orange']
linestyles = ['solid', 'solid', 'solid',
              'solid', 'solid', 'solid', 'solid', 'solid']
linewidths = [8, 8, 8, 8, 4, 4, 4, 4]
fig_size = [2, 4]  # nrows, ncols
fnt_size1D, fnt_size2D = 28, 35  # fontsize

# GIFs
FPS = 1
times2plot = [0, 1, 2, 3, 4, 5, 7, 9, 10, 13, 15, 18, 20, 25, 30,
              35, 40, 45, 50]  # list(np.arange(0, 52, 2))

# YELMO simulation
res, lenx, leny, lent, lent2D = 32, 191, 191, 501, 51
region_names = ['WAIS', 'EAIS', 'PAIS']
basin_names = ['1, Filchner-Ronne RSB', '2, Riiser-Larsen, Stancomb, Brunt', '3, Fimbul', '4, Baudouin', '5, Shirase, Holmes', '6, Amery', '7, Shackleton, West', '8, Totten (ASB)', '9, Cook, Ninnis, Mertz (WSB)',
               '10, Rennick (WSB)', '11, Drygalski (WSB)', '12, Ross', '13, Getz', '14, Pine Island, Thwaites (AMS)', '15, Abbot', '16, Wilkins, Stange, Bach, George VI', '17', '18, Larsen C', '19']

# Switches
sVAF = 0
sHCHANGE = 0
sZSRF = 0
sUXY = 0
sFWF = 0
sRMSE_HU = 0
sGIFS, zgif, hgif, ugif = 0, 0, 0, 0
sGIFS3D, zgif3D, hgif3D = 1, 0, 1   # only one at a time

# SCRIPT
# -- Directories
if os.path.isdir(locplot) == False:
    print('Plot main directory does not exist!')
if os.path.isdir(locdata) == False:
    print('Data main directory does not exist!')

if os.path.isdir(locplot+out_fldr) == False:
    os.mkdir(locplot+out_fldr)
if os.path.isdir(locplot+out_fldr+'/contributions/') == False:
    os.mkdir(locplot+out_fldr+'/contributions')
    print('/contributions/ made and ready')

# -- Calculations
# ---- Initialization
n = len(experiments)
if sVAF == 1:
    print('*** VAF and SLR ***')
    VAFdata, dVAFdata = np.empty((n, lent)), np.empty((n, lent))
    if any(shades1D) != 0:
        shades = np.empty((3, 2, 2, 51))
        kindlist, varlist, abumip_exps = ['min', 'max'], [
            'VAF', 'SLR'], ['ABUC', 'ABUK', 'ABUM']
        data_shades = nc.Dataset(
            locsources + '/ABUMIP_results/ABUMIP_vaf-slr-shades.nc')
    for i in range(3):
        if shades1D[i] != 0:
            for j in range(len(varlist)):
                for k in range(len(kindlist)):
                    shades[i, j, k, :] = data_shades.variables[kindlist[k] +
                                                               varlist[j]+' '+abumip_exps[i]][:]
        else:
            shades[i, :, :, :] = None
if sHCHANGE == 1:
    print('*** H_change ***')
    H_change, Hreg_change, Hbas_change = ma.empty(
        (n, lenx, leny)), np.empty((n, 3)), np.empty((n, 2, 19))
    hmask_bed = ma.empty((n, lenx, leny))
if sZSRF == 1:
    print('*** z_srf ***')
    z_srf = ma.empty((n, lenx, leny))
    zmask_bed = ma.empty((n, lenx, leny))
if sUXY == 1:
    print('*** uxy_s ***')
    uxy_s = ma.empty((n, lenx, leny))
    umask_bed = ma.empty((n, lenx, leny))
if sFWF == 1:
    print('*** fwf ***')
    fwf = ma.empty((n, lent))
if sRMSE_HU == 1:
    print('*** H and uxy RMSE ***')
    rmse_H, rmse_uxy = ma.empty((n, lent2D)), ma.empty((n, lent2D))
if sGIFS == 1:
    print('*** making gifs ... (time consuming) ***')
    zmask_bed_gif = ma.empty((n, len(times2plot), lenx, leny))
    if zgif == 1:
        z_srf_gif = ma.empty((n, len(times2plot), lenx, leny))
    if hgif == 1:
        H_grnd_gif = ma.empty((n, len(times2plot), lenx, leny))
    if ugif == 1:
        uxy_s_gif = ma.empty((n, len(times2plot), lenx, leny))
if sGIFS3D == 1:
    print('*** making gifs 3D ... (very time consuming) ***')
    zmask_bed_gif3 = ma.empty((n, len(times2plot), lenx, leny))
    if zgif3D == 1:
        z_srf_gif3 = ma.empty((n, len(times2plot), lenx, leny))
    if hgif3D == 1:
        H_grnd_gif3 = ma.empty((n, len(times2plot), lenx, leny))


# ---- Calcs
for i in range(n):
    if sVAF == 1:
        datan = yf.LoadYelmo1D(experiments[i], 'V_sl', locdata)
        if control_run != None:
            ref = yf.LoadYelmo1D(control_run, 'V_sl', locdata)
            drift = yf.Drift(ref)
            datan = datan - drift
        vaf = yf.SLE(datan*1e6)
        dvaf = yf.SLR(datan*1e6)
        VAFdata[i, :], dVAFdata[i, :] = vaf, dvaf

    if sHCHANGE == 1:
        H_grnd, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'H_grnd', locdata, time=[0, -1])
        basins, xc, yc = yf.LoadYelmo2D(experiments[i], 'basins', locdata)
        maskbed, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'mask_bed', locdata, time=0)

        if control_run != None:
            ref = yf.LoadYelmo3D(control_run, 'H_grnd', locdata, time=[0, -1])
            drift = yf.Drift(ref)
            H_grnd = H_grnd - drift
        H_change[i, :, :], Hreg_change[i, :], Hbas_change[i,
                                                          :, :] = yf.Hchange(H_grnd, basins=basins, resolution=res, basins_nasa=locsources + '/ANT-32KM/ANT-32KM_BASINS-nasa.nc')
        hmask_bed[i, :, :] = maskbed
        H_change[i, :, :] = ma.masked_where(
            hmask_bed[i, :, :] == 0, H_change[i, :, :])

        if i == 0:
            print('--> Each contribution is stored with plots')
        with open(locplot + out_fldr + '/contributions/' + 'Hreg_change-' + experiments[i] + '.txt', 'w') as f:
            f.write('#### ' + experiments[i] + ' ####' + '\n')
            f.write('\n')
            f.write('** Contribution to sea-level rise by each region **' + '\n')
            for j in range(len(region_names)):
                f.write(region_names[j] + ' --> ' +
                        str(Hreg_change[i, j])+'    m SLE' + '\n')
            f.write('\n')
            f.write('** Contribution to sea-level rise by each basin **' + '\n')
            for k in range(len(basin_names)):
                f.write(basin_names[k] + '  --> ' +
                        str(Hbas_change[i, 0, k])+' m SLE' + '\n')

    if sZSRF == 1:
        zsrf, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'z_srf', locdata, time=-1)
        maskbed, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'mask_bed', locdata, time=-1)

        if control_run != None:
            ref = yf.LoadYelmo3D(control_run, 'z_srf', locdata, time=-1)
            drift = yf.Drift(ref)
            zsrf = zsrf - drift

        zsrf = ma.masked_where(maskbed == 0, zsrf)
        z_srf[i, :, :], zmask_bed[i, :, :] = zsrf/1000, maskbed

    if sUXY == 1:
        uxys, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'uxy_s', locdata, time=-1)
        maskbed, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'mask_bed', locdata, time=-1)

        if control_run != None:
            ref = yf.LoadYelmo3D(control_run, 'uxy_s', locdata, time=-1)
            drift = yf.Drift(ref)
            uxys = uxys - drift

        uxys = ma.masked_where(maskbed == 0, uxys)
        uxy_s[i, :, :], umask_bed[i, :, :] = uxys, maskbed

    if sFWF == 1:
        fwf[i, :] = yf.LoadYelmo1D(experiments[i], 'fwf', locdata)

    if sRMSE_HU == 1:
        rmse_H[i, :], rmse_uxy[i, :] = yf.Load1DYelmo2D(
            experiments[i], 'rmse_H', locdata), yf.Load1DYelmo2D(experiments[i], 'rmse_uxy', locdata)

    if sGIFS == 1:
        maskbedgif, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'mask_bed', locdata, time=times2plot)
        zmask_bed_gif[i, :, :, :] = maskbedgif

        if zgif == 1:
            z_gif, xc, yc = yf.LoadYelmo3D(
                experiments[i], 'z_srf', locdata, time=times2plot)

            if control_run != None:
                ref = yf.LoadYelmo3D(control_run, 'z_srf',
                                     locdata, time=times2plot)
                drift = yf.Drift(ref)
                z_gif = z_gif - drift

            z_gif = ma.masked_where(maskbedgif == 0, z_gif)
            z_srf_gif[i, :, :, :] = z_gif/1000
        if hgif == 1:
            Hgif, xc, yc = yf.LoadYelmo3D(
                experiments[i], 'H_grnd',  locdata, time=times2plot)

            if control_run != None:
                ref = yf.LoadYelmo3D(control_run, 'H_grnd', locdata, time=-1)
                drift = yf.Drift(ref)
                Hgif = Hgif - drift

            Hgif = ma.masked_where(maskbedgif == 0, Hgif)
            H_grnd_gif[i, :, :, :] = Hgif
        if ugif == 1:
            u_gif, xc, yc = yf.LoadYelmo3D(
                experiments[i], 'uxy_s', locdata, time=times2plot)

            if control_run != None:
                ref = yf.LoadYelmo3D(control_run, 'uxy_s', locdata, time=-1)
                drift = yf.Drift(ref)
                u_gif = u_gif - drift

            u_gif = ma.masked_where(maskbedgif == 0, u_gif)
            uxy_s_gif[i, :, :, :] = u_gif
    if sGIFS3D == 1:
        maskbedgif3, xc, yc = yf.LoadYelmo3D(
            experiments[i], 'mask_bed', locdata, time=times2plot)
        zmask_bed_gif3[i, :, :, :] = maskbedgif3

        if zgif3D == 1:
            z_gif3, xc, yc = yf.LoadYelmo3D(
                experiments[i], 'z_srf', locdata, time=times2plot)

            if control_run != None:
                ref = yf.LoadYelmo3D(control_run, 'z_srf',
                                     locdata, time=times2plot)
                drift = yf.Drift(ref)
                z_gif3 = z_gif3 - drift

            z_gif3 = ma.masked_where(maskbedgif3 == 0, z_gif3)
            z_srf_gif3[i, :, :, :] = z_gif3/1000
        if hgif3D == 1:
            Hgif3, xc, yc = yf.LoadYelmo3D(
                experiments[i], 'H_grnd',  locdata, time=times2plot)

            if control_run != None:
                ref = yf.LoadYelmo3D(control_run, 'H_grnd', locdata, time=-1)
                drift = yf.Drift(ref)
                Hgif3 = Hgif3 - drift

            Hgif3 = ma.masked_where(maskbedgif3 == 0, Hgif3)
            H_grnd_gif3[i, :, :, :] = Hgif3

# -- Plots
if sVAF == 1:
    ypf.comPlot1D(VAFdata, dVAFdata, r'VAF', r'm', r'$\Delta$VAF', r'm', 'yr', [0, 100, 200, 300, 400, 500], locplot+out_fldr, shades, text=False,
                  labels=experiments, color=color, linestyles=linestyles, linewidths=linewidths, file_name='vaf-'+plot_name, fontsize=fnt_size1D)
if sHCHANGE == 1:
    ypf.Map2D(H_change, xc, yc, r'Grounded Ice thickness change (Relative change)', experiments, np.arange(0, 1.1, 0.1),
              contours=hmask_bed, contours_levels=[1, 4], cmap='cmo.tempo', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='Hchange-'+plot_name, fontsize=fnt_size2D, set_ax=set_ax)
if sZSRF == 1:
    ypf.Map2D(z_srf, xc, yc, r'Ice surface elevation (km)', experiments, np.arange(0, 4.5+0.1, 0.1),
              contours=zmask_bed, contours_levels=[1, 4], cmap='jet', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='zsurf-'+plot_name, fontsize=fnt_size2D, set_ax=set_ax)
if sUXY == 1:
    ypf.Map2D(uxy_s, xc, yc, r'Ice surface velocity (m/a)', experiments, [0, 1e4],
              contours=zmask_bed, contours_levels=[1, 4], cmap='cmo.solar_r', log_scale=True, fig_size=fig_size, plotpath=locplot+out_fldr, file_name='uxys-'+plot_name, fontsize=fnt_size2D, set_ax=set_ax)
if sFWF == 1:
    ypf.Plot1D(fwf, 'Freshwater flux', 'Sv',  'yr', locplot+out_fldr, labels=experiments,
               file_name='fwf-'+plot_name)
if sRMSE_HU == 1:
    ypf.comPlot1D(rmse_H, rmse_uxy, r'Ice thickness RMSE', r'm', r'Ice surface velocity RMSE', r'm/a', '10 yr', [0, 10, 20, 30, 40, 50], locplot+out_fldr, text=False,
                  labels=experiments, color=color, linestyles=linestyles, linewidths=linewidths, file_name='rmse_hu-'+plot_name, fontsize=fnt_size1D)

if sGIFS == 1:
    if zgif == 1:
        ygf.map2gif(xc, yc, z_srf_gif, r'Ice surface elevation (km)',
                    experiments, times2plot, np.arange(0, 4.5+0.1, 0.1), contours=zmask_bed_gif, con_levels=[1, 4], cmap='jet', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='zsurf-'+gif_name, FPS=FPS, fontsize=fnt_size2D, set_ax=set_ax)
        # ygf.mkGif(xc, yc, z_srf_gif, r'Ice surface elevation (km)',
        #          experiments, times2plot, np.arange(0, 4.5+0.1, 0.1), contours=zmask_bed_gif, con_levels=[1, 4], cmap='jet', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='zsurf-'+gif_name)
    if hgif == 1:
        ygf.map2gif(xc, yc, H_grnd_gif, r'Grounded ice thickness (m)',
                    experiments, times2plot, np.arange(0, 4500+500, 500), contours=zmask_bed_gif, con_levels=[1, 4], cmap='cmo.ice_r', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='Hgrnd-'+gif_name, FPS=FPS, fontsize=fnt_size2D, set_ax=set_ax)
    if ugif == 1:
        ygf.map2gif(xc, yc, uxy_s_gif, r'Ice surface velocity (m/a)',
                    experiments, times2plot, [0, 1e4], contours=zmask_bed_gif, con_levels=[1, 4], cmap='cmo.solar_r', log_scale=True, fig_size=fig_size, plotpath=locplot+out_fldr, file_name='uxys-'+gif_name, FPS=FPS, fontsize=fnt_size2D, set_ax=set_ax)
if sGIFS3D == 1:
    if zgif3D == 1:
        ygf.map2gif(xc, yc, z_srf_gif3, r'Ice surface elevation (km)',
                    experiments, times2plot, np.arange(0, 4.5+0.1, 0.1), contours=zmask_bed_gif3, con_levels=[1, 4], cmap='jet', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='zsurf-'+gif3_name, FPS=FPS, fontsize=fnt_size2D, set_ax=set_ax, vis='3D')
    if hgif3D == 1:
        ygf.map2gif(xc, yc, H_grnd_gif3, r'Grounded ice thickness (m)',
                    experiments, times2plot, np.arange(0, 4500+500, 500), contours=zmask_bed_gif3, con_levels=[1, 4], cmap='cmo.ice_r', fig_size=fig_size, plotpath=locplot+out_fldr, file_name='Hgrnd-'+gif3_name, FPS=FPS, fontsize=fnt_size2D, set_ax=set_ax, vis='3D')