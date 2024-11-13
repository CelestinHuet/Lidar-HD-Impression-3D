from laspy import Bounds, CopcReader, ScaleAwarePointRecord, LasHeader, LasData, PackedPointRecord, PointFormat
import geopandas as gpd
from shapely import Polygon
import numpy as np
from cube import Cube
from tqdm import tqdm
from liste_face_x import ListeFacesX, ListeFacesY, ListeFacesZ
from liste_sommets import ListeSommets
from statistics import median
import argparse
import os


def open_geopandas(path):
    gdf = gpd.read_file(path)
    return gdf.iloc[0].geometry


def get_bounds(polygon:Polygon)->Bounds:
    x, y = polygon.exterior.coords.xy
    x_min = min(x)
    y_min = min(y)
    x_max = max(x)
    y_max = max(y)
    bounds = Bounds(np.array([x_min, y_min]), np.array([x_max, y_max]))
    return bounds


def open_points(filename:str, bounds:Bounds)->ScaleAwarePointRecord:
    with CopcReader.open(filename) as crdr:
        query = crdr.query(bounds)
    return query


def filter_points(points):
    indices = np.where(np.logical_or(np.logical_or(points["classification"]==2, points["classification"]==6),  points["classification"]==1))
    points_valides = points[indices]

    #20 cm : on garde tout
    #1 mètres : on garde la moitié
    if resolution >= 0.33:
        nb_points = points_valides.shape[0]
        nb_keep = int(nb_points /( resolution**2 / 0.33**2 / 2))

        print(f"On conserve {nb_keep} points parmi les {nb_points} points.")

        idx = np.random.randint(nb_points, size=nb_keep)
        points_valides = points_valides[idx]

    return points_valides


def save_points(points:ScaleAwarePointRecord):
    header = LasHeader(point_format=6)
    new_las = LasData(header=header, points=points)
    new_las.write("lidar_extraction.las")

def save_points_from_numpy(points:np.array):
    header = LasHeader(point_format=6)
    aPackedpointRecord = PackedPointRecord(data=points, point_format=PointFormat(6))
    new_las = LasData(header=header, points=aPackedpointRecord)
    new_las.write("lidar_bati_sol.las")


def get_limites_cube(points:np.array, resolution:float, echelle):
    x_min = np.min(points["X"])
    x_max = np.max(points["X"])
    y_min = np.min(points["Y"])
    y_max = np.max(points["Y"])
    z_min = np.min(points["Z"]) - 10*resolution*100 # On ajoute un socle de dix cubes
    z_max = np.max(points["Z"])
    print(f"Taille en mètres : {(x_max-x_min)/100} x {(y_max-y_min)/100} x {(z_max-z_min)/100}")
    print(f"Taille en cubes : {int((x_max-x_min)/100/resolution)} x {int((y_max-y_min)/100/resolution)} x {int((z_max-z_min)/100/resolution)}")
    print(f"Taille de la maquette en mètres : {(x_max-x_min)/100*echelle} x {(y_max-y_min)/100*echelle} x {(z_max-z_min)/100*echelle}")    
    print(f"Taille d'un cube : {resolution*echelle} mètres")
    return x_min, x_max, y_min, y_max, z_min, z_max



def reconstruction(points, x_min, x_max, y_min, y_max, z_min, z_max, resolution):
    resolution = resolution*100

    i_x_max = int((x_max - x_min)/resolution)
    i_y_max = int((y_max - y_min)/resolution)
    i_z_max = int((z_max - z_min)/resolution)

    struct = [[[None for i_z in range(i_z_max)] for i_y in range(i_y_max)] for i_x in range(i_x_max)]
    espaces_vides = []

    print("Construction des cubes")
    for i_x in tqdm(range(i_x_max)):
        for i_y in range(i_y_max):
            x = x_min + i_x * resolution
            y = y_min + i_y * resolution

            selection_x = np.logical_and(points["X"]<=x+resolution, points["X"]>=x-resolution)
            selection_y = np.logical_and(points["Y"]<=y+resolution, points["Y"]>=y-resolution)
            selection = np.logical_and(selection_x, selection_y)
            indices = np.where(selection)
            points_dans_zone = points[indices]
            if points_dans_zone.shape[0] != 0:
                z_max_zone = np.max(points_dans_zone["Z"])

                i_z_max_zone = int((z_max_zone - z_min) / resolution)
                for i_z in range(i_z_max_zone):
                    
                    z = z_min + i_z * resolution
                    struct[i_x][i_y][i_z] = Cube(x, y, z, resolution, i_x, i_y, i_z)                    
            else:
                espaces_vides.append((i_x, i_y))

                
    struct = replace_espace_vide(struct, i_x_max, i_y_max, resolution, espaces_vides, x_min, y_min, z_min)
    return struct


