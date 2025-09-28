#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <optional>


#include "SocketHelper.h"

using namespace std;
// Create a function to run a GET command on a URL input, port 80?
#define PORT "80"
#define MAXDATASIZE 100
#define URL "ns-mn1.cse.nd.edu/cse30264/ads/file1.html"

class AdCheckServer
{
public:
  /**
   * Default constructor
   */
  AdCheckServer()
  {
    // placeholder
  }

  AdCheckServer(int listenPort) : m_ListenPort(listenPort)
  {

  }

  /**
   * Default destructor
   */
  ~AdCheckServer()
  {
    // placeholder
    close(m_ListenSocket);
  }

  /**
   * Begin listening for incoming connections on a designated port
   */
  int startListening(int listenPort) {
    // Optional library is giving me troubles, will come back to this
    // if (listenPort.has_value())
    // {
    //   m_ListenPort = listenPort;
    // }

    // Socket will be in the listening state
    m_ListenSocket = createSocket_TCP_Listen(m_ListenPort & 0xFFFF);
    if (m_ListenSocket == 0)
    {
      perror("AdCheckServer::startListening - failed to create TCP Listen socket.");
      return 1;
    }

    cout << "Got Here!" << endl;

    char clientData[BUFSIZ] = {0};
    int bytesRead = 0;
    while (true)
    {
      int clientSocket = accept(m_ListenSocket, nullptr, nullptr);

      bytesRead = recv(clientSocket, clientData, sizeof(clientData - 1), 0);
      if (bytesRead < 0)
      {
        cout << "AdCheckServer::startListening - error upon receiving data from client" << endl;
      }
      else
      {
        cout << "Data received from client!" << endl;
        // if (__check_request_present__)
        // {
        //   string url = __some_regex_magic__;
        //   read_Website(url.c_str());
        // }
      }
    }

    return 0;
  }

private:
  /**
   *
   */
  int read_Website(char* url) {

    cout << url << endl;
    create_Out_Socket(url);
    return 0;
  }

  /**
   *
   */
  void* get_in_addr(struct sockaddr* sa)
  {
      if (sa->sa_family == AF_INET) {
          return &(((struct sockaddr_in*)sa)->sin_addr);
      }

      return &(((struct sockaddr_in6*)sa)->sin6_addr);
  }

  /**
   *
   */
  int create_Out_Socket(char * address) {
    int sockfd, numbytes;
    char buf[MAXDATASIZE];
    struct addrinfo hints, *servinfo, *p;
    int rv;
    char s[INET6_ADDRSTRLEN];

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(address, PORT, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    // loop through all the results and connect to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("client: socket");
            continue;
        }

        inet_ntop(p->ai_family,
            get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
        printf("client: attempting connection to %s\n", s);

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            perror("client: connect");
            close(sockfd);
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        return 2;
    }

    inet_ntop(p->ai_family,
            get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
    printf("client: connected to %s\n", s);

    freeaddrinfo(servinfo); // all done with this structure

    if ((numbytes = recv(sockfd, buf, MAXDATASIZE-1, 0)) == -1) {
        perror("recv");
        exit(1);
    }

    buf[numbytes] = '\0';

    printf("client: received '%s'\n",buf);

    // @todo: Parse data for regex pattern. Log results

    close(sockfd);

    return 0;
  }

  /**
   * Port on which the server should listen for requests
   */
  int m_ListenPort = 0;

  /**
   * Socket number on which the server listens
   */
  int m_ListenSocket;
};

/**
 * Program takes in two arguments.
 *  1) Port number to run the server on
 *  2) Log directory location
 *
 * Upon receiving a request from a client in the form:
 * "CHECK [URL] [REGEX_PATTERN] [LOG_LOCATION]"
 *  1) Get contents from URL
 *  2) Check if REGEX_PATTERN appears in the URL's web contents
 *  3) If
 */
int main(int argc, char * argv[]) {

  AdCheckServer server = AdCheckServer();
  server.startListening(std::stoi(argv[1]));

	// string buffer;
  //   buffer = URL;
  //   char * url = new char[BUFSIZ];
  //   strncpy(url, buffer.c_str(), BUFSIZ-1);
	// server.read_Website(url);
	return 0;

}
