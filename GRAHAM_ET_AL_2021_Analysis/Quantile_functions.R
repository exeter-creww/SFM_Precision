
select_summs <- function(.data, .name){
  .data$.summ
}
select_preds <- function(.data, .name){
  .data$.pred
}


spatial_Qreg <- function(.df, .tau, enum=200, iter=200, model='exp'){
  .method <- .df$LoD_method[1]
  
  .df <- .df %>%
    group_by(signs_YNf) %>% 
    group_split() %>%
    map(., ~as.data.frame(.x))
  
  .zones <- c(.df[[1]]$signs_YNf[1], .df[[2]]$signs_YNf[1])
  
  zone_quant <- function(zone.df){
    y <- zone.df[, "canopy_change"]
    .coords <- zone.df[,c("x","y")]
    meig <- meigen_f(coords=.coords, model = model, enum=enum)
    resf_qr(y=y,x=NULL,meig=meig, tau=.tau, boot=TRUE, iter=iter)
  }
  
  zone.models <- .df %>%
    purrr::map(., ~zone_quant(.x))
  
  tau.df <- function(.model, .znames){
    make.df <- function(.tab, .nam){
      as_tibble(.tab) %>%
        mutate(tau = .nam,
               zone= .znames)
    }
    tau_names <- names(zone.models[[1]]$B) %>%
      map(., ~as.numeric(gsub("[^0-9.]", "",  .x)))
    purrr::map2(.x=.model$B, .y=tau_names, ~ make.df(.x, .y)) %>%
      unname()
  }
  
  stat_tab <- function(.df){
    stat_tau <- function(.g){
      .g_coefs <- dplyr::select(.g, estimate, conf.low, conf.upper)
      new.row <- .g_coefs[2,] - .g_coefs[1,]
      as.vector(new.row)
      
      .g %>%
        mutate(estimate = case_when(zone =='Foraging Observed' ~ new.row$estimate,
                                    TRUE ~ estimate),
               conf.low = case_when(zone =='Foraging Observed' ~ new.row$conf.low,
                                    TRUE ~ conf.low),
               conf.upper = case_when(zone =='Foraging Observed' ~ new.row$conf.upper,
                                      TRUE ~ conf.upper),
               term = case_when(as.character(zone) =='No Foraging' ~ 'Intercept',
                                TRUE ~ as.character(zone))
               )
      
    }
    
    new_coefs <- .df %>%
      group_by(tau) %>%
      group_map(., ~stat_tau(.x), .keep=T) %>%
      bind_rows()
    return(new_coefs)
  }
  
  preds <- purrr::map2(.x=zone.models, .y=.zones , ~tau.df(.x, .y)) %>%
    bind_rows() %>%
    arrange(., tau, zone) %>%
    rename(estimate = Estimates,
           conf.low = CI_lower,
           conf.upper = CI_upper) %>%
    dplyr::select(-c(p_value)) %>%
    mutate(`LoD Method` = .method)
  
  summs <- stat_tab(preds) %>%
    relocate(term, tau, estimate) %>%
    mutate(`LoD Method` = .method)
    
  return(list(.summ = summs, .pred = preds))
}


run_Qreg <- function(.data, .tau_list){
  .method <- .data$LoD_method[1]
  newdat <- tibble(signs_YNf = c("No Foraging", "Foraging Observed"))
  
  QR_single_tau <- function(.df, .tau){
    .mod <- quantreg::rq(canopy_change~signs_YNf, tau= .tau, data=.df, method='fn')
    
    
    tidied <- .mod %>%
      tidy(., conf.int=TRUE) %>%
      mutate(`LoD Method` = .method)
    
    augmented <- .mod %>%
      broom::augment(., newdata=newdat, interval='confidence') %>%
      mutate(`LoD Method` = .method)
    
    return(list(.summ = tidied, .pred = augmented))
  }
  
  QR_outs <- .tau_list %>%
    purrr::map(., ~ QR_single_tau(.data, .))
  
  QR_summ <- QR_outs %>%
    purrr::map(., ~select_summs(.)) %>%
    bind_rows() %>%
    rename(conf.upper=conf.high,
           .tau = tau) 
  
  QR_preds <- QR_outs %>%
    purrr::map(., ~select_preds(.)) %>%
    bind_rows() %>%
    rename(conf.upper=conf.high,
           .tau = tau)
  
  return(list(.summ = QR_summ, .pred = QR_preds))
  
}