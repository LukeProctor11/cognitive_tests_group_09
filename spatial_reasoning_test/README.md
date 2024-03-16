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
