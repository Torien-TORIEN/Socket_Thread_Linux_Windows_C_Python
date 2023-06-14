#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    //declaration
    int agence=2;

    // définir l'hôte et le port du serveur
    char* SERVER_HOST = "192.168.205.155";//'192.168.137.1'
    int SERVER_PORT = 5000;

    // créer une connexion au serveur
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);//création de socket en utilisant IPv4 , TCP et  et 
                                        //spécifie également que la couche de transport doit être choisie automatiquement (0)
                                        
    //déclare une variable de type struct sockaddr_in qui est utilisée pour stocker l'adresse du serveur.
    struct sockaddr_in server_address;
    
    /*initialise la famille d'adresse IP (sin_family) de la variable server_address à AF_INET, 
    *qui spécifie que le protocole IPv4 sera utilisé.
    */
    server_address.sin_family = AF_INET;
    
    /*définit le port (sin_port) de la variable server_address en utilisant la macro htons 
    *pour convertir le port du format hôte (byte order) au format réseau (network order).
    */
    server_address.sin_port = htons(SERVER_PORT);
    
    /*utilise la fonction inet_pton pour convertir l'adresse IP du serveur à partir de sa représentation en chaîne de caractères (SERVER_HOST) 
    *en une représentation binaire (sin_addr), qui est stockée dans la variable server_address.
    */
    inet_pton(AF_INET, SERVER_HOST, &server_address.sin_addr);

    if (connect(client_socket, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
        perror("Erreur lors de la connexion au serveur");
        return EXIT_FAILURE;
    }

    int done = 0;
    while (!done) {
        printf(" ------------------------------------------------------------------------------\n");
        printf("|                            | AGENCE %d |                                      |\n",agence);
        printf("|                             ----------                                       |\n");
        printf("|  [1] :DEMANDE DE RESEVATION               [2] :ANNULATION DE RESERVATION     |\n");
        printf("|  [3] :DEMANDE LA FACTURE                  [0] :SE DECONNECTER                |\n");
	  printf("|  [4] :LES VOLS DISPONIBLES                [5] :MES RESERVATIONS              |\n");
        printf(" ------------------------------------------------------------------------------\n");

        int num_req;
        printf("Numero de la requette [0-5] : ");
        scanf("%d", &num_req);
        char req[1024];

        // Se deconnecter et demander la facture
        if (num_req == 0) {
            done = 1;
            sprintf(req, "%d facture", agence);
            send(client_socket, req, strlen(req), 0);
            
        //Demander une resevation
        } else if (num_req == 1) {
            int ref, nb_places;
            printf("Donner la reference  du vol           :");
            scanf("%d", &ref);
            printf("Donner le nombre de places à reserver :");
            scanf("%d", &nb_places);
            sprintf(req, "%d demande %d %d", agence, ref, nb_places);
            send(client_socket, req, strlen(req), 0);
            
        //Annuler une reservation
        } else if (num_req == 2) {
            int ref, nb_places;
            printf("Donner la reference  du vol              :");
            scanf("%d", &ref);
            printf("Donner le nombre de places à annuler :");
            scanf("%d", &nb_places);
            sprintf(req, "%d annulation %d %d", agence, ref, nb_places);
            send(client_socket, req, strlen(req), 0);
        
        //Demander la facture
        } else if (num_req == 3) {
            sprintf(req, "%d facture", agence);
            send(client_socket, req, strlen(req), 0);
            
        //Demander les vols disponibles
        } else if(num_req == 4){
            sprintf(req, "%d vols", agence);
		send(client_socket, req, strlen(req), 0);
	  
	  //Demander mes reservations
	  } else if(num_req == 5){
		sprintf(req, "%d reservations", agence);
		send(client_socket, req, strlen(req), 0);
        }else {
            continue;
        }

        // attendre la réponse du serveur
        char response[1024];
        
        /*utilise la fonction "recv" pour recevoir des données sur le socket "client_socket
        *Les données reçues sont stockées dans le tableau "response" qui a une taille maximale de 1024 octets
        * L'argument "0" signifie que la fonction "recv" est bloquante
        *La fonction "recv" renvoie le nombre d'octets reçus, qui est stocké dans la variable "bytes_received".
        */
        int bytes_received = recv(client_socket, response, 1024, 0); //attend la reponse
        if (bytes_received < 0) {
            perror("Erreur lors de la reception de la réponse");
            return EXIT_FAILURE;
        }
        response[bytes_received] = '\0';

         printf("\n################################################################################\n");
    	 printf("# RESULTAT OBTENU :\n# ----------------\n# %s\n", response);
         printf("#\n################################################################################\n");
    }
    return 0;
}
