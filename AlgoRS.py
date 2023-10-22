import matplotlib.pyplot as plt
import random
import numpy as np
import copy


###Fonctions de cout et d'affichage

def genOrdo(n_patient):
    """Génère un ordonnancement au hasard -> Sert uniquement en test"""

    return [[random.randint(5,10),random.randint(10,30),random.randint(40,120),random.randint(10,30)] for _ in range(n_patient)]

def choixRessource(phase):
    """Soit phase une liste de ressources, cette fonction détermine quelle ressource prend la tâche"""

    mini = phase[0][-1][1]+phase[0][-1][2]
    index = 0

    found = False
    iRessource = 0

    while (not found) and iRessource < len(phase):
        ressource = phase[iRessource]
        if ressource == [(0,0,0)]:
            found = True
            index = iRessource
        elif ressource[-1][1]+ressource[-1][2] < mini:
            mini = ressource[-1][1]+ressource[-1][2]
            index = iRessource
        iRessource+=1

    return index

def searchPatient(ind, phase):
    """Trouve le patient n°ind dans la phase *phase*"""

    found = False
    iPhase = 0

    while (not found) and iPhase < len(phase):
        ressource = phase[iPhase]
        iRessource = 0
        while iRessource < len(ressource):
            patient = ressource[iRessource]
            if patient[0] == ind:
                found = True
                reponse = patient
            iRessource += 1
        iPhase+=1

    if found:
        return reponse
    else:
        return None

def decalPhase(ind, phase, delai):
    """Cette fonction décale d'un temps delai le patient ind dans la phase *phase*"""

    found = False
    iPhase = 0

    while (not found) and iPhase < len(phase):
        ressource = phase[iPhase]
        iRessource = 0
        while iRessource < len(ressource):
            patient = ressource[iRessource]
            if patient[0] == ind:
                found = True
                phase[iPhase][iRessource] = (phase[iPhase][iRessource][0], phase[iPhase][iRessource][1] + delai, phase[iPhase][iRessource][2]) # Un tuple n'est pas modifiable donc je dois le remplacer avec la nouvelle valeur
            iRessource += 1
        iPhase+=1


def arrangementFinal(ordo, nSSPIEntree = 3, nSSPIReveil = 3, nBloc = 4, nChir = 5, nAnesthesiste = 8, nBrancardier = 2):
    """Construit l'arrangement final en prenant en compte toutes les contraintes de ressources et de capacité"""

    # Initialisation des listes de phases qui représentent le passage
    # des patients dans chaque 'phase' : dans chaque phase il y a nPhase ressources
    # et dans chaque ressource il y aura des patients au format (id du patient, instant de début de la tâche, duree de la tâche)

    ordresBrancardiers = [[(0, 0, 0)] for _ in range(nBrancardier)]
    ordresSSPIEntrees = [[(0, 0, 0)] for _ in range(nSSPIEntree)]
    ordresBlocs = [[(0, 0, 0)] for _ in range(nBloc)]
    ordresSSPIReveils = [[(0, 0, 0)] for _ in range(nSSPIReveil)]

    for ind, patient in enumerate(ordo):

        # Choix du bloc : attribution prioritaire car c'est ce qu'on optimise, et les autres taches en dépendent
        bloc = choixRessource(ordresBlocs)
        if ordresBlocs[bloc] == [(0, 0, 0)] :     # Pour traiter les premiers cas, dû à l'initialisation, on remplace au lieu d'ajouter
            ordresBlocs[bloc] = [(ind, 0, patient[2])]
        else :
            readyTime = ordresBlocs[bloc][-1][1] + ordresBlocs[bloc][-1][2] + 10
            ordresBlocs[bloc].append((ind, readyTime, patient[2]))

        # Choix du lit SSPI + attribution du patient:
        litSSPIEntree = choixRessource(ordresSSPIEntrees)
        blocPhase = searchPatient(ind, ordresBlocs) # On retrouve les données de ce patient au bloc
        if ordresSSPIEntrees[litSSPIEntree] == [(0,0,0)] :   # Pour traiter les premiers cas, dû à l'initialisation, on remplace au lieu d'ajouter
            ordresSSPIEntrees[litSSPIEntree] = [(ind, blocPhase[1]-patient[1], patient[1])]
        else :
            readyTime = ordresSSPIEntrees[litSSPIEntree][-1][1] + ordresSSPIEntrees[litSSPIEntree][-1][2] # fin de la tâche précédente
            if readyTime + patient[1] < blocPhase[1] : # Si la tache a le temps d'être faite entre la fin de la précédente et le début du bloc
                ordresSSPIEntrees[litSSPIEntree].append((ind, blocPhase[1]-patient[1], patient[1]))
            else :     # Si on n'a pas le temps, il faut décaler le bloc
                decalPhase(ind, ordresBlocs, readyTime + patient[1] - blocPhase[1])
                ordresSSPIEntrees[litSSPIEntree].append((ind, readyTime, patient[1]))

        # Choix du brancardier + attribution du patient:
        brancardier = choixRessource(ordresBrancardiers)
        SSPIEntreePhase = searchPatient(ind, ordresSSPIEntrees) # On retrouve les données de ce patient au SSPI d'entree
        if ordresBrancardiers[brancardier] == [(0,0,0)] : # Pour traiter les premiers cas, dû à l'initialisation, on remplace au lieu d'ajouter
            ordresBrancardiers[brancardier] =  [(ind, SSPIEntreePhase[1] - patient[0], patient[0])]
        else :
            readyTime = ordresBrancardiers[brancardier][-1][1] + ordresBrancardiers[brancardier][-1][2] # fin de la tâche précédente
            if readyTime + patient[0] < SSPIEntreePhase[1] : # Si la tache a le temps d'être faite entre la fin de la précédente et le début du SSPI d'entrée
                ordresBrancardiers[brancardier].append((ind, SSPIEntreePhase[1] - patient[0], patient[0]))
            else :     # Si on n'a pas le temps, il faut décaler le SSPI d'entrée et le bloc
                decalPhase(ind, ordresBlocs, readyTime + patient[0] - SSPIEntreePhase[1])
                decalPhase(ind, ordresSSPIEntrees, readyTime + patient[0] - SSPIEntreePhase[1])
                ordresBrancardiers[brancardier].append((ind, readyTime, patient[0]))

        # Choix du lit SSPIReveil
        litSSPIReveil = choixRessource(ordresSSPIReveils)
        previousPhase = searchPatient(ind, ordresBlocs) # On retrouve ses données à la phase précédente
        if ordresSSPIReveils[litSSPIReveil] == [(0,0,0)] :   # Pour traiter les premiers cas, dû à l'initialisation, on remplace au lieu d'ajouter
            ordresSSPIReveils[litSSPIReveil] = [(ind, previousPhase[1] + previousPhase[2], patient[3])]
        else :
            readyTime = max(ordresSSPIReveils[litSSPIReveil][-1][1] + ordresSSPIReveils[litSSPIReveil][-1][2], previousPhase[1] + previousPhase[2])
            ordresSSPIReveils[litSSPIReveil].append((ind, readyTime, patient[3]))

    return [ordresBrancardiers, ordresSSPIEntrees, ordresBlocs, ordresSSPIReveils]

