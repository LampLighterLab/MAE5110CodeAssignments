def newstate(dyn,state,t,timestep,params):
    new = state + (timestep * dyn(t,state,params)) 
    return new


## simulation loop
##   for step, t in enumerate(time_traj[:-1]):
##      state_traj[:, step + 1] = state_traj[:, step] + timestep * model.dynamics(
##           t, state_traj[:, step], params)