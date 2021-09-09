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

zones_df <- read_csv('./data/CWC_can_change_df.csv') %>%
  mutate(loss_gain = ifelse(canopy_change <0, "Decrease", ifelse(canopy_change > 0, "Increase", "No change"))) %>%
  mutate(signs_YNf = fct_relevel(signs_YNf, "No Foraging", "Foraging Observed")) %>%
  mutate(LoD_method = ifelse(LoD_method =='weighted', 'LoD95 weighting', 
                             ifelse(LoD_method == 'no lod', 'No LoD',
                                    ifelse(LoD_method == 'threshold', 'LoDmin threshold', NA)))) %>%
  mutate(LoD_method = fct_relevel(LoD_method, 'No LoD', 'LoD95 weighting', 'LoDmin threshold' ))




# -------------- Summarise Data and plot--------------------
Total_Area_per_zone <- zones_df %>%
  drop_na()%>%
  filter(LoD_method == 'No LoD') %>%
  group_by(signs_YNf) %>%
  summarise(Total_Area_m2 = n()/4) %>%
  mutate(Total_Area_ha = Total_Area_m2*0.0001)


Prop_change <- zones_df %>%
  drop_na()%>%
  group_by(LoD_method, time_step, signs_YNf, loss_gain) %>%
  summarise(Area_m2 = n()*0.25) %>%
  ungroup()%>%
  group_by(LoD_method, time_step, signs_YNf) %>%
  mutate(Zone_area_m2 = sum(Area_m2)) %>%
  ungroup() %>%
  mutate(Perc_Area = Area_m2/Zone_area_m2*100) %>%
  mutate(loss_gain = fct_relevel(loss_gain, 'Increase', 'Decrease'))%>%
  mutate(signs_YNf = fct_relevel(signs_YNf, 'No Foraging')) 

Area_change_plot <- function(.data) {
  .data %>%
    mutate(signs_YNf = ifelse(signs_YNf == 'No Foraging', 'No', 'Yes')) %>%
    filter(loss_gain != "No change") %>%
    ggplot(., aes(x=loss_gain, y = Perc_Area, fill = signs_YNf)) +
    geom_bar(width=0.8, stat="identity", position=position_dodge(width=0.9), colour='black', alpha=0.5, lwd=0.1)+
    geom_text(aes(label=paste(round(Area_m2*0.0001, 2), "ha")),position=position_dodge(width=0.95), vjust=-1, size=2.5) +
    facet_wrap(~LoD_method) +
    labs(y=bquote('Area With Elevation Change %'), x= 'Direction of Elevation Change') +
    scale_fill_manual("Foraging Observed", values=c('#1b9e77','#d95f02')) 
  
}

Prop_change %>% 
  filter(time_step == 'Sep17 - Sep18') %>%
  Area_change_plot() %>%
  ggsave('Plots/Area_of_changeSep17_sep18.jpg', dpi=600, width=6, height = 6,.)

Prop_change %>% 
  filter(time_step == 'Dec16 - Jan18') %>%
  Area_change_plot()%>%
  ggsave('SI/Area_of_changeJan16_Dec18.jpg', dpi=600, width=6, height = 6,.)


# --------- Create summary table of areas with gain loss and no change for each group. ------------------- 

make_table <- function(.data){

  .data %>%
    mutate_if(is.numeric, round, 1) %>%
    gt(rowname_col = "loss_gain") %>%
    summary_rows(
      groups = TRUE,
      columns = vars(Area_m2),
      fns = list(total = "sum")) %>%
    tab_style(style = cell_fill('grey80'), locations = cells_title()) %>%
    tab_style(style = cell_fill('grey95'), locations = cells_row_groups()) %>%
    cols_label(
      Area_m2 = md('Area (m<sup>2</sup>)'),
      Perc_Area = md('% Area')) # %>%
    # tab_header(title = md(sprintf('**<div style="text-align: left"> %s </div>**',))) 
}


# Not saving as think this may be unnecessary with the above barplot...

Prop_change%>%
  filter(time_step == 'Sep17 - Sep18') %>%
  select(!c(Zone_area_m2, time_step))%>%
  group_by(LoD_method, signs_YNf) %>%
  make_table() # %>%
  # gtsave(., filename = normalizePath('NewPlots/Areas_Summary.png', mustWork=FALSE))
  # gtsave(., filename = normalizePath('NewPlots/Areas_Summary.html', mustWork=FALSE))

# ------------ Logistic regression ------------------


log_reg <- function(.data){
  lodM <- pull(.data, var = LoD_method)[1]
  
  .mod1 <- tidy(glm(formula = lossTRUE ~ signs_YNf, data = .data, family = binomial(link = "logit")), conf.int=TRUE, exponentiate=TRUE) %>%
    mutate(LoD_method = lodM) %>%
    mutate(loss_gain = 'Decrease')
  
  # message(sprintf("GAIN: Logistic Regression Table for %s", ts ))
  .mod2 <- tidy(glm(formula = gainTRUE ~ signs_YNf, data = .data, family = binomial(link = "logit")), conf.int=TRUE, exponentiate=TRUE)%>%
    mutate(LoD_method = lodM) %>%
    mutate(loss_gain = 'Increase')
  
  comb.tab <- bind_rows(.mod1, .mod2)
  
  return(comb.tab)
  
}

