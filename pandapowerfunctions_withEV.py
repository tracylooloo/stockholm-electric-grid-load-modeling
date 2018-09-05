
# coding: utf-8

# In[7]:
import itertools
import pandapower as pp
import numpy as np

#This python file contains 3 functions: ppsolverLP (loading percent of lines), ppsolverBV (bus voltages), ppsolverEG (external grid)

#just setting a bunch of variable values 
sn_kva = 1000
c_in_nF_km =420
vn_kv_SK = 11
max_i_ka_9 = .35 #0.054
max_i_ka_12b = .31 #0.09271
max_i_ka_12 = .35 #0.09271
max_i_ka_15b = .35 #0.09141
max_i_ka_15 = .35 #0.09141
PF = .4
pf=.4
q_kvarSK09=138*PF
q_kvarSK12 = 39*PF
q_kvarSK12b = 759*PF
q_kvarSK15b = 897*PF
q_kvarSK15 = 1112*PF

#outlet power rating, opr
opr= 6.72

#c is used for testing values
c=1.36

# LP stands for current(i) loading percents of the line. The function ppsolverLP returns a numpy array of arrays. First array is currents through first line for each hour of the day. 
#Second array is currents of second line for each hour, etc. same for third, fourth array
#the pandapower network is solved for each time step and the loading percent value solved for each line is appended to its 
#corresponding array for each time

