class ListeSommets:

    def __init__(self, size_x, size_y, size_z, resolution, x_min, y_min, z_min) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        self.resolution = resolution*100
        self.x_min = x_min
        self.y_min = y_min
        self.z_min = z_min

        self.array = [[[None for i_z in range(size_z)] for i_y in range(size_y)] for i_x in range(size_x)]

    def add_sommet(self, sommet):
        r = self.resolution/2
        i_x = int((sommet.x+r-self.x_min)/self.resolution)
        i_y = int((sommet.y+r-self.y_min)/self.resolution)
        i_z = int((sommet.z+r-self.z_min)/self.resolution)
        self.array[i_x][i_y][i_z] = sommet

    def get_sommet(self, sommet):
        r = self.resolution/2
        i_x = int((sommet.x+r-self.x_min)/self.resolution)
        i_y = int((sommet.y+r-self.y_min)/self.resolution)
        i_z = int((sommet.z+r-self.z_min)/self.resolution)
        return self.array[i_x][i_y][i_z]