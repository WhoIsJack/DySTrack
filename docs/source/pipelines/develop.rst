Developing image analysis pipelines
===================================


This section provides practical advice on how to develop a new image analysis
pipeline for use with DySTrack.


.. admonition:: **Advanced topic**
    :class: warning

    Building a custom image analysis pipeline requires some experience with
    python and bioimage analysis, and a good understanding of how DySTrack
    works in general.

    It is recommended to first read through most of this documentation and
    ideally to get hands-on experience by installing DySTrack on a microscope
    and testing it with one of the available pipelines (e.g. using
    center-of-mass tracking on some simple test sample).

    Also, be warned once again that serious mistakes in your pipeline could in
    the worst case trigger large stage movements and potentially cause damage.
    **Carefully test everything you do!**

.. include:: _includes/share_your_pipeline_note.rst



Collecting test data
--------------------

To make pipeline development efficient, we *stongly* recommend to first collect
a *comprehensive* set of example (prescan) data against which prototypes of the
pipeline can be tested and rapidly iterated. It is *very slow* to iterate by
going to the microscope and realizing after an hour of imaging that the
prototype pipeline doesn't work because the sample looks ever so slightly
different from the singular test case against which the pipeline was developed.

Thus, first collect a battery of test data:

- Several (5+) different samples, ideally including some that are sub-optimal,
  e.g. comparably weak transgene expression or comparably poor mounting

- Several (2-3) acquisition settings, with different levels of optimization for 
  speed over quality (though all prescan settings ultimately focus on speed)

- Examples across different stages; some samples change in structure or
  intensity over time, e.g. as the embryo develops; the pipeline should work
  across all stages that will ultimately be tracked; consider also that
  time-course acquisition may cause bleaching, so the pipeline may need to be
  robust to this as well

- Examples where the field of view is deliberately offset compared to the
  optimum (in all different dimensions and combinations thereof; x, y, z, xy, x
  z, yz, xzy)

- Examples where the sample is completely outside the field of view; this is
  useful to understand how the pipeline might behave if something has gone
  wrong and the sample has been lost entirely

- Other examples of common failure cases that can be anticipated and that the
  pipeline should be robust to (e.g. if there is a chance that a tracked cell
  will undergo apoptosis)

- Unless the desired pipeline is specific to a highly bespoke use case on a 
  particular microscope, it may well pay off in the long term to aim to create
  a highly robust pipeline that works on different micorscopes; where possible, 
  test data should thus be acquired on a couple different machines

With these data available, the pipeline can then be developed and tested
efficiently *in silico*, yielding a relatively robust implementation as the
starting point for live testing at the microscope.


.. admonition:: **A note on ML-based pipelines**
    :class: note
    
    When considering whether to use machine learning-based approaches for a
    DySTrack pipeline, the following caveats should be kept in mind:

    1. Directly training a model from scratch to predict target coordinates 
       based on an input image will likely require a much larger set of 
       training data than what is needed for an experienced image analyst to
       develop a robust algorithmic pipeline.

       .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

    2. Using an established ML tool as part of a pipeline (e.g. detecting
       nuclei with a pre-trained nuclear segmentation model, followed by some
       post-processing to exclude artifacts and to find the coordinates of the
       nucleus/nuclei of interest) may be more straightforward, but since 
       prescans are usually optimized for rapid acquisition at the cost of 
       image quality, they may be out-of-distribution for pre-trained models 
       and require extensive fine-tuning. The result may also not be robust to
       use with other settings, markers, or microscopes without further
       fine-tuning.



Prototyping the image analysis
------------------------------

With the test data in your hands, you are ready to develop a prototype 
pipeline.

The :doc:`Anatomy<anatomy>` section details the structure of image analysis
pipelines and in particular their call signature, which must be adhered to for
DySTrack manager to correctly interact with them.

Other than that, the choice of approach depends entirely on the target sample
and imaging setup in question. Two approaches we have successfully used are
sketched below, but of course there are countless other possibilities.


.. admonition:: Tip!
    :class: tip

    Always best start by making a copy of an existing pipeline and then modify 
    it as needed!


