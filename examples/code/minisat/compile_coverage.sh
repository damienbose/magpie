#!/bin/sh

MROOT=.. CFLAGS="-fpermissive --coverage" LFLAGS="-lgcov" make -C simp
