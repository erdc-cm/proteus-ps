# for simFlags in simFlagsList:
#     simFlags['errorQuantities']=['u']
#     simFlags['errorTypes']= ['numericalSolution'] #compute error in soln and glob. mass bal
#     simFlags['errorNorms']= ['L2'] #compute L2 norm in space
#     simFlags['errorTimes']= ['Last'] #'All'
#     simFlags['echo']=True
#     simFlags['dataFile']       = simFlags['simulationName']+'_results'
#     simFlags['dataDir']        = os.getcwd()+'/results'
#     simFlags['storeQuantities']= ['simulationData','errorData'] #include errorData for mass bal
#     simFlags['storeTimes']     = ['Last']

from proteus import Context
ctx = Context.get()


# simulation flags for error analysis
#
# simFlagsList is initialized in proteus.iproteus
#

# Density
simFlagsList[0]['errorQuantities']=['u']
simFlagsList[0]['errorTypes']= ['numericalSolution'] #compute error in soln and glob. mass bal
simFlagsList[0]['errorNorms']= ['L2'] #compute L2 norm in space
simFlagsList[0]['errorTimes']= ['All'] #'All', 'Last'
simFlagsList[0]['echo']=True
simFlagsList[0]['dataFile']       = simFlagsList[0]['simulationName'] + '_%3.0e_DT_BDF%1d.db' %(ctx.DT,int(float(ctx.globalTimeOrder)))
simFlagsList[0]['dataDir']        = os.getcwd()+'/results'
simFlagsList[0]['storeQuantities']= ['simulationData','errorData'] #include errorData for mass bal
simFlagsList[0]['storeTimes']     = ['Last']

# Momentum
simFlagsList[1]['errorQuantities']=['u']
simFlagsList[1]['errorTypes']= ['numericalSolution'] #compute error in soln and glob. mass bal
simFlagsList[1]['errorNorms']= ['L2'] #compute L2 norm in space or H1 or ...
simFlagsList[1]['errorTimes']= ['All'] #'All', 'Last'
simFlagsList[1]['echo']=True
simFlagsList[1]['dataFile']       = simFlagsList[1]['simulationName'] + '_%3.0e_DT_BDF%1d.db' %(ctx.DT,int(float(ctx.globalTimeOrder)))
simFlagsList[1]['dataDir']        = os.getcwd()+'/results'
simFlagsList[1]['storeQuantities']= ['simulationData','errorData'] #include errorData for mass bal
simFlagsList[1]['storeTimes']     = ['Last']

#
start
quit
