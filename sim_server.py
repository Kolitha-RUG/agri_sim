import asyncio, json, websockets, simpy

async def sim_handler(websocket):
    print("Unity connected. Waiting for parameters...")

    # Wait for command message from Unity
    params_msg = await websocket.recv()
    params = json.loads(params_msg)

    if params.get("command") == "run_simulation":
        num_workers = params.get("num_workers", 5)
        num_drones = params.get("num_drones", 2)
        fatigue_threshold = params.get("fatigue_threshold", 3)

        print(f"Running simulation: {num_workers=} {num_drones=} {fatigue_threshold=}")
        await run_simpy_simulation(websocket, num_workers, num_drones, fatigue_threshold)

async def run_simpy_simulation(ws, num_workers, num_drones, fatigue_threshold):
    env = simpy.Environment()
    x = 0
    while env.now < 20:
        await asyncio.sleep(0.2)
        env.step()
        x += 1
        msg = {
            "time": env.now,
            "worker": "W1",
            "x": x,
            "y": 0,
            "info": f"Running sim with {num_workers} workers"
        }
        await ws.send(json.dumps(msg))

async def main():
    async with websockets.serve(sim_handler, "localhost", 8765):
        print("Server ready on ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
