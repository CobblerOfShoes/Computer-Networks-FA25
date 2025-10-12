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
#include <thread>
#include <pthread.h>

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
    int listenPort = stoi(m_WorkerPort);
    if ((listenPort < 54000) || (listenPort > 54150))
    {
      cout << "Port does not fall within given range of 54000-54150." << endl;
      exit(1);
    }

    m_TCPListenSocket = createSocket_TCP_Listen(listenPort & 0xFFFF);
  }

  /**
   * Destructor
   */
  ~AdCheckWorker()
  {
    close(m_TCPListenSocket);
    close(m_OrchestratorSocket);
  }

  /** A threaded function that checks if the orchestrator is still alive */
  void heartbeat(int orchestratorSocket, struct sockaddr_in server_addr)
  {
    std::string message = "PING\r\n\r\n";
    char buffer[1024];
    bool orchestratorAlive = true;
    socklen_t addr_len = sizeof(server_addr);

    // Set a timeout
    struct timeval tv;
    tv.tv_sec = 10;
    tv.tv_usec = 0;
    setsockopt(orchestratorSocket, SOL_SOCKET, SO_RCVTIMEO,
               (const char *)&tv, sizeof(tv));

    while (orchestratorAlive)
    {
      std::this_thread::sleep_for(std::chrono::seconds(5));

      sendto(orchestratorSocket, message.c_str(), strlen(message.c_str()), 0,
              (struct sockaddr*)&server_addr, sizeof(server_addr));

      int result = recvfrom(orchestratorSocket, buffer, sizeof(buffer)-1, 0,
                            (struct sockaddr*)&server_addr, &addr_len);
      cout << "life" << endl;
      if (result < 0)
      {
        cout << "death" << endl;
        orchestratorAlive = false;
      }
    }

    close(orchestratorSocket);
    exit(1);
  }

  /**
   * Send a UDP message to the orchestrator to register
   */
  int register_worker()
  {
    int result = 0;

    int orchestratorUDPSocket = createUDPSocket(m_WorkerIP.c_str(),
                                                m_WorkerPort.c_str());

    string message = "REGISTER " + m_WorkerIP + " " + m_WorkerPort + " " + m_WorkerID;

    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(std::stoi(m_OrchestratorPort));
    server_addr.sin_addr.s_addr = inet_addr(m_OrchestratorIP.c_str());

    result = sendto(orchestratorUDPSocket, message.c_str(), strlen(message.c_str()), 0,
                    (struct sockaddr*)&server_addr, sizeof(server_addr));

    std::thread t1(&AdCheckWorker::heartbeat, this, orchestratorUDPSocket, server_addr);
    t1.detach();

    return result;
  }

  /**
   * Begin listening for incoming connections on a designated port
   */
  int startListening()
  {
    if (m_TCPListenSocket == 0)
    {
      perror("AdCheckServer::startListening - failed to create TCP Listen socket.");
      return 1;
    }

    m_OrchestratorSocket = accept(m_TCPListenSocket, nullptr, nullptr);

    int bytesRead = 0;
    while (true)
    {
      // Create a fresh buffer for each incoming request
      char buffer[BUFSIZ] = {0};

      // Begin receiving a new request
      while (true)
      {
        bytesRead = recv(m_OrchestratorSocket, buffer, sizeof(buffer) - 1, 0);
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
            break;
          }
        }
      }

      if (buffer[0] != '\0')
      {
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
    m_AdString = regex_pattern;

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
    // Pattern was found
    std::string responseMessage = "RESPONSE: " + m_WorkerID + " " + m_AdString;
    if (requestStatus == 0)
    {
      responseMessage += " 200 YES ";
      responseMessage += site_id;
      responseMessage += ' ' + datetime;
    }
    else if (requestStatus == 1)
    {
      responseMessage += " 200 NO";
    }
    else
    {
      responseMessage += " 400 ERROR";
    }

    if (send(m_OrchestratorSocket, responseMessage.data(), responseMessage.length(), 0) < 0)
    {
      return 1;
    }

    return 0;
  }


  // Port numbers to communicate on
  string m_WorkerPort;
  string m_OrchestratorPort;

  string m_WorkerIP;
  string m_OrchestratorIP;

  // Worker ID for distinguishing workers
  string m_WorkerID;

  string m_AdString;

  // Sockets for communicating with orchestrator
  int m_TCPListenSocket;
  int m_OrchestratorSocket;

  // Logging directory
  std::string m_LogDirectory;
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
