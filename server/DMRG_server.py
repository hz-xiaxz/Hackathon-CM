# Copyright (C) TeNPy Developers, Apache license

import numpy as np
from tenpy.models.tf_ising import TFIChain
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
import matplotlib.pyplot as plt
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List

# 1. Create the MCP server instance
mcp = FastMCP("TenPy TFIM Analysis Server")


def run_dmrg_calculation(
    g: float, L_unit_cell: int, chi_max: int, J: float
) -> Dict[str, Any]:
    """
    Performs the core DMRG calculation.
    """
    print(f"Running infinite DMRG for TFIM with g={g}, J={J}, chi_max={chi_max}...")

    model_params = dict(L=L_unit_cell, J=J, g=g, bc_MPS="infinite", conserve=None)

    dmrg_params = {
        "trunc_params": {"chi_max": chi_max, "svd_min": 1.0e-10},
        "update_env": 5,
        "start_env": 5,
        "max_E_err": 1.0e-4,
        "max_S_err": 1.0e-4,
        "max_sweeps": 100,
        "mixer": False,
    }

    # Setup the model and initial state
    M = TFIChain(model_params)

    # Choose an initial state based on the expected phase for better convergence
    initial_state = (["up", "down"] * L_unit_cell)[:L_unit_cell]

    psi = MPS.from_product_state(M.lat.mps_sites(), initial_state, M.lat.bc_MPS)
    np.set_printoptions(linewidth=120)

    # Run the DMRG engine
    engine = dmrg.TwoSiteDMRGEngine(psi, M, dmrg_params)

    E0, psi = engine.run()

    # The result from iDMRG engine.run() is the total energy of the unit cell.
    # We divide by the number of sites to get the intensive energy density.
    energy_density = E0 / L_unit_cell

    # Calculate other physical observables from the ground state MPS
    entanglement_entropy = psi.entanglement_entropy()[0]
    correlation_length = psi.correlation_length(tol_ev0=1.0e-3)

    # For observables like magnetization, average over the sites in the unit cell
    magnetization_z = np.mean(psi.expectation_value("Sigmaz"))

    # Correlation function is returned as a numpy array; convert to list for JSON compatibility
    correlation_xx = psi.correlation_function("Sigmax", "Sigmax", [0], 20)[0, :]

    print("DMRG calculation finished successfully.")

    # Package results into a dictionary for the MCP tool to return
    results = {
        "parameters": {"g": g, "L_unit_cell": L_unit_cell, "J": J, "chi_max": chi_max},
        "ground_state_energy_density": energy_density,
        "entanglement_entropy": entanglement_entropy,
        "correlation_length": correlation_length,
        "magnetization_z": magnetization_z,
        "correlation_xx": correlation_xx.tolist(),
    }

    return results


@mcp.tool()
def analyze_tfim_with_dmrg(
    g: float, L_unit_cell: int = 2, chi_max: int = 100, J: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates ground state properties of the infinite Transverse Field Ising Model (TFIM) using DMRG.

    This tool adapts the provided TenPy script to run for a single value of the
    transverse field 'g' and returns the calculated physical observables.

    Args:
        g: The strength of the transverse magnetic field.
        L_unit_cell: The number of sites in the MPS unit cell for the infinite system. Defaults to 2.
        chi_max: The maximum bond dimension for the DMRG simulation. Defaults to 100.
        J: The Ising coupling strength. Defaults to 1.0.

    Returns:
        A dictionary containing the calculated ground state properties:
        - ground_state_energy_density: The energy per site.
        - entanglement_entropy: The entropy of the half-chain.
        - correlation_length: The correlation length of the ground state.
        - magnetization_z: The expectation value of the Pauli Z operator, <Sigma_z>.
        - correlation_xx: The <Sigma_x(0) Sigma_x(i)> correlation function as a list.
    """
    return run_dmrg_calculation(g, L_unit_cell, chi_max, J)


if __name__ == "__main__":
    mcp.run("stdio")
