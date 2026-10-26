extern int source(void); int leaf(int x){return x;} int main(){int x=source(); if(x) x++; else x--; return leaf(x);}
