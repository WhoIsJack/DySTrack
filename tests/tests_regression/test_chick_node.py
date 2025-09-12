# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 23:23:41 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Regression tests for chick_node.py; ensures correct running of
            the masking pipeline for some established test data.
"""

import os
import pickle
import warnings

import pytest

from mate.pipelines import chick_node


def test_analyze_image(capsys):
    """Regression test for chick node pre-scan masking pipeline."""

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
        if fn.startswith("test-chicknode") and ".tif" in fn
    ]
    # warns_8bit = [True] * len(prescan_fnames) # 8bit conversion expected?
    warns_8bit = [False] * len(prescan_fnames)  # 8bit conversion expected?
    coords_fpath = os.path.join(datadir, "test-chicknode_coords.pkl")
    stdout_fpath = os.path.join(datadir, "test-chicknode_stdout.pkl")

    # Run function over test data
    outputs = {}
    stdouts = {}
    for prescan_fname, w8bit in zip(prescan_fnames, warns_8bit):

        if w8bit:  # Check that expected 8bit conversion warning is emitted
            with pytest.warns(
                UserWarning,
                match="Image converted down to 8bit using min-max scaling!",
            ) as w:
                out = chick_node.analyze_image(
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
                out = chick_node.analyze_image(
                    os.path.join(datadir, prescan_fname),
                    channel=None,
                    show=False,
                    verbose=True,
                )

        out = list(out)
        # out[:3] = [f"{c:.4f}" for c in out[:3]]
        out = [f"{c:.4f}" for c in out[:3]]
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
