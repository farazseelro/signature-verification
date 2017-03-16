from __future__ import print_function

from PIL import Image


class Analyzer:
    def __init__(self, image):
        # type: (Image) -> None
        self.image = image
        self.width = image.size[0]
        self.height = image.size[1]

    def transitions(self, bounds):
        count = 0
        prev = self.image.getpixel((bounds[0], bounds[1]))
        for x in range(bounds[0] + 1, bounds[2]):
            for y in range(bounds[1] + 1, bounds[3]):

                curr = self.image.getpixel((x, y))

                if curr == 255 and prev == 0:
                    count += 1

                prev = curr

        return count

    def centroid(self):
        XX, YY, count = 0, 0, 0
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.image.getpixel((x, y)) == 0:
                    XX += x
                    YY += y
                    count += 1
        return XX / count, YY / count

    def boundingbox(self):
        left = self.image.size[0]
        right = 0
        top = self.image.size[1]
        bottom = 0

        # Calculate bounds
        for x in range(0, self.image.size[0]):
            for y in range(0, self.image.size[1]):
                p = self.image.getpixel((x, y))

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


class Thresholder:
    def __init__(self, image):
        # type: (Image) -> None
        self.image = image

    def localthreshold(self, bounds):
        # type: (tuple) -> int
        min = 255
        max = 0
        for x in range(bounds[0], bounds[2]):
            for y in range(bounds[1], bounds[3]):
                p = self.image.getpixel((x, y))
                if p < min:
                    min = p

                if p > max:
                    max = p

        return (min + max) / 2

    def threshold(self):
        # type: () -> int
        bounds = (0, 0, self.image.size[0], self.image.size[1])
        return self.localthreshold(bounds)


class ImageProcessor:
    def __init__(self, image):
        # type: (Image) -> None
        self.image = image
        self.width = image.size[0]
        self.height = image.size[1]

    def binarize(self):
        # type: () -> Image
        # Convert RGB image to gray
        print("Converting to grayscale ... ")
        self.image = self.image.convert("L")

        # Make binary image
        print("Calculating threshold ... ", end="")
        T = Thresholder(self.image).threshold()
        print(T)

        print("Binarizing image ... ")
        self.__binarize(T)

        # Find bounding box of the signature
        print("Calculating bounding box ... ", end="")
        analyzer = Analyzer(self.image)
        bounds = analyzer.boundingbox()
        print(bounds)

        # Find centroid
        print("Locating centroid of signature ... ", end="")
        centroid = analyzer.centroid()
        print(centroid)

        # Find transitions in each sub-area
        print("Calculating black-to-white transitions ... ")
        print("Top-left: ", analyzer.transitions((0, 0, centroid[0], centroid[1])))
        print("Bottom-left: ", analyzer.transitions((0, centroid[1], centroid[0], bounds[3])))
        print("Top-right: ", analyzer.transitions((centroid[0], 0, bounds[1], centroid[1])))
        print("Bottom-right: ", analyzer.transitions((centroid[0], centroid[1], bounds[1], bounds[3])))

        # Draw bounding box
        print("Drawing bounding box ... ", end="")
        self.__drawBox(bounds)
        print("Done")

        # Draw segment partitions
        print("Drawing segment partiotions ... ", end="")
        for x in range(bounds[0], bounds[1]):
            self.image.putpixel((x, centroid[1]), (0))
        for y in range(bounds[2], bounds[3]):
            self.image.putpixel((centroid[0], y), (0))
        print("Done")

        return self.image

    def __binarize(self, T):
        # type: (int) -> None
        for x in range(0, self.width):
            for y in range(0, self.height):
                p = self.image.getpixel((x, y))

                if p > T:
                    p = 255
                else:
                    p = 0

                self.image.putpixel((x, y), p)

    def __drawBox(self, bounds):
        # type: (tuple) -> None
        left, right, top, bottom = bounds
        # Draw bounds on the image
        for x in range(left, right):
            self.image.putpixel((x, top), 0)
            self.image.putpixel((x, bottom), 0)

        for y in range(top, bottom):
            self.image.putpixel((left, y), 0)
            self.image.putpixel((right, y), 0)


if __name__ == "__main__":

    # Try to open image
    try:
        # Open image
        print("Opening dataset/sample.jpg ... ", end="")
        im = Image.open("dataset/sample.jpg")
        print("Done. Image size is", im.size)

        # Process image
        im = ImageProcessor(im).binarize()

        # Display processed image
        print("Saving processed image as dataset/sample-processed.jpg")
        im.save("dataset/sample-processed.jpg")
    except IOError:
        print("Error opening image")
        exit(-1)
