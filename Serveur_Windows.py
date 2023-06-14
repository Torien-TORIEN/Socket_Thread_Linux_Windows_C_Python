#####################################################################################
#                                   IMPORTATIONS                                    #
#####################################################################################
import socket
import threading
import time
HOST="192.168.205.155"
PORT=5000

#####################################################################################
#                                   DECLARATIONS                                    # 
#####################################################################################

f_vol="Vols.txt"
f_histo="histo.txt"
f_facture="facture.txt"

"---------------------------- LES MUTEX ------------------------------------"
mutex_vol=threading.Lock()
mutex_histo=threading.Lock()
mutex_fac=threading.Lock()

#####################################################################################
#                                    OPERATIONS                                     #
#####################################################################################
"---------------------------------------------------------------------------"
def ajouter_vol(ref,destination,nb_place,prix):
    mutex_vol.acquire() # acquisition du mutex vol
    f=open(f_vol,"a")
    line="\n"+str(ref)+" "+destination+" "+str(nb_place)+" "+str(prix)
    f.writelines(line)
    f.close()
    mutex_vol.release() # libération du mutex
    
def ajouter_historique(ref,agence,transaction,valeur,resultat):
    mutex_fac.acquire() # acquisition du mutex fac
    f=open(f_histo,"a")
    line="\n"+str(ref)+" "+str(agence)+" "+transaction+" "+str(valeur)+" "+resultat
    f.writelines(line)
    f.close()
    mutex_fac.release() # libération du mutex

def ajouter_ou_modifier_facture(ref,somme):
    mutex_fac.acquire() # acquisition du mutex fac
    f=open(f_facture,"r")
    factures=f.readlines()
    factures.sort()
    f.close()
    f=open(f_facture,"w")
    found=False
    for line in factures:
        fac=line.split()
        #print(fac)
        if fac[0]==str(ref):
            found=True
            f.writelines(str(ref)+" "+str(somme)+"\n")
        else:
            f.writelines(fac[0]+" "+fac[1]+"\n")
    if(not found):
        f.writelines(str(ref)+" "+str(somme))
    f.close()
    mutex_fac.release() # libération du mutex

def prix_par_place(ref_vol):
    mutex_vol.acquire() # acquisition du mutex vol
    f=open(f_vol,"r")
    line=f.readline()
    while(line!=""):
        liste=line.split()
        if liste[0]==str(ref_vol):
            f.close()
            mutex_vol.release() # libération du mutex
            return int(liste[3])
        line=f.readline()
    f.close()
    mutex_vol.release() # libération du mutex
    return -1


def get_nbplaces(ref_vol):
    mutex_vol.acquire() # acquisition du mutex vol
    f=open(f_vol,"r")
    vols=f.readlines()
    f.close()
    mutex_vol.release() # libération du mutex
    for vol in vols:
        L_vol=vol.split()
        if L_vol[0]==str(ref_vol):
            return int(L_vol[2])
    return -1

def get_nbplaces_reserved(agence,ref_vol):
    mutex_histo.acquire() # acquisition du mutex histo
    f=open(f_histo,"r")
    histos=f.readlines()
    f.close()
    mutex_histo.release() # libération du mutex
    nb_reserver=0
    for histo in histos:
        L_histo=histo.split()
        if(len(L_histo)==5 and L_histo[0]==str(ref_vol) and L_histo[1]==str(agence)and L_histo[4]=="succès"):
            if L_histo[2]=="Demande":
                nb_reserver+=int(L_histo[3])
            elif L_histo[2]=="Annulation":
                nb_reserver-=int(L_histo[3])
    return nb_reserver

def modifier_nbplace(ref_vol,nb_place):
    mutex_vol.acquire() # acquisition du mutex vol
    f=open(f_vol,"r")
    vols=f.readlines()
    vols.sort()
    f.close()
    g=open(f_vol,"w")
    for vol in vols:
        L_vol=vol.split()
        if(L_vol[0]==str(ref_vol)):
            g.writelines(L_vol[0]+" "+L_vol[1]+" "+str(nb_place)+" "+L_vol[3]+"\n")
            print(f"modification de nombre de place de {L_vol[0]} à {nb_place}")
        else:
            g.writelines(L_vol[0]+" "+L_vol[1]+" "+L_vol[2]+" "+L_vol[3]+"\n")
    g.close()
    mutex_vol.release() # libération du mutex


def get_all_vols():
    mutex_vol.acquire() # acquisition du mutex vol
    with open(f_vol, "r", encoding="utf-8") as f: #ouvre le fichier et le ferme automatiquement à la fin du traitement
        lines = f.readlines()
        #vols = "".join(lines) #joindre les lignes de texte lues en une seule chaîne de caractères
        #vols="#\t\t ID_Vol\tDestination\tPlace_disp\tPrix/pers\n#"
        vols="#\t\t {:<15} {:<15} {:<15} {:<15}\n#".format("ID_Vol", "Destination", "Place_Dispo", "Prix/place")
        for line in lines :
            vol=line.split()
            #vols+="\t\t "+vol[0]+"\t"+vol[1]+"\t"+vol[2]+"\t"+vol[3]+"\n#"
            vols+="#\t\t {:<15} {:<15} {:<15} {:<15}\n#".format(vol[0],vol[1],vol[2],vol[3])
    mutex_vol.release() # libération du mutex vol
    return vols

