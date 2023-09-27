###Algorythme RS
import numpy as np
import random as rd
import matplotlib.pyplot as pl
import copy

n_patient = 100
n_medecin = 1
n_salle = 1
SSPI_cap = 3
n_phase = 4
n_iter = 100000
fact_refroid = 0.99
k = 1
#Brancardier -> SSPI -> Opération -> SSPI
#Un seul brancardier



def gen_liste_ope(n_patient):
    return [[rd.randint(5,10),rd.randint(10,30),rd.randint(40,120),rd.randint(10,30)] for i in range(n_patient)]


def gen_solution_initiale():
    solution = [list(range(n_patient)) for _ in range(4)]
    for s in solution:
        rd.shuffle(s)
    return solution



#Nécessaire à la fonction c_max
def patient_precedant(phase,patient, solution, n_patient):
    k = 0
    while solution[phase][k] != patient:
        k+=1
        if k >= n_patient:
            return None
    return solution[phase][k-1]




def c_max(solution, liste_ope):
    tab_time = [[0 for k in range(n_patient)] for k in range(n_phase)]
    tab_time[0] = [liste_ope[solution[0][i]][0] + (tab_time[0][i-1] if i > 0 else 0) for i in range(n_patient)]

    for j in range(1, n_phase):
        for i in range(n_patient):
            previous_patient = patient_precedant(j, i, solution, n_patient)
            previous_time = tab_time[j][previous_patient] if previous_patient is not None else 0

            if j in [1, 3]:  # Les phases 2 et 4
                # Prendre en compte la capacité SSPI_cap
                # Récupérer les temps des SSPI_cap patients précédents
                waiting_times = [tab_time[j][i-x] for x in range(1, min(SSPI_cap, i+1)+1)]

                # Trouver le temps le plus court parmi ces patients
                earliest_free_time = min(waiting_times)

                tab_time[j][i] = earliest_free_time + liste_ope[solution[j][i]][j]

            else:
                tab_time[j][i] = max(previous_time, tab_time[j-1][i]) + liste_ope[solution[j][i]][j]

    return max(tab_time[n_phase-1])

def solution_voisine(solution, liste_ope):
    phase = rd.randint(0,n_phase-1)
    possibility = [k for k in range(n_patient)]
    i_patient1 = rd.choice(possibility)
    possibility.remove(i_patient1)
    i_patient2 = rd.choice(possibility)
    n_solution = copy.deepcopy(solution)
    n_solution[phase][i_patient1]=solution[phase][i_patient2]
    n_solution[phase][i_patient2]=solution[phase][i_patient1]
    return n_solution

def heuristique_rc(n_patient,n_phase,n_iter,fact_refroid):
    temperature = 10000
    liste_ope = gen_liste_ope(n_patient)
    solution = gen_solution_initiale()
    energie = c_max(solution, liste_ope)
    for _ in range(n_iter):
        n_solution = solution_voisine(solution, liste_ope)
        energie_voisine = c_max(n_solution, liste_ope)
        delta_e = (energie_voisine - energie)
        facteur = -delta_e/(k*temperature)
        if facteur > 0:
            probability =1
        elif facteur < -300 :
            probabily = 0
        else :
            probability = np.exp(facteur)
        if rd.random() < probability:
            solution = n_solution
            energie = energie_voisine
        temperature *= fact_refroid
    print(energie)
    print(temperature)
    "return solution,energie"


