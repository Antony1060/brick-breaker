#!/bin/sh

cc -g -fPIC -shared -I/usr/include/python3.10/ -L/usr/lib/python3.10/ -lpython3.10 -o ccollision.so ccollision.c
