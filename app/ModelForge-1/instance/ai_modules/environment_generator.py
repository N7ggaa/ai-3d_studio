import os
import logging
import json
import random
from typing import Dict, List, Optional, Tuple

def generate_environment(prompt: str, size: Tuple[int, int] = (100, 100)) -> Dict:
    """
    Generate environment/world layout based on natural language description
    
    Args:
        prompt: Description of the desired environment
        size: World size (width, height) in grid units
    
    Returns:
        Dictionary containing environment data
    """
    try:
        prompt_lower = prompt.lower()
        
        # Determine environment type
        env_type = detect_environment_type(prompt_lower)
        
        # Generate base terrain
        terrain = generate_terrain(env_type, size)
        
        # Place structures and objects
        structures = place_structures(prompt_lower, env_type, size)
        
        # Generate spawn points
        spawn_points = generate_spawn_points(env_type, size, structures)
        
        # Create lighting and atmosphere
        atmosphere = generate_atmosphere(env_type)
        
        # Generate paths/roads
        paths = generate_paths(structures, size)
        
        environment_data = {
            "type": env_type,
            "size": size,
            "terrain": terrain,
            "structures": structures,
            "spawn_points": spawn_points,
            "atmosphere": atmosphere,
            "paths": paths,
            "metadata": {
                "prompt": prompt,
                "version": "1.0"
            }
        }
        
        return environment_data
        
    except Exception as e:
        logging.error(f"Error generating environment: {e}")
        return generate_fallback_environment(size)

def detect_environment_type(prompt: str) -> str:
    """Detect the type of environment from the prompt"""
    if any(word in prompt for word in ['village', 'town', 'city', 'settlement']):
        return 'village'
    elif any(word in prompt for word in ['forest', 'woods', 'trees', 'jungle']):
        return 'forest'
    elif any(word in prompt for word in ['desert', 'sand', 'dunes', 'oasis']):
        return 'desert'
    elif any(word in prompt for word in ['mountain', 'hills', 'peaks', 'cliffs']):
        return 'mountain'
    elif any(word in prompt for word in ['beach', 'ocean', 'sea', 'coast', 'shore']):
        return 'beach'
    elif any(word in prompt for word in ['cave', 'cavern', 'underground', 'dungeon']):
        return 'cave'
    elif any(word in prompt for word in ['space', 'alien', 'sci-fi', 'futuristic']):
        return 'space'
    elif any(word in prompt for word in ['medieval', 'castle', 'kingdom', 'fantasy']):
        return 'medieval'
    else:
        return 'plains'

