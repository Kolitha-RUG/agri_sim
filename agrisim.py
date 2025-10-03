import simpy

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

class Worker:
    def __init__(self, env, worker_id, box_queue, events, fatigue_threshold=3):
        self.env = env
        self.id = worker_id
        self.box_queue = box_queue
        self.fatigue = 0
        self.fatigue_threshold = fatigue_threshold
        self.events = events
        env.process(self.run())

    def harvest_time(self):
        """Base 10 min, add penalty from fatigue."""
        base_time = 10
        fatigue_penalty = self.fatigue * 0.5   # each fatigue point adds 0.5 min
        return base_time + fatigue_penalty

    def transport_time(self):
        """Human transport time (slower than drone)."""
        return 12   # minutes to deliver

    def run(self):
        while True:
            yield self.env.timeout(self.harvest_time())  # time to fill box
            box = Box(self.id, self.env.now)
            print(f"Time {self.env.now}: Worker {self.id} filled {box} fatigue={self.fatigue}")

            if self.fatigue < self.fatigue_threshold:
                # Optionally, worker can deliver the box themselves
                yield self.env.timeout(self.transport_time())
                box.mark_delivered(self.env.now, f"W{self.id}")
                print(f"Time {self.env.now}: Worker {self.id} | {box} Delivered")
            else:
                yield self.box_queue.put(box)
                print(f"Time {self.env.now}: Worker {self.id} placed {box}. Queue size: {len(self.box_queue.items)}")

            self.fatigue += 1  # increase fatigue after each box



class Drone:
    def __init__(self, env, drone_id, box_queue, events):
        self.env = env
        self.id = drone_id
        self.box_queue = box_queue
        self.events = events
        env.process(self.run())

    def run(self):
        while True:
            if len(self.box_queue.items)!= 0:
                coming_time = 3
                yield self.env.timeout(coming_time)  # Time to arrive at the queue
                print(f"Time {self.env.now}: Drone {self.id} arrived at the queue")
                box = yield self.box_queue.get()   # wait for a box
                print(f"Time {self.env.now}: Drone {self.id} picked up {box}. Queue size: {len(self.box_queue.items)}")
                
                transport_time = 5
                yield self.env.timeout(transport_time)
                box.mark_delivered(self.env.now, f"D{self.id}")
                print(f"Time {self.env.now}: Drone {self.id} | {box} Delivered")
            else:
                yield self.env.timeout(1)  # Wait before checking the queue again



def run_sim(num_workers=5, num_drones=2, sim_time=60, fatigue_threshold=3):
    events = []
    env = simpy.Environment()
    box_queue = simpy.Store(env)

    workers = [Worker(env, i, box_queue, events, fatigue_threshold) for i in range(1, num_workers+1)]
    drones = [Drone(env, j, box_queue, events) for j in range(1, num_drones+1)]

    env.run(until=sim_time)

    # Collect results
    delivered = [w for w in workers]  # keep worker state
    return workers, drones, box_queue


class LiveSim:
    """Tiny wrapper to step the SimPy env and expose state snapshots."""
    def __init__(self, num_workers=5, num_drones=2, fatigue_threshold=3):
        self.env = simpy.Environment()
        self.box_queue = simpy.Store(self.env)
        self.events = []
        self.workers = [
            Worker(self.env, i, self.box_queue, self.events, fatigue_threshold)
            for i in range(1, num_workers + 1)
        ]
        self.drones = [
            Drone(self.env, j, self.box_queue, self.events)
            for j in range(1, num_drones + 1)
        ]

    @property
    def now(self):
        return self.env.now

    def step(self):
        """Advance to next scheduled event. Returns False if no more events."""
        nxt = self.env.peek()
        if nxt == float("inf"):
            return False
        self.env.step()
        return True

    def snapshot(self):
        """Lightweight state for plotting HUDs/charts."""
        delivered = sum(e["event"].endswith("Delivered") for e in self.events)
        return {
            "time": self.env.now,
            "queue": len(self.box_queue.items),
            "delivered": delivered,
        }


def make_live_sim(num_workers=5, num_drones=2, fatigue_threshold=3):
    return LiveSim(num_workers=num_workers, num_drones=num_drones, fatigue_threshold=fatigue_threshold)
