Anatomy of an image analysis pipeline
=====================================


This page describes the general anatomy of DySTrack image analysis pipelines in
some detail. It is primarily relevant to those who seek to develop their own
pipelines.


.. admonition:: Tip!
    :class: tip

    To build your own pipeline, best start by making a copy of an existing 
    pipeline and then modify it as needed.


.. include:: _includes/share_your_pipeline_note.rst



.. _anatomy-section-overview:

Overview
--------

DySTrack image analysis pipelines are python functions that take a file path as
their first and only positional argument and return new z, y, and x coordinates
(along with a couple of other things). They are called by the DySTrack manager,
which passes them the file path to a newly detected image file that the
pipeline is to analyze.

Pipeline functions will commonly include the following steps:

1. Load the image specified in the file path argument

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

2. Quick checks on the data; error out or warn users if something is wrong

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

3. Detect the desired new target coordinates within the image

   Typical steps might include:

   - Some smoothing to reduce noise
   - Masking foreground pixels/voxels (e.g. by thresholding)
   - Cleaning the foreground mask and/or identifying a specific target object
   - Detecting new coordinates based on the foreground mask / target object
   
   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

4. Quick checks on the coordinates; trigger fallbacks or constrain movement if
   needed, or error if something is very wrong

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

5. Return the final target coordinates

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst


Additional information on each step is provided 
:ref:`below<anatomy-section-pipeline-details>`.


.. admonition:: Freedom!
    :class: note
    
    Ultimately, pipeline functions are just python functions, so the above
    structure is not prescriptive; *you can do anything python allows you to 
    do!*

    For instance, you could run a machine learning model trained to detect your 
    target object instead of using standard image analysis functions. You could
    also do additional things besides detecting new target coordinates, such as 
    pushing results to a live dashboard that can be monitored over the internet 
    from another location. It doesn't even have to all be in python; you could
    just write a small python pipeline function that runs/triggers some
    non-python code/software in another process and retrieves the resulting
    coordinates at the end.


.. admonition:: Performance...
    :class: warning

    The only limitation to this freedom is performance; if a pipeline takes a
    long time to run, the microscope will be idle in that time (at least if
    using a default acquisition macro), and the sample may even start moving 
    away.

    This is a key reason why we usually use prescans for image analysis, as
    their low pixel/voxel number means they can be loaded and processed very
    quickly.



.. _anatomy-section-call-signature:

Call signature
--------------

Image analysis pipeline functions must adhere to the following call signature:

.. code-block:: python

    z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
        target_path, **img_kwargs, **img_cache)


**Information on the arguments:**

- ``target_path`` must be the only positional argument and must accept a 
  string. DySTrack manager will pass the full path of newly generated (prescan) 
  image files into the pipeline function through this argument.


- ``**img_kwargs`` represents any number of optional keyword arguments. 
  DySTrack manager will pass them as a dictionary using python's arbitrary
  keyword argument handling (``**dict``). A simple example might be:

  .. code-block:: python

    def image_analysis_func(
        target_path, channel=None, gauss_sigma=3.0, verbose=False
    ):
        <etc...>

  Here, the ``img_kwargs`` dictionary may contain any of ``channel``, 
  ``gauss_sigma``, and/or ``verbose``. These can be set as a fixed 
  configuration in the corresponding config file (in the ``run`` folder), or 
  otherwise dynamically as command line arguments.


- ``**img_cache`` works essentially the same way as ``img_kwargs``, but it is
  also returned by ``image_analysis_func`` itself. Thus, it provides a way of
  forwarding a variable from one call of the pipeline function to the next.
  This is an advanced feature; more information can be found 
  :doc:`here<advanced>`, but most users can safely ignore this.


**Information on the return values:**

The pipeline *must* return exactly 5 values:

- ``z_pos`` (float): the new z-coordinate for the next acquisition. Return
  ``0.0`` when working in 2D.

- ``y_pos`` (float): the new y-coordinate for the next acquisition.

- ``x_pos`` (float): the new x-coordinate for the next acquisition.

- ``img_msg`` (str): a string message that can be used to communicate extra
  information to the microscope or to log events. By convention, simply return
  ``"OK"`` if there is no meaningful information to communicate/log.

