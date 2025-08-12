library(tidyverse)

# Read your CSV
data <- read_csv("data/interim/wegmans_multi_prices.csv")

# Clean and separate Price and Size/Unit, plus extract price-per-unit info
data <- data %>%
  mutate(
    Price_clean = str_remove(Price, "Price is:") %>% str_trim(),
    Price_value = parse_number(Price_clean),
    Price_unit = str_extract(Price_clean, "(?<=\\d)\\s?/[a-zA-Z]+") %>%
                  str_remove_all("\\s|/"),
    
    Size_clean  = str_remove_all(`Size/Unit`, "[\\(\\)]"),  
    Size_value  = parse_number(Size_clean),
    Size_unit   = str_extract(Size_clean, "[a-zA-Z]+"),
    
    Rating      = as.numeric(Rating),
    Reviews     = as.integer(Reviews),

    # 1️⃣ Extract text inside parentheses → "$0.53/lb." etc.
    Price_per_unit_raw = str_extract(`Size/Unit`, "\\([^\\)]*\\)") %>%
                         str_remove_all("[\\(\\)]") %>%
                         str_trim(),

    # 2️⃣ Extract numeric price from that
    Price_per_unit_value = parse_number(Price_per_unit_raw),

    # 3️⃣ Extract unit (text after the slash)
    Price_per_unit_unit = str_extract(Price_per_unit_raw, "(?<=/)[a-zA-Z\\.]+")
  ) %>%
  # Remove unwanted columns from final dataset 
  select(-`Category URL`, -Rating, -Reviews, -Price_clean, -Price_value, -Price_unit, -Size_clean, -Price, -`Size/Unit`, -Size_value, -Size_unit)

# Save cleaned data
write_csv(data, "data/completed/wegmans_prices_clean.csv")
print("Completed")
