## Model Validation

Sanity Checks:

1. Use energy plot to judge if system reaches limit cycle or resting stability
My expectation was for the system was that the kinetic and potential energy would switch at impact and the total energy would reach a steady state with my current local energy formulas not taking into account the switching reference frame. When the system comes to rest I expected to see the energy come to rest also but in most cases the tota and potential energy oscillate as kinetic energy goes to zero as potential switches in between the lower spoke contact and the higher. 
2. System at rest at [0,0], [alpha + gamma], and [-alpha + gamma] initial conditions
I expected the system to be at rest at the selected initial condition and it was confirmed true by my model. One unexpected part is the oscillitary motion and some small noise during the two spokes touching at the same time IC, this ended up being the cause of my impact function and although there were oscillations, the model worked and proved to still be true. 
3. Lastly I tested the parameters to their respective bounds and making sure my system worked correctly. 
I expected the lower bound for N to be 4 and when tested I was unable to get rolling motion with a 3 spoke wheel with no added angular velocity. I then testing slope at 0 and tested rolling both ways and the model acted correctly and didn't oscillate when at rest because both spokes were at the same height. I then tested at 90 degree slope and was able to get a limit cycle.



