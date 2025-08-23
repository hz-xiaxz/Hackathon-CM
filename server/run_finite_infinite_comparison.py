import numpy as np
import matplotlib.pyplot as plt

# Import the core calculation functions from the server files
from Ising_ED_server import run_ising_ed_calculation
from DMRG_server import run_dmrg_calculation

def plot_finite_infinite_comparison(L_values, ed_energies, dmrg_infinite_energy):
    """
    Visualizes the finite-size scaling comparison between ED and iDMRG.
    """
    inverse_L = 1.0 / np.array(L_values)
    
    plt.figure(figsize=(10, 6))
    
    # Plot ED energies vs 1/L
    plt.plot(inverse_L, ed_energies, 'o-', label='Finite Size ED (PBC)')
    
    # Plot iDMRG energy as a horizontal line
    plt.axhline(y=dmrg_infinite_energy, color='r', linestyle='--', label=f'Infinite DMRG (Thermodynamic Limit)')
    
    plt.xlabel('1 / System Size (1/L)')
    plt.ylabel('Ground State Energy Density')
    plt.title('Finite-Size Scaling: ED vs. Infinite DMRG')
    plt.legend()
    plt.grid(True)
    
    # Extrapolate to L=infinity (1/L=0)
    # A simple linear fit to the last few points
    if len(L_values) >= 2:
        fit = np.polyfit(inverse_L[-3:], ed_energies[-3:], 1)
        extrapolated_ed = fit[1]
        plt.plot(0, extrapolated_ed, 'gX', markersize=12, label=f'Extrapolated ED Energy: {extrapolated_ed:.8f}')
        print(f"Extrapolated ED energy at 1/L=0: {extrapolated_ed:.8f}")
        print(f"Infinite DMRG energy:             {dmrg_infinite_energy:.8f}")

    plt.legend()
    absolute_path = "/home/hzxiaxz/hackathon/server/finite_infinite_comparison.png"
    plt.savefig(absolute_path)
    print(f"Comparison plot saved to {absolute_path}")

def run_finite_infinite_comparison():
    """
    Runs the comparison between finite ED and infinite DMRG.
    """
    # --- Simulation Parameters ---
    L_values_ed = [4, 6, 8, 10, 12, 14]  # System sizes for ED
    J = 1.0
    g = 1.0  # Transverse field (critical point is interesting)
    
    # Parameters for the single iDMRG calculation
    dmrg_chi_max = 100
    dmrg_L_unit_cell = 2

    print("Starting Finite (ED) vs. Infinite (DMRG) comparison...")
    print(f"Parameters: J={J}, g={g}")

    # --- Run Finite Size ED ---
    ed_energies = []
    print("\n--- Running Finite Size ED Calculations ---")
    for L in L_values_ed:
        print(f"Running ED for L = {L}...")
        ed_energy = run_ising_ed_calculation(L=L, J=J, h=g)
        ed_energies.append(ed_energy)
        print(f"  ED Energy / site: {ed_energy:.8f}")

    # --- Run Infinite DMRG ---
    print("\n--- Running Infinite DMRG Calculation ---")
    dmrg_results = run_dmrg_calculation(
        g=g, L_unit_cell=dmrg_L_unit_cell, chi_max=dmrg_chi_max, J=J
    )
    dmrg_infinite_energy = dmrg_results["ground_state_energy_density"]
    print(f"  Infinite DMRG Energy / site: {dmrg_infinite_energy:.8f}")

    # --- Generate the Plot ---
    print("\nAll calculations finished. Generating plot...")
    plot_finite_infinite_comparison(L_values_ed, ed_energies, dmrg_infinite_energy)

if __name__ == "__main__":
    run_finite_infinite_comparison()
