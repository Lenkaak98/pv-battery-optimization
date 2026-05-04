import pandas as pd
import pulp


#Load data, contains pv and battery model

data_file = pd.read_csv ('hourly_energy_balance.csv')
T = range(len(data_file))

solar_list = data_file['pv_power'].tolist()
load_list = data_file ['sum'].tolist()
buy_price = 0.33 
sell_price = 0.08



#define the constants

capacity = 8                                 #kWh
max_charge_rate = 8                          #kW
max_discharge_rate = 8                       #kW
round_trip_efficiency = 0.97   
initial_state_of_charge = 0.5 * capacity 
min_state_of_charge = 0.1 * capacity
max_state_of_charge = 0.95 * capacity


#initialize the model
model = pulp.LpProblem('Energy_optimization', pulp.LpMinimize)


#decision variables
power_charging = pulp.LpVariable.dicts('p_charging', T, lowBound=0)
power_discharging = pulp.LpVariable.dicts('p_discharging', T, lowBound=0)
export_grid = pulp.LpVariable.dicts('grid_out', T, lowBound=0)
import_grid = pulp.LpVariable.dicts('grid_in', T, lowBound=0)
state_of_charge = pulp.LpVariable.dicts('soc', T, lowBound=min_state_of_charge, upBound=max_state_of_charge)
delta = pulp.LpVariable.dicts('Delta', T, cat='Binary')


#objective function
model += pulp.lpSum(import_grid[t] * buy_price - export_grid[t] * sell_price for t in T)


#constraints

for t in T:
    model += solar_list[t] + power_discharging[t] + import_grid[t] == load_list[t] + power_charging[t] + export_grid[t]        #Energy balance
    model += power_charging[t] <= max_charge_rate * delta[t]                                                                   #Binary 
    model += power_discharging[t] <= max_discharge_rate * (1 - delta[t])

    if t == 0:
      model += state_of_charge[t]==initial_state_of_charge + (round_trip_efficiency*power_charging[t])-(power_discharging[t]/round_trip_efficiency)
    
    else:  
      model += state_of_charge[t]==state_of_charge[t-1] + (round_trip_efficiency*power_charging[t])-(power_discharging[t]/round_trip_efficiency)


model += state_of_charge[len(T)-1] == initial_state_of_charge                                                                  #cyclic constraint




#results

model.solve(pulp.PULP_CBC_CMD(msg=1))
if pulp.LpStatus[model.status] == 'Optimal':
    total_cost = pulp.value(model.objective)
    print (f'cost:{total_cost:.2f}')                                   #display the value of the minimized cost

    data_file['optimized_charging_kW'] = [power_charging[t].varValue for t in T]
    data_file['optimized_discharging_kW'] = [power_discharging[t].varValue for t in T]
    data_file['optimized_state_of_charge_kWh'] = [state_of_charge[t].varValue for t in T]

else:
    print (f'failed: {pulp.LpStatus[model.status]}')


data_file.to_csv('optimized_battery_dispatch.csv', index=False)

