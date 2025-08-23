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
    h_field = [[-h, i] for i in range(L)]
    J_zz = [[-J, i, (i + 1) % L] for i in range(L)]  # PBC
    static_spin = [["zz", J_zz], ["x", h_field]]
    
    min_energy = None

    # loop over spin inversion symmetry blocks
    for zblock in [-1, 1]:
        basis_spin = spin_basis_1d(L=L, zblock=zblock)
        H_spin = hamiltonian(
            static_spin, [], basis=basis_spin, dtype=np.float64
        )
        # calculate the lowest eigenvalue in the sector
        E_sector = H_spin.eigvalsh(k=1, which='SA') # 'SA' means smallest algebraic value
        
        if min_energy is None or E_sector[0] < min_energy:
            min_energy = E_sector[0]

    return min_energy / L


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
