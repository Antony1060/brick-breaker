.DEFAULT_GOAL := build

.PHONY: clean
clean:
	rm -rf build/*

.PHONY: build
build:
	mkdir -p build
	gcc -Wall -Wextra -Werror -Wno-missing-field-initializers -fPIC -shared -march=native -O3 -o ./build/ccollision.so ./src/c/ccollision.c
