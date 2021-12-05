# # Proportion of Change in area
#
# # -------------------- load libraries ---------------
library(tidyverse)
library(gt)
library(grid)
library(gridExtra)
library(png)
library(broom)
library(ggfortify)
library(quantreg)
library(RColorBrewer)
library(here)
library(terra)
library(sf)
library(purrr)
library(raster)
library(spmoran)
library(tictoc)
#
# #  ---------- set plotting themes -----------

theme_set(theme_bw() +
            theme(legend.position = 'bottom',
                  legend.key.size = unit(0.75, "cm"),
                  text = element_text(size=12),
                  strip.background =element_rect(fill="grey99"),
                  axis.title.y = element_text(margin = margin(t = 0, r = 10, b = 0, l = 0)),
                  axis.title.x = element_text(margin = margin(t = 10, r = 0, b = 0, l = 0))))


#
# # ----------- Load Data -------------------------
#

source('create_spatial_dataframe.R')

change_df <- rasters_to_spatdf()

# old version using csv from python export - results are the same.
# change_df <- read_csv('./data/CWC_can_change_df.csv') %>%
#   mutate(loss_gain = ifelse(canopy_change <0, "LOSS", ifelse(canopy_change > 0, "GAIN", "NO_CHANGE"))) %>%
#   mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) %>%
#   mutate(LoD_method = ifelse(LoD_method =='weighted', 'LoD95 weighting',
#                              ifelse(LoD_method == 'no lod', 'No LoD',
#                                     ifelse(LoD_method == 'threshold', 'LoDmin threshold', NA)))) %>%
#   mutate(LoD_method = fct_relevel(LoD_method, 'No LoD', 'LoD95 weighting', 'LoDmin threshold')) %>%
#   drop_na()


# --------- density plot -----------------

can_change_density <- function(.data){
  .data %>%
    mutate(signs_YNf = ifelse(signs_YNf == 'No Foraging', 'No', 'Yes')) %>%
    mutate(signs_YNf = fct_relevel(signs_YNf,   "Yes", "No")) %>%
    ggplot(., aes(x=canopy_change, y=..scaled.., fill=signs_YNf)) +
    geom_density(alpha=1, lwd=0.1) +
    scale_y_sqrt()+
    facet_wrap(~LoD_method)+
    scale_fill_manual("Foraging Observed", values=c('#76C4AE','#E79E67'), breaks=c('No', 'Yes')) +
    labs(x='Canopy Height Change (m)', y='Density')
}

change_df %>%
  filter(time_step == 'Sep17 - Sep18') %>%
  can_change_density(.) %>%
  ggsave('Plots/DoD_density_Sep17_Sep18.png', width=6, height=6,.)

change_df %>%
  filter(time_step == 'Dec16 - Jan18') %>%
  can_change_density(.) %>%
  ggsave('SI/DoD_density_Dec16_Jan18.png', width=6, height=6,.)

# ------ Quantile regression -------------------

# load functions for fitting, generating summary and predicting Quantile regressions

source('Quantile_functions.R')


Quantile_df <-   change_df %>%
  ## This chunk is no longer needed with spatial regression.
  ## add random noise to zero values in 'threshold' method to allow std err calculation. 
  # mutate(canopy_change = ifelse(LoD_method == 'LoDmin threshold' & canopy_change == 0,
  #                               runif(length(canopy_change[LoD_method == 'LoDmin threshold' & canopy_change == 0]),
  #                                     -0.00001, 0.00001),  canopy_change)) %>%
  mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) 

# split dataframe for the two time steps
Sep17Sep18_Quan_df <- Quantile_df %>% filter(time_step == 'Sep17 - Sep18')
Dec16Jan18_Quan_df <- Quantile_df %>% filter(time_step == 'Dec16 - Jan18')

# Fit regression models
Qreg <- function(.data, tlist=c(0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99),.enum=200,
                 iter=200){
  .data %>%
  group_by(LoD_method) %>%
    group_map(., ~spatial_Qreg(., .tau=tlist, enum = .enum, iter=iter), .keep=T)
    # group_map(., ~run_Qreg(., .tau=tlist), .keep=T)
  
}  

Sep17Sep18_Qreg <- Qreg(Sep17Sep18_Quan_df, iter=200)
Dec16Jan18_Qreg <- Qreg(Dec16Jan18_Quan_df, iter=200)

