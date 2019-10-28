"""

Authors
-------
Vacci-nation group
Julius Siebenaller, Jannes Hühnerbein, Benjamin Gundersen & Nicolas Antunes Morgado
2019++

Topic
-----
Epidemiology & Immunization

Description
-----------
* Insert summary of what the code accomplishes *

"""

# import all required libraries
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

"""
SPECIFICATION: here goes a description of the function/class method should do. It helps both consumers of the function and as a form of documentation.
PRE: pre-conditions of the function/method. Here the type of the inputs is made explicit, so as to avoid (for example) runtime errors. 
POST: post-condition; analogous to PRE.
"""

"""
Code from http://jaredgerschler.blog/2018/12/05/epidemic-modeling-using-python-part-i/
Further useful sources:
    https://pythonhosted.org/epydemic/
    https://pythonhosted.org/epydemic/glossary.html#term-compartmented-model-of-disease
"""

# demographics:
N = 5000 # total population
I0 = 0.001*N # initial infected
R0 = 0 * N # initial recovered
S0 = N - I0 - R0 #initial susceptible

# transition dynamics
beta = 0.35 # contact rate
gamma = 0.01 # mean recovery rate

# initial conditions vector
y0 = S0, I0, R0
# 200 evenly spaced values (representing days) 
t = np.linspace(0, 200, 200)

# differential equations
def func(y, t, N, beta, gamma):
    # S, I, R values assigned from vector
    S, I, R = y
    # differential equations
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

# Integrate the diff eqs over the time array
values = odeint(func, y0, t, args=(N, beta, gamma))
# assign S, I, R values from values transpose
S, I, R = values.T

fig = plt.figure()
ax = fig.add_subplot(111, axisbelow=True)
ax.plot(t, S, 'black', lw=1.5, label='Susceptible')
ax.plot(t, I, 'orange', lw=1.5, label='Infected')
ax.plot(t, R, 'blue', lw=1.5, label='Recovered')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Number of People')
ax.set_ylim(0,5100)
ax.set_xlim(0,200)
ax.grid(b=True, which='major', c='#bbbbbb', lw=1, ls='-')
legend = ax.legend()
legend.get_frame().set_alpha(0.5)
plt.show()
