#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(){
  char message[] = "hello world!";
  char* addr = message;

  printf("cleartext:\t%p, %s\n", message, message);
  getchar();
  printf("cleartext:\t%p, %s\n",message,message);
  return 0;
}
