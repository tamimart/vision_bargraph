library(dplyr)
library(readxl)
library(skimr)
library(stringr)

df <- readxl::read_excel("table200pub_content_path.xlsx")

df_tipos <- df |> mutate(tipo_dado = case_when(
  str_detect(source, "Figure") & str_detect(figure, "outroplot") ~ "outro",
  str_detect(source, "Figure") & !str_detect(figure, "outroplot") ~ "barplot",
  str_detect(source, "Table") ~ "Table",
  str_detect(source, "Text") ~ "Text"
)) |> select(tipo_dado) |> summarise(n = n(), .by = tipo_dado) 

df |> skimr::skim()
