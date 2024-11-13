from typing import List
from tqdm import tqdm
from sommet import Sommet
from face import Face

class Tranche:

    def __init__(self, size_i, size_j) -> None:
        self.size_i = size_i
        self.size_j = size_j

        self.array = [[None for j in range(size_j)] for i in range(size_i)] 
        self.done = [[False for j in range(size_j)] for i in range(size_i)]

    
    def add_face(self, i, j, face):
        self.array[i][j] = face

    def not_done(self, i, j):
        return self.array[i][j] is not None and not self.done[i][j]
    
    def ligne_suivante(self, i_0, i_max, j):
        if j >= self.size_j:
            return []
        faces = []
        for i in range(i_0, i_max):
            if self.not_done(i, j):
                faces.append(self.array[i][j])
            else:
                return []
            
        for i in range(i_0, i_max):
            self.done[i][j] = True
        return faces

    def do_ij(self, i, j):
        faces = []
        i_max = i
        while i_max<self.size_i and self.not_done(i_max, j):
            faces.append(self.array[i_max][j])
            self.done[i_max][j] = True
            i_max += 1

        ligne_suivante_ok = True
        j_max = j+1
        while ligne_suivante_ok:
            faces_suivantes = self.ligne_suivante(i, i_max, j_max)
            if len(faces_suivantes)==0:
                ligne_suivante_ok = False
            faces += faces_suivantes
            j_max += 1

        new_face = self.get_new_faces(faces)
        return new_face
    
    def get_new_faces(self, faces):

        x_min = 1e15
        x_max = -1e15
        y_min = 1e15
        y_max = -1e15
        z_min = 1e15
        z_max = -1e15
        for face in faces:
            x_min_1, x_max_1, y_min_1, y_max_1, z_min_1, z_max_1 = face.limite()
            x_min = min(x_min, x_min_1)
            x_max = max(x_max, x_max_1)
            y_min = min(y_min, y_min_1)
            y_max = max(y_max, y_max_1)
            z_min = min(z_min, z_min_1)
            z_max = max(z_max, z_max_1)

        if abs(x_min-x_max)<1e-5:
            sommets = [
                Sommet(x_min, y_min, z_min),
                Sommet(x_min, y_min, z_max),
                Sommet(x_min, y_max, z_max),
                Sommet(x_min, y_max, z_min)
            ]
        elif abs(y_min-y_max)<1e-5:
            sommets = [
                Sommet(x_min, y_min, z_min),
                Sommet(x_min, y_min, z_max),
                Sommet(x_max, y_min, z_max),
                Sommet(x_max, y_min, z_min)
            ] 
        elif abs(z_min-z_max)<1e-5:
            sommets = [
                Sommet(x_min, y_min, z_min),
                Sommet(x_min, y_max, z_min),
                Sommet(x_max, y_max, z_min),
                Sommet(x_max, y_min, z_min)
            ]                
        else:
            for face in faces:
                print(face)
            print("Erreur : ", x_min, x_max, y_min, y_max, z_min, z_max)
        return Face(sommets)

    def simplifier(self):
        faces = []
        for i in range(self.size_i):
            for j in range(self.size_j):
                if self.not_done(i, j):
                    faces.append(self.do_ij(i, j))
        return faces


class ListeFacesX:
    """
    Un empilement d'étages
    """

    def __init__(self, size_x, size_y, size_z) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.tranches:List[Tranche] = [Tranche(size_y, size_z) for i in range(size_x)]

    def add_face(self, face, i_x, i_y, i_z):
        self.tranches[i_x].add_face(i_y, i_z, face)

    def simplifier(self):
        faces = []
        print("Simplification des faces X")
        for tranche in tqdm(self.tranches):
            faces += tranche.simplifier()
        print("X : ", len(faces))
        return faces


class ListeFacesY:
    """
    Un empilement d'étages
    """

    def __init__(self, size_x, size_y, size_z) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.tranches:List[Tranche] = [Tranche(size_z, size_x) for i in range(size_y)]

    def add_face(self, face, i_x, i_y, i_z):
        self.tranches[i_y].add_face(i_z, i_x, face)

    def simplifier(self):
        faces = []
        print("Simplification des faces Y")
        for tranche in tqdm(self.tranches):
            faces += tranche.simplifier()
        print("Y : ", len(faces))
        return faces

class ListeFacesZ:
    """
    Un empilement d'étages
    """

    def __init__(self, size_x, size_y, size_z) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.tranches:List[Tranche] = [Tranche(size_x, size_y) for i in range(size_z)]

    def add_face(self, face, i_x, i_y, i_z):
        self.tranches[i_z].add_face(i_x, i_y, face)

    def simplifier(self):
        faces = []
        print("Simplification des faces Z")
        for tranche in tqdm(self.tranches):
            faces += tranche.simplifier()
        print("Z : ", len(faces))
        return faces

