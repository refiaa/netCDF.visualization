import matplotlib.pyplot as plt
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import os
import imageio.v2 as imageio
    
from shapely.geometry import box
from datetime import datetime, timedelta
from PIL import Image

##################################### DESCRIPTION #########################################
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
#                                                                                         #
###########################################################################################


#############################  NetCDF FILE PARAMETER  #####################################

# nc_filename = 'rivo_Eday_MIROC6_ssp585_r1i1p1f1_gn_20150101-20241231.nc'
# variable_name = 'rivo'
nc_filename = ''
variable_name = ''

lon_min = -180
lon_max = 180
lat_min = -90
lat_max = 90

resolution = (2000, 1000, 1000)  
max_value = 1000

#YYYY/MM/DD
start_date = '2039/01/01' 
end_date = '2039/12/31'

gif_filename = 'output.gif'

color_map = 'coolwarm' 
frame_duration = 15
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

def create_gif(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name):
    dataset = nc.Dataset(nc_file)
    lon = dataset.variables['lon'][:]
    lat = dataset.variables['lat'][:]
    data = dataset.variables[variable_name][:]
    
    lon, lat, data = wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max)
    world_cropped = crop_map(world, lon_min, lon_max, lat_min, lat_max)
    
    frames = []

    def resize_frame(frame, resolution):
        img = Image.fromarray(frame)
        img = img.resize(resolution)
        
        return np.array(img)

    start_date = datetime.strptime(start_date, '%Y/%m/%d')
    end_date = datetime.strptime(end_date, '%Y/%m/%d')

    for i in range(data.shape[0]):
        current_date = start_date + timedelta(days=i)
        
        if current_date <= end_date:
            fig, ax = plt.subplots(figsize=(resolution[0] / 100, resolution[1] / 100))
            world_cropped.boundary.plot(ax=ax, linewidth=1, color='k')

            plt.imshow(data[i, ::-1, :], extent=(lon_min, lon_max, lat_min, lat_max), cmap=color_map, alpha=transparency, vmax=max_value)
            
            plt.title(f'Time: {current_date.strftime("%Y/%m/%d")}')
            plt.colorbar(label=f'{variable_name} ({dataset.variables[variable_name].units})') 
            plt.savefig('./plot/temp.png', dpi=resolution[2], bbox_inches='tight')  
            plt.close()

            frame = imageio.imread('./plot/temp.png')
            frame = resize_frame(frame, resolution[:2])  
            frames.append(frame)

    imageio.mimsave(gif_file_path, frames, duration=frame_duration)
    os.remove('./plot/temp.png')

try:
    world = gpd.read_file('./shp/World_Countries_Generalized.shp')

except Exception as e:
    print(f"Error on shp file: {str(e)}")

BASE_NC_DIR = './nc/'
BASE_GIF_DIR = './plot/'

nc_file = os.path.join(BASE_NC_DIR, nc_filename) 
gif_file_path = os.path.join(BASE_GIF_DIR, gif_filename) 

create_gif(nc_file, gif_file_path, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name)