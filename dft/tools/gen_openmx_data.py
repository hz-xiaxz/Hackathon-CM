from ase.io import read
from ase import Atoms
import numpy as np

import os

element_initial_charges_map = {"C": 2.0,}


def gen_openmx_input(
    poscar_path: str,
    output_dir: str,
):
    atoms = read(poscar_path, format="vasp")
    cell = atoms.cell[:]
    chemical_symbols = atoms.get_chemical_symbols()
    species_type = set(chemical_symbols)
    n_species = len(species_type)
    n_atoms = len(atoms)

    openmx_in_str = f"""# 
# File name and path
#

System.CurrrentDirectory          ./
System.Name                       openmx
level.of.stdout                   1
level.of.fileout                  1
DATA.PATH                         /public/home/chenzz/envs/openmx3.9/DFT_DATA19

#
# Defination of Atomic Species
#

"""
    openmx_in_str += f"""Species.Number                    {n_species}
<Definition.of.Atomic.Species
 C     C6.0-s2p2d1       C_PBE19
Definition.of.Atomic.Species>

#
# Structure
#

Atoms.Number                      {n_atoms}
Atoms.SpeciesAndCoordinates.Unit  FRAC
<Atoms.SpeciesAndCoordinates"""
    for i, p in enumerate(atoms.get_scaled_positions()):
        element = chemical_symbols[i]
        openmx_in_str += f"\n   {i+1}  {element}  {p[0]}  {p[1]}  {p[2]} {element_initial_charges_map[element]} {element_initial_charges_map[element]} 0.0  0.0  0.0  0.0  0  off"

    openmx_in_str += f"""
Atoms.SpeciesAndCoordinates>
Atoms.UnitVectors.Unit            Ang
<Atoms.UnitVectors
 {cell[0,0]} {cell[0,1]} {cell[0,2]}
 {cell[1,0]} {cell[1,1]} {cell[1,2]}
 {cell[2,0]} {cell[2,1]} {cell[2,2]}
Atoms.UnitVectors>

#
# SCF Related Parameters
#

scf.XcType                        GGA-PBE
scf.ElectronicTemperature         300.0
scf.energycutoff                  300
scf.maxIter                       1000
scf.EigenvalueSolver              Band
#scf.Ngrid                        _____________
scf.Kgrid                            9    9    1
#scf.Generation.Kpoint             MP
#scf.lapack.dste                  _____________
scf.partialCoreCorrection         ON  


## Mixing parameters related to RMM-DIIS method ##
scf.Mixing.Type           RMM-DIIS     # Simple|Rmm-Diis|Gr-Pulay|Kerker|Rmm-Diisk
scf.Init.Mixing.Weight     0.0010      # default=0.30 
scf.Min.Mixing.Weight      0.0001      # default=0.001 
scf.Max.Mixing.Weight      0.1000      # default=0.40 
scf.Mixing.History          7          # default=5
scf.Mixing.StartPulay      25          # default=6
scf.criterion             1.0e-9       # default=1.0e-6 (Hartree) 

## 1DFFT ##
1DFFT.NumGridK                    900
1DFFT.NumGridR                    900
1DFFT.EnergyCutoff                3600.0
## Orbital Optimization ## (Blank)


## Others ##
scf.ProExpn.VNA                   Off
#scf.Electric.Field               _____________
#scf.system.charge                _____________
## Density of state ##
#Dos.fileout                      _____________
#Dos.Erange                       _____________
#Dos.Kgrd                         _____________

#
# Geometry Optimization
#

MD.Type                           Nomd
#MD.maxIter                       _____________
#MD.Opt.criterion                 _____________


#
# Iterface for developers
#

HS.fileout                        On
"""
    openmx_file_name = os.path.join(output_dir, "openmx_in.dat")
    with open(openmx_file_name, "w") as f:
        f.write(openmx_in_str)