def get_reservations(ref_ag):
    mutex_histo.acquire() # acquisition du mutex histo
    f=open(f_histo,"r")
    lines=f.readlines()   #toutes les lignes dans une liste lines
    f.close()
    mutex_histo.release() # libération du mutex
    
    resultat_trouvé=False #False si aucune transaction avec succès de l'agence ref_ag est trouvée
    Id_vols_trouvés={} #dictionnaire de vols: { id_vol:[ nb_place_reservé , nb_place_annulé] , ...}
    for line in lines:
        histo=line.split() #transformer une ligne en liste 
        if(len(histo)==5 and histo[1]==str(ref_ag) and histo[4]=="succès"):
            resultat_trouvé=True
            Id_vols_trouvés.setdefault(histo[0], [0,0]) #setdefault() permet d'initialiser une clé avec une valeur par défaut si elle n'existe pas déjà dans le dictionnaire
            if histo[2]=="Demande" :
                Id_vols_trouvés[histo[0]] = [ Id_vols_trouvés[histo[0]][0]+int(histo[3]),Id_vols_trouvés[histo[0]][1] ] #nb_place_reservé+=histo[3]
            elif histo[2]=="Annulation" :
                Id_vols_trouvés[histo[0]] = [ Id_vols_trouvés[histo[0]][0],Id_vols_trouvés[histo[0]][1]+int(histo[3]) ] #nb_place_annulé+=histo[3]
    if(resultat_trouvé):
        vols=dict(sorted(Id_vols_trouvés.items())) #Trier le resultat par Id_vol
        ch="#\t\t {:<15} {:<15} {:<15} {:<15}\n#".format("ID_Vol", "Places-Res", "Places-Annul", "Total-Res")
        total=0 #total de places reservées
        for id_vol,place in vols.items():
            ch+="\t\t {:<15} {:<15} {:<15} {:<15}\n#".format(id_vol,place[0],place[1],place[0]-place[1])
            total+=place[0]-place[1]
        ch+="\n#"
        ch+="\t\t {:<15}={:<15}={:<15}:{:<15}\n#".format("TOTAL==========", "===============", "===============", total)
                                                         
        return ch
    else:
        return "# Vous n'avez effectué aucune reservation !!! "


"---------------------------------------------------------------------------"


"---------------------------------------------------------------------------"


"---------------------------------------------------------------------------"
def consulter_liste_vol(ref_vol):
    mutex_vol.acquire() # acquisition du mutex vol
    vol=open(f_vol,"r")
    line=vol.readline()
    while(line!=""):
        Liste=line.split();
        if(Liste[0]==str(ref_vol)):
            vol.close()
            mutex_vol.release() # libération du mutex vol
            return Liste
        line=vol.readline();
    vol.close()
    mutex_vol.release() # libération du mutex vol
    return 0
    
    
def calculer_facture(ref_ag):
    mutex_histo.acquire() # acquisition du mutex histo
    f=open(f_histo,"r")
    line=f.readline()
    total=0
    while(line!=""):
        liste=line.split()
        if(len(liste)==5 and liste[1]==str(ref_ag)):
            if(liste[4]=="succès"):
                nb_places=int(liste[3])
                if(liste[2]=="Demande"):
                    total+=nb_places*prix_par_place(liste[0])
                elif(liste[2]=="Annulation"):
                    prix=nb_places*prix_par_place(liste[0])
                    total+=-prix+0.1*prix
        line=f.readline()
    f.close()
    mutex_histo.release() # libération du mutex histo
    ajouter_ou_modifier_facture(ref_ag,total) # Enregistrer
    return total
           
    
def consulter_historique():
    mutex_histo.acquire() # acquisition du mutex histo
    histo=open(f_histo,"r")
    line=histo.readline()
    while(line!=""):
        print(line)
        line=histo.readline()
    histo.close()
    mutex_histo.release() # libération du mutex histo
"---------------------------------------------------------------------------"


#####################################################################################
#                                    CONNEXION                                      #
#####################################################################################

