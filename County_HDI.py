# Perform imports.
import pandas as pd
import plotly.graph_objects as go
import plotly
from urllib.request import urlopen
import json
import numpy as np
import zipfile

# Unzip large files for Tract Income.
with zipfile.ZipFile('US_A-Ne_Tract_Income.csv.zip','r') as zf1:
    zf1.extractall()

with zipfile.ZipFile('US_No-W_Tract_Income.csv.zip','r') as zf2:
    zf2.extractall()

# Import tables for life expectancy and educational attainment, then concatenate educational attainment table.
us_life = pd.read_csv('2015_County_Life_Expectancy.csv')
us_edu1 = pd.read_csv('US_A-Ne_Edu.csv',encoding = "ISO-8859-1")
us_edu2 = pd.read_csv('US_No-W_Edu.csv',low_memory=False)
us_edu = pd.concat([us_edu1, us_edu2], axis=0)

# Import education codes for different educational categories. Set index as county FIPS.
county_edu_labels = pd.read_csv('County_Education_Codes.csv')
county_edu_labels.set_index('ID',inplace=True)

# Convert edu columns to usable format, then multiply by assumed number of years for each category.
for col in us_edu.columns[4:]:
    us_edu[col] = us_edu[col].replace('*****', 0).astype('float64').multiply(county_edu_labels.loc[col, 'Years'])
us_edu.dropna(axis=1,inplace=True)

# Add together estimated years of completion for each category and average over population educated.
for col in us_edu.columns:
    us_edu.rename(columns={col:county_edu_labels.loc[col, 'Value']}, inplace=True)
us_edu['Average Years of Education'] = (us_edu['Estimate; Less than high school graduate:'] + 
                                          us_edu['Estimate; High school graduate (includes equivalency):'] + 
                                          us_edu["Estimate; Some college or associate's degree:"] + 
                                           us_edu["Estimate; Bachelor's degree or higher:"]) / us_edu['Estimate; Total:']

# Set edu county and tracts based on id provided. Create index of counties and tracts.
us_edu['County'] = us_edu['Geography'].apply(lambda x: x.split(',')[1])
us_edu['Tract'] = us_edu['Geography'].apply(lambda x: x.split(',')[0].split()[-1])
us_edu.set_index(['County', 'Tract'],inplace=True)
us_edu = us_edu.iloc[:,1:]

# Rename to FIPS codes to compare to other tables. Drop unnecessary column to analysis.
us_edu.rename(columns={'Id2':'FIPS'}, inplace=True)
us_edu.drop(columns='Geography',inplace=True)

# Read in encoded US income data. Concatenate into one table.
us_income1 = pd.read_csv('US_A-Ne_Tract_Income.csv',encoding = "ISO-8859-1")
us_income2 = pd.read_csv('US_No-W_Tract_Income.csv',encoding = "ISO-8859-1")
us_income = pd.concat([us_income1,us_income2], axis=0)

# Determine county and census tract data on income. Set as index. Rename per capita income column. 
us_income['County'] = us_income['GEO.display-label'].apply(lambda x: x.split(',')[1].strip())
us_income['Tract'] = us_income['GEO.display-label'].apply(lambda x: x.split(',')[0].split()[-1].strip())
us_income.set_index(['County', 'Tract'],inplace=True)
us_income.rename(columns={'HC02_EST_VC20':'Per Capita Income'},inplace=True)

# Set index as per capita income and merge edu and income on FIPS code.
us_per_capita = us_income.reset_index().set_index('GEO.id2')['Per Capita Income']
us_edu_income = pd.merge(left=us_edu,right=us_per_capita,
                         left_on=us_edu['FIPS'],right_on=us_per_capita.index)

# Merge with life expectancy table on FIPS code. Select codes pertainent to HDI calculation.
us_all = pd.merge(left=us_edu_income,right=us_life,left_on='FIPS',right_on='Tract ID')
us_all = us_all[['Estimate; Total:','FIPS','Average Years of Education','Per Capita Income','e(0)']]

# Read in FIPS codes, and extend if necessary to include '0' at beginning. Set codes index.
FIPS_codes = pd.read_csv('FIPS.csv')
def fix_fips(fip):
    """Extend FIPS code to include leading zeros."""
    fip = str(fip)
    while len(fip) < 5:
        fip = '0{}'.format(fip)
    return fip
FIPS_codes['fips'] = FIPS_codes['fips'].apply(fix_fips)
FIPS_codes.set_index('fips',inplace=True)

def full_fips_fix(fips):
    """Extend full FIPS codes, similar to fix_fips function."""
    fips = str(fips)
    while len(fips) < 11:
        fips = '0{}'.format(fips)
    return fips

# Fix full FIPS codes, change fips to county, state names. Single out tract id's.
us_all['FIPS'] = us_all['FIPS'].apply(full_fips_fix)
us_all['County'] = us_all['FIPS'].apply(lambda x: str(FIPS_codes.loc[x[:5],'county_name']).strip())
us_all['Tract'] = us_all['FIPS'].apply(lambda x: x[5:])
us_all.set_index(['County', 'Tract'],inplace=True)

# Rename columns to reflect components of HDI. Convert per capita income to integer value.
us_all.rename(columns={'Estimate; Total:': 'Population','e(0)':'Life Expectancy'},inplace=True)
us_all['Per Capita Income'] = us_all['Per Capita Income'].apply(lambda x: int(x))

# Create three indices to HDI based on UN calculation guidance.
us_all['Health Index'] = us_all['Life Expectancy'].apply(lambda x: (x - 20) / 65)
us_all['Education Index'] = us_all['Average Years of Education'].apply(lambda x: (x / 18 + x / 15) / 2)
us_all['Income Index'] = us_all['Per Capita Income'].apply(lambda x: (np.log(x) - np.log(100)) / 
                                                                 (np.log(75000) - np.log(100)))

# Generate HDI using geometric mean of indices. Set FIPS to string.
us_all['HDI'] = (us_all['Health Index'] * us_all['Education Index'] * us_all['Income Index']) ** (1/3)
us_all['FIPS'] = us_all['FIPS'].astype('str')
us_counties = us_all.copy()

# Set county FIPS to only include state and county, not tract. Multiply HDI by tract population.
us_counties['FIPS'] = us_counties['FIPS'].apply(lambda x: x[:5])
us_counties['HDI * Population'] = us_counties['HDI'] * us_counties['Population']

# Group result by county. This gives weigted estimate of HDI by county, weighting by population.
us_counties_state = us_counties.reset_index().set_index(['FIPS', 'Tract']).groupby(level=0).sum()

# Create dictionary of US FIPS codes. Determine county based on FIPS dictionary.
us_fips = dict(us_counties.reset_index().set_index(['FIPS','County']).index)
us_counties_state['County'] = [us_fips[x] for x in us_counties_state.index]

# Average weighted HDI by population to get average HDI.
us_counties_state['HDI'] = us_counties_state['HDI * Population'] / us_counties_state['Population']

# Import county json for mapping.
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
    
# Create Mapbox figure using data as well as json. Set colorbar for HDI.
fig3 = go.Figure(go.Choroplethmapbox(geojson=counties, locations=us_counties_state.index, 
                                    z=us_counties_state.HDI, 
                                    colorscale="Viridis", marker_line_width=0, 
                                    text=us_counties_state['County'],
                                   colorbar={'title':'HDI'}, marker_opacity=0.5))

# Adjust center of map and style, as well as margins.
fig3.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Save plot as html file.
plotly.offline.plot(fig3,filename='US_All_County_HDI.html')