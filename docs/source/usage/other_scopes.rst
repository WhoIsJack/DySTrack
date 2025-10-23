Adapting DySTrack to other microscopes
======================================


DySTrack can be used with any microscope control software that supports basic
macro/automation features, even if there is no official support for it (yet).

To make this happen, you need to implement the equivalent to the macro/job
definitions provided in DySTrack's ``Macros`` folder, using whatever
macro/automation tools are available on the desired microscope. This page
provides information on how to do this.


.. admonition:: **Advanced topic**
    :class: warning

    Building a custom microscope interface macro for DySTrack is a somewhat 
    advanced task, and creative solutions may be required (cue MacGyver meme).

    It is recommended that you get a good understanding of how DySTrack
    operates first, both through this documentation and by using it on one of
    the supported microscopes.

    Furthermore, it is recommended that you work with facility staff or ideally
    with a rep from the microscope manufacturer who has experience with the
    microscope's macro/automation features.


.. admonition:: Please share your work!
    :class: note

    If you build DySTrack support for a microscope that is not currently
    supported, please consider contributing your work to the DySTrack project
    to make it available for others in the community.

    If you are interested in doing so, please open an issue `on GitHub`_.



Before you start
----------------

* **Ensure you have permission to use DySTrack on this microscope**

  .. admonition:: **Tread carefully - risk of damage!**
    :class: danger

    Modern microscopes are expensive machines, and automating them comes with
    an inherent risk of damage. Do not run DySTrack without permission from the
    microscope's administrator, and always ask for help if you are unsure about 
    something.

    **For developers:** Build up your solution incrementally and test every 
    step carefully, if possible at first without actually controlling the 
    microscope hardware or with a configuration where the risk of damage is 
    minimized even if the stage makes unexpected movements (e.g. no stage 
    inset/sample, or even no objective). When testing with an actual sample,
    monitor the microscope for a prolonged time to ensure there are no minor
    errors that accumulate over time.


* **Check if the microscope's macro/automation tools are installed/available**

  .. admonition:: Paywalled macro modules
      :class: warning

      Many manufacturers paywall access to their macro/automation tools, and in
      some cases older microscope software does not support them.

      We recommend enquiring with facility staff and/or a manufacturer rep 
      about the availability and cost of these tools for your microscope of 
      interest, prior to embarking on DySTrack Macro development.

      Note that reps can often offer a free trial for a couple months. We
      recommend asking for this and then prototyping the DySTrack Macro during
      the free trial. You can then decide whether to pay for long-term access 
      to the macro module based on whether it works for your purposes.


* **"Save early, save often" while working with commercial macro tools!**

  .. admonition:: Microscope macro/automation tools can be unstable
    :class: warning

    Advanced software features in commercial microscope control software are
    often somewhat unstable, as they are not the manufacturer's focus and lack
    extensive user feedback. Manufacturers / facilities also tend to update
    software in ways that can break advanced uses.

    **You should expect the possibility that the software will crash at any
    time** while you are writing macros or editing automation workflows. All
    unsaved changes will usually be gone if this happens.

    Say it with me: **Save early, save often!**



General macro structure
-----------------------

A standard DySTrack macro follows some variant of this pseudocode::

    for timepoint in timepoints:
        
        for position in positions:

            # Prescan
            move to position
            reload prescan settings
            acquire prescan

            # Wait for new coordinates
            while no new coordinates detected:
                check for new coordinates in `dystrack_coords.txt`
                wait for a second

            # Handle new coordinates
            parse coordinates from `dystrack_coords.txt`
            convert dystrack coordinates to stage coordinates
            update position

            # Mainscan
            move to updated position
            reload mainscan settings
            acquire mainscan

        wait until timepoint duration is up


For a fully worked example in python (using the Zeiss ZEN Blue IronPython API),
see ``Macros\LSM980_ZENBlue_macro.py``. This is the macro that runs DySTrack
:doc:`on the LSM980<zeiss_980>`.

On rare occasions, automation tools already exist that support all required
features purely through configuration of a GUI. An example of this is the 
`MyPiC`_ ZEN Black macro, which is used to run DySTrack
:doc:`on the LSM880<zeiss_880>`.

