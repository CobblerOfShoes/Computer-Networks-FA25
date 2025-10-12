CXX = g++
CXXFLAGS = -Wall
LDFLAGS = -lcurl
TARGET = adChecker
SOURCES = worker.cc worker-get-site.cc SocketHelper.cc
OBJECTS = $(SOURCES:.cc=.o)

all: $(TARGET)

clean:
	rm *.o
	rm $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@