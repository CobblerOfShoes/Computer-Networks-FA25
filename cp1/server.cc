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

#include <sys/types.h>
#include <optional>

#include "SocketHelper.h"
#include "server-get-site.h"

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
  int startListening(int listenPort = 0) {
    // Optional library is giving me troubles, will come back to this
    // if (listenPort.has_value())
    // {
    //   m_ListenPort = listenPort;
    // }

    // Socket will be in the listening state
    if (listenPort != 0)
    {
      m_ListenPort = listenPort;
    }
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

    cout << "Got Here!" << endl;

    int bytesRead = 0;
    while (true)
    {
      m_ClientSocket = accept(m_ListenSocket, nullptr, nullptr);

      char buffer[BUFSIZ] = {0};

      while (true)
      {
        cout << buffer << endl;
        bytesRead = recv(m_ClientSocket, buffer, sizeof(buffer) - 1, 0);
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
    std::string regex_pattern(raw_pattern);

    // Grab site id
    char *site_id = strtok(nullptr, delimeters);
    if (site_id == nullptr)
    {
      cout << errorHeader << " - no SiteID was given in CHECK request." << endl;
      return 1;
    }

    // Ensure no further arguments were given
    if (strtok(nullptr, delimeters) != nullptr)
    {
      cout << "ERROR: AdCheckServer::processRequest - CHECK request only takes 4 parameters, but more than 4 were received." << endl;
      return 1;
    }

    std::pair<int, std::string> result = read_Website(url, regex_pattern, site_id, m_LogDirectory);

    return sendResponse(result.first, result.second, site_id);
  }

  void chompNewline(char* str) {
    if (str == nullptr) {
        return;
    }

    size_t len = strlen(str);
    if (len > 0 && str[len - 1] == '\n') {
        str[len - 1] = '\0'; // Replace newline with null terminator
    }
  }

  int sendResponse(int requestStatus, std::string datetime, char* site_id)
  {
    cout << requestStatus << endl;

    // Pattern was found
    if (requestStatus == 0)
    {
      chompNewline(site_id);
      std::string responseMessage = "200 YES ";
      responseMessage += site_id;
      responseMessage += datetime;
      if (send(m_ClientSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }
    else if (requestStatus == 1)
    {
      std::string responseMessage = "200 NO";
      if (send(m_ClientSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }
    else
    {
      std::string responseMessage = "400 ERROR";
      if (send(m_ClientSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }

    return 0;
  }

  // Port on which the server should listen for requests
  int m_ListenPort = 0;

  // Socket number on which the server listens
  int m_ListenSocket;

  int m_ClientSocket;

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
