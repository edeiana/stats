CC=clang++
SRCS=makeOutputTxt.cpp

all: makeOutputTxt

makeOutputTxt: $(SRCS)
	$(CC) -O3 -std=c++14 -o $@ $(SRCS)

install: makeOutputTxt
	cp makeOutputTxt ../../inst/bin

clean:
	rm -f ../../inst/bin/makeOutputTxt makeOutputTxt *.o
