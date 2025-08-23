# Physics Calculation Servers

This project provides Python-based servers for performing condensed matter physics calculations. It includes two main functionalities, each exposed as a separate server.

## Servers

### Ising ED Server (`Ising_ED_server.py`)

This server uses the `quspin` library to perform exact diagonalization on the Ising chain to find the ground state energy.

#### Tools

*   **`Ising_ED(L: int, J: float, h: float) -> float`**

    Calculates the ground state energy of the Transverse Field Ising Model (TFIM).

    *   **Arguments:**
        *   `L`: The length of the Ising chain. Note: Values of `L > 12` may cause the server to use a large amount of memory and are not recommended. The tool will raise an error for `L > 12`.
        *   `J`: The strength of the `zz` interaction.
        *   `h`: The strength of the transverse magnetic field in the `x` direction.
    *   **Returns:** The ground state energy per site.

### DMRG Server (`DMRG_server.py`)

This server utilizes the `tenpy` library to perform Density Matrix Renormalization Group (DMRG) calculations on the infinite Transverse Field Ising Model (TFIM). This is useful for finding ground state properties of the model. The server is named "TenPy TFIM Analysis Server".

#### Tools

*   **`analyze_tfim_with_dmrg(g: float, L_unit_cell: int = 2, chi_max: int | None = None, J: float = 1.0) -> Dict[str, Any]`**

    Calculates various ground state properties of the infinite TFIM for a single set of parameters.
    Note: This tool is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    *   **Arguments:**
        *   `g`: The strength of the transverse magnetic field.
        *   `L_unit_cell`: The number of sites in the MPS unit cell (default: 2).
        *   `chi_max`: The maximum bond dimension for the DMRG simulation. If `None`, a convergence analysis will be performed to find a suitable value.
        *   `J`: The Ising coupling strength (default: 1.0).
    *   **Returns:** A dictionary with the calculated ground state properties.

*   **`analyze_L_convergence(g: float, L_values_str: str, chi_max: int = 100, J: float = 1.0, threshold: float = 1e-5, create_plot: bool = False) -> Dict[str, List[Any]]`**

    Analyzes the convergence of the ground state energy with respect to the unit cell size `L`.
    Note: This tool is primarily designed and tested for transverse magnetic field (g) values less than 1.0,
    especially away from the critical point g=1.0.

    *   **Arguments:**
        *   `g`: The strength of the transverse magnetic field.
        *   `L_values_str`: A comma-separated string of unit cell sizes to test (e.g., "2,4,6,8").
        *   `chi_max`: The maximum bond dimension (default: 100).
        *   `J`: The Ising coupling strength (default: 1.0).
        *   `threshold`: The energy difference threshold for convergence (default: 1e-5).
        *   `create_plot`: Whether to generate a plot of the results (default: False).
    *   **Returns:** A dictionary containing the tested `L` values and the corresponding ground state energy densities. If `create_plot` is True, it also returns the path to the generated plot image.

*   **`analyze_chi_convergence(g: float, L_unit_cell: int, chi_values_str: str, J: float = 1.0) -> Dict[str, List[Any]]`**

    Analyzes the convergence of the ground state energy with respect to the bond dimension `chi`.

    *   **Arguments:**
        *   `g`: The strength of the transverse magnetic field.
        *   `L_unit_cell`: The number of sites in the MPS unit cell.
        *   `chi_values_str`: A comma-separated string of bond dimensions to test (e.g., "50,100,150").
        *   `J`: The Ising coupling strength (default: 1.0).
    *   **Returns:** A dictionary containing the tested `chi` values and the corresponding ground state energy densities.

## Building and Running

The project is written in Python and its dependencies are managed by `uv` and defined in `pyproject.toml`.

### Prerequisites

*   Python 3.12
*   `uv` package manager

### Installation

To install the dependencies, run the following command from the project root directory:

```bash
uv pip install -r requirements.txt
```

### Running the Servers

Each server can be run as a standalone script.

**To run the DMRG server:**

```bash
uv run python DMRG_server.py
```

**To run the Ising ED server:**

```bash
uv run python Ising_ED_server.py
```

The servers will start and listen for requests on standard I/O.