gen_log_reg_summ <- function(.data){
  
  LR_zones_df <- .data %>%
    mutate(signs_YNf = fct_relevel(signs_YNf, 'No Foraging')) %>%
    mutate(lossTRUE = ifelse(canopy_change < 0, 1, 0)) %>%
    mutate(gainTRUE = ifelse(canopy_change > 0, 1, 0)) %>%
    group_by(LoD_method)%>%
    group_split()%>%
    purrr::map(., ~log_reg(.)) %>%
    bind_rows() %>%
    mutate(term = ifelse(term == 'signs_YNfForaging Observed', 'Foraging Observed', term)) 
  
}


LR_zones_df_Sep17Sep18 <- zones_df %>%
  filter(time_step == 'Sep17 - Sep18') %>%
  gen_log_reg_summ()

LR_zones_df_Dec16Jan18 <- zones_df %>%
  filter(time_step == 'Dec16 - Jan18') %>%
  gen_log_reg_summ()


Gen_LogReg_table <- function(.table, tit){
  .table %>%
    mutate(p.value = ifelse(p.value < 0.001, '< 0.001 **', 
                            ifelse(p.value < 0.05, paste(formatC(p.value,format = "f", 3), '*', sep = " "),
                                   ifelse(p.value < 0.1, paste(formatC(p.value,format = "f", 3), '.', sep = " "),
                                          formatC(p.value,format = "f", 3))))) %>%
    mutate_if(is.numeric, round, 2)%>%
    select(LoD_method, loss_gain, term, estimate,conf.low, conf.high, statistic, p.value) %>% 
    group_by(LoD_method, loss_gain) %>%
    gt() %>%
    tab_header(title = md(sprintf('**<div style="text-align: left"> %s </div>**', tit))) %>%
    tab_style(style = cell_fill('grey99'), locations = cells_title()) %>%
    tab_style(style = list(cell_fill('grey95'), cell_text(weight = "bold")), locations = cells_column_labels(c(
      'term', 'estimate', 'statistic','conf.low', 'conf.high', 'p.value'))) %>%
    tab_style(style = list(cell_fill('grey98'), cell_text(weight = "bold")), locations = cells_row_groups())
    
}

Gen_LogReg_table(LR_zones_df_Sep17Sep18, 'Logistic Regression Summary') %>%
  gtsave(., filename = normalizePath('Plots/Sep17Sep18_log_reg_Area.html', mustWork=FALSE))

Gen_LogReg_table(LR_zones_df_Dec16Jan18, 'Logistic Regression Summary: Dec16 - Jan18')%>%
  gtsave(., filename = normalizePath('SI/Dec16Jan18_log_reg_Area.html', mustWork=FALSE))


# ------------ Mean Change Table -------------

mean_summary_tab <- function(.data, tit) {
  .data %>%
    drop_na()%>%
    group_by(LoD_method, time_step, signs_YNf) %>%
    summarise(mean= mean(canopy_change),
                # StdError = sd(canopy_change)/sqrt(n()),
                conf.low = mean(canopy_change) - (1.96 *sd(canopy_change)/sqrt(n())),
                conf.high = mean(canopy_change) + (1.96 *sd(canopy_change)/sqrt(n()))) %>%
    ungroup() %>%
    select(!c(time_step)) %>%
    rename(Zone = signs_YNf) %>%
    mutate_if(is.numeric, round, 3)%>%
    group_by(LoD_method) %>%
    gt() %>%
    tab_header(title = md(sprintf('**<div style="text-align: left"> %s </div>**', tit))) %>%
    tab_style(style = cell_fill('grey99'), locations = cells_title()) %>%
    tab_style(style = list(cell_fill('grey95'), cell_text(weight = "bold")), locations = cells_column_labels(c(
      'Zone', 'mean', 'conf.low', 'conf.high'))) %>%
    tab_style(style = list(cell_fill('grey98'), cell_text(weight = "bold")), locations = cells_row_groups())
}

  
zones_df %>%
  filter(time_step == 'Sep17 - Sep18')%>%
  mean_summary_tab(., tit='Mean Canopy Change (m)') %>%
  gtsave(., filename = normalizePath('Plots/Sep17Sep18_Mean_Change.html', mustWork=FALSE))

zones_df %>%
  filter(time_step == 'Dec16 - Jan18')%>%
  mean_summary_tab(., tit='Mean Canopy Change (m): Dec16 - Jan18') %>%
  gtsave(., filename = normalizePath('SI/Dec16Jan18_Mean_Change.html', mustWork=FALSE))
  