#variable meaning in sk09p: sk09 is the bus, p means power
def ppsolverLP(sk09p, sk12p, sk15p):
    LP0all = []
    LP1all = []
    LP2all = []
    LP3all = []
    LP4all = []
    LPall = []
    
    for busL09,busL12,busL15 in zip(sk09p, sk12p, sk15p):
        
        net=pp.create_empty_network("HA_LF",f_hz=50) #create an empty network #name, f_hz, sn_kva unsure of 50, 1000

        ## BUSES (temp vn_kv)
        busSK = pp.create_bus(net, name="Bus SK", vn_kv=vn_kv_SK)
        busSK09 = pp.create_bus(net, name="Bus SK09", vn_kv=11)
        busSK12b = pp.create_bus(net, name="Bus SK12b", vn_kv=11) 
        busSK12 = pp.create_bus(net, name="Bus SK12", vn_kv=11)
        busSK15b= pp.create_bus(net, name="Bus SK15b", vn_kv=11)
        busSK15= pp.create_bus(net, name="Bus SK15", vn_kv=11)


        ## LINES  
        b=3.6e-6 #b/2=c*10^-9*2pi*freq
        #c_nf is line capacitance and Max_i is maximum thermal , max_i_ka=0.588, name="Line 1")
        lineM0=pp.create_line_from_parameters(net, busSK, busSK09, length_km=.119, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_9, name="Line M0")
        lineL0=pp.create_line_from_parameters(net, busSK, busSK12b, length_km=.1305, r_ohm_per_km=.151, x_ohm_per_km=.087, c_nf_per_km=388.5, max_i_ka= max_i_ka_12b, name="Line L0")
        lineL1=pp.create_line_from_parameters(net, busSK12b, busSK12, length_km=.300, r_ohm_per_km=.12777, x_ohm_per_km=.08115, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_12, name="Line L1")
        lineI0=pp.create_line_from_parameters(net, busSK, busSK15b, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15b, name="Line I0")
        lineI1=pp.create_line_from_parameters(net, busSK15b, busSK15, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15, name="Line I1")

        ## LOADS q=reactivepower, use the step values from busp09,busp12, busp15
        ## p_kw = percentage * step value, percentage determined from 2016 Substation_data
        load09=pp.create_load(net, busSK09, p_kw= busL09, q_kvar= q_kvarSK09,name="Load SK09") 
        load12b=pp.create_load(net, busSK12b, p_kw=0.9511278*busL12, q_kvar=q_kvarSK12b,name="Load SK12b") 
        load12=pp.create_load(net, busSK12, p_kw=0.0488721*busL12, q_kvar=q_kvarSK12,name="Load SK12") 
        load15b=pp.create_load(net, busSK15b, p_kw=0.4465*busL15, q_kvar=q_kvarSK15b,name="Load SK15b")
        load15=pp.create_load(net, busSK15, p_kw=0.5535*busL15, q_kvar=q_kvarSK15,name="Load SK15")

        EVload09=pp.create_load(net, busSK09, p_kw=opr*2*c, q_kvar= pf*opr*2*c,name="EV Load SK09")
        EVload12=pp.create_load(net, busSK12, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12")
        EVload12b=pp.create_load(net, busSK12b, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12b")
        EVload15b=pp.create_load(net, busSK15b, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15b")
        EVload15=pp.create_load(net, busSK15, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15")
        
        ## EXTERNAL GRID Slack, change vals, assume top substation is slack
        pp.create_ext_grid(net,busSK, voltage = 1.0, va_degree=0,name="SlackGrid")

        #PandaPowerResults (change look up by line name instead of index if possible)
        pp.runpp(net)
        net._ppc["internal"]["Ybus"].todense()
        #net.res_line
     #grabs each returned line current loading percent for each time step, appends to an array for each line
        LP0=net.res_line.loc[0].loading_percent #loadingpercent for line 0 (first line created, M0)
        LP0all.append(LP0)
        LP1=net.res_line.loc[1].loading_percent #loadingpercent for line 1 (second line created, L0)
        LP1all.append(LP1)
        LP2=net.res_line.loc[2].loading_percent #loadingpercent for line 2 (third line created, L1)
        LP2all.append(LP2)
        LP3=net.res_line.loc[3].loading_percent #loadingpercent for line 3 (third line created, I0)
        LP3all.append(LP3)
        LP4=net.res_line.loc[4].loading_percent #loadingpercent for line 4 (third line created, I1)
        LP4all.append(LP4)
    #combine all the line current loading percents    
    LPall= np.concatenate([[np.asarray(LP0all)], [np.asarray(LP1all)], [np.asarray(LP2all)], [np.asarray(LP3all)], [np.asarray(LP4all)]])

    
    return LPall
#end of ppsolverLP

#unfortunately in python you can only return one thing. Instead of having three functions, another option is to have an array of three arrays of arrays, that combines LPall, BVall, EGall. Not sure which would be faster or better for you

# BV stands for Bus Voltage in per unit. The function ppsolverBV returns a numpy array of arrays. First array is currents through first line for each hour of the day. 
#Second array is currents of second line for each hour, etc. same for third, fourth array
def ppsolverBV(sk09p, sk12p, sk15p):
    BV0all = []
    BV1all = []
    BV2all = []
    BV3all = []
    BV4all = []
    BV5all = []
    BVall = []
    
    for busL09,busL12,busL15 in zip(sk09p, sk12p, sk15p):
        #just setting a bunch of variable values 
        sn_kva = 1000
        c_in_nF_km =420
        vn_kv_SK = 11
        max_i_ka_9 = .35 #0.054
        max_i_ka_12b = .31 #0.09271
        max_i_ka_12 = .35 #0.09271
        max_i_ka_15b = .35 #0.09141
        max_i_ka_15 = .35 #0.09141
        PF = .4
        q_kvarSK09=138*PF
        q_kvarSK12 = 39*PF
        q_kvarSK12b = 759*PF
        q_kvarSK15b = 897*PF
        q_kvarSK15 = 1112*PF
        net=pp.create_empty_network("HA_LF",f_hz=50) #create an empty network #name, f_hz, sn_kva unsure of 50, 1000

        ## BUSES (temp vn_kv)
        busSK = pp.create_bus(net, name="Bus SK", vn_kv=vn_kv_SK)
        busSK09 = pp.create_bus(net, name="Bus SK09", vn_kv=11)
        busSK12b = pp.create_bus(net, name="Bus SK12b", vn_kv=11) 
        busSK12 = pp.create_bus(net, name="Bus SK12", vn_kv=11)
        busSK15b= pp.create_bus(net, name="Bus SK15b", vn_kv=11)
        busSK15= pp.create_bus(net, name="Bus SK15", vn_kv=11)


        ## LINES  
        b=3.6e-6 #b/2=c*10^-9*2pi*freq
        #c_nf is line capacitance and Max_i is maximum thermal , max_i_ka=0.588, name="Line 1")
        lineM0=pp.create_line_from_parameters(net, busSK, busSK09, length_km=.119, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_9, name="Line M0")
        lineL0=pp.create_line_from_parameters(net, busSK, busSK12b, length_km=.1305, r_ohm_per_km=.151, x_ohm_per_km=.087, c_nf_per_km=388.5, max_i_ka= max_i_ka_12b, name="Line L0")
        lineL1=pp.create_line_from_parameters(net, busSK12b, busSK12, length_km=.300, r_ohm_per_km=.12777, x_ohm_per_km=.08115, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_12, name="Line L1")
        lineI0=pp.create_line_from_parameters(net, busSK, busSK15b, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15b, name="Line I0")
        lineI1=pp.create_line_from_parameters(net, busSK15b, busSK15, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15, name="Line I1")

        ## LOADS q=reactivepower, use the step values from busp09,busp12, busp15
        ## p_kw = percentage * step value, percentage determined from 2016 Substation_data
        load09=pp.create_load(net, busSK09, p_kw= busL09, q_kvar= q_kvarSK09,name="Load SK09") 
        load12b=pp.create_load(net, busSK12b, p_kw=0.9511278*busL12, q_kvar=q_kvarSK12b,name="Load SK12b") 
        load12=pp.create_load(net, busSK12, p_kw=0.0488721*busL12, q_kvar=q_kvarSK12,name="Load SK12") 
        load15b=pp.create_load(net, busSK15b, p_kw=0.4465*busL15, q_kvar=q_kvarSK15b,name="Load SK15b")
        load15=pp.create_load(net, busSK15, p_kw=0.5535*busL15, q_kvar=q_kvarSK15,name="Load SK15")
        
        EVload09=pp.create_load(net, busSK09, p_kw=opr*2*c, q_kvar= pf*opr*2*c,name="EV Load SK09")
        EVload12=pp.create_load(net, busSK12, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12")
        EVload12b=pp.create_load(net, busSK12b, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12b")
        EVload15b=pp.create_load(net, busSK15b, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15b")
        EVload15=pp.create_load(net, busSK15, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15")
        ## EXTERNAL GRID Slack, change vals, assume top substation is slack
        pp.create_ext_grid(net,busSK, voltage = 1.0, va_degree=0,name="SlackGrid")

    #PandaPower Results (change look up by line name instead of index if possible)
        pp.runpp(net)
        net._ppc["internal"]["Ybus"].todense()
        #net.res_line
     #grabs each returned bus voltage per unit for each time step, appends to an array for each bus
        BV0 = net.res_bus.loc[0].vm_pu #slackbus
        BV0all.append(BV0)
        BV1 = net.res_bus.loc[1].vm_pu
        BV1all.append(BV1)
        BV2= net.res_bus.loc[2].vm_pu #bus voltage for bus 2 (second bus created, SK12)
        BV2all.append(BV2)
        BV3= net.res_bus.loc[3].vm_pu 
        BV3all.append(BV3)
        BV4= net.res_bus.loc[4].vm_pu 
        BV4all.append(BV4)
        BV5= net.res_bus.loc[5].vm_pu 
        BV5all.append(BV5)
        
    #combine all the line current loading percents    
    BVall= np.concatenate([[np.asarray(BV0all)], [np.asarray(BV1all)], [np.asarray(BV2all)], [np.asarray(BV3all)], [np.asarray(BV4all)], [np.asarray(BV5all)]])

    
    return BVall
#end of ppsolverBV function



# SV stands for Slack Voltage. p_ka is active power, q_kvar is reactive power. The function ppsolverEG (EG=external grid) returns a numpy array of arrays. First array is reactive powers for each time step, second array is reactive powers for eachtime step
def ppsolverEG(sk09p, sk12p, sk15p):
    EGpall = []
    EGqall = []
    
    
    for busL09,busL12,busL15 in zip(sk09p, sk12p, sk15p):
        #just setting a bunch of variable values 
        sn_kva = 1000
        c_in_nF_km =420
        vn_kv_SK = 11
        max_i_ka_9 = .35 #0.054
        max_i_ka_12b = .31 #0.09271
        max_i_ka_12 = .35 #0.09271
        max_i_ka_15b = .35 #0.09141
        max_i_ka_15 = .35 #0.09141
        PF = .4
        q_kvarSK09=138*PF
        q_kvarSK12 = 39*PF
        q_kvarSK12b = 759*PF
        q_kvarSK15b = 897*PF
        q_kvarSK15 = 1112*PF
        net=pp.create_empty_network("HA_LF",f_hz=50) #create an empty network #name, f_hz, sn_kva unsure of 50, 1000

        ## BUSES (temp vn_kv)
        busSK = pp.create_bus(net, name="Bus SK", vn_kv=vn_kv_SK)
        busSK09 = pp.create_bus(net, name="Bus SK09", vn_kv=11)
        busSK12b = pp.create_bus(net, name="Bus SK12b", vn_kv=11) 
        busSK12 = pp.create_bus(net, name="Bus SK12", vn_kv=11)
        busSK15b= pp.create_bus(net, name="Bus SK15b", vn_kv=11)
        busSK15= pp.create_bus(net, name="Bus SK15", vn_kv=11)


        ## LINES  
        b=3.6e-6 #b/2=c*10^-9*2pi*freq
        #c_nf is line capacitance and Max_i is maximum thermal , max_i_ka=0.588, name="Line 1")
        lineM0=pp.create_line_from_parameters(net, busSK, busSK09, length_km=.119, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_9, name="Line M0")
        lineL0=pp.create_line_from_parameters(net, busSK, busSK12b, length_km=.1305, r_ohm_per_km=.151, x_ohm_per_km=.087, c_nf_per_km=388.5, max_i_ka= max_i_ka_12b, name="Line L0")
        lineL1=pp.create_line_from_parameters(net, busSK12b, busSK12, length_km=.300, r_ohm_per_km=.12777, x_ohm_per_km=.08115, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_12, name="Line L1")
        lineI0=pp.create_line_from_parameters(net, busSK, busSK15b, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15b, name="Line I0")
        lineI1=pp.create_line_from_parameters(net, busSK15b, busSK15, length_km=.480, r_ohm_per_km=.13, x_ohm_per_km=.08, c_nf_per_km=c_in_nF_km, max_i_ka= max_i_ka_15, name="Line I1")

        ## LOADS q=reactivepower, use the step values from busp09,busp12, busp15
        ## p_kw = percentage * step value, percentage determined from 2016 Substation_data
        load09=pp.create_load(net, busSK09, p_kw= busL09, q_kvar= q_kvarSK09,name="Load SK09") 
        load12b=pp.create_load(net, busSK12b, p_kw=0.9511278*busL12, q_kvar=q_kvarSK12b,name="Load SK12b") 
        load12=pp.create_load(net, busSK12, p_kw=0.0488721*busL12, q_kvar=q_kvarSK12,name="Load SK12") 
        load15b=pp.create_load(net, busSK15b, p_kw=0.4465*busL15, q_kvar=q_kvarSK15b,name="Load SK15b")
        load15=pp.create_load(net, busSK15, p_kw=0.5535*busL15, q_kvar=q_kvarSK15,name="Load SK15")
        
        EVload09=pp.create_load(net, busSK09, p_kw=opr*2*c, q_kvar= pf*opr*2*c,name="EV Load SK09")
        EVload12=pp.create_load(net, busSK12, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12")
        EVload12b=pp.create_load(net, busSK12b, p_kw=opr*18*c, q_kvar= pf*opr*18*c,name="EV Load SK12b")
        EVload15b=pp.create_load(net, busSK15b, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15b")
        EVload15=pp.create_load(net, busSK15, p_kw=opr*276*c, q_kvar= pf*opr*276*c,name="EV Load SK15")
        ## EXTERNAL GRID Slack, change vals, assume top substation is slack
        pp.create_ext_grid(net,busSK, voltage = 1.0, va_degree=0,name="SlackGrid")

    #PandaPower Results (change look up by line name instead of index if possible)
        pp.runpp(net)
        net._ppc["internal"]["Ybus"].todense()
        #net.res_line
     #grabs each returned external grid voltage per unit for each time step, appends to an array for active, another for reactive
        EGp = net.res_ext_grid.loc[0].p_kw
        EGpall.append(EGp)
        EGq = net.res_ext_grid.loc[0].q_kvar
        EGqall.append(EGq)
        
        
    #combine both active array and reactive array    
    EGall= np.concatenate([[np.asarray(EGpall)], [np.asarray(EGqall)]])

    
    return EGall
#end of ppsolverEG function



