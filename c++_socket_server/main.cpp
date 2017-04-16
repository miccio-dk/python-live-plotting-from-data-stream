/*
* main.cpp
* -----------------------------------------------------------------------
* Copyright (C) Allan Hein, Inc - All Rights Reserved
* Unauthorized copying of this file, via any medium is strictly prohibited
* Proprietary and confidential
*
* Written by Allan Hein <allan@d0st3n.dk>
* Created 2016-03-10
*
* Updated 2016-29-12 - By Allan Hein
*  - Changed serial reading to be blocking instead of interval, this spare a bit of cpu power
* -----------------------------------------------------------------------
*/


// CPP libs
#include <iostream> // Only for debugging ?
#include <ctime>
#include <mutex>
#include <algorithm>
#include <ctime>
#include <vector>

// C libs
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <unistd.h>
#include <pthread.h>

// Custom libs
#include "simpleSerial.hpp"

// Make this define for debug information
// #define DEBUG_MODE

// Default defines
#define MAX_BUFFER_CAP  2048
#define LOOP_FREQ_SERIAL 3000 // in Herz
#define LOOP_FREQ_SOCKET 100 // in Herz
#define APP_PORT 12345
#define APP_HOST "0.0.0.0"

static void error(const char *msg)
{
  perror(msg);
  // std::cout << msg << std::endl;
  exit(1);
}

static void print_help(const char *name)
{
  std::cout << "Use this function with: " << name << " [serial_port] [socket_port (optional)]" << std::endl;
  exit(1);
}

static bool socketAlive(int socket)
{
  char buff;
  int rec = recv(socket, &buff, 1, MSG_PEEK | MSG_DONTWAIT);

  if(rec == 0)
  {
    return false;
  }
  return true;
}


class Client
{

public:
  Client() : addr_size(sizeof(sockaddr_storage)) {}
  // Socket stuff need to be public!
  socklen_t addr_size; // Size of addr
  sockaddr_storage addr_storage; // The addr
  int socket; // The file descriptor
  std::mutex mutex;
};

// Global list of clients!
std::vector<Client*> clients;
std::mutex clientsMutex;

// And port
int socket_port;


void *socket_listner(void *attr)
{
  SimpleSerial *serial = (SimpleSerial*) attr;
  int incoming_socket;
  struct sockaddr_in serverAddr;

  incoming_socket = socket(PF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);

  serverAddr.sin_family = AF_INET;
  serverAddr.sin_port = htons(socket_port);
  serverAddr.sin_addr.s_addr = inet_addr(APP_HOST);

  memset(serverAddr.sin_zero, '\0', sizeof(serverAddr.sin_zero));

  int optval = 1;
  if (setsockopt(incoming_socket, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(int)) == -1)
    error("setsockopt");

  // Let's bind ?
  if(bind(incoming_socket, (struct sockaddr *) &serverAddr, sizeof(serverAddr)) == 0)
    std::cout << "Is now bound to port " << socket_port << std::endl;
  else
    error("Failed to bind!");

  if(listen(incoming_socket, 5) == 0)
    std::cout << "Now in socket listing mode!" << std::endl;
  else
    error("Failed to start listing!");


  // Create the variables we need
  int recv_res;
  char * ip_in_str;
  char buff[MAX_BUFFER_CAP];

#ifdef DEBUG_MODE
  time_t time = std::time(NULL);
  int count = 0;
#endif

  Client *pclient = new Client;
  while(1)
  {
    // Check for new incomming connections!
    pclient->socket = accept(
      incoming_socket,
      (struct sockaddr*) &(pclient->addr_storage),
      &pclient->addr_size);

    clientsMutex.lock();
    // Check if got a new client, and push it back!
    if(pclient->socket != -1)
    {
      clients.push_back(pclient);
      ip_in_str = inet_ntoa(((sockaddr_in *)& (pclient)->addr_storage)->sin_addr);

      pclient = new Client;

      std::cout << "New connection from: " << ip_in_str << std::endl;
      std::cout << "Number of clients: " << clients.size() << std::endl;
    }

    for(auto client = clients.begin() ; client != clients.end();)
    {
      // Check if the client have something to say!
      recv_res = recv( (*client)->socket, buff, sizeof(buff), MSG_DONTWAIT);

      // Still a connection but no new data. Let's continue the loop!
      if(recv_res < 0)
      {
        client++;
        continue;
      }

      // Just to create the ip to a string!
      ip_in_str = inet_ntoa(((sockaddr_in *) &(*client)->addr_storage)->sin_addr);

      // The connection was terminated!
      if(recv_res == 0)
      {
        std::cout << "Lost connection to: "  << ip_in_str << std::endl;
        delete(*client);
        client = clients.erase(client);
        std::cout << "Number of clients: " << clients.size() << std::endl;
        continue;
      }

      // We got some data
      if(recv_res > 0)
      {
        // Add a line termination for easier use in the future
        buff[recv_res++] = '\r';
        buff[recv_res++] = '\n';
        buff[recv_res] = '\0';

        serial->putS(buff);
        // Put the data on the serial port!
        std::cout << "Got data (from " << ip_in_str << ")" << std::endl;
      }
      client++;
    }
    clientsMutex.unlock();
    usleep(1000000/LOOP_FREQ_SOCKET);

#ifdef DEBUG_MODE
    ++count;
    if((std::time(NULL) - time) >= 1)
    {
      std::cout << "Socket Thread speed: " << count << " hz" << std::endl;
      std::time(&time);
      count = 0;
    }
#endif

  }

}

void *serial_listner(void *attr)
{
  SimpleSerial *serial = (SimpleSerial*) attr;

#ifdef DEBUG_MODE
  time_t time = std::time(NULL);
  int count = 0;
#endif

  char c = '\n';
  char pc = ' ';
  while(1)
  {
    // Get the next char from the serial port
    if(serial->getC(&c))
    {
      if(c == '\n' && pc == '\n')
      {
        continue;
      }
      pc = c;

      // Loop over the clients and send the char to them!
      clientsMutex.lock();
      for(auto& client : clients)
      // for(auto client = clients.begin() ; client != clients.end(); ++client)
      {
        // send((*client)->socket, &c, 1, MSG_NOSIGNAL);
        send(client->socket, &c, 1, MSG_NOSIGNAL);
      }
      clientsMutex.unlock();
    }
    else
    {
     usleep(100);
    }

#ifdef DEBUG_MODE
    ++count;
    if((std::time(NULL) - time) >= 1)
    {
      std::cout << "Serial Thread speed: " << count << " hz" << std::endl;
      std::time(&time);
      count = 0;
    }
#endif
  }
}



// [serial port] [port]
int main(int argc, char const *argv[])
{
  if(argc < 2)
  {
    print_help(argv[0]);
  }

  // Set default port
  socket_port = 50007;
  if(argc == 3)
  {
    socket_port = atoi(argv[2]);
  }

  SimpleSerial serial(argv[1], 115200, false);

  if(!serial.isConnceted())
  {
    error("Failed to connect to serial port");
  }

  pthread_t socket_thread, serial_thread;

  if(pthread_create(&socket_thread, NULL, socket_listner, &serial))
  {
    error("Failed to start socket_thread!");
  }

  if(pthread_create(&serial_thread, NULL, serial_listner, &serial))
  {
    error("Failed to start serial thread!");
  }


  std::cout << "Main-thread is up and running with PID: " << getpid() << std::endl;


  // Wait for the threads to complete!
  pthread_join(socket_thread, NULL);
  pthread_join(serial_thread, NULL);
  return 0;
}