# définir la fonction pour gérer les connexions clientes
def handle_client_connection(conn, addr):
    print(f'Nouvelle connexion cliente: {addr}')

    while True:
        data = conn.recv(1024)
        if not data:
            print(f'L\'agence {addr} s\' est deconnectée ')
            break
        ###########################################################
        #          traiter les requêtes des clients ici           #
        ###########################################################
        request = data.decode()
        req=request.split() #transformer en liste en separant par un espace
        print("AGENCE :"+req[0])


        
        "---------------------------------------------------------"
        "                   DEMANDE DE RESERVATION                "
        "---------------------------------------------------------"
        if(req[1]=='demande' and len(req)==4):
            print("\tDemande de reservation par l'agence ",req[0]," - ref vol :",req[2]," nombre de places =",req[3])
            transaction="Demande"
            agence=int(req[0])
            ref_vol = int(req[2])
            nb_places_à_reserver = int(req[3])
            nb_places_dispo = get_nbplaces(ref_vol)
            resultat="succès"
            response=""
            if(nb_places_dispo==-1):#pas de vol avec ref donné
                response="Aucun vol avec une réference  "+str(ref_vol)+" !!!"
            else:
                if(nb_places_à_reserver > nb_places_dispo) :
                    resultat="impossible"
                    response="Votre demande reservation de "+str(nb_places_à_reserver)+" place(s) est impossible:\n\t"+str(nb_places_dispo)+" place(s) disponible(s) pour ce vol : ref =" + str(ref_vol)
                else :
                    #modifier la place disponible
                    modifier_nbplace(ref_vol,nb_places_dispo - nb_places_à_reserver)
                    response="Votre reservation de "+str(nb_places_à_reserver)+" place(s) est enregistrée !"
                    
                #ajouter une historique
                ajouter_historique(ref_vol,agence,transaction,nb_places_à_reserver,resultat)
            


            
            "---------------------------------------------------------"
            "               ANNULATION DE RESERVATION                 "
            "---------------------------------------------------------"
        elif(req[1]=='annulation' and len(req)==4):
            print("\tAnnulation de reservation par l'agence ",req[0]," - ref vol :",req[2]," nombre de places =",req[3])
            transaction="Annulation"
            agence=int(req[0])
            ref_vol = int(req[2])
            nb_places_à_annuler = int(req[3])
            nb_places_reservé = get_nbplaces_reserved(agence,ref_vol)
            nb_places_dispo = get_nbplaces(ref_vol)
            resultat="succès"
            response=""
            if(nb_places_dispo==-1):#pas de vol avec ref donné
                response="Aucun vol avec une réference  "+str(ref_vol)+" !!!"
            else:
                if(nb_places_reservé < nb_places_à_annuler) :
                    resultat="impossible"
                    response="Votre annulation de reservation de "+str(nb_places_à_annuler)+" place(s) pour le vol "+str(ref_vol)+" est impossible:"
                    response+="\n#\tVous avez "+str(nb_places_reservé)+" place(s) réservée(s) pour ce vol actuellement"
                else :
                    #modifier la place disponible
                    modifier_nbplace(ref_vol,nb_places_dispo+nb_places_à_annuler)
                    response="Votre annulation de reservation de "+str(nb_places_à_annuler)+" place(s) pour le vol :"+str(ref_vol)+" est effectuée !"
                    
                #ajouter une historique
                ajouter_historique(ref_vol,agence,transaction,nb_places_à_annuler,resultat)

        
            "---------------------------------------------------------"
            "                   DEMANDE DE FACTURE                    "
            "---------------------------------------------------------"    
        elif(req[1]=='facture'):
            print(f"\tEnvoi de la facture à l'agence {req[0]} ")
            agence=int(req[0])
            somme_à_payer=calculer_facture(agence)
            
            response="\t\t\t  FACTURE DE L'AGENCE "+str(agence)+" :"
            response+="\n# \t\t\t _______________________________"
            response+="\n# \t\t\t| Numéro de l'agence : "+str(agence)+"  "
            response+="\n# \t\t\t| Motant à payer  : "+str(somme_à_payer)+" DT"
            response+="\n# \t\t\t|_______________________________"

        

            "---------------------------------------------------------"
            "           DEMANDE DE LISTE DE VOLS                      "
            "---------------------------------------------------------"
        elif(req[1]=='vols'):
            agence=int(req[0])
            print(f"\tEnvoi des vols disponibles à l'agence {agence}")
            response="\t\t\t\tLES VOLS DISPONIBLES\n#"
            response+="\t\t\t\t--------------------\n"
            response+=get_all_vols()

            

            "---------------------------------------------------------"
            "           DEMANDE DES RESERVATIONS FAITES               "
            "---------------------------------------------------------"
        elif req[1]=="reservations":
            agence=int(req[0])
            print(f"\tEnvoi de son bilan de reservation à l'agence {req[0]}")
            response="\t\t\t\tBILAN DE VOTRE RESERVATION \n#"
            response+="\t\t\t\t--------------------------\n"
            response+=get_reservations(agence)

            
        else:
            response = 'Requette non reconnue'
            
            "---------------------------------------------------------------------------"
        
        conn.sendall(response.encode())

    conn.close()
"---------------------------------------------------------------------------"
#####################################################################################
#                            DEMARRER LE SERVEUR                                    #
#####################################################################################
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f'SERVEUR EST DEMARRE SUR {HOST}:{PORT}')

    # gérer les connexions clientes en boucle infinie
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        thread.start()


"---------------------------------------------------------------------------"
