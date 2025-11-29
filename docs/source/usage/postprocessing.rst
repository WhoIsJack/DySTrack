Advice on postprocessing DySTrack data
======================================


Some simple advice on processing data generated with DySTrack, based on our
practical experience.


.. admonition:: Note
    :class: note

    The biggest challenge with these data tends to be their size. For 3D 
    acquisitions of multiple samples over several hours, raw data can be 
    hundreds of GB or even several TB (in particular for AiryScan data).
    
    In consequence, we have generally adopted the convention that deconvolved,
    8bit-converted data is the true "raw data" that is actually stored
    long-term.

    One possible downside of this approach is that new methods of deconvolution
    cannot be applied retroactively.



Common postprocessing steps
---------------------------

1. **Deconvolution of mainscan images**

   If required/desired, deconvolve your data using the relevant software (e.g. 
   AiryScan Processing for Zeiss, or NIS Deconvolution or Denoising, or any 
   other tool you usually use). Use batch mode to process all time points as 
   one batch.

   .. admonition:: Tip
      :class: tip

      It can be useful to have a powerful second PC set up with a high-bandwith
      connection to the microscope PC and an offline-only version of the
      acquisition software. This means time-consuming processing steps can be
      run without blocking the microscope.


2. **8bit conversion of each time point**

   For most downstream analysis, 256 gray values are sufficient, so to save
   disk space and improve performance on downstream image analysis tasks, we 
   generally convert images from 16bit to 8bit format using ImageJ macros in 
   batch mode.

   .. admonition:: Warning: serious mistakes possible
      :class: warning

      Converting images to 8bit must be done with care, as mistakes can render
      data useless (or even misleading)!
      
      Crucially, unless all data / time points across an experiment are 
      converted using the same min and max values, intensity will no longer be 
      comparable (if it ever was; absolute intensity measurements in microscopy
      come with many pitfalls and must be handled with care or avoided)!
      
      For any data where intensity matters, it is therefore essential to 
      consistently set the same min and max values in the histogram prior to
      8bit conversion.

      If these min and max values are chosen poorly, other problems follow. If
      the range is chosen too small, data may get "cropped" and in consequence
      effectively look "overexposed". Conversely, if the range is chosen too
      large, the histogram of the data may get compressed into far too few gray
      values, leading to a "filled contour" effect.

      To pick the right min and max values, be sure to check examples at
      different time points (in case signal increases at later time points),
      across multiple samples and, where applicable, across all different
      experimental conditions.

      If this advice is at all unclear, you should probably speak to someone 
      with image analysis experience before processing your data.


3. **Maximum z-projection**

   We usually use maximum z-projections for visual analysis of time course data
   (whilst keeping the z-stacks themselves for quantitative analysis). Again, 
   batch processing in ImageJ is recommended.


4. **Loading time points as a time course (in ImageJ/Fiji)**

   There are many ways of converting individually-saved DySTrack time points
   into a single "movie". 

   One simple option using standard **ImageJ** is via ``File >> Import >> Image 
   Sequence...``:

   * Select the folder with your data
   * Use the ``Filter`` field to pick out files you want to load. For example,
     if your maximum z-projection macro adds ``_zmax.tif`` as the file ending, 
     type this into the ``Filter`` field and you should see that the ``Count``
     field now displays the correct number of detected files (i.e. the number 
     of time points). 
   * Click ``OK`` to load the images in a single viewer.
   * If there are multiple channels and/or slices, use ``Image >> Hyperstacks 
     >> Stack to Hyperstack...`` and type in the correct values to create A
     hyperstack.

   In **Fiji**, using ``File >> Import >> Bio-Formats`` and selecting the
   option ``Group files with similar names`` can be used to load data directly
   as a hyperstack (use e.g. ``File name | contains | _zmax.tif`` to get the
   same file filtering effect).

   Once loaded, you can customize and save the time course as usual.

   .. admonition:: Note
      :class: note

      Loading many time points in 3D simultaneously will require a lot of
      memory and may be slow. Using a **virtual stack** can help with this, 
      though we tend to just look at projections or at individual time points,
      depending on what we are looking for.


5. **"Deregistration" of DySTracked data**

   Sometimes it is of interest to visualize the actual movement of the tracked
   sample in real-space coordinates (see the bottom panel of the gif on the
   landing page), for example to measure the velocity or to create a kymograph.
   We refer to this as **"deregistration"**.

   The DySTrack repo comes with a Jupyter Notebook that performs deregistration
   on a dataset, using the coordinates in ``dystrack_coords.txt`` and the shape
   and pixel size of the prescan (must be provided). The notebook also provides
   some extra options to play around with.

   It is recommended to perform deregistration on z-projected images, as the
   resulting movies will tend to very large files.


6. **High-quality post-registration and tracking**

   Depending on the sample, acquisition settings, and image analysis pipeline,
   samples tracked with DySTrack may not necessarily be perfectly registered
   across time points. Indeed, DySTrack pipelines should be optimized for speed
   and robustness, not for high-quality registration.

   Thus, if high-quality registration is required, it is recommended to run it
   *in post*, rather than as a DySTrack pipeline during acquisition. This comes
   with the additional advantage that high-quality main scan data can be used 
   to optimize the registration (as opposed to low-quality prescan data).

   The same applies to get high-quality tracking data (i.e. linked 
   segmentations). It is usually preferable to segment and track objects in the
   high-quality main scan *in post*, without relying directly on the DySTrack
   coordinates. Depending on the smoothness of the raw data and the nature of
   the tracking algorithm, it may or may not be better to deregister the data
   (see above) prior to high-quality tracking.