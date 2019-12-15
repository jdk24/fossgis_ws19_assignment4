import grass.script as gs

w_slope = 1
w_fire = 1
w_landcover = 1 

def main(w_slope, w_fire, w_landcover):
    gs.run_command('g.region', flags='p')
    #calculate hazard
    gs.run_command('r.mapcalc', expression='hazard = slope_reclassified * %i + fire_probability_reclassified * %i + corine_landcover_reclassified * %i', overwrite=True % (w_slope, w_fire, w_landcover))    
    #calculate risk
    gs.run_command('r.mapcalc', expression='risk = hazard * exposuremap_raster * firestations_dist_reclassified', overwrite=True)
if __name__ == '__main__':
    main(w_slope, w_fire, w_landcover)