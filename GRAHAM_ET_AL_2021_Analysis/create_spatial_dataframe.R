

rasters_to_spatdf <- function(){
  Sep1718.r.W <- rast('data/rasters/DoD_Sep17_Sep18_weight.tif')
  Sep1718.r.T <- rast('data/rasters/DoD_Sep17_Sep18_threshold.tif')
  Wint1618.r.W <- rast('data/rasters/DoD_Dec16_Jan18_weight.tif')
  Wint1618.r.T <- rast('data/rasters/DoD_Dec16_Jan18_threshold.tif')
  
  feedsigns <- read_sf(file.path(dirname(here()),
                                 'GRAHAM_ET_AL_2021_PROCESSING/feed_data/FS_1618.shp'))
  
  zones <- read_sf(file.path(dirname(here()),
                             'GRAHAM_ET_AL_2021_PROCESSING/int_files/Woodland_Zones20m.gpkg')) %>%
    mutate(signs_YN = ifelse(st_intersects(., st_union(st_buffer(feedsigns, 10)), 
                                           sparse = FALSE)[,1], 1, 0)) %>%
    group_by(signs_YN) %>%
    group_split()
  
  # rescale <- function(x, x.min = NULL, x.max = NULL, new.min = 0.01, new.max = 1) {
  #   if(is.null(x.min)) x.min = minValue(x)
  #   if(is.null(x.max)) x.max = maxValue(x)
  #   new.min + (x - x.min) * ((new.max - new.min) / (x.max - x.min))
  # }
  
  t <- terra::mask(Sep1718.r.W$DoD_1, vect(bind_rows(zones))) 
  tp <- terra::as.polygons(t, trunc=F, dissolve=F, values=T) %>%
    st_as_sf()
  
  gen_df <- function(.ras, .lodMethod, .survdate){
    # .moran.weight <- MoranLocal(raster(.ras)) %>%
    #   rescale(.) %>%
    #   rast() 
    
    mask_ras <- function(.zone){
      
      # zone.m.w <- terra::mask(.moran.weight, vect(.zone), touches=F) %>%
      #   as.data.frame() 
      
      terra::mask(.ras, vect(.zone), touches=F) %>%
        as.data.frame(., xy=TRUE) %>%
        rename(canopy_change = !any_of(c('x', 'y') )) %>%
        mutate(signs_YN = unique(.zone$signs_YN),
               signs_YNf = ifelse(signs_YN==1, 'Foraging Observed', 
                                  "No Foraging"),
               time_step = .survdate,
               LoD_method = .lodMethod,
               # Moran.weight = zone.m.w$layer
               )
    }
    
    ras.df <- zones %>%
      map(., ~ mask_ras(.x)) %>%
      bind_rows() %>%
      tibble()
    
  }
  
  ras.list <- list(Sep1718.r.W$DoD_1, Sep1718.r.T$DoD_1, Sep1718.r.W$DoD_3,
                   Wint1618.r.W$DoD_1, Wint1618.r.T$DoD_1, Wint1618.r.T$DoD_3)
  
  lod.m.list <- rep(c('LoD95 weighting', 'LoDmin threshold', 'No LoD'),2)
  
  date.list <- c(rep("Sep17 - Sep18",3), rep("Dec16 - Jan18",3))
  
  comb.ras.df <- list(ras.list, lod.m.list, date.list) %>%
    pmap(., ~ gen_df(..1, ..2, ..3)) %>%
    bind_rows() %>%
    mutate(loss_gain = ifelse(canopy_change <0, "Decrease", ifelse(canopy_change > 0, "Increase", "No change"))) %>%
    mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) %>%
    mutate(LoD_method = fct_relevel(LoD_method, 'No LoD', 'LoD95 weighting', 'LoDmin threshold' )) %>%
    drop_na()
  
}