def hauteur_voisine(struct, i, j):
    for compte, element in enumerate(struct[i][j]):
        if element is None:
            return compte
    return compte

def medianne_hauteur_voisine(struct, i_x_max, i_y_max, i, j):
    liste = [-1, 0, 1]
    hauteurs = []
    for di in liste:
        for dj in liste:
            i_voisin = i+di
            j_voisin = j+dj
            if i_voisin>=0 and i_voisin<i_x_max and j_voisin>=0 and j_voisin<i_y_max:
                hauteur = hauteur_voisine(struct, i_voisin, j_voisin)
                if hauteur >= 10:
                    hauteurs.append(hauteur)
    if len(hauteurs)>=3:
        return median(hauteurs)
    else:
        return None



def replace_espace_vide(struct, i_x_max, i_y_max, resolution, espaces_vides, x_min, y_min, z_min):
    compte = 0
    while len(espaces_vides)>0:
        new_espaces_vides = []
        for espace_vide in espaces_vides:
            hauteur = medianne_hauteur_voisine(struct, i_x_max, i_y_max, espace_vide[0], espace_vide[1])
            if hauteur is None:
                new_espaces_vides.append(espace_vide)
            else:
                i_x = espace_vide[0]
                i_y = espace_vide[1]
                for i_z in range(int(hauteur)):
                    x = x_min + i_x * resolution
                    y = y_min + i_y * resolution
                    z = z_min + i_z * resolution
                    struct[i_x][i_y][i_z] = Cube(x, y, z, resolution, i_x, i_y, i_z)
        espaces_vides = new_espaces_vides
        compte += 1
        if compte >=30 :
            print("Espaces vides non remplis : ", len(espaces_vides))
            break
    return struct


def build_face(struct):
    i_x_max = len(struct)
    i_y_max = len(struct[0])
    i_z_max = len(struct[0][0])
    liste_faces_x = ListeFacesX(i_x_max+1, i_y_max, i_z_max)
    liste_faces_y = ListeFacesY(i_x_max, i_y_max+1, i_z_max)
    liste_faces_z = ListeFacesZ(i_x_max, i_y_max, i_z_max+1)
    sommets = []
    faces = []

    print("Construction des faces")
    for i_x in tqdm(range(i_x_max)):
        for i_y in range(i_y_max):
            for i_z in range(i_z_max):
                cube = struct[i_x][i_y][i_z]
                if cube is not None:
                    sommets, faces, liste_faces_x, liste_faces_y, liste_faces_z = cube.creer_faces(struct, faces, sommets, liste_faces_x, liste_faces_y, liste_faces_z)
    print(len(sommets))
    return sommets, faces, liste_faces_x, liste_faces_y, liste_faces_z


def write_obj(sommets, faces, echelle, x_min, y_min, z_min, output):
    with open(os.path.join(output, "model.obj"), "w") as f:
        f.write("o objet\n\n")
        for sommet in sommets:
            x, y, z = sommet.get_xyz(echelle, x_min, y_min, z_min)
            f.write(f"v {x} {y} {z}\n")

        f.write("\n")

        for face in faces:
            l0, l1 = face.get_sommet_id() 
            f.write(f"f {l0[0]} {l0[1]} {l0[2]}\n")
            f.write(f"f {l1[0]} {l1[1]} {l1[2]}\n")


def get_indice_sommet(sommets, sommet):
    for s in reversed(sommets):
        if s==sommet:
            return s.id
        
    return None


