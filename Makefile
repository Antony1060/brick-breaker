.DEFAULT_GOAL := build

.PHONY: clean
clean:
	rm -rf build/*

.PHONY: build
build:
	mkdir -p build
	gcc -fPIC -shared -O3 -o ./build/ccollision.so ./src/c/ccollision.c