Anatomy of an image analysis pipeline
=====================================


This page describes the general anatomy of DySTrack image analysis pipelines in
some detail. It is primarily relevant to those who seek to develop their own
pipelines.

.. include:: _includes/share_your_pipeline_note.rst



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

4. Quick checks on the coordinates; constrain them if needed, or error if
   something is very wrong

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst

5. Return the final target coordinates

   .. include:: /_includes/add_a_bit_of_extra_empty_space.rst


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
    long time to run, the microscope will be idle in that time, and the sample 
    may even start moving away.

    This is a key reason why we usually use prescans for image analysis, as
    their low pixel/voxel number means they can be loaded and processed very
    quickly.



Call signature
--------------

TODO/WIP! YAH!

Pipeline functions must...






Common pipeline steps
---------------------

TODO/WIP!

- Something on file reading

  Inspiration from elsewhere:

    Note that all pipelines start with an image loading step that is designed 
    to ensure that the microscope has finished writing the file before 
    attempting to read it, and that performs some basic checks to ensure the 
    input looks sensible.


- Something on the sanity checks


- Something on image analysis? (Keep it brief here?!)


- Something on z-limit

  Inspiration from elsewhere:

    As a safety measure, all pipelines also include a limit on how much the 
    z-position can change in one time point. Unless otherwise specified, the 
    default limit is to allow movement in either direction of no more than 10% 
    of the full stack size. Extra care needs to be taken when tracking objects
    that require substantially faster movement in z.