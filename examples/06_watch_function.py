
from time import sleep
from reloadr import reloadr


@reloadr
def move(car, dx=0, dy=0):
    car.x += dx
    car.y += dy


class Car:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def position(self):
        return 'Car on {} {}'.format(self.x, self.y)


car = Car(1000, 3000)

move._start_watch_reload()

while True:
    move(car, 1, 1)
    print(car.position())
    sleep(0.5)
