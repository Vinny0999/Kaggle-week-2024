import random
import copy
import os
import sys


class Photo:
    def __init__(self, id, line):
        param = line.split(" ")
        self.id = id
        self.isHorizontal = True if param[0] == "L" else False
        tags_unstripped = param[2::]
        self.tags = set([x.strip() for x in tags_unstripped])

    def pointsTo(self, slide):
        intersection = len(self.tags & slide.tags)
        if intersection == 0:
            return 0
        diff_self = len(self.tags) - intersection
        if diff_self == 0:
            return 0
        diff_slide = len(slide.tags) - intersection
        if diff_slide == 0:
            return 0
        return min(diff_self, intersection, diff_slide)


class Slide:
    def __init__(self, photo):
        self.photo1_n = photo.id
        self.photo2_n = None
        self.tags = photo.tags
        self.points = 0
        self.isHorizontal = photo.isHorizontal

    def addVertical(self, photo):
        if photo.isHorizontal:
            print("Cannot pair an landscape photo in a dataframe with a portrait one")
        else:
            self.photo2_n = photo.id
            self.tags.update(photo.tags)

    def previewPointsTo(self, photo, slide):
        prev_tags = self.tags.union(photo.tags)
        inters = len(prev_tags & slide.tags)
        if inters == 0:
            return 0
        diff1 = len(prev_tags) - inters
        if diff1 == 0:
            return 0
        diff2 = len(slide.tags) - inters
        if diff2 == 0:
            return 0
        return min(diff1, inters, diff2)

    def pointsTo(self, slide):
        intersection = len(self.tags & slide.tags)
        if intersection == 0:
            return 0
        diff_self = len(self.tags) - intersection
        if diff_self == 0:
            return 0
        diff_slide = len(slide.tags) - intersection
        if diff_slide == 0:
            return 0
        return min(diff_self, intersection, diff_slide)

    def __str__(self):
        line = str(self.photo1_n)
        if self.photo2_n is not None:
            line += " " + str(self.photo2_n)
        return line


def printPercentage(slides_processed, elements):
    perc = 100 * slides_processed / elements
    print("{:.2f}%".format(perc), end="\r", flush=True)


def calculateScore(slideshow):
    points = 0
    for i in range(0, len(slideshow) - 1):
        points += slideshow[i].pointsTo(slideshow[i+1])
    return points


def generateOutputFile(file, slideshow):
    file.write(str(len(slideshow)) + "\n")
    for slide in slideshow:
        file.write(str(slide) + "\n")


def recreateSolution(solutionFile, photos):
    slideshow = []
    next(solutionFile)
    for line in solutionFile:
        ids = line.split(" ")
        ids = [int(x.strip()) for x in ids]
        p1 = photos[ids[0]]
        p2 = photos[ids[1]] if len(ids) == 2 else None
        slide = Slide(p1)
        if p2:
            slide.addVertical(p2)
        slideshow.append(slide)
    return slideshow


def generatePhotoList(file):
    photos = []
    lineNumber = 0
    for line in file:
        if lineNumber != 0:
            photos.append(Photo(lineNumber - 1, line))
        lineNumber += 1
    return photos


def generateSlideshow(photos_toCopy):
    photos = copy.deepcopy(photos_toCopy)
    photos.sort(key=lambda x: len(x.tags))
    elements = len(photos)
    slideshow = []
    last = None
    for photo in photos:
        if photo.isHorizontal:
            last = Slide(photos.pop(photos.index(photo)))
            photos_processed = 1
            break
    if last is None:
        last = Slide(photos.pop(0))
        last.addVertical(photos.pop(0))
        photos_processed = 2
    slideshow.append(last)
    while photos:
        printPercentage(photos_processed, elements)
        points = -1
        selected = None
        for p in photos:
            new_points = last.pointsTo(p)
            if new_points > points:
                points = new_points
                selected = p
        if selected:
            last = Slide(photos.pop(photos.index(selected)))
            if selected.isHorizontal:
                photos_processed += 1
            else:
                match = None
                best_delta = -1000
                for p in [x for x in photos if not x.isHorizontal]:
                    new_points = last.previewPointsTo(p, slideshow[-1])
                    delta = new_points - points
                    if delta > best_delta:
                        best_delta = delta
                        match = p
                if match:
                    points += best_delta
                    last.addVertical(photos.pop(photos.index(match)))
                    photos_processed += 2
            slideshow[-1].points = points
            slideshow.append(last)
    print("       ", end="\r")
    return slideshow


