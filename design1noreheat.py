# --------------------------------------------------------------------------------------------------------


'''
Names:


Bagalavan Thurai
George D. 
Hamza Hashemi 
Hamzah Chamas 
Mohammad Ali 


Code Title: Rankine Cycle with No Reheats
'''


# --------------------------------------------------------------------------------------------------------


import pyromat as pyro
import numpy as np
import matplotlib.pyplot as plt
import csv


######### SET UP FOR THE CALCULATIONS ###########
steam = pyro.get('mp.H2O')


######### CONSTANTS FOR THE THERMO CYCLE ###########
p1 = 90 # (bar) The operating pressure of the boiler
turbEff = 0.87  # must be decimal | 0 <= turbEff <= 1 |
pumpEff = 0.8  # must be decimal | 0<= pumpEff <= 1 |


tc = 30 + 273.15  # (Kelvin) The cold temperature/temperature of the condenser
p5 = steam.p(T=tc)  # (Bar) The pressure at the condenser


Wnet = 80000  # 80000 kWe required electricity generated
Qout = 25000  # 25000 kWth required heat generated


######### FUNCTION DEFINITIONS ###########


# Calculate the intermediate pressures
def set_pressure_intervals(p1, p5):
    i = (p1 - p5) / 4
    p4 = p5 + i
    p3 = p4 + i
    p2 = p3 + i
    return p4, p3, p2


# Fix superheated state
def superheat(n, pi, ti):
    hn = steam.h(T=ti, p=pi)
    sn = steam.s(T=ti, p=pi)
    # dn = steam.d(T=ti, p=pi)
    # vn = 1/dn
    return hn, sn


def turbine(n, hi, si, pi):
   
    # Calculate hi,s (assuming isentropic conditions)
    hn = steam.h(s=si, p=pi)


    # Calculate hi (assuming non-isentropic conditions)
    hj = hi - turbEff*(hi-hn)
    sj = steam.s(h=hj, p=pi)


    # print(f"State {n}:\nh{n}: {hn}\n")
    return hj, sj


def saturated_liquid(n, type, i):
    if type == "T":
        hn = steam.h(T=i, x=0)
        sn = steam.s(T=i, x=0)
        dn = steam.d(T=i, x=0)
    elif type == "P":
        hn = steam.h(p=i, x=0)
        sn = steam.s(p=i, x=0)
        dn = steam.d(p=i, x=0)
    else:
        print("Invalid type")


    vn = 1 / dn
    return hn, sn, dn, vn


def pump(n, vi, hi, po, pi):
    vn = vi
    hn = hi + vn * (po - pi)
    return hn, vn


######### MAIN CODE ###########
pressurename = f"noreheatpressures_{p1}.csv"
enthalpyname = f"noreheatenthalpies_{p1}.csv"
naturalgas_data = f"noreheatdata_{p1}.csv"
massname = f"noreheatmass_{p1}.csv"


