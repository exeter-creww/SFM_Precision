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

change_df.test <- change_df %>%
  filter(time_step == 'Sep17 - Sep18',
         LoD_method == 'LoD95 weighting') %>%
  mutate(signs_YN = as.factor(signs_YN)) %>%
  drop_na() %>%
  group_by(signs_YN) %>% group_split() %>%
  map(., ~as.data.frame(.x))
  #st_as_sf(coords=c('x', 'y'))

# plot(st_geometry(st_make_grid(change_df.test, 0.5)))
library(spmoran)
library(tictoc)
tic()
# change values for each factor level
y1 <- change_df.test[[1]][, "canopy_change"]
y2 <- change_df.test[[2]][, "canopy_change"]

#coordinates and approximate Moran eigenvectors for each factor level.
coords1<- change_df.test[[1]][,c("x","y")]
coords2<- change_df.test[[2]][,c("x","y")]
meig1 <- meigen_f(coords=coords1)
meig2 <- meigen_f(coords=coords2)

# Run the models 
resL1 <- resf_qr(y=y1,x=NULL,meig=meig1, tau <- c(0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99), boot=T)
resL2 <- resf_qr(y=y2,x=NULL,meig=meig2, tau <- c(0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99), boot=T)
resL1
resL2
toc()

quantreg::rq(canopy_change~signs_YNf, tau= c(0.01, 0.05), data=change_df.test, method='fn') 

plot_qr(res,2)

y <- boston.c[, "CMEDV" ]
x <- boston.c[,c("CRIM")]
coords<- boston.c[,c("LON","LAT")]
meig <- meigen(coords=coords)
res <- resf_qr(y=y,x=x,meig=meig, boot=TRUE)


require(spdep)
data(boston)
head(boston.c)
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
    # scale_colour_manual("", values=c('#60C84E', '#AC4EC8')) +
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

# add random noise to zero values in 'threshold' method to allow std err calculation. 
Quantile_df <-   change_df %>%
  mutate(canopy_change = ifelse(LoD_method == 'LoDmin threshold' & canopy_change == 0, 
                                runif(length(canopy_change[LoD_method == 'LoDmin threshold' & canopy_change == 0]), 
                                      -0.00001, 0.00001),  canopy_change)) %>%
  mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) 

# split dataframe for the two time steps
Sep17Sep18_Quan_df <- Quantile_df %>% filter(time_step == 'Sep17 - Sep18')
Dec16Jan18_Quan_df <- Quantile_df %>% filter(time_step == 'Dec16 - Jan18')

# Fit regression models
Qreg <- function(.data, tlist=c(0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99)){
  .data %>%
  group_by(LoD_method) %>%
    group_split() %>%
    purrr::map(., ~run_Qreg(., .tau_list=tlist))
}  

Sep17Sep18_Qreg <- Qreg(Sep17Sep18_Quan_df)
Dec16Jan18_Qreg <- Qreg(Dec16Jan18_Quan_df,
                        tlist=c(0.01, 0.1, 0.5, 0.9, 0.95, 0.99))

# generate model summaries
QR_summ <- function(.QregOut, tit, .filter=F){

  
  df <-.QregOut %>%
    purrr::map(., ~select_summs(.)) %>%
    bind_rows() %>%
    mutate_if(is.numeric, round, 3) %>% 
    mutate(term = ifelse(term=='(Intercept)', 'Intercept', 'Foraging observed')) %>%
    rename(quantile = tau) %>%
    select(LoD_method,term, quantile, estimate, std.error, conf.low, conf.high, statistic, p.value)
  
  if (.filter == TRUE){
    df <- df %>%
      filter(quantile %in% c(0.05, 0.5, 0.95)) %>%
      select(-c(std.error, p.value, statistic))
  }
  
  df %>%
    group_by(LoD_method) %>%
    gt()%>%
    tab_header(title = md(sprintf('**<div style="text-align: left"> %s </div>**', tit))) %>%
    tab_style(style = cell_fill('grey99'), locations = cells_title()) %>%
    tab_style(style = list(cell_fill('grey95'), cell_text(weight = "bold")), 
              locations = cells_column_labels(colnames(df)[!colnames(df)%in%c('LoD_method')])) %>%
    tab_style(style = list(cell_fill('grey98'), cell_text(weight = "bold")), locations = cells_row_groups())
  }


QR_summ(Sep17Sep18_Qreg, 'Qantile Regression Summary', .filter = TRUE) %>%
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
    mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) %>%
    mutate(signs_YN = ifelse(signs_YNf == "No Foraging", 0, 1)) %>%
    mutate(signs_YNf = ifelse(signs_YNf == "No Foraging", 'No', 'Yes'))
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
    geom_crossbar(data=.predicted, aes(y=.fitted, ymin = .lower , ymax = .upper,
                                     colour=as.factor(.tau), fill=as.factor(.tau)), size = 0.8, width=0.82) +
    coord_cartesian(ylim = limits) +
    facet_wrap(~LoD_method)+
    scale_colour_manual(name='Quantile', values= alpha(brew_cols,1)) +
    scale_fill_manual(name='Quantile', values= alpha(brew_cols,1)) +
    labs(x='Foraging Observed', y= 'Canopy Height Change (m)') #+
    # theme(axis.text.x = element_text(size=8))
}

 
Quant_change_Sep17Sep18 <- Qreg_plot(Sep17Sep18_Quan_df, Sep17Sep18_QR_preds, c(-4, 3)) %>%
 ggsave('Plots/Quantile_Change_Sep17_Sep18.png', width = 6, height=6,.)

Quant_change_Dec16Jan18 <- Qreg_plot(Dec16Jan18_Quan_df, Dec16Jan18_QR_preds, c(-5, 4)) %>%
  ggsave('SI/Quantile_Change_Dec16Jan18.png', width = 6, height=6,.)
