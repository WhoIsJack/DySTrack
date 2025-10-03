DySTrack on the Nikon AX R (NIS Elements)
=========================================

.. admonition:: tl;dr
    :class: note

    If you've done this many times before and just need a quick reminder:

    #. Create target dir

    #. Start DySTrack manager

       .. code-block:: batch
        
           conda activate dystrack
           python <path-to-config-file.py> <path-to-target-dir> [optional arguments]

    #. Configure prescan and main scan Experiment Setups

    #. Run desired JOBS definition and go through the wizard

    #. Double-check that everything is ready, then launch

    #. Ensure everything is running correctly


Before you start
----------------

.. include:: _includes/generic_before_you_start_info.rst



Part 1: Start the DySTrack manager
----------------------------------

.. include:: _includes/start_dystrack_manager_instructions.rst



Part 2: Prepare the JOBS Definition
-----------------------------------

DySTrack uses Nikon's `JOBS`_ module for macro control within NIS Elements. 
Ideally, JOBS Definitions are prepared before running any experiments and do
not require changes at runtime. Therefore, **if the JOBS Definition for your
experiment is already prepared, you can skip to Part 3.**

.. _JOBS: https://www.microscope.healthcare.nikon.com/en_EU/products/software/nis-elements/nis-elements-jobs


.. admonition:: Note
    :class: note

    Non-expert users should work with experienced users, facility staff, and/or
    Nikon representatives to set up and correctly configure a JOBS definition
    for DySTrack, as this can be a non-trivial task.


The DySTrack repo comes with two JOBS Definitions in the ``Macros`` folder:

* ``AX_NISJOBS_lateral_line.bin``

  This definition is used for standard tracking tasks, optionally with multi-
  positioning for multiple samples. It should work for most simple experiments
  and should be the starting point for any customized workflows.


* ``AX_NISJOBS_chick_node.bin``

  This definition was implemented for a special case where the main scan is
  itself a tile scan. Here, a single field of view is acquired as the prescan
  (e.g. the chick node), but the subsequent main scan is a tile scan that
  covers a wider area (e.g. somitogenesis anterior of the node). This is an
  example of a slightly more advanced setup.


.. admonition:: GA3 is also needed...
    :class: warning

    Unfortunately, one particular step of the DySTrack JOBS pipeline requires a
    GA3 Script. This should be imported before JOBS Definitions are imported.


**Follow these steps to import the required GA3 dependency:**

1. Enter the ``JOBS/GA3`` tab (at the top):

   .. image:: /images/nikon_AXR/JOBS-GA3_tab.png
       :alt: JOBS/GA3 tab screenshot
       :width: 40%

   If this is unavailable, speak to an expert user / microscope administrator.

   
