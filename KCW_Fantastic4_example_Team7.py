import time
from collections import defaultdict
from typing import List, Tuple

INF = 99999999
bestMaxTest = 1000

# List of photos in file format
listPhoto = []

# Hash set of tags
ensembleTags = {}

# Define the Photo class
class Photo:
    def __init__(self, index: int, type: str, tags: List[str]):
        self.index = index
        self.type = type
        self.tags = [ensembleTags.get(tag, -1) for tag in tags]

# List of photos (horizontal and vertical)
photos = []
indexPhotosH = []
indexPhotosV = []

# Slideshow class
class Slideshow:
    def __init__(self, photo=None, photo2=None):
        self.index1 = -1
        self.index2 = -1
        self.tags = set()
        
        if photo:
            self.index1 = photo.index
            self.tags.update(photo.tags)
            
        if photo2:
            self.index2 = photo2.index
            self.tags.update(photo2.tags)

    def add(self, photo):
        self.index2 = photo.index
        self.tags.update(photo.tags)

# Album class
class Album:
    def __init__(self, slides=None, start=None, end=None):
        self.index = []
        self.score = 0
        if slides and start <= end:
            for i in range(start, end+1):
                if i != start:
                    self.score += interest(slides[i-1].tags, slides[i].tags)
                if slides[i].index2 != -1:
                    self.index.append((slides[i].index1, slides[i].index2))
                else:
                    self.index.append((slides[i].index1, -1))

    def add(self, slide):
        if slide.index2 != -1:
            self.index.append((slide.index1, slide.index2))
        else:
            self.index.append((slide.index1, -1))

# Function to hash the tags
def initHache():
    global ensembleTags
    ensembleTags.clear()
    key = 0
    for photo in listPhoto:
        for tag in photo[1]:
            if tag not in ensembleTags:
                ensembleTags[tag] = key
                key += 1

def hacher(tag: str) -> int:
    return ensembleTags.get(tag, -1)

def comparPhotoSize(i: int, j: int) -> bool:
    return len(listPhoto[i][1]) < len(listPhoto[j][1])

# Function to calculate the intersection length
def lenghtIntersection(v1: set, v2: set) -> int:
    return len(v1 & v2)

# Function to calculate the interest between two sets of tags
def interest(s1: set, s2: set) -> int:
    inter = len(s1 & s2)
    sizeS1 = len(s1)
    sizeS2 = len(s2)
    return min(sizeS1 - inter, sizeS2 - inter, inter)

def createPhotos():
    global photos, indexPhotosH, indexPhotosV
    photos.clear()
    indexPhotosH.clear()
    indexPhotosV.clear()
    
    for i, (type, tags) in enumerate(listPhoto):
        photo = Photo(i, type, tags)
        photos.append(photo)
        if type == 'L':
            indexPhotosH.append(i)
        else:
            indexPhotosV.append(i)

# Function to calculate penalty
def penality(s1: Slideshow, s2: Slideshow) -> int:
    return -interest(s1.tags, s2.tags)

def readFile(namefile: str):
    global listPhoto
    with open(namefile, 'r') as file:
        listPhoto.clear()
        numPhotos = int(file.readline().strip())
        for _ in range(numPhotos):
            line = file.readline().strip().split()
            photo_type = line[0]
            numTags = int(line[1])
            tags = line[2:]
            listPhoto.append((photo_type, tags))

def writeAlbum(namefile: str, alb: Album):
    with open(namefile, 'w') as file:
        file.write(f"{len(alb.index)}\n")
        for photo_pair in alb.index:
            if photo_pair[1] != -1:
                file.write(f"{photo_pair[0]} {photo_pair[1]}\n")
            else:
                file.write(f"{photo_pair[0]}\n")

# Main solve function
def solve():
    initHache()
    print("Creating Photos...")
    createPhotos()
    print("Sorting Photos by Size...")
    indexPhotosH.sort(key=lambda x: len(listPhoto[x][1]))
    indexPhotosV.sort(key=lambda x: len(listPhoto[x][1]))

    numberPhotoH = len(indexPhotosH)
    numberPhotoV = len(indexPhotosV)
    numberSlides = numberPhotoH + numberPhotoV // 2

    slides = [None] * (2 * numberSlides)
    notUseIndexH = set(range(numberPhotoH))
    notUseIndexV = set(range(numberPhotoV))

    left = numberSlides
    right = numberSlides
    
    if numberPhotoH > 0:
        slides[left] = Slideshow(photos[indexPhotosH[0]])
        notUseIndexH.remove(0)
    else:
        minPenality = INF
        indexPhoto = -1
        for j in notUseIndexV:
            p = lenghtIntersection(set(photos[indexPhotosV[0]].tags), set(photos[indexPhotosV[j]].tags))
            if p < minPenality:
                indexPhoto = j
                minPenality = p
        slides[left] = Slideshow(photos[indexPhotosV[indexPhoto]], photos[indexPhotosV[0]])
        notUseIndexV.remove(indexPhoto)
        notUseIndexV.remove(0)
    
    for i in range(1, numberSlides):
        minPenality = INF
        indexPhoto = -1
        isleft = False
        isV = False
        for j in notUseIndexH:
            newSlide = Slideshow(photos[indexPhotosH[j]])
            p = penality(slides[left], newSlide)
            if p < minPenality:
                isleft = True
                minPenality = p
                indexPhoto = j
                slides[left-1] = newSlide
            p = penality(slides[right], newSlide)
            if p < minPenality:
                isleft = False
                minPenality = p
                indexPhoto = j
                slides[right+1] = newSlide

        for j1 in notUseIndexV:
            for j2 in notUseIndexV:
                if j1 == j2: break
                newSlide = Slideshow(photos[indexPhotosV[j1]], photos[indexPhotosV[j2]])
                p = penality(slides[left], newSlide)
                if p < minPenality:
                    isV = True
                    isleft = True
                    minPenality = p
                    indexPhoto = j1
                    indexPhoto2 = j2
                    slides[left-1] = newSlide
                p = penality(slides[right], newSlide)
                if p < minPenality:
                    isV = True
                    isleft = False
                    minPenality = p
                    indexPhoto = j1
                    indexPhoto2 = j2
                    slides[right+1] = newSlide

        if isV:
            notUseIndexV.remove(indexPhoto)
            notUseIndexV.remove(indexPhoto2)
        else:
            notUseIndexH.remove(indexPhoto)

        if isleft:
            left -= 1
        else:
            right += 1
    
    print("Creating Album...")
    alb = Album(slides, left, right)
    return alb

def get_time_in_ms():
    return int(time.time() * 1000)

def main():
    current_time = get_time_in_ms()
    print("****** Test 1 *******")
    print("Reading from file...")
    readFile("inputs/0_example.txt")
    alb = solve()  # Capture the return value of solve() here
    print("Writing to file outputs/output_0_example.txt...")
    writeAlbum("outputs/output_0_example.txt", alb)
    print(f"End of 0_example.txt Score is {alb.score}")
    
    difference1 = get_time_in_ms() - current_time
    minute = difference1 // 60000
    sc = (difference1 % 60000) // 1000
    ms = difference1 % 1000
    print(f"Time taken: {minute}min {sc}s {ms}ms")

if __name__ == "__main__":
    main()
