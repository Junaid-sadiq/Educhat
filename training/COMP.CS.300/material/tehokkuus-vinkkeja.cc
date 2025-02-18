




std::sort(data.begin(), data.end()); // n log n
auto median = data[data.size()/2];







auto medianplace = data.begin() + data.size()/2;
std::nth_element(data.begin(), medianplace, data.end()); // linear on average
auto median = *medianplace;

















std::map<int, int> m;
// ... insert N elements to m.
for(int i=0; i<N; ++i)
{
    m[i] = m[i] + 1; // Logarithmic operation, and indexing twice!
}
// The whole for loop n log n, not linear!





















std::deque<int> v;
// ...
v[i] = 0;
// ...
v[i] = v[x] * v[x];
// ...
v[j] = v[i]  // In total 6 v[i] operations!



auto vi = 0;
auto vx = v[x];
// ...
vi = vx * vx;
// ...
v[i] = vi;
v[j] = vi;



auto vi = &v[i];
auto vx = &v[x];
*vi = 0;
// ...
*vi = *vx * *vx;
// ...
v[j] = *vi;


















bool min_valid = false;
int min_value;

int calculate_min()
{
    if (!min_valid)
    {
        min_value = *std::min_element(data.begin(), data.end());
        min_valid = true;
    }
    return min_value;
}












std::optional<int> min_value;

int calculate_min()
{
if (!min_value.has_value())
{
    min_value = std::min_element(data.begin(), data.end());
}

return min_value.value();
}




















vector<int> v;

void add_value(int i)
{
    v.push_back(i);
}

void remove_last()
{
    v.pop_back();
}

int average()
{
    int sum = 0;
    for (int i : v)
    {
        sum += i;
    }
    return sum/v.size();
}















vector<int> v;
int sum = 0;

void add_value(int i)
{
    v.push_back(i);
    sum += i;
}

void remove_last()
{
    sum -= v.back();
    v.pop_back();
}

int average()
{
    return sum/v.size();
}
