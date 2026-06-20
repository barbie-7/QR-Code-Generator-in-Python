# imports
import sys
import stdio
import stdarray
import stddraw

from qrcodelib import get_error_codewords, get_format_information_bits


def draw_qr_grid(qr_grid):
    size = len(qr_grid)
    border = 4  
    total_cells = size + 2 * border

    stddraw.setCanvasSize(600, 600)
    stddraw.setXscale(0, total_cells)
    stddraw.setYscale(0, total_cells)
    stddraw.clear(stddraw.WHITE)

    for i in range(size):
        for j in range(size):
            if qr_grid[i][j] == 1:
                stddraw.setPenColor(stddraw.BLACK)
            else:
                stddraw.setPenColor(stddraw.WHITE)
            stddraw.filledSquare(j + border + 0.5, total_cells - (i + border) - 0.5, 0.5)

    stddraw.save("output.png")
    # stddraw.show()



def print_qr_grid(qr_grid):
    for i in range(len(qr_grid)):
        for j in range(len(qr_grid)):
            stdio.write(str(qr_grid[i][j]) + ' ')
        stdio.writeln('')




def make_position_pattern(pos_square_size):
    size = pos_square_size
    if (size < 4) or ((size % 2 != 0)):
        stdio.writeln("ERROR: Invalid position pattern size argument: " + str(size))
        return None
    else:
        patterntemp = stdarray.create2D(4, 4, 1)
        for row in range(4):
            for col in range(4):
                if (row == 4 - 1) or (col == 4 - 1):
                    patterntemp[row][col] = 0

        pattern = patterntemp

        if size > 4:
            tempg = 4

            while tempg < size:
                grid = tempg + 2

                if (size % 4 == 0):
                    pattern = stdarray.create2D(grid, grid, 9)
                else:
                    pattern = stdarray.create2D(grid, grid, 8)

                for row in range(tempg):
                    for col in range(tempg):
                        pattern[row + 1][col + 1] = patterntemp[row][col]

                if grid % 4 == 0:
                    for row in range(grid):
                        for col in range(grid):
                            if row == 0 or col == 0:
                                pattern[row][col] = 1
                            if row == grid - 1 or col == grid - 1:
                                pattern[row][col] = 0
                else:
                    for row in range(grid):
                        for col in range(grid):
                            if row == 0 or col == 0:
                                pattern[row][col] = 0
                            if row == grid - 1 or col == grid - 1:
                                pattern[row][col] = 1

                tempg = grid
                patterntemp = pattern

        return pattern




