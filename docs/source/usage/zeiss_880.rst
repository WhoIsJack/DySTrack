DySTrack on the Zeiss LSM880 (ZEN Black)
========================================


.. admonition:: tl;dr
    :class: note

    If you've done this many times before and just need a quick reminder:

    #. Create target dir (on drive with enough free space)

    #. Start DySTrack manager

       .. code-block:: batch
        
           conda activate dystrack
           python <path-to-config-file.py> <path-to-target-dir> [optional arguments]

    #. Configure prescan and main scan settings and save job files

    #. In MyPiC: import job files, configure image analysis and time course,
       set positions, set target dir

    #. Double-check that everything is ready, then launch

    #. Ensure everything is running correctly



Before you start
----------------

.. include:: _includes/generic_before_you_start_info.rst



Part 1: Start the DySTrack manager
----------------------------------

.. admonition:: Important config details
    :class: important

    Since MyPiC is used to run DySTrack in ZEN Black, DySTrack *must* be
    configured to send coordinates via the Windows registry by adding 
    ``tra_method : "MyPiC"`` to ``manager_kwargs`` in the relevant config file
    (see step 3 and :doc:`Installation</intro/installation>`).

    Furthermore, MyPiC saves prescans with the prefix ``DE_1`` and images will
    be in ``.czi`` format, so ensure that ``file_start : "DE_1"`` and 
    ``file_end : ".czi"`` are set in the config file.


.. include:: _includes/start_dystrack_manager_instructions.rst



Part 2: Configure acquisition settings
--------------------------------------

The microscope and sample must be ready for this part.


1. **Configure the main scan settings and save an example stack (job file)**
   
   The main scan produces the actual data of interest for the experiment.
   
   It is usually a high-resolution, high-quality configuration using high pixel
   densities, multiple channels, and either AiryScan (usually in FAST/4y mode)
   or confocal with averaging optimized for SNR. Z-stacks **must** be a range 
   around the center. Use high/optimal z-resolution for the main scan.

   Save an example stack in a separate folder for job settings, not in the
   experiment folder.

   .. admonition:: Tip
       :class: tip
       
       You do not need to acquire an entire stack as an example; if you start
       the acquisition and immediately stop it, the resulting empty image can
       still be saved and contains all the information needed for loading as a
       job file.

   *Side note:* Main scan image data for a 3D time course can be quite large
   (esp. with AiryScan). Double-check that there is enough free disk space,
   i.e. roughly the size of a main scan stack times the number of samples (if
   multi-positioning) times the number of time points (plus some spare space 
   for prescans and as a precaution to avoid slow-down of file writing).


2. **Configure the prescan settings and save as an example stack (job file)**

   .. admonition:: Important
       :class: important
       
       Unlike for the main scan, do **not** use AiryScan for the prescan.

   The prescan is used for DySTrack to find coordinates.
   
   To create a suitable prescan configuration, start with the main scan (unless
   it is AiryScan) and trade off resolution and SNR for speed to the greatest 
   extent allowed by the image analysis pipeline. Remove any averaging, 
   substantially reduce pixel density, use only a single channel, and trade off 
   laser power for gain.
   
   Z-stacks **must** again be a range around the center. Use a (very) low 
   z-resolution for the prescan and include 15-30% spare space outside your
   sample at the top and bottom (how much is needed depends on the sample and
   analysis pipeline).

   Save an example stack in a separate folder for job settings, not in the
   experiment folder.


Part 3: Configure MyPiC
-----------------------

1. **Open the MyPiC pipeline constructor macro**

   .. image:: ../images/zeiss_880/open_mypic.png
       :alt: Opening MyPiC in ZEN Black
       :width: 80%

   If this option is not available, MyPiC must first be installed. Speak to an
   expert user and/or see :doc:`Installation</intro/installation>`.


2. **Import the prescan and main scan job files into JobSetter**

   .. image:: ../images/zeiss_880/import_settings.png
       :alt: Import job files in MyPIC
       :width: 100%

   (In this example, the main scan is named ``JOB_cldnb``.)


3. **Add prescan and main scan jobs to the pipeline**

   .. image:: ../images/zeiss_880/add_pipeline.png
       :alt: Add prescan and main scan jobs to pipeline
       :width: 50%

   Ensure they are in the correct order (prescan first).


4. **Configure the time course and image analysis parameters**

   .. admonition:: Important
       :class: important
       
       Ensure the prescan job is selected when configuring these settings.

   .. image:: ../images/zeiss_880/analysis_settings.png
       :alt: Set timings and image analysis on prescan job
       :width: 50%

   * Method: Select ``Online img. analysis``
   * Tick ``Track XY`` and ``Track Z`` (if needed)
   * Tick ``Interval (not delay)`` and set how long you want the interval
     duration and number of repetitions

     Example: ``Every 10 mins for 12 hours → 10 min interval, 72 repetitions``

     Calculate sufficient time for prescan, image analysis (usually quick), and 
     main scan (usually the bottleneck). Multiply by the number of positions 
     when using multi-positioning and add a bit of buffer time.


5. **If using multi-positioning, set your positions**

   * Go to ``Default Positions``
   * Select ``Multiple``
   * ``Mark`` positions (double-check in live mode that it is centered in z)

   .. admonition:: Tip
       :class: tip

       Mark all positions with the eyepiece and adjust in live mode.


6. **Select destination folder**

   In ``Saving``, select the target directory. This is the same folder that is
   being monitored by the DySTrack manager.

   Tick ``.czi`` as format.


7. **Pause for a moment to mentally review whether everything is ready**


8. **Start the experiment**


.. admonition:: **Troubleshooting**
    :class: note

    If MyPiC fails at any point during setup:
       
    * Try making new job files (reloading old ones can sometimes cause issues)
    * Then try a MyPiC restart
    * Then try a full system restart



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
  separate files

* Some advice on how to postprocess DySTrack data can be found 
  :doc:`here<postprocessing>`.

* Be sure to (process and) move data to a different storage location asap to 
  avoid filling up the scope PC's disk drives

