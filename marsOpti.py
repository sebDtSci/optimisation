import sys
import math

pastX = []
pastY = []
good = []
landYG = 0
target_center = 0
max_fuel = float('-inf')

n = int(input())  
for i in range(n):
    land_x, land_y = [int(j) for j in input().split()]
    # print(f"land_y: {land_y}", file=sys.stderr, flush=True)
    if not pastX:
        pastX.append(land_x)
        pastY.append(land_y)
    else:
        if land_y == pastY[-1]:
            good.append(pastX[-1])
            good.append(land_x)
            landYG = land_y
        pastX.append(land_x)
        pastY.append(land_y)

sommet = [el for el in pastY if el > landYG]
def find_peaks(pastX, pastY, landYG):
    """
    Trouve les coordonnées des sommets (x, y) où y > landYG.
    """
    peaks = [(x, y) for x, y in zip(pastX, pastY) if y > landYG]
    return peaks

peaks = find_peaks(pastX,pastY,landYG)

def check_trajectory_against_peaks(trajectory, peaks):
    """
    Vérifie si la trajectoire touche ou passe sous les sommets.
    Retourne True si une collision ou un passage sous un sommet est détecté.
    """
    for x, y, _, _,_ in trajectory:
        for px, py in peaks:
            # if abs(x - px) <= 10 and y <= py+100: 
            if abs(x - px) <= 10 and y < py: 
                return True
    return False

