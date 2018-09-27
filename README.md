# Summer 2018
*A showcase of part of my work as a Computer Vision Research Intern at Vanderbilt University*

### Overview
This summer, I had the pleasure of working with a team of professors and graduate students to build a system that identifies emergency medical procedures conducted on medevacs, relaying the procedure name and timestamp to the patient's destination. This technology will eventually be used to replace communication (i.e., hand-written notes and brief conversations) currently used in the field, allowing EMTs to focus solely on patient care in an emergency situation while providing accurate and detailed information to care centers. In our preliminary design, we run an open-source computer vision algorithm called "OpenPose" on a videofeed of the EMT and the patient that provides us with joint keypoints. 
![Pipeline Diagram](https://i.imgur.com/4CNAB2C.png)

A large part of my work involved automating the video processing pipeline through AWS and OpenPose (with Python and Shell scripting), and studying the resulting JSON data. As a side project, I decided to create a tool to process and visualize data that will eventually be used to train a convolutional neural network classifier which will aid in the identifying of the medical procedures of interest.

## Heat Map Generator
Included in this repository is [heatmapgenerator.py](https://github.com/sullivph/Summer-2018/blob/master/heatmapgenerator.py), the source code for the tool mentioned above. Using Python, along with numpy and PIL, I was able to write code that isolates and visualizes the movement of the EMT's hands over time, given the JSON output of the video processing pipeline.
![Heat Map Generator Diagram](https://i.imgur.com/odtYF8h.png)

A simple implementation as such will ask the user for a .JSON file along with information about the video and a location for the resulting heat map image:
```
h = HeatMapGenerator(85, 51, 17)
h.getJSON()
h.getDimensions()
h.getCenter()
h.attemptFix()
h.createPNG()
```
The three integers passed to a HeatMapGenerator object upon instantiation dictate the strength of the "brush" used to draw the heat map of the EMT's hands. These parameters can be visualized through the diagram below, which is what a 3x3 grouping of pixels would look like after the brush had painted over the middle pixel 3 times.

![Brush Diagram](https://i.imgur.com/q69RYAW.png)

This programatic brush adds the strength integers to the red value in RGB pixels. Over the course of a whole procedure, certain pixels are brushed to the point where they reach a maximal red value of 255, in which case the brush will start adding the strength integers to the green value, creating an overall heat gradient from black to red to orange to yellow in the final image.

### Final Remarks
As this tool is further developed, a more sophisticated methodology to identify the EMT and patient skeletons from the JSON data provided by OpenPose should be implemented. A streamlined approach in feeding the isolated EMT hand movement data to a convolutional neural network might involve replacing the image array with a simpler multi-dimensional array and ignoring the image output altogether.
