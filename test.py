import simpy
import random

# Parameters
NUM_WORKERS = 2
NUM_DRONES = 2
SIM_TIME = 50   # minutes

def worker(env, worker_id, box_queue):
    """Worker picks grapes and fills boxes."""
    box_id = 0
    while True:
        # Time to pick and fill a box (3–7 minutes)
        pick_time = random.randint(3, 7)
        yield env.timeout(pick_time)
        
        box_id += 1
        box_name = f"W{worker_id}-Box{box_id}"
        print(f"Time {env.now}: Worker {worker_id} filled {box_name}")
        
        # Put box into queue
        yield box_queue.put(box_name)
        print(f"Time {env.now}: Worker {worker_id} placed {box_name} in queue")

def drone(env, drone_id, box_queue):
    """Drone takes boxes from the queue and transports them."""
    while True:
        box = yield box_queue.get()   # wait for a box
        print(f"Time {env.now}: Drone {drone_id} picked up {box}")
        
        # Transport takes 5 minutes
        transport_time = 5
        yield env.timeout(transport_time)
        print(f"Time {env.now}: Drone {drone_id} delivered {box}")

# Setup environment
env = simpy.Environment()
box_queue = simpy.Store(env)

# Start worker processes
for i in range(1, NUM_WORKERS+1):
    env.process(worker(env, i, box_queue))

# Start drone processes
for j in range(1, NUM_DRONES+1):
    env.process(drone(env, j, box_queue))

# Run simulation
env.run(until=SIM_TIME)
