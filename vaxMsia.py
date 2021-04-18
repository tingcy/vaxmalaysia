import streamlit as st
import numpy as np
import pandas as pd 
import altair as alt
from scipy.integrate import odeint
import plotly.express as px
import calendar

st.set_page_config(layout="wide")

# Differential Function -----------------------------

def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

# Declaration for the Simulation ----------------------

# Total population, N.
N = 25000000
# Initial number of infected and recovered individuals, I0 and R0.
I0, R0 = 1, 0
# Everyone else, S0, is susceptible to infection initially.
S0 = N - I0 - R0
# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
beta, gamma = 0.10, 1./22 
# A grid of time points (in days)
t_max = 700
dt = 1
t = np.linspace(0, t_max, t_max + 1)

# Initial conditions vector
y0 = S0, I0, R0
# Integrate the SIR equations over the time grid, t.
ret = odeint(deriv, y0, t, args=(N, beta, gamma))
S, I, R = ret.T


# Generating the DataFrame -------------------------------

results = pd.DataFrame({'Eligible for Vaccination': S, 'Ignore': I, 'Registered for Vaccination': R} )
results['Day'] = 1 + results.index
results['Date']=pd.date_range(start='6/3/2020', periods= t_max+ 1)

st.image('asm.png')
st.title('Malaysia Vaccine Supply and Demand') 
PrecAlloc = int(st.selectbox(
    'The Percentage of 1st Dose Allocation?',
    ('50', '60', '70', '80','90','100')))/100



data_file = st.file_uploader("Upload CSV", type=['xlsx'])
if data_file is not None:
    
    # Pfizer
    dose_pfizer = pd.read_excel(data_file, sheet_name='Pfizer')
    dose_pfizer.Date = pd.to_datetime(dose_pfizer.Date) 

    # Sinovac
    dose_sinovac = pd.read_excel(data_file, sheet_name='Sinovac')
    dose_sinovac.Date = pd.to_datetime(dose_sinovac.Date) 

    # Cansino
    dose_cansino = pd.read_excel(data_file, sheet_name='Cansino')
    dose_cansino.Date = pd.to_datetime(dose_cansino.Date) 

    # AZ
    dose_AZ = pd.read_excel(data_file, sheet_name='AZ')
    dose_AZ.Date = pd.to_datetime(dose_AZ.Date) 

    # Sputnik
    dose_Sputnik = pd.read_excel(data_file, sheet_name='Sputnik')
    dose_Sputnik.Date = pd.to_datetime(dose_Sputnik.Date) 

    # Covax
    dose_Covax = pd.read_excel(data_file, sheet_name='Covax')
    dose_Covax.Date = pd.to_datetime(dose_Covax.Date) 

    results = pd.merge(results, dose_pfizer, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'Pfizer'})

    results = pd.merge(results, dose_sinovac, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'Sinovac'})

    results = pd.merge(results, dose_cansino, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'Cansino'})

    results = pd.merge(results, dose_AZ, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'AZ'})

    results = pd.merge(results, dose_Sputnik, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'Sputnik'})


    results = pd.merge(results, dose_Covax, how="left", on=["Date"])
    results = results.fillna(0) 
    results = results.rename(columns = {'Dose': 'Covax'})

    results['Pfizer Cummulative']=results.Pfizer.cumsum()
    results['Sinovac Cummulative']=results.Sinovac.cumsum()
    results['Cansino Cummulative']=results.Cansino.cumsum()
    results['AZ Cummulative']=results.AZ.cumsum()
    results['Sputnik Cummulative']=results.Sputnik.cumsum()
    results['Covax Cummulative']=results.Covax.cumsum()

    results_raw = results[['Date','Pfizer','Sinovac','Cansino','AZ','Sputnik','Covax']]
    results = results[['Date', 'Eligible for Vaccination', 'Registered for Vaccination', 'Pfizer Cummulative', 'Sinovac Cummulative', 'Cansino Cummulative', 'AZ Cummulative', 'Sputnik Cummulative']]

    results['Total Vaccine'] = results['Pfizer Cummulative'] + results['Sinovac Cummulative'] + results['Cansino Cummulative'] + results['AZ Cummulative'] + results['Sputnik Cummulative']
    results = results[(results.Date>'2020-12-15') & (results.Date<'2022-01-01')]


    def allocation1stdose(a, b, c):
        if a < b:
            return (a*c)
        else:
            return (b*c)
    
    def allocation2nddose(a, b, c):
        if a < b:
            return (a*c)
        else:
            return (b*c)

    results['Allocation for 1st Dose'] = results.apply(lambda row : allocation1stdose(row['Total Vaccine'], row['Registered for Vaccination'], PrecAlloc), axis = 1)
    results['Allocation for 2nd Dose'] = results.apply(lambda row : allocation2nddose(row['Total Vaccine'], row['Registered for Vaccination'], 1-PrecAlloc), axis = 1)
    #results['Allocation for 2nd Dose'] = results['Total Vaccine'] - results['Allocation for 1st Dose']

    results_raw['Allocation for 1st Dose'] = results['Allocation for 1st Dose']
    results_raw['Allocation for 2nd Dose'] = results['Allocation for 2nd Dose']

    results_raw['month'] = pd.DatetimeIndex(results_raw['Date']).month
    results_raw['month'] = results_raw['month'].apply(lambda x: calendar.month_abbr[x])    

    st.dataframe(results)

    results_raw_long = pd.melt(results_raw[['month','Pfizer','Sinovac','Cansino','AZ','Sputnik','Covax']], id_vars=['month'], value_vars=['Pfizer','Sinovac','Cansino','AZ','Sputnik','Covax'])
    results = pd.melt(results, id_vars=['Date'], value_vars=['Eligible for Vaccination', 'Registered for Vaccination','Pfizer Cummulative', 'Sinovac Cummulative', 'Cansino Cummulative', 'AZ Cummulative', 'Sputnik Cummulative', 'Total Vaccine', 'Allocation for 1st Dose', 'Allocation for 2nd Dose'])   
     

    # Plotly Express chart - monthly supply

    results_raw_long=results_raw_long.groupby(by=["month","variable"]).sum().reset_index()

    fig = px.bar(results_raw_long, x="month", color="variable",
                y='value',
                title="Monthly Vaccine Supply",  
                barmode='stack',
                height=600,
                category_orders={"month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]},            
                )

    fig.update_layout(title = "Monthly Vaccine Supply for Malaysia",
        xaxis_title = 'Month', yaxis_title = 'Vaccine Count', title_x=0.5, template="none",
        width = 1000, height = 600)

    st.plotly_chart(fig, use_container_width=True)

    # Plotly Express chart - daily estimation and vaccine supply

    filter_list = ['Registered for Vaccination', 'Pfizer Cummulative', 'Sinovac Cummulative', 'Cansino Cummulative', 'Cansino Cummulative', 'Sputnik Cummulative', 'Total Vaccine','Allocation for 1st Dose', 'Allocation for 2nd Dose']
    results = results[results.variable.isin(filter_list)] 
    fig2 = px.line(results, x="Date", y="value", color="variable", title='Malaysia: Forecasted Registration vs. Vaccine Supply', 
            labels=dict(value="Value"), template="none",
            width=1200, height=700)
    
    st.plotly_chart(fig2, use_container_width=True)
