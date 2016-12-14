# CPP=g++
CC=g++
# CPPFLAGS=-Wall -std=c++11 -g
# CFLAGS=-Wall -g -std=c11
CFLAGS=-std=c++11 -O3
LDFLAGS=-lpthread

#Build dirs!
BUILD_DIR=build
OBJ_DIR=$(BUILD_DIR)/obj
DEP_DIR=$(BUILD_DIR)/dep
BIN_DIR=.
BUILD_DIRS=$(BUILD_DIR) $(OBJ_DIR) $(BIN_DIR)





#Server Stuff
SERVER_CPPSRC=$(wildcard *.cpp)
SERVER_INC=.
SERVER_COBJ=$(addprefix $(OBJ_DIR)/server/, $(SERVER_CSRC:.c=.o))
SERVER_CPPOBJ=$(addprefix $(OBJ_DIR)/server/, $(SERVER_CPPSRC:.cpp=.oo))

## DONT EDIT UNDER HERE! ##



all: server

######################################
############# Server #################
######################################
server: $(SERVER_CPPOBJ)
	@mkdir -p $(BIN_DIR)
	@echo "Linking $@"
	@$(CC) $(CFLAGS) -o $(BIN_DIR)/$@ $^ $(LDFLAGS)

# Compile Caster
$(OBJ_DIR)/server/%.oo : %.cpp
	@mkdir -p $(dir $@)
	@echo "Compiling $<"
	@$(CC) $(CFLAGS) $(addprefix -I, $(SERVER_INC)) -c $< -o $@


clean: clean_server


clean_server:
	@rm -f $(SERVER_COBJ)
	@rm -f $(SERVER_CPPOBJ)
	@rm -f $(BIN_DIR)/server
	@rm -f $(BUILD_DIR)/server
	@rm -rf $(BUILD_DIR)

.PHONY: clean
.SECONDARY: clean
