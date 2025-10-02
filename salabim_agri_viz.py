from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
import random

# --- Agents ---

class Box(Agent):
    def __init__(self, model, pos):
        super().__init__(model)
        self.pos = pos

    def step(self):
        pass

class Worker(Agent):
    def __init__(self, model, pos):
        super().__init__(model)
        self.pos = pos
        self.time_to_box = random.randint(3, 7)

    def step(self):
        self.time_to_box -= 1
        if self.time_to_box <= 0:
            b = Box(self.model, self.pos)
            self.model.space.place_agent(b, b.pos)
            self.model.boxes.append(b)
            self.time_to_box = random.randint(3, 7)

class Drone(Agent):
    def __init__(self, model, pos, speed=1.5):
        super().__init__(model)
        self.pos = pos
        self.speed = speed
        self.carrying = False
        self.target = None  # either Box or drop location (x, y tuple)

    def _move_towards(self, target_xy):
        tx, ty = target_xy
        dx = tx - self.pos[0]
        dy = ty - self.pos[1]
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= self.speed or dist == 0:
            self.pos = (tx, ty)
            return True
        self.pos = (
            self.pos[0] + dx / dist * self.speed,
            self.pos[1] + dy / dist * self.speed,
        )
        return False

    def step(self):
        if self.target is None:
            if self.carrying:
                self.target = self.model.drop_point
            elif self.model.boxes:
                self.target = self.model.boxes.pop(0)
            else:
                return

        if isinstance(self.target, Box):
            tgt_xy = self.target.pos
        else:
            tgt_xy = self.target

        reached = self._move_towards(tgt_xy)

        if reached:
            if isinstance(self.target, Box):
                self.target.remove()  # remove from model
                self.carrying = True
                self.target = self.model.drop_point
            else:
                self.carrying = False
                self.target = None

# --- Model ---

class DroneBoxModel(Model):
    def __init__(self, n_workers=2, n_drones=2, width=50, height=30, seed=None):
        super().__init__(seed=seed)
        self.space = ContinuousSpace(x_max=width, y_max=height, torus=False)
        self.boxes = []
        self.drop_point = (width - 5, height / 2)

        for i in range(n_workers):
            w = Worker(self, pos=(5, 5 + i * 10))
            self.space.place_agent(w, w.pos)

        for j in range(n_drones):
            d = Drone(self, pos=(width - 5, 5 + j * 10), speed=1.5)
            self.space.place_agent(d, d.pos)

        self.datacollector = DataCollector(
            model_reporters={
                "boxes_waiting": lambda m: len(m.boxes),
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")  # random order

# --- Visualization / Portrayal ---

def agent_portrayal(agent):
    if isinstance(agent, Worker):
        return {"x": agent.pos[0], "y": agent.pos[1], "color": "green", "marker": "s", "size": 80}
    elif isinstance(agent, Drone):
        color = "blue" if not agent.carrying else "purple"
        return {"x": agent.pos[0], "y": agent.pos[1], "color": color, "marker": "^", "size": 90}
    elif isinstance(agent, Box):
        return {"x": agent.pos[0], "y": agent.pos[1], "color": "orange", "marker": "o", "size": 60}

# Build visualization
model = DroneBoxModel(n_workers=3, n_drones=2, width=50, height=30, seed=42)
space = make_space_component(agent_portrayal)
boxes_plot = make_plot_component("boxes_waiting")

page = SolaraViz(
    model,
    components=[space, boxes_plot],
    name="Drone & Box Simulation",
    play_interval=0.2,
)

page
