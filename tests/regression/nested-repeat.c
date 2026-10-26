int leaf(int x){return x;} int wrap(int x){return leaf(x)+leaf(x+1);} int main(){return wrap(1)+wrap(2);}
