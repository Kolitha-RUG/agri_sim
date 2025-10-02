import salabim as sim
sim.yieldless(False)


class Worker(sim.Component):
    """Worker that repeatedly fills boxes and places them into a queue."""
    def process(self):
        while True:
            yield self.hold(10)  # 10 minutes to fill a box
            box = Box()
            box.enter(full_boxes_queue)
            print(f"{self.env.now():.1f} {self.name()} filled a box -> Queue length = {len(full_boxes_queue)}")

            # Wake up drones if any are idle
            for d in drones:
                if d.ispassive():
                    d.activate()


class Box(sim.Component):
    """Represents a filled box in the system (sits in queue until picked)."""

    pass

class Drone(sim.Component):
    """Drone that picks boxes from queue and transports them."""
    def process(self):
        while True:
            if len(full_boxes_queue) == 0:
                yield self.passivate()

            yield self.hold(3)  # e.g., 5 minutes travel time
            print(f"{self.env.now():.1f} {self.name()} arrived at worker location")

            # Take a box
            box = full_boxes_queue.pop()
            print(f"{self.env.now():.1f} {self.name()} picked a box -> Queue length = {len(full_boxes_queue)}")

            # Transport time
            yield self.hold(3)  # 5 minutes transport
            print(f"{self.env.now():.1f} {self.name()} delivered a box to collection point")

# --- setup environment ---
env = sim.Environment(trace=False)
full_boxes_queue = sim.Queue("Full boxes")

# create multiple workers and drones
workers = [Worker(name=f"Worker{i+1}") for i in range(3)]   # 3 workers
drones  = [Drone(name=f"Drone{j+1}") for j in range(2)]     # 2 drones


sim.AnimateMonitor(full_boxes_queue.length, x=10, y=450, width=580, height=200, horizontal_scale=5, vertical_scale=5)
# sim.AnimateMonitor(full_boxes_queue.length_of_stay, x=10, y=570, width=480, height=100, horizontal_scale=10, vertical_scale=10)


# run for 60 minutes
env.animate(True)   # turn animation on
env.run(till=200)
