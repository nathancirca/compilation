# Projet Advanced compilation
Dans ce projet, nous avons choisi de traiter trois fonctionnalités différentes: les pointeurs, les chaines de caracteres et le typage python.

<h2>Les pointeurs</h2>
En ce qui concerne les pointeurs, les operations qui sont possibles sont l'allocation de l'espace mémoire avec malloc et la possiblilité d'acceder a l'adresse d'une variable avec &. Cependant, il n'est pas encore possible d'utiliser des double pointeurs.
Le fichier pour tester les pointeurs est le fichier test.txt. Il faut lancer les commandes suivantes:
compilo.py
nasm -f elf64 demo.asm
gcc -o main -no-pie -fno-pie demo.o
./main 8



<h2>Les strings</h2>


<h2>Typage python</h2>
Le typage devrait être prêt à accueuillir les pointeurs et les chaines de caractères mais des erreurs persistent quand on utilise nasm à cause des labels, si bien qu'une addition d'entiers ne fonctionne pas. L'erreur est "label changed during code generation" et elle apparait lors de l'utilisation de nasm pour des dizaines de labels dans le cas de l'addition.
