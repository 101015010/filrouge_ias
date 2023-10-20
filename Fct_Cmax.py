###Définition des représentations
import numpy as np
import random as rd
import matplotlib.pyplot as pl
import copy

n_patient = 100
n_SSPI_cap_pre = 3
n_SSPI_cap_post =3
n_salle_op = 4
n_medecin = 5
n_anestesiste = 8
n_brancardier = 2
n_phase = 4
temps_post_ope=20

limite_de_phase=[n_brancardier, [n_SSPI_cap_pre,n_anestesiste], [n_salle_op,n_medecin,n_anestesiste],[n_SSPI_cap_post,n_anestesiste]]
#Le medecin doit être lié au patient
#On ne peut pas brancarder avant qu'il y ai une place en SSPI_cap_pre, pareil pour Sortir de la salle d'opération
#20 minutes apèrs chaque utilisation d'une salle
#Gardez les actes importants
#Tenir compte des plannings des médecins
#Tenir compte des lits et faire le lissage.

def attribution_des_medecins(n_medecin,n_patient):
    liste_affiliation=[]
    for i in range(n_patient):
        liste_affiliation.append(rd.randint(0,n_medecin-1))
    return liste_affiliation

def gen_medecin(medecin):
    return [True]*medecin

def gen_salle(salle_op):
    return [True]*salle_op

l = [[k for k in range(n_patient)]*4] #Utiliser pour transcrire l'entrée de Marceau

def gen_temps_restant(liste_ope):
    res = copy.deepcopy(liste_ope)
    return res

def trouver_salle(liste_salle):
    for i in range(len(liste_salle)):
        if liste_salle[i]==True:
            liste_salle[i]=False
            return i



def peutetreprisencharge(temps_restant,solution,phase,liste_en_cours,liste_medecin,liste_affiliation):
    for i in solution[phase]:
        if temps_restant[i][phase] != 0:
            if i not in liste_en_cours:
                etape_suivante = True
                for etape in range(0,phase):
                    if temps_restant[i][etape]!=0:
                        etape_suivante = False
                if etape_suivante:
                    if phase == 2:
                        if liste_medecin[liste_affiliation[i]]:
                            liste_medecin[liste_affiliation[i]]=False
                            return i
                    else:
                        return i
    return None

def gen_liste_ope(n_patient):
    return [[rd.randint(5,10),rd.randint(10,30),rd.randint(40,120),rd.randint(10,30)] for i in range(n_patient)]


def gen_solution_initiale():
    solution = [list(range(n_patient)) for _ in range(4)]
    for s in solution:
        rd.shuffle(s)
    return solution


def Cmax(solution,liste_ope,SSPI_cap_pre = 3,SSPI_cap_post =3,salle_op = 4,medecin = 4,anestesiste = 8,brancardier = 2,temps_post_ope=20):
    n_SSPI_cap_pre = SSPI_cap_pre
    n_SSPI_cap_post =SSPI_cap_post
    n_salle_op = salle_op
    n_medecin = medecin
    liste_medecin = gen_medecin(medecin)
    liste_salle = gen_salle(salle_op)
    liste_affiliation = attribution_des_medecins(n_medecin,n_patient)
    n_anestesiste = anestesiste
    n_brancardier = brancardier
    temps_restant = gen_temps_restant(liste_ope)
    fin = False
    t = 0
    en_cours_utilisation_salle=[0]*salle_op
    en_cours_brancardage = []
    en_cours_SSPI_pre = []
    en_cours_operation = []
    en_cours_SSPI_post = []
    while fin == False:
        #Prise en charge
        if n_brancardier != 0:
            patient = peutetreprisencharge(temps_restant,solution,0,en_cours_brancardage,liste_medecin,liste_affiliation)
            if patient != None:
                en_cours_brancardage.append(patient)
                n_brancardier -=1

        if (n_SSPI_cap_pre != 0) and (n_anestesiste != 0):
            patient = peutetreprisencharge(temps_restant,solution,1,en_cours_SSPI_pre,liste_medecin,liste_affiliation)
            if patient != None:
                en_cours_SSPI_pre.append(patient)
                n_SSPI_cap_pre -=1
                n_anestesiste -=1

        if (n_medecin != 0) and (n_anestesiste !=0) and (n_salle_op != 0):
            patient = peutetreprisencharge(temps_restant,solution,2,en_cours_operation,liste_medecin,liste_affiliation)
            if patient != None:
                en_cours_operation.append(patient)
                n_medecin -= 1
                n_anestesiste -= 1
                n_salle_op -=1
                en_cours_utilisation_salle[trouver_salle(liste_salle)]+=temps_restant[i][2]+temps_post_ope


        if (n_SSPI_cap_post != 0) and (n_anestesiste != 0):
            patient = peutetreprisencharge(temps_restant,solution,3,en_cours_SSPI_post,liste_medecin,liste_affiliation)
            if patient != None:
                en_cours_SSPI_post.append(patient)
                n_SSPI_cap_post -=1
                n_anestesiste -=1
        #écoulement du temps
        for i in en_cours_brancardage:
            temps_restant[i][0] -= 1
            if temps_restant[i][0] == 0:
                n_brancardier += 1
        en_cours_brancardage = [i for i in en_cours_brancardage if temps_restant[i][0] > 0]

        for i in en_cours_SSPI_pre:
            temps_restant[i][1] -= 1
            if temps_restant[i][1] == 0:
                n_SSPI_cap_pre += 1
                n_anestesiste += 1
        en_cours_SSPI_pre = [i for i in en_cours_SSPI_pre if temps_restant[i][1] > 0]


        for i in en_cours_operation:
            temps_restant[i][2] -= 1
            if temps_restant[i][2] == 0:
                liste_medecin[liste_affiliation[i]]=True
                n_medecin += 1
                n_anestesiste += 1
        en_cours_operation = [i for i in en_cours_operation if temps_restant[i][2] > 0]
        for i in range(salle_op):
            if en_cours_utilisation_salle[i] != 0:
                en_cours_utilisation_salle[i]-=1
                if en_cours_utilisation_salle[i]==0:
                    liste_salle[i]=True
                    n_salle_op+=1




        for i in en_cours_SSPI_post:
            temps_restant[i][3] -= 1
            if temps_restant[i][3] == 0:
                n_SSPI_cap_post += 1
                n_anestesiste += 1
        en_cours_SSPI_post = [i for i in en_cours_SSPI_post if temps_restant[i][3] > 0]

        t+=1
        fin = True
        for i in range(len(temps_restant)):
            if  temps_restant[i][3] != 0:
                fin = False
    return t












