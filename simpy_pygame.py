import salabim as sim
import pygame
import threading
import time

sim.yieldless(False)

# Global state access
workers = []
drones = []
full_boxes_queue = None

# Simulation parameters (positions, speeds)
worker_location = (100, 300)
drop_location   = (400, 300)

class Worker(sim.Component):
    def __init__(self, *args, x=0, y=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y

    def process(self):
        while True:
            yield self.hold(10)
            box = Box()
            box.enter(full_boxes_queue)
            for d in drones:
                if d.ispassive():
                    d.activate()

class Box(sim.Component):
    pass

class Drone(sim.Component):
    def __init__(self, *args, x=0, y=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        # target positions for movement
        self.target_x = x
        self.target_y = y
        self.moving = False
        self.move_start_time = None
        self.move_end_time = None
        self.start_x = x
        self.start_y = y

    def process(self):
        while True:
            if len(full_boxes_queue) == 0:
                yield self.passivate()

            # Fly to worker
            fly_time = 5
            self.start_move_to(worker_location, fly_time)
            yield self.hold(fly_time)
            self.x, self.y = worker_location

            # Pick box
            box = full_boxes_queue.pop()

            # Fly to drop
            fly_time2 = 5
            self.start_move_to(drop_location, fly_time2)
            yield self.hold(fly_time2)
            self.x, self.y = drop_location

            # Return to worker side
            ret_time = 5
            self.start_move_to(worker_location, ret_time)
            yield self.hold(ret_time)
            self.x, self.y = worker_location

    def start_move_to(self, (tx, ty), duration):
        """Initialize movement parameters so Pygame can interpolate position."""
        self.start_x = self.x
        self.start_y = self.y
        self.target_x = tx
        self.target_y = ty
        self.move_start_time = self.env.now()
        self.move_end_time = self.move_start_time + duration
        self.moving = True

    def update_position(self, sim_time):
        """Call this (in graphics loop) to update x,y based on sim_time."""
        if self.moving and sim_time is not None:
            t0 = self.move_start_time
            t1 = self.move_end_time
            if sim_time >= t1:
                # reached
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
            else:
                # linear interpolation
                frac = (sim_time - t0) / (t1 - t0)
                self.x = self.start_x + frac * (self.target_x - self.start_x)
                self.y = self.start_y + frac * (self.target_y - self.start_y)

def run_simulation():
    global full_boxes_queue, workers, drones
    env = sim.Environment(trace=False)
    full_boxes_queue = sim.Queue("Full boxes")
    # create workers
    for i in range(3):
        w = Worker(name=f"W{i+1}", x=worker_location[0] + i*30, y=worker_location[1])
        workers.append(w)
    # create drones
    for j in range(2):
        d = Drone(name=f"D{j+1}", x=drop_location[0], y=drop_location[1] + j*50)
        drones.append(d)
    env.run(till=200)

def run_pygame():
    pygame.init()
    size = width, height = 600, 400
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    # We need to run simulation in parallel (thread) or step it manually
    sim_thread = threading.Thread(target=run_simulation)
    sim_thread.daemon = True
    sim_thread.start()

    start_wall = time.time()
    sim_start = 0  # simulation time start

    while running:
        dt = clock.tick(30)  # 30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Estimate current sim time as (wall time elapsed) * speed factor
        sim_time = (time.time() - start_wall)  # naive: 1 sec wall = 1 time unit sim

        # Update drone positions
        for d in drones:
            d.update_position(sim_time)

        # Draw
        screen.fill((255, 255, 255))
        # draw workers
        for w in workers:
            pygame.draw.rect(screen, (0, 200, 0),
                             pygame.Rect(w.x-15, w.y-15, 30, 30))
        # draw queue (as boxes waiting)
        # you might draw small boxes near worker location with a stack count
        qsize = len(full_boxes_queue)
        for i in range(qsize):
            pygame.draw.rect(screen, (255, 165, 0),
                             pygame.Rect(worker_location[0] - 60 - i*12,
                                         worker_location[1] - 40, 10, 10))
        # draw drones
        for d in drones:
            pygame.draw.circle(screen, (0, 0, 255),
                               (int(d.x), int(d.y)), 10)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_pygame()
