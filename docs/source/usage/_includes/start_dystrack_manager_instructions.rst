
.. Instructions for running the DySTrack manager.
   Reused across Usage instructions for different microscopes, as these steps
   are always the same.
    

.. admonition:: Tip
    :class: tip

    This works the same for all microscopes, regardless of manufacturer (aside
    from config details noted above).


0. **Make a new target directory for your experiment**

   The DySTrack manager will monitor this directory, and experiment data will 
   be saved there. *Ensure the hard disk has sufficient free space* and allows
   for sufficiently fast file writing for your use case.


1. **Open a Windows command console**

   Depending on how python was installed, you may need to specifically open a 
   "Miniforge Prompt" or "Anaconda Prompt", or run ``conda init``.


2. **Activate the environment in which DySTrack has been installed**

   For example:

   .. code-block:: batch
      
      conda activate dystrack


3. **Find/create the configuration file for your experiment**

   * Config files are found in ``DySTrack\run``
   * They specify the :doc:`image analysis pipeline</pipelines/available>` to 
     use
   * They can specify further parameters for the pipeline and the manager
   * To create a new config file, best copy an old one and modify it
   * Ensure that ``file_start`` and ``file_end`` (and where applicable 
     ``tra_method``) are set correctly
   
   If you are a non-expert user, the configuration file for your type of
   experiment should be configured for/with you by a more experienced user and
   should not require further changes at runtime. Additional information is 
   found under :doc:`Installation</intro/installation>` and in the provided 
   config files themselves.


4. **Start the DySTrack manager session in your command prompt:**

   .. code-block:: batch

       python <path-to-config-file.py> <path-to-target-dir> [optional arguments]

   .. admonition:: Tip
      :class: tip

      Instead of typing the entire file paths into the console, you can drag
      and drop the config file and the target directory into the console, which
      will automatically write out the full path.

   If everything is configured correctly, you should see the following message:

   .. code-block:: text

       DYSTRACK MANAGER SESSION STARTED!
       Monitoring target dir(s) for new files...
       Press <Esc> to terminate.

   In addition, you should see a file called ``dystrack_coords.txt`` appear in
   your target directory. The DySTrack manager will write detected coordinates
   to this file.