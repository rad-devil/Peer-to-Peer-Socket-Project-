import socket
import sys
from socket import *
import pickle
import selectors
import select
import random

n = len(sys.argv)
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
name = ""
game_identifier = 0
game_info = []
m_port = ""
r_port = ""
p_port = ""
player_index = 0
neighbor = []
deck = ["A", "A", "A", "A", "2", "2", "2", "2", "3", "3", "3", "3", "4", "4", "4", "4", "5", "5", "5", "5", "6", "6"
    , "6", "6", "7", "7", "7", "7", "8", "8", "8", "8", "9", "9", "9", "9", "10", "10", "10", "10",
        "J", "J", "J", "J", "Q", "Q", "Q", "Q", "K", "K", "K", "K"]
shuffled_deck = []
hand = []
rankings = [0]
books = 0
player_books = []
books_won = 0
game_in_progress = True

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket_M = socket(AF_INET, SOCK_DGRAM)
clientSocket_R = socket(AF_INET, SOCK_DGRAM)
clientSocket_P = socket(AF_INET, SOCK_DGRAM)
inputs = [clientSocket_P, clientSocket_M, clientSocket_R]
outputs = [clientSocket_P, clientSocket_M, clientSocket_R]
clientSocket_M.setblocking(False)
clientSocket_R.setblocking(False)
clientSocket_P.setblocking(False)