.. _MyPiC: https://github.com/manerotoni/mypic/



Notes on required features
--------------------------

To implement the macro logic outlined above, the microscope software must
support (a variant of) these features:


1. **Looping**

   Some microscopes do not support arbitrary loops (especially ``while`` 
   loops), but may support specific workflows that loop over preset time points 
   and positions. Depending on the details, this may be sufficient to get 
   DySTrack to work.


2. **Waiting for some time**

   This functionality is missing surprisingly often.

   For the purpose of waiting for new DySTrack coordinates, a creative solution 
   may be needed to emulate a waiting command. This could e.g. be a loop or 
   other command that does something pointless for a while (ideally not 
   something that interacts with the hardware).

   For the purpose of waiting until a timepoint's duration has elapsed, an
   actual wait command may not be required, as the microscope software may
   offer some variant of a specialized time point loop that allows durations to 
   be set as a parameter.


3. **Recalling and moving to stage positions**

   In the ideal case, the microscope macro supports the use of the microscope's
   built-in tool for multipositioning, allowing the user to specify the initial
   positions as they would do for any other multiposition experiment, and then 
   supporting macro commands to loop over these positions and update them as 
   needed.
   
   If this is not directly supported, the next-best option is a simple command 
   that allows movement of the stage to given coordinates, in combination with 
   a way of setting and updating custom variables. In this case, the 
   coordinates can be stored and updated as custom variables, then passed to
   the stage movement command as needed. Setting initial coordinates within the 
   custom variables may require a creative solution.

   If there is a command to move the stage to provided coordinates but no way
   to store and update coordinates in memory, the DySTrack pipelines could be
   altered to return absolute instead of relative coordinates, based on some
   starting point. To pass the absolutely coordinates from one time point to
   the next within DySTrack manager, use the ``img_cache`` keyword argument.
   (See also point 7 below for more on coordinate processing.)

   Note that XY coordinates and Z coordinates are sometimes controlled by two
   separate commands.

   .. admonition:: Tip
      :class: tip

      In some cases, it may be significantly easier to create a version that 
      only tracks a single position (without support for multi-positioning), at
      least as a first step.


4. **Reloading acquisition settings**

   This feature (or some variant of it) is required to enable switching between
   prescan and mainscan acquisition settings. Different microscopes may
   implement this differently, e.g. by reloading from an example stack or by
   restoring from a specific settings file or from a list of saved settings.

   Stage/focus positions are sometimes stored and reloaded along with other
   acquisition settings, which can interfere with step 3 above. This option 
   must be turned off (or creatively dealt with in some way).

   .. admonition:: Note
      :class: note

      Whilst we generally use DySTrack with a separate prescan and main scan, 
      it may sometimes be possible/preferable to only use a main scan, with
      DySTrack configured to compute new coordinates based on it, which are 
      then used for the next time point. This can make tracking harder, but may
      remove the need for the microscope software to support reloading of 
      different acquisition settings.


5. **Saving acquired data (correctly)**

   For DySTrack to work, the prescan data acquired at a given time point and
   position must be written out as a separate file with an appropriate file 
   name and format, so that the DySTrack manager recognizes it and the image
   analysis pipeline can load it.

   Some possible challenges include:

   * **Writing individual files**
   
     If the microscope does not allow writing of individual files and instead
     writes to some large file object that is meant to contain the entire time 
     course, it may not be possible to use (native) DySTrack.
   
     This is because DySTrack manager relies on the appearance of new files to
     recognize that a prescan has completed. In principle, it might be possible
     to add a feature that instead monitors the contents of the large file used
     by the microscope, but this is likely challenging and may be functionally
     impossible if the microscope retains a permanent file lock.

     However, note that sometimes the option of writing single files might 
     exist and just be obscurely named or deeply hidden, or it might be 
     possible to include some sort of ``Save As`` or ``Export`` command in the 
     macro that saves out a copy of an individual position / time point.
   

   * **Custom file naming**

     Ideally, the microscope allows prescan and main scan files to be saved 
     with different file prefixes (so that DySTrack can be configured to only 
     recognize the prescan) or saved to different directories (in which case
     DySTrack should be configured to only monitor the prescan directory).

     If neither is possible, some regex magic could be used to have DySTrack
     manager recognize only files with certain numbers (e.g. every other file),
     or the DySTrack pipeline could be modified to skip certain files even if
     the manager triggers their analysis. Creative solutions may be required.


   * **File format**

     By default, DySTrack supports ``.tif``\ /\ ``.tiff``, ``.czi``, and 
     ``.nd2`` files. 
     
     Support for other formats may be added by modifying |load_func|. DySTrack 
     uses `bioio`_ as its backend to load image data, so support for formats 
     covered by a bioio plugin can easily be added by installing that plugin
     and including the file ending among the supported file endings. 
     
     For more obscure formats, a custom reader must be integrated into 
     |load_func|.

