Welcome to the Spatial reasoning test.

Candidates will be tasked to match a 3D and impossible 2D image together out of a selection of figures, testing the ablity to mentally rotate and manipulate figures mentally.

Good luck!

Please find attached: 
* Spatial_test_v1.0.0.ipynb: Python notebook of version 1 of spatial reasoning test code.
* Spatial_test_v2.0.0.ipynb: Python notebook for the final spatial reasoning test code. Draws on functions of spatialfunctions.py.
* image_constructor_3d.ipynb: this is the code used to generate all 3D and 2D images used in the test.
* .png images: images of spatial reasoning questions. The test code will call on this during the test.
* spatialfunctions.py: file containing all code functions

Ensure all files are downloaded for the test to work smoothly.


Improvements in Version 2: overview

Code structure:
* Separated specific operations into individual functions, called when the main function run_spatial_reasoning() is executed.
  * run_introduction() : Contains biodata collection and test briefing
  * run_spatial_reasoning() : calls run_introduction(), then runs spatial reasoning test and uploads data into Google Form.
  * various functions defined for button execution

Biodata collection:
* Formatted all text into HTML.
* Updated text boxes:(instead of input(), Text() is used for improved UI)
* Buttons to streamline responses (dropdown, radiobuttons)
* Submit buttons present to confirm response
* Added code processing responses to streamline formatting (e.g, joHnNy is edited to become Johnny)
* Added consent button for data collection
* Added Textbox for 4-digit identifier

Test briefing:
* Added sequence of text to brief user on how the test works, how long it is, how to record responses.
* Added countdown to test start
