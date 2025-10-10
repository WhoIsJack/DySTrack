Advice on postprocessing DySTrack data
======================================


Part 1: Deconvolution of High-Resolution images
-----------------------------------------------

Deconvolve your data depending software (i.e. Airyscan Processing for Zeiss or NIS Deconvolution
for Nikon). Preferably only keep deconvolved data as 'raw' data to size for data storage.


Part 2: 8bit conversion each timepoint
--------------------------------------

Convert images from 16-bit to 8-bit using the same mininum and maximum values for all timepoints (set the values based on
the first timepoint). 

Part 3: Import as image sequence in FIJI
----------------------------------------

Import 8-bit individual timepoints as an image sequence in Fiji to make a movie. 

Part 4: Any downstream processing
---------------------------------

For example, deregistering image (notebook provided) and measuring speed with a kymograph. 