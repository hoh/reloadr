
from time import sleep
from reloadr import reloadr


@reloadr
class Car:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def position(self):
        return 'Car on {} {}'.format(self.x, self.y)


car = Car(1000, 3000)
Car._start_watch_reload()

while True:
    car.move(1, 1)
    print(car.position())
    sleep(0.1)
