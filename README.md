# US County Human Development Index

This repository was developed to create a Human Development Index (HDI) map of the US by county. Maine and Wisconsin are not included in the map as their data was not available in the database used for life expectancy. Some counties are also excluded from the map.

HDI calculations based on the UNDP training manual for HDI (UNDP 2015). The file is included as `hdi_training.pdf`.

Per capita income used for the income index was obtained using American Fact Finder from the US Census (US Census Per Capita Income 2017). The data for all census tracts in each state was obtained. These csv files were subdivided into two parts, as the data tool could only handle a query of a certain size. These files were then zipped to enable upload. The zipped csv files are `US_A-NE_Tract_Income.csv.zip` and `US_No-W_Tract_Income.csv.zip`. 

Educational attainment was also obtained using American Fact Finder (US Census Educational Attainment 2017). Again, the census tract data was subdivided based on the maximum query size of the tool. The data was subdivided into subjective categories. In order to quantitatively summarize this data, the following assumptions were made: “some high school” equates to 10 years, “high school graduate” equates to 12 years, “some college” equates to 14 years, “bachelor’s degree” equates to 16 years, and “graduate degree” equates to 18 years. These files are `US_A-NE_Edu.csv`, and `US_No-W_Edu.csv`. The codes for columns in the csv files were provided by American Fact Finder and are given in `County_Education_Codes.xlsx`.

Life expectancy per census tract was obtained by a CDC study from the neighborhood life expectancy project (CDC 2018). The file `2015_County_Life_Expectancy.csv` contains this data.

FIPS codes were obtained from a csv file compiled by GitHub user Kieran Healy (Healy 2018). This file is given as `FIPS.xlsx`. Only the "fips" and "county_code" columns were used.

The code used to compile the map is provided in `County_HDI.py`. The resulting HDI map has been created and is provided in `US_All_County_HDI.html`.

## Sources:

 “Training Material for Producing National Human Development Reports”. UNDP. March 2015. http://hdr.undp.org/sites/default/files/hdi_training.pdf.

“Per Capita Income in the Past 12 Months.” US Census. 2017. https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml?pid=ACS_17_5YR_B19301&prodType=table.

“Educational Attainment 2013-2017 American Community Survey”. US Census. 2017. https://factfinder.census.gov/faces/tableservices/jsf/pages/productview.xhtml?pid=ACS_17_5YR_S1501&prodType=table.

“U.S. Small-area Life Expectancy Estimates Project”. CDC. 2018 August 28. https://www.cdc.gov/nchs/nvss/usaleep/usaleep.html#life-expectancy.

“County and State FIPS codes”. Healy, Kieran. 2018 January 1. https://github.com/kjhealy/fips-codes/blob/master/county_fips_master.csv.






