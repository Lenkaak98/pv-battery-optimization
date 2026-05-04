import pvlib
import pandas as pd
from pvlib.location import Location


#Coordinates
location = Location(
    latitude=51.4818,
    longitude=7.2162,
    tz='Europe/Berlin',
    altitude=100,
    name='Bochum'
)


#system parameters

pdc0 = 8000                         #system capacity, W
gamma_pdc = -0.004                  #temperature co-efficient
eta_inv_nom = 0.97                  #inverter efficiency
tilt = 30
azimuth = 180


#weather data

weather = pvlib.iotools.get_pvgis_tmy(location.latitude,location.longitude)[0]
weather.index.name = 'utc_time'
weather.index = weather.index.tz_convert(location.tz).tz_localize(None)
weather.index = weather.index.map(lambda t: t.replace (year=2021))


#sun position, total & actual irradiance

times = weather.index
solpos = location.get_solarposition(times)
total_irradiance = pvlib.irradiance.get_total_irradiance(
    surface_tilt=tilt,
    surface_azimuth=azimuth,
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    dni=weather['dni'],
    ghi=weather['ghi'],
    dhi=weather['dhi']
)
irradiance = total_irradiance['poa_global']
temp = weather['temp_air']


#dc & ac power

dc = pdc0 * (irradiance/1000)*(1 + gamma_pdc*(temp-25))
ac = dc * eta_inv_nom
weather['pv_power'] = ac.clip(upper=8000) / 1000

weather.to_csv('solar_data.csv', index=True)




