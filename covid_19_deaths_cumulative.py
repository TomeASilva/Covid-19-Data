import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from color_pallete import colors
from default_country import traces_visible
import plotly
from datetime import date
today = date.today().strftime("%B %d, %Y")


df = pd.read_excel('https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide.xlsx')

pivot_deaths = df.pivot_table(index="dateRep", columns="countriesAndTerritories", values="deaths")
pivot_cases= df.pivot_table(index="dateRep", columns="countriesAndTerritories", values="cases")

country_list = pivot_cases.columns.tolist()
country_desease_evo_dict = {}
for country in country_list:
    
    country_data = pivot_deaths[country].to_numpy()
    
    #remove nan data
    country_deaths = country_data[np.logical_not(np.isnan(country_data))]

    #Filter data so that we have a series concerned only when disease started to grow 
    #Consistently
    country_deaths_rectified = []
    number_of_deaths_treshold = 2
    for element in country_deaths:
        if element >= number_of_deaths_treshold:
            country_deaths_rectified.append(element)
            number_of_deaths_treshold = 0

    #compute the cumulative number of cases
    country_total_number_deaths = []
    
    for i in range(len(country_deaths_rectified)):
        if i == 0:
            country_total_number_deaths.append(country_deaths_rectified[i])
        else:
            country_total_number_deaths.append(country_deaths_rectified[i] + country_total_number_deaths[i -1])
                
    # Stack country information in array
    country_data = np.stack((country_total_number_deaths, country_deaths_rectified), axis=1)
    country_desease_evo_dict[country] = country_data
    

    


fig = go.Figure()
color = 0 
for country, data in country_desease_evo_dict.items():
    x = np.arange(0 , data.shape[0] + 1)
    if country in traces_visible:
        visible = True
    else: visible = "legendonly" 
    
    fig.add_trace(go.Scatter(x=x, y=data[:, 0],  mode='lines', name=country, visible=visible, line={"color":colors[color]}))
    color += 1
    
fig.update_layout(yaxis_type="log",
                  title=f"Evolution of cumulative deaths - {today}",
                  yaxis_title="log number of deaths",
                  xaxis_title="Number of days from the start of epidemy in each country",
                  )
    
plotly.offline.plot(fig, filename = 'cumulative_death.html', auto_open=False)