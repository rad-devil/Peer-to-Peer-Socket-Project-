# Peer-to-Peer-Socket-Project-
Files Included: manager.py (Server Process), player.py (Client Process) and Socket Project.pdf (detailed description of the project)

This was a project that was completed in a group of 2 people.
Implemented a peer-to-peer application program in which processes communicate using sockets to play the card game of“Go Fish” using Python.
The objective of the game is to win the most books of cards, the game ends when all thirteen books have been won
 
How the game and the implementation works:

There are two or more processes running in this implementation. One is the manager(server in this case) and peer processes (client [could be multiple])
The manager process behaves like a server and is used for managing players and games. Before it does anything else, each peer process must register with the manager. 

When a peer wants to start a game of Go Fish, it requests 1 ≤ k ≤ 4 other peers from the manager to be players in the game. The manager selects k players, returns their information to the peer, and stores all participant information for the game. The peer starting the game acts as the dealer. Using the information returned by the manager, the dealer treats the k + 1 players (including itself) as logically organized in a clockwise ring.

The dealer shuffles the cards and then deals each player 5 or 7 cards  face down, starting with the player to the its left in the ring. The game then proceeds according to the rules of the game. Once all “books” have been won, the dealer announces the winner as the player with the most books, and the game terminates.

**Lessons Learned:**

1. Establishing socket connection and using P2P connection between the clients (Players)

2. Establishing socket connection between the Clients and Server

3. Defining Message Exchange and Message Formats between Clients and Server

4. Maintaing and binding different Port Number for clients and the server

5. How to use a single threaded application architecture to manage communication between multiple processes and to ensure that the communication between them is non-blocking  while recieving messages from the socket(ie. it will return immediately even if there is no message) so that it doesn't create a deadlock



