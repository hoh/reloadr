
from time import sleep
from reloadr import reloadr


@reloadr
def move_z(target, dz):
    target.z += dz


@reloadr
class Car:
    x = 0
    y = 0
    z = 0

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def position(self):
        return 'Car on {} {} {}'.format(self.x, self.y, self.z)


car = Car(1000, 3000)
while True:
    car.move(1, 1)
    move_z(car, 1)
    print(car.position())
    sleep(0.3)
    Car._reload()
    move_z._reload()