def make_alignment_pattern(align_square_size):
    if align_square_size <= 0 or (align_square_size - 1) % 4 != 0:
        stdio.writeln("ERROR: Invalid alignment pattern size argument: "+ str(align_square_size))
        return None

    pattern = stdarray.create2D(align_square_size, align_square_size, 0)

    for row in range(align_square_size):
        for col in range(align_square_size):
            if row == 0 or col == 0 or row == align_square_size - 1 or col == align_square_size - 1:
                pattern[row][col] = 1
            for b in range(1, align_square_size // 4):
                if (align_square_size - 1 - 2 * b == row or row == 2 * b) and (row % 2 == 0) and ((1.9 * b) < col < align_square_size - 2 * b):
                    pattern[row][col] = 1
                if (align_square_size - 1 - 2 * b == col or col == 2 * b) and (col % 2 == 0) and ((1.9 * b) < row < align_square_size - 2 * b):
                    pattern[row][col] = 1

    pattern[align_square_size // 2][align_square_size // 2] = 1
    return pattern


def rotate_pattern_clockwise(data):
    if data:
        n = len(data)
    else:
        n = 0

    for i in range(n):
        for j in range(i + 1, n):
            data[i][j], data[j][i] = data[j][i], data[i][j]

    for i in range(n):
        data[i] = data[i][::-1]

    return data





def add_data_at_anchor(qr_grid, x_cordinate, y_cordinate, data):
    size = len(data)

    for i in range(size):
        for j in range(size):
            target_x = x_cordinate + j  # target column
            target_y = y_cordinate + i  # target row

            # don't go out of bounds of the QR grid
            if 0 <= target_y < len(qr_grid) and 0 <= target_x < len(qr_grid[0]):
                qr_grid[target_y][target_x] = data[i][j]


def place_patterns(qr_grid, size, pos_size, align_size):

    # Place position patterns
    pos_pattern = make_position_pattern(pos_size)
    add_data_at_anchor(qr_grid, 0, 0, pos_pattern)

    rotate90 = rotate_pattern_clockwise(pos_pattern)
    add_data_at_anchor(qr_grid, size - pos_size, 0, rotate90)

    rotate180 = rotate_pattern_clockwise(rotate90)
    rotate270 = rotate_pattern_clockwise(rotate180)
    add_data_at_anchor(qr_grid, 0, size - pos_size, rotate270)

    # Place alignment pattern
    align_pattern = make_alignment_pattern(align_size)
    align_x = size - pos_size - 1
    align_y = size - pos_size - 1
    add_data_at_anchor(qr_grid, align_x, align_y, align_pattern)


def apply_mask(qr_grid, mask_id, pos_square_size, align_square_size):
    if qr_grid is None:
        sys.exit(0)
    else:
        size = len(qr_grid)

        if mask_id == '000':
            return qr_grid

        elif mask_id == '001':
            for x in range(size):
                for y in range(size):
                    if x % 2 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '010':
            for x in range(size):
                for y in range(size):
                    if y % 3 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '011':
            for x in range(size):
                for y in range(size):
                    if (x + y) % 3 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '100':
            for x in range(size):
                for y in range(size):
                    if (y // 3 + x // 2) % 2 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '101':
            for x in range(size):
                for y in range(size):
                    if (x * y) % 2 + (x * y) % 3 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '110':
            for x in range(size):
                for y in range(size):
                    if ((x * y) % 2 + (x * y) % 3) % 2 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        elif mask_id == '111':
            for x in range(size):
                for y in range(size):
                    if ((x + y) % 2 + (x * y) % 3) % 2 == 0:
                        if qr_grid[x][y] == 1:
                            qr_grid[x][y] = 0
                        elif qr_grid[x][y] == 0:
                            qr_grid[x][y] = 1

        place_patterns(qr_grid, size, pos_square_size, align_square_size)

    return qr_grid







def encode_snake(size, message, pos_square_size, align_square_size):


    if len(message) > 255:
        stdio.writeln("ERROR: Payload too large")
        sys.exit(1)
    required_bits = size * size - pos_square_size * pos_square_size * 3 - align_square_size* align_square_size

    mode_indicator = "0100"

    # ensures length is always stored as 8-bit binary
    binary_message_length = "0" * (8 - len(bin(len(message))[2:])) + bin(len(message))[2:]

    encoded_message = ""
    for character in message:

        if 255 < ord(character) or 32 > ord(character):
            stdio.writeln("ERROR: Payload too large")
            sys.exit(1)

        binary_char = bin(ord(character))[2:]  # Get binary representation without '0b'
        binary_char = "0" * (8 - len(binary_char)) + binary_char  # Pad to 8 bits
        encoded_message += binary_char


    end_marker = "0000"
    bit_sequence = mode_indicator + binary_message_length + encoded_message + end_marker

    while len(bit_sequence) % 8 != 0:
        bit_sequence += "0"

    padding_sequence = ""
    padding_bytes = ["11101100", "00010001"]
    index = 0

    if len(bit_sequence) > required_bits:
        stdio.writeln("ERROR: Payload too large")
        sys.exit(1)

    while len(bit_sequence) + len(padding_sequence) < required_bits:
        padding_sequence += padding_bytes[index]
        index = (index + 1) % 2

    
    snake_sequence = bit_sequence + padding_sequence



    qr_grid = stdarray.create2D(size, size, 9)

    place_patterns(qr_grid,size,pos_square_size,align_square_size)

    count = 0
    for i in range(size):
        if i % 2 == 0:
            # Fill left to right on even rows
            for j in range(size):
                if qr_grid[i][j] == 9:  
                    if count < len(snake_sequence):  # Avoid index error
                        qr_grid[i][j] = int(snake_sequence[count])
                        count += 1
        else:
            # Fill right to left on odd rows
            for j in range(size - 1, -1, -1):
                if qr_grid[i][j] == 9:  
                    if count < len(snake_sequence):  # Avoid index error
                        qr_grid[i][j] = int(snake_sequence[count])
                        count += 1              
                    
    return qr_grid

def encode_snake2(size, message, pos_square_size, align_square_size):

    if len(message) > 255:
        stdio.writeln("ERROR: Payload too large")
        sys.exit(1)
    required_bits = size * size - pos_square_size * pos_square_size * 3 - align_square_size* align_square_size - 19

    mode_indicator = "0100"

    # ensures length is always stored as 8-bit binary
    binary_message_length = "0" * (8 - len(bin(len(message))[2:])) + bin(len(message))[2:]

    encoded_message = ""
    for character in message:

        if 255 < ord(character) or 32 > ord(character):
            stdio.writeln("ERROR: Payload too large")
            sys.exit(1)

        binary_char = bin(ord(character))[2:]  # Get binary representation without '0b'
        binary_char = "0" * (8 - len(binary_char)) + binary_char  # Pad to 8 bits
        encoded_message += binary_char


    end_marker = "0000"
    bit_sequence = mode_indicator + binary_message_length + encoded_message + end_marker

    while len(bit_sequence) % 8 != 0:
        bit_sequence += "0"

    padding_sequence = ""
    padding_bytes = ["11101100", "00010001"]
    index = 0

    if len(bit_sequence) > required_bits:
        stdio.writeln("ERROR: Payload too large")
        sys.exit(1)

    while len(bit_sequence) + len(padding_sequence) < required_bits:
        padding_sequence += padding_bytes[index]
        index = (index + 1) % 2

    
    snake_sequence = bit_sequence + padding_sequence



    qr_grid = stdarray.create2D(size, size, 9)

    place_patterns(qr_grid,size,pos_square_size,align_square_size)

    count = 0
    for i in range(size):
        if i % 2 == 0:
            # Fill left to right on even rows
            for j in range(size):
                if qr_grid[i][j] == 9:  
                    if count < len(snake_sequence):  # Avoid index error
                        qr_grid[i][j] = int(snake_sequence[count])
                        count += 1
        else:
            # Fill right to left on odd rows
            for j in range(size - 1, -1, -1):
                if qr_grid[i][j] == 9:  
                    if count < len(snake_sequence):  # Avoid index error
                        qr_grid[i][j] = int(snake_sequence[count])
                        count += 1              
                    
    return qr_grid


def validate_int(value, name):
    if not value.isdigit():
        stdio.writeln("ERROR: Invalid " + name + " argument: " + value)
        sys.exit(1)  # Exit the script with an error
    return int(value)


def main(args):
    if len(sys.argv) < 5:
        stdio.writeln("ERROR: Too few arguments")
        sys.exit(1)
    if len(sys.argv) > 5:
        stdio.writeln("ERROR: Too many arguments")
        sys.exit(1)

    
    encoding_parameter  = validate_int(sys.argv[1], "encoding parameter")  
    size = validate_int(sys.argv[2], "size")
    pos_square_size = validate_int(sys.argv[3], "position pattern size")
    align_square_size = validate_int(sys.argv[4], "alignment pattern size")

    if (0 > int(encoding_parameter)) or (int(encoding_parameter) >= 32):
        stdio.writeln("ERROR: Invalid encoding argument: " + str(encoding_parameter))
        sys.exit(1)

    binary = ''
    # Compute v as the largest power of 2 <= n.
    v = 1
    while v <= encoding_parameter // 2:
        v *= 2
    # Cast out powers of 2 in decreasing order.
    while v > 0:
        if encoding_parameter < v:
            binary += '0'
        else:
            binary += '1'
            encoding_parameter -= v
        v //= 2
    if len(binary) != 5:
        for i in range(5 - len(binary)):
            binary = '0' + binary

    mask_id = binary[2:]

    # Read piped input message
    message = stdio.readAll().rstrip('\n')

    if size < 10 or size > 48:
        stdio.writeln("ERROR: Invalid size argument: " + str(size))
        sys.exit(1)

    if (pos_square_size < 4) or ((pos_square_size % 2 != 0)):
        stdio.writeln(
            "ERROR: Invalid position pattern size argument: " + str(pos_square_size))
        sys.exit(1)
    if align_square_size <= 0 or (align_square_size - 1) % 4 != 0:
        stdio.writeln(
            "ERROR: Invalid alignment pattern size argument: " + str(align_square_size))
        sys.exit(1)

    if (pos_square_size > align_square_size) and (size <= pos_square_size * 2):
        stdio.writeln('ERROR: Alignment/position pattern out of bounds')
        sys.exit(1)

    elif (pos_square_size < align_square_size) and (size <= pos_square_size + align_square_size):
        stdio.writeln('ERROR: Alignment/position pattern out of bounds')
        sys.exit(1)
    elif (pos_square_size + 1 < align_square_size ):
        stdio.writeln('ERROR: Alignment/position pattern out of bounds')
        sys.exit(1)
    


    if binary[1] == '1' and binary[0] == '0':
        if size != 25:
            stdio.writeln('ERROR: Invalid size argument: ' + str(size))
            sys.exit(1)
        if align_square_size != 5:
            stdio.writeln(
                "ERROR: Invalid alignment pattern size argument: " + str(align_square_size))
            sys.exit(1)
        if pos_square_size != 8:
            stdio.writeln(
                "ERROR: Invalid position pattern size argument: " + str(pos_square_size))
            sys.exit(1)
            
        qr_grid = encode_snake2(size, message, pos_square_size, align_square_size)
        apply_mask(qr_grid, mask_id, pos_square_size, align_square_size)
        print_qr_grid(qr_grid)

    if binary[1] == '1' and binary[0] == '1':
        if size != 25:
            stdio.writeln('ERROR: Invalid size argument: ' + str(size))
            sys.exit(1)
        if align_square_size != 5:
            stdio.writeln(
                "ERROR: Invalid alignment pattern size argument: " + str(align_square_size))
            sys.exit(1)
        if pos_square_size != 8:
            stdio.writeln(
                "ERROR: Invalid position pattern size argument: " + str(pos_square_size))
            sys.exit(1)

        qr_grid = encode_snake2(size, message, pos_square_size, align_square_size)
        
        apply_mask(qr_grid, mask_id, pos_square_size, align_square_size)
        draw_qr_grid(qr_grid)

    # Snake layout
    if binary[1] == '0' and binary[0] == '0':
        qr_grid = encode_snake(size, message, pos_square_size, align_square_size)
        
        apply_mask(qr_grid, mask_id, pos_square_size, align_square_size)
        print_qr_grid(qr_grid)

    if binary[1] == '0' and binary[0] == '1':
        qr_grid = encode_snake(size, message, pos_square_size, align_square_size)
        apply_mask(qr_grid, mask_id, pos_square_size, align_square_size)
        draw_qr_grid(qr_grid)

 


if __name__ == "__main__":
    """USage: echo 'message' | python3 SU29381487.py 26 25 8 5'"""
    main(sys.argv)
