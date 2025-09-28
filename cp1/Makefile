CXX = g++
CXXFLAGS = -Wall
TARGET = adChecker
SOURCES = server.cc SocketHelper.cc
OBJECTS = $(SOURCES:.cc=.o)

all: $(TARGET)

clean:
	rm *.o
	rm $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(TARGET)

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@