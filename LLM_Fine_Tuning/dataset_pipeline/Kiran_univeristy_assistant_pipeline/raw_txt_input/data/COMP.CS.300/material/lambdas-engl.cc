

void find_zero(std::vector<int>& v)
{
    int value_wanted = 0;
    ...
    auto place = std::find(v.begin(), v.end(), value_wanted);
    ...
}



void find_zero(std::vector<int>& v)
{
    ...
    auto place = std::find(v.begin(), v.end(), 0);
    ...
}








bool is_even(int x)
{
    return x % 2 == 0;
}
...
void find_even(std::vector<int>& v)
{
    ...
    auto place = std::find_if(v.begin(), v.end(), &is_even);
    ...
}

void find_even(std::vector<int>& v)
{
    ...
    auto place = std::find_if(v.begin(), v.end(),
                               [](int x){ return x % 2 == 0; } );
    ...
}

void count_smaller(std::vector<int>& v, int value)
{
    return std::count_if(v.begin(), v.end(), [value](auto elem){ return elem < value; } );
}

int count_comparisons(std::vector<int>& v)
{
    int comparisons = 0;
    std::sort(v.begin(), v.end(), [&comparisons](auto l, auto r){ ++comparisons; return l<r; } );
    return comparisons;
}

