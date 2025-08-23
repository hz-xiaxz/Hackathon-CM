####################################################################
#                            example 4                              #
#    in this script we demonstrate how to construct fermionic       #
#    hamiltonians, and check the jordan-wigner transformation.      #
#####################################################################
from quspin.operators import hamiltonian  # hamiltonians and operators
from quspin.basis import (
    spin_basis_1d,
    spinless_fermion_basis_1d,
)  # hilbert space spin basis
import numpy as np  # generic math functions
import matplotlib.pyplot as plt  # plotting library

#
##### define model parameters #####
l = 8  # system size
j = 1.0  # spin zz interaction
h = np.sqrt(2)  # z magnetic field strength
#
# loop over spin inversion symmetry block variable and boundary conditions
for zblock, pbc in zip([-1, 1], [1, -1]):
    #
    ##### define spin model
    # site-coupling lists (pbc for both spin inversion sectors)
    h_field = [[-h, i] for i in range(l)]
    j_zz = [[-j, i, (i + 1) % l] for i in range(l)]  # pbc
    # define spin static and dynamic lists
    static_spin = [["zz", j_zz], ["x", h_field]]  # static part of h
    dynamic_spin = []  # time-dependent part of h
    # construct spin basis in pos/neg spin inversion sector depending on apbc/pbc
    basis_spin = spin_basis_1d(l=l, zblock=zblock)
    # build spin hamiltonians
    h_spin = hamiltonian(static_spin, dynamic_spin, basis=basis_spin, dtype=np.float64)
    # calculate spin energy levels
    e_spin = h_spin.eigvalsh()
    #
    ##### define fermion model
    # define site-coupling lists for external field
    h_pot = [[2.0 * h, i] for i in range(l)]
    if pbc == 1:  # periodic bc: odd particle number subspace only
        # define site-coupling lists (including boudary couplings)
        j_pm = [[-j, i, (i + 1) % l] for i in range(l)]  # pbc
        j_mp = [[+j, i, (i + 1) % l] for i in range(l)]  # pbc
        j_pp = [[-j, i, (i + 1) % l] for i in range(l)]  # pbc
        j_mm = [[+j, i, (i + 1) % l] for i in range(l)]  # pbc
        # construct fermion basis in the odd particle number subsector
        basis_fermion = spinless_fermion_basis_1d(l=l, nf=range(1, l + 1, 2))
    elif pbc == -1:  # anti-periodic bc: even particle number subspace only
        # define bulk site coupling lists
        j_pm = [[-j, i, i + 1] for i in range(l - 1)]
        j_mp = [[+j, i, i + 1] for i in range(l - 1)]
        j_pp = [[-j, i, i + 1] for i in range(l - 1)]
        j_mm = [[+j, i, i + 1] for i in range(l - 1)]
        # add boundary coupling between sites (l-1,0)
        j_pm.append([+j, l - 1, 0])  # apbc
        j_mp.append([-j, l - 1, 0])  # apbc
        j_pp.append([+j, l - 1, 0])  # apbc
        j_mm.append([-j, l - 1, 0])  # apbc
        # construct fermion basis in the even particle number subsector
        basis_fermion = spinless_fermion_basis_1d(l=l, nf=range(0, l + 1, 2))
    # define fermionic static and dynamic lists
    static_fermion = [
        ["+-", j_pm],
        ["-+", j_mp],
        ["++", j_pp],
        ["--", j_mm],
        ["z", h_pot],
    ]
    dynamic_fermion = []
    # build fermionic hamiltonian
    h_fermion = hamiltonian(
        static_fermion,
        dynamic_fermion,
        basis=basis_fermion,
        dtype=np.float64,
        check_pcon=false,
        check_symm=false,
    )
    # calculate fermionic energy levels
    e_fermion = h_fermion.eigvalsh()
    #
    ##### plot spectra
    plt.plot(
        np.arange(h_fermion.ns), e_fermion / l, marker="o", color="b", label="fermion"
    )
    plt.plot(
        np.arange(h_spin.ns),
        e_spin / l,
        marker="x",
        color="r",
        markersize=2,
        label="spin",
    )
    plt.xlabel("state number", fontsize=16)
    plt.ylabel("energy", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=16)
    plt.grid()
    plt.tight_layout()
    plt.savefig("example4.pdf", bbox_inches="tight")
    # plt.show()
    plt.close()
