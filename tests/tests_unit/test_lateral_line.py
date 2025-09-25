# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 19:48:19 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Unit tests against `lateral_line.py`.
"""

import os
import warnings

import pytest

from mate.pipelines import lateral_line


def test_analyze_image_3D_success(capsys):

    # DEV: Set this to True to generate new reference coords and stdout files
    # (which will overwrite the old) if the data or the function's behavior has
    # changed. This will force the test to fail, since generating a new
    # reference from the output and then checking against it would always pass.
    create_new_reference_file = False

    # Targets
    testpath = r"./tests/testdata/"
    fnames = [
        "test-pllp_980_prescan.czi",  # ZEISS LSM980 .czi
        "test-pllp_NSPARC_prescan.tiff",  # Nikon AX .tiff
    ]

    # Expectations
    warns_8bit = [False, True]  # Whether 8bit conversion is expected
    reference_fpath = os.path.join(testpath, "test-pllp_refout.txt")

    # Run function over test data
    outputs = []
    for fname, w8bit in zip(fnames, warns_8bit):

        if w8bit:
            with pytest.warns(
                UserWarning,
                match="Image converted down to 8bit using min-max scaling!",
            ) as w:
                out = lateral_line.analyze_image(
                    os.path.join(testpath, fname),
                    channel=None,
                    show=False,
                    verbose=True,
                )

        else:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "error",
                    category=UserWarning,
                    message="Image converted down to 8bit using min-max scaling!",
                )
                out = lateral_line.analyze_image(
                    os.path.join(testpath, fname),
                    channel=None,
                    show=False,
                    verbose=True,
                )

        out = list(out)
        out[:3] = [f"{c:.4f}" for c in out[:3]]
        out[3:] = [v.__repr__() for v in out[3:]]

        outputs.append(f"\n# TESTFILE: {fname}")
        outputs.append("\n>> RETURN VALUES:")
        outputs.append(",".join(out))
        outputs.append("\n>> STDOUT:")
        outputs.append(capsys.readouterr().out)
    
    # Generate reference files
    if create_new_reference_file:
        with open(reference_fpath, "w") as outfile:
            outfile.write("\n".join(outputs))

    # Check outputs against reference
    with open(reference_fpath, "r") as infile:
        ref_outputs = infile.read()
    assert "\n".join(outputs) == ref_outputs

    # Ensure the test fails if any of the DEV mode flags were set to True
    assert (
        not create_new_reference_file
    ), "Generated new reference output file; forcing test failure."
