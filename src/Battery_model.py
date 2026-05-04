import pandas as pd


#preprocessing

solar_power = pd.read_csv('solar_data.csv')
solar_power['utc_time'] = pd.to_datetime(solar_power['utc_time'])


load = pd.read_csv('load_data.csv', sep=';')
load['Time'] = pd.to_datetime(load['Time'])
load = load.rename(columns={'Sum [kWh]' : 'sum'})


combined_data = pd.merge(load, solar_power, left_on='Time', right_on='utc_time', how='inner')
combined_data = combined_data.drop(columns=['Electricity.Timestep','utc_time'])




#battery parameters

capacity = 8                      #kWh                   
max_charge_rate = 8               #kW
max_discharge_rate = 8            #kW
round_trip_efficiency = 0.97    
initial_state_of_charge = 0.5 * capacity
min_state_of_charge = 0.1 * capacity
max_state_of_charge = 0.95 * capacity



#setting up energy flows

state_of_charge = initial_state_of_charge
state_of_charge_series = [ ]
charge_series = [ ]
discharge_series = [ ]
grid_import = [ ] 
grid_export = [ ]
time_step = 1



#loop over all timesteps
for t in range (len(combined_data)):
    pv = combined_data['pv_power'].iloc[t]
    demand = combined_data['sum'].iloc[t]

    net = pv - demand


#charging logic

    if net > 0:                                                                                  
        charge =min(net, max_charge_rate,
                    (max_state_of_charge - state_of_charge) / (round_trip_efficiency * time_step))
        state_of_charge +=charge * round_trip_efficiency * time_step
        export = net - charge
        import_grid = 0
        discharge = 0


#discharging logic
    else:
        needed = abs(net)
        discharge = min(needed, max_discharge_rate, 
                        (state_of_charge - min_state_of_charge) * (round_trip_efficiency / time_step))
        state_of_charge -= (discharge / round_trip_efficiency) * time_step
        import_grid = needed - discharge
        export = 0
        charge = 0

    state_of_charge_series.append(state_of_charge)
    charge_series.append(charge)
    discharge_series.append(discharge)
    grid_import.append(import_grid) 
    grid_export.append(export)


#store the results

combined_data['state_of_charge_kWh'] = pd.Series (state_of_charge_series, index=combined_data.index)
combined_data['charge_kW'] = pd.Series (charge_series, index=combined_data.index)
combined_data['discharge_kW'] = pd.Series (discharge_series, index=combined_data.index)
combined_data['imported_kW'] = pd.Series (grid_import, index=combined_data.index)
combined_data['exported_kW'] = pd.Series (grid_export, index=combined_data.index)


combined_data.to_csv('hourly_energy_balance.csv', index=True)


