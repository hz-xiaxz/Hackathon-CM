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
    g: float, L: int, chi_max: int, J: float, boundary_condition: str
) -> Dict[str, Any]:
    """
    Performs the core DMRG calculation.
    """
    print(f"Running DMRG for TFIM with g={g}, J={J}, chi_max={chi_max}, L={L}, bc={boundary_condition}...")

    if boundary_condition == 'infinite':
        bc_mps = 'infinite'
    elif boundary_condition == 'open':
        bc_mps = 'finite'
    else:
        raise ValueError(f"Unsupported boundary condition: {boundary_condition}")

    model_params = dict(L=L, J=J, g=g, bc_MPS=bc_mps, conserve=None)

    dmrg_params = {
        "trunc_params": {"chi_max": chi_max, "svd_min": 1.0e-10},
        "update_env": 5,
        "start_env": 5,
        "max_E_err": 1.0e-4,
        "max_S_err": 1.0e-4,
        "max_sweeps": 100,
        "mixer": False,
    }

    M = TFIChain(model_params)
    initial_state = (["up", "down"] * L)[:L]
    psi = MPS.from_product_state(M.lat.mps_sites(), initial_state, M.lat.bc_MPS)
    np.set_printoptions(linewidth=120)

    engine = dmrg.TwoSiteDMRGEngine(psi, M, dmrg_params)
    E0, psi = engine.run()

    energy_density = E0 / L

    entanglement_entropy = psi.entanglement_entropy()
    if boundary_condition == 'open' and len(entanglement_entropy) > 0:
        entanglement_entropy = entanglement_entropy[len(entanglement_entropy)//2]
    elif len(entanglement_entropy) > 0:
        entanglement_entropy = entanglement_entropy[0]
    else:
        entanglement_entropy = 0.0

    correlation_length = psi.correlation_length(tol_ev0=1.0e-3)
    magnetization_z = np.mean(psi.expectation_value("Sigmaz"))
    
    max_corr_dist = 20
    if boundary_condition == 'open':
        max_corr_dist = min(20, L - 1)
    
    if max_corr_dist > 0:
        correlation_xx = psi.correlation_function("Sigmax", "Sigmax", [0], max_corr_dist)[0, :]
        correlation_xx = correlation_xx.tolist()
    else:
        correlation_xx = []


    print("DMRG calculation finished successfully.")

    results = {
        "parameters": {"g": g, "L": L, "J": J, "chi_max": chi_max, "boundary_condition": boundary_condition},
        "ground_state_energy_density": energy_density,
        "entanglement_entropy": entanglement_entropy,
        "correlation_length": correlation_length,
        "magnetization_z": magnetization_z,
        "correlation_xx": correlation_xx,
    }

    return results


def analyze_convergence_with_L(
    g: float, L_values: List[int], chi_max: int, J: float, threshold: float, boundary_condition: str
) -> Dict[str, List[Any]]:
    """
    Analyzes the convergence of DMRG ground state energy with respect to the size L.
    Stops when the change in energy is below the threshold.
    """
    results_by_L = {
        "L_values": [],
        "ground_state_energy_density": [],
        "convergence_reached": False,
    }
    
    last_energy = None

    for L in L_values:
        result = run_dmrg_calculation(g=g, L=L, chi_max=chi_max, J=J, boundary_condition=boundary_condition)
        energy = result["ground_state_energy_density"]
        
        results_by_L["L_values"].append(L)
        results_by_L["ground_state_energy_density"].append(energy)

        if last_energy is not None:
            if abs(energy - last_energy) < threshold:
                results_by_L["convergence_reached"] = True
                print(f"Convergence reached at L={L} with energy difference {abs(energy - last_energy)}")
                break
        
        last_energy = energy

    return results_by_L


@mcp.tool()
def analyze_L_convergence(
    g: float, L_values_str: str | None = None, chi_max: int | None = None, J: float = 1.0, threshold: float = 1e-5,
    boundary_condition: str = 'open'
) -> Dict[str, List[Any]]:
    """
    Analyzes the convergence of DMRG ground state energy with respect to the size L.
    Note: A boundary condition ('open' or 'infinite') must be specified for the DMRG calculation.

    Args:
        g: The strength of the transverse magnetic field.
        L_values_str: Optional. A comma-separated string of sizes to test (e.g., "10,20,30").
                      If not provided, a default list is used.
        chi_max: Optional. The maximum bond dimension. If not provided, it's determined
                 automatically by running convergence analysis for the largest L.
        J: The Ising coupling strength. Defaults to 1.0.
        threshold: The convergence threshold for the energy difference. Defaults to 1e-5.
        boundary_condition: The boundary condition, 'open' or 'infinite'. Defaults to 'open'.

    Returns:
        A dictionary with results for each L, and whether convergence was reached.
    """
    if boundary_condition not in ['open', 'infinite']:
        raise ValueError("boundary_condition must be 'open' or 'infinite'")
    
    if L_values_str:
        L_values = [int(L.strip()) for L in L_values_str.split(',')]
    else:
        if boundary_condition == 'open':
            L_values = [10, 20, 30, 40, 50]
        else: # infinite
            L_values = [2, 4, 6, 8, 10]

    if chi_max is None:
        largest_L = max(L_values)
        print(f"chi_max not provided. Running convergence analysis for largest L={largest_L} to find a suitable value.")
        convergence_results = analyze_chi_convergence(g, largest_L, None, J, boundary_condition)
        chi_max = convergence_results["chi_values"][-1]
        print(f"Convergence analysis complete. Using chi_max = {chi_max} for all L values.")

    return analyze_convergence_with_L(g, L_values, chi_max, J, threshold, boundary_condition)


def analyze_convergence_with_chi(
    g: float, L: int, chi_values: List[int], J: float, boundary_condition: str, threshold: float
) -> Dict[str, List[Any]]:
    """
    Analyzes the convergence of DMRG ground state energy with respect to the bond dimension chi.
    Stops when the change in energy is below the threshold.
    """
    results_by_chi = {
        "chi_values": [],
        "ground_state_energy_density": [],
        "convergence_reached": False,
    }
    
    last_energy = None

    for chi in chi_values:
        result = run_dmrg_calculation(g=g, L=L, chi_max=chi, J=J, boundary_condition=boundary_condition)
        energy = result["ground_state_energy_density"]
        
        results_by_chi["chi_values"].append(chi)
        results_by_chi["ground_state_energy_density"].append(energy)

        if last_energy is not None:
            if abs(energy - last_energy) < threshold:
                results_by_chi["convergence_reached"] = True
                print(f"Convergence reached at chi={chi} with energy difference {abs(energy - last_energy)}")
                break
        
        last_energy = energy

    return results_by_chi


@mcp.tool()
def analyze_chi_convergence(
    g: float, L: int, chi_values_str: str | None = None, J: float = 1.0, boundary_condition: str = 'open',
    threshold: float = 1e-6
) -> Dict[str, List[Any]]:
    """
    Analyzes the convergence of DMRG ground state energy with respect to the bond dimension chi.
    Note: A boundary condition ('open' or 'infinite') must be specified for the DMRG calculation.

    Args:
        g: The strength of the transverse magnetic field.
        L: The number of sites. For 'open' bc, this is the total length.
           For 'infinite' bc, this is the unit cell size.
        chi_values_str: Optional. A comma-separated string of bond dimensions to test.
                        If not provided, a default set of values is used.
        J: The Ising coupling strength. Defaults to 1.0.
        boundary_condition: The boundary condition, 'open' or 'infinite'. Defaults to 'open'.
        threshold: The convergence threshold for the energy difference. Defaults to 1e-6.

    Returns:
        A dictionary with results for each chi, and whether convergence was reached.
    """
    if boundary_condition not in ['open', 'infinite']:
        raise ValueError("boundary_condition must be 'open' or 'infinite'")

    if chi_values_str:
        chi_values = [int(chi.strip()) for chi in chi_values_str.split(',')]
    else:
        base_chi = [20, 40, 60, 80, 100]
        if L >= 20 and boundary_condition == 'open':
            base_chi = [c + 20 for c in base_chi]
        
        if abs(g - J) < 0.1:
            chi_values = [c * 2 for c in base_chi]
        elif abs(g - J) < 0.4:
            chi_values = [int(c * 1.5) for c in base_chi]
        else:
            chi_values = base_chi
        
        chi_values = sorted(list(set(chi_values)))

    return analyze_convergence_with_chi(g, L, chi_values, J, boundary_condition, threshold)


@mcp.tool()
def analyze_tfim_with_dmrg(
    g: float, L: int = 10, chi_max: int | None = None, J: float = 1.0, boundary_condition: str = 'open'
) -> Dict[str, Any]:
    """
    Calculates ground state properties of the TFIM using DMRG.
    Note: A boundary condition ('open' or 'infinite') must be specified for the DMRG calculation.

    Args:
        g: The strength of the transverse magnetic field.
        L: The number of sites. For 'open' bc, this is the total length.
           For 'infinite' bc, this is the unit cell size. Defaults to 10.
        chi_max: Optional. The maximum bond dimension. If not provided, the tool will
                 automatically determine a suitable bond dimension by checking for convergence.
        J: The Ising coupling strength. Defaults to 1.0.
        boundary_condition: The boundary condition, 'open' or 'infinite'. Defaults to 'open'.

    Returns:
        A dictionary containing the calculated ground state properties.
    """
    if boundary_condition not in ['open', 'infinite']:
        raise ValueError("boundary_condition must be 'open' or 'infinite'")

    if chi_max is not None:
        return run_dmrg_calculation(g, L, chi_max, J, boundary_condition)
    else:
        print("chi_max not provided. Running convergence analysis to find a suitable value.")
        convergence_results = analyze_chi_convergence(g, L, None, J, boundary_condition)
        
        final_chi = convergence_results["chi_values"][-1]
        print(f"Convergence analysis complete. Using final chi_max = {final_chi}")
        return run_dmrg_calculation(g, L, final_chi, J, boundary_condition)


if __name__ == "__main__":
    mcp.run("stdio")
