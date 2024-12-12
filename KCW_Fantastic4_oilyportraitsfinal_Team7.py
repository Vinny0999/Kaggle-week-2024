import os
import json
import time
from tqdm import tqdm
from bitarray import bitarray
from typing import List, Tuple, Dict

INF = 99999999


class Photo:
    def __init__(self, index: int, photo_type: str, tags: List[str]):
        self.index = index
        self.type = photo_type
        self.tags = tags
        self.hash_tags = bitarray(500)  # Simulate bitset with size 500
        self.hash_tags.setall(False)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "type": self.type,
            "tags": self.tags,
            "hash_tags": self.hash_tags.to01()  # Convert bitarray to string for JSON serialization
        }

    @staticmethod
    def from_dict(data: dict) -> 'Photo':
        photo = Photo(index=data["index"], photo_type=data["type"], tags=data["tags"])
        photo.hash_tags = bitarray(data["hash_tags"])  # Convert string back to bitarray
        return photo


class SlideShow:
    def __init__(self, photo1: Photo, photo2: Photo = None):
        self.index1 = photo1.index
        self.index2 = photo2.index if photo2 else -1
        self.tags = photo1.hash_tags.copy()
        if photo2:
            self.tags |= photo2.hash_tags


class Album:
    def __init__(self):
        self.slides = []
        self.score = 0

    def add_slide(self, slide: SlideShow):
        if self.slides:
            prev_tags = self.slides[-1].tags
            self.score += calculate_interest(prev_tags, slide.tags)
        self.slides.append(slide)


def calculate_interest(tags1: bitarray, tags2: bitarray) -> int:
    intersection_count = (tags1 & tags2).count()
    count1 = tags1.count()
    count2 = tags2.count()
    return min(intersection_count, count1 - intersection_count, count2 - intersection_count)


def read_input(file_path: str) -> Tuple[List[Photo], Dict[str, int]]:
    with open(file_path, "r") as f:
        num_photos = int(f.readline().strip())
        photos = []
        tag_map = {}
        for i in tqdm(range(num_photos), desc="Reading Photos", unit="photo"):
            line = f.readline().strip().split()
            photo_type = line[0]
            tags = line[2:]
            photos.append(Photo(index=i, photo_type=photo_type, tags=tags))
            for tag in tags:
                if tag not in tag_map:
                    tag_map[tag] = len(tag_map)
        return photos, tag_map


def save_to_json(file_path: str, photos: List[Photo], tag_map: Dict[str, int]):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = {
        "photos": [photo.to_dict() for photo in photos],
        "tag_map": tag_map,
    }
    with open(file_path, "w") as f:
        json.dump(data, f)


def load_from_json(file_path: str) -> Tuple[List[Photo], Dict[str, int]]:
    with open(file_path, "r") as f:
        data = json.load(f)
        photos = [Photo.from_dict(photo_data) for photo_data in data["photos"]]
        tag_map = data["tag_map"]
    return photos, tag_map


def hash_photos(photos: List[Photo], tag_map: Dict[str, int]):
    for photo in tqdm(photos, desc="Tags Hashing Photos", unit="photo"):
        for tag in photo.tags:
            photo.hash_tags[tag_map[tag]] = True


def solve(photos: List[Photo]) -> Album:
    horizontal_photos = [p for p in photos if p.type == "L"]
    vertical_photos = [p for p in photos if p.type == "P"]

    # Pair vertical photos based on tag similarity
    vertical_photos.sort(key=lambda p: p.hash_tags.count())
    paired_verticals = []
    while len(vertical_photos) > 1:
        paired_verticals.append(SlideShow(vertical_photos.pop(), vertical_photos.pop()))

    slides = [SlideShow(photo) for photo in horizontal_photos] + paired_verticals

    # Optimize slide arrangement
    album = Album()
    used = set()
    current_slide = slides[0]
    album.add_slide(current_slide)
    used.add(current_slide.index1)
    if current_slide.index2 != -1:
        used.add(current_slide.index2)

    for _ in tqdm(range(1, len(slides)), desc="Creating Album", unit="slide"):
        best_slide = None
        best_interest = -INF

        for slide in slides:
            if slide.index1 not in used and (slide.index2 == -1 or slide.index2 not in used):
                current_interest = calculate_interest(current_slide.tags, slide.tags)
                if current_interest > best_interest:
                    best_interest = current_interest
                    best_slide = slide

        if best_slide:
            album.add_slide(best_slide)
            used.add(best_slide.index1)
            if best_slide.index2 != -1:
                used.add(best_slide.index2)
            current_slide = best_slide

    return album


def write_output(file_path: str, album: Album):
    """Writes the album output to the specified file."""
    with open(file_path, "w") as f:
        f.write(f"{len(album.slides)}\n")
        for slide in album.slides:
            if slide.index2 != -1:
                f.write(f"{slide.index1} {slide.index2}\n")
            else:
                f.write(f"{slide.index1}\n")


def main():
    start_time = time.time()
    input_file = "./inputs/110_oily_portraits.txt"
    json_file = "./pycache/op/photos_data.json"
    output_file = "./outputs/output_110_oily_portraits.txt"

    print("Reading input...")
    if os.path.exists(json_file):
        print("Loading data from JSON cache...")
        photos, tag_map = load_from_json(json_file)
    else:
        photos, tag_map = read_input(input_file)
        save_to_json(json_file, photos, tag_map)

    print("Hashing Tags in photos...")
    hash_photos(photos, tag_map)

    print("Solving the problem...")
    album = solve(photos)

    print("Writing output...")
    os.makedirs("./outputs", exist_ok=True)
    write_output(output_file, album)

    elapsed_time = time.time() - start_time
    print(f"Execution Time: {elapsed_time:.2f} seconds")
    print(f"Album Score: {album.score}")


if __name__ == "__main__":
    main()
