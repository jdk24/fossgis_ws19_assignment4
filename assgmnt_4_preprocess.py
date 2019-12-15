import grass.script as gs

def main():

    data_dir = 'D:/Projekte_Julian/GIS/fossgis_ws19_assignment4/assignment4_data/'

    # set region 
    gs.run_command('g.region', vector='tarragona_region@PERMANENT')
    # set resolution to 1km
    gs.run_command('g.region', res=1000)

    # reclassify corine landcover
    # import landcover data
    gs.run_command('r.import', input=data_dir+'corine_landcover_2018/CLC2018_tarragona.tif', output='corine_landcover', overwrite=True)
    # reclass landcover values
    gs.run_command('r.reclass', input='corine_landcover', output='corine_landcover_reclassified', rules=data_dir+'reclass/corine.txt', overwrite=True)
    # resample for permanent reclass
    gs.run_command('r.resample', input='corine_landcover_reclassified', output='corine_landcover_reclassified', overwrite=True)

    # calculate and reclassify the slope
    # import dems
    gs.run_command('r.import', title='DEM_N41E000', input=data_dir+'/dem/N41E000.SRTMGL1.hgt.zip', output='dem_N41E000', overwrite=True)
    gs.run_command('r.import', title='DEM_N40E000', input=data_dir+'/dem/N40E000.SRTMGL1.hgt.zip', output='dem_N40E000', overwrite=True)
    gs.run_command('r.import', title='DEM_N41E001', input=data_dir+'/dem/N41E001.SRTMGL1.hgt.zip', output='dem_N41E001', overwrite=True)
    # first create dem mosaic
    gs.run_command('i.image.mosaic', input= ['dem_N41E000', 'dem_N40E000', 'dem_N41E001'], output='dem_mosaic', overwrite=True)
    # calculating the slope
    gs.run_command('r.slope.aspect', elevation='dem_mosaic', slope='dem_slope', format='degrees', precision='FCELL', overwrite=True)
    # reclassifying the slope
    gs.run_command('r.reclass', input='dem_slope', output='slope_reclassified', rules=data_dir+'reclass/slope.txt', overwrite=True)
    # resample for permanent reclass
    gs.run_command('r.resample', input='slope_reclassified', output='slope_reclassified', overwrite=True)

    # calculate the exposure, probability for ignition of fire and distance to fire stations
    # import osm
    gs.run_command('v.import', input=data_dir+'/osm/fire_stations.geojson', output='firestations', overwrite=True)
    gs.run_command('v.import', input=data_dir+'/osm/buildings.geojson', output='buildings', overwrite=True)
    # and fire data
    gs.run_command('v.import', input=data_dir+'/fire_incidents/fire_archive_V1_89293.shp', output='fires', overwrite=True)        
    # make new grid maps for each calculations 
    gs.run_command('v.mkgrid', map='fire_map', position='region', box='1000,1000', overwrite=True)
    gs.run_command('v.mkgrid', map='exposure_map', position='region', box='1000,1000', overwrite=True)
    gs.run_command('v.mkgrid', map='firestations_map', position='region', box='1000,1000', overwrite=True)
    # get point occurences in grid via vector stats 
    gs.run_command('v.vect.stats', points='fires', count_column='fires_cnt', areas='fire_map')
    gs.run_command('v.vect.stats', points='buildings', type='centroid', count_column='buildings_cnt', areas='exposure_map')
    gs.run_command('v.vect.stats', points='firestations', type='point,centroid', count_column='firestations_cnt',  areas='firestations_map')
    # rasterize the results for raster calc
    gs.run_command('v.to.rast', input='fire_map', output='fire_rast', attribute_column='fires_cnt', use='attr', overwrite=True)
    gs.run_command('v.to.rast', input='exposure_map', output='exposuremap_rast', attribute_column='buildings_cnt', use='attr', type='area', overwrite=True)
    gs.run_command('v.to.rast', input='firestations_map', output='firestations_rast' ,attribute_column='firestations_cnt',use='attr', overwrite=True)
    # calculate fire probability 
    gs.run_command('r.mapcalc', expression='fire_prob = if (fire_rast> 15, 15, fire_rast * 100 / 15)', overwrite=True)
    # set setting all empty fire station grids null and calculate distance 
    gs.run_command('r.null', setnull='0', map='firestations_rast')
    gs.run_command('r.grow.distance', input='firestations_rast', distance='firestations_dist', overwrite=True)
    # reclass the results
    gs.run_command('r.reclass', input='fire_prob', output='fire_prob_class', rules=data_dir+'reclass/prob_fire.txt', overwrite=True)
    gs.run_command('r.reclass', input='exposuremap_rast', output='exposuremap_class', rules=data_dir+'osm_building.txt', overwrite=True)
    gs.run_command('r.reclass', input='firestations_dist', output='firestations_dist_reclassified', rules=data_dir+'/fire_stat_distance.txt', overwrite=True)
    # resample to make classification results permanent
    gs.run_command('r.resample', input='fire_prob_class', output='fire_prob_class', overwrite=True)
    gs.run_command('r.resample', input='exposure_class', output='exposuremap_reclassified', overwrite=True)
    gs.run_command('r.resample', input='firestations_dist_reclassified', output='firestations_dist_reclassified', overwrite=True)

if __name__ == '__main__':
    main()