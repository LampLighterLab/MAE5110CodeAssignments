## How to Run the code

## Running the Code

The relevant files are `assignment_1.py` and `assignment_1_sweep_graphs.py`. To run them, follow the directions enumerated below:

```bash
git clone https://github.com/jthomforde/MAE5110CodeAssignments.git
```

```bash
cd MAE5110CodeAssignments
```

The work for this assignment lives on a branch, so check it out before syncing:

```bash
git checkout jht224/assignment_1
```

```bash
uv sync --python 3.14
```

Then, to run the main assignment:

```bash
uv run python assignment_1.py
```

This takes roughly 3 minutes 40 seconds. It prints the classified initial states to the console and then displays the phase portrait with the analytic limit cycle overlaid.

To generate the parameter sweep graphs:

```bash
uv run python assignment_1_sweep_graphs.py
```

This takes roughly 30 seconds.



## Model Validation

Sanity Checks:

1. Use energy plot to judge if system reaches limit cycle or resting stability
My expectation was for the system was that the kinetic and potential energy would switch at impact and the total energy would reach a steady state with my current local energy formulas not taking into account the switching reference frame. When the system comes to rest I expected to see the energy come to rest also but in most cases the tota and potential energy oscillate as kinetic energy goes to zero as potential switches in between the lower spoke contact and the higher. 
2. System at rest at [0,0], [alpha + gamma], and [-alpha + gamma] initial conditions
I expected the system to be at rest at the selected initial condition and it was confirmed true by my model. One unexpected part is the oscillitary motion and some small noise during the two spokes touching at the same time IC, this ended up being the cause of my impact function and although there were oscillations, the model worked and proved to still be true. 
3. Lastly I tested the parameters to their respective bounds and making sure my system worked correctly. 
I expected the lower bound for N to be 4 and when tested I was unable to get rolling motion with a 3 spoke wheel with no added angular velocity. I then testing slope at 0 and tested rolling both ways and the model acted correctly and didn't oscillate when at rest because both spokes were at the same height. I then tested at 90 degree slope and was able to get a limit cycle.

## ROA Findings

I tested my ROA at  "length": 0.5,  # rod length (m) "mass": 0.2,  # point mass at end of rod (kg) "ramp_angle": -np.pi / 9,  # ramp angle (rad)  "number_of_spokes": 6,"alpha": np.pi / 6   # spoke angle (rad). Each point represents the initial conditions at that point and the color represents which attractor the point converged to. The red points converged to the red line at 0 angular velocity and the green converged to the green line representing the rolling limit cycle.
Params for the graphs:
length: 0.5m
mass: 0.2kg
ramp angle: -pi/9 - varied in ramp angle sweep
spoke number: 6 - varied in spoke number sweep
alpha: pi/num_spokes
![Alt Text](/Users/jtthomforde/4110projects/MAE5110CodeAssignments/assignment_1_graphs/ROA Sweep Phase Portrait ass1 4110.png)



Ramp Angle Graph:
![Alt Text](/Users/jtthomforde/4110projects/MAE5110CodeAssignments/assignment_1_graphs/Ramp Angle Sweep - ass_1 5110.png)
spoke number = 6

Spoke Number Graph:
![Alt Text](/Users/jtthomforde/4110projects/MAE5110CodeAssignments/assignment_1_graphs/Spoke Sweep ass1_graph.png)
ramp angle: pi/9 rad

After analyzing the spoke number and the ramp angle graphs its clear the an increase in ramp angle increases the number of spokes leads to higher percent of the state space converging to the limit cycle. This is also intuitive when thinking about the sweeps. The smaller alpha coorelates to a smaller loss in angular velocity during impact. The increase in ramp angle also means that it is easier for the wheel to turn over the upright position because its less change in potential energy between impact position and peak position at theta = 0. 

## Poncaire Section and Multiplier

Return Map:
![Alt Text](/Users/jtthomforde/4110projects/MAE5110CodeAssignments/assignment_1_graphs/Rimless Wheel Return Map.png)

Floqueint Multiplier Pertubation Sweep:

Deciding what Pertubation to use:
I swept pertubations from .01 to 0.5 to find a value that would find an accurate slope but not be too vulnurable to noise. I chose 0.1 because it was the closest to the theoretical value of 0.25. Results are below:



## Notes for PR
Im still working on the Multiplier Sweeps and finishing up the report, let me know if you have any advice




