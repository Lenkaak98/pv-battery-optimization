
import pandas as pd 
import matplotlib.pyplot as plt

data = pd.read_csv('optimized_battery_dispatch.csv')



#Plot 1
# Calculate Baseline (No Battery)
net_load = data['sum'] - data['pv_power']
base_cost = (net_load.clip(lower=0) * 0.33).sum() - (net_load.clip(upper=0).abs() * 0.08).sum()

# Plot Comparison
plt.figure(figsize=(6, 4))
plt.bar(['Without Battery', 'With optimized battery'], [base_cost, 377.58], color=['gray', '#2ecc71'])
plt.title('Annual Electricity Cost (Euros)')
plt.ylabel('Total Cost')
plt.tight_layout()
plt.show()




#Plot 2
#Baseline: No Battery
net_load = data['sum'] - data['pv_power']
import_no_battery = net_load.clip(lower=0).sum()

# With Battery
import_with_battery = data['imported_kW'].sum()

# Bar Chart
plt.figure(figsize=(6, 5))
plt.bar(['Without Battery', 'With Battery'], [import_no_battery, import_with_battery], color=['#95a5a6', '#3498db'])


plt.text(0, import_no_battery, f'{int(import_no_battery)} kWh', ha='center', va='bottom')
plt.text(1, import_with_battery, f'{int(import_with_battery)} kWh', ha='center', va='bottom')

plt.title('Annual_grid_energy_imported')
plt.ylabel('Imported_electricity_kWh')
plt.tight_layout()
plt.show()