def improveSolution(slideshow):
    elements = (len(slideshow)) * (len(slideshow) - 1) / 2
    size = len(slideshow)
    slides_processed = 0
    slideshow.reverse()
    for i in range(1, size):
        slideshow[i-1].points = slideshow[i-1].pointsTo(slideshow[i])
    for i in range(0, size-1):
        current = slideshow[i]
        current_score = current.points
        if i > 0 and slideshow[i-1] is not None:
            current_score += slideshow[i-1].points
        higher_delta = 0
        candidate_insert = i
        best_points1 = 0
        best_points2 = 0
        for j in range(i+1, size-1):
            if slides_processed % 10000 == 0:
                printPercentage(slides_processed, elements)
            slides_processed += 1
            pts1 = current.pointsTo(slideshow[j])
            pts2 = current.pointsTo(slideshow[j+1])
            previous_score = slideshow[j].points
            new_score = pts1 + pts2
            delta = (new_score - previous_score) - current_score
            if delta > higher_delta:
                higher_delta = delta
                candidate_insert = j+1
                best_points1 = pts1
                best_points2 = pts2
        if candidate_insert != i:
            slideshow[i] = None
            slideshow.insert(candidate_insert, current)
            slideshow[candidate_insert-1].points = best_points1
            slideshow[candidate_insert].points = best_points2
        print("", end="\r")
    return [x for x in slideshow if x is not None]


def main_run():
    inputFileNames = {
        "10": "10_computable_moments"
    }

    arguments = [x.lower() for x in sys.argv[1::]]
    if len(arguments) == 0:
        letter = "10"
    else:
        letter = arguments[0]

    print("\nSTARTED...")
    folder = "outputs"
    if not os.path.exists(folder):
        os.makedirs(folder)
    inputName = inputFileNames[letter]
    try:
        with open(f"inputs/{inputName}.txt", "r") as inputFile:
            photos = generatePhotoList(inputFile)
    except IOError:
        print(f"!!! {inputName}.txt NOT FOUND IN INPUT FOLDER !!!")
        exit()

    slideshow = generateSlideshow(photos)
    score = sum(x.points for x in slideshow[:-2])
    print(f"Found solution with score {score}.")
    outputFileName = f"{folder}/{inputName}_out_{score}.txt"
    with open(outputFileName, "w") as out:
        out.write(str(len(slideshow)) + "\n")
        for slide in slideshow:
            out.write(str(slide) + "\n")


def improve_run():
    inputFileNames = {
        "10": "10_computable_moments"
    }

    filePath = input("\nSolution file to improve -> ")
    filePath = filePath.replace("\\", "/")
    k = filePath.rfind("/")
    folder = filePath[:k]
    inputName = inputFileNames[filePath[k+1:k+2]]
    try:
        with open(f"inputs/{inputName}.txt", "r") as inputFile:
            photos = generatePhotoList(inputFile)
        with open(filePath, "r") as solutionFile:
            slideshow = recreateSolution(solutionFile, photos)
    except IOError:
        print("!!! NO INPUT WITH THAT NAME IN INPUT FOLDER !!!")
        exit()

    old_score = calculateScore(slideshow)
    slideshow = improveSolution(slideshow)
    score = calculateScore(slideshow)
    print(f"Improved score from {old_score} to {score}.")
    outputFileName = f"{folder}/{inputName}_out_{score}.txt"
    with open(outputFileName, "w") as out:
        generateOutputFile(out, slideshow)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "improve":
        improve_run()
    else:
        main_run()
