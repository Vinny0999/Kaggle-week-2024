import time
from collections import defaultdict

# Constants
INF = 99999999

# Global variables
adjIndex = []
listPhoto = []
ensembleTags = {}
photos = []
indexPhotosH = []
indexPhotosV = []
alb = None

# Function to read from the file
def read_file(file_name):
    global listPhoto
    with open(file_name, 'r') as file:
        listPhoto.clear()
        num_photos = int(file.readline().strip())
        for _ in range(num_photos):
            data = file.readline().strip().split()
            photo_type = data[0]
            num_tags = int(data[1])
            tags = data[2:]
            listPhoto.append((photo_type, tags))

# Function to write the album to a file
def write_album(file_name):
    with open(file_name, 'w') as file:
        file.write(f"{len(alb['index'])}\n")
        for idx, second in alb['index']:
            if second != -1:
                file.write(f"{idx} {second}\n")
            else:
                file.write(f"{idx}\n")

# Initialize the tag hashing system
def init_hash():
    global ensembleTags
    ensembleTags.clear()
    key = 0
    for _, tags in listPhoto:
        for tag in tags:
            if tag not in ensembleTags:
                ensembleTags[tag] = key
                key += 1

# Hash function for tags
def hash_tag(tag):
    return ensembleTags[tag]

# Function to calculate the intersection length between two tag lists
def length_intersection(v1, v2):
    i, j = 0, 0
    intersection_len = 0
    while i < len(v1) and j < len(v2):
        if v1[i] == v2[j]:
            intersection_len += 1
            i += 1
            j += 1
        elif v1[i] < v2[j]:
            i += 1
        else:
            j += 1
    return intersection_len

# Function to calculate the "interest" score between two photos
def interest(tags1, tags2):
    intersection = length_intersection(tags1, tags2)
    return min(len(tags1) - intersection, len(tags2) - intersection, intersection)

# Create photos from the list of photo data
def create_photos():
    global photos, indexPhotosH, indexPhotosV
    photos.clear()
    indexPhotosH.clear()
    indexPhotosV.clear()
    for idx, (photo_type, tags) in enumerate(listPhoto):
        photo = {
            'index': idx,
            'type': photo_type,
            'tags': sorted([hash_tag(tag) for tag in tags])
        }
        photos.append(photo)
        if photo_type == 'H':
            indexPhotosH.append(idx)
        else:
            indexPhotosV.append(idx)

# Comparison function for sorting photos
def compare_photo_inter(i, j):
    return len(adjIndex[i]) < len(adjIndex[j]) or (len(adjIndex[i]) == len(adjIndex[j]) and i < j)

# Function to solve the problem and create the album
def solve():
    init_hash()
    create_photos()
    num_tags = len(ensembleTags)
    
    ensemble_photos = defaultdict(list)
    for i in indexPhotosH:
        for tag in photos[i]['tags']:
            ensemble_photos[tag].append(i)
    
    # Create the graph of photo intersections
    adjIndex.clear()
    adjIndex = [[] for _ in range(len(indexPhotosH))]
    for tag in ensemble_photos.values():
        for i in tag:
            adjIndex[i].extend(tag)
    
    # Remove self references
    for i in range(len(indexPhotosH)):
        adjIndex[i] = [x for x in adjIndex[i] if x != i]

    # Sort photos based on the number of intersecting tags
    indexPhotosH.sort(key=lambda x: len(adjIndex[x]))
    
    # Solve by choosing photos and creating the album
    path = [-1] * len(indexPhotosH)
    for i in range(len(indexPhotosH)):
        j = indexPhotosH[i]
        if len(adjIndex[j]) > 0:
            v = sorted(adjIndex[j])
            k = v[0]
            path[j] = k
            adjIndex[k].remove(j)
            for idx in range(i + 1, len(indexPhotosH)):
                adjIndex[indexPhotosH[idx]].remove(k)
            indexPhotosH.sort(key=lambda x: len(adjIndex[x]))
    
    # Create the album from the chosen path
    inverse_path = [-2] * len(indexPhotosH)
    fin_path = []
    for i in range(len(indexPhotosH)):
        if path[i] == -1:
            fin_path.append(i)
        else:
            inverse_path[path[i]] = i
    
    global alb
    alb = {'index': [], 'score': 0}
    used = [False] * len(indexPhotosH)
    
    # Process the final path
    for i in fin_path:
        j = i
        while j >= 0 and not used[j]:
            alb['index'].append((j, -1))
            used[j] = True
            j = inverse_path[j]
    
    for i in range(len(indexPhotosH)):
        j = i
        while j >= 0 and not used[j]:
            alb['index'].append((j, -1))
            used[j] = True
            j = inverse_path[j]

# Main function
def main():
    start_time = time.time()
    print("Reading from file...")
    read_file("input/1_binary_landscapes.txt")
    
    print("Solving the problem...")
    solve()
    
    print("Writing to file...")
    write_album("output/1_binary_landscapes.txt")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(int(elapsed_time), 60)
    
    print(f"Score: {alb['score']}")
    print(f"Elapsed time: {minutes}min {seconds}s")

if __name__ == "__main__":
    main()
