# GEMINI.md

## Project Overview

This project is a Python-based server for performing condensed matter physics calculations. It provides two main functionalities, each exposed as a separate server:

*   **DMRG Server (`DMRG_server.py`):** Utilizes the `tenpy` library to perform Density Matrix Renormalization Group (DMRG) calculations on the infinite Transverse Field Ising Model (TFIM). This is useful for finding ground state properties of the model.

### DMRG Server Notes

*   **LLM Documentation:** All functions, especially those exposed via `mcp.tool()`, have been thoroughly documented to enhance understanding for Large Language Models.
*   **Applicability:** The `DMRG_server.py` script is primarily designed and tested for transverse magnetic field (g) values less than 1.0, particularly away from the critical point g=1.0. Its accuracy and convergence behavior may vary for g >= 1.0.
*   **Ising ED Server (`Ising_ED_server.py`):** Employs the `quspin` library to perform exact diagonalization on the Ising chain. This is used to find the ground state energy of the Ising chain.

The servers are built using the `mcp` framework, which allows the physics calculations to be exposed as tools.

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

## Development Conventions

*   **Language:** Python 3.12
*   **Dependencies:** Managed with `uv` and `pyproject.toml`.
*   **Style:** The code uses type hints for function signatures and follows a procedural programming style.
*   **Framework:** The `mcp` framework is used to expose the physics calculations as tools.
