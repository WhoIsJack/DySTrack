Using DySTrack on the Zeiss LSM980 (ZEN Blue)
=============================================

1. Open command prompt
-------------------------

2. Start DySTrack environment and change direction to run folder
------------------------------------------------------

.. code-block:: python

    conda activate DySTrack
    D:
    cd D:\\Users\\Your Name\\DySTrack/run

3. Start monitoring the experiment folder
--------------------------------

.. code-block:: python

    python run_lateral_line.py D:\\Your Name\\....

4. Make job ZEN experiment settings (.czexp file)
--------------------------------

.. note::
    **Important:**

    - Tick ``Tiles`` and ``AutoSave``
    - Focus Strategy *must* be set to ``Use Z Values/ Focus Surface Defined in Tiles``
    - Only need to set 1 position (it is updated by the macro)
    - Z-stack is a range around centre and must have the same centre as prescan
    - Save 

5. Make prescan ZEN experiment settings (.czexp file)
-----------------------------------------------------

.. note::
    **Important:**

    - Tick ``Tiles`` and ``AutoSave``
    - Focus Strategy *must* be set to ``Use Z Values/ Focus Surface Defined in Tiles``
    - Only need to set 1 position (it is updated by the macro)
    - Z-stack is a range around centre and must have the same centre as job
    - Set all positions in tiles (F10 to add position)
    - Save 

6. Open macro editor in ZEN Blue and DySTrack macro
--------------------------------------------------------

7. Change user inputs and run macro
-----------------------------------

- **prescan_name**: exact name from .czexp menu.
- **job_name**: exact name from .czexp menu.
- **output_folder**: must be the same as the one you’re monitoring.
- **max_iterations**: number of loops.
- **interval_min**: interval between timepoints in minutes.

.. note::
    **Tip:**

    - If you stop your current run but need to revert your positions set in the prescan, click **Reload** in the prescan menu

Once everything is set up, press **Run**

8. Troubleshooting
------------------

- To stop the macro press **Stop** in the macro editor.
- Then close the macro editor and reopen it.
- If it doesn’t work, perform a full system restart.