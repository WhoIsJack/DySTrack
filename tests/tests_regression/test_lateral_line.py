# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Regression tests for lateral_line.py; ensures correct running of
            the masking pipeline for some established test data.
"""

import os
import pickle
import warnings

import pytest

from mate.pipelines import lateral_line


def test_analyze_image(capsys):
    """Regression test for lateral line pre-scan masking pipeline."""

    # DEV: Set this to True to generate new reference coords and stdout files
    # (which will overwrite the old) if the data or the function's behavior has
    # changed. This will force the test to fail, since generating a new
    # reference from the output and then checking against it would always pass.
    create_new_reference_outputs = False

    # DEV: Generate a plain text version of the outputs; does not do anything
    # in the test itself, but can be useful for debugging.
    create_plaintext_of_outputs = False

    # Config
    datadir = "./tests/testdata"
    prescan_fnames = [
        fn
        for fn in os.listdir(datadir)
        if fn.startswith("test1_") and "_prescan" in fn
    ]
    warns_8bit = [False, False, True]  # Whether 8bit conversion is expected
    coords_fpath = os.path.join(datadir, "test1_coords.pkl")
    stdout_fpath = os.path.join(datadir, "test1_stdout.pkl")

    # Run function over test data
    outputs = {}
    stdouts = {}
    for prescan_fname, w8bit in zip(prescan_fnames, warns_8bit):

        if w8bit:  # Check that expected 8bit conversion warning is emitted
            with pytest.warns(
                UserWarning,
                match="Image converted down to 8bit using min-max scaling!",
            ) as w:
                out = lateral_line.analyze_image(
                    os.path.join(datadir, prescan_fname),
                    channel=None,
                    show=False,
                    verbose=True,
                )

        else:  # Check that *no* 8bit conversion warning is emitted
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "error",
                    category=UserWarning,
                    message="Image converted down to 8bit using min-max scaling!",
                )
                out = lateral_line.analyze_image(
                    os.path.join(datadir, prescan_fname),
                    channel=None,
                    show=False,
                    verbose=True,
                )

        out = list(out)
        out[:3] = [f"{c:.4f}" for c in out[:3]]
        outputs[prescan_fname] = out
        stdouts[prescan_fname] = capsys.readouterr().out

    # Generate reference files
    if create_new_reference_outputs:
        with open(coords_fpath, "wb") as outfile:
            pickle.dump(outputs, outfile)
        with open(stdout_fpath, "wb") as outfile:
            pickle.dump(stdouts, outfile)

    # Generate plain text files
    if create_plaintext_of_outputs:
        with open(coords_fpath.replace(".pkl", ".txt"), "w") as outfile:
            for fn in outputs:
                outfile.write(
                    fn
                    + "\t"
                    + "\t".join([o.__repr__() for o in outputs[fn]])
                    + "\n"
                )
        with open(stdout_fpath.replace(".pkl", ".txt"), "w") as outfile:
            for fn in stdouts:
                outfile.write("### " + fn + "\n")
                outfile.write(stdouts[fn])
                outfile.write("\n\n")

    # Check outputs against reference
    with open(coords_fpath, "rb") as infile:
        ref_outputs = pickle.load(infile)
    for pf in prescan_fnames:
        assert outputs[pf] == ref_outputs[pf], "Mismatched output for " + pf

    # Check stdouts against reference
    with open(stdout_fpath, "rb") as infile:
        ref_stdouts = pickle.load(infile)
    for pf in prescan_fnames:
        assert stdouts[pf] == ref_stdouts[pf], "Mismatched stdout for " + pf

    # Ensure the test fails if any of the DEV mode flags were set to True
    assert (
        not create_new_reference_outputs
    ), "Cannot test outputs when create_new_reference_outputs is set to True; forcing test failure."
