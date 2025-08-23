from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Ising_ED")

from quspin.operators import hamiltonian  # Hamiltonians and operators
from quspin.basis import spin_basis_1d  # Hilbert space spin basis
import numpy as np  # generic math functions

@mcp.tool()
async def Ising_ED(L: int, J: float, h: float) -> float:
    """返回Ising chain基态能量。
    Args:
        L: Ising chain长度
        J: 自旋zz相互作用强度
        h: x方向磁场大小
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
        H_spin = hamiltonian(static_spin, dynamic_spin, basis=basis_spin, dtype=np.float64)
        # calculate spin energy levels
        E_spin = H_spin.eigvalsh()
        
    return (E_spin / L)[0]

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")