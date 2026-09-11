# Assignment 1


## Dynamics of the System

There are two states that the system can go to: either there is enough energy in the system such that the wheel keeps going down the ramp, or there isn't enough energy and the wheel rocks back before settling in place and not moving. From drawing out the system on paper, the relationship between the ramp angle (gamma), the angle between the spokes of the wheel (2*alpha) and the angle of the spoke that is currently contacting with the vertical (theta) decides a lot of the behavior. At the moment that a second spoke contacts, it must be true theta = gamma + alpha because of trignometry and the isosceles triangle created by the contact from both rungs (when it is drawn out). That means that we know the behavior of the system changes around this point and if the wheel has enough energy to keep rolling, we have our new pivot point on the new spoke.  The equation of motion prior to this discontinuity occuring is a simple inverted pendulum with the contact point with the ramp being the pivot.

On the other hand, if the system doesn't have enough energy, the next time that the wheel swings forward onto a new rung and pivots about that, it won't have the energy for theta to be that large. Instead, it will swing backward and settle onto the previous rung that it was on. In this case, it must be true that theta = gamma - alpha, for similar geometry reasons to the first scenario. If the angle in the negative direction reaches this value we know the wheel cannot keep spinning because it has settled into a stationary position.

Thus, there are two event guards: we either trigger falling forward or lose energy to the point that the wheel stalls.

The energy in the system is lost because the collisions arent elastic and we assume that the contact is similar to a spring and damper so there is some loss every time the wheel turns. However, angular momentum about the new contact point is conserved so using that fact to evaluate angular momentum for the system at the old versus new contact point, we get the relationship thetadot(t minus) = thetadot(tplus)*cos(2alpha) with the cos(2*alpha) being a consequence of exactly one rotation of the rung. When this reset happens, we shift our coordinate frame to be centered on the new pivot point and use the above relationship to translate the values into the new frame. 

## Region of Attraction

As sort of mentioned before, there are two attractors in this system. Either the system comes to a complete stop and the wheel stands on two spokes or the wheel will continue to spin in a periodic, rolling limit cycle. If gamma is adjusted such that the slope angle is very small, we end up with one attractor since the wheel just stays stationary. If gamma is adjusted such that the slope angle is quite large, we could also potentially end up with one attactor where no matter the initial condition, the wheel always has enough energy to roll. 

In the region of attraction map, based off of different initial conditions for angular velocity and theta, all the points were classified as either positive (wheel continues to turn) or negative (wheel stops). Blue represents negative while red represents positive. Based on this graph we can see that we want to stay in the red region of initial conditions to have enough energy to keep rolling. I wasn't quite sure how to know when the system would reach steady state but I just simulated 100 steps because that seemed like a physically reasonable amount of steps to notice any sort of decaying behavior. To make this process accurate enough to capture behavior but not extremely slow, the timestep was slowed down slightly before and after impact so that enough detail is captured there. The swinging on one rung is more predictable and we aren't looking for an instantaneous change there so step detail doesn't matter as much at that point in time. 

On top of the region of attraction plot, the limit cycle line was also drawn. Because there is a discontinuous jump during the transition from one rung to another, the cycle looks like a curved line because we reset every time we switch rungs. The cycle is tracking the moment right after collision, the swing, and then going up until the moment right before the next collision. If we are above this line, the system has too much energy so more energy is lost in each collision, so we end up on the limit cycle line by dissipating energy faster. If we are below this line, the system has too little energy so it moves slower but less energy is lost at each impact and force from gravity helps it pick up speed more until we are on the limit cycle line. 

## Return Map

The return map is plotting post impact velocity for the previous step against the current step to look at how energy is changing in the system. The identity line represents when these two velocities are equal so we haven't lost energy and the wheel can continue turning. The intersection of looking at different outcomes from impact velocity ratios and the identity line is the optimal place to be to allow the wheel to keep turning. The floquet number measures how self-correcting the system is, so how robust the system is to any sort of disturbance like a bump on the ramp. The Floquet number is the slope of the return map line at a specified point, and equals cos^2(2*alpha) so our floquet number is expected to change as we change the number of spokes significantly but shouldn't change with the angle. The gamma_metrics plots confirm this. 

The other comparison on the metric plots is the fraction of initial conditions that cause stable rolling. As the slope angle is increased, the speed at which the wheel starts rolling is faster so the system is less sensitive to initial conditions. This increases our rate of success because as long as the other parameters (like acceleration due to gravity or spoke count) are good, the system can makeup for a bad angle for the system to start off on. Similarly, the higher the spoke count, the easier it is to swing from one rung to another because the distance between rungs is smaller. Therefore, the likelihood of sucess is higher because the closer we are to a perfectly smooth wheel. 

## Charts
return_map_demo.png - graph showing the return map versus the identity line for a baseline case

roa_demo.png - graph showing the region of attraction and limit cycle for a baseline case

sweep_gamma_metrics.png - graphically showing how the floquet multiplier changes as gamma changes and how the rate of success changes as gamma is increased. Floquet number isn't dependent on gamma so this stays stable, floquet number for fixed number of spokes of 8 is cos^2(2*alpha) = 0.5 which is exactly what we get for each gamma value. That means that local stability is not a function of gamma since floquet number is unaffected. The rate of success increases as the slope is increased because starting at a higher velocity from a steeper velocity makes the system more forgiving of bad initial conditions. The steeper slope also adds more net energy per stance from the higher change in height. 

sweep_gamma_roa.png - layout of different ROA plots for different gamma values. The rate of success increases as gamma  is increased as the red region becomes larger for larger gamma values. This is for the same reason mentioned above. 

sweep_N_metrics.png - graphically showing how the floquet multiplier changes as N, the spoke count, changes and how the rate of success increases as N is increased. The floquet number is cos^2(2*alpha) so increasing N decreases the angle between each spoke, alpha, which increases the floquet number. The rate of success also increases since increasing spoke count decreases alpha, which decreases the loss per step as that is a function of cos(2*alpha). This also makes sense physically as the wheel needs to swing a smaller distance to catch the next spoke so it is easier to keep spinning. And, the more spokes we add, the closer we are getting to a perfectly smooth wheel. 

sweep_N_roa.png -  layout of different ROA plots for different N values. Again, the rate of success increases as N is increased. 

## Run the code:
The main method is contained in assignment_1.py so that's the only file that needs to run. It will generate plots directly in the main folder. Values like the floquet number are output in the terminal while it runs. Most of the methods should be commented. 

