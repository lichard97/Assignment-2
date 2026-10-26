int g(int); int f(int n){if(n) return g(n-1); return 0;} int g(int n){if(n) return f(n-1); return 0;} int main(){return f(3);}
