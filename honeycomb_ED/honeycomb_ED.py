#
import sys, os

os.environ["KMP_DUPLICATE_LIB_OK"] = (
    "True"  # uncomment this line if omp error occurs on OSX for python 3
)
os.environ["OMP_NUM_THREADS"] = "1"  # set number of OpenMP threads to run in parallel
os.environ["MKL_NUM_THREADS"] = "1"  # set number of MKL threads to run in parallel
#

###########################################################################
#                            example 18 (modified)                        #
# This example exploits the python package 'networkx' for building a     #
# connectivity graph, using a model of spinless fermions on a honeycomb   #
# lattice with nearest-neighbor interactions.                             #
###########################################################################
from quspin.basis import spinless_fermion_basis_general
from quspin.operators import hamiltonian
import numpy as np
import networkx as nx  # networkx package, see https://networkx.github.io/documentation/stable/
import matplotlib.pyplot as plt  # plotting library

#
###### create honeycomb lattice
# lattice graph parameters
m = 2  # number of rows of hexagons in the lattice
n = 2  # number of columns of hexagons in the lattice
isPBC = True  # if True, use periodic boundary conditions
#
### build graph using networkx
hex_graph = nx.generators.lattice.hexagonal_lattice_graph(m, n, periodic=isPBC)
# label graph nodes by consecutive integers
hex_graph = nx.convert_node_labels_to_integers(hex_graph)
# set number of lattice sites
N = hex_graph.number_of_nodes()
print("constructed hexagonal lattice with {0:d} sites.\n".format(N))
nx.draw(hex_graph)
plt.savefig("honeycomb_lattice.png")  # save lattice figure

###### model parameters
#
N_f = m * n * 2 // 2  # number of spinless fermions
t = 1.0  # tunnelling matrix element
U = 0.0  # nearest-neighbor interaction strength
#
##### set up spinless fermion Hamiltonian with quspin #####
#
### compute basis
# use fermion_basis_general for spinless particles
basis = spinless_fermion_basis_general(N, Nf=N_f)
print("Hilbert space size: {0:d}.\n".format(basis.Ns))
#
# define site-coupling lists
# hopping term: -t * (c_i^dagger c_j + h.c.)
tunneling = [[-t, i, j] for i in range(N) for j in hex_graph.adj[i]]
print(len(hex_graph.edges()))
# nearest-neighbor interaction term: U * n_i * n_j
# hex_graph.edges() provides all unique nearest-neighbor pairs (i,j)
interactions = [[U, i, j] for i, j in hex_graph.edges()]
#
# define operator strings for Hamiltonian
# "+-" corresponds to hopping c_i^dagger c_j
# "nn" corresponds to interaction n_i * n_j
static = [["+-", tunneling], ["nn", interactions]]
dynamic = []
#
### construct Hamiltonian
H = hamiltonian(static, dynamic, basis=basi
                s, dtype=np.float64)
#
# compute eigensystem
E, V = H.eigsh(k=1, which="SA", maxiter=1e4)
print(f"\nlowest energies: {E}")
