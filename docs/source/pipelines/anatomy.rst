Anatomy of an image analysis pipeline
=====================================

TODO!


WIP:

Note that all pipelines start with an image loading step that is designed to
ensure that the microscope has finished writing the file before attempting to
read it, and that performs some basic checks to ensure the input looks 
sensible.

As a safety measure, all pipelines also include a limit on how much the 
z-position can change in one time point. Unless otherwise specified, the 
default limit is to allow movement in either direction of no more than 10% of
the full stack size. Extra care needs to be taken when tracking objects that
require substantially faster movement in z.