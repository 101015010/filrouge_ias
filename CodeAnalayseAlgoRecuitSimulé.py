###Import
import matplotlib.pyplot as plt
import random
import numpy as np
import copy

###Fonction de coût
def genOrdo(n_patient):
    #Génère un ordonnancement au hasard -> Sert uniquement en test

    return [[random.randint(5,10),random.randint(10,30),random.randint(40,120),random.randint(10,30)] for _ in range(n_patient)]

def choixRessource(phase):
    #Soit phase une liste de ressources, cette fonction détermine quelle ressource prend la tâche

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
    #Trouve le patient n°ind dans la phase *phase*

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
    #Cette fonction décale d'un temps delai le patient ind dans la phase *phase*

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
    #Construit l'arrangement final en prenant en compte toutes les contraintes de ressources et de capacité

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
    #Prend en entree un arrangement et donne son coût temporel total

    brancardiers = arrangement[0]
    debut = min([brancardier[0][1] for brancardier in brancardiers])  # date de debut minimale de tous les brancardiers (forcément parmi les premières prises en charge de chacun)

    litsReveil = arrangement[-1]
    fin = max(lit[-1][1]+lit[-1][2] for lit in litsReveil) # date de fin maximale de tous les lits de réveil (parmi leur dernière prise en charge)

    return fin - debut

def cout(ordo):
    #Prend en entree un ordo et donne son cout temporel total
    return coutOrdo(arrangementFinal(ordo))



###Algo Recuit simulé


def solution_voisine(ordo):
    possibility = [k for k in range(len(ordo))]
    i_patient1 = random.choice(possibility)
    possibility.remove(i_patient1)
    i_patient2 = random.choice(possibility)
    n_ordo = copy.deepcopy(ordo)
    n_ordo[i_patient1]=ordo[i_patient2]
    n_ordo[i_patient2]=ordo[i_patient1]
    return n_ordo

def mini(l):
    k=0
    ref=l[0]
    for i in range(1,len(l)):
        if ref>l[i]:
            k=i
            ref=l[i]
    return k





def Recuit(ordo,n_iter=1000,fact_refroid = 0.93,temperature_ini = 510,k_constant=6, n_voisins=10):
    temperature=temperature_ini
    energie = cout(ordo)
    energie_initiale = energie
    print(energie)
    count =0
    min_ener = energie
    n_count = 0
    Meilleur_solution=ordo
    k =0
    for j in range(n_iter):
        L_n_ordo = [solution_voisine(ordo) for k in range(n_voisins)]
        L_energie_voisine = list(map(cout, L_n_ordo))
        i =mini(L_energie_voisine)
        n_ordo = L_n_ordo[i]
        energie_voisine = L_energie_voisine[i]
        delta_e = (energie_voisine - energie)
        facteur = -delta_e/(k_constant*temperature)
        if delta_e>0:
            count+=1
        if energie_voisine < min_ener:
            min_ener=energie_voisine
            Meilleur_solution =n_ordo
            k = j
        if facteur > 0:
            probability =1
        elif facteur < -10 :
            probability = 0
        else :
            probability = np.exp(facteur)
        if random.random() < probability:
            count+=1
            if count == 2:
                print("Intéret à l'étape :",j)
                n_count+=1
            ordo = n_ordo
            energie = energie_voisine
        count =0
    print("Durée initiale :", energie_initiale)
    print("Durée finale :", energie)
    print("Durée de la solution optimale rencontrée :", min_ener)
    print("Etape à laquelle elle a été rencontrée :", k)
    print("Nombre de fois où l'on a accepté une solution non-optimale :", n_count)
    if energie > min_ener:
        return Meilleur_solution
    else:
        return ordo

###Tracé de l'optimisation des paramètres

meilleure_solution = None
meilleur_cout = float('inf')
meilleurs_parametres = {}

n_iter_range = [100]
fact_refroid_range = [0.98]
temperature_ini_range = [200]
k_constant_range = [10**(-23)]
moyenne_sur = 50

# Créez des listes pour stocker les résultats
results = []
param_values = []

# Parcourez les combinaisons de paramètres
for n_iter in n_iter_range:
    for fact_refroid in fact_refroid_range:
        for temperature_ini in temperature_ini_range:
            for k_constant in k_constant_range:
                print("Optimisation en cours pour n_iter={}, fact_refroid={}, temperature_ini={}, k_constant={}".format(n_iter, fact_refroid, temperature_ini, k_constant))
                cout_optimal = 0
                for _ in range(moyenne_sur):
                    ordo = genOrdo(25)
                    ordo_optimal = Recuit(ordo, n_iter, fact_refroid, temperature_ini, k_constant)
                    cout_optimal += cout(ordo_optimal)

                cout_optimal /= moyenne_sur

                # Ajoutez les résultats à la liste
                results.append(cout_optimal)
                param_values.append((n_iter, fact_refroid, temperature_ini, k_constant))

### Affichez les meilleurs paramètres
best_params_index = results.index(min(results))
best_params = param_values[best_params_index]
print("Meilleurs paramètres :", best_params)
print("Meilleur coût :", results[best_params_index])

# Tracer les courbes du coût optimal en fonction du paramètre en cours d'optimisation
param_label = "température_ini"  # Remplacez par le paramètre que vous optimisez
param_values_to_plot = [params[2] for params in param_values]  # Sélectionnez la colonne correspondant au paramètre
plt.plot(param_values_to_plot, results, marker='o')
plt.xlabel(param_label)
plt.ylabel("Coût optimal")
plt.title("Optimisation du paramètre {}.".format(param_label))
plt.show()

###Test des meilleurs paramètres
n_moyenne = 100
liste_ordo = [genOrdo(25) for _ in range(n_moyenne)]
cout_base = list(map(cout,liste_ordo))
cout_finaux = list(map(cout,list(map(Recuit,liste_ordo))))
res=(np.array(cout_base)-np.array(cout_finaux))
Gain= 0
Perte= 0
Sans_impact =0
Moyenne = 0
for i in range(len(res)):
    Moyenne+=res[i]
    if res[i]>0:
        Gain+=1
    elif res[i]==0:
        Sans_impact+=1
    else:
        Perte+=1
print("Gain : ",Gain)
print("Perte : ", Perte)
print("Aucune amélioration : ", Sans_impact)
print("Plus value moyenne :", Moyenne/n_moyenne)
###Test sur des ordos déjà optimisé.
cout_base = cout_finaux
cout_finaux = list(map(cout,list(map(Recuit,liste_ordo))))
res=(np.array(cout_base)-np.array(cout_finaux))
Gain= 0
Perte= 0
Sans_impact =0
Moyenne = 0
for i in range(len(res)):
    Moyenne+=res[i]
    if res[i]>0:
        Gain+=1
    elif res[i]==0:
        Sans_impact+=1
    else:
        Perte+=1
print("Gain : ",Gain)
print("Perte : ", Perte)
print("Aucune amélioration : ", Sans_impact)
print("Plus value moyenne :", Moyenne/n_moyenne)