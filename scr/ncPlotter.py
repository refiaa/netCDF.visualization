import matplotlib.pyplot as plt
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import os
import imageio.v2 as imageio

from eofs.standard import Eof
from io import BytesIO
from shapely.geometry import box
from datetime import datetime, timedelta
from PIL import Image


##################################### DESCRIPTION ################## ver 1.0.2 ############
#                                                                                         #
#            Input the name and variable of the nc file into PARAMETER,                   #
#                and specify the desired lon and lat range for output.                    #
#                                                                                         #
#             You can change the date by specifying start_date and end_date.              #
#                                                                                         #
#                                      !NOTICE!                                           #
#                                                                                         #
#            ***DATA WILL NOT SHOW PROPERLY WHEN LON RANGE IS NOT -90 to 90***            #
#                                                                                         #
###########################################################################################


################################# netCDF FILE VARIABLE ####################################

nc_filename = 'clt_day_CNRM-CM5_rcp85_r1i1p1_20210101-20251231.nc'
variable_name = 'clt'

lon_min = 115
lon_max = 155
lat_min = 20
lat_max = 60

resolution = (500, 500, 800)  
max_value = 100

start_date = '2039/01/01'
end_date = '2039/01/05'

gif_filename = 'output.gif'

color_map = 'coolwarm' 
frame_duration = 250
transparency = 0.7

###########################################################################################

if not os.path.exists('./plot'):
    os.makedirs('./plot')

def wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max):
    if len(lon.shape) == 2:
        lon_1d = np.mean(lon, axis=0)
    else:
        lon_1d = lon
        
    if len(lat.shape) == 2:
        lat_1d = np.mean(lat, axis=0)
    else:
        lat_1d = lat

    wrapped_lon = (lon_1d + 180) % 360 - 180
    sorted_indices_lon = np.argsort(wrapped_lon)
    wrapped_data = data[:, :, sorted_indices_lon]

    lon_mask = (wrapped_lon[sorted_indices_lon] >= lon_min) & (wrapped_lon[sorted_indices_lon] <= lon_max)
    lat_mask = (lat_1d >= lat_min) & (lat_1d <= lat_max)

    wrapped_data = wrapped_data[:, lat_mask, :]
    wrapped_data = wrapped_data[:, :, lon_mask]

    return wrapped_lon[sorted_indices_lon][lon_mask], lat_1d[lat_mask], wrapped_data

def crop_map(data, lon_min, lon_max, lat_min, lat_max):
    return data.cx[lon_min:lon_max, lat_min:lat_max]

def create_GIF(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name):
    dataset = nc.Dataset(nc_file)
    
    lon = dataset.variables['lon'][:]
    lat = dataset.variables['lat'][:]
    
    data = dataset.variables[variable_name][:]
    
    lon, lat, data = wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max)
    
    frames = []

    start_date = datetime.strptime(start_date, '%Y/%m/%d')
    end_date = datetime.strptime(end_date, '%Y/%m/%d')

    fig, ax = plt.subplots(figsize=(resolution[0] / 100, resolution[1] / 100))
    world.boundary.plot(ax=ax, linewidth=1, color='k')

    im = ax.imshow(data[0, ::-1, :], extent=(lon_min, lon_max, lat_min, lat_max), cmap=color_map, alpha=transparency, vmax=max_value)
    colorbar = fig.colorbar(im, ax=ax, label=f'{variable_name} ({dataset.variables[variable_name].units})')
    title = ax.set_title('')

    for i in range(data.shape[0]):
        current_date = start_date + timedelta(days=i)

        if current_date <= end_date:
            im.set_data(data[i, ::-1, :])
            title.set_text(f'Time: {current_date.strftime("%Y/%m/%d")}')

            with BytesIO() as buf:
                plt.savefig(buf, format='png', dpi=resolution[2], bbox_inches='tight')
                buf.seek(0)
                frame = Image.open(buf)
                frame = frame.resize(resolution[:2])
                frames.append(frame)

    frames[0].save(gif_file_path, save_all=True, append_images=frames[1:], duration=frame_duration, loop=0)
    plt.close(fig)  
    
try:
    world = gpd.read_file('./shp/World_Countries_Generalized.shp')

except Exception as e:
    print(f"Fail to load shapefile: {str(e)}")

BASE_NC_DIR = './nc/'
BASE_GIF_DIR = './plot/'

nc_file = os.path.join(BASE_NC_DIR, nc_filename)
gif_file_path = os.path.join(BASE_GIF_DIR, gif_filename)

create_GIF(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name)