while True:
    print("Choose an number:\n1. Register new player\n2.Query Games\n3.Query Player\n4.Start "
          "Game\n5.De-register\n6.Search for game\n7.Exit\n")
    choice = int(input())
    message = ''
    if choice == 1:
        print("Enter player name: ")
        name = input()
        print("Enter IPv4 Address: ")
        IPv4 = input()
        print("Enter m-port: ")
        m_port = input()
        clientSocket_M.bind(('', int(m_port)))
        print("Enter r-port: ")
        r_port = input()
        clientSocket_R.bind(('', int(r_port)))
        print("Enter p-port: ")
        p_port = input()
        clientSocket_P.bind(('', int(p_port)))
        message = "Register " + name + " " + IPv4 + " " + m_port + " " + r_port + " " + p_port
        clientSocket.sendto(message.encode(), (serverName, serverPort))  # Sends Register message
        print("Register message sent")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Recieves Response from manager
        print("Message Received: " + modifiedMessage.decode())
    if choice == 2:
        message = "Query_Games"
        clientSocket.sendto(message.encode(), (serverName, serverPort))  # Sends Query Games message
        print("Query Games message sent")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Recieves Response from manager
        print("Message Received: " + modifiedMessage.decode())
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Recieves Response from manager
        games = pickle.loads(modifiedMessage)  # Converts bytes back to a list object
        print("Games: " + str(games))
    if choice == 3:
        message = "Query_Players"
        clientSocket.sendto(message.encode(), (serverName, serverPort))  # Sends Query Players message
        print("Query Players message sent")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Recieves Response from manager
        print("Message Received: " + modifiedMessage.decode())
    if choice == 4:
        new_game = True
        print("How many additional players?(Choose 1-4)")
        add_players = input()
        message = "Start_Game " + name + " " + add_players
        clientSocket.sendto(message.encode(), (serverName, serverPort))  # Sends Start Game message
        print("Start Game message sent")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Receives Response from manager
        print("Message Received: " + modifiedMessage.decode())

        # Starts game
        if "Succeed" in modifiedMessage.decode():
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Receives Response from manager
            print("Game identifier: " + modifiedMessage.decode())
            game_identifier = int(modifiedMessage.decode())
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Receives Response from manager
            game_info = pickle.loads(modifiedMessage)
            print("Game Player Info: " + str(game_info))

            send_game = pickle.dumps(game_info)
            clientSocket_R.sendto("Set-up".encode(), (game_info[1][1], int(game_info[1][3])))
            clientSocket_R.sendto(send_game, (game_info[1][1], int(game_info[1][3])))

            # deals cards to each player depending on number of players in game using select function to listen asyncronously
            while new_game:
                readable, writeable, exceptional = select.select(inputs, outputs, inputs, 0.5)

                for s in writeable:
                    pass
                for s in readable:
                    s.setblocking(True)  # Sets socket to block since communication has started
                    s.recv(2048)
                    data = s.recv(2048)
                    game_info = pickle.loads(data)  # Retrieves list using pickle
                    print(str(game_info))
                    neighbor = game_info[1]

                    # shuffles deck
                    for i in range(52):
                        shuffled_deck.append(random.choice(deck))
                        deck.remove(shuffled_deck[(len(shuffled_deck) - 1)])

                    # decides to deal 5 or 7 cards depending on # of players
                    if int(add_players) >= 2:
                        for i in range(7):
                            for j in range(int(add_players) + 1):
                                if j == 0:
                                    hand.append(shuffled_deck.pop())
                                else:
                                    s.sendto("Deal".encode(), (game_info[j][1], int(game_info[j][3])))
                                    s.sendto(shuffled_deck.pop().encode(), (game_info[j][1], int(game_info[j][3])))
                    else:
                        for i in range(5):
                            for j in range(int(add_players) + 1):
                                if j == 0:
                                    hand.append(shuffled_deck.pop())
                                else:
                                    s.sendto("Deal".encode(), (game_info[j][1], int(game_info[j][3])))
                                    s.sendto(shuffled_deck.pop().encode(), (game_info[j][1], int(game_info[j][3])))

                    print("Cards have been dealt")
                    s.sendto("Your-Move".encode(), (game_info[1][1], int(
                        game_info[1][3])))  # Starts game by sending first your move message to player 1
                    send_deck = pickle.dumps(shuffled_deck)
                    s.sendto(send_deck, (game_info[1][1], int(game_info[1][3])))  # Sends updated deck to player
                    new_game = False  # exit condition
                    s.setblocking(False)
                for s in exceptional:
                    pass

            # Dealers game loop
            while game_in_progress:
                readable, writeable, exceptional = select.select(inputs, outputs, inputs, 1)  # creates list of available sockets for reading, writing, or errors

                for s in writeable:
                    pass
                for s in readable:
                    data = s.recv(2048)  # Message that determines which event will occur

                    # Sets up logical ring of players
                    if data.decode() == "Set-up":
                        s.setblocking(True)
                        data = s.recv(2048)
                        game_info = pickle.loads(data)

                        # Determines index of player
                        for index, i in enumerate(game_info):
                            if name in i:
                                player_index = index

                        neighbor = game_info[(player_index + 1) % (len(game_info))]  # sets players neighbor
                        print("Logical ring link connected")
                        s.sendto(data, (neighbor[1], int(neighbor[3])))
                        s.setblocking(False)

                    # Players turn executed
                    elif data.decode() == "Your-Move":
                        s.setblocking(True)
                        print("My Turn....")
                        data = s.recv(2048)  # Receives updated deck for drawing
                        shuffled_deck = pickle.loads(data)  # Stores updated deck
                        go_fish = True

                        # Loop for taking a player turn(runs until a player receives no cards from an ask)
                        while go_fish:

                            # Hand empty check for drawing cards(if deck is empty then player will pass turn with empty hand)
                            if len(hand) == 0 and len(shuffled_deck) != 0:
                                hand.append(shuffled_deck.pop())
                            elif len(hand) == 0 and len(shuffled_deck) == 0:
                                go_fish = False
                                s.sendto("Your-Move".encode(), (neighbor[1], int(neighbor[3])))
                                send_deck = pickle.dumps(shuffled_deck)
                                s.sendto(send_deck, (neighbor[1], int(neighbor[3])))
                                break

                            choose_player = random.choice(game_info)  # Random choice of player to ask for cards

                            # Check to see if player chosen is self
                            while name in choose_player:
                                choose_player = random.choice(game_info)

                            s.sendto("Ask".encode(),
                                     (choose_player[1], int(choose_player[4])))  # Intiate ask communication
                            s.sendto(str(player_index).encode(),
                                     (choose_player[1], int(choose_player[4])))  # Sends return player info
                            choose_card = random.choice(hand)  # Choose card to ask for at random
                            s.sendto(choose_card.encode(), (choose_player[1], int(choose_player[4])))  # Ask for card
                            print("Asking " + choose_player[0] + " " + "for " + choose_card)

                            data = s.recv(2048)  # Receive how many asked player has of choosen card
                            count = int(data.decode())
                            print("Player had " + str(count))

                            # Add cards to hand from other player or draw and pass turn
                            if count > 0:
                                for i in range(count):
                                    hand.append(choose_card)
                                check_book = hand.count(choose_card)

                                # Check if a book has been completed
                                if check_book == 4:
                                    for j in range(4):
                                        hand.remove(choose_card)
                                    books += 1  # update number of completed books for player
                                    rankings[0] = books  # update rankings list
                                    books_won += 1  # update total books won in game

                                    # Check if game is over
                                    if books_won == 13:
                                        player_books.append(choose_card)
                                        print("Player has following books:")
                                        for i in range(len(player_books)):
                                            print(player_books[i] + "C " + player_books[i] + "D " + player_books[
                                                i] + "H " +
                                                  player_books[i] + "S")
                                        s.sendto("Winner".encode(), (neighbor[1], int(neighbor[3])))
                                        go_fish = False

                                    player_books.append(choose_card)
                                    print("Player has following books:")
                                    for i in range(len(player_books)):
                                        print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                              player_books[i] + "S")
                                # loop exit
                                if not go_fish:
                                    break
                            else:
                                # Draw card
                                if len(shuffled_deck) != 0:
                                    hand.append(shuffled_deck.pop())

                                check_book = hand.count(hand[(len(hand) - 1)])
                                card = hand[(len(hand) - 1)]

                                # Check if book has been made
                                if check_book == 4:
                                    for j in range(4):
                                        hand.remove(card)
                                    books += 1  # update number of completed books for player
                                    rankings[0] = books  # update rankings list
                                    books_won += 1  # update total books won in game

                                    # Check if game is over
                                    if books_won == 13:
                                        player_books.append(choose_card)
                                        print("Player has following books:")
                                        for i in range(len(player_books)):
                                            print(player_books[i] + "C " + player_books[i] + "D " + player_books[
                                                i] + "H " +
                                                  player_books[i] + "S")
                                        s.sendto("Winner".encode(), (neighbor[1], int(neighbor[3])))
                                        go_fish = False
                                        break

                                    player_books.append(choose_card)
                                    print("Player has following books:")
                                    for i in range(len(player_books)):
                                        print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                              player_books[i] + "S")

                                go_fish = False

                                s.sendto("Your-Move".encode(), (neighbor[1], int(neighbor[3])))  # Pass Turn
                                send_deck = pickle.dumps(shuffled_deck)
                                s.sendto(send_deck, (neighbor[1], int(neighbor[3])))

                        s.setblocking(False)

                    # Player ask command
                    elif data.decode() == "Ask":
                        s.setblocking(True)
                        data = s.recv(2048)  # Return Player info
                        return_player = int(data.decode())

                        data = s.recv(2048)  # Card being asked for
                        print("Player is asking for " + data.decode())

                        # Check if hand is empty. If not count how many of the card the player has
                        if len(hand) != 0:
                            count = hand.count(data.decode())
                            print("I have " + str(count) + " of " + data.decode())
                        else:
                            count = 0

                        # Remove Cards from hand
                        for i in range(count):
                            hand.remove(data.decode())

                        s.sendto(str(count).encode(), (game_info[return_player][1], int(game_info[return_player][3]))) # Let player who asked know how many cards they had

                        s.setblocking(False)

                    # Dealers Winner message determines winner of game and ends game with manager
                    elif data.decode() == "Winner":
                        s.setblocking(True)

                        data = s.recv(2048) # Player book count
                        rankings.append(int(data.decode()))
                        winner = 0
                        highest_book = 0

                        # Determines winner by highest book amount and saves an index to locate in game_info list
                        if len(rankings) == (int(add_players) + 1):
                            for i in range(len(rankings)):
                                if rankings[i] > highest_book:
                                    highest_book = rankings[i]
                                    winner = i
                            print("The winner of the game is " + game_info[winner][0])

                            # Sends End message to manager
                            message = ("End " + name + " " + str(game_identifier))
                            clientSocket.sendto(message.encode(), (serverName, serverPort))
                            modifiedMessage, serverAddress = clientSocket.recvfrom(
                                2048)  # Receives Response from manager
                            print("Message Received from Manager: " + modifiedMessage.decode())

                            game_in_progress = False # exit condition

                        s.setblocking(False)

                    # Updates current total books won for determining end of game
                    elif data.decode() == "Update_Books":
                        s.setblocking(True)

                        books_won += 1

                        # Return Player info
                        data = s.recv(2048)
                        return_player = int(data.decode())

                        # Checks if all books have been won and starts end of game message around logical ring
                        if books_won == 13:
                            s.sendto("Game-Over".encode(),
                                     (game_info[return_player][1], int(game_info[return_player][3])))
                            s.sendto("Winner".encode(), (neighbor[1], int(neighbor[3])))
                        else:
                            s.sendto("Continue".encode(),
                                     (game_info[return_player][1], int(game_info[return_player][3])))

                        s.setblocking(False)

                    # Deal command that adds received card to hand
                    elif data.decode() == "Deal":
                        s.setblocking(True)
                        data = s.recv(2048)
                        hand.append(data.decode())
                        s.setblocking(False)

                for s in exceptional:
                    pass

    if choice == 5:
        message = "De-register" + " " + name
        clientSocket.sendto(message.encode(), (serverName, serverPort))  # Sends De-register message
        print("De-register message sent")
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)  # Recieves Response from manager
        print("Message Received: " + modifiedMessage.decode())
    if choice == 6:

        # Non Dealer game loop
        while game_in_progress:
            readable, writeable, exceptional = select.select(inputs, outputs, inputs, 1) # creates list of available sockets for reading, writing, or errors

            for s in writeable:
                pass
            for s in readable:
                data = s.recv(2048)  # Message that determines which event will occur

                # Sets up logical ring of players
                if data.decode() == "Set-up":

                    s.setblocking(True)

                    data = s.recv(2048)
                    game_info = pickle.loads(data)
                    print(str(game_info))

                    # Determines index of player
                    for index, i in enumerate(game_info):
                        if name in i:
                            player_index = index

                    print("Player Index: " + str(player_index))
                    neighbor = game_info[(player_index + 1) % (len(game_info))]  # Sets players neighbor
                    print(str(neighbor))
                    s.sendto("Set-up".encode(), (neighbor[1], int(neighbor[3])))
                    s.sendto(data, (neighbor[1], int(neighbor[3])))

                    s.setblocking(False)

                # Players turn executed
                elif data.decode() == "Your-Move":
                    s.setblocking(True)
                    print("My Turn....")
                    data = s.recv(2048)  # Receives updated deck for drawing
                    shuffled_deck = pickle.loads(data)  # Stores updated deck
                    go_fish = True

                    # Loop for taking a player turn(runs until a player receives no cards from an ask)
                    while go_fish:

                        # Hand empty check for drawing cards(if deck is empty then player will pass turn with empty hand)
                        if len(hand) == 0 and len(shuffled_deck) != 0:
                            hand.append(shuffled_deck.pop())
                        elif len(hand) == 0 and len(shuffled_deck) == 0:
                            go_fish = False
                            s.sendto("Your-Move".encode(), (neighbor[1], int(neighbor[3])))
                            send_deck = pickle.dumps(shuffled_deck)
                            s.sendto(send_deck, (neighbor[1], int(neighbor[3])))
                            break

                        choose_player = random.choice(game_info)  # Random choice of player to ask for cards

                        # Check to see if player chosen is self
                        while name in choose_player:
                            choose_player = random.choice(game_info)

                        s.sendto("Ask".encode(),
                                 (choose_player[1], int(choose_player[4])))  # Initiate ask communication
                        s.sendto(str(player_index).encode(),
                                 (choose_player[1], int(choose_player[4])))  # Sends return player info
                        choose_card = random.choice(hand)  # Choose card to ask for at random
                        s.sendto(choose_card.encode(), (choose_player[1], int(choose_player[4])))  # Ask for card
                        print("Asking " + choose_player[0] + " " + "for " + choose_card)

                        data = s.recv(2048)  # Receive how many asked player has of chosen card
                        count = int(data.decode())
                        print("Player had " + str(count))

                        # Add cards to hand or draw and pass turn
                        if count > 0:
                            for i in range(count):
                                hand.append(choose_card)
                            check_book = hand.count(choose_card)

                            # Check if a book has been made
                            if check_book == 4:
                                for j in range(4):
                                    hand.remove(choose_card)
                                books += 1
                                s.sendto("Update_Books".encode(), (game_info[0][1], int(game_info[0][3]))) # Updates books with dealer
                                s.sendto(str(player_index).encode(), (game_info[0][1], int(game_info[0][3])))
                                data = s.recv(2048)

                                # Check if game is over message has been received from dealer
                                if data.decode() == "Game-Over":

                                    # Prints players current Books
                                    player_books.append(choose_card)
                                    print("Player has following books:")
                                    for i in range(len(player_books)):
                                        print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                              player_books[i] + "S")

                                    print("Game-Over")
                                    go_fish = False
                                    break

                                # Prints players current books
                                player_books.append(choose_card)
                                print("Player has following books:")
                                for i in range(len(player_books)):
                                    print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                          player_books[i] + "S")
                        else:

                            # Draw card if deck isn't empty
                            if len(shuffled_deck) != 0:
                                hand.append(shuffled_deck.pop())

                            check_book = hand.count(hand[(len(hand) - 1)])
                            card = hand[(len(hand) - 1)]

                            # Check if book has been made from draw
                            if check_book == 4:
                                for j in range(4):
                                    hand.remove(card)

                                books += 1 # Update player book count
                                s.sendto("Update_Books".encode(), (game_info[0][1], int(game_info[0][3]))) # Updates books with dealer
                                s.sendto(str(player_index).encode(), (game_info[0][1], int(game_info[0][3])))

                                data = s.recv(2048)

                                # Check if game is over message received from dealer
                                if data.decode() == "Game-Over":
                                    player_books.append(choose_card)

                                    # Prints players current books
                                    print("Player has following books:")
                                    for i in range(len(player_books)):
                                        print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                              player_books[i] + "S")

                                    print("Game-Over")
                                    go_fish = False
                                    break

                                # Prints players current books
                                player_books.append(choose_card)
                                print("Player has following books:")
                                for i in range(len(player_books)):
                                    print(player_books[i] + "C " + player_books[i] + "D " + player_books[i] + "H " +
                                          player_books[i] + "S")

                            go_fish = False

                            s.sendto("Your-Move".encode(), (neighbor[1], int(neighbor[3])))  # Pass turn to neighbor
                            send_deck = pickle.dumps(shuffled_deck)
                            s.sendto(send_deck, (neighbor[1], int(neighbor[3])))

                    s.setblocking(False)

                # Player ask command
                elif data.decode() == "Ask":
                    s.setblocking(True)
                    data = s.recv(2048)  # Return Player info
                    return_player = int(data.decode())

                    data = s.recv(2048)  # Card being asked for
                    print("Player is asking for " + data.decode())

                    # Check if hand is empty. If not count how many of the card the player has
                    if len(hand) != 0:
                        count = hand.count(data.decode())
                        print("I have " + str(count) + " of " + data.decode())
                    else:
                        count = 0

                    # Remove Cards from hand
                    for i in range(count):
                        hand.remove(data.decode())

                    s.sendto(str(count).encode(), (game_info[return_player][1], int(
                        game_info[return_player][3])))  # Let player who asked know how many cards they had

                    s.setblocking(False)

                # Non Dealer winner command exits game after reporting how many books player won in game
                elif data.decode() == "Winner":
                    s.setblocking(True)
                    s.sendto("Winner".encode(), (game_info[0][1], int(game_info[0][3])))
                    s.sendto(str(books).encode(), (game_info[0][1], int(game_info[0][3])))

                    # Checks that neighbor is not dealer otherwise lets next player know game is over
                    if neighbor[0] != game_info[0][0]:
                        s.sendto("Winner".encode(), (neighbor[1], int(neighbor[3])))

                    game_in_progress = False  # exit condition

                    s.setblocking(False)

                # Deal command adds cards to players hands from dealer
                elif data.decode() == "Deal":
                    s.setblocking(True)
                    data = s.recv(2048)
                    hand.append(data.decode())
                    s.setblocking(False)

            for s in exceptional:
                pass

    if choice == 7:
        print("Goodbye!")
        clientSocket.close()
        clientSocket_R.close()
        clientSocket_M.close()
        clientSocket_P.close()
        break
