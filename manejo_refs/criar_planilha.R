
library(dplyr)
library(RCurl)
library(XML)
library(stringr)

# importa planilhas
refs <- readxl::read_excel("refs_200.xlsx")
data <- readxl::read_excel("Dataclean_200FST.xlsx")


refs <- refs |> 
  rename(idprints = ID,
         idgeral = IDGeral) |> 
  mutate(idgeral = as.character(idgeral))


planilha <- refs |> 
  inner_join(data, by = "idgeral") |> 
  select(idgeral,
         idprints,
         id, 
         study_reference,
         authors.x,
         title.x,
         year.x,
         language,
         figure,
         source,
         measure_unit,
         ctr_mean:N,
         comparator,
         atd_type,
         dose)

planilha <- planilha |>  select(!id)


# IMPORTAR DADOS ----

# importa arquivo do endnote no formato xml (linguagem de marcação) e gera estrutura equivalente dentro do R
xml_data <- XML::xmlParse("incluidos_geral.xml")

# acha nodos no arquivo xml que atendem ao critério especificado
x <-  getNodeSet(xml_data,'//record')

xpath2 <-function(x, ...){
  y <- xpathSApply(x, ...)
  y <- gsub(",", "", y)  # remove vírgula se usado como separador
  ifelse(length(y) == 0, NA,  paste(y, collapse=", "))
}

endnote_data <- data.frame(
  author = sapply(x, xpath2, ".//contributors/authors", xmlValue),
  auth_address = sapply(x, xpath2, ".//auth-address", xmlValue),
  year   = sapply(x, xpath2, ".//dates/year", xmlValue),
  journal = sapply(x, xpath2, ".//periodical/full-title", xmlValue),
  DOI = sapply(x, xpath2, ".//electronic-resource-num", xmlValue),
  title = sapply(x, xpath2, ".//titles/title", xmlValue),
  pages = sapply(x, xpath2, ".//pages", xmlValue),
  volume = sapply(x, xpath2, ".//volume", xmlValue),
  number = sapply(x, xpath2, ".//number", xmlValue),
  abstract = sapply(x, xpath2, ".//abstract", xmlValue),
  record_id = sapply(x, xpath2, ".//rec-number", xmlValue),
  secondary_title = sapply(x, xpath2, ".//titles/secondary-title", xmlValue),
  pdf_relative_path = sapply(x, xpath2, ".//pdf-urls", xmlValue),
  keywords = sapply(x, xpath2, ".//keywords/keyword", xmlValue))

# editar colunas: 1- se não apresentar nome da revista, colocar o "secondary title", 2- criar variavel com apenas numero da pasta em que o pdf está
endnote_data  <- endnote_data  |> 
  mutate(journal = ifelse(is.na(journal), paste(secondary_title), paste(journal)),
         # pdf_relative_path_id_folder = str_extract_all(pdf_relative_path, "(?<=\\/)(\\d+)(?=\\/)"),
         pdf_relative_path_id_folder = str_extract_all(pdf_relative_path, "(?<=internal-pdf://)(\\d+)"),
         pdf_relative_path_id = str_extract_all(pdf_relative_path, "(?<=internal-pdf://).+")
  )

# deixar apenas o primeiro caminho, para artigo que está em mais de uma pasta
endnote_data$pdf_relative_path_id = sapply(
  endnote_data$pdf_relative_path_id,
  function(x) ifelse(length(x) > 1, x[[1]], x)
)

dados_amostra200 <- planilha |> 
  left_join(endnote_data, by = join_by(idgeral == record_id)) 


dados_amostra200 <- dados_amostra200 |> 
  select(figure:dose,
         idgeral:language,
         journal,
         DOI,
         pages,
         volume,
         number,
         abstract,
         keywords,
         pdf_relative_path,
         pdf_relative_path_id,
         pdf_relative_path_id_folder) 

dados_amostra200 <- dados_amostra200 |> 
  rename(authors = authors.x,
         title = title.x,
         year = year.x)

writexl::write_xlsx(dados_amostra200, "table200pub_content_path.xlsx")

