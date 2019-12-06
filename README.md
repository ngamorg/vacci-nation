# Epidemics &amp; Immunization

Semester project in the Agent Based Modeling and Social System Simulation course at ETHZ, Autumn semester 2019.

> * Group Name: Vacci-nation
> * Group participants names: Antunes Morgado Nicolas G., Gundersen Benjamin, Hühnerbein Jannes, Siebenaller Julius
> * Project Title: Epidemiology & Immunization

## General Introduction

Several times in human history epidemics have left areas and sometimes entire
civilizations in total devastation. Only with the rise of modern medicine and
especially widely available vaccines the development of large and complex societies
of today was made possible.
The characteristics of the flu with its almost yearly outbreaks and frequent
mutations - making a general vaccine impossible to develop - yield an interesting
game theoretical problem.
In this project the behaviour of a fictional society that is split it up into two
different groups is investigated. One group trusts vaccines and hence needs very
little incentive to get vaccinated ('trusters'). The other group is very skeptical
towards the cost and return of vaccines and hence vaccinates much later, sometimes
not at all ('skepticals').
With 'anti-vaxing' groups becoming more popular and diseases thought to be
extinct reappearing even in Central Europe 1 this question is gaining relevance
and needs to be analysed in more detail.

## The Model

The general assumptions of our model are as follows:
> * The infectious disease is modelled as a time-homogeneous Markov chain with
a finite state space according to an SIVR-process with 'vaccinated', respectively
'recovered' representing the final or absorbing states with permanent
immunity. The population is assumed to stay constant.
> * Agents are assumed to be rational utility-maximisers endowed with complete
information about their immediate neighbourhood. They decide in each timestep
whether or not to update their vaccination decision and hence if they
will get vaccinated employing a mixed strategy.
> * When facing the vaccination decision, each agent samples the health status
of its direct neighbours and deduces the probability of infection during the
next epoch from the share of infected neighbours.
> * The time-horizon of an agent is bounded, in the sense that only a certain
amount of time-steps is considered in the calculation of expected utility to
be maximised through the vaccination-decision.
> * Agents have a group affiliation to either be skeptical (group: 'skepticals') or
trust (group: 'trusters') that vaccines are safe. The group membership of an
agent determines the subjective costs they assign to vaccination, while the
costs of infection are assumed to be equal between groups.
> * The population structure is modelled as a small-world network, relying on
a Watts-Strogatz model. Two groups are assumed which represent smallworlds
on their own. These two networks are then combined assuming that
closeness in a group is larger than between groups.

## Fundamental Questions

(At the end of the project you want to find the answer to these questions)
(Formulate a few, clear questions. Articulate them in sub-questions, from the more general to the more specific. )

> * What is the relationship between social attitudes with respect to vaccination and the dynamics of epidemic episodes?
> * What is the influence of health policy in relation to the laissez faire results in the presence of strong individual beliefs against immunization?

## Expected Results

(What are the answers to the above questions that you expect to find before starting your research?)


## References 

