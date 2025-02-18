

void etsi_nolla(std::vector<int>& v)
{
    int haettu_arvo = 0;
    ...
    auto paikka = std::find(v.begin(), v.end(), haettu_arvo);
    ...
}



void etsi_nolla(std::vector<int>& v)
{
    ...
    auto paikka = std::find(v.begin(), v.end(), 0);
    ...
}




bool onko_parillinen(int x)
{
    return x % 2 == 0;
}
// ...
void etsi_parillinen(std::vector<int>& v)
{
    // ...
    auto paikka = std::find_if(v.begin(), v.end(), &onko_parillinen);
    // ...
}

void etsi_parillinen(std::vector<int>& v)
{
    //...
    auto paikka = std::find_if(v.begin(), v.end(),
                               [](int x){ return x % 2 == 0; } );
    // ...
}

void laske_pienemmat(std::vector<int>& v, int arvo)
{
    return std::count_if(v.begin(), v.end(),
                         [arvo](auto alkio){ return alkio < arvo; } );
}

int laske_vertailut(std::vector<int>& v)
{
    int vertailuja = 0;
    std::sort(v.begin(), v.end(), [&vertailuja](auto vas, auto oik){ ++vertailuja; return vas<oik; } );
    return vertailuja;
}

