#include <vector>
#include <map>
#include <algorithm>
#include <utility>
#include <iterator>

using iterator = std::vector<int>::iterator;

// Move even elements first, tell how many there are
int even_first(std::vector<int>& v)
{
    auto even_end = std::partition(v.begin(), v.end(),
                        [](auto e){ return e % 2 == 0; });
    return even_end - v.begin(); // How many elements in the range
}

// Remove even elements
void remove_even(std::vector<int>& v)
{
    auto new_end = std::remove_if(v.begin(), v.end(),
                        [](auto e){ return e % 2 == 0; });
    v.erase(new_end, v.end()); // Remove "garbage" from the end
}

// Sort: even elements in ascending order, then odd in descending order
bool even_odd_comparison(int left, int right)
{
    if (left%2 == 0)
    {
        if (right%2 != 0) { return true; } // Even always before odd
        else { return left < right; } // Both even, smaller first
    }
    else
    {
        if (right%2 == 0) { return false; } // Odd always after even
        else { return right < left; } // Both odd, larger first
    }
}

void even_odd_sort(std::vector<int>& v)
{
    std::sort(v.begin(), v.end(), &even_odd_comparison);
}

void even_odd_sort2(std::vector<int>& v)
{
    // Partition into even and odd
    auto split = std::partition(v.begin(), v.end(),
                    [](auto e){ return e%2 == 0; } );
    // Sort even into ascending (normal) order
    std::sort(v.begin(), split);
    // Sort odd into descending order
    std::sort(split, v.end(),
              [](auto l, auto r){ return r < l; } );
}


void quicksort(iterator begin, iterator end)
{
    if (begin < end)
    {
        auto lastiter = end-1;
        auto pivotvalue = *lastiter;
        auto pivotiter = std::partition(begin, lastiter, 
                           [pivotvalue](auto elem)
                           { return elem < pivotvalue; } );
        std::swap(*lastiter, *pivotiter); // Swap pivot element to the middle
        quicksort(begin, pivotiter);
        quicksort(pivotiter+1, end); // (+1 = skip pivot element)
    }
}



struct Coord
{
    int x;
    int y;
};

bool operator<(Coord c1, Coord c2)
{
    if (c1.x < c2.x) { return true; }
    else if (c2.x < c1.x) { return false; }
    else { return c1.y < c2.y; }
}

std::map<Coord, int> coord_xy_map;





struct CompareCoord_yx
{
    bool operator()(Coord c1, Coord c2) const
    {
        if (c1.y < c2.y) { return true; }
        else if (c2.y < c1.y) { return false; }
        else { return c1.x < c2.x; }
    }
};

std::map<Coord, int, CompareCoord_yx> coord_yx_map;



#include <iostream>

int main()
{
    std::vector<int> v = {34, 635, 74, 24, 63, 42, 75, 967, 52, 24, 524, 31, 1};
    std::vector<int> v2 = v;
    
    auto res = even_first(v2);
    std::cout << "even_first : " << res << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
   remove_even(v2);
    std::cout << "remove_even" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    even_odd_sort(v2);
    std::cout << "even_odd_sort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    even_odd_sort2(v2);
    std::cout << "even_odd_sort2" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    quicksort(v2.begin(), v2.end());
    std::cout << "quicksort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
}