.. _bioio: https://github.com/bioio-devs/bioio
.. |load_func| replace:: :py:func:`robustly_load_image_after_write()<dystrack.pipelines.utilities.loading.robustly_load_image_after_write>`


6. **Reading coordinates provided by the DySTrack manager**

   Finally, the microscope software must provide some way of reading/receiving
   new coordinates from the DySTrack manager.

   Most commonly, this is done via the ``dystrack_coords.txt`` file that
   DySTrack generates in the target directory. This file looks something like
   this::
        
        Z	Y	X	msg
        8.1604	242.7783	373.4244	OK
        9.5309	251.5007	243.2269	OK
        9.1302	252.6594	258.4268	OK
        9.1110	254.4120	256.6196	OK
        _

   (The ``_`` symbol at the end signifies that the file always ends with an
   empty line. It is not actually there in the file. Also, note that this 
   follows the numpy convention of **ZYX** ordering of the dimensions.)

   Ideally, the microscope macro is able to read and parse text files and to
   store e.g. the number of lines as a variable. This can be used to check if a
   new line has been added while waiting for new coordinates.

   Once a new line is detected, the numbers should be parsed out. The ``msg``
   column can be used to add additional logic, e.g. to respond to failure cases
   or to trigger one of several different main scans (for a more complex
   experimental setup than standard tracking).

   One alternative to communicating via ``dystrack_coords.txt`` is found in our
   `MyPiC`_ ZEN Black macro (see also :doc:`here<zeiss_880>`), which reads new
   coordinates from the Windows registry.

   The relevant DySTrack manager keyword argument to specify the mode of 
   coordinate transmission is ``tra_method``. Currently available transmission
   functions are found |transmitters_module|, which is also where a new
   transmission function should be implemented if it is required to get a
   certain microscope to run.

.. |transmitters_module| replace:: :py:func:`here<dystrack.pipelines.transmitters>`