> * Bauch, C. T. and Bhattacharyya, S. (2012), `Evolutionary game theory and social
learning can determine how vaccine scares unfold', PLoS computational biology
8(4), e1002452.
> * Bauch, C. T. and Earn, D. J. (2004), `Vaccination and the theory of games',
Proceedings of the National Academy of Sciences 101(36), 13391-13394.
> * Dadlani, A. (2013), `Deterministic models in epidemiology: from modeling to implementation'.
> * Earn, D., Brauer, F., van den Driessche, P. and Wu, J. (2008), Mathematical
epidemiology, Springer Berlin.
> * Fu, F., Rosenbloom, D. I.,Wang, L. and Nowak, M. A. (2010), `Imitation dynamics
of vaccination behaviour on social networks', Proceedings of the Royal Society
B: Biological Sciences 278(1702), 42-49.
> * Hancock, K., Veguilla, V., Lu, X., Zhong, W., Butler, E. N., Sun, H., Liu, F.,
Dong, L., DeVos, J. R., Gargiullo, P. M. et al. (2009), `Cross-reactive antibody
responses to the 2009 pandemic h1n1 influenza virus', New England Journal of
Medicine 361(20), 1945-1952.
> * Heesterbeek, H. (2005), `The law of mass-action in epidemiology: a historical
perspective', Ecological paradigms lost: routes of theory change pp. 81-104.
> * Keeling, M. J. and Eames, K. T. (2005), `Networks and epidemic models', Journal
of the Royal Society Interface 2(4), 295-307.
> * Kermack, W. O. and McKendrick, A. G. (1927), `A contribution to the mathematical
theory of epidemics', Proceedings of the royal society of london. Series A,
Containing papers of a mathematical and physical character 115(772), 700-721.
> * Liu, M., Li, D., Qin, P., Liu, C., Wang, H. and Wang, F. (2015), `Epidemics in
interconnected small-world networks', PloS one 10(3), e0120701.
> * Liu, X.-T., Wu, Z.-X. and Zhang, L. (2012), `Impact of committed individuals on
vaccination behavior', Physical Review E 86(5), 051132.
> * Meyers, L. A., Pourbohloul, B., Newman, M. E., Skowronski, D. M. and Brunham,
R. C. (2005), `Network theory and sars: predicting outbreak diversity', Journal
of theoretical biology 232(1), 71-81.
> * Moore, C. and Newman, M. E. (2000), `Epidemics and percolation in small-world
networks', Physical Review E 61(5), 5678.
> * Neumann, G., Noda, T. and Kawaoka, Y. (2009), `Emergence and pandemic potential
of swine-origin h1n1 influenza virus', Nature 459(7249), 931.
> * Newman, M. E. and Watts, D. J. (1999), `Scaling and percolation in the smallworld
network model', Physical review E 60(6), 7332.
> * Pastor-Satorras, R. and Vespignani, A. (2002), `Immunization of complex networks',
Physical review E 65(3), 036104.
> * Rusu, E. (2015), `Network models in epidemiology: Considering discrete and continuous
dynamics', arXiv preprint arXiv:1511.01062.
> * Shi, B., Qiu, H., Niu, W., Ren, Y., Ding, H. and Chen, D. (2017), `Voluntary
vaccination through self-organizing behaviors on locally-mixed social networks',
Scientific reports 7(1), 2665.
> * Shim, E., Grefenstette, J. J., Albert, S. M., Cakouros, B. E. and Burke, D. S.
(2012), `A game dynamic model for vaccine skeptics and vaccine believers:
measles as an example', Journal of Theoretical Biology 295, 194-203.
> * Smith, G. J., Vijaykrishna, D., Bahl, J., Lycett, S. J., Worobey, M., Pybus, O. G.,
Ma, S. K., Cheung, C. L., Raghwani, J., Bhatt, S. et al. (2009), `Origins and evolutionary
genomics of the 2009 swine-origin h1n1 influenza a epidemic', Nature
459(7250), 1122.
> * Stegehuis, C., Van Der Hofstad, R. and Van Leeuwaarden, J. S. (2016), `Epidemic
spreading on complex networks with community structures', Scientific reports
6, 29748.
> * Sun, G.-Q., Jusup, M., Jin, Z., Wang, Y. and Wang, Z. (2016), `Pattern transitions
in spatial epidemics: Mechanisms and emergent properties', Physics of life
reviews 19, 43-73.
> * Tornatore, E., Vetro, P. and Buccellato, S. M. (2014), `Sivr epidemic model with
stochastic perturbation', Neural Computing and Applications 24(2), 309-315.
Watts, D. J. and Strogatz, S. H. (1998), `Collective dynamics of 'smallworld'networks',
nature 393(6684), 440.
> * Wilson, E. B. and Worcester, J. (1945), `The law of mass action in epidemiology',
Proceedings of the National Academy of Sciences of the United States of America
31(1), 24.


## Research Methods

(Cellular Automata, Agent-Based Model, Continuous Modeling...) (If you are not sure here: 1. Consult your colleagues, 2. ask the teachers, 3. remember that you can change it afterwards)


## Other

(mention datasets you are going to use)
