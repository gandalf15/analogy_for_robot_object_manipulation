.PHONY : clean all
CC=gcc
CFLAGS=-Wall -march=native -mtune=native -std=c99 -shared -fPIC
default: clean mollers devillers pipinstall

clean:
	rm -f analogy/collision_detection/build/*.so
	rm -rf venv/

mollers:
	$(CC) $(CFLAGS) analogy/collision_detection/src/mollers_tri_inter_alg.c -o analogy/collision_detection/build/mollers_tri_tri.so

devillers:
	$(CC) $(CFLAGS) analogy/collision_detection/src/devillers_tri_inter_alg.c -o analogy/collision_detection/build/devillers_tri_tri.so

pipinstall:
	python3 -m venv venv; \
	source venv/bin/activate; \
	pip install --upgrade pip; \
	pip install -r requirements.txt;