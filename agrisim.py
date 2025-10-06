import simpy
import math
import time
class Box:
    def __init__(self, worker_id, created_time):
        self.worker_id = worker_id
        self.created_time = created_time
        self.delivered_time = None
        self.delivered_by = None
    
    def mark_delivered(self, time, delivered_by):
        self.delivered_time = time
        self.delivered_by = delivered_by

    def __repr__(self):
        return f"Box(by W{self.worker_id}, created at={self.created_time}, " \
               f"delivered at={self.delivered_time}, delivered by={self.delivered_by})"

class Location:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class CollectionPoint:
    def __init__(self, location):
        self.location = location
        self.received_boxes = []
    
    def receive(self, box, time, delivered_by):
        box.mark_delivered(time, delivered_by)
        self.received_boxes.append(box)
        print(f"Time {time:.2f}: {delivered_by} delivered {box} to Collection Point at {self.location}")

class Worker:
    def __init__(self, env, worker_id, box_queue, collection_point, fatigue_threshold=3, location=Location(0, 0)):
        self.env = env
        self.id = worker_id
        self.box_queue = box_queue
        self.collection_point = collection_point
        self.fatigue = 0
        self.fatigue_threshold = fatigue_threshold
        self.location = location
        env.process(self.run())

    def harvest_time(self):
        """Base 10 min, add penalty from fatigue."""
        base_time = 10
        fatigue_penalty = self.fatigue * 0.5   # each fatigue point adds 0.5 min
        return base_time + fatigue_penalty

    def transport_time(self):
        """Human transport time (slower than drone)."""
        distance = self.location.distance_to(self.collection_point.location)
        speed = 1.0  # units per minute
        return distance / speed   # minutes to deliver

    def run(self):
        while True:
            yield self.env.timeout(self.harvest_time())  # time to fill box
            box = Box(self.id, self.env.now)
            print(f"Time {self.env.now:.2f}: Worker {self.id} filled {box} fatigue={self.fatigue}")

            if self.fatigue < self.fatigue_threshold:
                # Optionally, worker can deliver the box themselves
                yield self.env.timeout(self.transport_time())
                box.mark_delivered(self.env.now, f"W{self.id}")
                print(f"Time {self.env.now:.2f}: Worker {self.id} | {box} Delivered")
            else:
                yield self.box_queue.put(box)
                print(f"Time {self.env.now:.2f}: Worker {self.id} placed {box}. Queue size: {len(self.box_queue.items)}")

            self.fatigue += 1  # increase fatigue after each box



class Drone:
    def __init__(self, env, drone_id, box_queue, collection_point, location=Location(0, 0)):
        self.env = env
        self.id = drone_id
        self.box_queue = box_queue
        self.collection_point = collection_point
        self.location = location
        env.process(self.run())

    def run(self):
        while True:
            if len(self.box_queue.items)!= 0:
                coming_time = 3
                yield self.env.timeout(coming_time)  # Time to arrive at the queue
                print(f"Time {self.env.now}: Drone {self.id} arrived at the queue")
                box = yield self.box_queue.get()   # wait for a box
                print(f"Time {self.env.now}: Drone {self.id} picked up {box}. Queue size: {len(self.box_queue.items)}")

                transport_time = self.location.distance_to(self.collection_point.location) / 1.0  # Assume speed is 1.0
                yield self.env.timeout(transport_time)
                box.mark_delivered(self.env.now, f"D{self.id}")
                print(f"Time {self.env.now}: Drone {self.id} | {box} Delivered")
            else:
                yield self.env.timeout(1)  # Wait before checking the queue again



def run_sim(num_workers=5, num_drones=2, sim_time=60, fatigue_threshold=3):
    env = simpy.Environment()
    box_queue = simpy.Store(env)
    collection_point = CollectionPoint(Location(10, 5))

    workers = [
        Worker(env, i, box_queue, collection_point, fatigue_threshold, location=Location(i*2, 0))
        for i in range(1, num_workers+1)
    ]
    drones = [
        Drone(env, j, box_queue, collection_point, location=Location(0, j*2))
        for j in range(1, num_drones+1)
    ]

    env.run(until=sim_time)

    return workers, drones, collection_point, box_queue


def run_sim_stepwise(num_workers=5, num_drones=2, sim_time=60, fatigue_threshold=3):
    env = simpy.Environment()
    box_queue = simpy.Store(env)
    collection_point = CollectionPoint(Location(10, 5))

    workers = [
        Worker(env, i, box_queue, collection_point, fatigue_threshold, location=Location(i * 2, 0))
        for i in range(1, num_workers + 1)
    ]
    drones = [
        Drone(env, j, box_queue, collection_point, location=Location(0, j * 2))
        for j in range(1, num_drones + 1)
    ]

    while env.now < sim_time:
        env.step()
        yield env.now, workers, drones, collection_point
