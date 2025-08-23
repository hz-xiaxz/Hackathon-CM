"""Tuning through the phase transition of the transverse field Ising model.

This example uses DMRG to find the ground state of the transverse field Ising model for g=0.9.
It plots a few observables in the end.
"""
# Copyright (C) TeNPy Developers, Apache license

import numpy as np
from tenpy.models.tf_ising import TFIChain
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
import matplotlib.pyplot as plt


def run(gs):
    print("running for gs = ", gs)
    L = 2
    model_params = dict(L=L, J=1.0, g=gs[0], bc_MPS="infinite", conserve=None)
    chi = 100
    dmrg_params = {
        "trunc_params": {
            "chi_max": chi,
            "svd_min": 1.0e-10,
            "trunc_cut": None,
        },
        "update_env": 5,
        "start_env": 5,
        "max_E_err": 0.0001,
        "max_S_err": 0.0001,
        "max_sweeps": 100,
        "mixer": False,
    }

    M = TFIChain(model_params)
    psi = MPS.from_product_state(M.lat.mps_sites(), (["up", "down"] * L)[:L], M.lat.bc_MPS)

    engine = dmrg.TwoSiteDMRGEngine(psi, M, dmrg_params)
    np.set_printoptions(linewidth=120)

    corr_length = []
    fidelity = []
    Sz = []
    E = []
    S = []
    SxSx = []
    old_psi = None
    for g in gs:
        print("-" * 80)
        print("g =", g)
        print("-" * 80)
        model_params["g"] = g
        M = TFIChain(model_params)
        engine.init_env(model=M)  # (re)initialize DMRG environment with new model
        # this uses the result from the previous DMRG as first initial guess
        E0, psi = engine.run()
        E.append(E0)
        # psi is modified by engine.run() and now represents the ground state for the current `g`.
        S.append(psi.entanglement_entropy()[0])
        corr_length.append(psi.correlation_length(tol_ev0=1.0e-3))
        print("corr. length", corr_length[-1])
        Sz.append(psi.expectation_value("Sigmaz"))
        print("<Sigmaz>", Sz[-1])
        SxSx.append(psi.correlation_function("Sigmax", "Sigmax", [0], 20)[0, :])
        print("<Sigmax_0 Sigmax_i>", SxSx[-1])
        if old_psi is not None:
            fidelity.append(np.abs(old_psi.overlap(psi, understood_infinite=True)))
            print("fidelity", fidelity[-1])
        old_psi = psi.copy()
        dmrg_params["start_env"] = 0  # (some of) the parameters are read out again
    results = {
        "model_params": model_params,
        "dmrg_params": dmrg_params,
        "gs": gs,
        "corr_length": np.array(corr_length),
        "fidelity": np.array(fidelity),
        "Sz": np.array(Sz),
        "E": np.array(E),
        "S": np.array(S),
        "SxSx": np.array(SxSx),
        "eval_transfermatrix": np.exp(-1.0 / np.array(corr_length)),
    }
    return results



if __name__ == "__main__":
    g_val = 2.0 
    gs = [g_val]

    print(f"Starting DMRG simulation for a single g = {g_val}")
    results = run(gs)
