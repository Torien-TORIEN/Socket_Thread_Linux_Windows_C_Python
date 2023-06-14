import socket

#declaration
agence=3

# définir l'hôte et le port du serveur
SERVER_HOST = "192.168.205.155"
SERVER_PORT = 5000

# créer une connexion au serveur
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:#Création d socket en utilisant IPv4 et TCP
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    done = False
    while not done :
        print(" ------------------------------------------------------------------------------")
        print(f"|                            | AGENCE {agence} |                                      |")
        print("|                             ----------                                       |")
        print("|  [1] :DEMANDE DE RESEVATION               [2] :ANNULATION DE RESERVATION     |")
        print("|  [3] :DEMANDE LA FACTURE                  [0] :SE DECONNECTER                |")
        print("|  [4] :LES VOLS DISPONIBLES                [5] :MES RESERVATIONS              |")
        print(" ------------------------------------------------------------------------------")

        
        num_req = int(input("Numero de la requette [0-5] : "))
        
        # Se deconnecter et demander la facture
        if num_req == 0 :
            done = True
            req=str(agence)+' facture'
            client_socket.sendall(req.encode())
            

            #Demander une reservation
        elif num_req ==1:
            ref=int(input("Donner la reference  du vol           :"))
            nb_places=int(input("Donner le nombre de places à reserver :"))
            req=str(agence)+' demande '+str(ref)+' '+str(nb_places)
            client_socket.sendall(req.encode())

            #Annuler une reservation
        elif num_req == 2:
            ref=int(input("Donner la reference  du vol              :"))
            nb_places=int(input("Donner le nombre de places à annuler :"))
            req=str(agence)+' annulation '+str(ref)+' '+str(nb_places)
            client_socket.sendall(req.encode())

            #Demander la facture
        elif num_req == 3:
            req=str(agence)+' facture'
            client_socket.sendall(req.encode())


            #Demander les vols disponibles
        elif num_req == 4 :
            req=str(agence)+' vols'
            client_socket.sendall(req.encode())


            #Demander ses reservations
        elif num_req == 5 :
            req=str(agence)+' reservations'
            client_socket.sendall(req.encode())
            
        else:
            continue
        
        # attendre la réponse du serveur
        response = client_socket.recv(1024) # attend de recevoir des données jusqu'à un maximum de 1024 octets à la fois
        ligne = response.decode()
        print("\n################################################################################")
        print(f'# RESULTAT OBTENU :\n# ----------------\n# {ligne}')
        print("#\n################################################################################\n")
