#include <vector>
#include <algorithm>
#include <utility>
#include <iterator>

using iterator = std::vector<int>::iterator;


void selection_sort(iterator begin, iterator end)
{
    for (auto start = begin; start != end-1; ++start)
    {
        auto miniter = std::min_element(start, end);
        std::swap(*start, *miniter);
    }
}


void mergesort1(iterator begin, iterator end)
{
    if (end-begin > 1)
    {
        auto miditer = begin + (end-begin)/2;
        mergesort1(begin, miditer);
        mergesort1(miditer, end);
        
        // Vector with n zeroes
        std::vector<int> vec2(end-begin);
        std::merge(begin, miditer, // range 1
                   miditer, end, // range 2
                   vec2.begin()); // output: merge into the copy
        // Move back to original
        std::move(vec2.begin(), vec2.end(), begin);
    }
}

void mergesort2(iterator begin, iterator end)
{
    if (end-begin > 1)
    {
        auto miditer = begin + (end-begin)/2;
        mergesort2(begin, miditer);
        mergesort2(miditer, end);
        std::inplace_merge(begin, miditer, end);
    }
}

void insertion_sort(iterator begin, iterator end)
{
    for (auto next_elem = begin+1; next_elem != end;
         ++next_elem)
    {
        auto key = *next_elem;
        auto place = std::upper_bound(begin, next_elem, key); // Find key's place
        std::move_backward(place, next_elem, next_elem+1); // Move one to the right
        *place = key; // Put new element into the vacated place
    }
}

void mergesort3(iterator begin, iterator end)
{
    if (end-begin > 1)
    {
        auto miditer = begin + (end-begin)/2;
        mergesort3(begin, miditer);
        mergesort3(miditer, end);

        std::vector<int> vec2;
        vec2.reserve(end-begin);
        std::merge(begin, miditer, // range 1
                   miditer, end, // range 2
                   std::back_inserter(vec2)); // output: *insert* at end of vec2
        // Move back to original
        std::move(vec2.begin(), vec2.end(), begin);
    }
}






void mergesort4(iterator begin, iterator end)
{
    if (end-begin > 1)
    {
        // Copy elements into a new vector
        std::vector<int> vec2(begin, end); 
        auto begin2 = vec2.begin();
        auto end2 = vec2.end();
        auto miditer2 = begin2 + (end2-begin2)/2;
        mergesort3(begin2, miditer2);
        mergesort3(miditer2, end2);
        std::merge(begin2, miditer2, // range 1
                   miditer2, end2, // range 2
                   begin); // output: merge into the original vector
    }
}

void quicksort(iterator begin, iterator end)
{
    if (begin < end)
    {
        auto lastiter = end-1;
        auto pivotvalue = *lastiter;
        auto pivotiter = std::partition(begin, lastiter, [pivotvalue](auto elem){ return elem < pivotvalue; } );
        std::swap(*lastiter, *pivotiter); // Swap pivot element to the middle
        quicksort(begin, pivotiter);
        quicksort(pivotiter+1, end); // (+1 = skip pivot element)
    }
}





#include <iostream>

int main()
{
    std::vector<int> v = {34, 635, 74, 24, 63, 42, 75, 967, 52, 24, 524, 31, 1};
    std::vector<int> v2 = v;
    
    quicksort(v2.begin(), v2.end());
    std::cout << "quicksort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    mergesort1(v2.begin(), v2.end());
    std::cout << "mergesort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    mergesort2(v2.begin(), v2.end());
    std::cout << "mergesort2" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    mergesort3(v2.begin(), v2.end());
    std::cout << "mergesort3" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    mergesort4(v2.begin(), v2.end());
    std::cout << "mergesort4" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    selection_sort(v2.begin(), v2.end());
    std::cout << "selection_sort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
    
    v2 = v;
    insertion_sort(v2.begin(), v2.end());
    std::cout << "insertion_sort" << std::endl;
    for (auto x : v2) { std::cout << x << " "; }
    std::cout << std::endl << std::endl;
}
