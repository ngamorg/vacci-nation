# Code

The core of the project. Here lies the implementation of the model described in the documentation.

# Reproducibility

To reproduce our code generated results you need to have python installed and (if working on Windows) FFmpeg to generate the mp4 animations, which you can download from http://ffmpeg.zeranoe.com/builds/. Then you can run the code with "python main.py". All our plots and videos are in the folder "plots_vids/". "plots.txt" in that folder describes all the (non-default) parameters that were used to generate these results.

To produce different result you can change set the variable "mode" to different values:
- "mode = PlotMode.ONLYPLOT": generates a SIVR plot (Susceptible, Infected, Truster, Recovered).
- "mode = PlotMode.MP4PLOT": generates the plot from "mode = PlotMode.ONLYPLOT" and a simulaton.mp4 file which is an animation of the SIVR simulatoin, both represent the same simulation
- "mode = PlotMode.VACCIPLOT": generates two plots. Every line in both of those plots represents the average over multiple simulations (default 20 simulations).

Following variables can be changed in the file "main.py" to produce different results, the first ones listed are the ones that differ in generating our results:
- "mode": as explained above
- "truster_cost_vaccination": sets the cost of vaccination for trusters
- "skeptical_cost_vaccination": sets the cost of vaccination for skepticals
- "alpha": number of edges that are added between two different groups i, j is alpha * ([number of nodes in i] + [number of nodes in j])
- "Agent.T": how far agents look into the future when deciding to vaccinate (days)
- "Agent.beta": infection rate / probability that a person infects its neighbor

You don't have to change these variables to reproduce our results, but you are free to play with them:
- "n": numer of expected nodes in the generated graph
- "group_percentages": group_percentages[0] means that group number 0 will have (group_percentages[0] * n) members. The length of the list determines the amount of groups.
- "k": number of initial neighbors when creating a group graph / watts_strogatz_graph
- "change_edge_percentage": probability for every edge that it is relinked (in a group graph)
- "groups": same length as group_percentages, define the group of every initial graph
- "groups_behaviours": same length as group_percentages, define the believes of every group
- "lim_init_infected":  initially infected
- "lim_init_vacci": initially vaccinated
- "depth": change the depth of view the agents use to estimate their chance of getting infected, 1 => direct neighbors, 2 => neighbors of neighbors
- "frames": # number of iterations of the simulation
- "fps": # frames per second of the simulation
