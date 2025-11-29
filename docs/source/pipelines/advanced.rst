Advanced tools and strategies
=============================

This section discusses some advanced tools and suggested strategies for the
development of sophisticated experimental workflows using DySTrack.

.. admonition:: **Advanced topic**
    :class: warning

    This is for advanced users looking to extend DySTrack beyond its basic
    tracking capabilities.

.. include:: _includes/share_your_pipeline_note.rst



Multi-phase experiments
-----------------------

In some scenarios, different image analysis tasks are required withing a single
experiment. Although this differs from standard DySTrack use cases, it is quite
straightforward to implement.

The easiest way of doing so is to modify the macro / automation workflow in the
microscope control software to write prescans with different file names 
depending on the required image analysis task (so basically just an extension 
of the standard distinction between prescans and main scans). Within the image
analysis pipeline, you can then simply use ``if``-statements that check the 
file name and run the appropriate image analysis task.

Another, more modular but less interconnected option would be to run multiple
independent instances of DySTrack that monitor for different file names and
trigger different pipelines.

Example use case: **Event-based swapping between overview and targetted 
acquisitions**

  In this example, the microscope periodically images a field of largely
  stationary cells in a monolayer, using a low-magnification objective. These 
  images are passed to DySTrack, which computes and returns coordinates for 
  drift correction, especially in z. 
  
  Additionally, the pipeline also detects delamination events, where cells
  leave the monolayer and start to migrate away. If such an event is detected,
  the coordinates of the target cell are sent to the microscope, along with an 
  ``img_msg`` indicating that a target cell has been found.
  
  The scope then switches to a high-NA objective and images the delaminating
  cell at high resolution as it migrates away. During this time, DySTrack is
  used for single-cell tracking, enabling the microscope to closely track the
  target cell. After a certain time, or if some other condition is satisfied,
  the microscope returns to the low-magnification mode and monitors the cell
  layer for another delamination event.

  This is a quite sophisticated example that illustrates the combined use of
  multiple different image analysis tasks (drift correction on low-resolution 
  monolayer images, detection of delaminating cells, single-cell tracking of 
  migrating target cells, and possibly detection of some other event that 
  terminates single-cell tracking). Variations of this strategy could be used
  for countless applications, e.g. tracking patrolling immune cells at low
  resolution and swapping to high-resolution if one is activated and starts to
  engulf a target, or detecting division events and recursively tracking all
  daughter cells over several divisions to reconstruct a complete lineage.



Sending extra data to the scope
-------------------------------

Some applications require more data to be sent to the microscope than just a
single set of coordinates.

The easiest way of doing this is to encode the extra data as a string in 
``img_msg`` and then parse it within the macro / automation workflow in the 
microscope control software. However, whilst this approach is very good for 
raising flags (e.g. to switch experimental phases, see above), it quickly 
becomes cumbersome when passing actual data.

A simple and powerful alternative is to write out extra data in separate text
files, which are then again parsed out in the microscope control macro.

Example use case: **Periodic photoactivation of leader cells**

  In this example, normal tracking of a migratory tissue such as the lateral
  line is performed as usual. However, every n-th time point, the image
  analysis pipeline executes an additional workflow that identifies the
  position of the current leader cell.

  This extra coordinate is fed back to the microscope via ``img_msg``,
  triggering placement of a ROI and a pulse of light at an activating 
  wavelength for an optogenetic construct.

Example use case: **Detection and tracking of a subset of cells**

  Imagine a use case similar to the one described for delaminating cells in 
  the previous section, but here multiple target cells are detected in the
  overview image, e.g. all cells currently expressing some marker.

  In addition to returning the global coordinates of the monolayer for the next
  overview image in the usual way, the pipeline also writes an appropriately
  named text file (e.g. ``active_nuclei_coords_t012_p003.txt`` given a prescan
  named ``overview_t012_p003.tif``) with the coordinates of all detected target
  cells.

  The microscope macro is then configured to parse the text file and trigger
  acquisition of a high-resolution stack of each target cell before returning 
  to the overview acquisition setting.

 

Caching across time points
--------------------------

Normally, every call of the image analysis pipeline by the DySTrack manager is
completely independent. However, in some cases it may be useful to have
information about previous acquisitions available when running the image
analysis pipeline.

This is what the ``img_cache`` keyword argument is for. It works essentially
the same as ``img_kwargs``, except that it is also returned back by the image
analysis pipeline and can thus be updated to keep track of information over
multiple time points.

Example use case: **An absolute limit to z-movement**

  As mentioned under Step 2 of the 
  :ref:`pipeline anatomy<anatomy-section-pipeline-details>`, one standard
  safety measure we currently provide as a pipeline utility is to limit the 
  amount by which the stage can move in z at each time point. However, there is
  no tool to limit the total amount by which the stage can move in z over the
  entire time course.

  This is readily implemented using ``img_cache``, which can be used to keep
  track of the cumulative sum of stage movement across time points. The result
  can then be fed into a constraint function similar to |constrain_func|, and
  the user can configure the maximum allowed range using e.g. an additional
  (fixed) keyword argument in ``img_kwargs``.

.. |constrain_func| replace:: :py:func:`constrain_z_movement()<dystrack.pipelines.utilities.constraints.constrain_z_movement>`


Example use case: **Robust tracking using historical information**

  In engineering applications, tools such as `PID controllers`_ or `Kalman 
  filters`_ are often used for robust and smooth control in the presence of 
  noise (e.g. in airplane autopilots). These tools utilize past information 
  about the sample's movement as a prior when deciding the coordinates for the 
  next step.

  This can be implemented in DySTrack using e.g. a keyword argument 
  ``coordinate_history = []`` that starts an empty list to which coordinates
  are appended in each acquisition. As the list starts filling up, subsequent
  steps can use this information to improve the robustness of coordinate
  identification, the smoothness of the tracking, and/or the chance that
  fallbacks will be successful if the image analysis occasionally fails.

  For this case, one would set ``img_cache = {"coordinate_history" = []}`` as 
  the initial condition in the config file.

  To generalize this to multi-position tracking, use a dictionary instead of a 
  list and parse which position is currently being tracked based on the file 
  name suffix.

.. _PID controllers: https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller
.. _Kalman filters: https://en.wikipedia.org/wiki/Kalman_filter