with open(pressurename, mode="w", newline='') as pressure_file, \
    open(enthalpyname, mode="w", newline='') as enthalpy_file, \
    open(naturalgas_data, mode='w', newline='') as naturalgasdata_file, \
    open(massname, mode='w', newline='') as unisentropicMass_file:


    # CSV writer objects to print out values to respective files
    pressure_writer = csv.writer(pressure_file)
    enthalpy_writer = csv.writer(enthalpy_file)
    data_writer = csv.writer(naturalgasdata_file)
    mass_writer = csv.writer(unisentropicMass_file)


    # File headers
    pressure_writer.writerow(['Th', 'P1', 'P2', 'P3', 'P4', 'P5'])
    enthalpy_writer.writerow(['Th'] + [f'h{i}' for i in range(1, 19)])
    mass_writer.writerow(["y'", "y''", "y''"])
    data_writer.writerow([
        'Th', 'P1', 'm.', 'm.cw', 'W_net', 'Q_in', 'Q_out per unit mass', 'Q_out_steam', 'thermal eff',  'BWR', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'h11', 'h12', 'h13', 'h14',
        'h15', 'h16', 'h17', 'h18', "y'", "y''", "y'''"
    ])


    for Th in range(673, 874, 10):  # Starts at 673K (400C), ends at 873 (600C) (inclusive), steps by 5

        ##### Fix the state at the boiler outlet (State 1) - Superheated value
        h1, s1 = superheat(1, p1, Th)
        s5 = s1
        p5 = steam.p(T=tc, s=s5)

        # print(p5)
        # print(type(p5))
        # p5 = p5[0]
        # print(p5)


        ######### FIXING THERMODYNAMIC STATES ###########

        ##### Set the pressures based on the boiler and condenser pressures, at equal intervals
        p4, p3, p2 = set_pressure_intervals(p1, p5)
        pressure_writer.writerow([Th, p1, p2, p3, p4, p5])
        # print(f"T: {Th}, P1: {p1}, P2: {p2}, P3: {p3}, P4: {p4}, P5: {p5}")


        ##### Fix the state at the turbines - States 2, 3, 4
       
        s2 = s1  # For isentropic assumptions to calculate actual h values
        h2, s3 = turbine(2, h1, s2, p2) # Return the h2 value after calculating h2s value, assume isentropic process 2->3
        h3, s4 = turbine(3, h2, s3, p3)
        h4, s5 = turbine(4, h3, s4, p4)


        ##### Fix the state at the condenser inlet - State 5
        t5 = tc
        h5, s5 = turbine(5, h4, s4, p5)


        ##### Fix the state of the condenser outlet - State 6 (Saturated Liquid)
        t6 = tc
        p6 = p5
        h6, s6, d6, v6 = saturated_liquid(6, "T", t6)


        ##### Fix the states of the feedwater heater outlets - States 8, 10, and 12
        # State 8
        p8 = p4
        h8, s8, d8, v8 = saturated_liquid(8, "P", p8)

        # State 10
        p10 = p3
        h10, s10, d10, v10 = saturated_liquid(10, "P", p10)

        # State 12
        p12 = p1
        h12, s12, d12, v12 = saturated_liquid(12, "P", p12)


        #### Fix the states of the pump oulets - States 7, 9, 11
        # State 7
        p7 = p4
        s7 = s6
        h7_temp, v7 = pump(7, v6, h6, p7*100, p6*100)
        h7 = h6 + (h7_temp - h6) / pumpEff

        # State 9
        p9 = p3
        s9 = s8
        h9_temp, v9 = pump(9, v8, h8, p9*100, p8*100)
        h9 = h8 + (h9_temp - h8) / pumpEff

        # State 11
        p11 = p1
        s11 = s10
        h11_temp, v11 = pump(11, v10, h10, p11*100, p10*100)
        h11 = h10 + (h11_temp - h10) / pumpEff


        #### Fix the states of the closed feedwater outlets and following states
        # State 13 - Second CFW outlet
        p13 = p2
        h13, s13, d13, v13 = saturated_liquid(13, "P", p13)

        # State 14 - OFW inlet after trap
        h14, p14 = h13, p3

        # State 15 - First CFW outlet
        p15 = p4
        h15, s15, d15, v15 = saturated_liquid(15, "P", p15)

        # State 16 - Condenser inlet after trap
        h16, p16 = h15, p5


        ##### Write enthalpy values to file 
        enthalpy_writer.writerow([Th] + [
            h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16
        ])


        #### Fix states of cooling water
        # State 17
        h17, s17, d17, v17 = saturated_liquid(17, 'T', (80+273.15))

        # State 18
        h18, s18, d18, v18 = saturated_liquid(18, 'T', (125+273.15))


        ############ MASS FRACTION CALCULATION ######################
        y_prime = abs((h11 - h12) / (h2 - h13))
        y_doublePrime = abs((h10 - h9 - y_prime * (h14 - h9)) / (h3 - h9))
        y_triplePrime = abs(((1 - y_prime - y_doublePrime) * (h7 - h8)) / (h4 - h15))

        temp = y_prime + y_doublePrime + y_triplePrime # Verify if mass fractions sum to 1

        ##### Write mass fraction values to file
        mass_writer.writerow([y_prime, y_doublePrime, y_triplePrime])


        ######## PERFORMANCE METRICS #################
        # Calculate turbine work 
        W_turb1 = h1 - h2
        W_turb2 = (1 - y_prime) * (h2 - h3)
        W_turb3 = (1 - y_prime - y_doublePrime) * (h3 - h4)
        W_turb4 = (1 - y_prime - y_doublePrime - y_triplePrime) * (h4 - h5)

        # Calculate total work produced by the turbines
        W_out = W_turb1 + W_turb2 + W_turb3 + W_turb4

        # Calculate pump work 
        W_pump1 = (1 - y_prime - y_doublePrime) * (h7 - h6)
        W_pump2 = (1 - y_prime - y_doublePrime) * (h9 - h8)
        W_pump3 = h11 - h10

        # Calculate total pump work 
        W_in = W_pump1 + W_pump2 + W_pump3

        # Calculate net work, heat input
        W_net = W_out - W_in
        Q_in = h1 - h12

        # Calculate performance metrics (thermal efficiency, BWR)
        thermal_eff = W_net / Q_in
        bwr = W_in/W_out

        # Calculate mass flow rates
        m_dot = Wnet/W_net # mass flow rate of cycle
        m_dot_cw = Qout/abs(h18-h17) # mass flow rate of cooling water system

        # Calculate Qout 
        Q_out_unitmass = ((1-y_prime-y_doublePrime-y_triplePrime)*h5+y_triplePrime*h16-(1-y_prime-y_doublePrime)*h6)
        Q_out_steam = m_dot*((1-y_prime-y_doublePrime-y_triplePrime)*h5+y_triplePrime*h16-(1-y_prime-y_doublePrime)*h6)

        # system = m_dot*(Q_in-W_net)

        # Calculate net work, heat input in terms of mass
        W_net_mass = m_dot*W_net
        Q_in_mass = m_dot*Q_in

        # Efficiency and calculation checks 
        perfect_eff_check = (W_net_mass+Q_out_steam)/Q_in_mass # Check for perfect efficiency
        # print("Ratio Check: ", perfect_eff_check, "\n")        
        # print("Qout of steam sys =", Q_out_steam, "\t | \t Qin - W net =", system, "\n")
        # print("Q cycle =", Q_in_mass-Q_out_steam)


        ######## CALCULATING CO2 EMISSIONS #################
        Q_in_per_hour = Q_in_mass * 1 # Energy/1 hr
        Q_in_per_day = Q_in_mass * 24 # Energy/1 hr
        CO2_hour = Q_in_per_hour * (3.142/1000000) * 52.91 # lbs CO2 per 1 kWh Conversion factor: 52.91 kg/1mmBtu
        print("This is the CO2 emissions per hour: ", CO2_hour, "\n")
        CO2_day = Q_in_per_day * (3.142/1000000) * 52.91
        print("This is the CO2 emissions per day: ", CO2_day, "\n ")


        ######## WRITING DATA TO FILE #################
        # Selecting array for calculated variables
        m_dot = m_dot[0]
        m_dot_cw = m_dot_cw[0]
        W_net = W_net[0]
        Q_in = Q_in[0]
        Q_out_steam = Q_out_steam[0]
        thermal_eff = thermal_eff[0]
        bwr = bwr[0]

        # Writing calculated variables to file
        data_writer.writerow([
            Th, p1, m_dot, m_dot_cw, W_net, Q_in, Q_out_unitmass, Q_out_steam, thermal_eff, bwr, h1, h2, h3, h4,
            h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16, h17, h18, y_prime, y_doublePrime, y_triplePrime
        ])