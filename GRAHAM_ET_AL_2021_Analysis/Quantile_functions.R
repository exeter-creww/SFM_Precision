
select_summs <- function(.data, .name){
  .data$.summ
}
select_preds <- function(.data, .name){
  .data$.pred
}

run_Qreg <- function(.data, .tau_list){
  .method <- .data$LoD_method[1]
  newdat <- tibble(signs_YNf = c("No Foraging", "Foraging Observed"))
  
  QR_single_tau <- function(.df, .tau){
    .mod <- quantreg::rq(canopy_change~signs_YNf, tau= .tau, data=.df, method='fn') 
    
    tidied <- .mod %>%
      tidy(., conf.int=TRUE) %>%
      mutate(LoD_method = .method)
    
    augmented <- .mod %>%
      broom::augment(., newdata=newdat, interval='confidence') %>%
      mutate(LoD_method = .method)
    
    return(list(.summ = tidied, .pred = augmented))
  }
  
  QR_outs <- .tau_list %>%
    purrr::map(., ~ QR_single_tau(.data, .))
  
  QR_summ <- QR_outs %>%
    purrr::map(., ~select_summs(.)) %>%
    bind_rows()
  
  QR_preds <- QR_outs %>%
    purrr::map(., ~select_preds(.)) %>%
    bind_rows()
  
  return(list(.summ = QR_summ, .pred = QR_preds))
  
}