def coutOrdo(arrangement):
    """Prend en entree un arrangement et donne son coût temporel total"""

    brancardiers = arrangement[0]
    debut = min([brancardier[0][1] for brancardier in brancardiers])  # date de debut minimale de tous les brancardiers (forcément parmi les premières prises en charge de chacun)

    litsReveil = arrangement[-1]
    fin = max(lit[-1][1]+lit[-1][2] for lit in litsReveil) # date de fin maximale de tous les lits de réveil (parmi leur dernière prise en charge)

    return fin - debut



# Calcul le cout temporel total (du premier brancardage au dernier réveil en SSPI)
# et le temps passé en bloc (de h0 à sorti de la dernière opération)
def cout(ordo):
    liste = Lecture(ordo, 0)
    debutPremierActe = 0
    finDernierActe = 0
    ifinal = 0

    for i in range (len(liste)) :
        debutPremierActe = min(liste[i][0], debutPremierActe)
        finDernierActe = max(liste[i][3]+ordo[i][3], finDernierActe)

    coutTotal = finDernierActe - debutPremierActe
    coutBloc = liste[-1][3]
    return coutTotal, coutBloc


def emploiDuTemps(arrangement):
    """Affiche sous forme de diagramme en barre l'emploi du temps global d'un arrangement"""

    titres = [f"Brancardier {i+1}" for i in range(len(arrangement[0]))] + [f"Lit {i+1} en SSPIEntree" for i in range(len(arrangement[1]))] + [f"Bloc {i+1}" for i in range(len(arrangement[2]))] + [f"Lit {i+1} en SSPIReveil" for i in range(len(arrangement[3]))]
    couleurs = ['blue', 'red', 'green', 'yellow', 'black', 'purple', 'pink', 'orange', 'grey', 'brown']

    # Créer un graphique en barres horizontales
    ind = 0
    for phase in arrangement:
        for ressource in phase:
            for patient in ressource:
                plt.barh(titres[ind], left=patient[1], width = patient[2], color=couleurs[patient[0]%10])
            ind += 1

    # Ajouter des étiquettes d'axe et un titre
    plt.xlabel("Durée (minutes)")
    plt.ylabel("Phases")
    plt.title("Prise en charge des patients")

    plt.show()
###Algorithme RS



n_iter = 1000
fact_refroid = 0.96
k_constant = 100
temperature_ini = 273




def gen_solution_initiale():
    solution = [list(range(n_patient)) for _ in range(4)]
    for s in solution:
        rd.shuffle(s)
    return solution




def solution_voisine(ordo):
    possibility = [k for k in range(len(ordo))]
    i_patient1 = random.choice(possibility)
    possibility.remove(i_patient1)
    i_patient2 = random.choice(possibility)
    n_ordo = copy.deepcopy(ordo)
    n_ordo[i_patient1]=ordo[i_patient2]
    n_ordo[i_patient2]=ordo[i_patient1]
    return n_ordo

def heuristique_rc(ordo,n_iter,fact_refroid,temperature_ini,k_constant):
    temperature=temperature_ini
    arrangement = arrangementFinal(ordo)
    energie = coutOrdo(arrangement)
    print(energie)
    for _ in range(n_iter):
        n_ordo = solution_voisine(ordo)
        energie_voisine = coutOrdo(arrangementFinal(n_ordo))
        delta_e = (energie_voisine - energie)
        facteur = -delta_e/(k_constant*temperature)
        if facteur > 0:
            probability =1
        elif facteur < -10 :
            probabily = 0
        else :
            probability = np.exp(facteur)
        if random.random() < probability:
            ordo = n_ordo
            energie = energie_voisine
        temperature *= fact_refroid
    print(energie)


ordo = genOrdo(10)
heuristique_rc(ordo,n_iter,fact_refroid,temperature_ini,k_constant)


