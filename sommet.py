from math import sqrt

class Sommet:

    id = 0

    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.id = Sommet.id
        Sommet.id += 1

    def get_xyz(self, echelle, x_min, y_min, z_min):
        return (self.x-x_min)*echelle*10, (self.y-y_min)*echelle*10, (self.z-z_min)*echelle*10#*10 car c'est en cm dans les fichiers las
    
    def __eq__(self, value: object) -> bool:
        return self.x==value.x and self.y==value.y and self.z==value.z
    
    def distance(self, s):
        return sqrt((self.x - s.x)**2 + (self.y - s.y)**2 + (self.z - s.z)**2)
