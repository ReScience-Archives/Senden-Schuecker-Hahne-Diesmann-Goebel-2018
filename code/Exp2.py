# -----------------------------------------------------------------------------
# Distributed under the GNU General Public License.
#
# Contributors: Mario Senden mario.senden@maastrichtuniversity.nl
# -----------------------------------------------------------------------------
# References:
#
# Gancarz, G., Grossberg, S. "A Neural Model of the Saccade Generator in the
# Reticular Formation." Neural Networks 11, no. 7-8 (October 1998): 1159-74.
# doi:10.1016/S0893-6080(98)00096-3.
# -----------------------------------------------------------------------------
# File description:
#
# Simulates reimplemented saccade generation (SG) model of
# Gancarz & Grossberg (1998).
# Generates Fig. 2: Activity profiles in LLBN and EBN
# (figure 5 in original publication).
# LLBN and EBN discharge rates for 5, 10, and 20 degree saccades.
# Input to left SG was set equal to 1, 1.75, and 2.5; in each case for 85 ms
# -----------------------------------------------------------------------------

import sys
import pylab as pl
from matplotlib import rcParams

# set up model
from setup_model import *

# define additional variables
cm2inch = .394  # inch/cm


# figure setup
rcParams.update({'figure.autolayout': True})

fig_name = '../article/figures/fig2.eps'
fig_size = np.multiply([17.6, 8.5], cm2inch)
fig_rows = 1
fig_cols = 2
fig_plots = fig_rows * fig_cols
ppi = 1200
face = 'white'
edge = 'white'

ax = [None] * fig_plots
fig = pl.figure(facecolor=face, edgecolor=edge, figsize=fig_size)
for i in range(0, fig_plots):
    col = np.mod(i, 2)
    ax[i] = fig.add_subplot(fig_rows, fig_cols, i + 1)
    ax[i].axhline(color='k', linestyle='--')
    ax[i].set_xlabel('time (ms)', fontsize=14)
    ax[i].set_ylim([-1., 1.5])
    ax[i].tick_params(labelsize=12)
    ax[i].locator_params(axis='y', nbins=3)

ax[0].text(-0.075, 1.1, 'A', transform=ax[0].transAxes, size=16, weight='bold')
ax[1].text(-0.075, 1.1, 'B', transform=ax[1].transAxes, size=16, weight='bold')

'''set up experiment

input & external electric stimulation
-------------------------------------
I : inputs applied to left LLBN

time protocol (in ms)
-----------------------
t_relax  : relaxation period (prior to experiment)
preStim  : time interval prior to stimulus presentation
Stim     : time interval for which stimulus is presented
postStim : time interval after stimulus presentation

time vector T
-------------
since neuron activity is plotted as a function of time,
time vector T is pre-calculated based on time protocol
t_start : start of experiment
t_end   : end of experiment
t_steps : number of simulated time steps
'''
I = [1., 1.75, 2.5]

preStim = 50
Stim = 85
postStim = 65

t_relax = 100
t_start = 0
t_end = preStim + Stim + postStim
t_steps = int((t_end - t_start) / dt) - 1
T = np.linspace(t_start, t_end, t_steps)

'''set up recording devices

neuron activity is recorded using NEST's multimeter object
recording the 'rate' property of a neuron after each time step
'''
MM = [None] * 3
for s in range(0, 3):
    MM[s] = nest.Create('multimeter')
    nest.SetStatus(MM[s], {'interval': dt, 'record_from': ['rate']})

    '''relaxation

    let the system reach equilibrium
    in the absence of input and stimulation.
    '''
    nest.Simulate(t_relax)

    '''connect recording devices

    multimeters are connected to neurons of interest
    '''
    nest.Connect(MM[s], LLBN[0], syn_spec={'delay': dt})
    nest.Connect(MM[s], EBN[0], syn_spec={'delay': dt})

    # simulate pre-stimulus period
    nest.Simulate(preStim)

    # simulate stimulus period
    nest.SetStatus(LLBN[0], {'mean': I[s]})
    nest.Simulate(Stim)

    # simulate post-stimulus period
    nest.SetStatus(LLBN[0], {'mean': 0.})
    nest.Simulate(postStim)

    # gather data from recording device
    data = nest.GetStatus(MM[s])
    senders = data[0]['events']['senders']
    voltage = data[0]['events']['rate']

    # plot
    ax[0].plot(T, voltage[np.where(senders == LLBN[0])], linewidth=2)
    ax[1].plot(T, voltage[np.where(senders == EBN[0])], linewidth=2)

# save and display figure
pl.savefig(fig_name, format='eps', dpi=ppi, bbox_inches='tight')
pl.show()