- ``img_cache`` (dict): Used to forward variables to the next call of the 
  pipeline function (see above). This is an advanced feature, so most users 
  will not need it. Simply return ``{}`` (an empty dictionary) in that case.

.. admonition:: Convention
    :class: note
    
    We follow the numpy convention of ordering image dimensions as ZYX (not
    XYZ). Make sure you do not accidentally return coordinates in the wrong 
    order!


**An example function definition might thus looks like this:**

.. code-block:: python

    def image_analysis_func(
        target_path, channel=None, gauss_sigma=3.0, verbose=False
    ):
        """My very nice image analysis pipeline. It works by <explanation>.

        Parameters
        ----------
        target_path : str
            Path to the image file that is to be analyzed.
        channel : int, optional, default None
            Index of channel to use for masking in case of multi-channel images.
            If not specified, a single-channel image is assumed.
        gauss_sigma : float, optional, default 3.0
            Sigma for Gaussian filter prior to masking.
        verbose : bool, optional, default False
            If True, more information is printed.
        
        Returns
        -------
        z_pos, y_pos, x_pos : floats
            New coordinates for the next acquisition. For 2D inputs, z_pos is 0.0.
        img_msg : "_"
            A string output message; required by DySTrack but here unused and just
            set to "_".
        img_cache : {}
            A dictionary to be passed as keyword arguments to future calls to the
            pipeline; required by DySTrack but here unused and just set to {}.
        """
        
        # <code to load and process the image>

        return z_pos, y_pos, x_pos, "OK", {}


.. admonition:: Required: numpy-style doc string!
    :class: important
    
    Note that the ``Parameters`` section of the doc string is automatically
    parsed by DySTrack to forward information about keyword arguments to the
    DySTrack command line interface. For this to function properly, your doc
    string **must follow the numpy style** and should ideally be kept fairly
    simple.

    In particular, the ``Parameters`` section must adhere strictly to this
    structure::

        Parameters
        ----------
        x : type
            Description of parameter `x`.
        y : type
            Description of parameter `y`.
        <etc>



.. _anatomy-section-pipeline-details:

More details on pipeline steps
------------------------------

While the image analysis itself can be highly bespoke and completely different
depending on the sample for which it is defined, the initial and final steps of
pipelines will usually be very similar. The
:doc:`pipeline utilities</api/pipelines/dystrack.pipelines.utilities>` module 
offers a couple of functions that may be used for this, and the information in
this section provides further context and advice.


Step 1: Image loading
.....................

Load the image specified in the ``target_path`` argument.

In principle, any image reading function that works with the target image 
format can be used to do this. We use `bioio`_, which is a state-of-the-art
implementation of many bioimage read/write functions, but other tools could be 
used just as well. 

.. admonition:: Possible race condition
  :class: warning

  However, it is important to be aware that the DySTrack manager will call the 
  image analysis pipeline *as soon as it detects the new image file!* 
  This can lead to a race condition where the microscope has not yet fully 
  written the file when the pipeline is trying to load it, possibly causing an 
  error!

To solve this problem, DySTrack provides |load_func|, which waits until the 
size of the target file no longer increases within a 2-second window. It then
attempts to load the image and in case of failure loops back up to 5 times to
try again (before giving up and raising an error).

By default, |load_func| supports |supported_img_formats| files. Support for other formats may
be added by installing the relevant bioio plugin (if available) or by adding in 
a custom reader. The list of supported file extensions in |load_func| must also
be updated accordingly.

.. _bioio: https://github.com/bioio-devs/bioio
.. |load_func| replace:: :py:func:`robustly_load_image_after_write()<dystrack.pipelines.utilities.loading.robustly_load_image_after_write>`


Step 2: Sanity checks
.....................

We recommend including some sanity checks on the loaded data. This is mostly to
ensure that DySTrack errors immediately if something is misconfigured such that
the data produced by the microscope violates the user's assumptions.

Currently available pipelines include basic checks for appropriate image 
dimensionality and size. They also usually check if the image is in 8bit 
format, otherwise converting them down to 8bit (to accelerate processing) and
optionally issuing a warning.

