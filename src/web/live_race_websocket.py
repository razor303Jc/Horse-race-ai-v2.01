from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime, timedelta
import random
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, race_id: str):
        await websocket.accept()
        
        if race_id not in self.active_connections:
            self.active_connections[race_id] = set()
        
        self.active_connections[race_id].add(websocket)
        self.connection_info[websocket] = {
            'race_id': race_id,
            'connected_at': datetime.now(),
            'client_id': str(uuid.uuid4())[:8]
        }
        
        logger.info(
            f"Client connected to race {race_id}. "
            f"Total connections: {len(self.active_connections[race_id])}"
        )

    def disconnect(self, websocket: WebSocket):
        info = self.connection_info.get(websocket)
        if info:
            race_id = info['race_id']
            if race_id in self.active_connections:
                self.active_connections[race_id].discard(websocket)
                if not self.active_connections[race_id]:
                    del self.active_connections[race_id]
            
            del self.connection_info[websocket]
            logger.info(f"Client disconnected from race {race_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_race(self, message: str, race_id: str):
        if race_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[race_id].copy():
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection)

    def get_race_connections_count(self, race_id: str) -> int:
        return len(self.active_connections.get(race_id, set()))


manager = ConnectionManager()

# Mock race data generator


class RaceSimulator:
    def __init__(self, race_id: str):
        self.race_id = race_id
        self.is_running = False
        self.progress = 0
        self.horses = self._generate_horses()
        self.commentary = []
        self.start_time = datetime.now()
        
    def _generate_horses(self):
        horse_names = [
            "Thunder Bolt", "Lightning Strike", "Midnight Express", "Golden Arrow",
            "Storm Chaser", "Fire Dancer", "Ocean Breeze", "Desert Wind",
            "Mountain Peak", "Silver Bullet", "Royal Crown", "Wild Spirit"
        ]
        
        jockeys = [
            "J. Smith", "M. Johnson", "S. Williams", "A. Brown", "C. Davis",
            "R. Wilson", "L. Garcia", "K. Miller", "T. Anderson", "P. Martinez"
        ]
        
        trainers = [
            "H. Thompson", "D. White", "N. Harris", "B. Clark", "V. Lewis",
            "G. Walker", "F. Hall", "J. Allen", "M. Young", "S. King"
        ]
        
        horses = []
        for i, name in enumerate(horse_names[:8]):  # 8 horses per race
            horses.append({
                'id': f"horse_{i+1}",
                'name': name,
                'jockey': random.choice(jockeys),
                'trainer': random.choice(trainers),
                'position': i + 1,
                'distance': 0,
                'speed': round(random.uniform(45, 55), 1),
                'odds': round(random.uniform(2, 15), 1),
                'form': ''.join(random.choices(['1', '2', '3', '4', '5', '6'], k=5)),
                'silks': f"#{random.randint(100000, 999999)}"
            })
        
        return horses
    
    async def simulate_race(self):
        """Simulate a race with realistic progression"""
        self.is_running = True
        self.progress = 0
        race_distance = 2000  # 2000 meters
        
        # Add initial commentary
        await self._add_commentary("And they're off! The field is away cleanly.")
        
        while self.progress < 100 and self.is_running:
            # Update race progress
            self.progress = min(100, self.progress + random.uniform(1, 3))
            
            # Update horse positions and speeds
            for horse in self.horses:
                # Vary speed slightly
                speed_change = random.uniform(-2, 2)
                horse['speed'] = max(30, min(65, horse['speed'] + speed_change))
                
                # Update distance based on speed
                horse['distance'] = int((self.progress / 100) * race_distance)
                
                # Add some randomness to positions
                position_change = random.uniform(-0.5, 0.5)
                horse['position'] += position_change
            
            # Sort horses by distance covered
            self.horses.sort(key=lambda x: x['distance'], reverse=True)
            
            # Update positions
            for i, horse in enumerate(self.horses):
                horse['position'] = i + 1
            
            # Add commentary at key moments
            if self.progress > 25 and self.progress < 30:
                leader = self.horses[0]
                await self._add_commentary(
                    f"At the quarter mark, {leader['name']} is setting the pace!"
                )
            elif self.progress > 50 and self.progress < 55:
                leader = self.horses[0]
                second = self.horses[1]
                await self._add_commentary(
                    f"Halfway through and {leader['name']} leads from "
                    f"{second['name']}!"
                )
            elif self.progress > 75 and self.progress < 80:
                await self._add_commentary(
                    "Into the home straight they come! The race is heating up!"
                )
            elif self.progress > 90:
                leader = self.horses[0]
                second = self.horses[1]
                await self._add_commentary(
                    f"It's {leader['name']} and {second['name']} "
                    f"fighting it out!"
                )
            
            # Broadcast position update
            await manager.broadcast_to_race(
                json.dumps({
                    'type': 'position_update',
                    'race_id': self.race_id,
                    'positions': [
                        {
                            'id': horse['id'],
                            'position': horse['position'],
                            'distance': horse['distance'],
                            'speed': horse['speed']
                        }
                        for horse in self.horses
                    ],
                    'progress': round(self.progress, 1),
                    'timestamp': datetime.now().isoformat()
                }),
                self.race_id
            )
            
            await asyncio.sleep(2)  # Update every 2 seconds
        
        # Race finished
        if self.progress >= 100:
            winner = self.horses[0]
            await self._add_commentary(
                f"🏆 {winner['name']} wins! What a fantastic race!"
            )
            
            # Broadcast race finish
            await manager.broadcast_to_race(
                json.dumps({
                    'type': 'race_finish',
                    'race_id': self.race_id,
                    'winner': winner['name'],
                    'final_positions': self.horses,
                    'timestamp': datetime.now().isoformat()
                }),
                self.race_id
            )
        
        self.is_running = False
    
    async def _add_commentary(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        commentary_message = f"[{timestamp}] {message}"
        self.commentary.append(commentary_message)
        
        # Broadcast commentary
        await manager.broadcast_to_race(
            json.dumps({
                'type': 'commentary',
                'race_id': self.race_id,
                'message': commentary_message,
                'timestamp': datetime.now().isoformat()
            }),
            self.race_id
        )

# Store active race simulators


active_races: Dict[str, RaceSimulator] = {}


@router.websocket("/ws/race/{race_id}")
async def websocket_endpoint(websocket: WebSocket, race_id: str):
    await manager.connect(websocket, race_id)
    
    # Send initial race data
    if race_id not in active_races:
        active_races[race_id] = RaceSimulator(race_id)
    
    race = active_races[race_id]
    
    # Send current race state
    initial_data = {
        'type': 'race_state',
        'race_id': race_id,
        'status': 'running' if race.is_running else 'scheduled',
        'progress': race.progress,
        'horses': race.horses,
        'commentary': race.commentary[-10:],  # Last 10 comments
        'timestamp': datetime.now().isoformat()
    }
    
    await manager.send_personal_message(json.dumps(initial_data), websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('action') == 'start_race' and not race.is_running:
                # Start race simulation
                asyncio.create_task(race.simulate_race())
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'race_started',
                        'race_id': race_id,
                        'timestamp': datetime.now().isoformat()
                    }),
                    websocket
                )
            elif message.get('action') == 'subscribe':
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'subscribed',
                        'race_id': race_id,
                        'connections': manager.get_race_connections_count(race_id),
                        'timestamp': datetime.now().isoformat()
                    }),
                    websocket
                )
            elif message.get('action') == 'ping':
                await manager.send_personal_message(
                    json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# REST API endpoints for race data


@router.get("/races/{race_id}/live")
async def get_live_race_data(race_id: str):
    """Get current live race data"""
    if race_id not in active_races:
        active_races[race_id] = RaceSimulator(race_id)
    
    race = active_races[race_id]
    
    return {
        'id': race_id,
        'name': f"The {race_id.title()} Stakes",
        'track': "Cheltenham",
        'distance': "2m 4f",
        'startTime': race.start_time.isoformat(),
        'status': 'running' if race.is_running else 'scheduled',
        'progress': race.progress,
        'horses': race.horses,
        'commentary': race.commentary,
        'weather': "Good",
        'going': "Good to Firm",
        'currentTime': datetime.now().isoformat(),
        'connections': manager.get_race_connections_count(race_id)
    }

@router.get("/races/today")
async def get_todays_races():
    """Get all races for today"""
    # Generate mock races for today
    races = []
    race_names = [
        "Novice Hurdle", "Handicap Chase", "Maiden Stakes", "Listed Race",
        "Group 3 Stakes", "Conditions Stakes", "Selling Hurdle", "Bumper"
    ]
    
    tracks = ["Cheltenham", "Newmarket", "Ascot", "York", "Goodwood", "Epsom"]
    
    for i, name in enumerate(race_names):
        start_time = datetime.now() + timedelta(hours=i, minutes=random.randint(0, 59))
        race_id = f"race_{i+1}"
        
        # Determine status based on time
        now = datetime.now()
        if start_time <= now <= start_time + timedelta(minutes=10):
            status = 'running'
            is_live = True
        elif start_time < now:
            status = 'finished'
            is_live = False
        else:
            status = 'scheduled'
            is_live = False
        
        races.append({
            'id': race_id,
            'name': f"The {name}",
            'track': random.choice(tracks),
            'startTime': start_time.isoformat(),
            'distance': random.choice(["1m 2f", "1m 4f", "2m", "2m 4f", "3m"]),
            'going': random.choice(["Good", "Good to Firm", "Firm", "Good to Soft"]),
            'status': status,
            'horses': random.randint(6, 14),
            'prize': f"£{random.randint(10, 100)},000",
            'grade': random.choice(["Class 1", "Class 2", "Class 3", "Class 4"]),
            'weather': random.choice(["Fine", "Overcast", "Light Rain"]),
            'isLive': is_live
        })
    
    return races


@router.post("/races/{race_id}/start")
async def start_race(race_id: str):
    """Manually start a race simulation"""
    if race_id not in active_races:
        active_races[race_id] = RaceSimulator(race_id)
    
    race = active_races[race_id]
    
    if race.is_running:
        raise HTTPException(status_code=400, detail="Race is already running")
    
    # Start race simulation
    asyncio.create_task(race.simulate_race())
    
    return {"message": f"Race {race_id} started", "race_id": race_id}


@router.post("/races/{race_id}/stop")
async def stop_race(race_id: str):
    """Stop a race simulation"""
    if race_id in active_races:
        active_races[race_id].is_running = False
        return {"message": f"Race {race_id} stopped", "race_id": race_id}
    
    raise HTTPException(status_code=404, detail="Race not found")
