
.. Instructions for running the DySTrack manager.
   Reused across Usage instructions for different microscopes, as these steps
   are always the same.
    

.. admonition:: Tip
    :class: tip

    This works the same for all microscopes, regardless of manufacturer.


0. **Make a new target directory for your experiment**

   The DySTrack manager will monitor this directory, and experiment data will 
   be saved there. Ensure the hard disk has sufficient free space and allows
   for sufficiently fast file writing.


1. **Open a Windows command console**

   Depending on how python was installed, you may need to specifically open a 
   "Miniforge Prompt" or "Anaconda Prompt".


2. **Activate the environment in which DySTrack has been installed**

   For example:

   .. code-block:: python
      
      conda activate dystrack


3. **Find/create the configuration file for your experiment**

   * Config files are found in ``DySTrack\run``
   * They specify the **image analysis pipeline** to use
   * Optionally, they can specify further parameters for the pipeline and the 
     manager
   * To create a new config file, best copy an old one and modify it
   * Further instructions are included in the config file itself
   
   *Note:* If you are a non-expert user, the configuration file for your type 
   of experiment should be configured for/with you by a more senior user!


4. **Start the DySTrack manager session in your command prompt:**

   .. code-block:: batch

       python <path-to-config-file.py> <path-to-target-dir> [optional arguments]

   .. admonition:: Tip
      :class: tip

      Instead of typing the entire paths file path into the console, you can
      drag and drop the config file and the target directory into the console
      and the Windows console will automatically write out their paths.

   If everything is configured correctly, you should see the following message:

   .. code-block:: text

       DYSTRACK MANAGER SESSION STARTED!
       Monitoring target dir(s) for new files...
       Press <Esc> to terminate.

