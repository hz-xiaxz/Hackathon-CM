from typing import Dict, Any

from tenpy.networks.mps import MPS
from tenpy.algorithms.exact_diag import ExactDiag
from tenpy.models.haldane import FermionicHaldaneModel

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("honeycomb_ED_solver")

@mcp.tool()
def honeycomb_ED_solver(
    t: float, U: float, Lx: int, Ly: int, seed: int = 0
) -> Dict[str, Any]:
    """
    Calculate ground state properties of the honeycomb model using ExactDiag.
    Only returns the ground state energy (half-filling sector).

    Args:
        t: The strength of the nearest-neighbor hopping.
        U: The strength of the nearest-neighbor density interaction.
        Lx: Number of sides along the y-direction.
        Ly: Number of sides along the y-direction.
        seed: RNG seed for reproducibility.

    Returns:
        Calculation parameters and the ground state energy in a dict.
    """
    model_params = dict(conserve='N',
                        t1=-t,
                        t2=0.0,
                        mu=0.0,
                        V=U,
                        bc_x="periodic",
                        bc_y="periodic",
                        Lx=Lx,
                        Ly=Ly)

    # Setup the model
    M = FermionicHaldaneModel(model_params)
    
    prod_state = ['empty', 'full'] * (Lx * Ly)
    psi_DMRG = MPS.from_product_state(M.lat.mps_sites(), prod_state)
    charge_sector = psi_DMRG.get_total_charge(True)  # ED charge sector should match

    ED = ExactDiag(M, charge_sector=charge_sector, max_size=1.e11)
    ED.build_full_H_from_mpo()       # required here
    ED.full_diagonalization()        # fills ed.E and ed.V
    E0, _ = ED.groundstate()

    # Package results into a dictionary for the MCP tool to return
    results = {
        "parameters": {
            "t": t, "U": U, "Lx": Lx, "Ly": Ly, "seed": seed
        },
        "energy_density": float(E0) / Lx / Ly / 2
    }

    return results

def main():
    mcp.run("stdio")

if __name__ == "__main__":
    main()