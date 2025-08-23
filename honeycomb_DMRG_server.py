import numpy as np
from typing import Dict, Any

from tenpy.algorithms import dmrg
from tenpy.networks.mps import MPS
from tenpy.models.haldane import FermionicHaldaneModel

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("honeycomb_solver")

@mcp.tool()
def honeycomb_solver(
    t: float, U: float, Ly: int, chi_max: int = 50, seed: int = 0
) -> Dict[str, Any]:
    """
    Calculate ground state properties of the honeycomb model using DMRG.

    Args:
        t: The strength of the nearest-neighbor hopping.
        U: The strength of the nearest-neighbor density interaction.
        Ly: Number of sides along the cylinder circumference.
        chi_max: The maximum bond dimension for the DMRG simulation.
        seed: RNG seed for reproducibility.

    Returns:
        dict with parameters, energy_density (per site), chi, corr_length, entanglement_entropy (unit-cell bonds).
    """
    np.random.seed(seed)

    model_params = dict(conserve='N',
                        t1=-t,
                        t2=0.0,
                        mu=0,
                        V=U,
                        bc_MPS='infinite',
                        order='default',
                        Lx=1,
                        Ly=Ly,
                        bc_y='cylinder')

    dmrg_params = {
        'mixer': True,
        'mixer_params': {'amplitude': 1e-3, 'decay': 1.5, 'disable_after': 20},
        'trunc_params': {'svd_min': 1.e-5, 'chi_max': chi_max},
        'lanczos_params': {'N_min': 5, 'N_max': 20},
        'max_E_err': 1.e-4,
        'max_S_err': 1.e-4,
        'max_sweeps': 100,
        'verbose': 1,
    }

    # Setup the model and initial state
    M = FermionicHaldaneModel(model_params)

    # Choose an initial state
    prod_state = ['empty', 'full'] * (model_params['Lx'] * model_params['Ly'])

    psi = MPS.from_product_state(M.lat.mps_sites(), prod_state, bc=M.lat.bc_MPS)

    # Run the DMRG engine
    eng = dmrg.TwoSiteDMRGEngine(psi, M, dmrg_params)

    E0, psi = eng.run()

    # Diagnostics / observables
    S = psi.entanglement_entropy()          # entanglement entropies along unit cell bonds
    xi = psi.correlation_length()           # correlation length (in unit-cell lattice spacings)
    chi = psi.chi                           # current bond dimension(s); may be list or int

    # Package results into a dictionary for the MCP tool to return
    results = {
        "parameters": {
            "t": t, "U": U, "Ly": Ly, "chi_max": chi_max, "seed": seed
        },
        "ground_state_energy_density": float(E0),  # per site (iDMRG)
        "entanglement_entropy": list(map(float, S)),
        "correlation_length": float(xi),
        "chi": chi if isinstance(chi, int) else list(map(int, chi)),
    }

    return results

def main():
    mcp.run("stdio")

if __name__ == "__main__":
    main()