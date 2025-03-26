import os

dir = os.path.abspath(os.curdir)

def get_obj(name):
    vertex, faces = [], []
    with open(dir + "\\" + name + ".obj") as f:
        for line in f:
            if line.startswith('v '):
                vertex.append([float(i) for i in line.split()[1:]] + [1])
            elif line.startswith('f'):
                faces_ = line.split()[1:]
                faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])

    map_list = []

    c = 0

    print(len(vertex))
    print(len(faces))

    for i in range(len(faces)):
        map_list.append([])
        for j in range(3):
            map_list[i].append(round(vertex[faces[i][j]] [0] * 20, 1))
            map_list[i].append(round(vertex[faces[i][j]] [2] * 20, 1))
            map_list[i].append(round(vertex[faces[i][j]] [1] * -20, 1))

    print(len(map_list))
    #print(map_list)

    return map_list


def load_model():
    name = "model"

    return get_obj(name)