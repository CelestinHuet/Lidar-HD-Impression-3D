from sommet import Sommet
from face import Face


class Cube:

    compte = 0

    def __init__(self, x, y, z, size, i_x, i_y, i_z) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.i_x = i_x
        self.i_y = i_y
        self.i_z = i_z
        self.size = size
        self.id = Cube.compte
        Cube.compte += 1

        self.faces = []

    def add_face(self, face):
        self.faces.append(face)

    def has_voisin(self, struct, dx, dy, dz):
        i_x_max = len(struct)
        i_y_max = len(struct[0])
        i_z_max = len(struct[0][0])

        j_x = self.i_x + dx
        j_y = self.i_y + dy
        j_z = self.i_z + dz

        if j_x < 0 or j_x >= i_x_max:
            return False
        
        if j_y < 0 or j_y >= i_y_max:
            return False
        
        if j_z < 0 or j_z >= i_z_max:
            return False
        
        if struct[j_x][j_y][j_z] is None: 
            return False
        
        return True
    

    def get_or_create_sommets(self, sommets, x, y, z):
        #for sommet in sommets:
        #    if sommet.x == x and sommet.y == y and sommet.z == z:
        #        return sommet, sommets
            
        sommet = Sommet(x, y, z)
        sommets.append(sommet)
        return sommet, sommets

    

    def create_face_dx(self, dx, faces, sommets, liste_faces_x):
        sommets_face = []
        r = self.size / 2
        coords = [[self.x + dx*r, self.y - r, self.z -r],
                  [self.x + dx*r, self.y + r, self.z -r],
                  [self.x + dx*r, self.y + r, self.z +r],
                  [self.x + dx*r, self.y - r, self.z +r]]
        for coord in coords:
            sommet, sommets = self.get_or_create_sommets(sommets, coord[0], coord[1], coord[2])
            sommets_face.append(sommet)
        face = Face(sommets_face)
        faces.append(face)
        if dx==1:
            liste_faces_x.add_face(face, self.i_x+1, self.i_y, self.i_z)
        else:
            liste_faces_x.add_face(face, self.i_x, self.i_y, self.i_z)

        return sommets, faces, liste_faces_x
        

    def create_face_dy(self, dy, faces, sommets, liste_faces_y):
        sommets_face = []
        r = self.size / 2
        coords = [[self.x - r, self.y + dy* r, self.z -r],
                  [self.x + r, self.y + dy* r, self.z -r],
                  [self.x + r, self.y + dy* r, self.z +r],
                  [self.x - r, self.y + dy* r, self.z +r]]
        for coord in coords:
            sommet, sommets = self.get_or_create_sommets(sommets, coord[0], coord[1], coord[2])
            sommets_face.append(sommet)
        
        
        face = Face(sommets_face)
        faces.append(face)

        if dy==1:
            liste_faces_y.add_face(face, self.i_x, self.i_y+1, self.i_z)
        else:
            liste_faces_y.add_face(face, self.i_x, self.i_y, self.i_z)
        return sommets, faces, liste_faces_y
    

    def create_face_dz(self, dz, faces, sommets, liste_faces_z):
        sommets_face = []
        r = self.size / 2
        coords = [[self.x - r, self.y - r, self.z + dz * r],
                  [self.x - r, self.y + r, self.z + dz * r],
                  [self.x + r, self.y + r, self.z + dz * r],
                  [self.x + r, self.y - r, self.z + dz * r]]
        for coord in coords:
            sommet, sommets = self.get_or_create_sommets(sommets, coord[0], coord[1], coord[2])
            sommets_face.append(sommet)
        face = Face(sommets_face)
        faces.append(face)

        if dz==1:
            liste_faces_z.add_face(face, self.i_x, self.i_y, self.i_z+1)
        else:
            liste_faces_z.add_face(face, self.i_x, self.i_y, self.i_z)
        return sommets, faces, liste_faces_z

    def creer_faces(self, struct, faces, sommets, liste_faces_x, liste_faces_y, liste_faces_z):
        liste = [-1, 1]
        for dx in liste:
            if not self.has_voisin(struct, dx, 0, 0):
                sommets, faces, liste_faces_x = self.create_face_dx(dx, faces, sommets, liste_faces_x)
           
        for dy in liste:
            if not self.has_voisin(struct, 0, dy, 0):
                sommets, faces, liste_faces_y = self.create_face_dy(dy, faces, sommets, liste_faces_y)
        
        for dz in liste:
            if not self.has_voisin(struct, 0, 0, dz):
                sommets, faces, liste_faces_z = self.create_face_dz(dz, faces, sommets, liste_faces_z)

        return sommets, faces, liste_faces_x, liste_faces_y, liste_faces_z