print(f"good: {good}", file=sys.stderr, flush=True)
target_center = good[0] + ((good[1]-good[0])//2)

def print_ctrl(distance, distanceT, dp, y, hs, vs, landYG):
    print(f"target center: {target_center}", file=sys.stderr, flush=True)
    print(f"distance: {distance}", file=sys.stderr, flush=True)
    print(f"distance du centre: {distanceT}", file=sys.stderr, flush=True)
    print(f"dp: {dp}", file=sys.stderr, flush=True)
    print(f"dp - distance: {dp - distance}", file=sys.stderr, flush=True)
    print(f"dp+60: {dp+60}", file=sys.stderr, flush=True)
    print(f"Hauteur: {y - landYG}", file=sys.stderr, flush=True)
    print(f"Y: {y}", file=sys.stderr, flush=True)
    # print(f"landYG: {landYG}", file=sys.stderr, flush=True)
    # print(f"VS: {vs}", file=sys.stderr, flush=True)
    # print(f"max_fuel: {max_fuel}", file=sys.stderr, flush=True)
    
    return 0

def dist_center(x, xc):
    if x <= xc:
        distance = int(xc - x)
    else:
        distance = int(x - xc)
    return distance

def dist(x:int, xm_d:int, xm_f:int )-> int:
    if xm_d < x < xm_f:
        distance = 0
    if x <= xm_d:
        distance = int(xm_d - x)
    if x >= xm_f:
        distance = int(x - xm_f)
    return distance

def simulate_trajectory(x, y, hs, vs, f, angle, thrust, landYG, peaks, max_steps=500):
    """
    Simule la trajectoire du module et renvoie la vitesse et position finale.
    """
    g = 3.711  # Gravité martienne
    trajectory = []
    
    for step in range(max_steps):
        # Calcul de l'accélération horizontale et verticale
        ax = -thrust * math.sin(math.radians(angle))
        ay = thrust * math.cos(math.radians(angle)) - g

        # Mise à jour des vitesses
        hs += ax
        vs += ay

        # Mise à jour des positions
        # x += hs
        # y += vs

        # version avec accélération
        # x = x + hs - ax * 0.5
        # y = y + vs + ay * 0.5 
        x = x + hs + 0.5 * ax
        y = y + vs + 0.5 * ay

        # Trajectoire
        # trajectory.append((x, y, hs, vs))

        if thrust > 0:
            f -= thrust
            if f <= 0: 
                thrust = 0
        trajectory.append((x, y, hs, vs, f))
        # Arrêter si on atteint ou dépasse le sol
        # if y <= landYG+10:
        if y <= landYG+5:
            break
    touches_peak = check_trajectory_against_peaks(trajectory, peaks)
    # Retourne la trajectoire complète et l'état final
    return trajectory, (x, y, hs, vs, f), touches_peak

def optimize_landing(x, y, hs, vs, f, landYG, good, peaks, distance, max_steps=500):
    """
    Optimise les commandes pour un atterrissage vertical et sécurisé.
    """
    print(f"Opti phase", file=sys.stderr, flush=True)
    g = 3.711  # Gravité martienne
    best_angle, best_thrust = 0, 0
    min_error = float('inf')
    best_final_state = None

    # Best one
    # coef_1 = 4
    # coef_2 = 6

    # test
    # coef_1 = 4
    # coef_2 = 7


    if y - landYG > 1000:  
        coef_1 = 3
        coef_2 = 4 #4
    else: 
        coef_1 = 5 #5
        coef_2 = 7 #7

    if y - landYG > 1000:  
        angle_step = 1
    else:  
        angle_step = 1

    
    for angle in range(-90, 91, angle_step):  # Explore les angles par pas de 1°
        for thrust in range(0, 5):  # Explore les poussées possibles
            _, (pred_x, pred_y, pred_hs, pred_vs, pf), touches_peak = simulate_trajectory(
                x, y, hs, vs, f, angle, thrust, landYG, peaks, max_steps
            )

            # tentative d'une pénalisation quadratique mdr
            max_fuel_penality = 200 #200
            # fuel_penalty = max_fuel_penality * ((max_fuel - pf) / max_fuel) ** 2

            # tentative d'une pénalisation expo 
            # alpha = 0.005
            # fuel_penalty = max_fuel_penality * math.exp(-alpha * pf)

            # tentative d'une pénalisation linéaire inversée 
            fuel_penalty = max_fuel_penality * (1 - pf / max_fuel)

            # sortie = float('inf') if pred_x < 0 or pred_x > 7000 else 0
            sommetE = float('inf') if touches_peak else 0
            # Vérifie si la position finale est dans la zone cible
            if good[0] <= pred_x <= good[1]:

                if y - landYG > 1000:  # Phase haute
                    error = (
                        abs(pred_vs) * coef_1 +
                        abs(pred_hs) * coef_2 +
                        abs(pred_x - (good[0] + good[1]) / 2) +
                        abs(pred_y - landYG) * 1.5
                    )
                else:  # Phase basse
                    error = (
                        abs(pred_vs) * coef_1 +
                        abs(pred_hs) * coef_2 +
                        abs(pred_x - (good[0] + good[1]) / 2) * 0.5 +
                        abs(pred_y - landYG) * 2
                    )
                
                error += fuel_penalty + sommetE
                
                
                if error < min_error:
                    min_error = error
                    best_angle, best_thrust = angle, thrust
                    best_final_state = (pred_x, pred_y, pred_hs, pred_vs)


    return best_angle, best_thrust, best_final_state

dp = 0
dr:int = 0
time = 0

while True:
    x, y, hs, vs, f, r, p = [int(i) for i in input().split()]

    distance = dist(x, good[0], good[1])
    distanceT = dist_center(x, target_center)
    direction = -1 if x <target_center else 1

    if f > max_fuel:
        max_fuel = f
    
    angle = dr  # Angle actuel
    thrust = p  # Poussée actuelle
    trajectory, final_state, touches_peak = simulate_trajectory(x, y, hs, vs, f, angle, thrust, landYG, peaks)
    pred_x, pred_y, pred_hs, pred_vs, pf = final_state
    
    print_ctrl(distance, distanceT, dp, y, hs, vs, landYG)
    
    print(f"------------------------------------", file=sys.stderr, flush=True)
    print(f"touches_peak: =>{touches_peak}", file=sys.stderr, flush=True)
    print(f"Prévision de position finale: x={pred_x}, y={pred_y}", file=sys.stderr, flush=True)
    print(f"Vitesse horizontale finale: hs={pred_hs}", file=sys.stderr, flush=True)
    print(f"Vitesse verticale finale: vs={pred_vs}", file=sys.stderr, flush=True)
    print(f"predicted fuel: vs={pf}", file=sys.stderr, flush=True)

    hs_landing_limit = 25
    altitude_limit = 300
    hs_flight_limit = 50
        
    dp = distance
    time +=1

    dr, p, final_state = optimize_landing(x, y, hs, vs, f, landYG, good, peaks, distance)
    print(f"final_state ---->{final_state}", file=sys.stderr, flush=True)

 
    # Phase finale stricte
    if y - landYG < 29 and distance == 0:# and vs > -35:  # Proche du sol 65 75 20
        print(f"final S", file=sys.stderr, flush=True)
        dr = 0  
        p = 4 if vs < -39 or (hs < -20 or hs > 20) else 0
    
    print(f'{dr} {p}')