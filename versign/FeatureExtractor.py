from math import atan

from PIL import Image, ImageDraw


class FeatureExtractor:
    def __init__(self):
        self.features = {}

    def __getTransitions(self, image, bounds):
        left, right, top, bottom = bounds[0], bounds[1], bounds[2], bounds[3]
        count = 0
        prev = image.getpixel((left, top))
        for x in range(left + 1, right):
            for y in range(top + 1, bottom):

                curr = image.getpixel((x, y))

                if curr == 255 and prev == 0:
                    count += 1

                prev = curr

        return count

    def __getCentroid(self, image, bounds):
        XX, YY, count = 0, 0, 0
        for x in range(bounds[0], bounds[1]):
            for y in range(bounds[2], bounds[3]):
                if image.getpixel((x, y)) == 0:
                    XX += x
                    YY += y
                    count += 1

        if count == 0:
            centroid = (bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2

        else:
            centroid = XX / count, YY / count

        return centroid, count

    def __boundingBox(self, image):
        left, right, top, bottom = image.size[0], 0, image.size[1], 0

        # Calculate bounds
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                p = image.getpixel((x, y))

                if p < 128:
                    if x < left:
                        left = x

                    if x > right:
                        right = x

                    if y < top:
                        top = y

                    if y > bottom:
                        bottom = y

        return left, right, top, bottom

    def __extractFeatures(self, image, bounds, segment="", depth=0):
        # Find centroid
        centroid, blacks = self.__getCentroid(image, bounds)

        if depth < 3 and centroid != 0:
            image = self.__extractFeatures(image, (bounds[0], centroid[0], bounds[2], centroid[1]), segment + "1",
                                           depth + 1)
            image = self.__extractFeatures(image, (centroid[0], bounds[1], bounds[2], centroid[1]), segment + "2",
                                           depth + 1)
            image = self.__extractFeatures(image, (bounds[0], centroid[0], centroid[1], bounds[3]), segment + "3",
                                           depth + 1)
            image = self.__extractFeatures(image, (centroid[0], bounds[1], centroid[1], bounds[3]), segment + "4",
                                           depth + 1)
        else:
            # Find transitions in each sub-area
            transitions = self.__getTransitions(image, bounds)

            # Calculate aspect ratio
            width = (float)(bounds[1] - bounds[0])
            height = (float)(bounds[3] - bounds[2])

            if height == 0:
                ratio = 0
            else:
                ratio = round(width / height, 2)

            # Calculate normalized size
            if blacks != 0:
                nsize = width * height / blacks
            else:
                nsize = 0

            # Calculate angle of inclination
            dx = (float)(centroid[0] - bounds[0])
            dy = (float)(bounds[3] - centroid[1])
            if dx != 0:
                angle = atan(dy / dx)
            else:
                angle = 0

            # Draw bounding box
            image = self.__drawBox(image, bounds, centroid)

            # Return features
            self.features[segment] = (ratio, transitions, centroid, blacks, nsize, angle)
            return image

        return image

    def __drawBox(self, image, bounds, centroid):
        # type: (Image, tuple) -> Image
        left, right, top, bottom = bounds
        # Draw bounds on the image
        for x in range(left, right):
            image.putpixel((x, top), 0)
            image.putpixel((x, bottom - 1), 0)

        for y in range(top, bottom):
            image.putpixel((left, y), 0)
            image.putpixel((right - 1, y), 0)

        draw = ImageDraw.Draw(image)
        draw.line((bounds[0], bounds[3], centroid[0], centroid[1]), fill=128)

        return image

    def getFeatures(self, image):
        # type: (Image) -> (Image, dict)
        # Locate bounding box
        box = self.__boundingBox(image)
        image = image.crop((box[0], box[2], box[1] - box[0], box[3] - box[2]))
        size = image.size
        size = (2048, int(float(size[1]) / size[0] * 2048))
        image = image.resize(size)

        # Extract features
        self.features = {}
        image = self.__extractFeatures(image, (0, image.size[0], 0, image.size[1]))

        return image, self.features