def generate_terrain(env_type: str, size: Tuple[int, int]) -> Dict:
    """Generate terrain data based on environment type"""
    width, height = size
    terrain = {
        "type": env_type,
        "heightmap": [],
        "materials": [],
        "features": []
    }
    
    # Generate heightmap
    for y in range(height):
        row = []
        material_row = []
        for x in range(width):
            # Generate height based on environment type
            if env_type == 'mountain':
                # Higher in center, lower at edges
                center_dist = ((x - width//2)**2 + (y - height//2)**2)**0.5
                max_dist = (width//2**2 + height//2**2)**0.5
                height_val = max(0, 1 - center_dist/max_dist) * 50 + random.uniform(-2, 2)
                material = 'Rock' if height_val > 30 else 'Grass'
            elif env_type == 'desert':
                # Rolling dunes
                height_val = abs(random.gauss(5, 3)) + 2
                material = 'Sand'
            elif env_type == 'beach':
                # Gradual slope towards water
                if x < width * 0.3:
                    height_val = random.uniform(0, 1)  # Water level
                    material = 'Water'
                elif x < width * 0.5:
                    height_val = random.uniform(1, 3)  # Beach
                    material = 'Sand'
                else:
                    height_val = random.uniform(3, 8)  # Land
                    material = 'Grass'
            elif env_type == 'cave':
                # Mostly flat with some variation
                height_val = random.uniform(0, 2)
                material = 'Rock'
            else:  # plains, forest, village, medieval
                # Gentle rolling hills
                height_val = random.uniform(0, 5) + random.gauss(0, 1)
                if env_type == 'forest':
                    material = 'Grass' if random.random() > 0.3 else 'LeafyGrass'
                else:
                    material = 'Grass'
            
            row.append(max(0, height_val))
            material_row.append(material)
        
        terrain["heightmap"].append(row)
        terrain["materials"].append(material_row)
    
    # Add terrain features
    if env_type == 'mountain':
        terrain["features"].extend(generate_mountain_features(size))
    elif env_type == 'forest':
        terrain["features"].extend(generate_forest_features(size))
    elif env_type == 'desert':
        terrain["features"].extend(generate_desert_features(size))
    elif env_type == 'beach':
        terrain["features"].extend(generate_beach_features(size))
    
    return terrain

def place_structures(prompt: str, env_type: str, size: Tuple[int, int]) -> List[Dict]:
    """Place structures based on environment type and prompt"""
    structures = []
    width, height = size
    
    if env_type == 'village' or 'village' in prompt:
        structures.extend(generate_village_structures(size))
    elif env_type == 'medieval' or 'castle' in prompt:
        structures.extend(generate_medieval_structures(size))
    elif env_type == 'forest':
        structures.extend(generate_forest_structures(size))
    elif env_type == 'cave' or 'dungeon' in prompt:
        structures.extend(generate_cave_structures(size))
    elif env_type == 'space':
        structures.extend(generate_space_structures(size))
    
    # Add specific structures mentioned in prompt
    if 'house' in prompt:
        structures.append(create_structure('House', random.randint(10, width-10), random.randint(10, height-10)))
    if 'shop' in prompt or 'store' in prompt:
        structures.append(create_structure('Shop', random.randint(10, width-10), random.randint(10, height-10)))
    if 'tower' in prompt:
        structures.append(create_structure('Tower', random.randint(10, width-10), random.randint(10, height-10)))
    if 'bridge' in prompt:
        structures.append(create_structure('Bridge', width//2, height//2))
    
    return structures

def generate_village_structures(size: Tuple[int, int]) -> List[Dict]:
    """Generate structures for a village"""
    structures = []
    width, height = size
    
    # Village center
    center_x, center_y = width // 2, height // 2
    
    # Town hall in center
    structures.append(create_structure('TownHall', center_x, center_y, size=(8, 8)))
    
    # Houses around the center
    house_positions = [
        (center_x - 15, center_y - 10),
        (center_x + 15, center_y - 10),
        (center_x - 15, center_y + 10),
        (center_x + 15, center_y + 10),
        (center_x - 10, center_y - 15),
        (center_x + 10, center_y - 15),
        (center_x - 10, center_y + 15),
        (center_x + 10, center_y + 15),
    ]
    
    for x, y in house_positions:
        if 0 < x < width and 0 < y < height:
            house_type = random.choice(['House', 'Cottage', 'Shop'])
            structures.append(create_structure(house_type, x, y))
    
    # Well in center
    structures.append(create_structure('Well', center_x + 5, center_y + 5, size=(2, 2)))
    
    return structures

def generate_medieval_structures(size: Tuple[int, int]) -> List[Dict]:
    """Generate structures for medieval environment"""
    structures = []
    width, height = size
    
    # Castle in center-back
    castle_x, castle_y = width // 2, height // 4
    structures.append(create_structure('Castle', castle_x, castle_y, size=(20, 15)))
    
    # Walls around castle
    wall_points = generate_castle_walls(castle_x, castle_y, 25, 20)
    for x, y in wall_points:
        if 0 < x < width and 0 < y < height:
            structures.append(create_structure('Wall', x, y, size=(1, 1)))
    
    # Watchtowers at corners
    towers = [
        (castle_x - 25, castle_y - 20),
        (castle_x + 25, castle_y - 20),
        (castle_x - 25, castle_y + 20),
        (castle_x + 25, castle_y + 20),
    ]
    
    for x, y in towers:
        if 0 < x < width and 0 < y < height:
            structures.append(create_structure('Watchtower', x, y, size=(4, 4)))
    
    # Village outside walls
    village_center_x, village_center_y = width // 2, height * 3 // 4
    village_houses = [
        (village_center_x - 10, village_center_y - 5),
        (village_center_x + 10, village_center_y - 5),
        (village_center_x - 5, village_center_y + 5),
        (village_center_x + 5, village_center_y + 5),
    ]
    
    for x, y in village_houses:
        if 0 < x < width and 0 < y < height:
            structures.append(create_structure('Peasant House', x, y))
    
    return structures

def generate_forest_structures(size: Tuple[int, int]) -> List[Dict]:
    """Generate structures for forest environment"""
    structures = []
    width, height = size
    
    # Scattered trees
    tree_count = (width * height) // 50
    for _ in range(tree_count):
        x = random.randint(5, width - 5)
        y = random.randint(5, height - 5)
        tree_type = random.choice(['Oak', 'Pine', 'Birch', 'Willow'])
        structures.append(create_structure(f'{tree_type}Tree', x, y, size=(2, 2)))
    
    # Forest camp
    camp_x, camp_y = width // 3, height // 3
    structures.append(create_structure('Tent', camp_x, camp_y))
    structures.append(create_structure('Campfire', camp_x + 3, camp_y + 3, size=(1, 1)))
    
    # Hidden cave entrance
    cave_x, cave_y = random.randint(width//2, width-10), random.randint(height//2, height-10)
    structures.append(create_structure('CaveEntrance', cave_x, cave_y, size=(3, 2)))
    
    return structures

def generate_cave_structures(size: Tuple[int, int]) -> List[Dict]:
    """Generate structures for cave/dungeon environment"""
    structures = []
    width, height = size
    
    # Cave walls (perimeter)
    for x in range(width):
        structures.append(create_structure('CaveWall', x, 0, size=(1, 1)))
        structures.append(create_structure('CaveWall', x, height-1, size=(1, 1)))
    
    for y in range(height):
        structures.append(create_structure('CaveWall', 0, y, size=(1, 1)))
        structures.append(create_structure('CaveWall', width-1, y, size=(1, 1)))
    
    # Cave chambers
    chambers = [
        (width//4, height//4, 8, 6),
        (width*3//4, height//4, 6, 8),
        (width//2, height*3//4, 10, 8),
    ]
    
    for chamber_x, chamber_y, chamber_w, chamber_h in chambers:
        # Chamber walls
        for x in range(chamber_x, chamber_x + chamber_w):
            structures.append(create_structure('CaveWall', x, chamber_y, size=(1, 1)))
            structures.append(create_structure('CaveWall', x, chamber_y + chamber_h, size=(1, 1)))
        
        for y in range(chamber_y, chamber_y + chamber_h):
            structures.append(create_structure('CaveWall', chamber_x, y, size=(1, 1)))
            structures.append(create_structure('CaveWall', chamber_x + chamber_w, y, size=(1, 1)))
        
        # Chamber entrance
        entrance_x = chamber_x + chamber_w // 2
        entrance_y = chamber_y
        structures.append(create_structure('Entrance', entrance_x, entrance_y, size=(2, 1)))
        
        # Treasure chest in largest chamber
        if chamber_w >= 10:
            chest_x = chamber_x + chamber_w // 2
            chest_y = chamber_y + chamber_h // 2
            structures.append(create_structure('TreasureChest', chest_x, chest_y))
    
    # Stalactites and stalagmites
    feature_count = (width * height) // 100
    for _ in range(feature_count):
        x = random.randint(10, width - 10)
        y = random.randint(10, height - 10)
        feature_type = random.choice(['Stalactite', 'Stalagmite', 'CrystalFormation'])
        structures.append(create_structure(feature_type, x, y, size=(1, 1)))
    
    return structures

def generate_space_structures(size: Tuple[int, int]) -> List[Dict]:
    """Generate structures for space environment"""
    structures = []
    width, height = size
    
    # Space station in center
    station_x, station_y = width // 2, height // 2
    structures.append(create_structure('SpaceStation', station_x, station_y, size=(15, 10)))
    
    # Landing pads
    pads = [
        (station_x - 20, station_y),
        (station_x + 20, station_y),
        (station_x, station_y - 15),
        (station_x, station_y + 15),
    ]
    
    for x, y in pads:
        if 0 < x < width and 0 < y < height:
            structures.append(create_structure('LandingPad', x, y, size=(6, 6)))
    
    # Scattered asteroids
    asteroid_count = (width * height) // 200
    for _ in range(asteroid_count):
        x = random.randint(10, width - 10)
        y = random.randint(10, height - 10)
        # Don't place asteroids too close to station
        if abs(x - station_x) > 25 or abs(y - station_y) > 25:
            asteroid_size = random.choice([(2, 2), (3, 3), (4, 4)])
            structures.append(create_structure('Asteroid', x, y, size=asteroid_size))
    
    return structures

def create_structure(structure_type: str, x: int, y: int, size: Tuple[int, int] = (4, 4)) -> Dict:
    """Create a structure definition"""
    return {
        "type": structure_type,
        "position": {"x": x, "y": y},
        "size": {"width": size[0], "height": size[1]},
        "rotation": 0,
        "properties": get_structure_properties(structure_type)
    }

def get_structure_properties(structure_type: str) -> Dict:
    """Get default properties for structure types"""
    properties = {
        # Buildings
        'House': {'material': 'Wood', 'color': 'Brown', 'has_door': True, 'interactable': True},
        'Cottage': {'material': 'Stone', 'color': 'Gray', 'has_door': True, 'interactable': True},
        'Shop': {'material': 'Wood', 'color': 'Blue', 'has_door': True, 'interactable': True, 'shop_type': 'general'},
        'TownHall': {'material': 'Stone', 'color': 'White', 'has_door': True, 'interactable': True},
        'Castle': {'material': 'Stone', 'color': 'Gray', 'has_door': True, 'interactable': True, 'height': 20},
        'Tower': {'material': 'Stone', 'color': 'Gray', 'height': 15, 'interactable': True},
        'Watchtower': {'material': 'Stone', 'color': 'Gray', 'height': 12, 'interactable': True},
        
        # Natural features
        'OakTree': {'material': 'Wood', 'color': 'Brown', 'height': 8, 'has_leaves': True},
        'PineTree': {'material': 'Wood', 'color': 'DarkBrown', 'height': 10, 'has_leaves': True},
        'BirchTree': {'material': 'Wood', 'color': 'LightBrown', 'height': 7, 'has_leaves': True},
        'WillowTree': {'material': 'Wood', 'color': 'Brown', 'height': 6, 'has_leaves': True},
        
        # Interactive objects
        'Well': {'material': 'Stone', 'color': 'Gray', 'interactable': True, 'function': 'water_source'},
        'Campfire': {'material': 'Wood', 'color': 'Orange', 'interactable': True, 'lit': True},
        'TreasureChest': {'material': 'Wood', 'color': 'Brown', 'interactable': True, 'has_loot': True},
        
        # Structural
        'Wall': {'material': 'Stone', 'color': 'Gray', 'height': 3},
        'CaveWall': {'material': 'Rock', 'color': 'DarkGray', 'height': 5},
        'Entrance': {'material': 'Air', 'passable': True},
        
        # Cave features
        'Stalactite': {'material': 'Rock', 'color': 'Gray', 'hangs_from_ceiling': True},
        'Stalagmite': {'material': 'Rock', 'color': 'Gray', 'rises_from_floor': True},
        'CrystalFormation': {'material': 'Crystal', 'color': 'Blue', 'glows': True},
        'CaveEntrance': {'material': 'Rock', 'color': 'DarkGray', 'interactable': True, 'leads_to': 'cave'},
        
        # Space structures
        'SpaceStation': {'material': 'Metal', 'color': 'Silver', 'has_door': True, 'interactable': True},
        'LandingPad': {'material': 'Metal', 'color': 'Blue', 'landing_point': True},
        'Asteroid': {'material': 'Rock', 'color': 'Gray', 'minable': True},
        
        # Camp
        'Tent': {'material': 'Fabric', 'color': 'Green', 'has_door': True, 'interactable': True},
        'PeasantHouse': {'material': 'Wood', 'color': 'Brown', 'has_door': True, 'interactable': True},
    }
    
    return properties.get(structure_type, {'material': 'Wood', 'color': 'Brown'})

def generate_spawn_points(env_type: str, size: Tuple[int, int], structures: List[Dict]) -> List[Dict]:
    """Generate player and NPC spawn points"""
    spawn_points = []
    width, height = size
    
    # Player spawn point (safe location)
    if env_type == 'village':
        # Spawn in village center
        spawn_points.append({
            "type": "player",
            "position": {"x": width // 2, "y": height // 2 + 10},
            "safe": True
        })
    elif env_type == 'cave':
        # Spawn at cave entrance
        spawn_points.append({
            "type": "player",
            "position": {"x": 10, "y": height // 2},
            "safe": True
        })
    else:
        # Spawn at edge of map
        spawn_points.append({
            "type": "player",
            "position": {"x": 10, "y": height // 2},
            "safe": True
        })
    
    # NPC spawn points near structures
    for structure in structures:
        if structure["type"] in ["Shop", "TownHall", "House"]:
            spawn_points.append({
                "type": "npc",
                "position": {
                    "x": structure["position"]["x"] + 2,
                    "y": structure["position"]["y"] + 2
                },
                "npc_type": get_npc_type_for_structure(structure["type"]),
                "safe": True
            })
    
    # Enemy spawn points
    if env_type == 'cave':
        # Spawn enemies in cave chambers
        enemy_count = 5
        for _ in range(enemy_count):
            x = random.randint(20, width - 20)
            y = random.randint(20, height - 20)
            spawn_points.append({
                "type": "enemy",
                "position": {"x": x, "y": y},
                "enemy_type": random.choice(["Skeleton", "Spider", "Bat"]),
                "safe": False
            })
    elif env_type == 'forest':
        # Spawn forest creatures
        creature_count = 3
        for _ in range(creature_count):
            x = random.randint(15, width - 15)
            y = random.randint(15, height - 15)
            spawn_points.append({
                "type": "enemy",
                "position": {"x": x, "y": y},
                "enemy_type": random.choice(["Wolf", "Bear", "Bandit"]),
                "safe": False
            })
    
    return spawn_points

def get_npc_type_for_structure(structure_type: str) -> str:
    """Get appropriate NPC type for structure"""
    npc_mapping = {
        "Shop": "Shopkeeper",
        "TownHall": "Mayor",
        "House": "Villager",
        "Cottage": "Farmer",
        "Castle": "Guard",
        "Tower": "Wizard"
    }
    return npc_mapping.get(structure_type, "Villager")

def generate_atmosphere(env_type: str) -> Dict:
    """Generate atmosphere settings for the environment"""
    atmosphere_configs = {
        'village': {
            'sky_color': '#87CEEB',
            'fog_color': '#F0F8FF',
            'fog_density': 0.1,
            'lighting': 'bright',
            'ambient_sound': 'village_ambience',
            'time_of_day': 'noon'
        },
        'forest': {
            'sky_color': '#228B22',
            'fog_color': '#90EE90',
            'fog_density': 0.3,
            'lighting': 'filtered',
            'ambient_sound': 'forest_ambience',
            'time_of_day': 'morning'
        },
        'desert': {
            'sky_color': '#FFD700',
            'fog_color': '#F4A460',
            'fog_density': 0.2,
            'lighting': 'harsh',
            'ambient_sound': 'desert_wind',
            'time_of_day': 'afternoon'
        },
        'mountain': {
            'sky_color': '#4682B4',
            'fog_color': '#B0C4DE',
            'fog_density': 0.4,
            'lighting': 'cool',
            'ambient_sound': 'mountain_wind',
            'time_of_day': 'evening'
        },
        'beach': {
            'sky_color': '#00BFFF',
            'fog_color': '#F0F8FF',
            'fog_density': 0.1,
            'lighting': 'warm',
            'ambient_sound': 'ocean_waves',
            'time_of_day': 'sunset'
        },
        'cave': {
            'sky_color': '#000000',
            'fog_color': '#2F2F2F',
            'fog_density': 0.6,
            'lighting': 'dark',
            'ambient_sound': 'cave_echoes',
            'time_of_day': 'none'
        },
        'space': {
            'sky_color': '#000000',
            'fog_color': '#191970',
            'fog_density': 0.0,
            'lighting': 'artificial',
            'ambient_sound': 'space_hum',
            'time_of_day': 'none'
        },
        'medieval': {
            'sky_color': '#708090',
            'fog_color': '#D3D3D3',
            'fog_density': 0.2,
            'lighting': 'medieval',
            'ambient_sound': 'medieval_ambience',
            'time_of_day': 'dusk'
        }
    }
    
    return atmosphere_configs.get(env_type, atmosphere_configs['village'])

def generate_paths(structures: List[Dict], size: Tuple[int, int]) -> List[Dict]:
    """Generate paths connecting structures"""
    paths = []
    
    # Find important structures to connect
    important_structures = [s for s in structures if s["type"] in 
                          ["TownHall", "Castle", "Shop", "House", "SpaceStation"]]
    
    # Connect structures with paths
    for i, start_struct in enumerate(important_structures):
        for end_struct in important_structures[i+1:]:
            start_pos = start_struct["position"]
            end_pos = end_struct["position"]
            
            # Generate simple straight path
            path_points = generate_straight_path(
                (start_pos["x"], start_pos["y"]),
                (end_pos["x"], end_pos["y"])
            )
            
            paths.append({
                "type": "road",
                "points": path_points,
                "width": 2,
                "material": "Stone"
            })
    
    return paths

def generate_straight_path(start: Tuple[int, int], end: Tuple[int, int]) -> List[Dict]:
    """Generate a straight path between two points"""
    start_x, start_y = start
    end_x, end_y = end
    
    points = []
    
    # Calculate steps
    dx = end_x - start_x
    dy = end_y - start_y
    steps = max(abs(dx), abs(dy))
    
    if steps == 0:
        return points
    
    step_x = dx / steps
    step_y = dy / steps
    
    for i in range(steps + 1):
        x = int(start_x + step_x * i)
        y = int(start_y + step_y * i)
        points.append({"x": x, "y": y})
    
    return points

def generate_mountain_features(size: Tuple[int, int]) -> List[Dict]:
    """Generate mountain-specific terrain features"""
    features = []
    width, height = size
    
    # Add some peaks
    peak_count = random.randint(3, 6)
    for _ in range(peak_count):
        x = random.randint(width//4, 3*width//4)
        y = random.randint(height//4, 3*height//4)
        features.append({
            "type": "peak",
            "position": {"x": x, "y": y},
            "height": random.randint(20, 40)
        })
    
    return features

def generate_forest_features(size: Tuple[int, int]) -> List[Dict]:
    """Generate forest-specific terrain features"""
    features = []
    width, height = size
    
    # Add clearings
    clearing_count = random.randint(2, 4)
    for _ in range(clearing_count):
        x = random.randint(10, width-10)
        y = random.randint(10, height-10)
        radius = random.randint(5, 10)
        features.append({
            "type": "clearing",
            "position": {"x": x, "y": y},
            "radius": radius
        })
    
    return features

def generate_desert_features(size: Tuple[int, int]) -> List[Dict]:
    """Generate desert-specific terrain features"""
    features = []
    width, height = size
    
    # Add oases
    oasis_count = random.randint(1, 3)
    for _ in range(oasis_count):
        x = random.randint(20, width-20)
        y = random.randint(20, height-20)
        features.append({
            "type": "oasis",
            "position": {"x": x, "y": y},
            "radius": random.randint(3, 8)
        })
    
    return features

def generate_beach_features(size: Tuple[int, int]) -> List[Dict]:
    """Generate beach-specific terrain features"""
    features = []
    width, height = size
    
    # Add rock formations along shore
    rock_count = random.randint(3, 8)
    for _ in range(rock_count):
        x = random.randint(int(width*0.2), int(width*0.6))
        y = random.randint(10, height-10)
        features.append({
            "type": "rock_formation",
            "position": {"x": x, "y": y},
            "size": random.randint(2, 5)
        })
    
    return features

def generate_castle_walls(center_x: int, center_y: int, wall_width: int, wall_height: int) -> List[Tuple[int, int]]:
    """Generate points for castle walls"""
    points = []
    
    # Top wall
    for x in range(center_x - wall_width//2, center_x + wall_width//2):
        points.append((x, center_y - wall_height//2))
    
    # Bottom wall
    for x in range(center_x - wall_width//2, center_x + wall_width//2):
        points.append((x, center_y + wall_height//2))
    
    # Left wall
    for y in range(center_y - wall_height//2, center_y + wall_height//2):
        points.append((center_x - wall_width//2, y))
    
    # Right wall
    for y in range(center_y - wall_height//2, center_y + wall_height//2):
        points.append((center_x + wall_width//2, y))
    
    return points

def generate_fallback_environment(size: Tuple[int, int]) -> Dict:
    """Generate a basic fallback environment when other methods fail"""
    width, height = size
    
    return {
        "type": "plains",
        "size": size,
        "terrain": {
            "type": "plains",
            "heightmap": [[random.uniform(0, 2) for _ in range(width)] for _ in range(height)],
            "materials": [["Grass" for _ in range(width)] for _ in range(height)],
            "features": []
        },
        "structures": [
            create_structure("House", width//2, height//2)
        ],
        "spawn_points": [
            {
                "type": "player",
                "position": {"x": 10, "y": height//2},
                "safe": True
            }
        ],
        "atmosphere": generate_atmosphere("village"),
        "paths": [],
        "metadata": {
            "prompt": "fallback environment",
            "version": "1.0"
        }
    }