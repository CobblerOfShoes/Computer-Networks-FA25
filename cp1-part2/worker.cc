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
#include "worker-get-site.h"

using namespace std;
// Create a function to run a GET command on a URL input, port 80?
#define PORT "80"
#define MAXDATASIZE 100
#define URL "ns-mn1.cse.nd.edu/cse30264/ads/file1.html"

class AdCheckWorker
{
public:
  /**
   * Constructor
   *
   * @param[in] listenPort   Port on which to listen for clients
   * @param[in] logDirectory Directory to store log files in
   */
  AdCheckWorker(string workerPort,
                string logDirectory,
                string workerIP,
                string orchestratorIP,
                string orchestratorPort,
                string workerID) : m_WorkerPort(workerPort),
                                   m_LogDirectory(logDirectory),
                                   m_WorkerIP(workerIP),
                                   m_OrchestratorIP(orchestratorIP),
                                   m_OrchestratorPort(orchestratorPort),
                                   m_WorkerID(workerID)
  {

  }

  /**
   * Destructor
   */
  ~AdCheckWorker()
  {
    close(m_OrchestratorTCPSocket);
  }

  /**
   * Send a UDP message to the orchestrator to register
   */
  int register_worker()
  {
    int result = 0;

    int orchestratorUDPSocket = createUDPSocket(m_OrchestratorIP.c_str(),
                                                m_OrchestratorPort.c_str());

    string message = "REGISTER " + m_WorkerIP + " " + m_WorkerPort + " " + m_WorkerID;

    result = send(orchestratorUDPSocket, message.c_str(), strlen(message.c_str()), 0);

    return result;
  }

  /**
   * Begin listening for incoming connections on a designated port
   *
   * @param[in] listenPort The port on which to listen to listen for connections
   */
  int startListening(int listenPort = 0)
  {
    // Socket will be in the listening state
    if (listenPort == 0)
    {
      listenPort = stoi(m_WorkerPort);
    }
    if ((listenPort < 54000) || (listenPort > 54150))
    {
      cout << "Port does not fall within given range of 54000-54150." << endl;
      return 1;
    }

    m_OrchestratorTCPSocket = createSocket_TCP_Listen(stoi(m_WorkerPort) & 0xFFFF);
    if (m_OrchestratorTCPSocket == 0)
    {
      perror("AdCheckServer::startListening - failed to create TCP Listen socket.");
      return 1;
    }

    int bytesRead = 0;
    while (true)
    {
      // Create a fresh buffer for each incoming request
      char buffer[BUFSIZ] = {0};

      // Begin receiving a new request
      while (true)
      {
        cout << buffer << endl;
        bytesRead = recv(m_OrchestratorTCPSocket, buffer, sizeof(buffer) - 1, 0);
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
        printf("%s", buffer);
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

    const char* delimeters = " \t\v\r\n";

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

  int sendResponse(int requestStatus, std::string datetime, char* site_id)
  {
    cout << requestStatus << endl;

    // Pattern was found
    if (requestStatus == 0)
    {
      std::string responseMessage = "200 YES ";
      responseMessage += site_id;
      responseMessage += ' ' + datetime;
      if (send(m_OrchestratorTCPSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }
    else if (requestStatus == 1)
    {
      std::string responseMessage = "200 NO";
      if (send(m_OrchestratorTCPSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }
    else
    {
      std::string responseMessage = "400 ERROR";
      if (send(m_OrchestratorTCPSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
      {
        return 1;
      }
    }

    return 0;
  }


  // Port numbers to communicate on
  string m_WorkerPort = "";
  string m_OrchestratorPort = "";

  string m_WorkerIP = "";
  string m_OrchestratorIP = "";

  // Worker ID for distinguishing workers
  string m_WorkerID = "";

  // Sockets for communicating with orchestrator
  int m_OrchestratorTCPSocket;

  // Logging directory
  std::string m_LogDirectory = "server-logs";
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
  if (argc == 7)
  {
    string listenPort(argv[1]);
    string logDirectory(argv[2]);
    string workerIP(argv[3]);
    string orchestratorIP(argv[4]);
    string orchestratorPort(argv[5]);
    string workerID(argv[6]);

    AdCheckWorker worker = AdCheckWorker(listenPort, logDirectory,
                                         workerIP, orchestratorIP,
                                         orchestratorPort, workerID);

    worker.register_worker();

    worker.startListening();

    return 0;
  }

	printf("ERROR: Insufficient arguments received.\n");
  printf("Usage: adChecker [PORT_#] [LOG_FILEPATH]\n");
  return 1;
}
