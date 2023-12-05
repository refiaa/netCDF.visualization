import matplotlib.pyplot as plt
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import os
import imageio.v2 as imageio
import winsound as ws

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
#           *** DATA WILL NOT SHOW PROPERLY WHEN LON RANGE IS NOT -90 to 90 ***           #
#          *** NEVER SET lon RANGE -180 to 180 after 231121 commited version ***          #
#                                                                                         #
###########################################################################################


################################# netCDF FILE VARIABLE ####################################

variable_name = 'r1d'

lon_min = 120
lon_max = 150
lat_min = 22.40
lat_max = 47.60

# width, height, dpi
resolution = (1190, 1000, 800)  
max_value = 15

# YYYY/MM/DD
start_date = '2015/01/01'
end_date = '2015/01/01'

gif_filename = 'output.gif'

# matplotlib Colormap Reference
color_map = 'coolwarm' 

# milliseconds
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

def convert_to_date(time_val, year):
    return datetime(year, 1, 1) + timedelta(days=time_val - 1)

def create_GIF(nc_file, gif_file_path, file_name, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name):
    dataset = nc.Dataset(nc_file)

    lon = dataset.variables['lon'][:]
    lat = dataset.variables['lat'][:]
    time = dataset.variables['time'][:]
    time_units = dataset.variables['time'].units

    reference_date_str = time_units.split('since ')[-1].split('.')[0]
    if len(reference_date_str.split()) == 1:
        reference_date_str += " 00:00:00"
    reference_date = datetime.strptime(reference_date_str, "%Y-%m-%d %H:%M:%S")

    dates = [reference_date + timedelta(days=int(t)) for t in time]
    
    file_start_date = dates[0].strftime('%Y/%m/%d')
    file_end_date = dates[-1].strftime('%Y/%m/%d')
    
    print(f"Processing file: {file_name}")
    print(f"Time Range: {file_start_date} ~ {file_end_date}")

    user_start_date_dt = datetime.strptime(start_date, '%Y/%m/%d')
    user_end_date_dt = datetime.strptime(end_date, '%Y/%m/%d')

    if user_start_date_dt < dates[0] or user_end_date_dt > dates[-1]:
        print("Time range is out of range.")
        return
    
    data = dataset.variables[variable_name][:]

    lon, lat, data = wrap_data(lon, lat, data, lon_min, lon_max, lat_min, lat_max)

    frames = []

    fig, ax = plt.subplots(figsize=(resolution[0] / 100, resolution[1] / 100))
    world.boundary.plot(ax=ax, linewidth=1, color='k')

    im = ax.imshow(data[0, ::-1, :], extent=(lon_min, lon_max, lat_min, lat_max), cmap=color_map, alpha=transparency, vmax=max_value)
    colorbar = fig.colorbar(im, ax=ax, label=f'{variable_name} ({dataset.variables[variable_name].units})')
    title = ax.set_title('')

    for i in range(len(dates)):
        current_date = dates[i]

        if user_start_date_dt <= current_date <= user_end_date_dt:
            im.set_data(data[i, ::-1, :])
            title.set_text(f'Time: {current_date.strftime("%Y/%m/%d")}')

            with BytesIO() as buf:
                plt.savefig(buf, format='png', dpi=resolution[2], bbox_inches='tight')
                buf.seek(0)
                
                frame = Image.open(buf)
                frame = frame.resize(resolution[:2])
                frames.append(frame)

    if frames:
        frames[0].save(gif_file_path, save_all=True, append_images=frames[1:], duration=frame_duration, loop=0)
        
    else:
        print("No frames generated within the specified date range.")

    plt.close(fig)

    dataset.close()
    
try:
    world = gpd.read_file('./shp/World_Countries_Generalized.shp')

except Exception as e:
    print(f"Fail to load shapefile: {str(e)}")

def scan_directory(directory_path):
    nc_files = []
    for file in os.listdir(directory_path):
        if file.endswith('.nc'):
            nc_files.append(file)
    return nc_files

def generate_output_filename(input_filename):
    base_filename = input_filename.rsplit('.', 1)[0]
    return base_filename + '.gif'

def main():
    directory_path = './nc/' 
    nc_files = scan_directory(directory_path) 

    for file_name in nc_files:
        nc_file = os.path.join(directory_path, file_name)
        gif_filename = generate_output_filename(file_name)
        gif_file_path = os.path.join('./plot/', gif_filename)

        create_GIF(nc_file, gif_file_path, file_name, lon_min, lon_max, lat_min, lat_max, start_date, end_date, resolution, transparency, max_value, color_map, frame_duration, variable_name)

        frequency = 2500  
        duration = 500
        ws.Beep(frequency, duration)

if __name__ == "__main__":
    main()