def create_liste_sommets(struct, x_min, y_min, z_min, resolution):
    size_x = len(struct)+1
    size_y = len(struct[0])+1
    size_z = len(struct[0][0])+1
    return ListeSommets(size_x, size_y, size_z, resolution, x_min, y_min, z_min)


def simplifier(liste_faces_x, liste_faces_y, liste_faces_z, liste_sommets):
    faces = []
    faces += liste_faces_x.simplifier()
    faces += liste_faces_y.simplifier()
    faces += liste_faces_z.simplifier()
    print("Nombre faces : ", len(faces))


    sommets = []
    print("Simplification des sommets")
    for face in tqdm(faces):
        for sommet in face.sommets:
            s = liste_sommets.get_sommet(sommet)
            if s is None:
                liste_sommets.add_sommet(sommet)
                sommets.append(sommet)
                sommet.id = len(sommets)
            else:
                sommet.id = s.id
    print("Nombre de sommets : ", len(sommets))
    return faces, sommets


def save_info(resolution, echelle, taille_cube, output):
    with open(os.path.join(output, "info.txt"), "w") as f:
        f.write(f"resolution : {resolution}\n")
        f.write(f"echelle : {echelle}\n")
        f.write(f"taille_cube : {taille_cube}")


parser = argparse.ArgumentParser()
parser.add_argument('--lidar')
parser.add_argument('--emprise') 
parser.add_argument('--echelle', help="Doit être du format x/y avec x et y des entiers", default=None, type=str)
parser.add_argument('--resolution', default=None, type=float)
parser.add_argument('--taille_cube', help="Pas plus de 0.0005 mètres idéalement", default=None, type=float)
parser.add_argument('--taille_maquette', help="Pas plus de 0.25 m de côté idéalement", default=None, type=float)
parser.add_argument('--output', help="Répertoire où sauvegarder le modèle")
args = parser.parse_args()


lidar_path = args.lidar
emprise_path = args.emprise

echelle = args.echelle
if echelle is not None:
    echelle = int(echelle.split("/")[0]) / int(echelle.split("/")[1])
resolution = args.resolution
if resolution is not None:
    resolution = float(args.resolution)
taille_cube = args.taille_cube
if taille_cube is not None:
    taille_cube = float(args.taille_cube)
taille_maquette = args.taille_maquette
if taille_maquette is not None:
    taille_maquette = float(args.taille_maquette)
output = args.output
if output is None:
    raise ValueError("--output doit être défini")





emprise = open_geopandas(emprise_path)



if taille_maquette is not None and echelle is None:
    x, y = emprise.exterior.coords.xy
    x_min = min(x)
    y_min = min(y)
    x_max = max(x)
    y_max = max(y)
    cote_max = max(max(x)-min(x), max(y)-min(y))
    echelle = taille_maquette/cote_max
if echelle is not None and taille_cube is not None and resolution is None:
    resolution = taille_cube/echelle
    
print(f"Echelle : 1/{int(1/echelle)}")
print("Résolution : ", resolution)

if echelle is None:
    raise ValueError("L'échelle n'a pas été définie")

if resolution is None:
    raise ValueError("La résolution n'a pas été définie")

bounds = get_bounds(emprise)
aScaleAwarePointRecord = open_points(lidar_path, bounds)
points:np.array = aScaleAwarePointRecord.array
points = filter_points(points)
print("Points : ", points.shape[0])
save_points(aScaleAwarePointRecord)
save_points_from_numpy(points)
x_min, x_max, y_min, y_max, z_min, z_max = get_limites_cube(points, resolution, echelle)
struct = reconstruction(points, x_min, x_max, y_min, y_max, z_min, z_max, resolution)
print(Cube.compte)
sommets, faces, liste_faces_x, liste_faces_y, liste_faces_z = build_face(struct)
liste_sommets = create_liste_sommets(struct, x_min, y_min, z_min, resolution)
faces, sommets = simplifier(liste_faces_x, liste_faces_y, liste_faces_z, liste_sommets)
write_obj(sommets, faces, echelle, x_min, y_min, z_min, output)
save_info(resolution, echelle, taille_cube, output)