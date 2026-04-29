import time
import threading
import requests
import math
from datetime import datetime
from models.db_manager import DBManager

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000                            
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class TelemetrySimulator(threading.Thread):
    def __init__(self, db_manager: DBManager, update_interval=2):
        super().__init__()
        self.db = db_manager
        self.update_interval = update_interval
        self.running = True
        self.truck_states = {}
        self.daemon = True
        self.MAX_RANGE_METERS = 800000.0                       

    def fetch_route(self, coords):
                                        
        try:
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
            url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
            response = requests.get(url, headers={'User-Agent': 'AlexanderMoya/1.0'}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:
                    route_coords = data['routes'][0]['geometry']['coordinates']
                    distance = data['routes'][0]['distance']         
                    duration = data['routes'][0]['duration']          
                    return [(lat, lon) for lon, lat in route_coords], distance, duration
        except Exception as e:
            print(f"Error fetching route: {e}")
        return [(coords[0][0], coords[0][1]), (coords[-1][0], coords[-1][1])], 0, 0

    def start_custom_route(self, placa, lat1, lon1, lat2, lon2):
                                         
        direct_route, dist, duration = self.fetch_route([(lat1, lon1), (lat2, lon2)])
        
        has_gas_stop = False
        gas_stop_index = -1
        
                                                                            
        if dist > 600000.0 and len(direct_route) > 2:
            midpoint = direct_route[len(direct_route) // 2]
                                                                      
            gas_lat = midpoint[0] + 0.005
            gas_lon = midpoint[1] + 0.005
            
                                 
            final_route, dist, duration = self.fetch_route([(lat1, lon1), (gas_lat, gas_lon), (lat2, lon2)])
            has_gas_stop = True
            gas_stop_index = len(final_route) // 2                                             
        else:
            final_route = direct_route

        self.truck_states[placa] = {
            'lat': final_route[0][0], 'lon': final_route[0][1], 'gas': 100.0, 
            'last_move_time': time.time(),
            'stopped': False,
            'route': final_route,
            'route_index': 0,
            'alert_sent': False,
            'total_distance': dist,
            'total_duration': duration,
            'has_gas_stop': has_gas_stop,
            'gas_stop_index': gas_stop_index,
            'eta_text': self.format_eta(duration)
        }

    def format_eta(self, seconds):
        if seconds <= 0: return "Llegando..."
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def run(self):
        while self.running:
            self._simulate_step()
            time.sleep(self.update_interval)

    def _simulate_step(self):
        placas = self.db.get_all_trucks()
        for placa in placas:
            info = self.db.get_truck_info(placa)
            if info and info['viaje'] and info['camion']['estado'] != 'ACCIDENTE':
                self._update_truck(placa, info)

    def _update_truck(self, placa, info):
        if placa not in self.truck_states:
            return

        state = self.truck_states[placa]

        if not state.get('stopped', False):
            if state['route_index'] < len(state['route']) - 1:
                current_point = state['route'][state['route_index']]
                
                state['route_index'] += 1
                next_point = state['route'][state['route_index']]
                
                                                       
                step_dist = haversine(current_point[0], current_point[1], next_point[0], next_point[1])
                
                                              
                gas_consumed = (step_dist / self.MAX_RANGE_METERS) * 100.0
                state['gas'] = max(0.0, state['gas'] - gas_consumed)
                
                state['lat'] = next_point[0]
                state['lon'] = next_point[1]
                state['last_move_time'] = time.time()
                
                                          
                if state['has_gas_stop'] and state['route_index'] == state['gas_stop_index']:
                    state['gas'] = 100.0          
                    self.db.log_alert(placa, "RECARGA", "Se detuvo en estación de servicio (Diesel) y recargó al 100%.")

                            
                progress = state['route_index'] / len(state['route'])
                remaining_seconds = state['total_duration'] * (1.0 - progress)
                state['eta_text'] = self.format_eta(remaining_seconds)
                
                                       
                if state['route_index'] >= len(state['route']) - 1:
                                            
                    self.db.end_trip(placa)
                    self.db.update_truck_state(placa, "ACTIVO")
                    self.db.log_alert(placa, "LLEGADA", "Viaje completado exitosamente. Camión devuelto a base.")
                    state['eta_text'] = "Llegó a su destino"
                    state['stopped'] = True
            
                             
        self.db.add_telemetry(placa, state['lat'], state['lon'], state['gas'])

                                      
        idle_time = time.time() - state['last_move_time']
        if idle_time > (45 * 60) and not state.get('stopped', False):
            if not state.get('alert_sent'):
                self.db.log_alert(placa, "DETENCION_PROLONGADA", f"El camión {placa} ha estado detenido por más de 45 minutos.")
                state['alert_sent'] = True
        else:
            state['alert_sent'] = False

    def stop_truck(self, placa):
        if placa in self.truck_states:
            self.truck_states[placa]['stopped'] = True
            self.truck_states[placa]['last_move_time'] = time.time() - (46 * 60)

    def stop_simulation(self):
        self.running = False
