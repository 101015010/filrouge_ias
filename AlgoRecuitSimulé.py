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
    min_ener = energie
    Meilleur_solution=ordo
    for j in range(n_iter):
        L_n_ordo = [solution_voisine(ordo) for k in range(n_voisins)]
        L_energie_voisine = list(map(cout, L_n_ordo))
        i =mini(L_energie_voisine)
        n_ordo = L_n_ordo[i]
        energie_voisine = L_energie_voisine[i]
        delta_e = (energie_voisine - energie)
        facteur = -delta_e/(k_constant*temperature)
        if energie_voisine < min_ener:
            min_ener=energie_voisine
            Meilleur_solution =n_ordo
        if facteur > 0:
            probability =1
        elif facteur < -10 :
            probability = 0
        else :
            probability = np.exp(facteur)
        if random.random() < probability:
            ordo = n_ordo
            energie = energie_voisine

    if energie > min_ener:
        return Meilleur_solution
    else:
        return ordo