7. **Converting DySTrack coordinates to stage coordinates**

   As noted in step 3 above, the macro must track and update stage coordinates.

   The default for DySTrack pipelines is to return coordinates of the tracked
   object in **units pixel/voxel of the prescan** and **relative to the
   prescna's origin**, which is normally the voxel at index ``[0, 0, 0]`` in
   the numpy array that results from loading the prescan with `bioio_`.

   Within the microscope control software, stage coordinates may be represented
   in different ways depending on the manufacturer, so it is up to the 
   microscope macro to convert the DySTrack coordinates into stage coordinates.

   There are three aspects to consider: **units, image origins, and reference
   frames**.
   
   This is further explained below - but first, some warnings:


   .. admonition:: Beware XY vs Z differences
       :class: warning

       Microscope software often treats Z coordinates very differently to XY
       coordinates (for good reason). 
       
       Information about the XY and Z dimensions may thus be found in different 
       places, and the transformations required to convert XY and Z DySTrack 
       coordinates into XY and Z stage coordinates may differ respectively.

       It can make sense to treat the two as essentially totally independent
       coordinate systems and reason about (and test!) both of them separately.


   .. admonition:: Beware fenceposting errors
       :class: warning

       If the first pixel of a 100px line marks coordinate ``0`` (as is the 
       case in python/DySTrack), then pixel 100 is at position ``99``. Thus, 
       the center is at ``(100 - 1) / 2.0 = 49.5``! It is *not* at pixel 50.

       This is the *fencepost problem* and is likely to come up here because
       images are based on pixels but stage coordinates are continuous.
       Carefully test if the results of coordinate conversions are exactly
       right and not off by one or by one-half!


   .. admonition:: Tread carefully!
       :class: danger

       Errors in coordinate conversions may lead to unexpected stage movement,
       so this step requires extra care up front to preclude order-of-magnitude
       errors (e.g. if the stage uses a different unit than microns) as well as
       extra testing in post to detect and fix small errors that might
       accumulate over time.


   Aspects to consider when converting between DySTrack coordinates and stage
   coordinates:

   * **Units**, e.g. pixels vs microns

     Microscope software usually tracks stage position in microns, so DySTrack
     coordinates must be converted from pixels::

        microns = pixels * microns/pixel

     Obviously, this requires knowledge of the prescan's pixel sizes. Ideally,
     the microscope macro can retrieve this directly from the prescan's 
     experiment settings or by loading an example prescan (this can be done 
     once, before starting the actual loop or during the first iteration).
     
     If this is not supported, a creative solution must be found, or users must
     manually input this information before running DySTrack (**risky**).

     Remember that information about XY pixel sizes and Z step sizes are often 
     stored in different places and accessed in different ways!

     .. admonition:: Order-of-magnitude errors
        :class: danger

        Carefully check what units the stage is actually using. Though it is
        usually microns, I would not be surprised if there are stages out there
        that use inches or something. That could end badly.


   * **Image origins**, e.g. bottom left vs center

     Stage coordinates within the microscope software usually point to the
     center of the image (though they may point to a different origin, such as
     the bottom left or top left of the image, or some reference location on
     the stage itself).

     DySTrack returns coordinates relative to the corner at ``[0, 0, 0]``, so
     they often need to be converted to be relative to the center of the 
     prescan instead, e.g.::

        center = dystrack_coords - (prescan_size / 2.0)

     Remember that such conversions are a likely source of fenceposting errors,
     so you may instead need something like::

        center = dystrack_coords - ((prescan_size - 1) / 2.0)
     
     This step requires knowledge of the total size of the prescan (in pixels 
     or microns, depending on which conversion is done first), which again 
     should ideally be retrievable from the prescan settings or an example 
     file.


   * **Reference frames**, e.g. prescan location vs absolute stage position

     Microscope software usually keeps the stage coordinates in a (calibrated) 
     absolute reference frame relative to some zero-position of the stage,
     whereas DySTrack coordinates are relative to the prescan itself.

     Luckily, if units and image origins have been accounted for (see above),
     this means the DySTrack coordinates directly correspond to the required
     **offset** between old absolute stage coordinates and the new, updated
     absolute stage coordinates.

     Thus, the new coordinates can be calculated simply as::
        
        new_coords = old_coords + dystrack_coords_with_correct_units_and_origins

     However, in some cases (particularly for z-coordinates!), the absolute
     reference frame of the stage may be reversed compared to how DySTrack is
     treating the image, so you may need::

        new_coords = old_coords - dystrack_coords_with_correct_units_and_origins

     Some trial and error may be required to get to the right solution. 

     .. admonition:: Accumulating errors
        :class: warning

        If the offset direction is wrong, this may only produce a small error
        initially (since the initial position will usually not require much
        correction anyway), but a small correction in the wrong direction will 
        trigger a greater correction (in the wrong direction) on the next 
        iteration, and so on.
 

   See ``Macros\LSM980_ZENBlue_macro.py`` for a worked example that shows the 
   relevant conversions as simple python code, including a fenceposting 
   correction and the need to treat XY and Z differently.



.. admonition:: Please share your amazing work!
    :class: note

    If you got all the way to this point and actually built DySTrack support 
    for a microscope that is not currently supported, please consider 
    contributing your valuable work to the DySTrack project to make it 
    available for others in the community!

    If you are interested in doing so, please open an issue `on GitHub`_.
