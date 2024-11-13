from statistics import mean

class Face:

    def __init__(self, sommets) -> None:
        self.sommets = sommets

    def __str__(self):
        liste_x = []
        liste_y = []
        liste_z = []
        for sommet in self.sommets:
            liste_x.append(sommet.x)
            liste_y.append(sommet.y)
            liste_z.append(sommet.z)
        return f"{mean(liste_x)}, {mean(liste_y)}, {mean(liste_z)}"

    def get_sommet_id(self):
        s1 = self.sommets[0]
        s2 = self.sommets[1]
        s3 = self.sommets[2]
        s4 = self.sommets[3]

        l0 = [s1.id, s2.id, s3.id]

        d1 = s1.distance(s2)
        d2 = s1.distance(s3)
        d3 = s2.distance(s3)
        if d1 > d2 and d1 > d3:
            l1 = [s1.id, s2.id, s4.id]
        elif d2 > d1 and d2 > d3:
            l1 = [s1.id, s3.id, s4.id]
        elif d3 > d2 and d3 > d1:
            l1 = [s2.id, s3.id, s4.id]
        else:
            raise ValueError("Erreur")
    
        return l0, l1
    
    def limite(self):
        liste_x = []
        liste_y = []
        liste_z = []
        for sommet in self.sommets:
            liste_x.append(sommet.x)
            liste_y.append(sommet.y)
            liste_z.append(sommet.z)
        return min(liste_x), max(liste_x), min(liste_y), max(liste_y), min(liste_z), max(liste_z)