import sys
from socket import *
import pickle
import random


serverPort = int(sys.argv[1])
player_list = []
game_list = []
game_identifier = 0
dealer_index = 0
contains_player = False
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print("Message from player: " + message.decode())
    modifiedMessage = message.decode()

    if "Register" in modifiedMessage:
        #Splits string into a list using " " as a delimiter
        player_info = modifiedMessage.split(" ")
        player_info.remove(player_info[0])

        #Searches current registered players to make sure no duplicates are registered
        for i in player_list:
            if player_info[0] in i:
                contains_player = True

        #Sends Succeed or Failure and adds player to list if they are not a duplicate
        if contains_player:
            serverSocket.sendto("Failure".encode(), clientAddress)
            print("Response Message Sent")
        else:
            player_list.insert(0, player_info)
            serverSocket.sendto("Succeed".encode(), clientAddress)
            print("Response Message Sent")

        contains_player = False

    elif "Query_Games" in modifiedMessage:
        games = pickle.dumps(game_list) #converts game_list into bytes

        response = "The number of games ongoing is " + str(len(game_list))

        serverSocket.sendto(response.encode(), clientAddress) #Sends # of ongoing games
        serverSocket.sendto(games, clientAddress) #Sends ongoing game information in list form
        print("Response Message Sent")

    elif "Query_Players" in modifiedMessage:
        response = "The number of registered players are " + str(
            len(player_list)) + ". Following are the player information:"

        #Creates a string of player data from the current list of players
        for i in player_list:
            response = response + " \n" + '(' + ', '.join(i) + ')'

        print(response)
        serverSocket.sendto(response.encode(), clientAddress) #Sends player information
        print("Response Message Sent")

    elif "Start_Game" in modifiedMessage:
        start_info = modifiedMessage.split(" ")
        start_info.remove(start_info[0])

        for index, i in enumerate(player_list):
            if start_info[0] in i:
                dealer_index = index
                contains_player = True

        if int(start_info[1]) > 4 or int(start_info[1]) < 1:
            serverSocket.sendto("Failure".encode(), clientAddress)
            print("Response Message Sent")

        if contains_player and int(start_info[1]) <= len(player_list) - 1:
            temp_list = player_list
            new_game = []
            new_game.insert(0, temp_list[dealer_index])
            temp_list.remove(temp_list[dealer_index])

            for i in range(int(start_info[1])):
                new_game.append(random.choice(temp_list))
                temp_list.remove(new_game[(len(new_game)-1)])

            #new_game.reverse()
            game_info = pickle.dumps(new_game)

            serverSocket.sendto("Succeed".encode(), clientAddress)
            print("Response Message Sent")
            serverSocket.sendto(str(game_identifier).encode(), clientAddress)
            serverSocket.sendto(game_info, clientAddress)
            print("New Game Info Sent")
            game_list.insert(0, new_game)
        else:
            serverSocket.sendto("Failure".encode(), clientAddress)
            print("Response Message Sent")

        contains_player = False

    elif "De-register" in modifiedMessage:
        in_game = False
        player_removed = False
        remove_player = modifiedMessage.split(" ")
        remove_player.remove(remove_player[0])

        #Checks if player is involved in a game currently
        for i in game_list:
            if remove_player[0] in i[0]:
                in_game = True

        #Searches for player in list and removes them if found if they are not in any games currently
        if not in_game:
            for i in player_list:
                if remove_player[0] in i:
                    player_list.remove(i)
                    serverSocket.sendto("Succeed".encode(), clientAddress)
                    print("Response Message Sent")
                    player_removed = True

        #Sends failure if player is not removed due to being in a game or not registered
        if not player_removed:
            serverSocket.sendto("Failure".encode(), clientAddress)
            print("Response Message Sent")

    elif "End" in modifiedMessage:
        end_game = modifiedMessage.split(" ")

        # Checks if game is in list and removes it from list and adds players back to player list
        for i in game_list:
            if end_game[1] in i[0]:
                for j in game_list:
                    for x in j:
                        player_list.append(x)
                game_list.remove(i)
                serverSocket.sendto("Succeed".encode(), clientAddress)