**Standard masking-based approach\:**

1. Preprocessing (image cleaning)

   - Gaussian smoothing is a near-universal step to suppress noise
   - Median smoothing can be useful for shot noise / dead pixels
   - Various background subtraction approaches could be useful

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

2. Foreground detection (masking)

   - Usually based on some form of global or local threshold detection

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

3. Postprocessing (mask clean-up)

   - Morphological methods (e.g. hole filling) may be useful
   - Volume filtering or retaining only the largest object may also be useful

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

4. Coordinate identification

   - Based on either the center, or an edge, or some other feature of the mask
   - Different dimensions may track different features, e.g. the center in z 
     and y and the leading edge in x

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

Examples using this approach include the 
:ref:`center of mass pipeline<pipeline-section-center-of-mass>` and the
:ref:`lateral line pipeline<pipeline-section-lateral-line>`.



**Model fitting approach\:**

1. Preprocessing (image cleaning), as above

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

2. Fit a model/function to the signal

   - We've had success fitting a 1d function to the intensity profile along
     each axis
   - Fit e.g. a Gaussian to track the center of a diffuse signal
   - Fit e.g. a sigmoid function to track a leading edge
   - Different functions can be chosen along different axes
   - Fitting bespoke functions (e.g. templates) could also work

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

3. Use the relevant fitted parameter as a target coordinate

   - E.g. the mean of a Gaussian or the inflection point of a sigmoid function

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst


An example using this approach is the 
:ref:`chick node pipeline<pipeline-section-chick-node>`.


.. admonition:: **Some general tips**
    :class: tip
    
    - Simplicity *greatly* helps with robustness!
    - Fully understand your code before testing at the scope
    - Expect edge cases to be a problem; incorporate sanity checks
    - Errors should not pass silently; the experimenter needs to be aware
    - Visualize every step with plots, and include key plots in the final 
      pipeline

    [Partly inspired by ``The Zen of Python, by Tim Peters``]



Live testing at the microscope
------------------------------

Once the prototype works robustly across the battery of test data, you are
ready for the first live test at the microscope.

.. admonition:: **Warning**
    :class: warning

    **Expect the first test(s) to fail!**

    When they do, try to understand the problem as deeply as possible while at
    the scope. If it's not a simple fix that can be retested immediately, be
    sure to collect relevant test data for offline testing of improved versions
    of the prototype!


A sensible testing sequence for a fresh pipeline might include the following\:


1. **Dry run**

   Remove the sample and stage inset, ensuring ample clearance for the
   stage/objective. Have the microscope acquire an empty prescan in a different
   folder and then manually move a previously acquired example prescan to the
   target folder that DySTrack is monitoring.

   This is to check against order-of-magnitude conversion errors where the
   stage might move e.g. a centimeter instead of a micron.


2. **Single time-point checks**

   Set everything up as if for a full time course, but start by only running
   the first two time points to check if everything behaves as intended.

   Do the same thing again, but deliberately offset the sample in the initial
   position to check that DySTrack corrects properly corrects for it (and
   doesn't e.g. correct in the opposite direction).


3. **Supervised time-lapse test**

   Start an actual full time lapse but supervise the microscope for the first
   several iterations to ensure everything is running as intended, and even if
   things look good still check back at very regular intervals throughout the
   entire duration of the time course.

   *Tip:* It can be useful to configure remote access to the microscope PC to 
   enable regular remote checks during the first several tests.


4. **Celebrate!**

   When it works, the results are often spectacular! \:\)


.. admonition:: **Future-proofing with automated tests**
    :class: tip
    
    We recommend writing automated tests (ideally within the pytest framework
    included in the DySTrack distribution) that make it easy to check whether
    the pipeline behaves as expected after any fixes, improvements, or version 
    upgrades.

    The DySTrack GitHub repository implements a simple set of tests for all
    included pipelines, which can be used for inspiration (see 
    ``DySTrack\tests\tests_unitary\tests_pipelines``). These tests generally
    just use a single prescan example to keep the size of the GitHub repo in
    check, but when developing your own pipeline you could include additional
    private tests on data that is in a different folder (not tracked by git).