# generate model summaries
QR_summ <- function(.QregOut, tit, .filter=F){

  
  df <-.QregOut %>%
    purrr::map(., ~select_summs(.)) %>%
    bind_rows() %>%
    mutate_if(is.numeric, round, 3) %>% 
    # mutate(term = ifelse(term=='(Intercept)', 'Intercept', 'Foraging observed')) %>%
    rename(quantile = tau) %>%
    dplyr::select(`LoD Method`,term, quantile, estimate, conf.low, conf.upper) #std.error , statistic, p.value
  
  if (.filter == TRUE){
    df <- df %>%
      filter(quantile %in% c(0.05, 0.5, 0.95)) #%>%
      # dplyr::select(-c(std.error, p.value, statistic))
  }
  
  df %>%
    group_by(`LoD Method`) %>%
    gt()%>%
    tab_header(title = md(sprintf('**<div style="text-align: left"> %s </div>**', tit))) %>%
    tab_style(style = cell_fill('grey99'), locations = cells_title()) %>%
    tab_style(style = list(cell_fill('grey95'), cell_text(weight = "bold")), 
              locations = cells_column_labels(colnames(df)[!colnames(df)%in%c('LoD_method')])) %>%
    tab_style(style = list(cell_fill('grey98'), cell_text(weight = "bold")), locations = cells_row_groups())
  }


QR_summ(Sep17Sep18_Qreg, 'Qantile Regression Summary', .filter = T) %>%
  gtsave(., file.path(here(), "Plots","Sep17Sep18QuantRegTabMinimal.html"))

QR_summ(Sep17Sep18_Qreg, 'Qantile Regression Summary (Sep17-Sep18)') %>%
  gtsave(., file.path(here(), "SI","Sep17Sep18QuantRegTable.html"))

QR_summ(Dec16Jan18_Qreg, 'Qantile Regression Summary (Dec16-Jan18)')%>%
  gtsave(., file.path(here(), "SI","Dec16Jan18QuantRegTable.html"))

# generate model predictions
QR_preds <- function(.QregOut){
  .QregOut %>%
    purrr::map(., ~select_preds(.)) %>%
    bind_rows() %>%
    mutate(zone = fct_relevel(zone, "No Foraging", "Foraging Observed")) %>%
    mutate(signs_YN = ifelse(zone == "No Foraging", 0, 1)) %>%
    mutate(signs_YNf = ifelse(zone == "No Foraging", 'No', 'Yes'))
  }

Sep17Sep18_QR_preds <- QR_preds(Sep17Sep18_Qreg)
Dec16Jan18_QR_preds <- QR_preds(Dec16Jan18_Qreg)



# ---------- Quantile regression plot --------------

brew_cols <- brewer.pal(7, "Dark2")

Qreg_plot <- function(.all_data, .predicted, limits){
  .all_data %>%
    mutate(signs_YNf = ifelse(signs_YNf == 'No Foraging', 'No', 'Yes')) %>%
    ggplot(., aes(x=signs_YNf, y=canopy_change)) +
    geom_jitter(colour="grey60", alpha=0.1, width = 0.4, height = 0) +
    # geom_errorbar(data=QR_preds, aes(y=.fitted, ymin = .lower , ymax = .upper,
    #                                  colour=as.factor(.tau)), size = 0.8) +
    geom_crossbar(data=.predicted, aes(y=estimate, ymin = conf.low , ymax = conf.upper,
                                     colour=as.factor(tau), fill=as.factor(tau)), size = 0.8, width=0.82) +
    coord_cartesian(ylim = limits) +
    facet_wrap(~`LoD Method`)+
    scale_colour_manual(name='Quantile', values= alpha(brew_cols,1)) +
    scale_fill_manual(name='Quantile', values= alpha(brew_cols,1)) +
    labs(x='Foraging Observed', y= 'Canopy Height Change (m)') #+
    # theme(axis.text.x = element_text(size=8))
}

 
Quant_change_Sep17Sep18 <- Qreg_plot(Sep17Sep18_Quan_df, Sep17Sep18_QR_preds, c(-4, 3)) %>%
 ggsave('Plots/Quantile_Change_Sep17_Sep18.png', width = 6, height=6,.)

Quant_change_Dec16Jan18 <- Qreg_plot(Dec16Jan18_Quan_df, Dec16Jan18_QR_preds, c(-5, 4)) %>%
  ggsave('SI/Quantile_Change_Dec16Jan18.png', width = 6, height=6,.)
