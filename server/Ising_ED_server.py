from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Ising_ED")

from quspin.operators import hamiltonian  # Hamiltonians and operators
from quspin.basis import spin_basis_1d  # Hilbert space spin basis
import numpy as np  # generic math functions


def run_ising_ed_calculation(L: int, J: float, h: float) -> float:
    """Calculates the ground state energy of the Transverse Field Ising Model (TFIM) using exact diagonalization.
    Args:
        L: The length of the Ising chain.
        J: The strength of the zz interaction.
        h: The strength of the transverse magnetic field in the x direction.
    """
    # loop over spin inversion symmetry block variable and boundary conditions
    for zblock, PBC in zip([-1, 1], [1, -1]):
        #
        ##### define spin model
        # site-coupling lists (PBC for both spin inversion sectors)
        h_field = [[-h, i] for i in range(L)]
        J_zz = [[-J, i, (i + 1) % L] for i in range(L)]  # PBC
        # define spin static and dynamic lists
        static_spin = [["zz", J_zz], ["x", h_field]]  # static part of H
        dynamic_spin = []  # time-dependent part of H
        # construct spin basis in pos/neg spin inversion sector depending on APBC/PBC
        basis_spin = spin_basis_1d(L=L, zblock=zblock)
        # build spin Hamiltonians
        H_spin = hamiltonian(
            static_spin, dynamic_spin, basis=basis_spin, dtype=np.float64
        )
        # calculate spin energy levels
        E_spin = H_spin.eigvalsh()

    return (E_spin / L)[0]


@mcp.tool()
def Ising_ED(L: int, J: float, h: float) -> float:
    """Calculates the ground state energy of the Transverse Field Ising Model (TFIM).
    Args:
        L: The length of the Ising chain. L > 12 may allocate too much memory.
        J: The strength of the zz interaction.
        h: The strength of the transverse magnetic field in the x direction.
    """
    if L > 12:
        raise ValueError("L > 12 may allocate too much memory.")
    return run_ising_ed_calculation(L, J, h)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run("stdio")
