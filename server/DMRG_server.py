# Copyright (C) TeNPy Developers, Apache license

# Note: This script is primarily designed and tested for transverse magnetic field (g) values less than 1.0,

import numpy as np
from tenpy.models.tf_ising import TFIChain
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
import matplotlib.pyplot as plt
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Literal

# 1. Create the MCP server instance
mcp = FastMCP("TenPy TFIM Analysis Server")


def run_dmrg_calculation(
    g: float, L_unit_cell: int, chi_max: int, J: float
) -> Dict[str, Any]:
    """
    Performs the core infinite Density Matrix Renormalization Group (iDMRG) calculation
    for an infinite Transverse Field Ising Model (TFIM).
    Note: This function is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field.
        L_unit_cell: The length of the unit cell used in the iDMRG calculation.
        chi_max: The maximum bond dimension allowed in the MPS.
        J: The Ising coupling strength.

    Returns:
        A dictionary containing the calculation results, including:
        - "parameters": A dictionary of input parameters.
        - "ground_state_energy_density": The calculated ground state energy per site.
        - "entanglement_entropy": The entanglement entropy of the ground state.
        - "correlation_length": The correlation length of the ground state.
        - "magnetization_z": The average magnetization in the z-direction.
        - "correlation_xx": A list of spin-spin correlations in the x-direction.
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

    M = TFIChain(model_params)
    initial_state = ["down"] * L_unit_cell

    psi = MPS.from_product_state(M.lat.mps_sites(), initial_state, M.lat.bc_MPS)

    engine = dmrg.TwoSiteDMRGEngine(psi, M, dmrg_params)
    E0, psi = engine.run()

    energy_density = E0 / L_unit_cell
    entanglement_entropy = psi.entanglement_entropy()[0]
    correlation_length = psi.correlation_length(tol_ev0=1.0e-3)
    magnetization_z = np.mean(psi.expectation_value("Sigmaz"))
    correlation_xx = psi.correlation_function("Sigmax", "Sigmax", [0], 20)[0, :]

    print("DMRG calculation finished successfully.")

    results = {
        "parameters": {"g": g, "L_unit_cell": L_unit_cell, "J": J, "chi_max": chi_max},
        "ground_state_energy_density": energy_density,
        "entanglement_entropy": entanglement_entropy,
        "correlation_length": correlation_length,
        "magnetization_z": magnetization_z,
        "correlation_xx": correlation_xx.tolist(),
    }

    return results


def plot_convergence_data(results: Dict[str, Any], param_name: str) -> str:
    """
    Generates and saves a plot of the convergence data.

    Args:
        results (dict): The dictionary returned by a convergence analysis function.
        param_name (str): The name of the parameter that was varied (e.g., 'L' or 'chi').

    Returns:
        str: The absolute file path of the generated plot image.
    """
    param_values = results[f"{param_name}_values"]
    energy_values = results["ground_state_energy_density"]

    plt.figure(figsize=(10, 6))
    plt.plot(param_values, energy_values, marker="o", linestyle="-")
    plt.xlabel(f"Parameter: {param_name}")
    plt.ylabel("Ground State Energy Density")
    plt.title(f"DMRG Convergence: Energy vs. {param_name}")
    plt.grid(True)

    plot_filename = f"dmrg_convergence_{param_name}.png"
    absolute_path = f"/home/hzxiaxz/hackathon/server/{plot_filename}"
    plt.savefig(absolute_path)
    print(f"Convergence plot saved to {absolute_path}")

    return absolute_path


def analyze_convergence_with_L(
    g: float, L_values: List[int], chi_max: int, J: float, threshold: float
) -> Dict[str, Any]:
    """
    Helper function to analyze the convergence of iDMRG ground state energy with respect to the unit cell size.
    It iteratively calls `run_dmrg_calculation` for different unit cell sizes.
    Note: This function is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field.
        L_values: A list of unit cell lengths to test for convergence.
        chi_max: The maximum bond dimension allowed in the MPS for each DMRG calculation.
        J: The Ising coupling strength.
        threshold: The energy difference threshold to determine convergence.

    Returns:
        A dictionary containing the L_unit_cell values tested, corresponding ground state energy densities,
        and a boolean indicating if convergence was reached within the given threshold.
    """
    results_by_L = {
        "L_unit_cell_values": [],
        "ground_state_energy_density": [],
        "convergence_reached": False,
    }

    last_energy = None

    for L_unit_cell in L_values:
        result = run_dmrg_calculation(
            g=g, L_unit_cell=L_unit_cell, chi_max=chi_max, J=J
        )
        energy = result["ground_state_energy_density"]

        results_by_L["L_unit_cell_values"].append(L_unit_cell)
        results_by_L["ground_state_energy_density"].append(energy)

        if last_energy is not None:
            if abs(energy - last_energy) < threshold:
                results_by_L["convergence_reached"] = True
                print(
                    f"Convergence reached at L_unit_cell={L_unit_cell} with energy difference {abs(energy - last_energy)}"
                )
                break

        last_energy = energy

    return results_by_L


@mcp.tool()
def analyze_L_convergence(
    g: float,
    L_values_str: str | None = None,
    chi_max: int = 500,
    J: float = 1.0,
    threshold: float = 1e-5,
    create_plot: bool = False,
) -> Dict[str, Any]:
    """
    MCP Tool: Analyzes the convergence of iDMRG energy with respect to the unit cell size.
    This tool is exposed via the MCP server for external consumption.
    Note: This tool is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field (h in ED).
        L_values_str: Comma-separated string of system sizes to compare.
        chi_max: The bond dimension to use for the DMRG calculations.
        J: The Ising coupling strength.
        threshold: The energy difference threshold for convergence.
        create_plot: Whether to generate a plot of the results.
    Returns:
        A dictionary containing the convergence results and optionally the plot file path.

        The "plot_file_path" key will contain the absolute path to the saved plot image if `create_plot` is True. Please render as image

    """
    if L_values_str:
        L_values = [int(L.strip()) for L in L_values_str.split(",")]
    else:
        L_values = [2, 4, 6, 8, 10]

    if chi_max is None:
        largest_L = max(L_values)
        print(
            f"chi_max not provided. Running convergence for largest L_unit_cell={largest_L} to find a suitable value."
        )
        convergence_results = analyze_chi_convergence(g, largest_L, None, J)
        chi_max = convergence_results["chi_values"][-1]
        print(
            f"Convergence analysis complete. Using chi_max = {chi_max} for all L_unit_cell values."
        )

    results = analyze_convergence_with_L(g, L_values, chi_max, J, threshold)

    if create_plot:
        plot_path = plot_convergence_data(results, "L_unit_cell")
        results["plot_file_path"] = plot_path

    return results


def analyze_convergence_with_chi(
    g: float, L_unit_cell: int, chi_values: List[int], J: float, threshold: float
) -> Dict[str, Any]:
    """
    Helper function to analyze the convergence of iDMRG ground state energy with respect to the bond dimension.
    It iteratively calls `run_dmrg_calculation` for different bond dimensions.
    Note: This function is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field.
        L_unit_cell: The length of the unit cell used in the iDMRG calculation.
        chi_values: A list of bond dimensions to test for convergence.
        J: The Ising coupling strength.
        threshold: The energy difference threshold to determine convergence.

    Returns:
        A dictionary containing the chi_values tested, corresponding ground state energy densities,
        and a boolean indicating if convergence was reached within the given threshold.
    """
    results_by_chi = {
        "chi_values": [],
        "ground_state_energy_density": [],
        "convergence_reached": False,
    }

    last_energy = None

    for chi in chi_values:
        result = run_dmrg_calculation(g=g, L_unit_cell=L_unit_cell, chi_max=chi, J=J)
        energy = result["ground_state_energy_density"]

        results_by_chi["chi_values"].append(chi)
        results_by_chi["ground_state_energy_density"].append(energy)

        if last_energy is not None:
            if abs(energy - last_energy) < threshold:
                results_by_chi["convergence_reached"] = True
                print(
                    f"Convergence reached at chi={chi} with energy difference {abs(energy - last_energy)}"
                )
                break

        last_energy = energy

    return results_by_chi


@mcp.tool()
def analyze_chi_convergence(
    g: float,
    L_unit_cell: int,
    chi_values_str: str | None = None,
    J: float = 1.0,
    threshold: float = 1e-6,
    create_plot: bool = False,
) -> Dict[str, Any]:
    """
    MCP Tool: Analyzes the convergence of iDMRG energy with respect to the bond dimension.
    This tool is exposed via the MCP server for external consumption.
    Note: This tool is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field.
        L_unit_cell: The length of the unit cell used in the iDMRG calculation.
        chi_values_str: Comma-separated string of bond dimensions to test.
        J: The Ising coupling strength.
        threshold: The energy difference threshold for convergence.
        create_plot: Whether to generate a plot of the results.

    Returns:
        A dictionary containing the convergence results and optionally the plot file path.

        The "plot_file_path" key will contain the absolute path to the saved plot image if `create_plot` is True. Please render as image.
    """
    if chi_values_str:
        chi_values = [int(chi.strip()) for chi in chi_values_str.split(",")]
    else:
        base_chi = [50, 80, 110, 140, 170]
        if L_unit_cell >= 4:
            base_chi = [c + 20 for c in base_chi]

        if abs(g - J) < 0.1:
            chi_values = [c * 2 for c in base_chi]
        elif abs(g - J) < 0.4:
            chi_values = [int(c * 1.5) for c in base_chi]
        else:
            chi_values = base_chi

        chi_values = sorted(list(set(chi_values)))

    results = analyze_convergence_with_chi(g, L_unit_cell, chi_values, J, threshold)

    if create_plot:
        plot_path = plot_convergence_data(results, "chi")
        results["plot_file_path"] = plot_path

    return results


@mcp.tool()
def analyze_tfim_with_dmrg(
    g: float, L_unit_cell: int = 2, chi_max: int | None = None, J: float = 1.0
) -> Dict[str, Any]:
    """
    MCP Tool: Calculates ground state properties of the infinite TFIM using DMRG.
    This tool is exposed via the MCP server for external consumption.
    Note: This tool is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    Args:
        g: The strength of the transverse magnetic field.
        L_unit_cell: The length of the unit cell used in the iDMRG calculation.
        chi_max: The maximum bond dimension allowed in the MPS. If None, a convergence analysis will be performed to find a suitable value.
        J: The Ising coupling strength.

    Returns:
        A dictionary containing the calculation results, including:
        - "parameters": A dictionary of input parameters.
        - "ground_state_energy_density": The calculated ground state energy per site.
        - "entanglement_entropy": The entanglement entropy of the ground state.
        - "correlation_length": The correlation length of the ground state.
        - "magnetization_z": The average magnetization in the z-direction.
        - "correlation_xx": A list of spin-spin correlations in the x-direction.
    """
    if chi_max is not None:
        return run_dmrg_calculation(g, L_unit_cell, chi_max, J)
    else:
        print(
            "chi_max not provided. Running convergence analysis to find a suitable value."
        )
        convergence_results = analyze_chi_convergence(g, L_unit_cell, None, J)

        final_chi = convergence_results["chi_values"][-1]
        print(f"Convergence analysis complete. Using final chi_max = {final_chi}")
        return run_dmrg_calculation(g, L_unit_cell, final_chi, J)


if __name__ == "__main__":
    mcp.run("stdio")
