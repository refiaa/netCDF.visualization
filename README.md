# netCDF.visualization
py code for visualize netCDF(.nc) climate file


This is a Python code designed to output the IPCC's CMIP. It is verified to function
with the nc datasets from CMIP5 and CMIP6. 

There is a known issue when the lat values in the nc files range from -90 to 90, but this will be addressed in future updates.
To use, input the name of the nc file and its variables in the PARAMETER, and set the desired lon and lat range. Dates can be adjusted using start_date and end_date.


There is no netCDF file in this project. You hav to download a nc file from this kind of site : https://esgf-node.llnl.gov/search/cmip6/

・using wgs84 coordinate system but you can chg shp file to use other coordination system.

## update list

231101 : change gif creation method to optimize 
231108 : change gif plotting method for better performance



## Example 

### using pr_day_CNRM-CM6-1-HR_ssp585_r1i1p1f2_gr_20150101-20391231
![output1](https://github.com/refiaa/netCDF.visualization/assets/112306763/0950bb13-9d5d-4003-bfa2-5562b1f69afd)

## 

### using rivo_Eday_MIROC6_ssp585_r1i1p1f1_gn_20150101-20241231
![output2](https://github.com/refiaa/netCDF.visualization/assets/112306763/785ac5da-91c7-403c-81c8-77a851c8a344)

##

### Also work confirmed in : 

rivo_Eday_MIROC6_ssp585_r1i1p1f1_gn_20150101-20241231.nc         
prc_day_CanESM5_ssp126_r12i1p2f1_gn_20150101-21001231.nc                
clt_day_CNRM-CM5_rcp85_r1i1p1_20210101-20251231.nc                   
pr_day_CNRM-CM6-1-HR_ssp585_r1i1p1f2_gr_20150101-20391231.nc   

##

## Shp file info 

shp is from ArcGIS :

Layer: World_Countries_Generalized (ID:0)
View In:   Map Viewer

Name: World_Countries_Generalized

Display Field:

Type: Feature Layer

Geometry Type: esriGeometryPolygon

Description: <div style="text-align:Left;"><div><div><p><span>World Countries Generalized represents generalized boundaries for the countries of the world.</span></p></div></div></div>

Copyright Text: Sources: Esri; Garmin International, Inc.; U.S. Central Intelligence Agency (The World Factbook); National Geographic Society

Min. Scale: 0

Max. Scale: 0

Default Visibility: true

Max Record Count: 2000

Supported query Formats: JSON
