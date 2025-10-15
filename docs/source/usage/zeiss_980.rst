DySTrack on the Zeiss LSM980 (ZEN Blue)
=======================================


.. admonition:: tl;dr
    :class: note

    If you've done this many times before and just need a quick reminder:

    #. Create target dir

    #. Start DySTrack manager

       .. code-block:: batch
        
           conda activate dystrack
           python <path-to-config-file.py> <path-to-target-dir> [optional arguments]

    #. Configure prescan and main scan experiment settings (``.czexp`` files)

    #. Open macro editor and adjust user inputs

    #. Double-check that everything is ready, then launch

    #. Ensure everything is running correctly



Before you start
----------------

.. include:: _includes/generic_before_you_start_info.rst



Part 1: Start the DySTrack manager
----------------------------------

.. include:: _includes/start_dystrack_manager_instructions.rst


Part 2: Configure experiment settings
-------------------------------------

The microscope and sample must be ready for this part.


1. **Configure the main scan settings and save them as a** ``.czexp`` **file**
   
   The main scan produces the actual data of interest for the experiment.
   
   It is usually a high-resolution, high-quality configuration using high pixel
   densities, multiple channels, and either AiryScan (8y mode) or confocal with 
   averaging optimized for SNR. Use high/optimal z-resolution for stacks.

   .. admonition:: Important
       :class: important
       
       * Always tick ``Tiles`` and ``AutoSave``
       * The Focus Strategy *must* be set to 
         ``Use Z Values / Focus Surface Defined in Tiles``
       * Z-stacks **must** be a range around the center and have the same 
         center as the prescan.
       * Only set one position in tiles (F10 to add); this will be updated by
         the macro

   Save the settings as a ``.czexp`` file.


2. **Configure the prescan settings and save them as a** ``.czexp`` **file**

   .. admonition:: Important
       :class: important
       
       Unlike for the main scan, do **not** use AiryScan for the prescan.

   The prescan is used for DySTrack to find coordinates.
   
   To create a suitable prescan configuration, start with the main scan (unless
   it is AiryScan) and trade off resolution and SNR for speed to the greatest 
   extent allowed by the image analysis pipeline. Remove any averaging, 
   substantially reduce pixel density, use only a single channel, and trade off 
   laser power for gain.
   
   Use a (very) low z-resolution for the prescan and include 15-30% spare space 
   outside your sample at the top and bottom (how much is needed depends on the 
   sample and analysis pipeline).

   .. admonition:: Important
       :class: important
       
       * Always tick ``Tiles`` and ``AutoSave``
       * The Focus Strategy *must* be set to 
         ``Use Z Values / Focus Surface Defined in Tiles``
       * Z-stacks **must** be a range around the center and have the same 
         center as the main scan.
       * Set all desired sample positions in tiles (F10 to add position)

   Save the setting as another ``.czexp`` file.


Part 3: Configure the ZEN Blue macro
------------------------------------

1. **Open the ZEN Blue macro editor**

   .. image:: ../images/zeiss_980/start_macro.png
      :alt: Opening Macro Editor in ZEN Blue
      :width: 60%

   If this option is not available, your ZEN Blue version is lacking the macro
   module. Speak to an expert user or facility staff, and/or see
   :doc:`Installation</intro/installation>`.


2. **Open the DySTrack macro**

   .. image:: ../images/zeiss_980/macro_editor_open.png
      :alt: Macro Editor in ZEN Blue
      :width: 80% 

   ``LSM980_ZENBlue_macro.py`` in the ``macros`` folder.


3. **Configure the settings in the** ``USER INPUT`` **section**

   * ``prescan_name``: name of prescan experiment settings from ``.czexp`` menu
   * ``job_name``: name of main scan experiment settings from ``.czexp`` menu
   * ``output_folder``: the target directory monitored by the DySTrack manager
   * ``max_iterations``: number of time points
   * ``interval_min``: interval between time points in minutes

     For the interval, calculate sufficient time for prescan, image analysis 
     (usually quick), and main scan (usually the bottleneck). Multiply by the 
     number of positions when using multi-positioning and add a bit of buffer
     time.

   .. admonition:: Tip
       :class: tip

       The macro works by taking all the initial positions set in the prescan 
       into its memory and then clearing all positions to populate them back
       one by one as acquisition proceeds. This means if you stop the 
       experiment after starting it (e.g. to tweak something), the previously
       marked initial positions will be gone. To recover them, click **Reload**
       in the prescan's ``.czexp`` menu.


4. **Pause for a moment to mentally review whether everything is ready**


5. **Start the experiment by clicking** ``Run``


.. admonition:: **Troubleshooting**
    :class: note

    * To stop the macro press ``Stop`` in the macro editor
    * If there are problems with the macro editor, close and reopen it
    * If things don't work for unknown reasons, try a full system restart


Part 4: Look after your experiment
----------------------------------

Monitor the microscope for the first few time points to ensure everything is 
working as intended.

A prescan should be rapidly acquired and saved in the target directory. The
DySTrack command line should then report detection of the prescan, execution of
the image analysis pipeline, and then pushing of new coordinates, which in turn
should trigger the main scan and then the next position / time point.

.. admonition:: Tip
    :class: tip

    It's useful to configure remote access to the microscope PC to periodically
    check in on the experiment.


**After the experiment:**

* The DySTrack manager can be stopped by pressing ``Esc`` in the command line

* The microscope software and hardware should be shut down as usual

* The main scan images/stacks for each position and time point are saved as 
  separate files.

* Some advice on how to postprocess DySTrack data can be found 
  :doc:`here<postprocessing>`.

