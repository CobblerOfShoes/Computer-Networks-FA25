#include <iostream>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>

#include <cstring>
#include <string>
#include <string.h>
#include <regex>

#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>

#include <ctime>

#include <sys/types.h>
#include <optional>

#include <curl/curl.h>

// #include "lib/curlpp/include/curlpp/cURLpp.hpp"
// // #include "lib/curlpp/include/curlpp/Easy.hpp"
// #include "lib/curlpp/include/curlpp/Options.hpp"
// // #include "lib/curlpp/include/curlpp/Exceptions.hpp"
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
   *
   * @param[in] listenPort Port on which to listen for clients
   */
  AdCheckServer()
  {
    // placeholder
  }

  /**
   * Overloaded constructor
   *
   * @param[in] listenPort   Port on which to listen for clients
   * @param[in] logDirectory Directory to store log files in
   */
  AdCheckServer(int listenPort,
                string logDirectory) : m_ListenPort(listenPort),
                                       m_LogDirectory(logDirectory)
  {

  }

  /**
   * Default destructor
   */
  ~AdCheckServer()
  {
    close(m_ListenSocket);
  }

  /**
   * Begin listening for incoming connections on a designated port
   *
   * @param[in] listenPort The port on which to listen to listen for connections
   */
  int startListening(int listenPort) {
    // Optional library is giving me troubles, will come back to this
    // if (listenPort.has_value())
    // {
    //   m_ListenPort = listenPort;
    // }

    // Socket will be in the listening state
    m_ListenPort = listenPort;
    if ((m_ListenPort < 54000) || (m_ListenPort > 54150))
    {
      cout << "Port does not fall within given range of 54000-54150." << endl;
      return 1;
    }

    m_ListenSocket = createSocket_TCP_Listen(m_ListenPort & 0xFFFF);
    if (m_ListenSocket == 0)
    {
      perror("AdCheckServer::startListening - failed to create TCP Listen socket.");
      return 1;
    }

    int bytesRead = 0;
    while (true)
    {
      int clientSocket = accept(m_ListenSocket, nullptr, nullptr);

      char buffer[BUFSIZ] = {0};

      while (true)
      {
        cout << buffer << endl;
        bytesRead = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
        if (bytesRead < 0)
        {
          cout << "AdCheckServer::startListening - error upon receiving data from client" << endl;
          break;
        }
        else if (bytesRead == 0)
        {
          // End of data from client
          break;
        }
        else
        {
          buffer[bytesRead] = '\0';

          // Check for a specific termination sequence from the client
          if (strstr(buffer, "\r\n\r\n") != nullptr)
          {
            cout << "Termination sequence received. Stopping read." << endl;
            break;
          }
        }
      }

      if (buffer[0] != '\0')
      {
        cout << "Data received from client!" << endl;
        int result = processRequest(buffer);
      }
    }

    return 0;
  }

private:
  /**
   * Process requests in the CHECK format
   *
   * @param[in] request String data of
   *
   * @return 0 on success, 1 on invalid request,
   */
  int processRequest(char* request)
  {
    std::string errorHeader = "ERROR: AdCheckServer::processRequest";

    cout << request << endl;

    const char* delimeters = " ";

    char *token = strtok(request, delimeters);
    if (token == nullptr)
    {
      cout << errorHeader << " - empty request received." << endl;
      return 1;
    }

    // Check request type
    if (strcmp(token, "CHECK") != 0)
    {
      cout << errorHeader << " - invalid request of " << token << " received." << endl;
      return 1;
    }

    // Grab url
    char *url = strtok(nullptr, delimeters);
    if (url == nullptr)
    {
      cout << errorHeader << " - no URL present in CHECK request." << endl;
      return 1;
    }

    // Grab regex patter
    char *raw_pattern = strtok(nullptr, delimeters);
    if (raw_pattern == nullptr)
    {
      cout << errorHeader << " - no regex pattern given in CHECK request." << endl;
      return 1;
    }
    std::regex regex_pattern(raw_pattern);

    // Grab site id
    char *site_id = strtok(nullptr, delimeters);
    if (site_id == nullptr)
    {
      cout << errorHeader << " - no SiteID was given in CHECK request." << endl;
      return 1;
    }

    // Ensure no further arguments were given
    token = strtok(nullptr, delimeters);
    if (token != nullptr)
    {
      cout << "ERROR: AdCheckServer::processRequest - CHECK request only takes 4 parameters, but more than 4 were received." << endl;
      return 1;
    }

    return read_Website(url, regex_pattern, site_id);
  }

  /**
   * When a CHECK request is received from a client, process the request
   *
   * @param[in] url     URL to check for the received regex pattern
   * @param[in] pattern Regex pattern to scan site contents for
   * @param[in] siteID  Site ID used for logging purposes
   *
   * @return 0 for pattern not found, 1 for pattern found in site contents
   */
  int read_Website(char* url, std::regex pattern, char* siteID) {
    int scanSocket = create_Out_Socket(url);

    // @todo: Send a GET request and check for pattern
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if(curl)
    {
      long my_scope_id;
      curl_easy_setopt(curl, CURLOPT_URL, "https://example.com");

      /* Perform the request, res gets the return code */
      res = curl_easy_perform(curl);
      /* Check for errors */
      if(res != CURLE_OK)
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));

      /* always cleanup */
      curl_easy_cleanup(curl);
    }

    cout << res << endl;

    bool patternFound = regex_match(curl_easy_strerror(res), pattern);

    close(scanSocket);
    return ;
  }

  int sendResponse(bool success, bool patternFound = false, int siteID = 0, )

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
   * Create an outward facing socket to process a client's request
   *
   * @param[in] address IP address of site to check ads of
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

  // Port on which the server should listen for requests
  int m_ListenPort = 0;

  // Socket number on which the server listens
  int m_ListenSocket;

  // Logging directory
  std::string m_LogDirectory = "server-logs";

  // Format of CHECK requests
  // std::regex checkRequest("CHECK (([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))? ");
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
 *  3) If pattern appears, log all images on the site
 */
int main(int argc, char * argv[]) {
  int listenPort = std::stoi(argv[1]);
  string logDirectory = static_cast<std::string>(argv[2]);

  AdCheckServer server = AdCheckServer(listenPort, logDirectory);
  server.startListening(std::stoi(argv[1]));

	// string buffer;
  //   buffer = URL;
  //   char * url = new char[BUFSIZ];
  //   strncpy(url, buffer.c_str(), BUFSIZ-1);
	// server.read_Website(url);
	return 0;

}