2. Go to ``Analysis Explorer`` (middle-left):

   .. image:: /images/nikon_AXR/JOBS_explorer.png
       :alt: JOBS/GA3 tab screenshot
       :width: 40%

   (It's the tab to the left of the ``JOBS Explorer`` shown here.)

   .. TODO: Replace with more appropriate screen shot!

3. ``Create New >> Import Analysis From File...``

4. Import ``DySTrack\Macros\DySTrack_PointsExpose``

5. To test, double-click it and select the file 
   ``DySTrack\tests\testdata\test-pllp_NSPARC_prescan.tiff``
   
   The GA3 preview should run and display some numbers about the prescan file;
   ``PrescanDims`` in particular should have 8 columns (``VolumeSizeX[um]``, 
   etc.) with a single number in each.


**Next, follow these steps to import a JOBS Definition:**

1. Go to the ``JOBS Explorer`` (next to the ``Analysis Explorer``)

2. If necessary, create a new empty JOBS Database

3. If necessary, create a new Project (named e.g. ``DySTrack``)

4. Find the ``Import from File`` button
   It's a yellow folder icon with a yellow upwards arrow.

5. Import the desired ``.bin`` file from ``DySTrack\Macros``

If necessary, you can now view and edit/customize the JOBS definition by
double-clicking on it. We recommend making a copy of an existing JOBS
definition before trying out any modifications on it.


.. include:: /_includes/generic_unstable_software_warning.rst



Part 3: Configure acquisition settings
--------------------------------------

The microscope and sample must be ready for this part.


1. **Configure or reload the main scan Experiment Setup**
   
   The main scan produces the actual data of interest for the experiment.
   
   It is usually a high-resolution, high-quality configuration with averaging 
   optimized for SNR, high pixel density (Nyquist if needed), and multiple 
   channels.


2. **Configure or reload the prescan Experiment Setup**

   The prescan is used for DySTrack to find coordinates.
   
   To create a suitable prescan configuration, start with the main scan and 
   trade off resolution and SNR for speed to the greatest extent allowed by the
   image analysis pipeline. Remove any averaging, substantially reduce pixel 
   density, use only a single channel, and trade off laser power for gain. 

   .. admonition:: Tip
       :class: tip
       
       Rename your Experiment Setups to reflect whether they are main scan or
       prescan settings.
 


Part 4: Start the JOBS workflow
-------------------------------

.. TODO: Double-check that this is all still correct in the latest version!

1. **Enter the** ``JOBS/GA3`` **tab (at the top):**

   .. image:: /images/nikon_AXR/JOBS-GA3_tab.png
       :alt: JOBS/GA3 tab screenshot
       :width: 40%

   If this is unavailable, speak to an expert user / microscope administrator.


2. **Go to the** ``JOBS Explorer``\ **:**

   .. image:: /images/nikon_AXR/JOBS_explorer.png
       :alt: JOBS/GA3 tab screenshot
       :width: 40%

   .. TODO: Replace with better screen shot!

   Select the JOBS Definition for your experiment and **press the green "Play"
   button** to open the JOBS wizard.


3. **Select your target directory as** ``Alternative Storage Location`` 

   .. image:: /images/nikon_AXR/JOBS_wizard_storage_location.png
       :alt: JOBS wizard target directory screenshot
       :width: 90%

   For the two radio buttons, keep the top option selected (all runs into 
   specified folder). If you instead need to use automatically generated
   subfolders in your experiment, you must provide the ``--recurse True`` 
   option when starting the DySTrack manager, otherwise it will not detect 
   prescans placed in subfolders.


4. **Set the duration and acquisition period for your time course**

   .. image:: /images/nikon_AXR/JOBS_wizard_time_course_settings.png
       :alt: JOBS wizard time course settings screenshot
       :width: 90%

   Calculate sufficient time for prescan, image analysis (usually quick), and 
   main scan (usually the bottleneck). Multiply by the number of positions when
   using multi-positioning and add a bit of buffer time.

   .. admonition:: Important
       :class: important
       
       Ensure ``Split Storage per Time point`` is ticked!


5. **If using multiple positions, set the positions**
   
   .. TODO!

   TODO: [Add screenshot and any further info as needed.]


6. **Configure the settings for the prescan**

   In the first ND Acqusition block, select your prescan Experiment Setup in
   the Lambda tab, then configure the z-stack in the Z tab.

   .. image:: /images/nikon_AXR/JOBS_wizard_prescan_selection.png
       :alt: JOBS wizard prescan lambda settings
       :width: 70%
   
   The prescan should have a low z-resolution and wide z-range.

   .. admonition:: Important
       :class: important

       The z-stack must be defined around the center; see buttons marked 5 and 
       6 in the step-by-step guide below!
   
   We recommend the following process to find good z-stack settings:

   1. Go to range mode
   2. Find and set the top of your stack; include 15-30% spare space past your 
      sample (how much is needed depends on the sample and analysis pipeline)
   3. Find and set the bottom of your stack; include 15-30% spare space past
      your sample
   4. Double-click the central coordinates to move the focus to the center
   5. Swap to centered mode

   .. image:: /images/nikon_AXR/JOBS_wizard_prescan_zstack_1to5.png
       :alt: JOBS wizard prescan zstack settings steps 1 to 5
       :width: 70%

   6. Click the ``relative`` button.
   7. Set an appropriate step size (large for prescan) / step number (button 8;
      small for prescan)

   .. image:: /images/nikon_AXR/JOBS_wizard_prescan_zstack_6to8.png
       :alt: JOBS wizard prescan zstack settings steps 6 to 8
       :width: 70%

   .. admonition:: Tip
       :class: tip

       If using a Piezo stage, reset the Piezo (button marked ``+``) to ensure 
       it is centered near your samples. For multi-positioning, issues with the 
       piezo range may occur if samples are mounted at very different distances 
       from the cover slip.


7. **Configure the settings for the main scan**

   In the second ND Acqusition block, select your main scan Experiment Setup in
   the Lambda tab, then configure the z-stack in the Z tab.

   Proceed exactly as with the prescan, but now use a higher z-resolution (use
   Nyquist if desired) and with less spare space around the sample.

   .. admonition:: Important
       :class: important

       Again, the z-stack must be defined around the center; see above.


8. **Pause for a moment to mentally review whether everything is ready**


9. **Start the experiment**



Part 5: Look after your experiment
----------------------------------

Monitor the microscope for the first few time points to ensure everything is 
working as intended.

A prescan should be rapidly acquired and saved in the target directory. The
DySTrack command line should then report detection of the prescan, execution of
the image analysis pipeline, and then pushing of new coordinates.

NIS Elements will appear "frozen" while awaiting new coordinates from the
DySTrack manager. As soon as the coordinates are written, it should "unfreeze"
and trigger main scan acquisition, then move on to the next position / time 
point.

.. admonition:: Tip
    :class: tip

    It's useful to configure remote access to the microscope PC to periodically
    check in on the experiment.

**After the experiment:**

* The DySTrack manager can be stopped by pressing ``Esc`` in the command line

* The microscope software and hardware should be shut down as usual

* The main scan images/stacks for each position and time point are saved as 
  separate files

