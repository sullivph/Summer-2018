import datetime
import json
import math
import numpy as np
from PIL import Image


class HeatMapGenerator:

    # Class instantiation
    def __init__(self, centerStrength, secondaryStrength, tertiaryStrength):
        # Pixel strength for heat map brush
        self.centerStrength = centerStrength
        self.secondaryStrength = secondaryStrength
        self.tertiaryStrength = tertiaryStrength

        # User entered information
        self.dataJSON = None
        self.frameRate = 0.0
        self.dimensions = [0, 0]
        self.center = [0, 0]

    # Grabs path to JSON file
    def getJSON(self):
        isValid = False
        while not (isValid):
            path = input('Enter path to the target JSON file '
                         '(ex: /path/to/target/file.json): ')
            try:
                with open(path) as file:
                    self.dataJSON = json.load(file)
                    isValid = True
                    pass
            except IOError as e:
                print('Unable to open file! Try again.')

    # Grabs frame rate
    def getFrameRate(self):
        self.frameRate = input('Enter the source video frame rate: ')

    # Grabs source video dimensions
    def getDimensions(self):
        self.dimensions[0] = int(input('Enter the source video width (in pixels): '))
        self.dimensions[1] = int(input('Enter the source video height (in pixels): '))

    # Asks user for approximate coordinates of center of patient
    def getCenter(self):
        self.center[0] = int(input('Enter the approximate '
                                   'X coordinate of the center of the patient: '))
        self.center[1] = int(input('Enter the approximate '
                                   'Y coordinate of the center of the patient: '))

    # Calculates the average position of all key points of a given person
    def getPos(self, personKeyPoints):
        averagePos = [0.0, 0.0]
        numValidPoints = 0
        for i in range(0, 18):  # Iterate over each key point to calculate average
            index = i * 3
            if personKeyPoints['pose_keypoints'][index + 2] != 0:
                averagePos[0] += personKeyPoints['pose_keypoints'][index]
                averagePos[1] += personKeyPoints['pose_keypoints'][index + 1]
                numValidPoints += 1
        averagePos[0] /= numValidPoints
        averagePos[1] /= numValidPoints
        return averagePos

    # Assigns person closest to the center of the frame to the 0th index position
    def attemptFix(self):
        blankFrame = False
        frameNum = 0
        for frame in self.dataJSON['frame']:  # Iterate over each frame
            if len(frame['people']) == 0:  # Check if frame has no persons
                if not blankFrame:
                    blankFrame = True
                    print('No poses detected from '
                          + str(self.timestamp(frameNum))),
            elif blankFrame:
                blankFrame = False
                print('to ' + str(self.timestamp(frameNum)))
            if len(frame['people']) != 0:  # If frame has persons, handle
                personIndex = 0
                mostCentered = 0
                closestDist = None
                for person in frame['people']:  # Check for closest person to center
                    if personIndex == 0:
                        closestDist = self.getDist(self.getPos(person))
                    else:
                        dist = self.getDist(self.getPos(person))
                        if dist < closestDist:
                            closestDist = dist
                            mostCentered = personIndex
                    personIndex += 1
                if mostCentered != 0:  # Notify user of person swap if made
                    print('0th person index swap made at '
                          + str(self.timestamp(frameNum)))
                    frame['people'][0], frame['people'][mostCentered] = \
                        frame['people'][mostCentered], frame['people'][0]
                    print('Position of new 0th: '
                          + str(self.getPos(frame['people'][0])))
            frameNum += 1

    # Converts frame number to timestamp
    def timestamp(self, frameNum):
        secs = frameNum / float(self.frameRate)
        dec = round(secs, 3)
        dec = str(dec - int(dec))[1:]
        while len(dec) < 4:
            dec += '0'
        secs = int(secs)
        time = str(datetime.timedelta(seconds=secs))
        time += dec
        return time

    # Calculates distance of person to center of the frame
    def getDist(self, position):
        a = self.center[0] - position[0]
        b = self.center[1] - position[1]
        dist = math.sqrt(a ** 2 + b ** 2)
        return dist

    # Creates and returns heat map of hands from start frame to end frame
    def createMap(self):
        print('Creating hand heat map...')
        data = np.full((self.dimensions[1], self.dimensions[0], 3),
                       [0, 0, 0],
                       dtype=np.uint8)  # Create image array
        frameNum = 0
        for frame in self.dataJSON['frame']:  # Paint hand key points of
            personIndex = 0  # persons other than patient onto image array
            if len(frame['people']) > 1:
                for person in frame['people']:
                    if personIndex != 0:
                        self.paintHands(person, data)
                    personIndex += 1
                print ('Painted at frame ' + str(frameNum))
            frameNum += 1
        map = Image.fromarray(data, 'RGB')
        return map

    # Creates and saves heat map to user entered directory
    def createPNG(self):
        fileName = input('Enter file name and extension for heat map '
                         '(ex: heatmap.png): ')
        directory = input('Enter directory to save to (ex: /path/to/directory/): ')
        map = self.createMap()
        map.save(directory + fileName)

    # Draws frame onto hand heat map given an image array and a person
    def paintHands(self, personKeyPoints, imageArray):
        rightHand = [0, 0]
        leftHand = [0, 0]
        rightHandWeight = personKeyPoints['pose_keypoints'][14]
        leftHandWeight = personKeyPoints['pose_keypoints'][23]
        if rightHandWeight != 0:
            rightHand[0] = int(round(personKeyPoints['pose_keypoints'][12], 0))
            rightHand[1] = int(round(personKeyPoints['pose_keypoints'][13], 0))
            self.paintPoint(rightHand, imageArray)
        if leftHandWeight != 0:
            leftHand[0] = int(round(personKeyPoints['pose_keypoints'][21], 0))
            leftHand[1] = int(round(personKeyPoints['pose_keypoints'][22], 0))
            self.paintPoint(leftHand, imageArray)

    # Paint soft brush point onto image array
    def paintPoint(self, point, imageArray):
        if point[0] >= self.dimensions[0]:
            point[0] = self.dimensions[0] - 1
        if point[1] >= self.dimensions[1]:
            point[1] = self.dimensions[1] - 1
        self.heatPixel(point, self.centerStrength, imageArray)
        # Create tuples for surrounding points
        up = [point[0], point[1] + 1]
        down = [point[0], point[1] - 1]
        left = [point[0] - 1, point[1]]
        right = [point[0] + 1, point[1]]
        upLeft = [point[0] - 1, point[1] + 1]
        upRight = [point[0] + 1, point[1] + 1]
        downLeft = [point[0] - 1, point[1] - 1]
        downRight = [point[0] + 1, point[1] - 1]
        secondary = [up, down, left, right]
        tertiary = [upLeft, upRight, downLeft, downRight]
        for point in secondary:  # Paint pixels accordingly
            if self.inBounds(point):
                self.heatPixel(point, self.secondaryStrength, imageArray)
        for point in tertiary:
            if self.inBounds(point):
                self.heatPixel(point, self.tertiaryStrength, imageArray)

    # Check if point is within dimensions
    def inBounds(self, point):
        if point[0] >= self.dimensions[0]:
            return False
        if point[0] < 0:
            return False
        if point[1] >= self.dimensions[1]:
            return False
        if point[1] < 0:
            return False
        return True

    # Paints pixel
    def heatPixel(self, point, strength, imageArray):
        if imageArray[point[1], point[0]][0] != 255:
            imageArray[point[1], point[0]][0] += strength
        elif imageArray[point[1], point[0]][1] != 255:
            imageArray[point[1], point[0]][1] += strength