What checks and adjustments are appropriate can vary considerably depending on 
the sample and pipeline, and many additional checks could be envisioned. 
Furthermore, in some cases it may be more useful to focus on sanity checks on 
the output of the image analysis (see Step 4 below). Thus, there is currently
no utility function that offers generic sanity checking. Instead, pipeline 
developers should include bespoke sanity checks as appropriate for their use 
case.

.. admonition:: DySTrack manager error handling
  :class: note

  When raising errors within the image analysis pipeline, it is important to
  consider how DySTrack manager will respond, which is as follows:

  - If an error is raised the very first time the image analysis pipeline is
    triggered, DySTRack manager will always just raise the error and exit. No
    coordinates will be sent to the microscope. This is intended to abort a run
    immediately if user expectations were violated from the very start.
    
    .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

  - If an error is raised on subsequent iterations and the keyword argument 
    ``img_err_fallback`` in |manager_func| is set to ``True`` (the default!),
    DySTrack manager will print the error but will continue running and **fall
    back to the previous coordinates**, meaning the same result will be sent
    to the microscope as in the last iteration, except that the ``msg`` column
    in ``dystrack_coords.txt`` will read ``"Image analysis failed!"``. This
    may sometimes save an experiment, or at least keeps it going for the other
    samples in a multi-positioning setup.

    .. TODO: This seems kinda bad; a better fallback would be to write all zeroes!

  .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

  - If an error is raised on subsequent iterations and ``img_err_fallback`` is
    set to ``False``, DySTrack manager raises the error and exits. No further
    coordinates will be sent to the microscope.


.. |manager_func| replace:: :py:func:`run_dystrack_manager()<dystrack.manager.manager.run_dystrack_manager>`



Step 3: Image analysis
......................

Analyze the image in order to extract new target coordinates for subsequent
acquisition(s).

The best solution depends entirely on the sample that is being tracked and on
the (prescan) acquisition parameters. It could take the form of a classical
image analysis pipeline (involving e.g. smoothing and thresholding), or of a 
pre-trained machine learning model, or of some other approach (e.g. fitting 
models/functions to the data).
 
For simple cases, basic thresholding (e.g. using Otsu) and tracking of the
center of mass may be a good starting point (see 
:ref:`here<pipeline-section-center-of-mass>`).
Alternatively, existing pipelines can sometimes be found in the literature or
are already established in the lab. These can also serve as good starting
points, but they must be carefully tested as they often assume high-quality 
data or make other assumptions that may be violated in a live tracking setting.

For more advice on how to develop image analysis pipelines for use with 
DySTrack, see :doc:`Developing image analysis pipelines</pipelines/develop>`.

.. TODO: ADD A WARNING!


Step 4: Post-checks, fallbacks, and constraints
...............................................

As with the input, it can make sense to do some sanity checks on the outputs of
the image analysis, either to error out in completely unexpected cases, or to
try to recover from common problems, or to constrain how much the microscope is
allowed to move at all as a safety precaution.

When raising errors at this stage, remember to consider how DySTrack manager
will respond to them (see the relevant Note above).

An example of attempting to recover from common problems is found in the 
lateral line tracking pipeline, where two failure cases that crop up 
occuasionally (one being masking failure, the other being that the tissue has 
moved too far between time points) are being caught and handled by moving 
default distances. For more details on this see 
:ref:`here<pipeline-section-lateral-line>` and in the source code. This is not
a particularly robust fallback handling and could be further improved, but it
illustrates the concept and works reasonably well in practice.

An example of constraining microscope motion is currently included in all
pipelines and is implemented as a utility function; **[TODO: ADD LINK!]**. To
reduce the risk of the stage inset / sample being moved against the objective,
the maximum z-distance that the system is allowed to move per time point is
being limited to a preset fraction of the stack size. Obviously, a hard limit
on total movement would be preferable (and can easily be implemented using the
``img_cache``, see :doc:`here<advanced>`), however in practice it can be 
difficult to figure out what this limit should be for a given setup, and such
safety measures would ideally be implemented within the microscope control
software instead.

.. TODO: Add the link above once z-constraining has been refactored!



Step 5: Returning the results
.............................

See the :ref:`Call signature<anatomy-section-call-signature>` section for 
details on the format in which the image analysis pipeline function must return
its outputs to the DySTrack manager.


