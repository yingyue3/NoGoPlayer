"""
gain_weight.py

gain the original weight of each move from the txt file

This file contributed to the group.
"""

class weight_map():
    def __init__(self):
        self.weight_map = {}
        file1 = open('weights.txt', 'r')
        while True:
            line = file1.readline()

            if not line:
                break
            words = line.split()
            self.weight_map[int(words[0])] = float(words[1])
        file1.close()


if __name__ == "__main__":
    map = weight_map()
    print(map.weight_map[0])
