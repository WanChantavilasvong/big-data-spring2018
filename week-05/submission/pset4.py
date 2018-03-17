from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import os
%matplotlib inline

#Identifying locations and paths
DATA = "week-05/materials/"

#0: Read in raster data
def tif2array(location):
    """
    Should:
    1. Use gdal.open to open a connection to a file.
    2. Get band 1 of the raster
    3. Read the band as a numpy array
    4. Convert the numpy array to type 'float32'
    5. Return the numpy array.
    """
    data = gdal.Open(location)
    band = data.GetRasterBand(1)
    band_array = band.ReadAsArray()
    return band_array.astype('float32')
#0: Read in metadata return
def process_string (st):
    """
    Parses Landsat metadata
    """
    return float(st.split(' = ')[1].strip('\n'))
def retrieve_meta(meta_text):
    with open(meta_text) as f:
        meta = f.readlines()
    matchers = ['RADIANCE_MULT_BAND_10', 'RADIANCE_ADD_BAND_10', 'K1_CONSTANT_BAND_10', 'K2_CONSTANT_BAND_10']
    matching = [process_string(s) for s in meta if any(xs in s for xs in matchers)]
    return matching
#1: Filtering out the clouds
def cloud_filter(array, bqa):
    array_dest = array.copy()
    array_dest[np.where((bqa != 2720) & (bqa != 2724) & (bqa != 2728) & (bqa != 2732)) ] = 'nan'
    return array_dest
#2: Calculate Top of Atmosphere Spectral Radiance
def rad_calc(tirs, var_list):
    rad_mult_b10, rad_add_b10, k1_b10, k2_b10 = var_list
    rad = (rad_mult_b10 * tirs) + rad_add_b10
    return rad
#3: Calculate Brightness Temperature
def bt_calc(rad, var_list):
    rad_mult_b10, rad_add_b10, k1_b10, k2_b10 = var_list
    bt = k2_b10 / np.log((k1_b10/rad) + 1) - 273.15
    return bt
#4: Calculate Normalized Difference Vegetation Index
def ndvi_calc(red, nir):
    ndvi = (nir - red) / (nir + red)
    return ndvi
#5: Calculate Proportional Vegetation
def pv_calc(ndvi, ndvi_s, ndvi_v):
    pv = ((ndvi - ndvi_s) / (ndvi_v - ndvi_s))** 2
    return pv
#6: Calculate Land Surface Emissitivity
def emissivity_calc (pv, ndvi):
    ndvi_dest = ndvi.copy()
    ndvi_dest[np.where(ndvi < 0)] = 0.991
    ndvi_dest[np.where((0 <= ndvi) & (ndvi < 0.2)) ] = 0.966
    ndvi_dest[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ] = (0.973 * pv[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ]) + (0.966 * (1 - pv[np.where((0.2 <= ndvi) & (ndvi < 0.5)) ]) + 0.005)
    ndvi_dest[np.where(ndvi >= 0.5)] = 0.973
    return ndvi_dest
#7: Final calculation of Land Surface Temperature
def lst_calc(location):
    #1. Define constants
    wave = 10.8E-06
    h = 6.626e-34 # PLANCK'S CONSTANT
    c = 2.998e8 # SPEED OF LIGHT
    s = 1.38e-23 # BOLTZMANN's CONSTANT
    p = h * c / s
    ndvi_s = 0.2
    ndvi_v = 0.5
    #2. Read in tifs
    red_path = os.path.join(location, 'LC08_L1TP_012031_20170716_20170727_01_T1_B4.TIF')
    nir_path = os.path.join(location, 'LC08_L1TP_012031_20170716_20170727_01_T1_B5.TIF')
    tirs_path = os.path.join(location, 'LC08_L1TP_012031_20170716_20170727_01_T1_B10.TIF')
    bqa_path = os.path.join(location, 'LC08_L1TP_012031_20170716_20170727_01_T1_BQA.TIF')
    red_unfiltered = tif2array(red_path)
    nir_unfiltered = tif2array(nir_path)
    tirs_unfiltered = tif2array(tirs_path)
    bqa = tif2array(bqa_path)
    #3. Filter out the clouds
    red = cloud_filter(red_unfiltered, bqa)
    nir = cloud_filter(nir_unfiltered, bqa)
    tirs = cloud_filter(tirs_unfiltered, bqa)

    #3. Retrieve variables from metadata
    meta_file = os.path.join(location, 'LC08_L1TP_012031_20170716_20170727_01_T1_MTL.txt')
    var_meta = retrieve_meta(meta_file)
    #4. Calculate ndvi, rad, bt, pv, emis
    ndvi = ndvi_calc(red, nir)
    rad = rad_calc(tirs, var_meta)
    bt = bt_calc(rad, var_meta)
    pv = pv_calc(ndvi, ndvi_s, ndvi_v)
    emis = emissivity_calc(pv, ndvi)
    #5. Calculate land surface temperature and return it.
    lst = bt / (1 + (wave * bt / p) * np.log(emis))
    return lst
#8: Export back to raster data
def array2tif(raster_file, new_raster_file, array):
    """
    Writes 'array' to a new tif, 'new_raster_file',
    whose properties are given by a reference tif,
    here called 'raster_file.'
    """
    # Invoke the GDAL Geotiff driver
    raster = gdal.Open(raster_file)

    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(new_raster_file,
                        raster.RasterXSize,
                        raster.RasterYSize,
                        1,
                        gdal.GDT_Float32)
    out_raster.SetProjection(raster.GetProjection())
    # Set transformation - same logic as above.
    out_raster.SetGeoTransform(raster.GetGeoTransform())
    # Set up a new band.
    out_band = out_raster.GetRasterBand(1)
    # Set NoData Value
    out_band.SetNoDataValue(-1)
    # Write our Numpy array to the new band!
    out_band.WriteArray(array)

#-------------------------------------------------------------------------------
##NDVI
#Run the lansat data through the Normalized Difference Vegetation Index function
red_path = os.path.join(DATA, 'LC08_L1TP_012031_20170716_20170727_01_T1_B4.TIF')
nir_path = os.path.join(DATA, 'LC08_L1TP_012031_20170716_20170727_01_T1_B5.TIF')
bqa_path = os.path.join(DATA, 'LC08_L1TP_012031_20170716_20170727_01_T1_BQA.TIF')
red_unfiltered = tif2array(red_path)
nir_unfiltered = tif2array(nir_path)
bqa = tif2array(bqa_path)
red = cloud_filter(red_unfiltered, bqa)
nir = cloud_filter(nir_unfiltered, bqa)
ndvi = ndvi_calc(red, nir)
plt.imshow(ndvi, cmap='YlGn')
plt.colorbar()
#Export NDVI.tif with clouds filtered.
out_path = os.path.join(DATA, 'chantavilasvong_ndvi_20170716.tif')
tirs_path = os.path.join(DATA, 'LC08_L1TP_012031_20170716_20170727_01_T1_B10.TIF') #for export reference
array2tif(tirs_path, out_path, ndvi)

#LST
#Run the lansat data through the Land Suurface Temperature function (cloud_filter embedded)
lst = lst_calc(DATA)
plt.imshow(lst, cmap='RdYlGn')
plt.colorbar()
#Export LST.tif with clouds filtered.
out_path = os.path.join(DATA, 'chantavilasvong_lst_20170716.tif')
tirs_path = os.path.join(DATA, 'LC08_L1TP_012031_20170716_20170727_01_T1_B10.TIF') #for export reference
array2tif(tirs_path, out_path, lst)
