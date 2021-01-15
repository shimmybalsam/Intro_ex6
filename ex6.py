import copy
import sys
import mosaic
NUMBER_OF_ARGUMENTS = 5
ERROR_MESSAGE = "Wrong number of parameters. The correct usage is: \
ex6.py <image_source> <images_dir> <output_name> <tile_height> \
<num_candidates>"

def compare_pixel(pixel1, pixel2):
    """Calculates and returns the sum of the absolute differences between the
    red, green and blue values of two pixels"""
    r = abs(pixel1[0] - pixel2[0])
    g = abs(pixel1[1] - pixel2[1])
    b = abs(pixel1[2] - pixel2[2])
    return r + g + b


def compare(image1, image2):
    """Calculates and returns the distance between two pictures, whilst
    comparing each pixel to pixel as explaind in the previous function."""
    row = min(len(image1),len(image2))
    column = min(len(image1[0]),len(image2[0]))
    sum_distances = 0
    for i in range(row):
        for j in range(column):
            sum_distances += compare_pixel(image1[i][j],image2[i][j])
    return sum_distances


def get_piece(image, upper_left, size):
    """Returns a cropped piece of a given image, based on a starting point
    within the image and a given size of said cropped piece, given by the
    user. If said willed piece extends the border of the original image, the
    function will return a smaller piece, starting at the users will and
    ending at the image's borderline"""
    piece = []
    rows_border = min(len(image), size[0]+upper_left[0])
    columns_border = min(len(image[0]), upper_left[1]+ size[1])
    for i in range(upper_left[0],rows_border):
            piece.append(image[i][upper_left[1]:columns_border])
    return piece


def set_piece(image, upper_left, piece):
    """This function doesn't return anything, but it takes a given piece
    (made by the previous function) and replaces the equivilant area in the
    original image with the given piece."""
    rows_border = min(len(image), upper_left[0] + len(piece))
    columns_border = min(len(image[0]), upper_left[1] + len(piece[0]))
    for i in range(upper_left[0],rows_border):
        for j in range(upper_left[1],columns_border):
            image[i][j] = piece[i-upper_left[0]][j-upper_left[1]]


def average(image):
    """Returns a tuple of the average values of red, green and blue values
    within an entire image, in said order"""
    red_avg = 0
    green_avg = 0
    blue_avg = 0
    pixel_count = 0
    for i in range(len(image)):
        for j in range(len(image[0])):
            red_avg += image[i][j][0]
            green_avg += image[i][j][1]
            blue_avg += image[i][j][2]
            pixel_count += 1
    red_avg = float(red_avg/pixel_count)
    green_avg = float(green_avg/pixel_count)
    blue_avg = float(blue_avg/pixel_count)
    return (red_avg, green_avg, blue_avg)


def preprocess_tiles(tiles):
    """Recieves a list of tiles, and returns a list of averages per tile, so
    that the index of each tile is equivalent to the index of it's average"""
    avg_per_tile = []
    for pic in tiles:
        avg_per_tile.append(average(pic))
    return avg_per_tile

def help_new_min(list_of_averages):
    """An original function which finds the index of the smallest object in a
     list. This function will be used in order to make the get_best_tiles
     shorter and more efficient"""
    temp = 0
    for i in range(1,len(list_of_averages)):
        if list_of_averages[i] < list_of_averages[temp]:
            temp = i
    return temp

def get_best_tiles(objective, tiles, averages, num_candidates):
    """Receives an image, a list of tiles and a list of those tiles averages,
    and also a integer number which will be used as a length of a new list
    which will be returned once containing the tiles which averages are
    closest to the average of the original image."""
    objective_avg = average(objective)
    best_candidates = []
    best_avgs = []
    tile_copies = tiles[:]
    for i in range(len(tiles)):
        best_avgs.append(compare_pixel(averages[i],objective_avg))
    while len(best_candidates) < num_candidates:
        min_avg_index = help_new_min(best_avgs)
        best_candidates.append(tile_copies[min_avg_index])
        tile_copies.pop(min_avg_index)
        best_avgs.pop(min_avg_index)
    return best_candidates


def choose_tile(piece, tiles):
    """Returns the tile, out of a list of given tiles,
    which is closest in average to a given piece."""
    smallest_difference = compare(piece,tiles[0])
    chosen_one = tiles[0]
    for pic in tiles:
        if compare(piece,pic) < smallest_difference:
            smallest_difference = compare(piece,pic)
            chosen_one = pic
    return chosen_one


def make_mosaic(image, tiles, num_candidates):
    """Receives an image, a list of tiles and a length of a new wanted list,
    and using previous function, recreates the entire original given image as a
    mosaic, piece by piece. Once completed, returns said mosaic."""
    mosaic_image = copy.deepcopy(image)
    HEIGHT = len(tiles[0])
    WIDTH = len(tiles[0][0])
    averages = preprocess_tiles(tiles)
    for i in range(0,len(image),HEIGHT):
        for j in range(0,len(image[0]),WIDTH):
            new_piece = get_piece(mosaic_image,(i,j),(HEIGHT,WIDTH))
            best_tiles =get_best_tiles(new_piece,tiles,averages,num_candidates)
            winner_tile = choose_tile(new_piece,best_tiles)
            set_piece(mosaic_image,(i,j),winner_tile)
    return mosaic_image

if __name__ == "__main__":
    #The main calls all the previous functions, using specific arguments,
    #in order to create the wanted mosaic, so long as the amount and type of
    #arguments are as needed.
    if len(sys.argv) != NUMBER_OF_ARGUMENTS+1:
        print(ERROR_MESSAGE)
    else:
        image_source = sys.argv[1]
        images_dir = sys.argv[2]
        output_name = sys.argv[3]
        tile_height = int(sys.argv[4])
        num_candidates = int(sys.argv[5])
        image = mosaic.load_image(image_source)
        tiles = mosaic.build_tile_base(images_dir,tile_height)
        real_mosaic = make_mosaic(image,tiles,num_candidates)
        mosaic.save(real_mosaic,output_name)