from __future__ import print_function

from PIL import Image


class Signature:

    def __init__(self, image):
        self.signature = image
        self.processed = None

    def preprocess(self):
        processed = self.signature.convert("L")
        processed = processed.convert("L")

        print("Threshold: ", end="")
        threshold = self.__calculateThreshold(processed)
        print(threshold)

        print("Binarizing ... ", end="")
        processed = self.__makeBinary(processed, threshold)
        print("Done")

        self.processed = processed

    def __calculateLocalThreshold(self, image, bounds):
        # type: (Image, tuple) -> int
        min = 255
        max = 0
        for x in range(bounds[0], bounds[2]):
            for y in range(bounds[1], bounds[3]):
                p = image.getpixel((x, y))
                if p < min:
                    min = p

                if p > max:
                    max = p

        return (min + max) / 2

    def __calculateThreshold(self, image):
        # type: (Image) -> int
        bounds = (0, 0, image.size[0], image.size[1])
        return self.__calculateLocalThreshold(image, bounds)

    def __makeBinary(self, image, threshold):
        # type: (int) -> None
        for x in range(0, image.size[0]):
            for y in range(0, image.size[1]):
                p = image.getpixel((x, y))

                if p > threshold:
                    p = 255
                else:
                    p = 0

                image.putpixel((x, y), p)

        return image

class SignatureFeatures:

    def __init__(self):
        self.centroid = ()
        self.boundingBox = ()
        self.transitions = ()

class FeatureExtractor:
    def __init__(self):
        pass

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
            return 0

        else:
            return XX / count, YY / count

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

        return left, right,top, bottom

    def __extractFeatures(self, image, bounds, segment = "all", depth = 0):
        print("\nSegment:", depth, segment)

        # Find centroid
        centroid = self.__getCentroid(image, bounds)

        if depth <  3 and centroid != 0:
            image = self.__extractFeatures(image, (bounds[0], centroid[0], bounds[2], centroid[1]), "top-left", depth + 1)
            image = self.__extractFeatures(image, (centroid[0], bounds[1], bounds[2], centroid[1]), "top-right", depth + 1)
            image = self.__extractFeatures(image, (bounds[0], centroid[0], centroid[1], bounds[3]), "bottom-left", depth + 1)
            image = self.__extractFeatures(image, (centroid[0], bounds[1], centroid[1], bounds[3]), "bottom-right", depth + 1)
        else:
            # Print centroid
            print("Centroid: ", end="")
            print(centroid)

            # Find transitions in each sub-area
            print("Transitions:", self.__getTransitions(image, bounds))

            # Draw bounding box
            image = self.__drawBox(image, bounds)

        return image

    def __drawBox(self, image, bounds):
        # type: (Image, tuple) -> Image
        left, right, top, bottom = bounds
        # Draw bounds on the image
        for x in range(left, right):
            image.putpixel((x, top), 0)
            image.putpixel((x, bottom - 1), 0)

        for y in range(top, bottom):
            image.putpixel((left, y), 0)
            image.putpixel((right - 1, y), 0)

        return image

    def getFeatures(self, signature):
        # type: (Signature) -> []

        # Pre-process signature
        signature.preprocess()
        image = signature.processed
        print("Image size:", image.size)

        # Locate bounding box
        box = self.__boundingBox(image)
        print("Bounding box: ", box)

        # Extract features
        features = self.__extractFeatures(image, (0, image.size[0], 0, image.size[1]))

        return features


def train(person, file, dir ="./"):
    # Try to open image
    try:
        # Open image
        infile = dir + "training-set/" + file
        print("Input:", infile)
        sign = Image.open(infile)

        # Process image
        signature = Signature(sign)
        featureExtractor = FeatureExtractor()
        processed = featureExtractor.getFeatures(signature)

        # Display processed image
        outfile = dir + "processed/" + file
        print("Output:", outfile)
        processed.save(outfile)

    except IOError:
        print("Error opening image")
        exit(-1)

def test(person, file, dir ="./"):
    # Try to open image
    try:
        # Open image
        infile = dir + "training-set/" + file
        print("Input:", infile)
        sign = Image.open(infile)

        # Process image
        signature = Signature(sign)
        featureExtractor = FeatureExtractor()
        processed = featureExtractor.getFeatures(signature)

        # Display processed image
        outfile = dir + "processed/" + file
        print("Output:", outfile)
        processed.save(outfile)

    except IOError:
        print("Error opening image")
        exit(-1)